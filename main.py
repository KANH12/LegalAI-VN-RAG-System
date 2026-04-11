import pandas as pd
import pickle
import faiss

from config.settings import *
from retrieval.embedding import load_model
from retrieval.hybrid import hybrid_search
from rag.query_expansion import expand_query
from rag.reranker import simple_rerank
from rag.generator import generate_answer

# ===== LOAD =====
df = pd.read_parquet(DATA_PATH)

with open(GOLD_PATH + "bm25.pkl", "rb") as f:
    bm25 = pickle.load(f)

faiss_index = faiss.read_index(GOLD_PATH + "faiss.index")

load_model(EMBED_MODEL)


# ===== RAG SYSTEM =====
def rag_system(query):
    query = expand_query(query)

    contexts = hybrid_search(query, df, bm25, faiss_index)

    contexts = simple_rerank(contexts)

    answer = generate_answer(query, contexts)

    return answer


# ===== TEST =====
if __name__ == "__main__":
    while True:
        q = input("👉 Nhập câu hỏi: ")
        print(rag_system(q))