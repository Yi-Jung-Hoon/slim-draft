# models.py
import time
from .database import get_db_connection
import logging

logger = logging.getLogger(__name__)


def fetch_data(sql, bind_vars=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    logger.debug(f"sql : {sql}")
    logger.debug(f"bind_vars : {bind_vars}")

    try:
        if bind_vars is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, bind_vars)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return results
    except Exception as e:
        logger.error(f"Error occurred while fetching data: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def fetch_test_graph(bind_vars=None):
    logger.debug(f"bind_vars : {bind_vars}")
    base_sql = """
    SELECT 
      ROI_ID "id",
      SNAPSHOT_DATE "snapshot_date",
      to_char(REG_DATE,'YYYY-MM-DD') "item",
      UPDATE_DATE "update_date",
      DISTANCE "value",
      WATER_RATIO "water_ratio",
      (100- WATER_RATIO) "land_ratio",
      CLOUD_COVER "cloud_cover"
      FROM peru.STAT_INFO
     """

    if bind_vars is not None:
        sql = (
            base_sql
            + """
        WHERE REG_DATE BETWEEN TO_TIMESTAMP(:start_date, 'YYYY-MM-DD') AND TO_TIMESTAMP(:end_date, 'YYYY-MM-DD')
        ORDER BY reg_date
        """
        )
    else:
        sql = base_sql + "ORDER BY reg_date"

    return fetch_data(sql, bind_vars)


def fetch_roi():
    sql = """
    SELECT ROI_ID "id", ROI_NAME "name", DAM_ASSET_ID "dam_id", 
           POLOYGON_ASSET_ID "polygon_id", RECT_ASSET_ID "rect_id"
    FROM PERU.ROI_TAB
    """
    return fetch_data(sql)  # Use the refactored function


def fetch_mines():
    time.sleep(2)

    sql = """
    SELECT id "id", name "name", location_name "location_name" FROM PERU1.ORIGIN_MINES_LINK
    """
    return fetch_data(sql)  # Use the refactored function


# def fetch_test_graph():
#     sql = """
#     SELECT id, item, value FROM peru.graph
#     """
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     logger.debug(f"sql : {sql}")

#     try:
#         cursor.execute(sql)
#         # 컬럼 이름 가져오기
#         columns = [col[0].lower() for col in cursor.description]
#         logger.info(f"columns : {columns}")

#         # 결과를 딕셔너리 리스트로 변환
#         results = [dict(zip(columns, row)) for row in cursor.fetchall()]
#         return results
#     except Exception as e:
#         logger.error(f"Error occurred while fetching ROI data: {e}")
#         raise
#     finally:
#         cursor.close()
#         conn.close()


# def fetch_roi():
#     sql = """
#     SELECT ROI_ID "id", ROI_NAME "name", DAM_ASSET_ID "dam_id",
#            POLOYGON_ASSET_ID "polygon_id", RECT_ASSET_ID "rect_id"
#       FROM PERU.ROI_TAB
#     """
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     logger.debug(f"sql : {sql}")

#     try:
#         cursor.execute(sql)
#         # 컬럼 이름 가져오기
#         columns = [col[0] for col in cursor.description]
#         # 결과를 딕셔너리 리스트로 변환
#         results = [dict(zip(columns, row)) for row in cursor.fetchall()]
#         return results
#     except Exception as e:
#         logger.error(f"Error occurred while fetching ROI data: {e}")
#         raise
#     finally:
#         cursor.close()
#         conn.close()

# def fetch_mines():
#     sql = """
#     SELECT id, name, location_name FROM PERU1.ORIGIN_MINES_LINK
#     """
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     logger.debug(f"sql : {sql}")

#     try:
#         cursor.execute(sql)
#         # 컬럼 이름 가져오기
#         columns = [col[0] for col in cursor.description]
#         # 결과를 딕셔너리 리스트로 변환
#         results = [dict(zip(columns, row)) for row in cursor.fetchall()]
#         return results
#     except Exception as e:
#         logger.error(f"Error occurred while fetching ROI data: {e}")
#         raise
#     finally:
#         cursor.close()
#         conn.close()


def execute_query(sql, bind_vars):
    """_summary_

    Args:
        sql (_type_): _description_
        bind_vars (_type_): _description_
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    logger.debug(f"sql : {sql}")

    try:
        cursor.execute(sql, bind_vars)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def insert_many(sql, bind_vars_tuple):
    """_summary_

    Args:
        sql (_type_): _description_
        bind_vars_tuple (_type_): _description_
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    logger.debug(f"sql : {sql}")

    try:
        cursor.executemany(sql, bind_vars_tuple)
        conn.commit()
        logger.info("insert_many request completed successfully")
    finally:
        cursor.close()
        conn.close()


def insert_stats(stats):
    """계산된 통계 정보 추가

    Args:
        stats (_tuple_): 계산된 통계 정보
    """
    logger.info("insert computed data into DB")
    sql = """
    INSERT INTO peru.STAT_INFO (ROI_ID, DISTANCE, WATER_RATIO) VALUES (:ROI_ID, :DISTANCE, :WATER_RATIO)
    """
    insert_many(sql, stats)


def insert_distance(distance):
    sql = """
    INSERT INTO peru.stats (STAT_TYPE, value) VALUES (:type, :value)
    """
    bind_vars = {"type": 0, "value": distance}
    execute_query(sql, bind_vars)


def insert_ratio(ratio):
    sql = """
    INSERT INTO peru.stats (STAT_TYPE, value) VALUES (:type, :value)
    """
    bind_vars = {"type": 1, "value": ratio}
    execute_query(sql, bind_vars)
