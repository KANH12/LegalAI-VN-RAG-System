import pandas as pd
import pickle
import faiss
import os

from thefuzz import fuzz
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
def clean_text(text, max_len=1000): 
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
        is_insufficient = True 
        
       # ===== STEP 2: MATCH LAYER (PRIORITY #1) =====
        print(f"\n[PIPELINE] 1. Executing Match Layer for: '{extracted_violation}'...")
        matched_rows = matcher.search(extracted_violation, vehicle_type=extracted_vehicle)
        
        is_insufficient = True 
        query_expanded = query

        if matched_rows:
            
            # --- CALCULATE & SORT SCORE ---
            for r in matched_rows:
                if r.get('score', 0) == 0: 
                    actual_text = str(r.get('chunk_text', ''))
                    r['score'] = fuzz.token_set_ratio(extracted_violation, actual_text)
            
            #high score
            matched_rows = sorted(matched_rows, key=lambda x: x.get('score', 0), reverse=True)
            top_score = matched_rows[0].get('score', 0)
            
            print(f"   => [SUCCESS] Match Layer found {len(matched_rows)} records! (Top Score: {top_score}%)")
            
            #FILTER TOP SCORE
            if top_score < 60.0:
                print(f"   => [REJECTED] Match score too low. Forcing Hybrid Search...")
                is_insufficient = True
            else:
                penalty_contexts, concept_contexts = [], []
                
                for r in matched_rows:
                    if r.get('score', 0) < 65.0: continue
                    
                    dtype = r.get('doc_type')
                    content = clean_text(str(r.get('chunk_text', '')))
                    
                    if dtype == 'decree':
                        penalty_contexts.append(content)
                    else:
                        concept_contexts.append(content)
                
                if top_score >= 90.0:
                    if intent == 'penalty' and len(penalty_contexts) > 0:
                        is_insufficient = False
                    elif intent in ['definition', 'general'] and len(concept_contexts) > 0:
                        is_insufficient = False
                
                if is_insufficient:
                    print(f"   => [LOW CONFIDENCE] Score {top_score}% < 90% hoặc thiếu loại tài liệu cần thiết.")
                
                final_match_blocks = []
                if concept_contexts: final_match_blocks.append("### PRIMARY LEGAL CONCEPTS:\n" + "\n".join(concept_contexts))
                if penalty_contexts: final_match_blocks.append("### PRIMARY FINES & VIOLATIONS:\n" + "\n".join(penalty_contexts))
                
                if final_match_blocks:
                    expanded_contexts.append("\n\n".join(final_match_blocks))
                
                if not is_insufficient:
                    print(f"   => [OPTIMIZED] High confidence match. Skipping Hybrid Search.")
        else:
            print(f"   => [NOT FOUND] Match Layer returned no results.")

        # ===== STEP 3: HYBRID SEARCH (ONLY IF INSUFFICIENT) =====
        if is_insufficient:
            reason = "low confidence match" if matched_rows else "no match found"
            print(f"[PIPELINE] 2. Executing Hybrid Search (FAISS + BM25) due to {reason}...")
            
            # Tối ưu query cho ca Tai nạn/Chết người nếu cần
            if any(word in query for word in ["chết", "tử vong", "tai nạn"]):
                query_expanded = query + " mức phạt trách nhiệm hình sự gây hậu quả nghiêm trọng"
            else:
                query_expanded = expand_query(query)
                
            top_indices = hybrid_search(query_expanded, df, bm25, faiss_index)

            if top_indices:
                top_indices = top_indices[:3] 
                seen_articles = set()
                hybrid_contexts = []
                
                for idx in top_indices:
                    idx = int(idx)
                    try: current_row = df.iloc[idx]
                    except: continue

                    article, doc_name = current_row.get('article'), current_row.get('document_name', '')
                    article_key = f"{doc_name}_{article}"

                    if article and doc_name and article_key not in seen_articles:
                        article_rows = df[(df['article'] == article) & 
                                          (df['document_name'] == doc_name)].sort_index().head(5)
                        
                        full_text = " ".join(article_rows["chunk_text"].astype(str).values)
                        hybrid_contexts.append(clean_text(full_text))
                        seen_articles.add(article_key)
                
                if hybrid_contexts:
                    expanded_contexts.append("### SUPPLEMENTARY LEGAL DATA:\n" + "\n\n".join(hybrid_contexts))
                print(f"   => Context expanded from {len(seen_articles)} related articles.")

        # ===== STEP 4: RERANK & FINAL TRIMMING =====
        expanded_contexts = list(dict.fromkeys(expanded_contexts))

        if not expanded_contexts:
            return "Không tìm thấy thông tin phù hợp trong cơ sở dữ liệu pháp luật."

        try:
            refined_contexts = rerank(query, expanded_contexts)
            refined_contexts = refined_contexts[:2] 
        except Exception as e:
            print(f"[WARN] Rerank fail: {e}")
            refined_contexts = expanded_contexts[:2]

        # --- TOKEN SAFETY SHIELD (Use for Groq Limit 6000) ---
        context_for_llm = "\n\n".join(refined_contexts)
        if len(context_for_llm) > 15000:
            context_for_llm = context_for_llm[:15000] + "... [Dữ liệu được cắt gọn để tối ưu]"

        # ===== DEBUG =====
        print(f"[DEBUG] INTENT: {intent}")
        print(f"[DEBUG] VEHICLE: {extracted_vehicle}")

        # ===== STEP 5: GENERATE =====
        answer = generate_answer(query, [context_for_llm], intent)
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