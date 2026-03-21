#!/usr/bin/env bash

# Source this file before running the demo backend.
# Example:
#   source backend/scripts/demo_preset.sh
#   .venv/bin/uvicorn app.main:app --reload

export SKILLGRAPH_API_VERSION="v1"
export SKILLGRAPH_REQUIRED_THRESHOLD="0.65"
export SKILLGRAPH_PREFERRED_THRESHOLD="0.50"
export SKILLGRAPH_MISSING_DELTA="0.35"
export SKILLGRAPH_WEAK_DELTA="0.15"

echo "SkillGraph demo preset loaded."
