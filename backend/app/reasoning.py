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
) -> dict:
    required = skill in jd_data.required
    preferred = skill in jd_data.preferred
    mastery = mastery_scores.get(skill, 0.0)
    priority = priorities.get(skill, 0.0)
    descendants = nx.descendants(subgraph, skill)
    depth = (
        nx.dag_longest_path_length(subgraph.subgraph({skill} | descendants))
        if descendants
        else 0
    )
    unlocks = list(subgraph.successors(skill))
    reasons = []
    if required:
        reasons.append("explicitly required by the Job Description")
    elif preferred:
        reasons.append("listed as preferred in the Job Description")
    if depth >= 2:
        reasons.append(f"unlocks {depth} downstream skill levels")
    elif unlocks:
        reasons.append(f"directly unlocks {', '.join(unlocks)}")
    if mastery < 0.3:
        reasons.append(f"current mastery is low ({mastery:.2f})")
    if path_position == 0:
        reasons.append("no unmet prerequisites remain, so it is a valid starting point")
    return {
        "skill": skill,
        "position": path_position + 1,
        "mastery": mastery,
        "priority_score": priority,
        "required_by_jd": required,
        "preferred_by_jd": preferred,
        "unlocks": unlocks,
        "downstream_depth": depth,
        "reason": f"Selected because: {'; '.join(reasons)}." if reasons else "Required dependency for downstream skills.",
    }
