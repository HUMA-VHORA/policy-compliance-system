import re
from app.services.llm_keyword_extractor import extract_keywords_llm


# ===============================
# Extract Compliance Keywords (Regex)
# ===============================
def extract_compliance_keywords(text: str):
    text = text.lower()

    # 🔥 EXPANDED KEYWORDS (VERY IMPORTANT)
    pattern = r'\b(' \
              r'must|shall|required|require|requires|mandatory|should|recommended|' \
              r'prohibit|prohibited|not allowed|ensure|ensures|enforced|enforce|' \
              r'access|control|security|risk|audit|monitor|review|encrypt|authentication|' \
              r'authorization|compliance|policy|procedure|incident|report|manage|protect' \
              r')\b'

    return set(re.findall(pattern, text))


# ===============================
# HYBRID Keyword Extraction
# ===============================
def extract_compliance_keywords_hybrid(text: str):
    regex_keywords = extract_compliance_keywords(text)

    llm_keywords = set()
    if len(text.split()) > 8:
        try:
            llm_keywords = extract_keywords_llm(text)
        except Exception as e:
            print("⚠️ LLM keyword fallback:", e)

    return regex_keywords.union(llm_keywords), regex_keywords, llm_keywords


# ===============================
# Normalize Text
# ===============================
def normalize_text(text: str):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return text


# ===============================
# Keyword Similarity (Jaccard)
# ===============================
def keyword_similarity(text_a: str, text_b: str):
    keywords_a, regex_a, llm_a = extract_compliance_keywords_hybrid(text_a)
    keywords_b, regex_b, llm_b = extract_compliance_keywords_hybrid(text_b)

    union = keywords_a.union(keywords_b)

    if not union:
        return 0, keywords_a, keywords_b, regex_a, regex_b, llm_a, llm_b

    match = len(keywords_a.intersection(keywords_b))
    similarity = match / len(union)

    # 🔥 SMART FALLBACK BOOST
    if match == 0:
        if keywords_a and keywords_b:
            similarity = 0.25   # increased
        elif llm_a or llm_b:
            similarity = 0.35   # stronger semantic hint

    return similarity, keywords_a, keywords_b, regex_a, regex_b, llm_a, llm_b


# ===============================
# Text Similarity (Improved)
# ===============================
def text_similarity(text_a: str, text_b: str):
    words_a = set(normalize_text(text_a).split())
    words_b = set(normalize_text(text_b).split())

    if not words_a or not words_b:
        return 0

    intersection = words_a.intersection(words_b)
    union = words_a.union(words_b)

    return len(intersection) / len(union)


# ===============================
# FINAL COMPARISON (HYBRID READY)
# ===============================
def compare_clauses_regex(clause_a: str, clause_b: str):
    (
        keyword_score,
        keywords_a,
        keywords_b,
        regex_a,
        regex_b,
        llm_a,
        llm_b
    ) = keyword_similarity(clause_a, clause_b)

    text_score = text_similarity(clause_a, clause_b)

    # 🔥 STRONGER LOCAL SCORE
    local_score = (
        0.7 * keyword_score +   # 🔥 more weight to intent
        0.3 * text_score
    )

    # 🔥 BOOST if both scores decent
    if keyword_score > 0.3 and text_score > 0.3:
        local_score += 0.1

    local_score = min(local_score, 1.0)  # cap at 1

    return {
        "keywords_a": list(keywords_a),
        "keywords_b": list(keywords_b),

        "regex_a": list(regex_a),
        "regex_b": list(regex_b),

        "llm_a": list(llm_a),
        "llm_b": list(llm_b),

        "keyword_overlap": list(keywords_a.intersection(keywords_b)),

        "keyword_score": round(keyword_score, 2),
        "text_score": round(text_score, 2),

        # 🔥 FINAL LOCAL SCORE
        "local_score": round(local_score, 2)
    }