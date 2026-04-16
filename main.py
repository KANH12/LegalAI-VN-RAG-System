import pandas as pd
import pickle
import faiss
import os

from config.settings import *
from retrieval.embedding import load_model
from retrieval.hybrid import hybrid_search
from retrieval.matcher import ViolationMatcher  
from rag.query_expansion import expand_query
from rag.reranker import rerank
from rag.generator import generate_answer
from rag.intent import detect_intent

# ===== LOAD DATA & MODELS =====
df = pd.read_parquet(DATA_PATH)

with open(GOLD_PATH + "bm25.pkl", "rb") as f:
    bm25 = pickle.load(f)

faiss_index = faiss.read_index(GOLD_PATH + "faiss.index")

matcher = ViolationMatcher() 

load_model(EMBED_MODEL)

# ===== HELPER =====
def clean_text(text, max_len=1500):
    text = str(text).strip().replace("\n", " ")
    return text[:max_len]

# ===== RAG SYSTEM =====
def rag_system(query):
    try:
        # ===== STEP 1: INTENT & ENTITY EXTRACTION =====
        intent_data = detect_intent(query)
        intent = intent_data.get("intent", "general")
        extracted_violation = intent_data.get("violation")
        extracted_vehicle = intent_data.get("vehicle", "chung")

        expanded_contexts = []
        
        # ===== STEP 2: MATCH LAYER (PRIORITY #1) =====
        print(f"\n[PIPELINE] 1. Executing Match Layer for: '{extracted_violation}'...")
        matched_rows = matcher.search(extracted_violation, vehicle_type=extracted_vehicle)
        
        if matched_rows:
            print(f"   => [SUCCESS] Match Layer found {len(matched_rows)} exact records!")
            # Group matched rows into context
            matched_text = " ".join([str(r['chunk_text']) for r in matched_rows])
            expanded_contexts.append(clean_text(matched_text))
        else:
            print(f"   => [NOT FOUND] Match Layer returned no results for this violation type.")

        # ===== STEP 3: HYBRID SEARCH (FALLBACK / AUGMENTATION) =====
        # Fallback if Match Layer failed or returned insufficient context
        if not expanded_contexts or len(expanded_contexts) < 1:
            print(f"[PIPELINE] 2. Executing Hybrid Search (FAISS + BM25) fallback...")
            
            query_expanded = expand_query(query)
            top_indices = hybrid_search(query_expanded, df, bm25, faiss_index)

            if top_indices:
                print(f"   => [HIT] Hybrid Search retrieved {len(top_indices)} relevant chunks.")
                seen_articles = set()
                for idx in top_indices:
                    idx = int(idx)
                    try:
                        current_row = df.iloc[idx]
                    except: continue

                    article = current_row.get('article')
                    doc_name = current_row.get('document_name', '')
                    article_key = f"{doc_name}_{article}"

                    if article and doc_name and article_key not in seen_articles:
                        article_rows = df[(df['article'] == article) & 
                                          (df['document_name'] == doc_name)].sort_index().head(10)
                        
                        full_text = " ".join(article_rows["chunk_text"].astype(str).values)
                        expanded_contexts.append(clean_text(full_text))
                        seen_articles.add(article_key)
                print(f"   => Context expanded from {len(seen_articles)} related legal articles.")
            else:
                print(f"   => [FAILED] Hybrid Search could not find any relevant data.")
        else:
            print(f"[PIPELINE] 2. Match Layer results found -> Skipping Hybrid Search for optimization.")
            query_expanded = query

        # ===== STEP 4: RERANK & FILTER =====
        expanded_contexts = list(dict.fromkeys(expanded_contexts))[:5] # Dedup & Limit

        if not expanded_contexts:
            return "Không tìm thấy thông tin phù hợp trong cơ sở dữ liệu pháp luật."

        try:
            refined_contexts = rerank(query, expanded_contexts)
        except Exception as e:
            print(f"[WARN] Rerank fail: {e}")
            refined_contexts = expanded_contexts[:2]

        # ===== DEBUG =====
        print(f"[DEBUG] INTENT: {intent}")
        print(f"[DEBUG] VEHICLE: {extracted_vehicle}")

        # ===== STEP 5: GENERATE =====
        answer = generate_answer(query, refined_contexts, intent)
        return answer

    except Exception as e:
        import traceback
        print("ERROR:", traceback.format_exc())
        return "Xin lỗi, hệ thống đang gặp sự cố khi xử lý điều khoản này."

# ===== TEST LOOP =====
if __name__ == "__main__":
    while True:
        q = input("\nNhập câu hỏi luật giao thông: ")
        if q.lower() in ["exit", "quit"]: break

        print("\n" + "="*20 + " BỘ LỌC PHÁP LUẬT " + "="*20)
        print(rag_system(q))
        print("="*58)