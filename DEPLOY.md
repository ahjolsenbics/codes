# 运满满 Demo 部署

当前是展示阶段。把整个 `codes/` 目录交给对方即可。首次启动会自动写入与本地相同的演示货盘、司机、运单和资质，不必再单独拷贝数据库文件。

## 数据存在哪

| 环境 | 存储 | 说明 |
| --- | --- | --- |
| 本地开发（`pnpm dev` + uvicorn） | `codes/backend/yunmm_demo.db`（SQLite 文件） | 空库时 `seed.py` 自动灌入演示数据 |
| Docker / 服务器 | Postgres 卷 `yunmm_pg` | API 容器第一次连上空库同样走 `seed.py` |
| 证件与上传图 | 卷 `yunmm_uploads` 或本地 `codes/backend/data/uploads` | 演示资质图在前端静态 `/kyc` |

演示账号（密码均为 `Yunmm@2026`，短信验证码 `000000`）：

- 运营后台 `13800001000`
- 货主 `13800001001`
- 司机 `13900001001`

## 本地 Docker

机器需安装 Docker Desktop（或 Docker Engine + Compose）。

```bash
cd codes
docker compose --profile app up -d --build
```

打开 http://127.0.0.1:8080  
API：http://127.0.0.1:8000

停掉：`docker compose --profile app down`  
清空数据并重新灌演示库：

```bash
docker compose --profile app down -v
docker compose --profile app up -d --build
```

## 服务器部署

与本地同一条命令。建议：

1. 把 `codes/` 拷到服务器（不要带 `node_modules`、`.venv`）。
2. 安装 Docker，开放 **8080**（页面）和按需开放 **8000**（直连 API）。
3. 在 `codes/` 执行：

```bash
docker compose --profile app up -d --build
```

4. 若前面有 Nginx / 宝塔反向代理，把域名反代到 `127.0.0.1:8080`。页面和 `/api`、`/files` 都走 8080，浏览器只访问一个入口。
5. 有独立域名时，可在 `docker-compose.yml` 的 `api.environment.CORS_ORIGINS` 里加上 `https://你的域名`。

打包给别人时：压缩 `codes/` 即可。对方解压后执行上面的 compose。不要依赖你本机的 SQLite 文件；容器用 Postgres，启动时空库会自动 seed。

## 部署到 Railway

云端展示用 Railway 时，不要导入 `docker-compose.yml`。步骤、环境变量和数据说明见 **[DEPLOY-RAILWAY.md](./DEPLOY-RAILWAY.md)**。那边会把前端和 API 打进一个 Web 服务，数据库用 Railway 的 Postgres 插件，空库同样自动灌演示数据。

## 不走 Docker 的本地开发

```bash
# 后端
cd codes/backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 前端
cd codes/apps/admin
pnpm install
pnpm dev
```

前端默认 http://127.0.0.1:5175 ，接口由 Vite 代理到 8000。SQLite 会生成在 `backend/yunmm_demo.db`。
