import json
import os
import random
import sys

# Ensure 'app' module can be imported
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from app.data_loader import load_skills, Domain
from app.graph import build_skill_graph, identify_gaps, build_gap_subgraph, compute_priority, build_learning_subgraph, generate_learning_path
from app.schemas import JDData
from app.gnn_scorer import gnn_score

def main():
    domains = ["swe", "data"]
    random.seed(42)
    
    profiles_per_domain = 250
    total_generated = 0
    total_pairs = 0
    
    X = []
    y = []
    groups = []
    
    for domain in domains:
        all_skills = load_skills(domain)
        graph = build_skill_graph(domain)
        
        generated_in_domain = 0
        while generated_in_domain < profiles_per_domain:
            # Randomly assign mastery scores uniform(0.0, 1.0) to 40-70% of domain skills
            num_mastery = int(len(all_skills) * random.uniform(0.4, 0.7))
            mastery_skills = random.sample(all_skills, num_mastery)
            mastery_scores = {skill: random.uniform(0.0, 1.0) for skill in mastery_skills}
            
            # Unassigned skills get mastery 0.0 (done via .get(skill, 0.0))
            
            # Randomly select 5-12 required skills from domain skill list
            num_required = random.randint(5, min(12, len(all_skills)))
            required = random.sample(all_skills, num_required)
            
            # Randomly select 3-6 preferred skills (different from required)
            remaining_skills = [s for s in all_skills if s not in required]
            num_preferred = random.randint(3, min(6, len(remaining_skills)))
            preferred = random.sample(remaining_skills, num_preferred)
            
            jd_data = JDData(required=required, preferred=preferred)
            
            gap_skills = identify_gaps(all_skills, mastery_scores, jd_data)
            gap_subgraph = build_gap_subgraph(graph, gap_skills)
            
            if gap_subgraph.number_of_nodes() < 3:
                continue
                
            priorities = {node: compute_priority(node, gap_subgraph, jd_data, mastery_scores, domain) for node in gap_subgraph.nodes}
            learning_subgraph = build_learning_subgraph(gap_subgraph, mastery_scores)
            path = generate_learning_path(learning_subgraph, priorities, mastery_scores)
            
            # Skip if path is empty but we require features... Actually if gap > 3, path should have some nodes
            
            # Build feature matrix
            group_size = 0
            for skill in gap_subgraph.nodes:
                jd_imp = 1.0 if skill in required else (0.6 if skill in preferred else 0.0)
                gnn = gnn_score(skill, domain)
                mastery = mastery_scores.get(skill, 0.0)
                in_deg = gap_subgraph.in_degree(skill)
                out_deg = gap_subgraph.out_degree(skill)
                
                features = [jd_imp, gnn, mastery, in_deg, out_deg]
                label = len(path) - path.index(skill) if skill in path else 0
                
                X.append(features)
                y.append(label)
                group_size += 1
            
            if group_size > 0:
                groups.append(group_size)
                total_pairs += group_size
                generated_in_domain += 1
                total_generated += 1

    feature_names = ["jd_importance", "gnn_score", "mastery", "in_degree", "out_degree"]
    
    output_path = os.path.join(base_dir, "training", "synthetic_data.json")
    with open(output_path, "w") as f:
        json.dump({
            "X": X,
            "y": y,
            "groups": groups,
            "feature_names": feature_names
        }, f)
        
    print(f"total profiles generated: {total_generated}")
    print(f"total skill-label pairs: {total_pairs}")
    print(f"feature matrix shape: ({len(X)}, {len(feature_names)})")

if __name__ == "__main__":
    main()
