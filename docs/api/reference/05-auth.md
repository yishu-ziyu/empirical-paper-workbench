# 认证

> 上级：[econpaper API 文档](../README.md)


认证采用 httpOnly Cookie 双 token：`POST /auth/login` 成功后下发 `ep_access`（15 分钟，全站可见）与 `ep_access_refresh`（7 天，仅 `/auth` 路径）两个 HttpOnly Cookie；`POST /auth/refresh` 轮换 refresh（一次性，旧 token 即刻作废），`POST /auth/logout` 撤销 refresh 并清 Cookie。`Authorization: Bearer` 头仅为旧客户端兼容保留。登录/注册接口带限流与账号锁定（连续 5 次失败锁 10 分钟）。

---
