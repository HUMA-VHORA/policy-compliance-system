# app/core/config.py

import os
from dotenv import load_dotenv

# ===============================
# Load Environment Variables
# ===============================
load_dotenv()


class Settings:
    # ===============================
    # Pinecone Configuration
    # ===============================
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_ENV: str = os.getenv("PINECONE_ENV", "")
    PINECONE_INDEX: str = os.getenv("PINECONE_INDEX", "policy-index")

    # ===============================
    # Mistral Configuration (NEW 🔥)
    # ===============================
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")

    # ===============================
    # Data Paths
    # ===============================
    DATA_RAW: str = os.getenv("DATA_RAW", "data/raw")
    DATA_PARSED: str = os.getenv("DATA_PARSED", "data/parsed")
    DATA_SEGMENTED: str = os.getenv("DATA_SEGMENTED", "data/segmented")
    DATA_RESULTS: str = os.getenv("DATA_RESULTS", "data/results")

    # ===============================
    # Validation
    # ===============================
    def validate(self):
        warnings = []

        if not self.PINECONE_API_KEY:
            warnings.append("⚠️ PINECONE_API_KEY not set")

        if not self.MISTRAL_API_KEY:
            warnings.append("⚠️ MISTRAL_API_KEY not set")

        return warnings


# Singleton instance
settings = Settings()


# ===============================
# Create Data Directories
# ===============================
def create_directories():
    paths = [
        settings.DATA_RAW,
        settings.DATA_PARSED,
        settings.DATA_SEGMENTED,
        settings.DATA_RESULTS
    ]

    for path in paths:
        os.makedirs(path, exist_ok=True)


# ===============================
# Initialize System
# ===============================
def init_config():
    print("⚙️ Initializing Configuration...")

    create_directories()

    warnings = settings.validate()

    if warnings:
        for w in warnings:
            print(w)
    else:
        print("✅ All environment variables loaded")


# Run on import
init_config()