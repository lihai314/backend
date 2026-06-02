# 认证设计

## 范围

第一版认证只支持 `username` + `password`。`username` 是唯一登录标识，不使用 email 登录注册。

本阶段只落地认证基础设施，不提供公开认证 API。以下端点留到 PR 2：

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/users/me`
- `PATCH /api/v1/users/me`
- `POST /api/v1/users/me/actions/change-password`

## 用户模型

`users` 表保存账户基础信息：

- `id`: UUID 主键
- `username`: 唯一登录名
- `password_hash`: 密码哈希
- `display_name`: 展示名
- `is_active`: 账户是否可登录
- `created_at` / `updated_at`: 审计时间

第一版不做邮箱验证、忘记密码、OAuth、MFA、角色权限系统、管理员用户管理、删除账号。

## 密码哈希

密码哈希使用 `argon2-cffi` 提供的 Argon2id。业务代码只能通过 `PasswordHashService` 生成和校验哈希，不自研哈希算法。

## Session

认证方案为 Bearer opaque session token + Redis session store。

登录成功后由 session 服务生成随机 opaque token，客户端通过：

```http
Authorization: Bearer <token>
```

传递凭证。服务端仅在 Redis 中保存 token 的 SHA-256 摘要 key，对应 value 为最小 session 数据：

- `user_id`
- `created_at`

Redis key 使用 TTL 控制 session 生命周期。logout 的含义是退出登录，即删除当前 token 对应的 Redis session，不删除账号。

## 当前用户依赖

`get_current_user` 负责：

1. 从 Bearer header 提取 opaque token。
2. 从 Redis session store 解析 `user_id`。
3. 从数据库加载 `User`。
4. 用户不存在、session 过期或用户被停用时统一返回 401。

公开认证 API 会在 PR 2 基于这些基础设施实现。
