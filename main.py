import pandas as pd
import pickle
import faiss

from config.settings import *
from retrieval.embedding import load_model
from retrieval.hybrid import hybrid_search
from rag.query_expansion import expand_query
from rag.reranker import rerank
from rag.generator import generate_answer
from rag.intent import detect_intent

# ===== LOAD =====
df = pd.read_parquet(DATA_PATH)

with open(GOLD_PATH + "bm25.pkl", "rb") as f:
    bm25 = pickle.load(f)

faiss_index = faiss.read_index(GOLD_PATH + "faiss.index")

load_model(EMBED_MODEL)


# ===== HELPER =====
def clean_text(text, max_len=1500):
    text = str(text).strip().replace("\n", " ")
    return text[:max_len]


# ===== RAG SYSTEM =====
def rag_system(query):
    try:
        # ===== STEP 1: INTENT =====
        intent = detect_intent(query)

        # ===== STEP 2: QUERY EXPANSION =====
        query_expanded = expand_query(query)

        # ===== STEP 3: RETRIEVAL =====
        top_indices = hybrid_search(query_expanded, df, bm25, faiss_index)

        if not top_indices:
            return "Không tìm thấy dữ liệu phù hợp."

        print("\n[DEBUG] TOP IDX:", top_indices[:5])

        # ===== STEP 4: CONTEXT EXPANSION =====
        expanded_contexts = []
        seen_articles = set()

        for idx in top_indices:
            idx = int(idx)

            try:
                current_row = df.iloc[idx]
            except:
                continue

            article = current_row.get('article')
            doc_name = current_row.get('document_name', '')

            # ===== ƯU TIÊN GROUP THEO ARTICLE =====
            if article and doc_name:
                article_key = f"{doc_name}_{article}"

                if article_key not in seen_articles:
                    article_rows = df[
                        (df['article'] == article) &
                        (df['document_name'] == doc_name)
                    ].sort_index()

                    article_rows = article_rows.head(10)

                    full_text = " ".join(
                        article_rows["chunk_text"].astype(str).values
                    )

                    expanded_contexts.append(clean_text(full_text))
                    seen_articles.add(article_key)

            # ===== FALLBACK WINDOW =====
            else:
                start_idx = max(0, idx - 1)
                end_idx = min(len(df), idx + 2)

                window_text = " ".join(
                    df.iloc[start_idx:end_idx]["chunk_text"].astype(str).values
                )

                expanded_contexts.append(clean_text(window_text))

        # limit
        expanded_contexts = expanded_contexts[:5]

        if not expanded_contexts:
            return "Không tìm thấy context phù hợp."

        # ===== STEP 5: RERANK =====
        try:
            refined_contexts = rerank(query_expanded, expanded_contexts)
        except Exception as e:
            print(f"[WARN] Rerank fail → fallback: {e}")
            refined_contexts = expanded_contexts[:2]

        # ===== DEBUG =====
        print(f"[DEBUG] INTENT: {intent}")
        print(f"[DEBUG] QUERY: {query}")
        print(f"[DEBUG] EXPANDED: {query_expanded[:300]}...")

        # ===== STEP 6: GENERATE =====
        answer = generate_answer(query, refined_contexts, intent)

        return answer

    except Exception as e:
        print("ERROR:", e)
        return "Hệ thống bị lỗi rồi!!!"


# ===== TEST =====
if __name__ == "__main__":
    while True:
        q = input("Nhập câu hỏi: ")

        if q.lower() in ["exit", "quit"]:
            print("Bye")
            break

        print("\n===== ANSWER =====")
        print(rag_system(q))
        print("=" * 50)