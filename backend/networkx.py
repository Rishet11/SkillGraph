from __future__ import annotations

from collections import deque


class DiGraph:
    def __init__(self):
        self._succ: dict[str, set[str]] = {}
        self._pred: dict[str, set[str]] = {}

    def add_nodes_from(self, nodes):
        for node in nodes:
            self._succ.setdefault(node, set())
            self._pred.setdefault(node, set())

    def add_edges_from(self, edges):
        for source, target in edges:
            self.add_nodes_from([source, target])
            self._succ[source].add(target)
            self._pred[target].add(source)

    @property
    def nodes(self):
        return list(self._succ.keys())

    @property
    def edges(self):
        return [(source, target) for source, targets in self._succ.items() for target in targets]

    def subgraph(self, nodes):
        nodes_set = set(nodes)
        graph = DiGraph()
        graph.add_nodes_from(nodes_set)
        graph.add_edges_from(
            (source, target)
            for source, target in self.edges
            if source in nodes_set and target in nodes_set
        )
        return graph

    def copy(self):
        graph = DiGraph()
        graph.add_nodes_from(self.nodes)
        graph.add_edges_from(self.edges)
        return graph

    def successors(self, node):
        return iter(sorted(self._succ.get(node, set())))

    def predecessors(self, node):
        return iter(sorted(self._pred.get(node, set())))

    def in_degree(self):
        return [(node, len(preds)) for node, preds in self._pred.items()]

    def number_of_nodes(self):
        return len(self._succ)


def ancestors(graph: DiGraph, node: str) -> set[str]:
    visited: set[str] = set()
    queue = deque(graph._pred.get(node, set()))
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        queue.extend(graph._pred.get(current, set()))
    return visited


def descendants(graph: DiGraph, node: str) -> set[str]:
    visited: set[str] = set()
    queue = deque(graph._succ.get(node, set()))
    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)
        queue.extend(graph._succ.get(current, set()))
    return visited


def dag_longest_path_length(graph: DiGraph) -> int:
    if graph.number_of_nodes() <= 1:
        return 0
    indegree = {node: len(graph._pred.get(node, set())) for node in graph.nodes}
    distance = {node: 0 for node in graph.nodes}
    queue = deque([node for node, degree in indegree.items() if degree == 0])
    while queue:
        node = queue.popleft()
        for successor in graph._succ.get(node, set()):
            distance[successor] = max(distance[successor], distance[node] + 1)
            indegree[successor] -= 1
            if indegree[successor] == 0:
                queue.append(successor)
    return max(distance.values(), default=0)

