import json
import os
import numpy as np
from scipy.optimize import minimize

# Default weights as starting point
DEFAULT_WEIGHTS = {"frequency": 0.35, "recency": 0.35, "jd_match": 0.30}

def mastery_formula(weights, features):
    """
    weights: [w_freq, w_rec, w_jd]
    features: list of [freq, rec, jd]
    """
    return np.dot(features, weights)

def objective(weights, features, targets):
    # Constraint: weights must sum to 1.0 (handled by 'constraints' in minimize)
    preds = mastery_formula(weights, features)
    return np.mean((preds - targets)**2)

def main():
    # 1. Create a mock "Expert Labelled" dataset
    # Features: [frequency (0-1), recency (0.5 or 1.0), jd_match (0.0, 0.6, 1.0)]
    # Target: The mastery score an expert would give
    features = np.array([
        [0.1, 1.0, 1.0],  # Case 1: Low freq, but recent and required
        [0.8, 0.5, 0.0],  # Case 2: High freq, but old and not in JD
        [0.4, 1.0, 0.6],  # Case 3: Balanced
        [0.05, 0.5, 1.0], # Case 4: Minimal evidence, but required by JD
    ])
    
    # Let's say experts care MORE about JD match than we thought
    targets = np.array([0.75, 0.40, 0.65, 0.50])
    
    # 2. Optimize
    initial_guess = [0.33, 0.33, 0.34]
    bounds = [(0, 1), (0, 1), (0, 1)]
    # Constraint: sum(weights) == 1
    cons = ({'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0})
    
    res = minimize(objective, initial_guess, args=(features, targets),
                   bounds=bounds, constraints=cons)
    
    optimized_weights = {
        "frequency": round(float(res.x[0]), 3),
        "recency": round(float(res.x[1]), 3),
        "jd_match": round(float(res.x[2]), 3)
    }
    
    print("Optimization Complete.")
    print(f"Old Weights: {DEFAULT_WEIGHTS}")
    print(f"New Weights: {optimized_weights}")
    print(f"MSE Improvement: {objective(initial_guess, features, targets):.4f} -> {res.fun:.4f}")
    
    # 3. Save to backend/models/mastery_weights.json
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_path = os.path.join(base_dir, 'models', 'mastery_weights.json')
    
    with open(out_path, 'w') as f:
        json.dump(optimized_weights, f, indent=2)
    
    print(f"Saved optimized weights to {out_path}")

if __name__ == "__main__":
    main()
