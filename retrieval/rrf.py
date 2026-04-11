def rrf(rankings, k=60):
    scores ={}

    for rank_list in rankings:
        for rank, idx in enumerate(rank_list):
            scores[idx] = scores.get(idx, 0) + 1 / (k + rank)

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)