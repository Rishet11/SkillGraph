from __future__ import annotations

import os
import json
import torch
from sentence_transformers import SentenceTransformer, util
from .data_loader import Domain, load_skills

_model = None
_skill_embeddings: dict[str, torch.Tensor] = {}

def get_model():
    global _model
    if _model is None:
        # Using a balanced model for fast, local semantic mapping
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

def get_skill_embeddings(domain: Domain):
    global _skill_embeddings
    if domain not in _skill_embeddings:
        model = get_model()
        skills = load_skills(domain)
        # Pre-compute skill embeddings for the domain
        _skill_embeddings[domain] = model.encode(skills, convert_to_tensor=True)
    return _skill_embeddings[domain]

def semantic_extract(text: str, domain: Domain, threshold: float = 0.5) -> list[dict]:
    """
    Matches text spans to the skill taxonomy using vector embeddings.
    Returns: [{"skill": str, "score": float}]
    """
    model = get_model()
    all_skills = load_skills(domain)
    if not all_skills:
        return []
        
    skill_embeddings = get_skill_embeddings(domain)
    
    # Encode the input text
    # In a production scenario, we might chunk the text, 
    # but for this scale, encoding the full text works well.
    text_embedding = model.encode(text, convert_to_tensor=True)
    
    # Compute cosine similarities
    cosine_scores = util.cos_sim(text_embedding, skill_embeddings)[0]
    
    results = []
    for idx, score in enumerate(cosine_scores):
        if score >= threshold:
            results.append({
                "skill": all_skills[idx],
                "score": float(score),
                "mentions": 1, # Heuristic for semantic match
                "in_recent_experience": True # Heuristic
            })
    
    # Sort by relevance
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

def classify_jd_semantic(jd_text: str, domain: Domain) -> dict:
    """
    Uses semantic similarity to categorize JD skills into Required vs Preferred.
    """
    # Thresholds: if similarity > 0.7 -> Required, 0.5-0.7 -> Preferred
    # Low threshold for document-to-word comparison
    matches = semantic_extract(jd_text, domain, threshold=0.35)
    
    required = []
    preferred = []
    
    for m in matches:
        if m["score"] >= 0.75:
            required.append(m["skill"])
        else:
            preferred.append(m["skill"])
            
    return {"required": required, "preferred": preferred}
