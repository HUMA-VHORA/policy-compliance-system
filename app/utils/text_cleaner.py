# app/utils/text_cleaner.py

import re


# ===============================
# Clean Text (Main Function)
# ===============================
def clean_text(text: str) -> str:
    if not text:
        return ""

    # Normalize line breaks
    text = re.sub(r'\n+', '\n', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove weird unicode characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    return text.strip()


# ===============================
# Remove Special Characters (SAFE)
# ===============================
def remove_special_characters(text: str) -> str:
    if not text:
        return ""

    # Keep important compliance characters
    return re.sub(r'[^A-Za-z0-9.,()\-:/% ]+', '', text)


# ===============================
# Normalize for NLP / Embedding
# ===============================
def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    # Remove punctuation (light cleaning)
    text = re.sub(r'[^\w\s]', ' ', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# ===============================
# Sentence Splitting (Improved)
# ===============================
def split_into_sentences(text: str):
    if not text:
        return []

    # Handles ., ?, ! and avoids breaking numbers like 1.1
    sentences = re.split(r'(?<!\d)[.!?]+\s+', text)

    return [s.strip() for s in sentences if s.strip()]