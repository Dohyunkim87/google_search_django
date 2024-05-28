# 베이스 이미지로 Python 3.9 슬림 버전을 사용합니다.
FROM python:3.11.7-slim

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리를 /app으로 설정합니다.
WORKDIR /app

# 로컬의 requirements.txt 파일을 컨테이너의 /app 디렉토리로 복사합니다.
COPY requirements.txt .

# requirements.txt에 명시된 의존성 패키지들을 설치합니다.
RUN pip install --no-cache-dir -r requirements.txt

# 현재 디렉토리의 모든 파일을 컨테이너의 /app 디렉토리로 복사합니다.
COPY . .

# static 파일을 모으는 명령어 실행
RUN python manage.py collectstatic --noinput

# 컨테이너 실행 시, gunicorn을 사용해 Django 애플리케이션을 실행합니다.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "myproject.wsgi:application"]

# 포트 8000을 컨테이너 외부에 노출합니다.
EXPOSE 8000
