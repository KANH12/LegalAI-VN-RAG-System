import faiss
import numpy as np

def build_faiss(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index


def search_faiss(index, query_vec, top_k):
    scores, indices = index.search(query_vec, top_k)
    return indices[0]