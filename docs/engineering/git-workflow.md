# Git 工作流规范

## 1. 默认分支

默认分支为 `main`。

`main` 是唯一长期主分支，必须始终保持可运行状态。

所有开发从 `main` 拉取新分支，所有变更通过 PR 合并回 `main`。

本仓库暂不使用长期 `develop` 分支、`staging` 分支或复杂 Git Flow。

## 2. 分支类型

允许使用以下分支类型：

- `feature/*`
- `fix/*`
- `docs/*`
- `chore/*`
- `ci/*`
- `refactor/*`
- `test/*`

示例：

```text
feature/user-auth
fix/db-session-leak
docs/git-workflow
chore/initial-backend-baseline
ci/add-pytest-workflow
refactor/settings-module
test/healthcheck-api
```

## 3. 分支命名规则

分支命名格式：

```text
<type>/<short-description>
```

规则：

1. 使用小写英文
2. 单词使用短横线连接
3. 不使用中文
4. 不使用个人名作为主要分支名
5. 不长期保留个人开发分支

## 4. 分支生命周期

分支应保持短生命周期。

建议：

1. 普通功能分支 1 到 3 天内合并
2. 小修复分支当天合并
3. 超过 3 天的分支需要同步 `main`
4. 大功能应拆成多个小 PR

## 5. Commit Message

提交信息采用 Conventional Commits 格式：

```text
<type>: <description>
```

常用 type：

- `feat`: 新功能
- `fix`: 修复问题
- `docs`: 文档
- `chore`: 工程杂项
- `refactor`: 重构
- `test`: 测试
- `ci`: CI 配置
- `build`: 构建相关
- `style`: 格式调整

示例：

```text
feat: add user register API
fix: close database session after request
docs: add backend tech stack document
chore: initial backend baseline
test: add health check API test
ci: add backend pytest workflow
```

禁止使用含义不清的提交信息：

```text
update
fix bug
wip
临时提交
改一下
```

## 6. PR 规则

所有进入 `main` 的变更必须通过 PR。

最低要求：

1. PR 标题遵守 Conventional Commits 风格
2. PR 必须说明变更内容
3. PR 必须说明验证方式
4. 至少 1 人 Review
5. 后端代码优先由另一名后端 Review
6. 合并后删除临时开发分支

## 7. PR 大小

一个 PR 应只解决一个问题。

如果一个 PR 超过 300 到 500 行有效代码变更，需要说明为什么不能拆分。

禁止在一个 PR 中混合大量无关变更，例如：

- 新功能
- 重构
- 格式化
- 数据库迁移
- 配置调整
- 依赖升级

## 8. 数据库变更规则

本项目使用 SQLAlchemy 2.0 和 Alembic。

规则：

1. 修改数据库结构必须提交 Alembic migration
2. migration 文件必须进入 Git
3. 不允许只改 SQLAlchemy model 不生成 migration
4. 不允许手动修改数据库后不补 migration
5. migration 命名必须能表达业务意图

## 9. 配置变更规则

本项目使用 `pydantic-settings` 读取配置。

规则：

1. 新增配置项必须更新 `.env.example`
2. 禁止提交 `.env`
3. 禁止提交密码、token、密钥、数据库连接串等敏感信息
4. 配置项必须有明确默认值或启动校验

## 10. API 变更规则

本项目使用 FastAPI 内置 OpenAPI。

规则：

1. 新增 API 必须能体现在 `/openapi.json`
2. 修改 API 入参、出参、状态码时，必须在 PR 中说明
3. 删除或不兼容修改 API 时，必须说明影响范围
4. 面向前端或外部系统的接口变更必须提前同步

## 11. 依赖变更规则

本项目使用 `uv` 管理依赖。

规则：

1. 新增依赖必须说明原因
2. `uv.lock` 必须提交
3. 不允许绕过 `uv` 手动安装依赖后不更新项目依赖
4. 依赖升级必须说明影响范围

## 12. 主分支保护

远程仓库创建后，应配置 `main` 分支保护：

1. 禁止直接 push 到 `main`
2. 禁止 force push
3. 禁止删除 `main`
4. 合并必须通过 PR
5. 至少 1 个 approval

基础 CI 完成后，再要求 PR 必须通过自动检查后才能合并。
