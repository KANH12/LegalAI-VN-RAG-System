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

# ===== RAG SYSTEM =====
def rag_system(query):
    try:
        intent = detect_intent(query)
        query_expanded = expand_query(query)

        top_indices = hybrid_search(query_expanded, df, bm25, faiss_index)

        expanded_contexts = []
        seen_articles = set()

        for idx in top_indices:
            idx = int(idx)
            current_row = df.iloc[idx]
            
            article = current_row.get('article')
            doc_name = current_row.get('document_name', '')

            if article and doc_name:
                article_key = f"{doc_name}_{article}"
                if article_key not in seen_articles:
                    article_rows = df[
                        (df['article'] == article) & 
                        (df['document_name'] == doc_name)
                    ].sort_index() 
                    
                    if len(article_rows) > 12:
                        article_rows = article_rows.head(12) 
                    
                    full_article_text = " ".join(article_rows["chunk_text"].astype(str).values)
                    
                    if len(full_article_text) > 3000:
                        full_article_text = full_article_text[:3000] + "..."
                        
                    expanded_contexts.append(full_article_text)
                    seen_articles.add(article_key)
            else:
                start_idx = max(0, idx - 1)
                end_idx = min(len(df), idx + 2) 
                window_text = " ".join(df.iloc[start_idx : end_idx]["chunk_text"].values)
                if window_text not in expanded_contexts:
                    expanded_contexts.append(window_text)

        expanded_contexts = expanded_contexts[:3] 
        
        try:
            refined_contexts = rerank(query, expanded_contexts)
        except Exception as e:
            print(f"--> Rerank vẫn lỗi do quá nặng, dùng top 1 search gốc: {e}")
            refined_contexts = expanded_contexts[:1] 

        final_context_str = "\n\n---\n\n".join(refined_contexts)

        print(f"\n[DEBUG] INTENT: {intent}")
        print(f"[DEBUG] SEARCH QUERY: {query_expanded[:100]}...")
        
        answer = generate_answer(query, final_context_str, intent)
        return answer

    except Exception as e:
        print("ERROR:", e)
        return "Hệ thống bị lỗi rồi!!!"

# ===== TEST =====
if __name__ == "__main__":
    while True:
        q = input("Nhập câu hỏi: ")
        print(rag_system(q))