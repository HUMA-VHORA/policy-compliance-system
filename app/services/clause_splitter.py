import re
import json


# ===============================
# SPLIT CLAUSES
# ===============================
def split_clauses(input_json, output_json):
    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    full_text = data.get("text", "")

    if not full_text:
        return []

    # 🔥 Split by clause numbers (1. 2. 3.)
    pattern = r'(?=\n?\s*\d+\.\s+[A-Z])'
    raw_clauses = re.split(pattern, full_text)

    clauses = []

    for idx, clause in enumerate(raw_clauses, start=1):
        clause = clause.strip()

        if not clause:
            continue

        clause_number, title, body = parse_clause(clause)

        clauses.append({
            "clause_id": f"C-{clause_number or idx}",
            "clause_number": clause_number or str(idx),
            "sub_clause": None,
            "title": title,
            "text": body
        })

    # ===============================
    # SAVE OUTPUT
    # ===============================
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(clauses, f, indent=4, ensure_ascii=False)

    return clauses


# ===============================
# PARSE CLAUSE
# ===============================
def parse_clause(clause_text: str):
    match = re.match(r'^\s*(\d+)\.\s*(.+)', clause_text, re.DOTALL)

    if not match:
        return None, "Untitled", clause_text

    clause_number = match.group(1)
    remaining = match.group(2).strip()

    lines = remaining.split("\n")

    if len(lines) > 1:
        title = lines[0].strip()
        body = " ".join(lines[1:]).strip()
    else:
        parts = re.split(r'\.\s+', remaining, maxsplit=1)
        title = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else remaining

    return clause_number, title, body