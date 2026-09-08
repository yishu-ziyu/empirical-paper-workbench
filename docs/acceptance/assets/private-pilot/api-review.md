# 隔离 API 实测（不替代浏览器）

通过 `https://localhost:18443` 的真实两层代理、证书校验、入口 Basic 和应用账号 Cookie 执行。未注入 Bearer、修改 Cookie Path 或调用 `process_one_run`。只用公开 Card 与合成 CSV；全部原始输出保留。

## 结果

- `api-valid-uuid-run.json`：注册 201、真实登录 200、生产响应 token 为空；两个账号均拿到 Secure/httpOnly Cookie。
- 双账号/匿名 session、run、events、export、artifacts 读取，以及 freeze/delete/上传 capability resolve 均拒绝。原账号仍读取同一会话 200。
- 1,200,006 字节、200,000 行合成 CSV 上传 202。超过产品/入口限制上传 413；另一次不发送正文的 Content-Length 探针同样 413。匿名小文件上传 401。
- Card upload 与 spec run 均真实 runner 终态 `SUCCEEDED`、attempt=1、error=null、result存在；终态 SSE 为 `run.succeeded`。12/12 specification runs `ok`。两条 SSE 流分阶段到达，API 接收时间约 0.05→0.55→2.07 秒及 0.01→1.02→2.54→3.59→4.06 秒；这不是浏览器 SSE 验收。
- 当次 OLS region：coef 0.07469325559311328，SE 0.003498345658478739，n=3010，HC1；IV region：coef 0.13150383624724782，SE 0.05496367260152569，n=3010，nonrobust。数值来自该次 API，完整公式/生产 run ID 在原件。OLS 与 IV 的协方差口径不同。
- `api-cookie-corrected-probe.json`：真实 `ep_access_refresh` Cookie Path=`/auth`，Secure/httpOnly 保留；访问 `/api/auth/refresh` 不携带该 Cookie，返回 401。**正常续期未通过**。logout 200 后 `/api/auth/me` 401 仅证明正常客户端退出，不证明复制出的 access token 立即失效。
- 独立 `api-evaluation.json` 对 51 个检查作判定：50 pass、1 known_reproduced_failure（续期）。整体不通过，浏览器与 Results 不由本脚本验收。

## 首次失败与采集器修正

1. `api-first-run.json`：真实注册 500；实现者修复 Postgres naive timestamp 默认值后再执行。没有重放失败 POST。
2. `api-after-registration-fix.json`：真实入口 API 502；实现者修复服务重建后的代理地址问题后继续。
3. `api-ssot-run.json`：Card/上传 422 是测试采集器传入 hex40 Idempotency-Key，接口要求 UUIDv4。拒绝发生在任务入队前；修正输入后的新任务保存在 `api-valid-uuid-run.json`。这不是业务间歇失败，不能用于给 #34 归因。
4. 原件将 `owner session after forbidden deletes` 的合法 HTTP 200 判 fail，是标签包含 forbidden 触发了采集器的非拥有者拒绝规则。独立 evaluation 纠正，未重跑业务、未覆盖原件。
5. 原件 `jar_refresh_paths` 查询错写 `ep_refresh`，但登录时完整 Cookie 属性已正确记录 `ep_access_refresh` + `/auth`。另一次仅正常登录/refresh 的独立探针使用正确名，仍得到不发送 Cookie 与 401；原件不改。

## 可复现命令与边界

```sh
python3 scripts/private_pilot_api_check.py \
  --env-file /absolute/private/project-ssot-provider.env \
  --output docs/acceptance/assets/private-pilot/api-new-observation.json
```

命令读取外部安全 env 指定的证书/htpasswd，并从同目录 gateway-password 读取入口密码。生成账号仅落同目录 0600 文件，证据不含凭证或响应正文。输出存在时拒绝覆盖；每次执行创建新测试资源，不用于重试直到绿。脚本退出 1，明确表示契约未闭环。

脚本未等待 access token 自然过期；已直接证明真实续期 endpoint 的路径失败。未验证用户浏览器、正文生成、证据回跳、语言切换、备份恢复；这些由独立工作线留证。Card 及合成上传资源已保留供恢复核验，未删研究数据。
