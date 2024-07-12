# 개요
>FastAPI를 사용하며 오라클과 연동하는 기본적인 API 서버
---
# 프로젝트 생성
app 디렉토리 생성/파일 생성
- .env, sample.env
- main.py
- database.py
- google_earth_engine.py

# 환경변수 읽어오기
1. python-dotenv 패키지 설치
```bash
pip install python-dotenv
```
2. .env 파일 생성
프로젝트 루트 디렉토리에 .env 파일을 생성하고, 오라클 데이터베이스 접속 정보를 작성합니다.
# .env
ORACLE_HOST=your_host
ORACLE_PORT=your_port
ORACLE_SERVICE_NAME=your_service_name
ORACLE_USER=your_username
ORACLE_PASSWORD=your_password

# 의존관계 추출 lib 설치 후, 의존관계 설정 파일 생성
```bash
pip install pipreqs
pipreqs .

# 프로젝트 복사 후, 의존관계 설치하기
pip install -r requirements.txt
```

pip install python-multipart

# 서버 구동
uvicorn app.main:app --reload

# oracle geo 관련
pip install geopandas