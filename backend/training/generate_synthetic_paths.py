import json
import os
import random
import sys
from tqdm import tqdm

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
    
    # Light training scale for instant deployment
    profiles_per_domain = 500 
    total_generated = 0
    total_pairs = 0
    
    X = []
    y = []
    groups = []
    
    print(f"Starting V2 Data Generation: Aiming for {profiles_per_domain * 2} profiles...")

    for domain in domains:
        all_skills = load_skills(domain)
        full_graph = build_skill_graph(domain)
        
        generated_in_domain = 0
        pbar = tqdm(total=profiles_per_domain, desc=f"Generating {domain.upper()} profiles")
        
        while generated_in_domain < profiles_per_domain:
            # 1. Randomly assign mastery (Skill Context)
            num_mastery = int(len(all_skills) * random.uniform(0.3, 0.8)) # Variable coverage
            mastery_skills = random.sample(all_skills, num_mastery)
            mastery_scores = {skill: random.uniform(0.0, 1.0) for skill in mastery_skills}
            
            # 2. Randomly select JD Requirements
            num_required = random.randint(4, min(15, len(all_skills)))
            required = random.sample(all_skills, num_required)
            
            remaining_skills = [s for s in all_skills if s not in required]
            num_preferred = random.randint(2, min(8, len(remaining_skills)))
            preferred = random.sample(remaining_skills, num_preferred)
            
            jd_data = JDData(required=required, preferred=preferred)
            
            # 3. Process Graph Logic (Fast)
            gap_skills = identify_gaps(all_skills, mastery_scores, jd_data)
            if not gap_skills:
                continue
                
            gap_subgraph = build_gap_subgraph(full_graph, gap_skills)
            if gap_subgraph.number_of_nodes() < 2:
                continue
                
            # Compute priorities once for the subgraph
            priorities = {node: compute_priority(node, gap_subgraph, jd_data, mastery_scores, domain) for node in gap_subgraph.nodes}
            learning_subgraph = build_learning_subgraph(gap_subgraph, mastery_scores)
            
            # Generate the Golden Path (Teacher Path)
            path = generate_learning_path(learning_subgraph, priorities, mastery_scores)
            
            # 4. Extract Features & Labels
            group_size = 0
            for skill in gap_subgraph.nodes:
                jd_imp = 1.0 if skill in required else (0.6 if skill in preferred else 0.0)
                gnn = gnn_score(skill, domain)
                mastery = mastery_scores.get(skill, 0.0)
                in_deg = gap_subgraph.in_degree(skill)
                out_deg = gap_subgraph.out_degree(skill)
                
                # Label is "relevance" for LambdaRank: Inverse of path index (Higher = More Urgent)
                try:
                    rank_label = len(path) - path.index(skill) if skill in path else 0
                except ValueError:
                    rank_label = 0 # Not in path (already mastered or redundant)
                
                X.append([jd_imp, gnn, mastery, in_deg, out_deg])
                y.append(rank_label)
                group_size += 1
            
            if group_size > 0:
                groups.append(group_size)
                total_pairs += group_size
                generated_in_domain += 1
                total_generated += 1
                pbar.update(1)
        
        pbar.close()

    feature_names = ["jd_importance", "gnn_score", "mastery", "in_degree", "out_degree"]
    
    # Save Scaled Dataset
    output_path = os.path.join(base_dir, "training", "synthetic_data.json")
    print(f"Saving scaled dataset ({len(X)} pairs) to {output_path}...")
    
    with open(output_path, "w") as f:
        json.dump({
            "X": X,
            "y": y,
            "groups": groups,
            "feature_names": feature_names
        }, f)
        
    print(f"\nV2 DATA GENERATION COMPLETE:")
    print(f"- Total Profiles: {total_generated}")
    print(f"- Total Skill-Label Pairs: {total_pairs}")
    print(f"- Feature Matrix Size: {len(X)} x {len(feature_names)}")

if __name__ == "__main__":
    main()
