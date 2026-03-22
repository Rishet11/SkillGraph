from __future__ import annotations

import os
import json
from collections import deque
from .schemas import JDData


WEIGHTS = {"frequency": 0.31, "recency": 0.336, "jd_match": 0.354}


def _load_dynamic_weights():
    global WEIGHTS
    base = os.path.dirname(__file__)
    path = os.path.normpath(os.path.join(base, '..', 'models', 'mastery_weights.json'))
    if os.path.exists(path):
        try:
            with open(path) as f:
                WEIGHTS = json.load(f)
        except Exception:
            pass


_load_dynamic_weights()

MASTERY_THRESHOLD = 0.6

# Inferred mastery for a direct prerequisite of a mastered skill
BASE_INFERRED_MASTERY = 0.55
# Each extra hop away from the mastered skill reduces inferred mastery by this
INFERENCE_DECAY_PER_HOP = 0.08
# Minimum floor for any inferred score (avoids negative decay)
MIN_INFERRED_MASTERY = 0.20
# Boost applied when the JD explicitly requires an inferred skill
JD_INFERENCE_BOOST = 0.05
# Forward inference: if this fraction of a skill's prerequisites are mastered,
# infer partial knowledge of that skill itself
FORWARD_INFERENCE_PREREQ_RATIO = 0.5


def compute_mastery(
    skill: str,
    resume_data: list[dict],
    jd_data: JDData,
    total_skills_mentioned: int,
) -> float:
    skill_entry = next((item for item in resume_data if item["skill"] == skill), None)
    if skill_entry is None:
        return 0.0
    frequency = min(skill_entry["mentions"] / max(total_skills_mentioned, 1), 1.0)
    recency = 1.0 if skill_entry["in_recent_experience"] else 0.5
    if skill in jd_data.required:
        jd_match = 1.0
    elif skill in jd_data.preferred:
        jd_match = 0.6
    else:
        jd_match = 0.0
    score = (
        WEIGHTS["frequency"] * frequency
        + WEIGHTS["recency"] * recency
        + WEIGHTS["jd_match"] * jd_match
    )
    return round(min(score, 1.0), 3)


def infer_prerequisite_mastery(
    mastery_scores: dict[str, float],
    edges: list[tuple[str, str]],
    jd_data: JDData | None = None,
) -> dict[str, float]:
    """
    Graph-aware skill inference with four improvements over the naive approach:

    FIX 1 — Transitive chains (BFS instead of repeated iteration):
        Uses BFS from every mastered skill backward through the prerequisite
        graph. Records the *minimum depth* from any mastered skill for each
        prerequisite node, so the chain ML → NumPy → Python is fully traversed
        even though NumPy's inferred score (0.55) is below MASTERY_THRESHOLD.

    FIX 2 — Distance-weighted decay:
        Direct prerequisite (depth 1) → BASE_INFERRED_MASTERY (0.55)
        2 hops away           (depth 2) → 0.47
        3 hops away           (depth 3) → 0.39
        … (floor at 0.20)
        So knowing ML gives stronger inference for NumPy than for Python.

    FIX 3 — JD-aware boost:
        If the JD explicitly requires an inferred skill, its inferred score is
        bumped by JD_INFERENCE_BOOST so it's treated more seriously in ranking.

    FIX 4 — Forward inference (prerequisite → dependent):
        If the majority (≥50%) of a skill's prerequisites are mastered,
        we infer partial knowledge of the dependent skill itself.
        e.g. knowing NumPy + Statistics → infer partial ML knowledge (0.3–0.5)
        This is capped well below MASTERY_THRESHOLD so it stays a visible gap.
    """
    result = dict(mastery_scores)

    # ── Build graph lookups ──────────────────────────────────────────────────
    prereqs: dict[str, list[str]] = {}     # dst → list of src (prerequisites)
    dependents: dict[str, list[str]] = {}  # src → list of dst (what requires src)
    for src, dst in edges:
        prereqs.setdefault(dst, []).append(src)
        dependents.setdefault(src, []).append(dst)

    jd_skills: set[str] = set()
    if jd_data:
        jd_skills = set(jd_data.required) | set(jd_data.preferred)

    # ── FIX 1 & 2: BFS backward from all mastered skills ────────────────────
    # depth[skill] = minimum hops from any directly-mastered skill
    depth: dict[str, int] = {}
    queue: deque[str] = deque()

    for skill, score in result.items():
        if score >= MASTERY_THRESHOLD:
            depth[skill] = 0
            queue.append(skill)

    while queue:
        skill = queue.popleft()
        current_depth = depth[skill]
        for prereq in prereqs.get(skill, []):
            new_depth = current_depth + 1
            # Only enqueue if we found a shorter path (or haven't visited yet)
            if prereq not in depth or depth[prereq] > new_depth:
                depth[prereq] = new_depth
                queue.append(prereq)

    # ── Apply distance-weighted inferred scores ──────────────────────────────
    for skill, d in depth.items():
        if d == 0:
            continue  # already mastered — don't reduce their score

        decayed = BASE_INFERRED_MASTERY - (d - 1) * INFERENCE_DECAY_PER_HOP
        inferred = max(MIN_INFERRED_MASTERY, decayed)

        # FIX 3: boost if JD explicitly requires this inferred skill
        if skill in jd_skills:
            inferred = min(BASE_INFERRED_MASTERY, inferred + JD_INFERENCE_BOOST)

        # Only boost, never reduce existing scores
        if result.get(skill, 0.0) < inferred:
            result[skill] = round(inferred, 3)

    # ── FIX 4: Forward inference — prereqs known → infer dependent ──────────
    # e.g. knows NumPy + Statistics → infer partial ML Fundamentals knowledge
    for skill in list(result.keys()):
        if result[skill] >= MASTERY_THRESHOLD:
            continue  # already mastered; don't touch
        prereq_list = prereqs.get(skill, [])
        if not prereq_list:
            continue
        mastered_prereqs = [
            p for p in prereq_list if result.get(p, 0.0) >= MASTERY_THRESHOLD
        ]
        ratio = len(mastered_prereqs) / len(prereq_list)
        if ratio >= FORWARD_INFERENCE_PREREQ_RATIO:
            # Scale: 50% prereqs known → 0.30, 100% known → 0.50
            forward_score = round(0.30 + 0.20 * ratio, 3)
            if result[skill] < forward_score:
                result[skill] = forward_score

    return result


def compute_mastery_scores(
    all_skills: list[str],
    resume_data: list[dict],
    jd_data: JDData,
    domain: str | None = None,           # FIX: explicit domain — no list comparison
) -> dict[str, float]:
    total_mentions = sum(item["mentions"] for item in resume_data)
    raw_scores = {
        skill: compute_mastery(skill, resume_data, jd_data, total_mentions)
        for skill in all_skills
    }

    if domain:
        try:
            from .data_loader import load_edges
            edges = load_edges(domain)
            return infer_prerequisite_mastery(raw_scores, edges, jd_data)
        except Exception:
            pass  # fall back to raw scores on any error

    return raw_scores
