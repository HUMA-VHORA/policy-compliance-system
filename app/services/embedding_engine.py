# app/services/embedding_engine.py

from sentence_transformers import SentenceTransformer
import numpy as np

# ===============================
# Load Model (Singleton)
# ===============================
model = SentenceTransformer("all-MiniLM-L6-v2")


# ===============================
# Generate Single Embedding
# ===============================
def generate_embedding(text: str):
    try:
        if not text or not text.strip():
            return []

        embedding = model.encode(
            text,
            normalize_embeddings=True  # 🔥 better similarity
        )

        return embedding.tolist()

    except Exception as e:
        print("❌ Embedding Error:", e)
        return []


# ===============================
# Generate Batch Embeddings (FAST 🔥)
# ===============================
def generate_embeddings_batch(texts: list[str]):
    try:
        if not texts:
            return []

        embeddings = model.encode(
            texts,
            batch_size=32,
            normalize_embeddings=True
        )

        return [emb.tolist() for emb in embeddings]

    except Exception as e:
        print("❌ Batch Embedding Error:", e)
        return []