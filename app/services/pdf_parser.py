import pdfplumber
import json
import re
import os
import logging

logger = logging.getLogger(__name__)


# ===============================
# CLEAN TEXT (KEEP NEWLINES ✅)
# ===============================
def clean_text(text: str):
    """
    Clean extracted PDF text while preserving structure.
    """
    # Remove non-ASCII
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    # Normalize spaces but KEEP newlines
    text = re.sub(r'[ \t]+', ' ', text)

    return text.strip()


# ===============================
# MAIN PDF PARSER (RAW TEXT ONLY ✅)
# ===============================
def parse_pdf(file_path: str, output_json: str):
    """
    Extract full text from PDF and save as JSON.

    NOTE:
    - NO clause splitting here ❌
    - Segmentation handled separately ✅
    """

    try:
        full_text = ""

        # ===============================
        # READ PDF
        # ===============================
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()

                if text:
                    full_text += "\n" + text

        # ===============================
        # VALIDATE TEXT
        # ===============================
        if not full_text.strip():
            logger.warning("No text extracted from PDF")
            return {}

        # ===============================
        # CLEAN TEXT
        # ===============================
        full_text = clean_text(full_text)

        file_name = os.path.basename(file_path)

        # ===============================
        # STRUCTURED OUTPUT
        # ===============================
        parsed_data = {
            "file_name": file_name,
            "text": full_text
        }

        # ===============================
        # SAVE JSON
        # ===============================
        os.makedirs(os.path.dirname(output_json), exist_ok=True)

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(parsed_data, f, indent=4, ensure_ascii=False)

        logger.info(f"✅ Parsed file saved: {output_json}")

        return parsed_data

    except Exception as e:
        logger.error(f"❌ PDF Parsing Error: {e}", exc_info=True)
        return {}