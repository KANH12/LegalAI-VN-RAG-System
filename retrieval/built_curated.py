import pandas as pd
import pickle
import faiss

from config.settings import *
from retrieval.embedding import load_model, embed_text
from retrieval.faiss_index import build_faiss
from retrieval.bm25 import build_bm25

# load data
df = pd.read_parquet(DATA_PATH)

texts = df["chunk_text"].astype(str).tolist()

# embedding
load_model(EMBED_MODEL)
embeddings = embed_text(texts)

# build FAISS
faiss_index = build_faiss(embeddings)
faiss.write_index(faiss_index, GOLD_PATH + "faiss.index")

# build BM25
bm25 = build_bm25(texts)
with open(GOLD_PATH + "bm25.pkl", "wb") as f:
    pickle.dump(bm25, f)

print("CURATED BUILT")