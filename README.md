# SkillGraph — AI-Adaptive Onboarding Engine

SkillGraph is a hackathon-ready onboarding prototype that parses a candidate resume and a target job description, computes deterministic mastery scores over a fixed skill taxonomy, identifies the skill-gap subgraph, and generates a dependency-aware learning path grounded in a fixed course catalog.

## What It Does

SkillGraph supports two domains: `SWE` and `Data`. Given a resume and JD, it classifies skills into a predefined list, computes mastery from mention frequency, recency, and JD relevance, identifies unmet gaps, and produces a prioritized path with a deterministic reasoning trace.

## Live Demo

- Local app: `http://127.0.0.1:3000`
- API: `http://127.0.0.1:8000`
- Fixed demo scenarios are bundled in the app and exposed through `/samples`

## Architecture

```text
Resume + JD
   -> parser
   -> deterministic skill classifier
   -> mastery scorer
   -> gap identifier
   -> domain DAG / gap subgraph
   -> priority-aware traversal
   -> course mapper
   -> reasoning trace
   -> frontend 3-panel UI
```

## Skill-Gap Analysis Logic

### 1. Skill classification

- Skills are classified only into a fixed domain taxonomy.
- No free-form skill generation is allowed.
- The course catalog is fixed JSON; the system never invents courses.

### 2. Mastery formula

For each skill:

```text
mastery = 0.35 * frequency + 0.35 * recency + 0.30 * jd_match
```

Where:

- `frequency` = normalized mention count in the resume, capped at `1.0`
- `recency` = `1.0` if seen in recent experience, otherwise `0.5`
- `jd_match` = `1.0` if required by JD, `0.6` if preferred, else `0.0`

Gap rule:

```text
skill is a gap if it is required/preferred by the JD and mastery < 0.6
```

### 3. Priority formula

```text
priority(skill) = 0.4 * jd_importance + 0.4 * downstream_depth - 0.2 * mastery
```

Where:

- `jd_importance` = `1.0` if required, `0.6` if preferred, else `0.0`
- `downstream_depth` = longest dependency chain unlocked by that skill
- `mastery` = current deterministic mastery score

### 4. Traversal algorithm

The learning path uses a frontier-based greedy traversal:

- only skills with all unmet prerequisites satisfied enter the frontier
- the highest-priority frontier skill is selected next
- dependency constraints are never violated
- `Mark Learned` sets a skill mastery to `1.0` and recomputes the path

## Tech Stack

- Backend: FastAPI
- Graph engine: NetworkX with a local compatibility fallback for offline environments
- Frontend: Next.js 14 + TypeScript
- Data: fixed JSON taxonomies, edges, course catalog, demo scenarios
- Parsing: PDF/TXT/DOCX support

## Setup Instructions

### Backend

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r backend/requirements.txt
./.venv/bin/python -m uvicorn backend.app.main:app --reload
```

### Frontend

Use Node 22:

```bash
cd frontend
npm install
npm run dev
```

If your machine defaults to a newer Node version, switch to Node 22 first.

## API Endpoints

- `POST /parse`
- `POST /pathway`
- `POST /recompute`
- `POST /analyze`
- `GET /graph/{domain}`
- `GET /catalog/{domain}`
- `GET /samples`
- `GET /samples/{id}`
- `GET /health`

## Datasets & Models Used

- O*NET-grounded skill taxonomy, manually curated into `SWE` and `Data` domains
- Fixed prerequisite edges defined from the PRD
- Fixed course catalog grounded in public-learning style content
- Deterministic classification is the default demo path
- Gemini classifier-only integration is supported behind env flags and constrained to the fixed taxonomy

## Optional Gemini Classifier

SkillGraph does not require an LLM to run. If you want classifier-only Gemini support, set:

```bash
export SKILLGRAPH_ENABLE_GEMINI=1
export GEMINI_API_KEY=your_key_here
export SKILLGRAPH_GEMINI_MODEL=gemini-1.5-flash
```

Guardrails:

- Gemini is used only to classify text into the predefined domain taxonomy.
- It cannot invent new skills.
- It cannot invent new courses.
- If Gemini is disabled or fails, the backend falls back to deterministic classification.

## Adaptive Logic (Original Implementation)

The adaptive logic is original to this project:

- mastery computation
- gap detection
- gap subgraph construction
- priority scoring
- dependency-safe path traversal
- deterministic reasoning trace
- adaptive recompute after `Mark Learned`

## Repository Structure

```text
backend/  FastAPI API, parsing, mastery, graph, reasoning, pathway logic
frontend/ Next.js UI
data/     Skills, edges, courses, demo scenarios
docs/     Deck content, demo notes, metrics
```

## Submission Artifacts

- Final deck: `docs/deck/SkillGraph_Hackathon_Deck.pptx`
- Demo runbook: `docs/demo-runbook.md`
- Demo metrics: `docs/demo-metrics.md`
- Browser evidence:
  - `docs/screenshots/homepage.png`
  - `docs/screenshots/data-demo.png`
  - `docs/screenshots/data-demo-recomputed.png`
  - `docs/screenshots/swe-demo.png`

## Verification

Backend:

```bash
./.venv/bin/pytest backend/tests
```

Frontend:

```bash
cd frontend
npm run build
```

## Notes

- The system is grounded to a fixed course catalog to avoid hallucination.
- The current prototype covers only `SWE` and `Data`.
- The reasoning trace is deterministic and visible in the UI.
