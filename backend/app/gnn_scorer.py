import json
import os

_cache: dict = {}

def gnn_score(skill: str, domain: str) -> float:
    """
    Returns normalized structural importance score (0.0 to 1.0).
    Loads from backend/models/embeddings_{domain}.json.
    Returns 0.5 as fallback if file not found.
    """
    global _cache
    if domain not in _cache:
        base = os.path.dirname(__file__)
        path = os.path.join(base, '..', 'models', f'embeddings_{domain}.json')
        path = os.path.normpath(path)
        if os.path.exists(path):
            with open(path) as f:
                _cache[domain] = json.load(f)
        else:
            _cache[domain] = {}
    return float(_cache.get(domain, {}).get(skill, 0.5))
