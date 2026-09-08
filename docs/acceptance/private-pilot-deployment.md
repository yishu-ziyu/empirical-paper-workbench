# 验收契约：首个受保护试用环境

Status: open

## Change
从 main 的独立分支交付可复现部署包，使现有工作台在隔离环境通过真实登录完成 Card → Results → 证据回跳，并在续期、服务重建和一致性备份恢复后保留研究。

## Not this
构建成功、import/HTTP 200、runner 返回 True、mock 正文、API 脚本替代浏览器、重试到绿均不算研究旅程成功。不改阶段 C 设计、不合并、不购服务、不改日常环境、不开放公网、不将密钥写入 Git/镜像/日志/截图。issue #34 根因保持待查。

## Evaluator
implementer 在独立工作树实现并留下去敏证据；validator 仅据本契约独立复核客观检查。用户与外部验收保留最终批准权；未授权目标主机时远端部署保持待授权，其他可执行验证继续。

## Checks
- [ ] C1 固定 StatsPAI 修订和 Card 数据来源、许可决定、列/行/checksum；干净 checkout 构建同一 backend/runner 镜像，记录源码完整 SHA、镜像摘要、构建上下文秘密排除证据。程序：部署运行说明中的 clean-build/check-data 命令；预期不依赖 sibling/editable/开发挂载。
- [ ] C2 实际 Nginx 与干净浏览器先复现 cookie 路径问题后验证修复；DEBUG=false、真实登录、短 token 到期自动续期后操作继续、退出拒绝访问。保留 Secure/httpOnly；设置删除路径一致。程序：隔离 HTTPS 浏览器验收及代理配置导出。
- [ ] C3 上传 >1 MiB 合成文件成功，超限明确拒绝；SSE 渐进到达，长生成请求完成；数据库及 bucket/专用权限初始化先于 backend/runner 就绪；缺配置明确失败。程序：隔离 Compose + 浏览器/定向检查。
- [ ] C4 真实生成和评审 provider 配置存在且可达；干净浏览器完成新 Card、预期/方案确认、真实比较、来源、人工批准/主分析门禁、非空 Results、证据回跳、中英文切换/刷新及支持的导出打开。记录 status/error/attempt、终态事件、result、completed specification runs、实际生成评审模式与请求/token 用量。程序：完整浏览器旅程与对应去敏运行证据。
- [ ] C5 未登录与另一账户不能读写他人的 session/run/events/upload/export；正常续期可用。程序：双账号隔离验证，真实失败响应和续期证据。
- [ ] C6 完成研究后保留独立卷重建服务，同浏览器恢复账号/正文/来源/主分析；停写窗口一致性数据库与文件备份并在独立恢复卷验证。记录前镜像、停止/恢复/回滚及兼容约束。程序：运行说明中已实跑的 rebuild/backup/restore 命令。
- [ ] C7 独立部署 PR、最新源码 SHA/镜像标识、focused checks 与 CI、去敏证据和 git status 齐全。远端目标未授权时明确未部署并集中列真实缺项；不得声称本地等于受保护远端验收。程序：git/gh 与独立 validator。

## Evidence
尚待执行。任务原文：/Users/mahaoxuan/Downloads/econpaper_private_pilot_deployment_task_2026-09-08.md。

## Named relaxations
无。远端主机/安全入口/访问范围授权为待满足前提，不豁免本地隔离验证；无法执行的检查保持未勾选并记录原因。
