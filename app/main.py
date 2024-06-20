# main.py
import logging
import logging.config
import yaml

# def setup_logging():
#     logging.basicConfig(
#         level=logging.DEBUG,
#         format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#         handlers=[logging.FileHandler("my_project.log"), logging.StreamHandler()],
#     )
#     logging.info("로깅 초기화 완료")


# setup_logging()


def setup_logging():
    with open("logging_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    logging.info("로깅 초기화 완료")


setup_logging()

logger = logging.getLogger(__name__)

from fastapi import FastAPI
from dotenv import load_dotenv
from .controllers import calculate_and_save_distance, calculate_and_save_ratio

logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()


@app.get("/")
def test():
    return {"status": "success", "message": "OK"}


@app.post("/api/v1/batch/statistics/distance")
def calculate_distance():
    return calculate_and_save_distance()


@app.post("/api/v1/batch/statistics/ratio")
def calculate_ratio():
    return calculate_and_save_ratio()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
