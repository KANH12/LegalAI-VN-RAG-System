from sentence_transformers import SentenceTransformer
import numpy as np

model = None

def load_model(name):
    global model
    model = SentenceTransformer(name)

def embed_text(texts):
    emb = model.encode(texts, normalize_embeddings=True)
    return np.array(emb).astype("float32")