# ==================== 第一阶段：uv 工具镜像 ====================
# 使用官方 uv 镜像，仅用于获取 uv 二进制文件
FROM ghcr.io/astral-sh/uv:0.11.3 AS uv

# ==================== 第二阶段：运行环境镜像 ====================
FROM python:3.11-slim AS runtime

# Python 与 uv 环境变量配置
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

# 复制 uv 二进制文件
COPY --from=uv /uv /usr/local/bin/uv

# 创建非 root 用户运行应用
RUN groupadd --system app \
    && useradd --system --gid app --home-dir /app --shell /usr/sbin/nologin app

# 复制项目依赖定义和源代码
COPY pyproject.toml uv.lock README.md ./
COPY src ./src

# 安装生产依赖（冻结版本、不安装 dev、不进行可编辑安装）
RUN uv sync --frozen --no-dev --no-editable \
    && chown -R app:app /app

USER app

EXPOSE 8000

# 使用 uvicorn 启动应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
