import faiss
import numpy as np

def build_faiss(embeddings):
    embeddings = np.array(embeddings).astype("float32")
    faiss.normalize_L2(embeddings)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    return index

def search_faiss(index, query_vec, top_k):
    import faiss
    query_vec = query_vec.astype("float32")
    faiss.normalize_L2(query_vec)

    scores, indices = index.search(query_vec, top_k)
    return indices[0]