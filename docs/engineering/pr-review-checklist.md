# 后端 PR Review 清单

## 1. Review 目标

Review 的目标不是重新实现一遍代码，而是确认变更可以安全进入 `main`：

1. 需求被正确实现
2. 行为变化清晰可控
3. 测试和验证足够支撑合并
4. 数据库、配置、API、依赖等高风险变更没有遗漏
5. 代码符合当前后端工程约定

`main` 必须始终保持可运行。无法确认这一点时，不要 Approve。

## 2. 推荐审查顺序

建议按以下顺序 review，避免一上来陷进局部 diff：

1. 看 PR 标题和描述，确认是否符合 Conventional Commits，是否只解决一个问题
2. 看验证方式，确认作者已说明并执行必要检查
3. 看文件列表，判断是否出现意料之外的范围扩张
4. 先看测试，再看实现
5. 按本清单检查数据库、配置、API、依赖、Docker、CI 等条件项
6. 最后给出 `Approve`、`Comment` 或 `Request changes`

## 3. 通用必查项

每个 PR 都必须检查：

- [ ] PR 标题遵守 Conventional Commits
- [ ] PR 描述说明了变更内容、验证方式和影响范围
- [ ] PR 只解决一个清晰问题，没有混入无关重构或格式化
- [ ] 变更范围和 PR 描述一致
- [ ] 没有提交 `.env`、密钥、token、数据库密码或云服务凭证
- [ ] 没有提交 `.venv/`、缓存文件、系统文件或无关生成物
- [ ] 代码没有引入未评审的新技术、新框架或新外部服务
- [ ] 命名清晰，模块边界符合当前项目结构
- [ ] 没有使用 `print` 作为长期日志方案
- [ ] 错误响应不暴露 traceback、数据库错误细节或内部异常消息
- [ ] CI 必须通过 `Quality checks` 和 `Docker build`

## 4. 正确性与可维护性

Reviewer 需要重点看：

- [ ] 代码路径覆盖了正常场景和关键异常场景
- [ ] 条件判断、默认值和边界值符合预期
- [ ] 没有吞掉异常或返回误导性成功结果
- [ ] 没有把临时方案写成长期接口
- [ ] 没有重复实现已有公共能力
- [ ] 没有把业务逻辑塞进配置、迁移、测试辅助或基础设施文件
- [ ] 注释解释的是必要上下文，而不是重复代码本身

## 5. 测试与验证

每个 PR 都应确认：

- [ ] 新行为有对应 pytest 覆盖
- [ ] 修复 bug 时有能复现问题的回归测试
- [ ] 测试断言的是行为，不是无意义地覆盖实现细节
- [ ] 测试不依赖开发者本机状态
- [ ] 测试不连接真实外部数据库或生产服务
- [ ] 作者已执行或 CI 已覆盖：

```bash
uv run ruff check .
uv run mypy src
uv run pytest
```

涉及 Docker 时还应确认：

```bash
docker build -t backend:local .
```

## 6. API 变更检查

如果 PR 涉及 HTTP API，必须检查：

- [ ] 业务 API 使用 `/api/v1` 前缀
- [ ] 新增或修改的 API 能体现在 `/openapi.json`
- [ ] 请求体和响应体使用明确的 Pydantic Schema
- [ ] 长期接口不直接返回 ORM Model
- [ ] 长期接口不直接返回裸 `dict`
- [ ] 成功响应符合 `code` / `message` / `data`
- [ ] 错误响应符合 `code` / `message` / `data`
- [ ] HTTP 状态码和业务错误码语义一致
- [ ] 422 校验错误如有影响，仍保留 `data.details`
- [ ] 不兼容变更已说明影响范围，并已同步相关调用方
- [ ] 动作接口使用 `POST /api/v1/{resources}/{resource_id}/actions/{action-name}` 或 `POST /api/v1/{resources}/actions/{action-name}`
- [ ] 动作名使用 kebab-case，且语义明确

