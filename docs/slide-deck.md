# SkillGraph — 5-Slide Deck

## Slide 1 — Solution Overview

- One-line pitch: explainable adaptive onboarding from skill graph + mastery scoring
- Pain: static onboarding wastes expert time and overwhelms juniors
- Solution: parse resume + JD, compute mastery, build gap subgraph, generate targeted path
- Show the 3-panel UI screenshot

## Slide 2 — Architecture & Workflow

- Resume + JD -> parser
- classifier -> mastery scorer
- gap identifier -> gap subgraph
- priority scoring -> frontier traversal
- course mapper -> reasoning trace -> UI
- Call out domain-based DAG and fixed catalog grounding

## Slide 3 — Tech Stack & Models

- Backend: FastAPI
- Graph engine: DAG traversal with NetworkX-compatible interface
- Frontend: Next.js + TypeScript
- Data: O*NET-grounded domain taxonomy
- Models: current build uses deterministic classification; classifier-only LLM can be swapped in later
- Emphasize: no course generation, no hallucinated outputs

## Slide 4 — Algorithms & Training

- Show mastery formula
- Show priority formula
- Explain frontier-based traversal
- Show one reasoning trace example
- State clearly: adaptive logic is original implementation; no custom trained model required

## Slide 5 — Datasets & Metrics

- Domains: SWE and Data
- Inputs: fixed demo personas
- Grounding: fixed course catalog
- Metrics:
  - redundant modules eliminated
  - naive path length vs recommended path length
  - reasoning trace coverage
- State scope honestly: prototype currently covers two domains only

