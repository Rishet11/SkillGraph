from __future__ import annotations

from .data_loader import Domain, load_courses


def recommend_course(skill: str, gap_skills: set[str], domain: Domain) -> dict:
    catalog = load_courses(domain)
    candidates = [course for course in catalog if skill in course["covers"]]
    
    if candidates:
        def score_course(course: dict):
            gap_coverage = sum(1 for covered in course["covers"] if covered in gap_skills)
            return (gap_coverage, -course["difficulty"])
        return max(candidates, key=score_course)

    # V2 Upgrade: Universal Course Discovery
    # If no catalog match, generate a custom syllabus placeholder
    # This ensures the "Learn" path is always populated for any industry
    return {
        "id": f"custom-{skill.lower().replace(' ', '-')}",
        "name": f"Comprehensive {skill} Mastery Module",
        "covers": [skill],
        "difficulty": 2,
        "domain": str(domain).upper(),
        "url": "https://skillgraph.ai/custom-curriculum"
    }

