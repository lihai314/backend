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

应用层统一使用 Python 标准库 `logging`，通过 `LOG_LEVEL` 控制日志级别。暂不引入 `loguru`、`structlog` 或其他第三方日志框架；长期日志禁止使用 `print`。

## 运行服务

```bash
uv run uvicorn app.main:app --reload
```

启动后可访问：

- 健康检查：`http://127.0.0.1:8000/health`
- OpenAPI 文档：`http://127.0.0.1:8000/docs`
- OpenAPI JSON：`http://127.0.0.1:8000/openapi.json`

## Docker

构建镜像：

```bash
docker build -t backend:local .
```

运行容器：

```bash
docker run --rm -p 8000:8000 --env-file .env backend:local
```

容器启动后可访问：

- 健康检查：`http://127.0.0.1:8000/health`
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
