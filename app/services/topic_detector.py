# app/services/topic_detector.py

def detect_topic(text: str):
    """
    Detect topic based on keyword scoring.
    Returns the most relevant topic or 'general'.
    """

    # ===============================
    # Normalize text
    # ===============================
    text = text.lower()

    # ===============================
    # Topic Keywords Dictionary
    # ===============================
    topics = {
        "security": [
            "encrypt", "encryption", "aes", "tls", "ssl",
            "data protection", "confidential", "cipher", "key"
        ],
        "risk": [
            "risk", "vendor", "third-party", "third party",
            "assessment", "mitigation", "compliance"
        ],
        "access": [
            "access", "authentication", "authorization",
            "mfa", "privilege", "login", "identity"
        ],
        "business": [
            "continuity", "recovery", "drp", "bcp",
            "disaster", "backup", "availability"
        ],
        "incident": [
            "incident", "breach", "attack", "alert",
            "response", "threat", "vulnerability"
        ]
    }

    # ===============================
    # Initialize scores (Sonar fix)
    # ===============================
    scores = dict.fromkeys(topics, 0)

    # ===============================
    # Calculate scores
    # ===============================
    for topic, keywords in topics.items():
        for keyword in keywords:
            if keyword in text:
                scores[topic] += 1

    # ===============================
    # Select best topic
    # ===============================
    best_topic = max(scores, key=scores.get)

    # ===============================
    # Return result
    # ===============================
    if scores[best_topic] == 0:
        return "general"

    return best_topic