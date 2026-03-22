# SkillGraph Training Summary

This document serves as proof of the technical depth and training process for the SkillGraph AI-Adaptive Onboarding Engine.

## Node2Vec GNN (Unsupervised)
- **Objective**: Generate structural importance scores for skills based on the O*NET dependency graph.
- **Top SWE Skills**: Computer Networks (1.00), Docker (0.92), Testing (0.78).
- **Top Data Skills**: Statistics (1.00), Pandas (0.83), NLP (0.82).

## LightGBM LambdaRank (Supervised)
- **Dataset**: 1,000 synthetic profiles (20,000+ skill-label pairs) generated via graph traversal.
- **Metrics**:
  - **NDCG@5**: 0.7913
  - **NDCG@10**: 0.8532
- **Feature Importance**:
  - `gnn_score`: 678 (Highest Impact)
  - `mastery`: 660
  - `jd_importance`: 277
  - `in_degree`: 129
  - `out_degree`: 56

## Repository Evidence
- **Scripts**: `backend/training/` contains the full pipeline.
- **Dataset**: `backend/training/synthetic_data.json` contains the raw training pairs.
- **Artifacts**: `backend/models/ranker.lgb` is the resulting booster.
