# main.py
import logging
import logging.config
import yaml
import app.google_earth_engine as gee


def setup_logging():
    with open("logging_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    logging.info("로깅 초기화 완료")


setup_logging()

logger = logging.getLogger(__name__)

from fastapi import FastAPI
from app.routers import (
    statistics_router,
    test_router,
    root_router,
    satellite_router,
    mines_router,
)
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

gee.initialize_gee()

app = FastAPI()
app.include_router(statistics_router)
app.include_router(test_router)
app.include_router(root_router)
app.include_router(satellite_router)
app.include_router(mines_router)


@app.get("/")
def test():
    return {"status": "success", "message": "OK"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
