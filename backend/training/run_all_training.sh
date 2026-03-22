# Change to backend directory so python training/*.py works
cd "$(dirname "$0")/.."

echo "=== SkillGraph V2 Training Pipeline ==="
# Use local venv python if it exists, otherwise fall back to python3
PYTHON_BIN=".venv/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

echo "[1/3] Training Node2Vec GNN embeddings..."
$PYTHON_BIN training/train_node2vec.py
echo "[2/3] Generating synthetic paths..."
$PYTHON_BIN training/generate_synthetic_paths.py
echo "[3/3] Training LightGBM ranker..."
$PYTHON_BIN training/train_ranker.py
echo "=== All training complete. Models saved to backend/models/ ==="
