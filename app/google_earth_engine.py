# google_earth_engine.py
import logging
import ee
from datetime import datetime

logger = logging.getLogger(__name__)

logging.getLogger("google_auth_httplib2").setLevel(logging.ERROR)
logging.getLogger("googleapiclient.discovery").setLevel(logging.ERROR)
logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)

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


def calculate_statistics(roi):
    snippet_id = "COPERNICUS/S2_SR_HARMONIZED"
    start_date = "2024-01-01"
    end_date = "2024-06-30"  # today
    cloud_coverage = 20

    # ROI 데이터에서 polygon과 dam 추출
    polygon = ee.Geometry.Polygon(roi["POLYGON"]["SDO_ORDINATES"])
    dam = ee.Geometry.LineString(roi["DAM"]["SDO_ORDINATES"])

    image_collection = (
        ee.ImageCollection(snippet_id)
        .filterBounds(polygon)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_coverage))
        .sort("system:time_start", False)
        .map(lambda image: image.clip(polygon))
    )  # 각 이미지를 polygon으로 클리핑

    latest_image = image_collection.first()
    time_start_ms = latest_image.get("system:time_start").getInfo()

    # Unix 타임스탬프(밀리초)를 datetime 객체로 변환
    time_start_datetime = datetime.fromtimestamp(time_start_ms / 1000)

    # datetime 객체를 'YYYY-MM-dd' 형식의 문자열로 변환
    time_start_formatted = time_start_datetime.strftime("%Y-%m-%d")

    logger.info(f"Latest image date: {time_start_formatted}")

    water_mask = mask_water(latest_image)

    vectors = water_mask.reduceToVectors(
        geometry=latest_image.geometry(),
        scale=30,
        eightConnected=False,
        maxPixels=1e9,
        geometryType="polygon",
    )

    # 각 벡터 피처의 기하학을 처리
    polygons = ee.FeatureCollection(vectors)

    # 각 폴리곤의 vertex 수 계산
    polygons_with_vertex_count = polygons.map(
        lambda feature: feature.set(
            "vertexCount", feature.geometry().coordinates().flatten().length()
        )
    )

    largest_polygon = polygons_with_vertex_count.sort("vertexCount", False).first()

    # 최소 거리 계산
    min_distance = dam.distance(largest_polygon.geometry(), 1).getInfo()

    # 결과 출력
    logger.info(f"min_distance: {min_distance}m")

    # 지표수 비율 계산
    water_ratio = cal_ratio(water_mask, polygon)

    return min_distance, water_ratio
