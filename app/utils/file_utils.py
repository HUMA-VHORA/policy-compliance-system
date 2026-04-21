# app/utils/file_utils.py

import os
import json


# ===============================
# Create Directory
# ===============================
def create_directory(path: str):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print(f"❌ Error creating directory {path}: {e}")


# ===============================
# Save JSON File
# ===============================
def save_json(data, file_path: str):
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"❌ Error saving JSON {file_path}: {e}")


# ===============================
# Load JSON File
# ===============================
def load_json(file_path: str):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} not found")

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print(f"❌ Error loading JSON {file_path}: {e}")
        return None


# ===============================
# Save Text File
# ===============================
def save_text(text: str, file_path: str):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

    except Exception as e:
        print(f"❌ Error saving text file {file_path}: {e}")


# ===============================
# Load Text File
# ===============================
def load_text(file_path: str):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} not found")

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    except Exception as e:
        print(f"❌ Error loading text file {file_path}: {e}")
        return None