from pinecone import Pinecone
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

# ===============================
# Load Environment Variables
# ===============================
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

if not PINECONE_API_KEY or not PINECONE_INDEX:
    raise ValueError("Pinecone API key or index name is missing in .env")

# ===============================
# Initialize Pinecone
# ===============================
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)


# ===============================
# STORE SINGLE EMBEDDING
# ===============================
def store_embedding(
    id: str,
    embedding: List[float],
    metadata: Dict[str, Any],
    namespace: str
):
    try:
        if not embedding:
            return

        index.upsert(
            vectors=[{
                "id": id,
                "values": embedding,
                "metadata": metadata
            }],
            namespace=namespace  # 🔥 MUST be "bank" or "vendor"
        )

    except Exception as e:
        print(f"❌ Error storing embedding for {id}: {e}")


# ===============================
# STORE BATCH EMBEDDINGS
# ===============================
def store_embeddings_batch(
    items: List[Dict[str, Any]],
    namespace: str
):
    try:
        vectors = []

        for item in items:
            if not item.get("embedding"):
                continue

            vectors.append({
                "id": item["id"],
                "values": item["embedding"],
                "metadata": item.get("metadata", {})
            })

        if not vectors:
            return

        index.upsert(vectors=vectors, namespace=namespace)

    except Exception as e:
        print(f"❌ Batch insert error: {e}")


# ===============================
# SEARCH EMBEDDING (STRICT VENDOR ONLY 🔥)
# ===============================
def search_embedding(
    vector: List[float],
    top_k: int = 5,
    topic: str = None,
    namespace: str = "vendor"   # 🔥 Always search vendor
):
    try:
        if not vector:
            return []

        # ===============================
        # 🔥 STRICT FILTER (CRITICAL FIX)
        # ===============================
        filter_query = {
            "policy": {"$eq": "VENDOR_POLICY"}
        }

        # Optional topic refinement
        if topic:
            filter_query["topic"] = {"$eq": topic}

        # ===============================
        # QUERY PINECONE
        # ===============================
        results = index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            namespace=namespace,
            filter=filter_query
        )

        # ===============================
        # DEBUG (VERY IMPORTANT)
        # ===============================
        print("\n--- MATCH DEBUG ---")
        for m in results.get("matches", []):
            print("POLICY:", m.get("metadata", {}).get("policy"))
            print("TEXT:", m.get("metadata", {}).get("text", "")[:80])
            print("-------------------")

        # ===============================
        # FORMAT RESULTS
        # ===============================
        matches = []

        for match in results.get("matches", []):
            matches.append({
                "id": match.get("id"),
                "score": match.get("score"),
                "text": match.get("metadata", {}).get("text"),
                "metadata": match.get("metadata", {})
            })

        return matches

    except Exception as e:
        print(f"❌ Error searching embeddings: {e}")
        return []