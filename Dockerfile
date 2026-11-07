FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

# 対局者名・タイトルなどの日本語文字列描画用フォント
# (Pillow は manylinux wheel で入るのでビルドツールは不要)
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run は PORT 環境変数でポートを渡す
CMD exec gunicorn --bind :${PORT:-8080} --workers 1 --threads 8 --timeout 0 main:app
