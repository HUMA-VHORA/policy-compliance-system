# app/api/embed.py
from fastapi import APIRouter, HTTPException, Query
import json
import os
from typing import Annotated

from app.services.embedding_engine import generate_embedding
from app.services.pinecone_db import store_embedding
from app.services.topic_detector import detect_topic
from app.core.config import settings

router = APIRouter(prefix="/embed", tags=["Embeddings"])


@router.post(
    "/",
    responses={
        404: {"description": "Segmented file not found"},
        500: {"description": "Embedding process failed"}
    }
)
def embed_policy(
    file_name: Annotated[str, Query(..., description="Policy file name (e.g., BANK_POLICY.pdf)")]
):
    try:
        # ===============================
        # Clean file name
        # ===============================
        file_name = file_name.replace(".pdf", "").strip()

        input_json = os.path.join(
            settings.DATA_SEGMENTED,
            f"{file_name}_segmented.json"
        )

        # ===============================
        # Validate file existence
        # ===============================
        if not os.path.exists(input_json):
            raise HTTPException(
                status_code=404,
                detail=f"{input_json} not found"
            )

        # ===============================
        # 🔥 Determine namespace + policy
        # ===============================
        if "BANK" in file_name.upper():
            namespace = "bank"
            policy_name = "BANK_POLICY"
        else:
            namespace = "vendor"
            policy_name = "VENDOR_POLICY"

        print(f"📦 Storing in namespace: {namespace}")

        # ===============================
        # Load clauses
        # ===============================
        with open(input_json, "r", encoding="utf-8") as f:
            clauses = json.load(f)

        if not clauses:
            return {
                "message": "No clauses found to embed",
                "total_clauses": 0
            }

        success_count = 0
        failed_count = 0

        # ===============================
        # Process each clause
        # ===============================
        for clause in clauses:
            try:
                text = clause.get("text", "").strip()
                clause_id = clause.get("clause_id")

                if not text or not clause_id:
                    failed_count += 1
                    continue

                # 🔹 Generate embedding
                embedding = generate_embedding(text)

                if not embedding:
                    failed_count += 1
                    continue

                # 🔹 Detect topic
                topic = detect_topic(text)

                # 🔹 Store in Pinecone (FINAL FIX ✅)
                store_embedding(
                    id=f"{file_name}_{clause_id}",   # 🔥 UNIQUE ID
                    embedding=embedding,
                    metadata={
                        "text": text,
                        "policy": policy_name,   # 🔥 CRITICAL for filtering
                        "topic": topic
                    },
                    namespace=namespace         # 🔥 CRITICAL separation
                )

                success_count += 1

            except Exception as e:
                print(f"❌ Error processing clause {clause.get('clause_id')}: {e}")
                failed_count += 1

        return {
            "message": "Embeddings stored in Pinecone ✅",
            "file": file_name,
            "namespace": namespace,
            "total_clauses": len(clauses),
            "successful": success_count,
            "failed": failed_count
        }

    except HTTPException:
        raise

    except Exception as e:
        print("❌ Embedding Error:", e)
        raise HTTPException(
            status_code=500,
            detail="Embedding process failed"
        )