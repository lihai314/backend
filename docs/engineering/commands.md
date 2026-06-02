# 项目命令与脚本

## 1. Makefile 入口

常用命令以 `make` 作为稳定入口：

```bash
make help
make install
make format
make lint
make lint-fix
make type-check
make test
make test-cov
make check
make hooks-install
make hooks-run
make docker-build
make docker-up
make docker-ps
make docker-health
make docker-logs
make docker-down
make docker-local-check
```

`make docker-down` 不删除数据卷。需要清理 PostgreSQL 和 Redis 数据时，手动执行：

```bash
docker compose down -v
```

## 2. Docker 命令

本地完整启动：

```bash
make docker-up
```

本地完整检查：

```bash
make docker-local-check
```

`make docker-local-check` 使用隔离 Compose 项目 `backend-local-check` 和独立端口：

- 后端：`18000`
- PostgreSQL：`15432`
- Redis：`16379`

该命令结束后会清理隔离项目的容器、网络、数据卷和临时镜像，不会删除当前开发环境的数据卷。

## 3. 验证范围

本项目当前验证以下内容：

- Python 版本
- uv 依赖同步
- Ruff 格式化和 lint
- mypy 类型检查
- pytest 和覆盖率
- pre-commit hooks
- Docker build
- Docker Compose config
- Docker Compose 启停
- 后端健康检查
- Redis ping
- PostgreSQL readiness
- Alembic upgrade
- Alembic revision 生成能力
- 本地 uvicorn 启动
- 独立 Docker 容器启动
