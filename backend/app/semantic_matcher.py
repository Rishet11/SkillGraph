from __future__ import annotations

import re
import torch
from functools import lru_cache
from sentence_transformers import SentenceTransformer, util
from .data_loader import Domain, load_skills

# ─────────────────────────────────────────────────────────────────────────────
#  SKILL DESCRIPTIONS
#  The key insight: instead of embedding the bare skill name (e.g. "Python"),
#  we embed a rich natural-language description that includes abbreviations,
#  synonyms, and tool names.  This way the transformer model understands:
#    - "py"  → Python
#    - "ml"  → Machine Learning
#    - "js"  → JavaScript
#    - "postgres" → SQL
#  … because "py is a Python abbreviation" has high semantic similarity to
#  a resume sentence like "3 yrs py/flask experience".
# ─────────────────────────────────────────────────────────────────────────────
SKILL_DESCRIPTIONS: dict[str, str] = {
    # ── SWE ──────────────────────────────────────────────────────────────────
    "Python":
        "Python programming language, py, python3, flask, fastapi, django, scripting",
    "JavaScript":
        "JavaScript, js, ES6, ES2015, vanilla JS, web scripting, frontend scripting",
    "TypeScript":
        "TypeScript, ts, typed JavaScript, strongly typed JS",
    "React":
        "React, ReactJS, React.js, react hooks, component-based UI, frontend framework",
    "Node.js":
        "Node.js, nodejs, node js, server-side JavaScript, express.js, backend JS",
    "HTML/CSS":
        "HTML, CSS, html5, css3, sass, scss, web markup, styling, frontend",
    "Git":
        "Git, GitHub, GitLab, BitBucket, version control, source control, vcs",
    "Docker":
        "Docker, containerization, containers, dockerfile, docker-compose",
    "REST APIs":
        "REST API, RESTful, HTTP API, web services, API endpoints, JSON API",
    "GraphQL":
        "GraphQL, gql, graph query language, apollo",
    "SQL":
        "SQL, mysql, postgresql, postgres, sqlite, relational database, database queries, orm",
    "Databases (NoSQL)":
        "NoSQL, mongodb, mongo, dynamodb, cassandra, document database, non-relational",
    "CI/CD":
        "CI/CD, cicd, continuous integration, continuous delivery, github actions, jenkins, gitlab ci, devops pipelines",
    "Linux/CLI":
        "Linux, CLI, bash, shell, terminal, unix, command line, zsh, scripting",
    "Testing":
        "testing, unit tests, pytest, jest, mocha, tdd, test driven development, integration testing",
    "Cloud Basics":
        "cloud, AWS, GCP, Azure, google cloud, amazon web services, cloud infrastructure, s3, ec2",
    "Microservices":
        "microservices, microservice architecture, service-oriented, distributed services",
    "Caching (Redis)":
        "Redis, memcached, caching, cache, in-memory store",
    "Message Queues":
        "Kafka, RabbitMQ, message queue, pub sub, SQS, event streaming",
    "System Design":
        "system design, distributed systems, scalability, high availability, load balancing, architecture",
    "Security Basics":
        "security, OAuth, JWT, authentication, authorization, HTTPS, cryptography, OWASP",
    "OOP":
        "OOP, object oriented programming, object-oriented, classes, inheritance, polymorphism",
    "Data Structures":
        "data structures, arrays, linked lists, trees, graphs, hash maps, stacks, queues",
    "Algorithms":
        "algorithms, sorting, searching, dynamic programming, complexity, big-O, recursion",
    "Operating Systems":
        "operating systems, OS, processes, threads, memory management, scheduling",
    "Computer Networks":
        "networking, computer networks, TCP/IP, HTTP, DNS, protocols, sockets",
    "Design Patterns":
        "design patterns, MVC, SOLID, factory pattern, observer pattern, singleton",
    "Clean Code":
        "clean code, code quality, refactoring, code review",

    # ── Data Science ─────────────────────────────────────────────────────────
    "Statistics":
        "statistics, statistical analysis, hypothesis testing, p-value, descriptive statistics",
    "Probability":
        "probability, probabilistic models, distributions, bayesian probability",
    "Linear Algebra":
        "linear algebra, matrix operations, vectors, eigenvalues, numpy linear algebra",
    "NumPy":
        "NumPy, numpy, numerical python, nd-array, array operations",
    "Pandas":
        "Pandas, pandas, dataframes, data wrangling, data manipulation, series",
    "Machine Learning Fundamentals":
        "machine learning, ML, ml algorithms, scikit-learn, sklearn, supervised learning, unsupervised learning",
    "Feature Engineering":
        "feature engineering, feature selection, feature extraction, data features",
    "Supervised Learning":
        "supervised learning, classification, regression, decision tree, random forest, svm, gradient boosting, xgboost",
    "Model Evaluation":
        "model evaluation, cross-validation, precision, recall, F1 score, ROC, AUC, confusion matrix",
    "Deep Learning":
        "deep learning, DL, neural networks, pytorch, tensorflow, keras, gpu training",
    "Neural Networks":
        "neural networks, CNN, RNN, LSTM, GRU, transformer model, attention mechanism",
    "NLP":
        "NLP, natural language processing, text classification, named entity recognition, sentiment analysis, BERT, spacy, nltk",
    "Data Engineering":
        "data engineering, data pipelines, ETL, data ingestion, batch processing, spark",
    "ETL Pipelines":
        "ETL, extract transform load, data orchestration, airflow, data pipeline, luigi",
    "LLMs":
        "LLM, large language models, GPT, ChatGPT, prompt engineering, openai, langchain, llama, fine-tuning",
    "Vector Databases":
        "vector database, embeddings, semantic search, faiss, pinecone, weaviate, chroma",
    "MLOps":
        "MLOps, ml ops, model registry, mlflow, model monitoring, model versioning, kubeflow",
    "Model Deployment":
        "model deployment, model serving, inference, triton, torchserve, onnx, production ML",
    "Data Visualization":
        "data visualization, matplotlib, seaborn, plotly, tableau, power bi, charts, dashboards",
    "Bayesian Methods":
        "bayesian methods, bayesian inference, bayesian statistics, prior posterior, mcmc",
}

