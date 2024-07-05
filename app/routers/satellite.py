from fastapi import APIRouter
import app.services as svc
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/satellite",
    tags=["satellite"],
)


@router.get("/list")
async def do_fetch_roi():
    logger.info("/satellite/ called")
    return svc.fetch_roi()
