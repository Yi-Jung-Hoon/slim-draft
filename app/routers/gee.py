from fastapi import APIRouter, File, UploadFile
from typing import List
import app.services as svc
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/gee",
    tags=["gee"],
)


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    logger.info("Uploading files")
    file_names = svc.save_uploaded_files(files)
    return {
        "message": f"Successfully uploaded {len(files)} files",
        "filenames": file_names,
    }
