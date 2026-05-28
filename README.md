# FastAPI 后端最小可运行脚手架

这是一个同步 FastAPI 后端最小脚手架，使用 Python 3.11、uv、PostgreSQL、SQLAlchemy 2.0、Alembic、Pydantic v2、pytest、Ruff 和 mypy。

## 本地准备

本地、Docker、CI 统一使用 Python 3.11 minor 版本。项目通过 `.python-version` 和 `pyproject.toml` 约束本地运行时：

```bash
uv python install 3.11
uv sync
uv run python --version
```

`uv run python --version` 应输出 `Python 3.11.x`。

安装依赖：

```bash
uv sync
```

复制环境变量示例：

```bash
cp .env.example .env
```

根据本地 PostgreSQL 修改 `.env` 中的 `DATABASE_URL`。
如需使用 Redis，可修改 `.env` 中的 `REDIS_URL`。

应用层统一使用 Python 标准库 `logging`，通过 `LOG_LEVEL` 控制日志级别。暂不引入 `loguru`、`structlog` 或其他第三方日志框架；长期日志禁止使用 `print`。

## 本地开发

### 1. 安装依赖

```bash
uv sync
```

### 2. 准备环境变量

```bash
cp .env.example .env
```

默认本地数据库连接：

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/backend
```

### 3. 启动 PostgreSQL

```bash
docker compose up -d postgres
```

如需同时启动 Redis：

```bash
docker compose up -d postgres redis
```

### 4. 执行数据库迁移

```bash
uv run alembic upgrade head
```

### 5. 启动后端服务

```bash
uv run uvicorn app.main:app --reload
```

默认访问：

- 健康检查：`http://127.0.0.1:8000/api/v1/health`
- API 文档：`http://localhost:8000/docs`
- OpenAPI JSON：`http://localhost:8000/openapi.json`

### 6. 停止本地依赖

```bash
docker compose down
```

如需清理本地数据库数据：

```bash
docker compose down -v
```

## Docker

构建、启动、联调、测试并自动清理本地 Docker 资源：

```bash
make docker-local-check
```

该命令会启动后端、PostgreSQL 和 Redis，检查健康接口、API 文档、Redis、PostgreSQL、Compose 配置、mypy 和 pytest，结束后自动删除容器、网络、数据卷和临时镜像 `backend:local-check`。如果本地不存在 `.env`，会临时使用 `.env.example` 生成，并在结束后删除；如果 PostgreSQL、Redis、Python 或 uv 基础镜像是本次命令新拉取的，也会自动删除。

一键启动后端、PostgreSQL 和 Redis：

```bash
docker compose up -d --build
```

构建镜像：

```bash
docker build -t backend:local .
```

如果拉取 Docker Hub 的 `python:3.11-slim` 经常超时，可以指定可访问的 Python 基础镜像：

```bash
PYTHON_BASE_IMAGE=public.ecr.aws/docker/library/python:3.11-slim docker compose up -d --build
```

单独构建镜像时也可以使用相同参数：

```bash
docker build \
  --build-arg PYTHON_BASE_IMAGE=public.ecr.aws/docker/library/python:3.11-slim \
  -t backend:local .
```

如果 `ghcr.io/astral-sh/uv:0.11.3` 也不可访问，可以通过 `UV_BASE_IMAGE` 指定可访问的 uv 镜像源。生产或发布构建建议把 `PYTHON_BASE_IMAGE` 和 `UV_BASE_IMAGE` 指定为带 digest 的镜像引用，保证构建结果可复现。

运行容器：

```bash
docker run --rm -p 8000:8000 --env-file .env backend:local
```

容器启动后可访问：

- 健康检查：`http://127.0.0.1:8000/api/v1/health`
- OpenAPI 文档：`http://127.0.0.1:8000/docs`

## 数据库迁移

创建迁移：

```bash
uv run alembic revision --autogenerate -m "初始化迁移"
```

执行迁移：

```bash
uv run alembic upgrade head
```

## 质量检查

安装本地 Git hooks：

```bash
make hooks-install
```

提交前可手动执行全量 hooks：

```bash
make hooks-run
```

本地 hooks 会依次执行 Ruff 格式化、Ruff lint 自动修复、mypy 类型检查和带覆盖率的 pytest。

运行测试：

```bash
uv run pytest
```

运行 Ruff：

```bash
uv run ruff check .
```

运行 mypy：

```bash
uv run mypy src
```

也可以使用 Makefile 统一入口：

```bash
make format
make lint
make type-check
make test
make test-cov
make check
```
