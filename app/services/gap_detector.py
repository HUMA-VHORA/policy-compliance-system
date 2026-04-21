# app/services/gap_detector.py

def detect_gap(similarity_score, llm_result):
    """
    Final decision using:
    - Hybrid similarity score (semantic + regex)
    - LLM only for override in weak cases
    """

    status = llm_result.get("status", "")
    confidence = llm_result.get("confidence", 0)

    # ===============================
    # 1. VERY LOW → MISSING
    # ===============================
    if similarity_score < 0.30:
        return "Missing"

    # ===============================
    # 2. HIGH → COMPLIANT
    # ===============================
    if similarity_score >= 0.75:
        return "Compliant"

    # ===============================
    # 3. MEDIUM → PARTIAL
    # ===============================
    if similarity_score >= 0.50:
        return "Partial"

    # ===============================
    # 4. LOW → LLM DECISION
    # ===============================
    if status == "Non-Compliant" and confidence > 0.6:
        return "Gap"

    return "Partial"