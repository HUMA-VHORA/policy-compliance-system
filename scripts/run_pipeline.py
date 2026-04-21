# scripts/run_pipeline.py

from app.services.pdf_parser import parse_pdf
from app.services.clause_splitter import split_clauses
from app.services.embedding_engine import generate_embeddings_batch
from app.services.pinecone_db import store_embeddings_batch
from app.services.semantic_search import find_similar_clauses
from app.services.regex_comparator import compare_clauses_regex

from app.services.llm_comparator import compare_clauses_llm
from app.services.gap_detector import detect_gap
from app.services.risk_scorer import assign_risk
from app.services.compliance_scorer import calculate_score

import json
import os


# ===============================
# Step 1: Parse PDFs
# ===============================
parse_pdf("data/raw/companyA.pdf", "data/parsed/A.json")
parse_pdf("data/raw/companyB.pdf", "data/parsed/B.json")

print("✅ PDF Parsing Completed")


# ===============================
# Step 2: Split Clauses
# ===============================
split_clauses("data/parsed/A.json", "data/segmented/A_seg.json")
split_clauses("data/parsed/B.json", "data/segmented/B_seg.json")

print("✅ Clause Segmentation Completed")


# ===============================
# Step 3: Batch Embedding (FAST 🔥)
# ===============================
with open("data/segmented/B_seg.json") as f:
    clauses_b = json.load(f)

texts = [c["text"] for c in clauses_b]
embeddings = generate_embeddings_batch(texts)

items = []
for clause, emb in zip(clauses_b, embeddings):
    items.append({
        "id": f"B_{clause['clause_id']}",  # 🔥 unique ID
        "embedding": emb,
        "metadata": {
            "text": clause["text"],
            "policy": "companyB"
        }
    })

store_embeddings_batch(items)

print("✅ Embeddings Stored in Pinecone")


# ===============================
# Step 4: Compare Policies
# ===============================
with open("data/segmented/A_seg.json") as f:
    clauses_a = json.load(f)

results = []

for clause in clauses_a:
    text_a = clause["text"]

    similar = find_similar_clauses(
        text_a,
        policy_name="companyA",
        top_k=3
    )

    # ❌ No match → Missing
    if not similar:
        results.append({
            "clause_a": text_a,
            "clause_b": None,
            "status": "Missing",
            "risk": "High",
            "reason": "No similar clause found",
            "gap": "Clause not implemented",
            "confidence": 0,
            "score": 0
        })
        continue

    # ✅ Best match
    best_match = similar[0]
    text_b = best_match["text"]

    # ===============================
    # Step 4.1: Regex
    # ===============================
    regex_result = compare_clauses_regex(text_a, text_b)

    # ===============================
    # Step 4.2: LLM (Optimized 🔥)
    # ===============================
    if regex_result["final_score"] > 0.8:
        llm_result = {
            "status": "Compliant",
            "reason": "High similarity",
            "gap": "",
            "missing_elements": [],
            "confidence": 0.9
        }
    else:
        llm_result = compare_clauses_llm(text_a, text_b)

    # ===============================
    # Step 4.3: Gap Detection
    # ===============================
    final_status = detect_gap(regex_result["final_score"], llm_result)

    # ===============================
    # Step 4.4: Risk Scoring
    # ===============================
    risk = assign_risk(llm_result, similarity_score=regex_result["final_score"])

    # ===============================
    # Save Result
    # ===============================
    results.append({
        "clause_a": text_a,
        "clause_b": text_b,

        "status": final_status,
        "risk": risk,

        "reason": llm_result.get("reason", ""),
        "gap": llm_result.get("gap", ""),
        "missing_elements": llm_result.get("missing_elements", []),
        "confidence": llm_result.get("confidence", 0),

        "score": regex_result["final_score"]
    })


print("✅ Clause Comparison Completed")


# ===============================
# Step 5: Compliance Score
# ===============================
summary = calculate_score(results)

os.makedirs("data/results", exist_ok=True)

with open("data/results/final_results.json", "w") as f:
    json.dump({
        "summary": summary,
        "results": results
    }, f, indent=4)

print("✅ Policy Comparison Completed")
print("📊 Compliance Score:", summary)