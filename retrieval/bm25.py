from rank_bm25 import BM25Okapi

def build_bm25(texts):
    tokenized = [t.split() for t in texts]
    return BM25Okapi(tokenized)

def search_bm25(bm25, query):
    scores = bm25.get_scores(query.split())
    return sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)