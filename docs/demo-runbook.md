# Demo Runbook

## Goal

Record a 2-3 minute demo using only the tested fixed scenarios.

## Recommended sequence

1. Open the app on the landing/input screen.
2. Select the fixed `demo-data` or `demo-swe` scenario.
3. Explain that the system uses a fixed taxonomy and deterministic adaptive pathing.
4. Run the analysis.
5. Show:
   - domain
   - gap count
   - skill panel
   - graph panel
   - path + reasoning trace
6. Click `Mark learned` on the first recommended skill.
7. Show that the path and graph recompute immediately.
8. Close with:
   - fixed course catalog
   - zero hallucination claim
   - adaptive logic is original implementation

## Evidence to capture

- one screenshot showing the reasoning trace
- one screenshot showing the graph with selected path nodes
- one screenshot showing the post-recompute path
- one screenshot showing the metrics cards

## Included artifacts

- Landing page: `docs/screenshots/homepage.png`
- Data demo result: `docs/screenshots/data-demo.png`
- Data demo after recompute: `docs/screenshots/data-demo-recomputed.png`
- SWE demo result: `docs/screenshots/swe-demo.png`
- Slide deck: `docs/deck/SkillGraph_Hackathon_Deck.pptx`
