# 运满满 Demo：Railway 部署方案

当前仍是展示阶段。Railway 上跑起来后，**空 Postgres 会在第一次启动时自动写入与本地相同的演示数据**（货盘、司机、运单、资质、账号），不必再导入 SQLite 或备份文件。

Railway **不会执行** `docker-compose.yml`。下面这套方案把前端和 API 打进 **一个 Web 服务**，数据库用 Railway 托管的 Postgres。Redis 在 Demo 里没有实际读写，**不要加**。

---

## 1. 上线后长什么样

```
浏览器  https://xxx.up.railway.app
              │
              ▼
        ┌─────────────┐     私有网络      ┌──────────────────┐
        │  Web 服务    │ ───────────────► │ Postgres 插件     │
        │  前端 + API  │   DATABASE_URL   │ 演示数据存在这里   │
        └─────────────┘                   └──────────────────┘
```

访问这个域名就能打开首页。`/api`、`/files`、页面路由都在同一个域名下，没有跨域问题。

演示账号（密码均为 `Yunmm@2026`，短信验证码 `000000`）：

| 角色 | 手机号 |
| --- | --- |
| 运营后台 | `13800001000` |
| 货主 | `+7 7270001005` |
| 司机 | `+7 7010001002` |

健康检查：`https://你的域名/api/v1/health` 应返回 `"status": "ok"`。

---

## 2. 费用与限制（先看再动手）

