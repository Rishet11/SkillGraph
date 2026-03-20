from __future__ import annotations

from .data_loader import load_weights
from .graph import collect_missing_prerequisites


def score_resume_skills(resume_evidence):
    weights = load_weights()
    scored = []
    for item in resume_evidence:
        base = weights["evidence_base"]
        score = base + item["hits"] * weights["evidence_boost_per_hit"]
        if item["source_section"] in {"skills", "summary", "experience"}:
            score += weights["section_bonus"]
        scored.append(
            {
                "skill_id": item["skill_id"],
                "label": item["label"],
                "mastery_score": min(100, round(score)),
                "evidence_snippets": item["snippets"],
                "source_section": item["source_section"],
            }
        )
    return scored


def compare_skills(resume_skills, target_skills):
    weights = load_weights()
    weight_map = weights["importance_weights"]
    resume_index = {skill["skill_id"]: skill for skill in resume_skills}
    matched = []
    missing = []
    total_weight = 0.0
    earned_weight = 0.0
    owned_skills = set(resume_index)
    for target in target_skills:
        importance_weight = weight_map[target["importance"]]
        total_weight += importance_weight
        if target["skill_id"] in resume_index:
            skill = resume_index[target["skill_id"]]
            matched.append(
                {
                    "skill_id": skill["skill_id"],
                    "label": skill["label"],
                    "status": "matched" if skill["mastery_score"] >= 65 else "partial",
                    "mastery_score": skill["mastery_score"],
                    "reason": f"{skill['label']} appears in the resume with evidence from the {skill['source_section']} section.",
                }
            )
            earned_weight += importance_weight * min(1.0, skill["mastery_score"] / 100)
        else:
            prereqs = collect_missing_prerequisites(target["skill_id"], owned_skills)
            gap_type = "adjacent" if prereqs and len(prereqs) <= 2 else "missing"
            missing.append(
                {
                    "skill_id": target["skill_id"],
                    "label": target["label"],
                    "gap_type": gap_type,
                    "missing_prerequisites": prereqs,
                    "reason": f"{target['label']} is expected for the role but was not clearly evidenced in the resume.",
                }
            )
            earned_weight -= importance_weight * weights["missing_penalty"]
    fit_score = max(0, min(100, round((max(0.0, earned_weight) / total_weight) * 100 if total_weight else 0)))
    confidence = max(35, min(96, round(55 + len(resume_skills) * 4 + len(target_skills) * 2 - len(missing) * 3)))
    return matched, missing, fit_score, confidence

