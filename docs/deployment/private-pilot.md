# 受保护个人试用部署

状态：部署包实现中，尚未部署。验收以 [契约](../acceptance/private-pilot-deployment.md) 为准。

沿用根目录 Compose；使用独立 `econpaper-private-pilot` 项目、loopback 端口和新卷。
严禁 `down -v`、覆盖现有部署、挂载开发源码补依赖或上传凭据。
本地验证需 Docker 可用、专用本地安全配置、TLS 入口和真实生成/评审服务；远端另需目标主机、入口与访问范围明确授权。

后续在本文件记录已执行构建/验证/停止/备份/恢复命令与结果，未运行项目不会标记通过。

## 环境和入口

`deploy/private-pilot/environment.example` 仅为字段模板。实际配置必须放在 checkout 外、权限 0600；TLS 私钥和 `htpasswd` 放在专用目录 0700，不进入构建上下文。入口对整个页面及 `/api` 使用 Basic 访问限制，应用再用真实账号登录。正常 access 有效期 15 分钟；短期验证可单独设 1 分钟并记录，验后恢复 15。入口只绑定 loopback；获得目标主机授权前不改成公网监听。远端应接已有授权 TLS/访问限制入口。

产品文件上限固定 50 MiB，代理接受 51 MiB 含 multipart 包装，超限返回 JSON 413。普通 API 读取预算 900 秒，SSE 1 小时、两层关闭缓冲；这些是代理预算，不证明模型执行成功，也不自动重放写请求。单 runner、并发 1；本轮最多一项 Card 研究和一次正文生成/评审。供应商预算/费用未知时只报告可验证请求和 token，不承诺金额。

## 运维命令

以下脚本维护方执行，执行结果在验收证据中单独标记。`PILOT_ENV_FILE` 指向安全配置；`PILOT_PROJECT` 默认为 `econpaper-private-pilot`，恢复必须另用 `econpaper-private-pilot-restore-*`。

```sh
PILOT_ENV_FILE=/private/pilot.env deploy/private-pilot/ops.sh check
PILOT_ENV_FILE=/private/pilot.env deploy/private-pilot/ops.sh build
PILOT_ENV_FILE=/private/pilot.env deploy/private-pilot/ops.sh up
PILOT_ENV_FILE=/private/pilot.env deploy/private-pilot/ops.sh check-data
PILOT_ENV_FILE=/private/pilot.env deploy/private-pilot/ops.sh rebuild
PILOT_ENV_FILE=/private/pilot.env PILOT_BACKUP_DIR=/private/new-backup deploy/private-pilot/ops.sh backup
PILOT_ENV_FILE=/private/restore.env PILOT_PROJECT=econpaper-private-pilot-restore-01 PILOT_BACKUP_DIR=/private/new-backup deploy/private-pilot/ops.sh restore
PILOT_ENV_FILE=/private/pilot.env deploy/private-pilot/ops.sh stop
```

构建前要求 Git clean；将 `ECONPAPER_IMAGE` 设为 `econpaper-backend:<完整源码SHA>`，backend/runner 引用同一镜像。build 后用 `docker image inspect --format '{{.Id}}' <tag>` 记录镜像内容标识；`RepoDigests` 为空表示未推镜像仓库，不虚构 registry digest。部署不挂载开发源码，只挂载固定 init/网关配置和 checkout 外入口秘密。

`backup` 先停止网关、应用写者和 MinIO，用 `pg_dump -Fc` 导出数据库，再备份静止共享文件和对象；失败保持停止，维护者排查后再 `up`。恢复脚本拒绝存在容器或旧卷的目标 project，恢复后另用不冲突端口启动，浏览器核验关系和文件，不能仅凭 tar 命令成功认可恢复。

回滚：保存本次与前次源码SHA/镜像ID；先停止写入并备份，确认数据库/会话格式向后兼容后，将安全配置 `ECONPAPER_IMAGE` 指回前一镜像，执行 `up`，不重建或删除卷。未知兼容性时不回滚数据库、不覆盖现有研究。首个 pilot 尚无前一已验收版本。

`.tex` 导出需实际下载并打开验证；镜像未提供 latexmk/pandoc，不承诺 PDF/Word。

兼容边界：新增 `refresh_revocations` 表保存 refresh 单次消费；部署前旧进程内存撤销无法迁移。首次干净试用无旧账号迁移；已有部署升级需轮换 JWT 密钥或等待旧 refresh 自然过期，不能承诺旧撤销记录恢复。退出后已复制的短期 access 仍到期前有效，此处未引入 access 黑名单。

验证工具：本机 Docker Compose 5.0.2 接受 `ports: !reset []`，pilot overlay 移除 backend/frontend 发布端口，只发布 TLS gateway。MinIO 固定镜像不含 tar；备份维护容器复用应用镜像、无网络，仅临时访问独立对象卷。

## 本轮实证与未完成项

- Docker 29.2.0 / Compose 5.0.2；`git archive` 导出源树后构建，未包含开发环境。构建首次因缺 gcc、第二次因 Debian HTTP 502 失败，分别修复为独立编译阶段及 HTTPS，原失败保留。
- 容器无网络执行公开 Card 依赖烟测成功：3,010 行、34 数据列，固定 checksum。其 OLS 显式 HC1 SE 与历史设计材料不同；这是直接 StatsPAI 封装烟测，不是历史工作台结果复刻，不能归因平台浮点。当前应用 run 数字另存 API 证据。
- 初始 `.env.docker` 的生成/评审配置各一次 401；项目原生 SSOT 的两 role 各一次 200，各 173 tokens。未输出凭据，未回退 mock；费用金额未知。详见 `provider-first-attempt.json` 与 `provider-project-ssot.json`。
- 正常真实 PostgreSQL 注册暴露 naive/aware datetime 错配；保留 schema、明确 naive UTC 默认后验证。前端 IPv6 localhost 健康探针和重建后代理旧地址问题均保留首证据，分别修为真实 IPv4 探针和联合重建代理。
- 浏览器先复现 Cookie 路径问题的授权尚未恢复，所以 `/auth` → `/api/auth` 修复未实施。正常续期、完整浏览器旅程、真人理解与远端发布未完成。API 请求与容器检查不能替代。

相关去敏工件位于 `docs/acceptance/assets/private-pilot/`；当前契约保持 open。请阅读每份工件的失败/未运行状态，不以运行镜像或健康状态视为试用验收通过。