- 需要 [Railway](https://railway.app) 账号。Hobby 方案通常要绑定支付方式，新账号可能有试用额度。
- 本方案 **2 个服务**：`Postgres` + `web`。不要再开 Redis、不要再拆一个前端容器，避免多花钱。
- 机器在海外。国内网络访问 `*.up.railway.app` 可能偏慢或不稳定，给别人演示时建议先自己打开确认。
- 区域尽量选 **Southeast Asia（新加坡）**，比美国节点更接近国内访问。

---

## 3. 代码要先上 GitHub

Railway 从 Git 仓库构建。把 `codes/` 推上去即可（不要带 `node_modules`、`.venv`、`*.db`，仓库里的 `.gitignore` 已排除）。

### 做法 A（推荐）：只把 `codes` 当成仓库

在 `codes/` 目录初始化并推送：

```bash
cd codes
git init
git add .
git commit -m "YunMM demo for Railway"
# 在 GitHub 新建空仓库后：
git remote add origin https://github.com/你的用户名/yunmm-demo.git
git branch -M main
git push -u origin main
```

后面 Railway **不用改 Root Directory**。

### 做法 B：整个 YunMM 项目已经是一个 Git 仓库

照常 push。到 Railway 后必须改一处（见第 4.3 步）：

- Root Directory = `codes`

---

## 4. 在 Railway 建项目（按这个顺序）

打开 [https://railway.app/new](https://railway.app/new)。

### 4.1 建空项目

1. 选 **Empty Project**（空项目），不要选 Docker Compose 导入。
2. 项目名可写成 `yunmm-demo`。
3. 右上角 **Settings → Environments** 里确认当前是 `production`。
4. 项目 Settings 里把 **Region** 调到 **Southeast Asia**（若列表有）。

### 4.2 先加数据库

1. 画布上点 **Add Service**（或 **Create**）→ **Database** → **PostgreSQL**。
2. 等状态变成 **Online**。默认库名/账号由 Railway 生成即可，不要改。
3. 点进这个 Postgres 服务，记住它在画布上的 **名称**（一般是 `Postgres`）。后面变量引用要用这个名字。

**不要**给 Postgres 点 Generate Domain，数据库只走内网。

### 4.3 再加 Web 服务

1. **Add Service** → **GitHub Repo** → 选上一步推送的仓库。
2. 服务名称改成 `web`（方便对照本文档）。
3. 打开 `web` → **Settings**：

仓库地址如果是 `github.com/你的用户名/codes`（做法 A），**Root Directory 必须留空**。填成 `codes` 会立刻报 `There was an error deploying from source`。

2026-08-28 之后新建的服务 **不能再用** `railway.toml`（Config as Code 已废弃）。Settings 里 **Railway Config File 必须留空**，否则也会报同一句 source 错误。

| 配置项 | 做法 A（仓库就是 codes，例如 `ahjolsenbics/codes`） | 做法 B（仓库是 YunMM 根） |
| --- | --- | --- |
| Root Directory | **留空**（不要填 `codes`） | `codes` |
| Builder | Dockerfile | Dockerfile |
| Dockerfile Path | `/Dockerfile` | `/Dockerfile` |
| Railway Config File | **留空**（不要填 `/railway.toml`） | **留空** |
| Watch Paths | 留空或 `**` | `codes/**` |
| Branch | `main` | `main` |

同一页 **Deploy** 里再设：

- Healthcheck Path：`/api/v1/health`
- Healthcheck Timeout：`180`

4. 同一页 **Networking → Generate Domain**，记下 `https://xxxx.up.railway.app`。
5. 先不要急着看页面，先配变量。

### 4.4 给 Web 配环境变量

打开 `web` → **Variables** → **Add Variable**。至少这几项：

| 变量 | 值 | 说明 |
| --- | --- | --- |
| `DATABASE_URL` | 点 **Add Reference**（变量引用），选 `Postgres` 的 `DATABASE_URL` | 画面上会显示成 `${{Postgres.DATABASE_URL}}`。若你把数据库服务改名了，把 `Postgres` 换成实际名称 |
| `UPLOAD_DIR` | `/app/data/uploads` | 证件上传目录 |
| `WEB_DIR` | `/app/web` | 前端打包结果 |
| `ENV` | `demo` | 启动日志用 |

不要手动粘贴一条带密码的 `postgres://...`，用引用才能在 Railway 轮换密码后自动更新。

`CORS_ORIGINS` 可以不填：接口已允许任意 `http/https` 来源，而且页面和 API 同域。

Redis **不要配**。

### 4.5 触发部署

1. 打开 `web` → **Deployments**，点 **Deploy**（或推一次空 commit）。
2. 第一次构建大约 3～8 分钟：装 pnpm 依赖、编译 Vue、装 Python 依赖。
3. 构建成功后，看 Deploy Logs，应出现类似：

   `Demo 数据已写入`  
   `服务启动 ... db=postgresql+psycopg2://...`

4. 浏览器打开第 4.3 步生成的域名。

---

## 5. 数据存在哪、怎么带给别人

| 内容 | 存在哪 | 给别人时怎么处理 |
| --- | --- | --- |
| 货盘 / 账号 / 运单 / 资质记录 | Railway **Postgres** | 空库启动即自动 seed，与本地展示数据同一套 |
| 资质示意图（KYC 预览图） | 镜像内 `/kyc`（前端 `public/kyc`） | 已打进镜像，不用另传 |
| 用户现场上传的图片 | 容器内 `/app/data/uploads` | **默认重启会丢**。展示阶段一般够用；若要保留，见下面「挂卷」 |
| 本机 SQLite `yunmm_demo.db` | 不要上传 | Railway 不用这个文件 |

给别人看两种方式：

1. **直接把 Railway 域名发给对方**（最快，数据已经在云库里）。
2. **让对方自己部署一份**：把 GitHub 仓库 + 本文档给他们。他们按第 4 步走一遍，空库会自动灌同样的演示数据。

### 可选：给上传文件挂持久卷

`web` → **Settings → Volumes → Add Volume**

- Mount Path：`/app/data`
- 大小：1 GB 足够展示

不挂卷也能正常演示首页和运营台；只是有人上传新证件后，下一次重新部署可能看不到那张新图。

### 把演示库清掉重灌

Postgres 插件里打开 **Data** / Query（或用 Railway 提供的 `psql`）：

```sql
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

然后在 `web` 服务点 **Restart**。启动时发现用户表为空，会再次执行 `seed.py`。

---

## 6. 自定义域名（可选）

1. `web` → **Settings → Networking → Custom Domain**，填 `demo.你的域名.com`。
2. 按提示去 DNS 加 CNAME（或 Railway 显示的记录）。
3. 等证书 Ready。之后对外只发这个域名。

---

## 7. 以后改代码怎么更新

把代码 push 到 GitHub 的 `main`（或你在 Railway 里选的分支）。Railway 会自动构建并发布新版本。

Postgres **不会**被重建，已经产生的业务数据还在。`seed_if_empty` 只在库是空的时候灌全量演示数据；库里已有用户就不会再整库覆盖。

---

## 8. 用 CLI 部署（不走控制台逐步点）

机器需安装 Node，然后：

```bash
npm i -g @railway/cli
cd codes
railway login
railway init
railway add --database postgres
```

在控制台把第 4.4 节的变量配到 `web` 上（CLI 对 `${{Postgres.DATABASE_URL}}` 引用不如网页直观，建议变量仍在网页里加）。

```bash
railway up
railway domain
```

`railway up` 会用当前目录的 `Dockerfile` 构建。

---

## 9. 常见失败

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `Deploying service from xxx/codes` 然后 `There was an error deploying from source` | ① Root Directory 填了 `codes`（仓库根已经是 codes）；② **Railway Config File 填了 `/railway.toml`**——2026-08-28 后新服务不能用 Config as Code；③ GitHub 应用没授权这个仓库 | Root Directory **清空**；Railway Config File **清空**；Dockerfile Path 填 `/Dockerfile`；到 [GitHub Applications → Railway](https://github.com/settings/installations) 勾上仓库后再 Deploy |
| 构建报 `COPY backend/requirements.txt: not found` | 构建上下文不是 `codes/` | Root Directory 改成 `codes`，或把 Git 仓库改成只含 `codes` |
| 构建用了 Nixpacks / 没吃到 Dockerfile | Settings 里 Builder = Dockerfile，Dockerfile Path = `/Dockerfile` |
| `ERR_PNPM_TARBALL_URL_MISMATCH` / lockfile failed supply-chain policy | 本机 `pnpm-lock.yaml` 里的包地址是 npmmirror，Railway 用官方 npm 源校验对不上；Corepack 还会拉最新 pnpm 12 | 已把锁文件改成 `registry.npmjs.org`，镜像里钉死 `pnpm@9.15.9`。把这次改动 push 后再 Deploy |
| 健康检查超时、容器反复重启 | 第一次连不上库，或 `DATABASE_URL` 没配上，或健康检查超时太短（启动时要灌演示数据） | 确认变量引用的是当前项目里的 Postgres；Postgres 为 Online；Deploy 里 Healthcheck Path=`/api/v1/health`、Timeout=`180`；再 Restart `web` |
| 日志里 `could not translate host name` / IPv6 连不上 | 偶发的私网解析问题 | 临时改为 Postgres 服务 Variables 里的 **公网** `DATABASE_URL`，并在末尾加 `?sslmode=require`（仅排查用） |
| 打开域名是 502 / Application failed | 进程没监听 `$PORT` | 确认用的是仓库根目录 `Dockerfile`，启动命令带 `--port ${PORT:-8000}` |
| 页面出了但登录失败 | 库是空的或 seed 失败 | 看启动日志有没有 `Demo 数据已写入`；没有就按第 5 节清库重启 |
| 国内打不开 | 海外节点或 DNS | 换节点重试、或前面加国内反代；展示阶段可让对方开代理访问 |

---

## 10. 和本地 Docker 的对应关系

| 本地 `docker compose --profile app` | Railway |
| --- | --- |
| 浏览器 `http://IP:8080` | `https://xxx.up.railway.app` |
| 容器 `admin`（nginx）+ 容器 `api` | **合并为** 一个 `web` 服务 |
| 容器 `postgres` + 卷 `yunmm_pg` | Railway **PostgreSQL** 插件 |
| 容器 `redis` | 不部署 |
| 卷 `yunmm_uploads` | 可选 Volume，挂 `/app/data` |
| 首次空库 `seed.py` | 同样会跑 |

本地开发、自己的 Linux 服务器，仍看 `DEPLOY.md`，继续用 `docker compose --profile app up -d --build`。
