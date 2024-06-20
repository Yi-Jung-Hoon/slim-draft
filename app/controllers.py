# controllers.py
import logging

logger = logging.getLogger(__name__)

from fastapi import HTTPException
from .models import insert_distance, insert_ratio
from .google_earth_engine import calculate_minimum_distance, calculate_surface_ratio


def calculate_and_save_distance():
    try:
        distance = calculate_minimum_distance()
        logger.debug(f"distance : {distance}")
        insert_distance(distance)
        return {"status": "success", "distance": distance}
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))


def calculate_and_save_ratio():
    try:
        ratio = calculate_surface_ratio()
        insert_ratio(ratio)
        return {"status": "success", "distance": ratio}
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))
