FROM python:3.12-slim

WORKDIR /app

# Install system dependencies (curl for healthchecks, ffmpeg for video rendering)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    libass-dev \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pymysql cryptography argon2-cffi alembic pydantic-settings redis pytest httpx

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
