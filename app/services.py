import concurrent.futures
import threading
import time

import os
import shutil
from typing import List
from fastapi import UploadFile
from . import constants

import logging

import app.models as model
from app.google_earth_engine import calculate_statistics

logger = logging.getLogger(__name__)


def fetch_mines():
    return model.fetch_mines()


def fetch_test_graph(bind_vars=None):
    return model.fetch_test_graph(bind_vars)


def fetch_roi():
    """DB 접속하여
    스레드를 이용하여 거리를 계산한다.

    Returns:
        _type_: _description_
    """
    # model을 이용하여 값을 가져온다.
    roi_list = model.fetch_roi()

    return roi_list


def run_batch():
    target_list = model.get_batch_target()
    calculate_roi_stats(target_list)

    return True


# 전역 변수로 shared_data와 lock 생성
shared_data = []
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
        # executor.submit(worker, roi["ROI_ID"])는 worker 함수를 ROI ID를 인수로 하여 비동기적으로 실행
        # futures = [executor.submit(worker, roi["ROI_ID"]) for roi in roi_list]
        futures = [executor.submit(worker, roi) for roi in roi_list]

        # 작업 완료 여부 확인 및 결과 처리
        for future in concurrent.futures.as_completed(futures):
            # as_completed() 함수는 이 Future 객체들이 완료되는 순서대로 이터레이터를 생성합니다.
            try:
                future.result()
            except Exception as exc:
                logger.error(f"Task generated an exception: {exc}")

    logger.info("all batch processing completed")
    logger.debug(f"shared_data : {shared_data}")

    """
    리스트 컴프리헨션:
    리스트 컴프리헨션은 간결하고 효율적으로 리스트를 생성하는 파이썬의 문법입니다.
    형식: [expression for item in iterable]
    여기서 expression은 각 요소가 변환되는 방식이고, item은 반복되는 각 요소를 나타냅니다.
    """
    """shared_data를 반복하여 tuple 구성함
    stats = [
        (1, 10, 50),
        (2, 11, 50),
        (3, 12, 50),
        (4, 13, 50),
        (5, 14, 50)
    ]
    """
    stats = [
        (d["roi"], d["row"]["distance"], d["row"]["water_ratio"]) for d in shared_data
    ]
    logger.info(f"stat :{stats}")
    model.insert_stats(stats)


def worker(roi):
    # 여기서 하나의 장소에 대한 실제 작업을 수행
    logger.info(f"ROI_ID({roi["ROI_ID"]}) started")
    time.sleep(2)  # 작업을 시뮬레이션하기 위해 5분 대신 2초로 설정
    # Google Earth Engine API를 사용하여 최소 거리를 계산하는 로직 구현
    # 공유 dictionary 에 DB에 저장할 값을 추가한다.

    min_distance, water_ratio = calculate_statistics(roi)

    # shared_data에 결과 저장
    with lock:
        shared_data.append(
            {
                "roi": roi["ROI_ID"],
                "row": {
                    "distance": min_distance,
                    "water_ratio": water_ratio,
                },
            }
        )

    logger.debug(f"shared_data : {shared_data}")    
    logger.info(f"ROI_ID({roi["ROI_ID"]}) finished")
    return roi["ROI_ID"]


def save_uploaded_files(files: List[UploadFile]) -> List[str]:
    """_summary_

    Args:
        files (List[UploadFile]): _description_

    Returns:
        List[str]: _description_
    """
    print(f"files : ${files}")
    file_names = []
    for file in files:
        file_name = file.filename
        file_names.append(file_name)

        # 파일 저장(binary write)
        with open(os.path.join(constants.UPLOAD_DIRECTORY, file_name), "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    return file_names
