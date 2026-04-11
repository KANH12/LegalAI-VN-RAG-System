from retrieval.embedding import embed_text
from retrieval.faiss_index import search_faiss
from retrieval.bm25 import search_bm25
from retrieval.rrf import rrf
from config.settings import TOP_K, TOP_K_RETRIEVE

def hybrid_search(query, df, bm25, faiss_index):
    query_vec = embed_text([query])

    bm25_rank = search_bm25(bm25, query)
    faiss_rank = search_faiss(faiss_index, query_vec, TOP_K_RETRIEVE)

    final_rank = rrf([bm25_rank, faiss_rank])

    top = final_rank[:TOP_K]

    print("\n🔎 TOP RESULTS:")
    for idx, score in top:
        print(df.iloc[idx]["chunk_text"][:200])
        print("-----")

    return [df.iloc[idx]["chunk_text"] for idx, _ in top]