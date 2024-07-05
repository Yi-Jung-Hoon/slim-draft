from fastapi import APIRouter
import app.services as svc
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["mines"],
)


@router.get("/mines/list")
async def do_fetch_mines():
    logger.info("/mine/list called")
    return svc.fetch_mines()