# ─────────────────────────────────────────────────────────────────────────────
#  ABBREVIATION EXPANDER
#  Applied as a pre-processing step before embedding.
#  Expands common abbreviations in the raw text so the model sees the full term.
# ─────────────────────────────────────────────────────────────────────────────
ABBREVIATION_MAP: dict[str, str] = {
    r"\bpy\b": "python",
    r"\bjs\b": "javascript",
    r"\bts\b": "typescript",
    r"\bml\b": "machine learning",
    r"\bdl\b": "deep learning",
    r"\bnlp\b": "natural language processing",
    r"\bllm\b": "large language model",
    r"\bllms\b": "large language models",
    r"\bci/cd\b": "continuous integration continuous delivery",
    r"\bcicd\b": "continuous integration continuous delivery",
    r"\bdevops\b": "devops continuous integration",
    r"\boop\b": "object oriented programming",
    r"\bsql\b": "structured query language sql",
    r"\bnosql\b": "nosql non-relational database",
    r"\bapi\b": "application programming interface api",
    r"\baws\b": "amazon web services cloud",
    r"\bgcp\b": "google cloud platform",
    r"\bk8s\b": "kubernetes",
    r"\bvcs\b": "version control git",
}


def expand_abbreviations(text: str) -> str:
    """Expand common abbreviations so the transformer recognises them."""
    result = text
    for pattern, replacement in ABBREVIATION_MAP.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  MODEL & EMBEDDING CACHE
# ─────────────────────────────────────────────────────────────────────────────
_model: SentenceTransformer | None = None
_skill_embeddings: dict[str, torch.Tensor] = {}  # keyed by domain


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


@lru_cache(maxsize=4)
def get_skill_descriptions(domain: Domain) -> tuple[list[str], list[str]]:
    """
    Returns (canonical_skill_names, description_strings) for the domain.
    Descriptions are cached — they are the embedding keys, not raw names.
    """
    skills = load_skills(domain)
    descs = [
        SKILL_DESCRIPTIONS.get(skill, skill)  # fall back to skill name if no description
        for skill in skills
    ]
    return skills, descs


