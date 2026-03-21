from __future__ import annotations

from .schemas import JDData


WEIGHTS = {"evidence": 0.45, "recency": 0.35, "jd_match": 0.20}
MASTERY_THRESHOLD = 0.6


def compute_mastery(skill: str, resume_data: list[dict], jd_data: JDData, total_skills_mentioned: int) -> float:
    skill_entry = next((item for item in resume_data if item["skill"] == skill), None)
    if skill_entry is None:
        return 0.0
    frequency = min(skill_entry["mentions"] / max(total_skills_mentioned, 1), 1.0)
    evidence = float(skill_entry.get("evidence_score", frequency))
    recency = 1.0 if skill_entry["in_recent_experience"] else 0.5
    if skill in jd_data.required:
        jd_match = 1.0
    elif skill in jd_data.preferred:
        jd_match = 0.6
    else:
        jd_match = 0.0
    score = (
        WEIGHTS["evidence"] * evidence
        + WEIGHTS["recency"] * recency
        + WEIGHTS["jd_match"] * jd_match
    )
    return round(min(score, 1.0), 3)


def compute_mastery_scores(all_skills: list[str], resume_data: list[dict], jd_data: JDData) -> dict[str, float]:
    total_mentions = sum(item["mentions"] for item in resume_data)
    return {
        skill: compute_mastery(skill, resume_data, jd_data, total_mentions)
        for skill in all_skills
    }
