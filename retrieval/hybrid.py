from retrieval.embedding import embed_text
from retrieval.faiss_index import search_faiss
from retrieval.bm25 import search_bm25
from retrieval.rrf import rrf
from config.settings import TOP_K, TOP_K_RETRIEVE


def hybrid_search(query, df, bm25, faiss_index):

    # ===== BM25 =====
    bm25_rank = search_bm25(bm25, query, TOP_K)

    # ===== FAISS =====
    query_vec = embed_text([query])
    faiss_rank = search_faiss(faiss_index, query_vec, TOP_K)

    # ===== RRF =====
    final_rank = rrf([bm25_rank, faiss_rank])

    # ===== BOOST VIOLATION  =====
    boosted = []
    for idx, score in final_rank:
        row = df.iloc[idx]
        v = row.get("violation_type")

        if v and v in query.lower():
            score += 0.5  

        boosted.append((idx, score))

    boosted = sorted(boosted, key=lambda x: x[1], reverse=True)

    # ===== FINAL =====
    top = boosted[:TOP_K_RETRIEVE]

    return [int(idx) for idx, _ in top]