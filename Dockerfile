ARG UV_BASE_IMAGE=ghcr.io/astral-sh/uv:0.11.3
ARG PYTHON_BASE_IMAGE=python:3.11-slim

# ==================== 第一阶段：uv 工具镜像 ====================
# 使用官方 uv 镜像，仅用于获取 uv 二进制文件
FROM ${UV_BASE_IMAGE} AS uv

# ==================== 第二阶段：依赖构建镜像 ====================
FROM ${PYTHON_BASE_IMAGE} AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

# 复制 uv 二进制文件
COPY --from=uv /uv /usr/local/bin/uv

# 先安装第三方依赖，提高业务代码变更时的 Docker 构建缓存命中率
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable --no-install-project

# 再复制源码并安装当前项目包
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# ==================== 第三阶段：运行环境镜像 ====================
FROM ${PYTHON_BASE_IMAGE} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

# 创建非 root 用户运行应用
RUN groupadd --system app \
    && useradd --system --gid app --home-dir /app --shell /usr/sbin/nologin app

# 运行镜像只保留生产虚拟环境，不复制源码、README 或锁文件
COPY --from=builder --chown=app:app /app/.venv /app/.venv

USER app

EXPOSE 8000

# 使用 uvicorn 启动应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
