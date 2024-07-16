# google_earth_engine.py
import logging
import ee
import datetime

# 임시
import random

logger = logging.getLogger(__name__)

from google.oauth2.service_account import Credentials
from google.auth.exceptions import GoogleAuthError  # 올바른 범위 설정


def initialize_gee():
    """Initialization of Google Earth Engine including Authentification"""
    SCOPES = ["https://www.googleapis.com/auth/earthengine"]

    try:
        # credentials = Credentials.from_service_account_file(
        #     "my-first_project.json",  ## [서비스 사용량 소비자, Earth Engine 리소스 뷰어] 역할
        #     # "ee-hoony77lee-9c802931e08f.json", ## [서비스 사용량 소비자, Earth Engine 리소스 뷰어] 역할
        #     scopes=SCOPES,
        # )

        # print(f"creendtials : {credentials.service_account_email}")
        # ee.Initialize(credentials=credentials)

        # ee.Authenticate()
        # ee.Initialize(project="lively-pursuit-426306-i4")
        # ee.Initialize(project="aerobic-tesla-417706")

        credentials = Credentials.from_service_account_file(
            "aerobic-tesla-417706-7ef0ce8ab6f5.json", scopes=SCOPES
        )
        ee.Initialize(credentials=credentials)
        logger.info("Initialization successful.")

    except GoogleAuthError as e:
        logger.error(f"Authentication failed: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


def mask_water_v1(image: ee.image) -> ee.image:
    """
    Calculate NDWI (Normalized Difference Water Index) and mask water regions from a Sentinel-2 image.

    Args:
        image (ee.Image): A Sentinel-2 image.

    Returns:
        ee.Image: A binary image where water regions are masked (1) and non-water regions are not (0).
    """
    # B3 (Green): 560 nm (중심 파장)
    # B8 (NIR): 842 nm (중심 파장)
    ndwi = image.normalizedDifference(["B3", "B8"]).rename("NDWI")
    # ndwi = image.normalizedDifference(['B3', 'B5']).rename('NDWI')

    # NDWI > 0인 조건만 적용하여 이진 마스크를 생성합니다.
    # 이 경우 물 영역은 1, 나머지는 0의 값을 가지게 됩니다.
    water_mask = ndwi.gt(0.0)

    return water_mask


def mask_water_v2(image: ee.image) -> ee.image:
    # B3 (Green): 560 nm (중심 파장)
    # B5 (SWIR 1): 1610 nm (중심 파장)
    ndwi = image.normalizedDifference(["B3", "B5"]).rename("NDWI")
    # NDWI > 0인 픽셀만 유지하고 나머지는 마스크 처리
    water_mask = ndwi.gt(0.0).selfMask()
    return water_mask


def mask_water(image: ee.image) -> ee.image:
    # B3 (Green): 560 nm (중심 파장)
    # B8 (NIR): 842 nm (중심 파장)
    ndwi = image.normalizedDifference(["B3", "B8"]).rename("NDWI")
    # NDWI > 0인 픽셀만 유지하고 나머지는 마스크 처리
    water_mask = ndwi.gt(0.0).selfMask()
    return water_mask


# 면적 계산 함수 (제곱킬로미터 단위, 소수점 둘째 자리까지)
def calculate_area(geometry):
    area = geometry.area(maxError=1).divide(1000000)
    return ee.Number(area).format("%.2f")


def cal_ratio(water_mask: ee.Image, polygon_geometry: ee.Geometry) -> None:
    """
    Calculate the ratio of water-covered pixels within a specified polygon boundary.

    Args:
        water_mask (ee.Image): A binary image where water regions are masked (1) and non-water regions are not (0).

    Returns:
        None: This function prints the water mask ratio and pixel counts within the specified boundary.
    """
    logger.debug(f"boundary: { polygon_geometry.getInfo()}")

    # polygonGeometry 내에서 waterMask를 마스킹합니다.
    water_mask_within_boundary = water_mask.clip(polygon_geometry)

    # boundary 내에서 waterMask의 픽셀 수를 계산합니다.
    # ee.Reducer.sum()을 사용하여 픽셀 값을 합한다.
    water_mask_count = (
        water_mask_within_boundary.reduceRegion(
            reducer=ee.Reducer.sum(), geometry=polygon_geometry, scale=30, maxPixels=1e9
        )
        .values()
        .get(0)
        .getInfo()
    )  # reduceRegion 결과의 첫 번째 값을 가져옵니다.

    # boundary의 면적을 계산하여 픽셀 수로 변환합니다.
    boundary_pixel_count = polygon_geometry.area().divide(
        30 * 30
    )  # 30m 해상도를 기준으로 픽셀로 변환

    # waterMask의 비율을 계산합니다.
    water_mask_ratio = (
        ee.Number(water_mask_count).divide(boundary_pixel_count).getInfo()
    )

    # 결과를 출력합니다.
    logger.debug(f"polygonGeometry 내의 waterMask 픽셀 수:{water_mask_count}")
    logger.debug(f"polygonGeometry 내의 전체 픽셀 수: {boundary_pixel_count.getInfo()}")
    logger.debug(f"polygonGeometry 내의 waterMask 비율: {water_mask_ratio}")

    return water_mask_ratio * 100


def calculate_batch_processing(criteria):
    logger.info("calculate_batch_processing started")

    # 자산 ID 정의
    polygon_asset = "projects/aerobic-tesla-417706/assets/roi/cuscos/polygon"

    # 자산 불러오기
    polygon = ee.FeatureCollection(polygon_asset)

    # 날짜 설정
    today = ee.Date(datetime.datetime.now())
    three_months_ago = today.advance(-3, "month")

    # 이미지 컬렉션 필터링
    image = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(polygon)
        .filterDate(three_months_ago, "2024-06-07")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .sort("system:time_start", False)
        .first()
    )
    water_mask = mask_water(image)

    # 이미지 날짜 정보 추출
    image_date = ee.Date(image.get("system:time_start"))
    formatted_date = image_date.format("YYYY-MM-dd").getInfo()

    # 결과 출력
    print("날짜:", formatted_date)
    cal_ratio(water_mask, polygon.geometry())

    return random.randint(1, 1000)


def calculate_minimum_distance(criteria):
    logger.info("calculate_minimum_distance started")
    # Google Earth Engine API를 사용하여 최소 거리를 계산하는 로직 구현
    ## 아래 코드 실행 시, 권한이 없는 경우 오류 발생함
    T1 = (
        ee.ImageCollection("LANDSAT/LC08/C02/T1")
        .filterDate("2024-03-15", "2024-04-03")
        .sort("system:time_start", False)
        .first()
    )

    # 이미지 정보 출력 (옵션)
    info = T1.getInfo()
    logger.info(info)
    return random.randint(1, 1000)


def calculate_surface_ratio(criteria):
    # Google Earth Engine API를 사용하여 지표수 비율을 계산하는 로직 구현

    return random.randint(1, 100)
