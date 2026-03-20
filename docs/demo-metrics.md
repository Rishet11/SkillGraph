# Demo Metrics

These are the metrics the judges should see:

- `redundant_modules_eliminated`
  - percentage reduction from the full-domain naive path to the recommended path
- `naive_path_length`
  - total domain skill count used as the naive baseline
- `recommended_path_length`
  - actual dependency-aware path length
- `reasoning_trace_coverage`
  - should be `100%` when every path node has a deterministic trace

## Demo framing

### Junior SWE -> Senior SWE

- candidate already knows Python, HTML/CSS, JavaScript, Git, SQL, and some OOP
- system should skip basics and focus on production-readiness gaps
- key dependency story: Linux/CLI before Docker, System Design before Microservices

### Junior Data Analyst -> ML Engineer

- candidate already knows SQL, Pandas, Python, and basic visualization
- system should preserve existing analysis skills and build the ML stack upward
- key dependency story: Statistics/Linear Algebra before ML, MLOps before Model Deployment

