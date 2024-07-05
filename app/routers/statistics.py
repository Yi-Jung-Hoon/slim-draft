from typing import Callable
from fastapi import APIRouter, HTTPException
import app.services as svc
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/batch/statistics",
    tags=["statistics"],
)


def execute_calculation(calculation_func: Callable):
    try:
        roi = svc.fetch_roi()
        calculation_func(roi)
        return {"status": "success"}
    except Exception as e:
        error_message = f"Error occurred while calculating: {e}"
        logger.error(error_message)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/roi_stats")
async def calculate_distance():
    logger.info("roi_stats")
    return "0"


@router.get("/graph")
async def do_default_test():
    logger.info("graph called")
    return svc.fetch_test_graph()
