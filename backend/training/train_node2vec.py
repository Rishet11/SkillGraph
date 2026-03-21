import json
import os
import networkx as nx
from node2vec import Node2Vec

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, '..', 'data')
    models_dir = os.path.join(base_dir, 'models')
    
    os.makedirs(models_dir, exist_ok=True)
    
    domains = ['swe', 'data']
    
    for domain in domains:
        edges_path = os.path.join(data_dir, f'edges_{domain}.json')
        skills_path = os.path.join(data_dir, f'skills_{domain}.json')
        
        with open(edges_path, 'r') as f:
            edges = json.load(f)
        
        with open(skills_path, 'r') as f:
            skills = json.load(f)
            
        G = nx.DiGraph()
        G.add_edges_from(edges)
        G.add_nodes_from(skills)
        
        node2vec = Node2Vec(G, dimensions=64, walk_length=10, num_walks=20, workers=1, quiet=True)
        model = node2vec.fit(window=5, min_count=1, batch_words=4)
        
        scores = {}
        for skill in G.nodes():
            if skill in model.wv:
                vec = model.wv[skill]
                # L2 norm
                norm = float((sum(x**2 for x in vec))**0.5)
                scores[skill] = norm
            else:
                scores[skill] = 0.0
                
        if scores:
            min_norm = min(scores.values())
            max_norm = max(scores.values())
            
            normalized = {}
            for skill, norm in scores.items():
                if max_norm > min_norm:
                    normalized[skill] = (norm - min_norm) / (max_norm - min_norm)
                else:
                    normalized[skill] = 0.5
        else:
            normalized = {}
            
        out_path = os.path.join(models_dir, f'embeddings_{domain}.json')
        with open(out_path, 'w') as f:
            json.dump(normalized, f, indent=2)
            
        # Print top 5 skills
        top_5 = sorted(normalized.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"Top 5 skills for {domain}:")
        for skill, score in top_5:
            print(f"  {skill}: {score:.4f}")
            
    print("Node2Vec training complete. Saved to backend/models/")

if __name__ == '__main__':
    main()
