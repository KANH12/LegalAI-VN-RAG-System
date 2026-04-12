def rrf(rankings, k=60):
    scores = {}

    for rank_list in rankings:
        for rank, idx in enumerate(rank_list):
            clean_idx = int(idx) 
            
            scores[clean_idx] = scores.get(clean_idx, 0) + 1 / (k + rank + 1)

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)