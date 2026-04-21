# main.py

from fastapi import FastAPI
from app.api import upload, parse, segment, embed, compare
from app.core.config import settings
import os

app = FastAPI(
    title="Policy Compliance System",
    description="AI-powered Policy Comparison using Regex + LLM (Mistral)",
    version="2.1"
)

# ===============================
# Include API Routers
# ===============================
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(parse.router, prefix="/parse", tags=["Parse"])
app.include_router(segment.router, prefix="/segment", tags=["Segment"])
app.include_router(embed.router, prefix="/embed", tags=["Embed"])
app.include_router(compare.router, prefix="/compare", tags=["Compare"])


# ===============================
# Startup Event
# ===============================
@app.on_event("startup")
def startup_event():
    print("\n🚀 Policy Compliance System Started\n")

    print("📁 Raw Data Path:", settings.DATA_RAW)
    print("📁 Parsed Data Path:", settings.DATA_PARSED)
    print("📁 Segmented Data Path:", settings.DATA_SEGMENTED)
    print("📁 Results Path:", settings.DATA_RESULTS)

    # ===============================
    # Environment Checks
    # ===============================
    print("\n🔍 Environment Check:")

    if not os.getenv("MISTRAL_API_KEY"):
        print("⚠️ MISTRAL_API_KEY not set")
    else:
        print("✅ Mistral API Key Loaded")

    if not os.getenv("PINECONE_API_KEY"):
        print("⚠️ PINECONE_API_KEY not set")
    else:
        print("✅ Pinecone API Key Loaded")

    print("\n✅ System Ready\n")


# ===============================
# Shutdown Event (NEW 🔥)
# ===============================
@app.on_event("shutdown")
def shutdown_event():
    print("\n🛑 Policy Compliance System Stopped\n")


# ===============================
# Health Check Route
# ===============================
@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "OK",
        "service": "Policy Compliance System",
        "version": "2.1"
    }


# ===============================
# Root Endpoint
# ===============================
@app.get("/", tags=["Home"])
def home():
    return {
        "message": "Policy Compliance System Running 🚀",
        "version": "2.1",
        "features": [
            "Regex Comparison",
            "LLM Clause Comparison (Mistral)",
            "Hybrid Keyword Extraction",
            "Semantic Search (Pinecone)",
            "Gap Detection",
            "Risk Scoring"
        ]
    }