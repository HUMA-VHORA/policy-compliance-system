# app/services/compliance_scorer.py

def calculate_score(results):
    total = len(results)

    if total == 0:
        return {
            "total": 0,
            "compliant": 0,
            "partial": 0,
            "missing": 0,
            "score": 0
        }

    # ===============================
    # Count statuses (UPDATED)
    # ===============================
    compliant = sum(1 for r in results if r["status"] == "Compliant")
    partial = sum(1 for r in results if r["status"] == "Partial")
    missing = sum(1 for r in results if r["status"] in ["Missing", "Gap"])

    # ===============================
    # Score Calculation
    # ===============================
    score = ((compliant + 0.5 * partial) / total) * 100

    return {
        "total_clauses": total,
        "compliant": compliant,
        "partial": partial,
        "missing": missing,
        "critical_gaps": missing,
        "overall_compliance": round(score)
    }