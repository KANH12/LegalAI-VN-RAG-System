from sentence_transformers import SentenceTransformer

model = None

def load_model(name):
    global model
    model = SentenceTransformer(name)

def embed_text(texts):
    return model.encode(texts)