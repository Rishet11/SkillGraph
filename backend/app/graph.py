from __future__ import annotations

from .data_loader import Domain, load_edges, load_skills
from .mastery import MASTERY_THRESHOLD
from .nx_compat import nx
from .schemas import JDData
from .ontology import get_skill_ontology


def build_skill_graph(domain: Domain) -> nx.DiGraph:
    graph = nx.DiGraph()
    skills = load_skills(domain)
    graph.add_nodes_from(skills)
    graph.add_edges_from(load_edges(domain))
    return graph


def identify_gaps(all_skills: list[str], mastery_scores: dict[str, float], jd_data: JDData) -> set[str]:
    jd_skills = set(jd_data.required) | set(jd_data.preferred)
    gaps = set()
    for skill in jd_skills:
        # V2 Upgrade: JIT Prerequisite Discovery
        # If skill is not in our local list, we treat it as a gap
        if skill not in all_skills:
            gaps.add(skill)
            continue
            
        if mastery_scores.get(skill, 0.0) < MASTERY_THRESHOLD:
            gaps.add(skill)
    return gaps


def build_gap_subgraph(graph: nx.DiGraph, gap_skills: set[str], industry: str = "Technology/Software") -> nx.DiGraph:
    nodes_to_include = set(gap_skills)
    
    # Track skills already processed to avoid infinite loops in JIT discovery
    processed = set()
    queue = list(gap_skills)
    
    while queue:
        skill = queue.pop(0)
        if skill in processed:
            continue
        processed.add(skill)
        
        if skill in graph:
            nodes_to_include.update(nx.ancestors(graph, skill))
        else:
            # V2 Upgrade: JIT Prerequisite Fetch for unknown industries
            prereqs = get_skill_ontology(skill, industry)
            for p in prereqs:
                if p not in nodes_to_include:
                    nodes_to_include.add(p)
                    queue.append(p)
                    # We might want to add these "new" edges to a local session graph
                    # But for the subgraph, adding nodes is enough for now
    
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
