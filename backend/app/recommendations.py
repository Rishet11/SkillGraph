from __future__ import annotations

from .data_loader import load_courses
from .graph import get_skill_label


def recommend_courses(skill_id: str):
    matches = []
    for course in load_courses():
        if skill_id in course["skill_tags"]:
            matches.append(
                {
                    "course_id": course["id"],
                    "title": course["title"],
                    "provider": course["provider"],
                    "url": course["url"],
                    "duration": course["duration"],
                }
            )
    return matches[:2]


def build_learning_path(gaps):
    prioritized = sorted(gaps, key=lambda gap: (len(gap["missing_prerequisites"]), gap["label"]))
    path = []
    for index, gap in enumerate(prioritized, start=1):
        path.append(
            {
                "order": index,
                "skill_id": gap["skill_id"],
                "goal": f"Build working confidence in {gap['label']}.",
                "recommended_courses": recommend_courses(gap["skill_id"]),
                "why_now": (
                    f"Close {gap['label']} early because it unlocks "
                    f"{', '.join(get_skill_label(item) for item in gap['missing_prerequisites']) or 'the target role requirements'}."
                ),
            }
        )
    return path

