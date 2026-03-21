from __future__ import annotations

from .nx_compat import nx
from .schemas import JDData


def generate_trace(
    skill: str,
    path_position: int,
    subgraph: nx.DiGraph,
    priorities: dict[str, float],
    mastery_scores: dict[str, float],
    jd_data: JDData,
    resume_skill: dict | None = None,
) -> dict:
    required = skill in jd_data.required
    preferred = skill in jd_data.preferred
    mastery = mastery_scores.get(skill, 0.0)
    required_level = 1.0 if required else (0.6 if preferred else 0.5)
    gap = max(0.0, required_level - mastery)
    priority = priorities.get(skill, 0.0)
    descendants = nx.descendants(subgraph, skill)
    depth = (
        nx.dag_longest_path_length(subgraph.subgraph({skill} | descendants))
        if descendants
        else 0
    )
    unlocks = list(subgraph.successors(skill))
    reasons = []
    reason_codes: list[str] = []
    if required:
        reasons.append("explicitly required by the Job Description")
        reason_codes.append("JD_REQUIRED")
    elif preferred:
        reasons.append("listed as preferred in the Job Description")
        reason_codes.append("JD_PREFERRED")
    if depth >= 2:
        reasons.append(f"unlocks {depth} downstream skill levels")
        reason_codes.append("UNLOCKS_DEEP_CHAIN")
    elif unlocks:
        reasons.append(f"directly unlocks {', '.join(unlocks)}")
        reason_codes.append("UNLOCKS_NEXT")
    if mastery < 0.3:
        reasons.append(f"current mastery is low ({mastery:.2f})")
        reason_codes.append("LOW_CURRENT_CONFIDENCE")
    if gap >= 0.15:
        reasons.append(f"required level is {required_level:.2f}, leaving a {gap:.2f} gap")
        reason_codes.append("REQUIRED_LEVEL_GAP")
    if path_position == 0:
        reasons.append("no unmet prerequisites remain, so it is a valid starting point")
        reason_codes.append("VALID_FRONTIER_START")
    if not reason_codes:
        reason_codes.append("DEPENDENCY_SUPPORT")

    resume_mentions = int((resume_skill or {}).get("mentions", 0))
    source_sections = list((resume_skill or {}).get("source_sections", []))
    resume_snippets = list((resume_skill or {}).get("evidence_snippets", []))
    resume_refs = list((resume_skill or {}).get("evidence_refs", []))
    required_evidence = getattr(jd_data, "required_evidence", {})
    preferred_evidence = getattr(jd_data, "preferred_evidence", {})
    required_evidence_refs = getattr(jd_data, "required_evidence_refs", {})
    preferred_evidence_refs = getattr(jd_data, "preferred_evidence_refs", {})
    jd_snippets = list(required_evidence.get(skill, []) or preferred_evidence.get(skill, []))
    jd_refs = list(required_evidence_refs.get(skill, []) or preferred_evidence_refs.get(skill, []))
    if required:
        jd_signal = "required"
    elif preferred:
        jd_signal = "preferred"
    else:
        jd_signal = "prerequisite"

    return {
        "skill": skill,
        "position": path_position + 1,
        "mastery": mastery,
        "required_level": required_level,
        "gap": round(gap, 3),
        "priority_score": priority,
        "required_by_jd": required,
        "preferred_by_jd": preferred,
        "reason_codes": reason_codes,
        "unlocks": unlocks,
        "downstream_depth": depth,
        "reason": f"Selected because: {'; '.join(reasons)}." if reasons else "Required dependency for downstream skills.",
        "evidence": {
            "resume_mentions": resume_mentions,
            "resume_sections": source_sections,
            "resume_snippets": resume_snippets,
            "resume_refs": resume_refs,
            "jd_signal": jd_signal,
            "jd_snippets": jd_snippets,
            "jd_refs": jd_refs,
        },
    }
