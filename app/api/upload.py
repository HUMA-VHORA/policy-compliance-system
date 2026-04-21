# app/api/upload.py

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Annotated
import os
import aiofiles

from app.core.config import settings

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post(
    "/",
    responses={
        400: {"description": "Invalid file type"},
        500: {"description": "Upload failed"}
    }
)
async def upload_file(
    file: Annotated[UploadFile, File(...)]
):
    try:
        # ===============================
        # Validate file type
        # ===============================
        if not file.filename.endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )

        # ===============================
        # Ensure upload directory exists
        # ===============================
        os.makedirs(settings.DATA_RAW, exist_ok=True)

        # ===============================
        # Safe filename (security fix)
        # ===============================
        file_name = os.path.basename(file.filename)

        file_path = os.path.join(settings.DATA_RAW, file_name)

        # ===============================
        # Save file (async)
        # ===============================
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(1024):
                await f.write(chunk)

        return {
            "message": "File uploaded successfully ✅",
            "file_name": file_name,
            "file_path": file_path
        }

    except HTTPException:
        raise

    except Exception as e:
        print("❌ Upload Error:", e)
        raise HTTPException(
            status_code=500,
            detail="File upload failed"
        )