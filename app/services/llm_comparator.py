# app/services/llm_comparator.py

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os
import json
import re
from dotenv import load_dotenv

# ===============================
# Load Environment Variables
# ===============================
load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    raise ValueError("MISTRAL_API_KEY not found")

client = MistralClient(api_key=api_key)


# ===============================
# Helper: Extract JSON safely
# ===============================
def extract_json(text: str):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except json.JSONDecodeError:
        print("⚠️ JSON extraction failed")
    return None


# ===============================
# LLM Clause Comparison Function
# ===============================
def compare_clauses_llm(clause_a: str, clause_b: str):
    """
    Compare two policy clauses using Mistral LLM.
    """

    prompt = f"""
You are a senior compliance auditor.

Compare the following clauses.

Clause A (Source of Truth):
{clause_a}

Clause B (Target Policy):
{clause_b}

Rules:
- "Must/Shall" = mandatory requirement
- Missing specific details = Partial
- No relevant coverage = Non-Compliant

Return ONLY valid JSON:
{{
  "status": "Compliant | Partial | Non-Compliant",
  "reason": "short explanation",
  "gap": "what is missing",
  "missing_elements": [],
  "confidence": 0 to 1
}}
"""

    content = ""

    try:
        response = client.chat(
            model="mistral-small",
            messages=[ChatMessage(role="user", content=prompt)]
        )

        content = response.choices[0].message.content.strip()

        # ===============================
        # Try direct JSON parsing
        # ===============================
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            print("⚠️ Direct JSON parse failed, trying extraction...")
            result = extract_json(content)

        # ===============================
        # Validate result
        # ===============================
        if not isinstance(result, dict):
            raise ValueError("Invalid LLM response format")

        # ===============================
        # Ensure required keys
        # ===============================
        required_keys = ["status", "reason", "gap", "missing_elements", "confidence"]

        for key in required_keys:
            if key not in result:
                result[key] = "" if key != "confidence" else 0

        return result

    except Exception as e:
        print("❌ Mistral API Error:", e)
        print("⚠️ Raw response:", content)

        return {
            "status": "Error",
            "reason": "LLM failed",
            "gap": "",
            "missing_elements": [],
            "confidence": 0
        }


# ===============================
# Test Function
# ===============================
if __name__ == "__main__":
    a = "All data must be encrypted using AES-256"
    b = "Data is encrypted using industry standard methods"

    result = compare_clauses_llm(a, b)

    print("\n🔍 LLM Comparison Result:\n")
    print(json.dumps(result, indent=4))