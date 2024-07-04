import concurrent.futures
import threading
import time

import logging

import app.models as model
from app.google_earth_engine import calculate_batch_processing

logger = logging.getLogger(__name__)


def fetch_mines():
    return model.fetch_mines()


def fetch_test_graph():
    return model.fetch_test_graph()


def fetch_roi():
    """DB 접속하여
    스레드를 이용하여 거리를 계산한다.

    Returns:
        _type_: _description_
    """
    # model을 이용하여 값을 가져온다.
    roi_list = model.fetch_roi()

    return roi_list


# 전역 변수로 shared_data와 lock 생성
shared_data = [
    {"roi": 1, "row": {"distance:": 10, "water_ratio": 50}},
    {"roi": 2, "row": {"distance:": 11, "water_ratio": 50}},
    {"roi": 3, "row": {"distance:": 12, "water_ratio": 50}},
    {"roi": 4, "row": {"distance:": 13, "water_ratio": 50}},
    {"roi": 5, "row": {"distance:": 14, "water_ratio": 50}},
]
lock = threading.Lock()


def calculate_roi_stats(roi_list):
    """최소거리, 지표수 비율 계산 후, 저장

    Args:
        roi_list (_type_): 관심영역 목록
    """
    logger.debug(f"ROI List : {roi_list}")
    # 스레드 풀의 크기 설정 (최대 스레드 수)
    max_workers = 10  # 필요에 따라 조절
    # ThreadPoolExecutor를 사용하여 작업 처리
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        logger.debug("threadpool starting...")
        # roi_list 개수 만큼의 작업을 스레드 풀에 제출
        futures = [executor.submit(worker, roi["ROI_ID"]) for roi in roi_list]

        # 작업 완료 여부 확인 및 결과 처리
        for future in concurrent.futures.as_completed(futures):
            # as_completed() 함수는 이 Future 객체들이 완료되는 순서대로 이터레이터를 생성합니다.
            try:
                result = future.result()
                print(f"Task {result} completed successfully")
            except Exception as exc:
                print(f"Task generated an exception: {exc}")

    logger.info("all batch processing completed")
    logger.debug(f"result : {result}")
    logger.debug(f"shared_data : {shared_data}")

    stats = [
        (d["roi"], d["row"]["distance:"], d["row"]["water_ratio"]) for d in shared_data
    ]
    logger.info(f"stat :{stats}")
    model.insert_stats(stats)
    # model.insert_stats(stats) # 실행결과 로그 저장


def worker(roi_id):
    # 여기서 하나의 장소에 대한 실제 작업을 수행
    logger.info(f"Task {roi_id} started")
    time.sleep(2)  # 작업을 시뮬레이션하기 위해 5분 대신 2초로 설정
    # Google Earth Engine API를 사용하여 최소 거리를 계산하는 로직 구현
    # 공유 dictionary 에 DB에 저장할 값을 추가한다.

    distance = calculate_batch_processing(roi_id)
    logger.info(f"Task {roi_id} finished")
    # water_ratio = calculate_surface_ratio(roi_id)

    # shared_data에 결과 저장
    # with lock:
    #     shared_data.append(
    #         {
    #             "roi": roi_id,
    #             "row": {
    #                 "distance": distance,
    #                 "water_ratio": water_ratio,
    #             },
    #         }
    #     )

    # logger.debug(f"shared_data : {shared_data}")

    # print(f"Task {roi_id} finished")
    # return roi_id
