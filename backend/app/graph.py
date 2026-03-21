from __future__ import annotations

from .config import MISSING_GAP_DELTA, PREFERRED_MASTERY_THRESHOLD, REQUIRED_MASTERY_THRESHOLD, WEAK_GAP_DELTA
from .data_loader import Domain, load_edges, load_skills
from .mastery import MASTERY_THRESHOLD
from .nx_compat import nx
from .schemas import JDData


def _required_level(skill: str, jd_data: JDData) -> float:
    if skill in jd_data.required:
        return 1.0
    if skill in jd_data.preferred:
        return 0.6
    return 0.5


def build_skill_graph(domain: Domain) -> nx.DiGraph:
    graph = nx.DiGraph()
    skills = load_skills(domain)
    graph.add_nodes_from(skills)
    graph.add_edges_from(load_edges(domain))
    return graph


def identify_gaps(all_skills: list[str], mastery_scores: dict[str, float], jd_data: JDData) -> set[str]:
    required_threshold = max(MASTERY_THRESHOLD, REQUIRED_MASTERY_THRESHOLD)
    preferred_threshold = max(MASTERY_THRESHOLD - 0.1, PREFERRED_MASTERY_THRESHOLD)
    gaps: set[str] = set()
    for skill in all_skills:
        mastery = mastery_scores.get(skill, 0.0)
        if skill in jd_data.required and mastery < required_threshold:
            gaps.add(skill)
        elif skill in jd_data.preferred and mastery < preferred_threshold:
            gaps.add(skill)
    return gaps


def compute_gap_report(mastery_scores: dict[str, float], jd_data: JDData) -> dict[str, list[str]]:
    ordered_skills = list(dict.fromkeys([*jd_data.required, *jd_data.preferred]))
    missing: list[str] = []
    weak: list[str] = []
    met: list[str] = []

    for skill in ordered_skills:
        required_level = _required_level(skill, jd_data)
        mastery = mastery_scores.get(skill, 0.0)
        delta = required_level - mastery
        if delta >= MISSING_GAP_DELTA:
            missing.append(skill)
        elif delta >= WEAK_GAP_DELTA:
            weak.append(skill)
        else:
            met.append(skill)

    return {
        "missing": sorted(missing),
        "weak": sorted(weak),
        "met": sorted(met),
    }


def build_gap_subgraph(graph: nx.DiGraph, gap_skills: set[str]) -> nx.DiGraph:
    nodes_to_include = set(gap_skills)
    for skill in gap_skills:
        nodes_to_include.update(nx.ancestors(graph, skill))
    return graph.subgraph(nodes_to_include).copy()


from .gnn_scorer import gnn_score


def compute_priority(
    skill: str, subgraph: nx.DiGraph, jd_data: JDData, mastery_scores: dict[str, float], domain: str
) -> float:
    if skill in jd_data.required:
        jd_importance = 1.0
    elif skill in jd_data.preferred:
        jd_importance = 0.6
    else:
        jd_importance = 0.0
    mastery = mastery_scores.get(skill, 0.0)
    priority = 0.4 * jd_importance + 0.4 * gnn_score(skill, domain) - 0.2 * mastery
    return round(priority, 4)


def build_learning_subgraph(subgraph: nx.DiGraph, mastery_scores: dict[str, float]) -> nx.DiGraph:
    nodes = [
        node for node in subgraph.nodes
        if mastery_scores.get(node, 0.0) < MASTERY_THRESHOLD
    ]
    return subgraph.subgraph(nodes).copy()


def generate_learning_path(
    subgraph: nx.DiGraph, priorities: dict[str, float], mastery_scores: dict[str, float]
) -> list[str]:
    if subgraph.number_of_nodes() == 0:
        return []
    in_degree = dict(subgraph.in_degree())
    path: list[str] = []
    visited: set[str] = set()
    frontier = [node for node, degree in in_degree.items() if degree == 0]
    while frontier:
        frontier = list(dict.fromkeys(frontier))
        frontier.sort(key=lambda node: (-priorities.get(node, 0.0), mastery_scores.get(node, 0.0), node))
        chosen = frontier.pop(0)
        if chosen in visited:
            continue
        path.append(chosen)
        visited.add(chosen)
        for successor in subgraph.successors(chosen):
            if successor in visited:
                continue
            if all(pred in visited for pred in subgraph.predecessors(successor)):
                frontier.append(successor)
    return path


def build_graph_payload(
    subgraph: nx.DiGraph,
    path: list[str],
    mastery_scores: dict[str, float],
    gap_skills: set[str],
) -> dict:
    path_set = set(path)
    nodes = []
    for node in subgraph.nodes:
        mastery = mastery_scores.get(node, 0.0)
        if node in path_set:
            status = "selected_path"
        elif node in gap_skills:
            status = "critical_gap"
        elif mastery >= 0.8:
            status = "mastered"
        elif mastery >= 0.4:
            status = "partial"
        else:
            status = "unseen"
        nodes.append({"id": node, "label": node, "mastery": mastery, "status": status})
    edges = [{"source": source, "target": target} for source, target in subgraph.edges]
    return {"nodes": nodes, "edges": edges}
