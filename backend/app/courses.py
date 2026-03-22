from __future__ import annotations

from .data_loader import Domain, load_courses


def recommend_course(skill: str, gap_skills: set[str], domain: Domain, mastery: float = 0.0) -> dict:
    catalog = load_courses(domain)
    candidates = [course for course in catalog if skill in course["covers"]]
    
    if candidates:
        # Mastery-aware difficulty selection:
        # Mastery 0.0-0.3 -> Difficulty 1 (Beginner)
        # Mastery 0.3-0.6 -> Difficulty 2 (Intermediate)
        # Mastery 0.6+   -> Difficulty 3 (Advanced)
        target_difficulty = 1 if mastery < 0.3 else (2 if mastery < 0.6 else 3)
        
        def score_course(course: dict):
            # 1. Prefer courses that cover more of the detected gaps
            gap_coverage = sum(1 for covered in course["covers"] if covered in gap_skills)
            # 2. Prefer difficulty that matches the user's current mastery level
            difficulty_fit = 1.0 - (abs(course["difficulty"] - target_difficulty) / 3.0)
            return (gap_coverage, difficulty_fit)
            
        return max(candidates, key=score_course)

    # Better Fallback Discovery
    # If no catalog match, generate a direct link to high-quality learning resources
    skill_query = skill.replace(' ', '+')
    fallbacks = {
        "Python": "https://docs.python.org/3/tutorial/",
        "JavaScript": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide",
        "React": "https://react.dev/learn",
        "Docker": "https://docs.docker.com/get-started/",
        "Machine Learning Fundamentals": "https://scikit-learn.org/stable/tutorial/index.html",
        "LLMs": "https://www.deeplearning.ai/short-courses/",
    }
    
    url = fallbacks.get(skill, f"https://www.google.com/search?q=learn+{skill_query}+official+documentation")
    
    return {
        "id": f"external-{skill.lower().replace(' ', '-')}",
        "name": f"{skill} Professional Documentation & Tutorial",
        "covers": [skill],
        "difficulty": 2,
        "domain": str(domain).upper(),
        "url": url,
        "estimated_hours": 15 # Default fallback estimate
    }

