from __future__ import annotations

import re
from functools import lru_cache

from .data_loader import Domain, load_skills
from .llm_classifier import classify_with_gemini
from .schemas import JDData


MANUAL_ALIASES: dict[str, list[str]] = {
    "CI/CD": ["ci/cd", "cicd", "pipeline", "pipelines"],
    "Linux/CLI": ["linux", "cli", "terminal", "shell"],
    "HTML/CSS": ["html", "css", "html/css"],
    "REST APIs": ["rest api", "rest apis", "restful api", "api development"],
    "Node.js": ["node.js", "nodejs", "node js"],
    "Databases (NoSQL)": ["nosql", "mongodb", "document database"],
    "Caching (Redis)": ["redis", "cache", "caching"],
    "Message Queues": ["message queue", "message queues", "kafka", "rabbitmq"],
    "Cloud Basics": ["cloud", "aws", "gcp", "azure"],
    "Security Basics": ["security", "application security", "auth"],
    "TypeScript": ["typescript", "ts"],
    "OOP": ["oop", "object oriented programming", "object-oriented programming"],
    "Data Visualization": ["data visualization", "dashboard", "dashboards", "visualization"],
    "Machine Learning Fundamentals": ["machine learning fundamentals", "machine learning", "ml fundamentals", "ml"],
    "Feature Engineering": ["feature engineering", "feature selection"],
    "Model Evaluation": ["model evaluation", "cross validation", "precision", "recall", "roc"],
    "Deep Learning": ["deep learning", "dl"],
    "Neural Networks": ["neural networks", "neural network", "cnn", "rnn"],
    "NLP": ["nlp", "natural language processing"],
    "Data Engineering": ["data engineering", "data pipeline", "data pipelines"],
    "ETL Pipelines": ["etl", "etl pipelines", "data orchestration"],
    "LLMs": ["llm", "llms", "large language models", "prompt engineering", "gpt"],
    "Vector Databases": ["vector database", "vector databases", "embeddings", "semantic search"],
    "NumPy": ["numpy"],
    "Pandas": ["pandas", "dataframe", "dataframes"],
    "MLOps": ["mlops", "ml ops"],
    "Model Deployment": ["model deployment", "deployment", "inference endpoint"],
}


@lru_cache(maxsize=2)
def build_aliases(domain: Domain) -> dict[str, list[str]]:
    aliases: dict[str, list[str]] = {}
    for skill in load_skills(domain):
        normalized = skill.lower()
        generated = {
            normalized,
            normalized.replace("/", " "),
            normalized.replace("-", " "),
            normalized.replace("(", "").replace(")", ""),
        }
        generated.update(MANUAL_ALIASES.get(skill, []))
        aliases[skill] = sorted(alias for alias in generated if alias.strip())
    return aliases


from .semantic_matcher import semantic_extract, classify_jd_semantic
from .ontology import detect_industry

def classify_resume_skills(resume_text: str, domain: Domain = None) -> list[dict]:
    # V2 Upgrade: Auto-Industry Detection for "Universal" support
    if domain is None:
        detected = detect_industry(resume_text)
        # Map industry string to Domain enum for current logic
        domain = "swe" if "Technology" in detected else ("data" if "Data" in detected else "swe")
        print(f"Auto-Detected Domain: {domain} (from {detected})")

    # V2 Optimized: Local-First Semantic Extraction (Instant)
    local_results = semantic_extract(resume_text, domain)
    
    # If local results are sparse or confidence is low, uses Gemini for "Global Refinement"
    # This keeps the UI fast while leveraging LLM power for complex contexts
    if len(local_results) < 5 and gemini_enabled():
        llm_result = classify_with_gemini(resume_text, domain, mode="resume")
        if isinstance(llm_result, list):
            allowed = set(load_skills(domain))
            normalized = []
            for item in llm_result:
                skill = item.get("skill")
                if skill in allowed:
                    normalized.append({
                        "skill": skill,
                        "mentions": int(item.get("mentions", 1)),
                        "in_recent_experience": bool(item.get("in_recent_experience", False)),
                    })
            if normalized:
                return normalized

    return local_results


def classify_jd(jd_text: str, domain: Domain = None) -> JDData:
    # V2 Upgrade: Auto-Industry Detection
    if domain is None:
        detected = detect_industry(jd_text)
        domain = "swe" if "Technology" in detected else ("data" if "Data" in detected else "swe")
        print(f"Auto-Detected JD Domain: {domain} (from {detected})")

    # V2 Optimized: Local-First Semantic JD Classification
    res = classify_jd_semantic(jd_text, domain)
    required = set(res["required"])
    preferred = set(res["preferred"])

    # If parsing is extremely sparse, trigger Gemini for "Deep Context"
    if len(required) < 3 and gemini_enabled():
        llm_result = classify_with_gemini(jd_text, domain, mode="jd")
        if isinstance(llm_result, dict):
            allowed = set(load_skills(domain))
            req_llm = [skill for skill in llm_result.get("required", []) if skill in allowed]
            pref_llm = [skill for skill in llm_result.get("preferred", []) if skill in allowed and skill not in req_llm]
            if req_llm or pref_llm:
                return JDData(required=req_llm, preferred=pref_llm)

    # High-Recall Extraction: Alias-Aware Keyword Matching
    # This ensures items mentioned by name are always caught
    aliases_map = build_aliases(domain)
    for skill, aliases in aliases_map.items():
        if contains_any(jd_text, aliases):
            # If not already found by semantic, add to required
            if skill not in required and skill not in preferred:
                required.add(skill)

    return JDData(required=list(required), preferred=list(preferred))


def contains_any(text: str, aliases: list[str]) -> bool:
    return any(re.search(rf"\b{re.escape(alias)}\b", text, re.IGNORECASE) for alias in aliases)


def extract_block(text: str, starts: list[str], ends: list[str]) -> str:
    start_positions = [text.find(keyword) for keyword in starts if text.find(keyword) != -1]
    if not start_positions:
        return ""
    start = min(start_positions)
    end = len(text)
    for keyword in ends:
        position = text.find(keyword, start + 1)
        if position != -1:
            end = min(end, position)
    return text[start:end]
