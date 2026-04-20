import streamlit as st
import pandas as pd
import time
from main import rag_system 

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="VietTraffic AI",
    page_icon="⚖️",
    layout="wide" 
)

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .main { background-color: #f8f9fa; }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }

    .stStatusWidget, .stExpander {
        border-radius: 12px !important;
        border: 1px solid #eef0f2 !important;
        background-color: white !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    .stChatMessage {
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #f0f2f6;
    }
    
    .main-title {
        font-weight: 800;
        color: #0f172a;
        text-align: center;
        font-size: 2.6rem;
        margin-bottom: 0.1rem;
    }

    .sub-title {
        text-align: center;
        color: #64748b;
        font-size: 1.05rem;
        margin-bottom: 2.5rem;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2850/2850730.png", width=70)
    st.title("VietTraffic AI")
    st.markdown("---")
    st.markdown("### 🛠️ Pipeline Architecture")
    st.success("**Tier 1:** Violation Matcher")
    st.info("**Tier 2:** Hybrid RAG (FAISS+BM25)")
    st.warning("**Tier 3:** Cross-Encoder Reranker")
    st.markdown("---")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- MAIN UI ---
_, col_main, _ = st.columns([0.1, 8, 0.1])

with col_main:
    st.markdown('<h1 class="main-title">Trợ lý Luật Giao thông 2024</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Hệ thống tra cứu thông minh dựa trên văn bản pháp luật giao thông tại Thư viện Pháp luật</p>', unsafe_allow_html=True)

    query = st.chat_input("Hỏi về vi phạm, mức phạt (VD: không đội mũ bảo hiểm)...")

    if query:
        # User Message
        with st.chat_message("user", avatar="👤"):
            st.markdown(f"**{query}**")

        # Assistant Message
        with st.chat_message("assistant", avatar="⚖️"):
            with st.status("🔍 Đang truy vấn hệ thống dữ liệu...", expanded=True) as status:
                st.write("1️⃣ Đang phân tích câu hỏi...")
                
                start_time = time.time()
                result = rag_system(query) 
                end_time = time.time()
                
                # Metadata from main.py
                meta = result.get("metadata", {})
                
                st.write(f"2️⃣ Chiến lược: {meta.get('search_strategy', 'N/A')}")
                st.write("3️⃣ Reranking & Generating Answer...")
                
                duration = round(end_time - start_time, 2)
                status.update(label=f"✅ Hoàn tất trong {duration}s", state="complete", expanded=False)
            
            # Show answer
            st.markdown(result.get("answer", "Không có phản hồi."))
            
            # Metadata Expander
            st.write("")
            with st.expander("📝 Chi tiết Pipeline & Metadata"):
                tab1, tab2 = st.tabs(["🔍 Retrieval Info", "⚙️ Tech Stack"])
                with tab1:
                    st.json({
                        "query_intent": meta.get("intent"),
                        "detected_vehicle": meta.get("vehicle"),
                        "violation_tag": meta.get("violation_detected"),
                        "search_strategy": meta.get("search_strategy"),
                        "is_hybrid_triggered": meta.get("is_hybrid"),
                        "processing_time": f"{duration}s"
                    })
                with tab2:
                    st.write("- **Embedding:** Sentence-Transformers (Keep-it-simple)")
                    st.write("- **Vector DB:** FAISS (FlatL2 Index)")
                    st.write("- **Text Search:** BM25 Okapi")
                    st.write("- **Reranker:** Cross-Encoder Strategy")

# --- FOOTER ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.caption("<p style='text-align: center;'>Dữ liệu được trích xuất từ văn bản pháp luật chính thống. Vui lòng đối chiếu khi cần thiết.</p>", unsafe_allow_html=True)