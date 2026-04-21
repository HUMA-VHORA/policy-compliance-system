from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import os
import json
from dotenv import load_dotenv

# ===============================
# Load API Key
# ===============================
load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    raise ValueError("MISTRAL_API_KEY not found")

client = MistralClient(api_key=api_key)


# ===============================
# LLM Keyword Extraction
# ===============================
def extract_keywords_llm(text: str):
    prompt = f"""
Extract compliance-related keywords from the text.

Focus on:
- obligations (must, require, enforce)
- controls (encryption, MFA, logging)
- governance terms

Return ONLY a JSON list.

Text:
{text}
"""

    content = ""

    try:
        response = client.chat(
            model="mistral-small",
            messages=[ChatMessage(role="user", content=prompt)]
        )

        content = response.choices[0].message.content.strip()

        # ===============================
        # Safe JSON parsing
        # ===============================
        try:
            keywords = json.loads(content)
        except json.JSONDecodeError:
            return set()

        # Validate type
        if not isinstance(keywords, list):
            return set()

        return {str(k).lower() for k in keywords}

    except Exception as e:
        print("❌ Mistral Keyword Error:", e)
        return set()