from typing import Callable, Optional
from fastapi import APIRouter, HTTPException, Request
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


## /api/v1/batch/statistics/roi_stats 요청 처리
@router.post("/roi_stats")
async def run_batch():
    logger.info("batch started")
    svc.run_batch()
    return "0"


@router.get("/graph")
async def do_default_test(
    request: Request, start_date: Optional[str] = None, end_date: Optional[str] = None
):
    logger.info(f"graph called: {start_date}, {end_date}")
    # 모든 요청 파라미터 정보 출력
    logger.info(f"Request query params: {request.query_params}")
    logger.info(f"Request headers: {request.headers}")

    if start_date is None or end_date is None:
        logger.debug("1")
        bind_vars = None
    else:
        logger.debug("2")
        bind_vars = {"start_date": start_date, "end_date": end_date}

    return svc.fetch_test_graph(bind_vars)
