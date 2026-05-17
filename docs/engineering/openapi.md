# OpenAPI / API 契约规范

## 1. API 版本前缀

所有对外业务 API 统一使用 `/api/v1` 前缀。

当前健康检查接口也挂载在：

```text
GET /api/v1/health
```

暂不引入 `/api/v2`，也不把环境名写入路径，例如 `/dev/api` 或 `/staging/api`。

## 2. 资源接口

标准资源操作优先使用 HTTP Method 表达：

```text
GET    /api/v1/users
POST   /api/v1/users
GET    /api/v1/users/{user_id}
PATCH  /api/v1/users/{user_id}
DELETE /api/v1/users/{user_id}
```

请求体和响应体必须尽量显式声明 Pydantic Schema。长期接口契约不直接返回 ORM Model，也不直接返回裸 `dict`。

## 3. 动作接口

对于无法由标准 CRUD 清晰表达的业务动作，允许定义动作接口：

```text
POST /api/v1/{resources}/{resource_id}/actions/{action-name}
POST /api/v1/{resources}/actions/{action-name}
```

示例：

```text
POST /api/v1/users/{user_id}/actions/activate
POST /api/v1/orders/{order_id}/actions/cancel
POST /api/v1/invitations/actions/accept
```

动作接口规则：

1. 必须使用 `POST`
2. 动作名使用 kebab-case
3. 动作必须表达明确业务语义
4. 标准 CRUD 足以表达时，不定义动作接口
5. 不使用 `/do`、`/handle`、`/process` 等含义模糊路径
6. 请求体和响应体仍必须声明 Schema，并使用统一响应包裹
7. 动作接口必须出现在 OpenAPI 文档中

## 4. 统一响应格式

所有业务接口统一返回：

```json
{
  "code": "OK",
  "message": "ok",
  "data": {
    "id": "123"
  }
}
```

字段含义：

- `code`：业务码，例如 `OK`、`NOT_FOUND`
- `message`：面向客户端的简短说明
- `data`：资源对象、分页对象、布尔结果或 `null`

错误响应使用相同外层结构，同时保留正确 HTTP 状态码：

```json
{
  "code": "NOT_FOUND",
  "message": "Resource not found",
  "data": null
}
```

禁止把所有错误都返回 HTTP 200。`message` 不得直接暴露 Python exception、数据库错误细节、堆栈或敏感信息。

## 5. 错误码

基础错误码与建议 HTTP 状态码：

| code | HTTP 状态码 |
| --- | --- |
| `OK` | 200 |
| `BAD_REQUEST` | 400 |
| `UNAUTHORIZED` | 401 |
| `FORBIDDEN` | 403 |
| `NOT_FOUND` | 404 |
| `CONFLICT` | 409 |
| `VALIDATION_ERROR` | 422 |
| `INTERNAL_SERVER_ERROR` | 500 |

当前阶段 FastAPI 默认 422 校验错误可以暂时保留。后续需要统一错误处理时，应将其转换为标准响应结构。

## 6. 分页

列表接口统一使用：

```text
page
page_size
```

规则：

- `page` 从 1 开始
- `page_size` 默认 20
- `page_size` 最大 100

分页响应必须放在统一响应的 `data` 内：

```json
{
  "code": "OK",
  "message": "ok",
  "data": {
    "items": [],
    "page": 1,
    "page_size": 20,
    "total": 0
  }
}
```

当前阶段不引入 cursor pagination。除非经过单独说明，否则列表接口不得混用 `limit/offset`。

## 7. Schema 命名

推荐命名：

```text
{Resource}Create
{Resource}Update
{Resource}Read
{Resource}ListItem
{Resource}ActionRequest
{Resource}ActionResult
```

示例：

```text
UserCreate
UserUpdate
UserRead
UserListItem
UserActivateResult
OrderCancelRequest
OrderCancelResult
```

规则：

1. 请求体和响应体分开定义
2. Create、Update、Read 不混用同一个 Schema
3. 不直接返回 ORM Model
4. 字段名统一使用 `snake_case`
5. 时间字段统一使用 ISO 8601
6. ID 命名保持一致，例如 `id` 或 `{resource}_id`，不要在同一业务域内混用多种风格

## 8. 认证预留

当前不强制实现认证。

后续需要认证的接口统一预留：

```text
Authorization: Bearer <token>
```

OpenAPI 中后续应使用 HTTP Bearer Auth。当前阶段不引入 session、Redis、OAuth 服务或额外权限系统。

## 9. OpenAPI 输出

FastAPI 默认暴露：

- `/docs`
- `/openapi.json`

所有对前端或外部系统提供的 HTTP API 都必须体现在 `/openapi.json` 中。

当前阶段暂不强制提交导出的 `docs/openapi/openapi.json`，后续在基础 CI 阶段再处理自动校验或导出策略。

## 10. API 变更规则

PR 中必须说明以下变更：

1. 新增 API
2. 修改请求或响应 Schema
3. 修改错误码或 HTTP 状态码
4. 删除 API
5. 不兼容变更及其影响范围

面向前端或外部系统的接口变更必须提前同步。
