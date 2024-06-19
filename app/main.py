from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

print("dotenv completed")
from .database import get_db_connection
from .google_earth_engine import calculate_minimum_distance, calculate_surface_ratio

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

app = FastAPI()


@app.post("/api/v1/batch/statistics/distance")
def calculate_and_save_distance():
    try:
        distance = calculate_minimum_distance()

        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO peru.stats (STAT_TYPE, value) VALUES (:type, :value)
        """
        cursor.execute(insert_query, {"type": 0, "value": distance})
        conn.commit()

        cursor.close()
        conn.close()

        return {"status": "success", "distance": distance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/batch/statistics/ratio")
def calculate_and_save_ratio():
    try:
        ratio = calculate_surface_ratio()

        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO peru.stats (STAT_TYPE, value) VALUES (:type, :value)
        """
        cursor.execute(insert_query, {"type": 1, "value": ratio})
        conn.commit()

        cursor.close()
        conn.close()

        return {"status": "success", "ratio": ratio}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
