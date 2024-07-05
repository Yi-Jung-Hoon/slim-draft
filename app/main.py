# main.py
from . import constants
import logging
import logging.config
import yaml
import os
import app.google_earth_engine as gee


def setup_logging():
    with open("logging_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    logging.info("로깅 초기화 완료")


setup_logging()

logger = logging.getLogger(__name__)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import all_routers

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

gee.initialize_gee()

app = FastAPI()

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in all_routers:
    app.include_router(router)

# 디렉토리가 없으면 생성
if not os.path.exists(constants.UPLOAD_DIRECTORY):
    os.makedirs(constants.UPLOAD_DIRECTORY)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
