from rank_bm25 import BM25Okapi
import re

def tokenize(text):
    # lower + remove punctuation
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)

    # giữ phrase quan trọng
    tokens = text.split()

    return tokens


def build_bm25(texts):
    tokenized = [tokenize(t) for t in texts]
    return BM25Okapi(tokenized)


def search_bm25(bm25, query, top_k=50):
    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)

    top_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:top_k]

    return top_indices