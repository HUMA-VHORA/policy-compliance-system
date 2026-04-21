# app/api/segment.py

from fastapi import APIRouter, HTTPException, Query
from typing import Annotated
import os

from app.services.clause_splitter import split_clauses
from app.core.config import settings

router = APIRouter(prefix="/segment", tags=["Segmentation"])


@router.post(
    "/",
    responses={
        404: {"description": "Parsed JSON file not found"},
        500: {"description": "Segmentation failed"}
    }
)
def segment_policy(
    file_name: Annotated[str, Query(...)]
):
    try:
        # ===============================
        # Clean filename
        # ===============================
        clean_name = file_name.replace(".pdf", "").strip()

        input_json = os.path.join(
            settings.DATA_PARSED,
            f"{clean_name}.json"
        )

        output_json = os.path.join(
            settings.DATA_SEGMENTED,
            f"{clean_name}_segmented.json"
        )

        # ===============================
        # Validate file
        # ===============================
        if not os.path.exists(input_json):
            raise HTTPException(
                status_code=404,
                detail=f"{input_json} not found"
            )

        # ===============================
        # USE YOUR ORIGINAL SPLITTER ✅
        # ===============================
        clauses = split_clauses(input_json, output_json)

        if not clauses:
            return {
                "message": "No clauses extracted ❌",
                "clauses_created": 0
            }

        return {
            "message": "Segmentation completed ✅",
            "output_file": output_json,
            "clauses_created": len(clauses)
        }

    except HTTPException:
        raise

    except Exception as e:
        print("❌ Segmentation Error:", e)
        raise HTTPException(
            status_code=500,
            detail="Segmentation failed"
        )