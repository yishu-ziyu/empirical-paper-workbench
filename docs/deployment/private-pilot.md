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
