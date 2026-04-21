from fastapi import APIRouter, HTTPException, Query
from typing import Annotated, List, Dict, Any
import json
import os
import pandas as pd

from app.services.semantic_search import find_similar_clauses
from app.services.regex_comparator import compare_clauses_regex
from app.services.llm_comparator import compare_clauses_llm
from app.services.gap_detector import detect_gap
from app.services.risk_scorer import assign_risk
from app.core.config import settings

router = APIRouter(prefix="/compare", tags=["Bank vs Vendor Comparison"])


# ===============================
# LOAD JSON
# ===============================
def load_json(file_path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"{file_path} not found"
        )

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ===============================
# LLM FALLBACK
# ===============================
def llm_fallback(regex_result: dict, text_a: str, text_b: str) -> dict:
    # ✅ FIXED: use local_score
    if regex_result["local_score"] > 0.8:
        return {
            "status": "Compliant",
            "reason": "High similarity (regex + semantic)",
            "gap": "",
            "missing_elements": [],
            "confidence": 0.9
        }

    return compare_clauses_llm(text_a, text_b)


# ===============================
# BUILD RESULT ROW
# ===============================
def build_result(clause, best_match, regex_result, llm_result, status, risk, combined_score):
    return {
        "clause_id": clause.get("clause_id"),
        "title": clause.get("title"),
        "clause_text": clause.get("text"),
        "matched_clause": best_match.get("text"),

        "semantic_score": round(best_match.get("score", 0), 2),

        # ✅ FIXED
        "regex_score": regex_result["local_score"],

        "combined_score": round(combined_score, 2),

        "keyword_score": regex_result["keyword_score"],
        "keywords_a": regex_result["keywords_a"],
        "keywords_b": regex_result["keywords_b"],
        "keyword_overlap": regex_result["keyword_overlap"],

        "status": status,
        "risk": risk,
        "reason": llm_result.get("reason", ""),
        "gap": llm_result.get("gap", ""),
        "missing_elements": llm_result.get("missing_elements", []),
        "confidence": llm_result.get("confidence", 0)
    }


# ===============================
# ALIGNMENT MATRIX
# ===============================
def build_alignment_matrix(results: list):
    return [
        {
            "bank_clause_id": r["clause_id"],
            "bank_clause_text": r["clause_text"][:200],
            "vendor_clause_text": (r["matched_clause"] or "")[:200],
            "semantic_score": r["semantic_score"],
            "regex_score": r["regex_score"],
            "combined_score": r["combined_score"],
            "status": r["status"],
            "risk": r["risk"]
        }
        for r in results
    ]


# ===============================
# EXCEL EXPORT
# ===============================
def export_to_excel(results: list, summary: dict, output_path: str):
    rows = []

    for r in results:
        rows.append({
            "Clause ID": r["clause_id"],
            "Title": r["title"],
            "Bank Clause": r["clause_text"],
            "Vendor Match": r["matched_clause"],
            "Semantic Score": r["semantic_score"],
            "Regex Score": r["regex_score"],
            "Combined Score": r["combined_score"],
            "Status": r["status"],
            "Risk": r["risk"],
            "Reason": r["reason"],
            "Gap": r["gap"],
            "Confidence": r["confidence"]
        })

    df = pd.DataFrame(rows)
    summary_df = pd.DataFrame([summary])

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Clause Comparison", index=False)
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

    return output_path


# ===============================
# MAIN API
# ===============================
@router.post(
    "/",
    summary="Compare Bank vs Vendor Policy",
    description="Compares bank policy clauses using semantic + regex + LLM",
    responses={
        200: {"description": "Comparison completed successfully"},
        404: {"description": "Policy file not found"},
        500: {"description": "Internal processing error"}
    }
)
def compare_bank_to_vendor(
    bank_file: Annotated[str, Query(..., description="Bank policy file")],
    vendor_file: Annotated[str, Query(..., description="Vendor policy file")]
):
    try:
        bank_file = bank_file.replace(".pdf", "")
        vendor_file = vendor_file.replace(".pdf", "")

        bank_path = os.path.join(
            settings.DATA_SEGMENTED,
            f"{bank_file}_segmented.json"
        )

        bank_clauses = load_json(bank_path)

        results = []

        # ===============================
        # LOOP
        # ===============================
        for clause in bank_clauses:
            text_a = clause["text"]

            similar = find_similar_clauses(text_a, top_k=3)

            if not similar:
                results.append({
                    "clause_id": clause.get("clause_id"),
                    "title": clause.get("title"),
                    "clause_text": text_a,
                    "matched_clause": None,
                    "semantic_score": 0,
                    "regex_score": 0,
                    "combined_score": 0,
                    "status": "Missing",
                    "risk": "High",
                    "reason": "No matching vendor clause found",
                    "gap": "Clause not implemented",
                    "missing_elements": [],
                    "confidence": 0
                })
                continue

            best_match = max(similar, key=lambda x: x["score"])
            text_b = best_match["text"]

            regex_result = compare_clauses_regex(text_a, text_b)
            llm_result = llm_fallback(regex_result, text_a, text_b)

            # 🔥 FINAL HYBRID SCORE (KEY FIX)
            combined_score = (
                0.7 * best_match.get("score", 0) +   # semantic
                0.3 * regex_result["local_score"]    # regex
            )

            status = detect_gap(combined_score, llm_result)
            risk = assign_risk(llm_result)

            results.append(
                build_result(
                    clause,
                    best_match,
                    regex_result,
                    llm_result,
                    status,
                    risk,
                    combined_score
                )
            )

        # ===============================
        # SUMMARY
        # ===============================
        total = len(results)
        compliant = sum(1 for r in results if r["status"] == "Compliant")
        partial = sum(1 for r in results if r["status"] == "Partial")
        missing = sum(1 for r in results if r["status"] in ["Missing", "Gap"])

        summary = {
            "overall_compliance": int((compliant + 0.5 * partial) / total * 100) if total else 0,
            "total_clauses": total,
            "compliant": compliant,
            "partial": partial,
            "missing": missing,
            "critical_gaps": missing
        }

        os.makedirs(settings.DATA_RESULTS, exist_ok=True)

        json_file = os.path.join(settings.DATA_RESULTS, "bank_vs_vendor_comparison.json")
        excel_file = os.path.join(settings.DATA_RESULTS, "bank_vs_vendor_report.xlsx")

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump({"summary": summary, "results": results}, f, indent=4)

        export_to_excel(results, summary, excel_file)

        return {
            "message": "Bank → Vendor comparison completed ✅",
            "output_file": json_file,
            "excel_report": excel_file,
            "summary": summary,
            "alignment_matrix": build_alignment_matrix(results)
        }

    except HTTPException:
        raise

    except Exception as e:
        print("❌ Error:", e)
        raise HTTPException(status_code=500, detail="Comparison failed")