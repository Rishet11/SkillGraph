from __future__ import annotations

import json
import os
import torch
from typing import Optional
from .llm_classifier import classify_with_gemini
from .semantic_matcher import get_model, util
from .data_loader import Domain

# Core Industry Centroids for Auto-Detection
INDUSTRIES = {
    "Technology/Software": [
        "Software Engineer", "Frontend", "Backend", "Fullstack", "DevOps", 
        "Cloud Architect", "SRE", "Security Engineer", "Mobile Developer"
    ],
    "Data/AI": [
        "Data Scientist", "Machine Learning Engineer", "Data Engineer", 
        "Data Analyst", "AI Researcher", "NLP Scientist", "MLOps"
    ],
    "Healthcare/Clinical": [
        "Nurse", "Doctor", "Clinical Research", "Pharmacist", 
        "Medical Assistant", "Health Administration", "Patient Care"
    ],
    "Marketing/Sales": [
        "Digital Marketing", "SEO Specialist", "Content Strategist", 
        "Sales Executive", "Account Manager", "Brand Manager"
    ],
    "Finance/Banking": [
        "Financial Analyst", "Investment Banker", "Risk Manager", 
        "Accountant", "Quantitative Analyst", "Portfolio Manager"
    ],
    "HR/Operations": [
        "Recruiter", "Operations Manager", "Supply Chain", 
        "Talent Acquisition", "Employee Relations"
    ]
}

_industry_embeddings = None

def detect_industry(text: str) -> str:
    """
    Uses semantic embeddings to classify a JD/Resume into one of the core industries.
    """
    global _industry_embeddings
    model = get_model()
    
    industry_names = list(INDUSTRIES.keys())
    if _industry_embeddings is None:
        # Pre-compute centroids
        _industry_embeddings = []
        for ind in industry_names:
            # Encode keywords as the industry "centroid"
            centroid_text = " ".join(INDUSTRIES[ind])
            _industry_embeddings.append(model.encode(centroid_text, convert_to_tensor=True))
        _industry_embeddings = torch.stack(_industry_embeddings)
        
    text_emb = model.encode(text, convert_to_tensor=True)
    cos_scores = util.cos_sim(text_emb, _industry_embeddings)[0]
    
    best_idx = int(torch.argmax(cos_scores))
    if cos_scores[best_idx] > 0.4:
        return industry_names[best_idx]
    
    # Fallback to general detection if low confidence
    return "Technology/Software"

def get_skill_ontology(skill_name: str, industry: str) -> list[str]:
    """
    Just-in-Time (JIT) Prerequisite discovery.
    First checks local JSON caches, then calls Gemini for real-time graphing.
    """
    # 1. Check existing specialized JSONs
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Map industry to known files
    domain_map = {
        "Technology/Software": "swe",
        "Data/AI": "data",
        "HR/Operations": "hr"
    }
    
    domain_suffix = domain_map.get(industry)
    if domain_suffix:
        edge_path = os.path.join(base, 'data', f'edges_{domain_suffix}.json')
        if os.path.exists(edge_path):
            with open(edge_path) as f:
                edges = json.load(f)
                # Simple extraction of prerequisites from existing edge list
                prereqs = [e[0] for e in edges if e[1].lower() == skill_name.lower()]
                if prereqs:
                    return prereqs

    # 2. Fallback to Gemini for JIT Graph Generation
    prompt = f"Identify the direct prerequisites for the skill '{skill_name}' in the '{industry}' industry. Return a simple comma-separated list of 3-5 foundation skills."
    
    # We call Gemini in a simplified mode for JIT
    try:
        response = classify_with_gemini(f"Prereqs for {skill_name} in {industry}", "swe", mode="prereqs") # We use a mock mode
        if isinstance(response, list):
            return response
    except:
        pass
        
    return [] # Fail gracefully
