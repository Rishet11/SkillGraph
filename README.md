# SkillGraph - AI-Adaptive Learning Path Engine

Paste your resume and a job description. Get a personalized, dependency-aware skill roadmap powered by Graph Neural Networks.

---

## What It Does

SkillGraph identifies the exact skills you need to bridge the gap between your current experience and a target role. It:

1. **Parses** your resume and job description to extract skills using local semantic search
2. **Scores your mastery** for each skill using a weighted formula (how often, how recently, how relevant)
3. **Identifies gaps** - skills required by the JD that you haven't mastered yet
4. **Builds a learning path** - ordered by a trained ML ranker, respecting prerequisite dependencies
5. **Maps curated resources** - from a fixed 45-course catalog, zero hallucination

---

## How It Works - 8-Layer Architecture

| Layer | Component | Function |
|-------|-----------|----------|
| 1 | `all-MiniLM-L6-v2` (local) | Semantic skill extraction from resume and JD text |
| 2 | Gemini 1.5 Flash (optional fallback) | Deep classification for sparse or low-confidence documents |
| 3 | NetworkX DAG | Skill gap identification - flags skills where mastery < 0.6 and JD requires them |
| 4 | Node2Vec GNN (trained) | Graph Neural Network that learns structural importance of each skill in the dependency graph |
| 5 | LightGBM LambdaRank (trained) | Ranks gap skills by learning priority using GNN scores, mastery, and JD weight |
| 6 | Greedy Frontier Traversal | Generates a prerequisite-safe path - never suggests a skill before its prerequisites |
| 7 | Course Catalog Lookup | Maps each path step to a curated resource (Coursera, official docs, etc.) |
| 8 | Deterministic Reasoning Trace | Plain-English explanation for every recommendation - rule-based, zero LLM |

---

## Trained Models

### Node2Vec Graph Neural Network
- Learns a **64-dimensional embedding** for each skill based on its position in the skill dependency graph
- Trained on O\*NET-derived skill dependency graphs for Software Engineering and Data Science domains
- Output: a structural importance score per skill, used as a feature in the ranker

### LightGBM LambdaRank
- Ranks the learning path by priority - given your skill gaps, which should you learn first?
- Trained on **500 synthetic candidate profiles** generated from the graph algorithm
- Features: JD importance, GNN score, mastery level, skill in-degree, skill out-degree
- **Validation results:**
  - **NDCG@5: 0.7978** - the top 5 recommended skills are correctly prioritized ~80% of the time
  - **NDCG@10: 0.8486** - the top 10 recommendations are in the right order ~85% of the time

  > **What is NDCG?** NDCG (Normalized Discounted Cumulative Gain) is an industry-standard metric for measuring ranking quality. A score of 1.0 means perfect ordering. Scores of 0.80-0.85 indicate the model reliably surfaces the most impactful skills first.

### Gemini 1.5 Flash *(classifier-only, pre-trained)*
- Used only as a fallback classifier when local semantic search returns sparse results
- Maps resume/JD text to a **predefined skill list only** - it cannot invent skill or course names

---

## Skill-Gap Scoring Logic

```
Mastery(skill)  = 0.31 * frequency  +  0.336 * recency  +  0.354 * jd_match

Gap             = skill required by JD  AND  Mastery(skill) < 0.6

Priority(skill) = LightGBM([jd_importance, gnn_score, mastery, in_degree, out_degree])

Path            = greedy frontier traversal - always pick the highest-priority skill
                  whose prerequisites are all satisfied
```

---

## Datasets and Sources

| Dataset | Purpose |
|---------|---------|
| [O\*NET Occupational Database](https://www.onetonline.org/) (SOC 15-1252.00 and 15-2051.00) | Skill taxonomy and dependency edges for SWE and Data Science domains |
| [Kaggle Resume Dataset](https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset) (2,400 resumes, 25 categories) | Validated skill list coverage against real-world resumes |
| [Kaggle JD Dataset](https://www.kaggle.com/datasets/kshitizregmi/jobs-and-job-description) | Validated JD skill pattern extraction |
| Synthetic profiles (500) | Generated from graph algorithm; used to train the LightGBM LambdaRank model |

---

## Quick Start (Docker) - Recommended for Judges

```bash
docker-compose up -d
```

Then open:
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000/docs](http://localhost:8000/docs)

> All dependencies (LightGBM OpenMP, Python, Node.js) are pre-configured inside Docker.

---

## Manual Setup (Local Development)

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

### 3. Run Model Training *(first time only, ~15 minutes)*
```bash
bash backend/training/run_all_training.sh
```

### 4. Optional: Enable Gemini fallback
```bash
export GEMINI_API_KEY=your_key
export SKILLGRAPH_ENABLE_GEMINI=1
```

### macOS only - Required for LightGBM
```bash
export DYLD_LIBRARY_PATH="/opt/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH"
```

---

## Proof of Training

All training artifacts are included in the repository:

| Artifact | Location |
|----------|----------|
| Training scripts (Node2Vec + LightGBM) | `backend/training/` |
| Synthetic training data (500 profiles) | `backend/training/synthetic_data.json` |
| NDCG scores and feature importance report | `backend/models/training_summary.md` |

---

## Zero Hallucination by Design

All course recommendations come from a **fixed 45-course catalog** via deterministic lookup. The LLM is used only as a classifier - it maps text to a predefined skill list and **cannot generate** course names, skill names, or any free-form content. If Gemini is disabled, the system falls back to local semantic search seamlessly.