def get_skill_embeddings(domain: Domain) -> tuple[list[str], torch.Tensor]:
    """Embed skill descriptions once and cache them."""
    if domain not in _skill_embeddings:
        model = get_model()
        skills, descs = get_skill_descriptions(domain)
        _skill_embeddings[domain] = (skills, model.encode(descs, convert_to_tensor=True))
    return _skill_embeddings[domain]  # type: ignore[return-value]


# ─────────────────────────────────────────────────────────────────────────────
#  SENTENCE SPLITTER
# ─────────────────────────────────────────────────────────────────────────────
def split_sentences(text: str) -> list[str]:
    """
    Split document text into individual sentences.
    Each sentence is a self-contained context window for the transformer.
    """
    # Split on newlines, periods, semicolons, bullet characters
    raw = re.split(r'[\n\r]+|(?<=[.!?;•])\s+', text.strip())
    sentences = [s.strip() for s in raw if len(s.strip()) > 3]
    return sentences or [text[:500]]


# ─────────────────────────────────────────────────────────────────────────────
#  CORE EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────
def semantic_extract(text: str, domain: Domain, threshold: float = 0.40) -> list[dict]:
    """
    Transformer-based skill extraction.

    How it works:
    1. Pre-process: expand abbreviations (py→python, ml→machine learning, etc.)
    2. Split the text into sentences — each sentence is a focused context window.
    3. Embed all sentences with all-MiniLM-L6-v2.
    4. Embed skill DESCRIPTIONS (rich phrases, not bare names) — pre-cached.
    5. Compute cosine similarity: (n_sentences × n_skills).
    6. For each skill, take MAX similarity across all sentences.
    7. Sentences above threshold count as "mentions"; position → recency.

    This approach handles:
    - Case variations: the model is case-insensitive by design.
    - Abbreviations: pre-processor expands them before embedding.
    - Contextual mentions: "built a py microservice" → matches Python.
    - Synonym/tool names: "sklearn" → matches "Machine Learning Fundamentals".
    """
    if not text or not text.strip():
        return []

    model = get_model()
    skills, skill_embs = get_skill_embeddings(domain)

    # Step 1: expand abbreviations
    expanded = expand_abbreviations(text)

    # Step 2: split into sentences
    sentences = split_sentences(expanded)
    total = max(1, len(sentences))
    recency_cutoff = total // 2  # top half of document = recent experience

    # Step 3: embed sentences
    sentence_embs = model.encode(sentences, convert_to_tensor=True)  # (n_sents, dim)

    # Step 4: similarity matrix
    sim_matrix = util.cos_sim(sentence_embs, skill_embs)  # (n_sents, n_skills)

    # Step 5: aggregate per skill
    max_scores, _ = sim_matrix.max(dim=0)                                  # (n_skills,)
    mention_counts = (sim_matrix >= threshold).sum(dim=0)                  # (n_skills,)
    recent_hits = (sim_matrix[:recency_cutoff] >= threshold).any(dim=0)    # (n_skills,)

    results = []
    for idx, score in enumerate(max_scores):
        if float(score) >= threshold:
            results.append({
                "skill": skills[idx],
                "score": float(score),
                "mentions": max(1, int(mention_counts[idx].item())),
                "in_recent_experience": bool(recent_hits[idx].item()),
            })

    results.sort(key=lambda x: (-x["mentions"], -x["score"]))
    return results


def classify_jd_semantic(jd_text: str, domain: Domain) -> dict:
    """
    Classify JD skills into Required vs Preferred.
    Skills with high similarity (model-determined) → Required.
    Borderline matches → Preferred.
    """
    matches = semantic_extract(jd_text, domain, threshold=0.38)

    required = []
    preferred = []
    for m in matches:
        if m["score"] >= 0.60 or m["mentions"] >= 2:
            required.append(m["skill"])
        else:
            preferred.append(m["skill"])

    return {"required": required, "preferred": preferred}
