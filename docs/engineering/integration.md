# 前后端联调指南

## 1. 目标

本文档用于说明后端在本地如何支持前端联调，包括服务启动、接口契约、OpenAPI 同步、响应格式和接口变更检查。

当前默认联调地址：

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000
OpenAPI:  http://localhost:8000/openapi.json
Docs:     http://localhost:8000/docs
```

## 2. 前置条件

后端本地需要：

- Python 3.11
- uv
- Docker Desktop
- PostgreSQL 和 Redis，可由 Docker Compose 启动

前端本地需要：

- Node.js 20+
- pnpm
- 前端依赖已安装

## 3. 启动后端服务

推荐使用 Docker Compose 启动完整后端依赖：

```bash
cd /Users/lihai/code/project/backend
[ -f .env ] || cp .env.example .env
make docker-up
```

该命令会启动：

- FastAPI：`http://localhost:8000`
- PostgreSQL：`localhost:5432`
- Redis：`localhost:6379`

检查服务健康状态：

```bash
make docker-health
```

期望返回：

```json
{
  "code": "OK",
  "message": "ok",
  "data": {
    "status": "healthy"
  }
}
```

如需使用本地 uvicorn 方式启动：

```bash
cd /Users/lihai/code/project/backend
make install
[ -f .env ] || cp .env.example .env
docker compose up -d postgres redis
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

## 4. 启动前端服务

```bash
cd /Users/lihai/code/project/frontend
pnpm install
pnpm dev
```

默认访问：

```text
http://localhost:5173/
```

前端默认读取：

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_OPENAPI_URL=http://localhost:8000/openapi.json
```

`VITE_API_BASE_URL` 只配置服务根地址，不包含 `/api/v1`。

## 5. API 契约

所有对前端提供的业务 API 统一挂载在：

```text
/api/v1
```

当前健康检查接口：

```text
GET /api/v1/health
```

所有对前端可用的接口必须出现在：

```text
http://localhost:8000/openapi.json
```

同时应能在 Swagger 文档中查看：

```text
http://localhost:8000/docs
```

## 6. 响应格式

成功响应统一返回：

```json
{
  "code": "OK",
  "message": "ok",
  "data": {}
}
```

错误响应统一返回：

```json
{
  "code": "ERROR_CODE",
  "message": "Error message",
  "data": null
}
```

错误响应必须保留正确 HTTP 状态码，不允许所有错误都返回 200。

422 参数校验错误统一使用：

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Invalid request payload",
  "data": {
    "details": []
  }
}
```

前端 API Client 会统一解包 `data`，也会统一转换错误对象。后端接口不要返回裸对象、裸数组或非标准错误结构。

## 7. OpenAPI 同步给前端

后端新增或修改接口后，需要先确认 OpenAPI 已更新：

```bash
curl http://localhost:8000/openapi.json
```

再到前端仓库生成类型：

```bash
cd /Users/lihai/code/project/frontend
pnpm api:types
```

生成文件：

```text
src/api/generated/schema.ts
```

前端会基于该文件更新或新增 `src/api/modules/*`。

## 8. 浏览器跨域说明

前端开发服务器和后端服务端口不同：

```text
http://localhost:5173 -> http://localhost:8000
```

浏览器实际联调需要满足以下任一条件：

1. 后端允许 `http://localhost:5173` 跨域访问
2. 前端 Vite dev server 配置代理，由同源地址转发到后端

接口契约可先通过命令行验证：

```bash
make docker-health
curl -fsS http://localhost:8000/openapi.json
```

如果 curl 正常但浏览器失败，优先检查浏览器控制台是否存在 CORS 报错。

## 9. 接口变更检查清单

后端新增或修改接口时，按以下顺序检查：

1. 路径遵循 `/api/v1` 前缀
2. 请求体和响应体声明 Pydantic Schema
3. 响应使用统一 `code` / `message` / `data` 结构
4. 错误响应保留正确 HTTP 状态码
5. 422 校验错误结构符合前端读取方式
6. 接口出现在 `/openapi.json`
7. 新增或更新 pytest 接口测试
8. 执行 `make check`
9. 涉及 Docker 时执行 `make docker-local-check`
10. 通知前端执行 `pnpm api:types`

## 10. 常见问题

### 前端请求 404

确认接口路径是否包含 `/api/v1` 前缀。前端 `VITE_API_BASE_URL` 不包含 `/api/v1`，资源路径由前端 API module 声明。

### 前端类型未更新

确认后端服务已启动，且 `http://localhost:8000/openapi.json` 可访问。随后在前端仓库执行：

```bash
pnpm api:types
```

### 浏览器联调失败但后端日志无请求

优先检查浏览器控制台是否为 CORS 或网络层错误。浏览器跨域失败时，请求可能不会进入业务路由。

### 接口在 Swagger 可见但前端生成类型缺失

确认前端读取的 `VITE_OPENAPI_URL` 是否指向当前后端服务：

```env
VITE_OPENAPI_URL=http://localhost:8000/openapi.json
```

### 前端收到 `HTTP_ERROR`

通常表示后端返回结构不符合统一响应格式。请检查接口是否返回了裸对象、HTML 错误页或 FastAPI 默认异常结构。
