FROM python:3.9-slim

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコピー
COPY . .

# ログディレクトリの作成
RUN mkdir -p logs

# 本番環境設定
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# ポート8000で実行
EXPOSE 8000

# Gunicornで実行（本番環境用）
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "app:app"]