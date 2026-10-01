# Railway 用：一个容器同时跑前端静态站 + FastAPI。
# 本地 docker compose 仍用 backend/Dockerfile 与 apps/admin/Dockerfile，不要拿本文件替换。
#
# 构建上下文必须是 codes/ 目录（Git 仓库根就是 codes，或 Railway Root Directory = codes）。

FROM node:22-alpine AS web
WORKDIR /web
ENV COREPACK_ENABLE_DOWNLOAD_PROMPT=0
RUN corepack enable && corepack prepare pnpm@9.15.9 --activate
COPY apps/admin/package.json apps/admin/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY apps/admin/ ./
RUN pnpm build

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    WEB_DIR=/app/web \
    UPLOAD_DIR=/app/data/uploads

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY apps/admin/public/kyc ./kyc
COPY --from=web /web/dist ./web
RUN mkdir -p /app/data/uploads

EXPOSE 8000
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
