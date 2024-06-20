# models.py
from .database import get_db_connection
import logging

logger = logging.getLogger(__name__)


def execute_query(sql, bind_vars):
    conn = get_db_connection()
    cursor = conn.cursor()
    logger.debug(f"sql : {sql}")

    try:
        cursor.execute(sql, bind_vars)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


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
