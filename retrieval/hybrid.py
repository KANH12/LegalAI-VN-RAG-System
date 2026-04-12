from retrieval.embedding import embed_text
from retrieval.faiss_index import search_faiss
from retrieval.bm25 import search_bm25
from retrieval.rrf import rrf
from config.settings import TOP_K, TOP_K_RETRIEVE

def hybrid_search(query, df, bm25, faiss_index):

    bm25_rank = search_bm25(bm25, query) 

    query_vec = embed_text([query])

    faiss_rank = search_faiss(faiss_index, query_vec, TOP_K)

    final_rank = rrf([bm25_rank, faiss_rank])

    top = final_rank[:TOP_K_RETRIEVE]

    results = []
    for idx, score in top:
        results.append(int(idx))
        
    return results