## 7. 数据库与迁移检查

如果 PR 涉及数据库结构或 ORM Model，必须检查：

- [ ] SQLAlchemy Model 变更对应 Alembic migration
- [ ] migration 文件已提交到 Git
- [ ] migration 命名能表达业务意图
- [ ] 没有只手动改数据库而不补 migration
- [ ] migration 不包含真实数据、密钥或环境相关配置
- [ ] migration 可以正向执行
- [ ] 如有破坏性变更，PR 已说明风险和回滚方案

## 8. 配置检查

如果 PR 新增或修改配置项，必须检查：

- [ ] 使用 `pydantic-settings` 读取配置
- [ ] `.env.example` 已同步更新
- [ ] 配置项有明确默认值或启动校验
- [ ] 没有提交真实 `.env`
- [ ] 没有在代码、文档或 workflow 中写入真实密钥
- [ ] 配置名语义清楚，符合现有命名风格

## 9. 依赖检查

如果 PR 涉及依赖，必须检查：

- [ ] 使用 `uv` 管理依赖
- [ ] `pyproject.toml` 和 `uv.lock` 都已更新
- [ ] 新依赖有明确引入原因
- [ ] 没有引入重复能力或过重依赖
- [ ] 没有绕过技术评审引入缓存、消息队列、第三方日志框架、认证系统等基础设施
- [ ] 没有改用非约定技术，例如 `asyncpg`、`psycopg2` 或异步 SQLAlchemy

## 10. Docker 与本地开发检查

如果 PR 涉及 Docker 或本地开发流程，必须检查：

- [ ] Dockerfile 仍使用 Python 3.11
- [ ] Docker build 不依赖 `.env`
- [ ] `.dockerignore` 排除了 `.env`、`.venv/`、缓存、日志和 Git 元数据
- [ ] `docker-compose.yml` 当前只包含 PostgreSQL
- [ ] README 本地开发流程仍可执行
- [ ] 没有引入 Redis、消息队列、Nginx、Kubernetes、staging 或 CD

## 11. CI 检查

如果 PR 涉及 CI，必须检查：

- [ ] GitHub Actions 仍只使用 Python 3.11
- [ ] CI 执行 `uv sync --frozen`
- [ ] CI 执行 `uv run ruff check .`
- [ ] CI 执行 `uv run mypy src`
- [ ] CI 执行 `uv run pytest`
- [ ] CI 执行 `docker build -t backend:ci .`
- [ ] CI 不推送 Docker 镜像
- [ ] CI 不做 staging、production、CD 或 Kubernetes 部署
- [ ] CI 不依赖本地 `.env` 或真实外部数据库

## 12. 安全与日志检查

每个 PR 都应留意：

- [ ] 日志使用 Python 标准 `logging`
- [ ] 日志不输出密码、token、secret、私钥、完整 `DATABASE_URL`
- [ ] 错误响应不暴露内部异常细节
- [ ] 认证相关接口如有新增，必须说明鉴权边界
- [ ] 没有把用户敏感身份信息写入日志、异常消息或测试快照

## 13. Review 结论规则

### 可以 Approve

满足以下条件时可以 Approve：

1. 变更意图清楚
2. CI 全部通过
3. 测试和文档足够支撑变更
4. 没有阻塞问题
5. 高风险项已说明并处理

### 应 Request changes

出现以下情况应要求修改：

- 代码会导致明显 bug、数据错误或安全风险
- CI 未通过且没有合理解释
- 缺少必要测试
- API、配置、数据库、依赖变更未按规范处理
- 错误响应或日志暴露敏感信息
- PR 混入大量无关变更，难以安全 review

### 可以 Comment

以下情况通常可以 Comment，不一定阻塞：

- 命名可以更清楚
- 文档表述可以更精炼
- 非关键实现可以后续优化
- 有替代方案但当前方案也能接受

Comment 应尽量说明原因和建议，不只写“这里不太好”。
