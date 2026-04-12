from rank_bm25 import BM25Okapi

def build_bm25(texts):
    tokenized = [t.split() for t in texts]
    return BM25Okapi(tokenized)

def search_bm25(bm25, query, top_k=50): # Giới hạn lại
    scores = bm25.get_scores(query.split())
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return top_indices