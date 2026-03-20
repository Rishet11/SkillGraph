# SkillGraph

SkillGraph is a local-first hackathon MVP for explainable role-fit analysis.

It compares a candidate resume with a target job description, extracts skills, measures role fit, identifies prerequisite gaps, and generates a learning roadmap. The goal is to make onboarding recommendations explainable instead of black-box.

## What it does

- Accepts resume and job description input through upload or pasted text
- Extracts canonical skills from both documents
- Scores mastery and overall fit with deterministic logic
- Highlights matched skills, missing skills, and adjacent prerequisite gaps
- Builds a simple skill graph for explanation during demos
- Recommends courses from a curated local catalog
- Includes sample candidate and role inputs for demo-safe flows

## Stack

- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- Data: local JSON files and text samples
- Tests: pytest for backend

## Project structure

```text
frontend/   Next.js app
backend/    FastAPI service
data/       Skills, edges, courses, weights, sample inputs
docs/       Demo notes and scoring explanation
```

## Local setup

### 1. Backend

```bash
python3 -m venv .venv
./.venv/bin/python3 -m pip install -r backend/requirements.txt
./.venv/bin/python3 -m uvicorn backend.app.main:app --reload
```

Backend runs on `http://127.0.0.1:8000`.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://127.0.0.1:3000`.

## Verification

Backend tests:

```bash
./.venv/bin/python3 -m pytest backend/tests
```

Frontend production build:

```bash
cd frontend
npm run build
```

## Core API

- `GET /health` - health check
- `GET /samples` - list bundled sample resumes and job descriptions
- `GET /samples/{id}` - fetch one sample input
- `POST /analyze` - analyze text or uploaded files

## Demo flow

1. Open the app and position SkillGraph as an explainable onboarding engine.
2. Load one sample resume and one sample role.
3. Run the analysis.
4. Walk through fit score, matched skills, gaps, graph, and learning path.
5. Use real uploads only after the sample path is stable.

## Current scope

Implemented:

- Local-first MVP
- Deterministic extraction and scoring
- Upload and text fallback flow
- Sample-based hackathon demo flow
- Explainable graph and learning path

Not implemented yet:

- Persistent storage
- Authentication
- Production deployment config
- Advanced LLM reasoning pipeline
- Recruiter workflow and collaboration features

## Notes

- Next.js is pinned to a patched `15.x` release.
- The backend is the source of truth for scoring, graph construction, and recommendations.
- LLM enrichment is scaffolded as optional future work, but the current MVP stays deterministic.
