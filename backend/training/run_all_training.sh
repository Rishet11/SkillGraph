#!/bin/bash
set -e
echo "=== SkillGraph V2 Training Pipeline ==="
echo "[1/3] Training Node2Vec GNN embeddings..."
python training/train_node2vec.py
echo "[2/3] Generating synthetic paths..."
python training/generate_synthetic_paths.py
echo "[3/3] Training LightGBM ranker..."
python training/train_ranker.py
echo "=== All training complete. Models saved to backend/models/ ==="
