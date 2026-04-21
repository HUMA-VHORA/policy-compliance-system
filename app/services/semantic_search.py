# app/services/semantic_search.py

from app.services.embedding_engine import generate_embedding
from app.services.pinecone_db import search_embedding
from app.services.topic_detector import detect_topic


def find_similar_clauses(text: str, top_k: int = 3):
    """
    Find similar clauses ONLY from vendor namespace.

    Steps:
    1. Generate embedding
    2. Detect topic
    3. Search in vendor namespace (strict)
    4. Fallback (remove topic)
    5. Filter weak matches
    """

    try:
        # ===============================
        # Step 1: Generate embedding
        # ===============================
        vector = generate_embedding(text)

        if not vector:
            return []

        # ===============================
        # Step 2: Detect topic
        # ===============================
        topic = detect_topic(text)

        # ===============================
        # Step 3: Strict search (vendor only)
        # ===============================
        matches = search_embedding(
            vector=vector,
            top_k=top_k,
            topic=topic
        )

        # ===============================
        # Step 4: Fallback (remove topic)
        # ===============================
        if not matches:
            matches = search_embedding(
                vector=vector,
                top_k=top_k
            )

        if not matches:
            return []

        # ===============================
        # Step 5: Filter weak matches
        # ===============================
        filtered = [
            m for m in matches
            if m.get("score", 0) > 0.4 and len(m.get("text", "")) > 50
        ]

        if not filtered:
            filtered = matches

        # ===============================
        # Step 6: Sort results
        # ===============================
        filtered.sort(key=lambda x: x["score"], reverse=True)

        # ===============================
        # Step 7: Format output
        # ===============================
        formatted_matches = []

        for match in filtered[:top_k]:
            metadata = match.get("metadata", {})

            formatted_matches.append({
                "score": round(match.get("score", 0), 3),
                "text": match.get("text"),
                "title": metadata.get("title"),
                "policy": metadata.get("policy"),
                "topic": metadata.get("topic")
            })

        # ===============================
        # DEBUG (remove later)
        # ===============================
        print("\n--- MATCH DEBUG ---")
        for m in formatted_matches:
            print("POLICY:", m["policy"])
            print("TEXT:", m["text"][:80])
            print("-------------------")

        return formatted_matches

    except Exception as e:
        print("❌ Semantic Search Error:", e)
        return []