#schema.py
from pydantic import BaseModel
from typing import List, Optional


# ===============================
# Upload Response
# ===============================
class UploadResponse(BaseModel):
    message: str
    file_path: str


# ===============================
# Parse Request & Response
# ===============================
class ParseRequest(BaseModel):
    file_name: str


class ParseResponse(BaseModel):
    message: str
    output_file: str
    pages_parsed: int


# ===============================
# Segment Request & Response
# ===============================
class SegmentRequest(BaseModel):
    file_name: str


class SegmentResponse(BaseModel):
    message: str
    clauses_created: int
    output_file: str


# ===============================
# Embed Request & Response
# ===============================
class EmbedRequest(BaseModel):
    file_name: str


class EmbedResponse(BaseModel):
    message: str
    total_clauses: int


# ===============================
# Compare Request & Response
# ===============================
class CompareRequest(BaseModel):
    file_a: str
    file_b: str


class ClauseResult(BaseModel):
    clause_a: str
    clause_b: str
    result: str


class CompareResponse(BaseModel):
    message: str
    score: float
    output_file: str
    results: List[ClauseResult]


# ===============================
# Clause Model (Segmentation)
# ===============================
class Clause(BaseModel):
    clause_id: str
    text: str
    policy_name: Optional[str] = None
    section: Optional[str] = None