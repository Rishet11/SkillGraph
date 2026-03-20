from __future__ import annotations

try:  # Prefer the real package when available.
    import networkx as nx  # type: ignore
except ImportError:  # pragma: no cover - fallback for constrained environments
    from backend import networkx as nx  # type: ignore

