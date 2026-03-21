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

def classify_resume_skills(resume_text: str, domain: Domain) -> list[dict]:
    llm_result = classify_with_gemini(resume_text, domain, mode="resume")
    if isinstance(llm_result, list):
        normalized = []
        allowed = set(load_skills(domain))
        for item in llm_result:
            skill = item.get("skill")
            if skill in allowed:
                normalized.append(
                    {
                        "skill": skill,
                        "mentions": int(item.get("mentions", 1)),
                        "in_recent_experience": bool(item.get("in_recent_experience", False)),
                    }
                )
        if normalized:
            normalized.sort(key=lambda item: (-item["mentions"], item["skill"]))
            return normalized

    # V2 Upgrade: Semantic Extraction replaces Keyword Falling
    return semantic_extract(resume_text, domain)


def classify_jd(jd_text: str, domain: Domain) -> JDData:
    llm_result = classify_with_gemini(jd_text, domain, mode="jd")
    if isinstance(llm_result, dict):
        allowed = set(load_skills(domain))
        required = [skill for skill in llm_result.get("required", []) if skill in allowed]
        preferred = [skill for skill in llm_result.get("preferred", []) if skill in allowed and skill not in required]
        if required or preferred:
            return JDData(required=required, preferred=preferred)

    # V2 Upgrade: Semantic JD Classification replaces block extraction
    res = classify_jd_semantic(jd_text, domain)
    return JDData(required=res["required"], preferred=res["preferred"])


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
