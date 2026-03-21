import json
import os
import lightgbm as lgb
import numpy as np

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "training", "synthetic_data.json")
    
    with open(data_path, "r") as f:
        data = json.load(f)
        
    X = np.array(data["X"])
    y = np.array(data["y"])
    groups = np.array(data["groups"])
    feature_names = data["feature_names"]
    
    num_groups = len(groups)
    train_groups_count = int(num_groups * 0.8)
    
    train_groups = groups[:train_groups_count]
    eval_groups = groups[train_groups_count:]
    
    train_samples = sum(train_groups)
    
    X_train = X[:train_samples]
    y_train = y[:train_samples]
    
    X_eval = X[train_samples:]
    y_eval = y[train_samples:]
    
    train_data = lgb.Dataset(X_train, label=y_train, group=train_groups, feature_name=feature_names)
    eval_data = lgb.Dataset(X_eval, label=y_eval, group=eval_groups, feature_name=feature_names, reference=train_data)
    
    params = {
        "objective": "lambdarank",
        "metric": "ndcg",
        "ndcg_eval_at": [5, 10],
        "num_leaves": 31,
        "learning_rate": 0.05,
        "verbose": -1,
    }
    
    model = lgb.train(
        params,
        train_data,
        num_boost_round=100,
        valid_sets=[eval_data],
        callbacks=[lgb.early_stopping(20)]
    )
    
    best_score = model.best_score["valid_0"]
    ndcg_5 = best_score.get("ndcg@5", best_score.get("ndcg@5"))
    ndcg_10 = best_score.get("ndcg@10", best_score.get("ndcg@10"))
    
    print(f"NDCG@5: {ndcg_5:.4f}")
    print(f"NDCG@10: {ndcg_10:.4f}")
    
    importances = model.feature_importance()
    print("Feature importances:")
    for name, imp in zip(feature_names, importances):
        print(f"  {name}: {imp}")
        
    model_dir = os.path.join(base_dir, "models")
    os.makedirs(model_dir, exist_ok=True)
    model.save_model(os.path.join(model_dir, "ranker.lgb"))
    
    print(f"LightGBM training complete. NDCG@5: {ndcg_5:.4f}")

if __name__ == "__main__":
    main()
