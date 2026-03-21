import os
import numpy as np

_model = None

def _load_model():
    global _model
    if _model is None:
        path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), '..', 'models', 'ranker.lgb')
        )
        if os.path.exists(path):
            import lightgbm as lgb
            _model = lgb.Booster(model_file=path)
    return _model

def rank_skills(
    skills: list,
    domain: str,
    jd_data: dict,
    mastery_scores: dict,
    subgraph
) -> dict:
    """
    Returns {skill: priority_score} for all skills.
    Uses LightGBM if model exists, formula fallback if not.
    """
    from .gnn_scorer import gnn_score as get_gnn_score
    model = _load_model()

    features = []
    
    # We reconstruct JDData fields inside in case it's a Pydantic model vs dict
    # Wait, the instruction says "jd_data: dict", but graph.py passes jd_data as JDData which has required/preferred attributes.
    # The instruction says: jd_imp = (1.0 if skill in jd_data.get("required", []) else ...)
    # If it's a JDData, jd_data.get will fail.
    # Let's handle both Dict and Pydantic just in case.
    if hasattr(jd_data, "required"):
        req = jd_data.required
        pref = jd_data.preferred
    else:
        req = jd_data.get("required", [])
        pref = jd_data.get("preferred", [])

    for skill in skills:
        jd_imp = 1.0 if skill in req else (0.6 if skill in pref else 0.0)
        gnn = get_gnn_score(skill, domain)
        mastery = mastery_scores.get(skill, 0.0)
        in_deg = subgraph.in_degree(skill) if skill in subgraph else 0
        out_deg = subgraph.out_degree(skill) if skill in subgraph else 0
        features.append([jd_imp, gnn, mastery, in_deg, out_deg])

    if model is not None and features:
        scores = model.predict(np.array(features))
    else:
        scores = [0.4*f[0] + 0.4*f[1] - 0.2*f[2] for f in features]

    return {skill: float(score) for skill, score in zip(skills, scores)}
