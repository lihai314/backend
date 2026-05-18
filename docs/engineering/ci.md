# 基础 CI 规范

## 1. CI 平台

本仓库使用 GitHub Actions。

工作流文件：

```text
.github/workflows/backend-ci.yml
```

## 2. 触发条件

CI 在以下场景触发：

- Pull Request 到 `main`
- Push 到 `main`

## 3. Python 版本

CI 使用 Python 3.11。

本地开发、Docker 和 CI 应保持同一 Python minor 版本。

## 4. 检查内容

基础 CI 执行：

```bash
uv sync --frozen
uv run ruff check .
uv run mypy src
uv run pytest
docker build -t backend:ci .
```

当前测试不依赖真实 PostgreSQL，因此基础 CI 暂不启动数据库 service。

## 5. 合并规则

基础 CI 完成后，进入 `main` 的 PR 应通过以下检查：

- ruff
- mypy
- pytest
- Docker build

## 6. 当前不做的事情

当前 CI 不负责：

- staging 部署
- production 部署
- Docker 镜像推送
- Kubernetes 部署
- 多 Python 版本矩阵
- 静态 `openapi.json` 导出检查

## 7. 后续扩展

后续可以逐步增加：

- 测试覆盖率
- OpenAPI 导出和 diff 检查
- Alembic migration 检查
- Docker 镜像推送
- staging 部署
