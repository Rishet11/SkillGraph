from __future__ import annotations

from .data_loader import Domain, load_courses


def recommend_course(skill: str, gap_skills: set[str], domain: Domain) -> dict:
    catalog = load_courses(domain)
    candidates = [course for course in catalog if skill in course["covers"]]
    if not candidates:
        return {
            "id": f"missing-{skill.lower().replace(' ', '-')}",
            "name": "No course available",
            "covers": [skill],
            "difficulty": 0,
            "domain": domain.upper(),
            "url": "",
        }

    def score_course(course: dict):
        gap_coverage = sum(1 for covered in course["covers"] if covered in gap_skills)
        return (gap_coverage, -course["difficulty"])

    return max(candidates, key=score_course)

