from fastapi import APIRouter
import app.services as svc
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/test/statistics",
    tags=["default"],
)


@router.get("/graph")
async def do_default_test():
    logger.info("graph called")
    return svc.fetch_test_graph()
