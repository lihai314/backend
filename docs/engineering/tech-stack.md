# 后端技术栈约定

## 1. 当前后端技术栈

- 后端语言：Python
- 运行时版本：Python 3.11
- 后端框架：FastAPI
- 包管理器：uv
- 数据库：PostgreSQL
- ORM / 数据访问层：SQLAlchemy 2.0
- 数据库迁移：Alembic
- 缓存：暂不配置
- 消息队列：暂不配置
- API 风格：REST
- API 文档方案：FastAPI 内置 OpenAPI，暴露 `/docs` 和 `/openapi.json`
- 配置管理：pydantic-settings，通过 `.env` 和环境变量读取配置
- 日志方案：Python 标准库 `logging`
- 测试框架：pytest
- 接口测试：FastAPI TestClient
- 本地开发方式：uv + uvicorn
- 部署方式：Docker 镜像，当前已有 Dockerfile，可构建本地镜像

## 2. Python 版本约定

后端运行时统一使用 Python 3.11。

本地开发、Docker 镜像、未来 CI 环境应保持同一 Python minor 版本。

未经评审，不升级 Python minor 版本。

当前项目通过以下文件约束 Python 版本：

- `.python-version`：声明本地使用 Python 3.11
- `pyproject.toml`：声明 `requires-python = ">=3.11,<3.12"`
- `Dockerfile`：使用 `python:3.11-slim`

## 3. 配置管理约定

应用配置通过 `pydantic-settings` 读取。

当前基础配置包括：

- `APP_NAME`
- `ENVIRONMENT`
- `LOG_LEVEL`
- `DATABASE_URL`

必须提交 `.env.example`。

禁止提交 `.env`、数据库密码、token、密钥、云服务凭证等敏感信息。

## 4. 数据库约定

主数据库为 PostgreSQL。

数据库访问层使用 SQLAlchemy 2.0。

数据库迁移使用 Alembic。

所有 schema 变更必须通过 Alembic migration 管理。

migration 文件必须提交到 Git。

## 5. API 约定

后端 API 采用 REST 风格。

接口文档使用 FastAPI 内置 OpenAPI。

默认暴露：

- `/docs`
- `/openapi.json`

所有对前端或外部系统提供的 HTTP API，都应能在 OpenAPI 文档中体现。

## 6. 日志约定

应用层统一使用 Python 标准 logging。

暂不引入第三方日志框架。

应用代码禁止使用 `print` 作为长期日志方案。当前项目通过 Ruff `T20` 规则检查 `print` 使用。

生产日志禁止输出以下敏感信息：

- 密码
- token
- secret
- 私钥
- DATABASE_URL
- 用户敏感身份信息

后续如需结构化日志、日志采集平台或链路追踪，必须经过技术评审。

## 7. 缓存约定

当前不配置缓存。

Redis 不作为默认依赖。

只有出现明确场景时才允许引入缓存，例如：

- 登录 session
- 验证码
- 接口限流
- 分布式锁
- 热点数据缓存

引入缓存前必须说明：

1. 使用场景
2. key 设计
3. 过期策略
4. 数据一致性风险
5. 故障降级方案

## 8. 消息队列约定

当前不配置消息队列。

不默认引入 RabbitMQ、Kafka、Redis Stream、Celery、RQ 或其他任务队列系统。

如确实需要异步任务或消息队列，必须先提交技术评审说明。

## 9. 测试约定

测试框架使用 pytest。

接口测试使用 FastAPI TestClient。

后续 CI 中必须至少执行：

- 依赖安装
- 静态检查
- 类型检查
- 测试

当前本地验证命令：

```bash
uv sync
uv run ruff check .
uv run mypy src
uv run pytest
```

## 10. Docker 约定

后端应用必须可以构建为 Docker 镜像。

当前本地镜像名称可使用：

```bash
backend:local
```

当前本地构建命令：

```bash
docker build -t backend:local .
```

当前本地运行命令：

```bash
docker run --rm -p 8000:8000 --env-file .env backend:local
```

Docker 镜像必须使用 Python 3.11 minor 版本。

## 11. 新技术引入约定

新技术默认不允许随意引入；如确有明确业务或工程问题需要解决，必须先经过轻量技术评审。不得把缓存、消息队列、第三方日志框架、链路追踪、CI/CD 平台能力作为默认依赖预置。

以下类型的新技术引入必须经过技术评审：

- Python minor 版本升级
- 数据库、缓存、消息队列、任务队列
- 第三方日志框架、结构化日志平台、链路追踪
- 认证授权、安全、密钥管理
- 部署、CI/CD、staging 基础设施

技术评审至少应说明：

1. 引入原因
2. 替代方案
3. 运行成本
4. 故障风险
5. 回滚方案
