# routers/statistics.py
# controller-like file in java-web
# routers/statistics.py

from fastapi import APIRouter, HTTPException

import app.services as svc
from typing import Callable
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/batch/statistics",
    tags=["statistics"],
)
satellite_router = APIRouter(
    prefix="/api/v1/satellite",
    tags=["satellite"],
)

mines_router = APIRouter(
    prefix="/api/v1",
    tags=["mines"],
)

test_router = APIRouter(
    prefix="/api/v1/test/statistics",
    tags=["default"],
)
root_router = APIRouter()


# calculation_func 이 함수 타입이라고 선언함
def execute_calculation(calculation_func: Callable):
    """
    공통로직을 포함한 템플릿 패턴이라고 볼수 있음
    calculation_func 콜백함수만 호출할 동적으로 바뀜
    """
    try:
        roi = svc.fetch_roi()
        calculation_func(roi)
        return {"status": "success"}
    except Exception as e:
        error_message = f"Error occurred while calculating: {e}"
        logger.error(error_message)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/roi_stats")
def calculate_distance():
    """거리/비율에 대한 배치 요청 처리
    Returns:
        _type_: 성공 여부 및 오류 메시지
    """
    logger.info("roi_stats")
    return "0"
    # return execute_calculation(svc.calculate_roi_stats)


@test_router.get("/graph")
def do_default_test():
    logger.info("graph called")
    return svc.fetch_test_graph()


@root_router.get("/graph")
def do_root_test():
    logger.info("/graph called")
    return svc.fetch_test_graph()


# 목록 조회
@satellite_router.get("/list")
def do_fetch_roi():
    logger.info("/satellite/ called")
    return svc.fetch_roi()


# 광산 조회
@mines_router.get("/mines/list")
def do_fetch_mines():
    logger.info("/mine/list called")
    return svc.fetch_mines()
