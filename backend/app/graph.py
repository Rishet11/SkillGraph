from __future__ import annotations

from collections import defaultdict, deque

from .data_loader import load_edges, load_skills


def build_prerequisite_map():
    prerequisites = defaultdict(list)
    for edge in load_edges():
        prerequisites[edge["target"]].append(edge)
    return prerequisites


def get_skill_label(skill_id: str) -> str:
    for skill in load_skills():
        if skill["id"] == skill_id:
            return skill["label"]
    return skill_id.replace("_", " ").title()


def collect_missing_prerequisites(skill_id: str, owned_skills: set[str]) -> list[str]:
    prerequisites = build_prerequisite_map()
    queue = deque([skill_id])
    missing: list[str] = []
    visited: set[str] = set()
    while queue:
        current = queue.popleft()
        for edge in prerequisites.get(current, []):
            source = edge["source"]
            if source in visited:
                continue
            visited.add(source)
            if source not in owned_skills:
                missing.append(source)
            queue.append(source)
    return missing


def build_graph_payload(resume_skills, target_skills, gaps, learning_path):
    resume_ids = {skill["skill_id"] for skill in resume_skills}
    target_ids = {skill["skill_id"] for skill in target_skills}
    nodes = []
    edges = []
    for skill in resume_skills:
        nodes.append(
            {
                "id": skill["skill_id"],
                "label": skill["label"],
                "type": "current_skill",
                "score": skill["mastery_score"],
            }
        )
    for skill in target_skills:
        nodes.append(
            {
                "id": f"target:{skill['skill_id']}",
                "label": skill["label"],
                "type": "target_skill",
                "score": None,
            }
        )
        edges.append(
            {
                "source": skill["skill_id"] if skill["skill_id"] in resume_ids else f"gap:{skill['skill_id']}",
                "target": f"target:{skill['skill_id']}",
                "kind": "targets",
                "reason": f"{skill['label']} is expected for the target role.",
            }
        )
    for gap in gaps:
        gap_id = f"gap:{gap['skill_id']}"
        nodes.append(
            {
                "id": gap_id,
                "label": gap["label"],
                "type": "gap_skill",
                "score": None,
            }
        )
        for prereq in gap["missing_prerequisites"]:
            prereq_id = f"prereq:{prereq}"
            nodes.append(
                {
                    "id": prereq_id,
                    "label": get_skill_label(prereq),
                    "type": "prerequisite",
                    "score": None,
                }
            )
            edges.append(
                {
                    "source": prereq_id,
                    "target": gap_id,
                    "kind": "prerequisite",
                    "reason": f"{get_skill_label(prereq)} supports {gap['label']}.",
                }
            )
    for step in learning_path:
        course_ids = []
        for course in step["recommended_courses"]:
            course_node_id = f"course:{course['course_id']}"
            course_ids.append(course_node_id)
            nodes.append(
                {
                    "id": course_node_id,
                    "label": course["title"],
                    "type": "recommended_course",
                    "score": None,
                }
            )
            edges.append(
                {
                    "source": course_node_id,
                    "target": f"gap:{step['skill_id']}",
                    "kind": "recommended_for",
                    "reason": f"{course['title']} helps close the {get_skill_label(step['skill_id'])} gap.",
                }
            )
    deduped_nodes = list({node["id"]: node for node in nodes}.values())
    deduped_edges = list({(edge["source"], edge["target"], edge["kind"]): edge for edge in edges}.values())
    return {"nodes": deduped_nodes, "edges": deduped_edges}

