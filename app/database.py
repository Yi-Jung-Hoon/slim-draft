import os
import cx_Oracle
import logging

logger = logging.getLogger(__name__)


def get_db_connection():
    logger.info("trying to connect to Oracle")
    host = os.getenv("ORACLE_HOST")
    port = os.getenv("ORACLE_PORT")
    service_name = os.getenv("ORACLE_SERVICE_NAME")
    user = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")

    # logger.debug(f"connection info : {host}, {port}, {service_name}")

    # dsn = cx_Oracle.makedsn(host, port, service_name=service_name)
    # logger.debug(f"dsn : {dsn}")
    dsn = "peru_high"
    logger.debug(f"connection info : {user}, {dsn}, {password}")
    connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
    return connection
