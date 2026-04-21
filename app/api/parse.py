#parse.py
from fastapi import APIRouter, HTTPException, Query
from typing import Annotated
import os
import logging

from app.services.pdf_parser import parse_pdf
from app.core.config import settings

router = APIRouter(prefix="/parse", tags=["Parsing"])

logger = logging.getLogger(__name__)


@router.post(
    "/",
    responses={
        200: {"description": "Parsing completed successfully"},
        400: {"description": "Bad request - file_name is missing or invalid"},
        404: {"description": "Input PDF file not found"},
        500: {"description": "Internal server error during parsing"}
    }
)
def parse_policy(
    file_name: Annotated[str, Query(..., description="Policy file name (e.g., companyA.pdf)")]
):
    try:
        # ===============================
        # Validate input
        # ===============================
        if not file_name:
            raise HTTPException(
                status_code=400,
                detail="file_name is required"
            )

        # ===============================
        # Clean filename safely
        # ===============================
        file_name = os.path.splitext(file_name.strip())[0] + ".pdf"

        input_path = os.path.join(settings.DATA_RAW, file_name)

        output_file_name = file_name.replace(".pdf", ".json")
        output_path = os.path.join(settings.DATA_PARSED, output_file_name)

        # ===============================
        # Check if file exists
        # ===============================
        if not os.path.exists(input_path):
            raise HTTPException(
                status_code=404,
                detail=f"{file_name} not found"
            )

        # ===============================
        # Parse PDF
        # ===============================
        data = parse_pdf(input_path, output_path)

        # ===============================
        # Handle empty output
        # ===============================
        if not data:
            return {
                "message": "No content extracted from PDF",
                "input_file": file_name,
                "output_file": output_file_name,
                "clauses_parsed": 0
            }

        # ===============================
        # Success response
        # ===============================
        return {
            "message": "Parsing completed successfully ✅",
            "input_file": file_name,
            "output_file": output_file_name,
            "clauses_parsed": len(data)
        }

    except HTTPException:
        # Re-raise FastAPI HTTP errors
        raise

    except Exception as e:
        logger.error(f"Parsing Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during parsing"
        )