# SkillGraph — AI-Adaptive Onboarding Engine

AI-adaptive onboarding engine using graph-based skill gap analysis and trained ML models.

### Topics: `machine-learning`, `fastapi`, `nextjs`, `graph-neural-network`, `adaptive-learning`

## What It Does
SkillGraph parses a resume and job description, computes a personalized skill gap using a weighted mastery formula, and generates a dependency-aware learning path using graph-based adaptive pathing. Every recommendation comes from a fixed course catalog — zero hallucination.

## Architecture
Layer 1: Semantic Search — `all-MiniLM-L6-v2` local vector embeddings for instant skill matching
Layer 2: Gemini 1.5 Flash — "Deep Thinker" fallback for low-confidence or sparse document contexts
Layer 3: Gap Identification — NetworkX DAG subgraph of skills where mastery < 0.6 AND required by JD
Layer 4: Node2Vec GNN — trained on skill dependency DAG, produces structural importance score per skill
Layer 5: LightGBM Ranker — LambdaRank trained on 500 synthetic profiles, scores skill priority
Layer 6: Greedy Frontier Traversal — original adaptive logic, prerequisite-safe path generation
Layer 7: Course Mapping — fixed catalog lookup, maximizes gap skill coverage per step
Layer 8: Deterministic Reasoning Trace — rule-based explanation per path node, no LLM involved

## Models Used
- Node2Vec (trained): unsupervised GNN on skill dependency DAG, 64-dim embeddings, L2 norm as structural importance score. Trained on O*NET-derived skill graphs for SWE and Data domains.
- LightGBM LambdaRank (trained): priority ranker trained on 500 synthetic candidate profiles. Features: JD importance, GNN score, mastery, in-degree, out-degree. NDCG@5: 0.7978, NDCG@10: 0.8486.
- Gemini 1.5 Flash (pre-trained): classifier-only. Maps resume and JD text to predefined skill list. Never generates course names or skill names.

## Datasets Used
- O*NET Occupational Database: skill taxonomy for SWE (15-1252.00) and Data Scientist (15-2051.00). Source for all skill lists and dependency edges.
- Kaggle Resume Dataset (snehaanbhawal/resume-dataset): validated skill taxonomy coverage against 2400 real resumes across 25 job categories.
- Kaggle JD Dataset (kshitizregmi/jobs-and-job-description): validated JD skill patterns against real job descriptions.
- Synthetic path data: 500 candidate profiles generated from graph algorithm. Used as LightGBM LambdaRank training data.

## Skill-Gap Analysis Logic
Mastery(s) = 0.31 * frequency + 0.336 * recency + 0.354 * jd_match
Gap: skill in JD AND mastery < 0.6
Priority(s) = LightGBM([jd_importance, gnn_score, mastery, in_degree, out_degree])
Path: greedy frontier traversal — pick highest-priority node with all prerequisites satisfied

## Quick Start (Docker) — Recommended for Judges

The easiest way to run SkillGraph is using Docker. This ensures all system dependencies (like LightGBM's OpenMP) are correctly configured.

1. **Start the environment**:
   ```bash
   docker-compose up -d
   ```

2. **Access the Application**:
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000](http://localhost:8000)

---

## 🛠 Manual Setup (Local Development)

### 1. Install backend dependencies
cd backend && pip install -r requirements.txt

### 2. Install frontend dependencies
cd frontend && npm install

### 3. Run training (First time only, ~15 minutes)
bash backend/training/run_all_training.sh

### 4. Start backend
cd backend && uvicorn app.main:app --reload

### 5. Start frontend
cd frontend && npm run dev

### 6. Environment variables (Optional — enables Gemini)
export GEMINI_API_KEY=your_key
export SKILLGRAPH_ENABLE_GEMINI=1

### macOS only (Required for local LightGBM build)
export DYLD_LIBRARY_PATH="/opt/homebrew/opt/libomp/lib:$DYLD_LIBRARY_PATH"

## Adaptive Logic
The adaptive pathing layer is an original implementation. Greedy frontier traversal on a directed acyclic skill dependency graph. At each step, the algorithm selects the highest-priority node from skills whose prerequisites are all satisfied. Priority is scored by a trained LightGBM ranker using GNN structural embeddings and mastery. When a user marks a skill as learned, mastery updates to 1.0 and the full path recomputes.

## Grounding and Reliability
All course recommendations are selected from a fixed 48-course catalog via deterministic lookup. The LLM is constrained to classify into the predefined skill list only — it cannot generate course names, skill names, or any free-form content. Zero hallucination by construction.

## 📊 Evaluation & Proof of Training
For formal evaluation:
- **Scripts**: See `backend/training/` for GNN and LightGBM training logic.
- **Dataset**: See `backend/training/synthetic_data.json` for the generated profile dataset.
- **Metrics**: See `backend/models/training_summary.md` for a summary of NDCG scores and feature importance.
