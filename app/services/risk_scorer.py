# app/services/risk_scorer.py

def assign_risk(llm_result, similarity_score=None):
    """
    Assign risk level based on:
    - LLM status
    - confidence
    - similarity score
    """

    status = llm_result.get("status", "")
    confidence = llm_result.get("confidence", 0)

    # ===============================
    # 1. High Risk (Critical Issues)
    # ===============================
    if status == "Non-Compliant":
        return "High"

    if status == "Partial" and confidence < 0.5:
        return "High"

    # ===============================
    # 2. Medium Risk (Moderate Gaps)
    # ===============================
    if status == "Partial":
        return "Medium"

    if similarity_score is not None and similarity_score < 0.4:
        return "Medium"

    # ===============================
    # 3. Low Risk (Compliant)
    # ===============================
    if status == "Compliant":
        return "Low"

    # ===============================
    # 4. Fallback
    # ===============================
    return "Unknown"