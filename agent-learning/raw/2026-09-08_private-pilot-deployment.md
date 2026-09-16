# econpaper Codex Run Record

- Date: 2026-09-08
- Task ID: 20260908-private-pilot / runtime/tasks/20260908-private-pilot.md
- Git context: deploy/private-pilot / Draft PR #36; runtime source 5d6fd9889edaf006c09eda16b1983fb29ddcf4bb
- Environment: Docker 29.2.0, Compose 5.0.2, isolated loopback TLS + PostgreSQL/MinIO; no daily-service modification.
- Dataset: public Card 3010-row extract and synthetic upload only.
- Result: partial; acceptance contract open.
- Session / run: b0c198b9-68d2-4ced-9e6b-8d87c74578d0 / c96fd037-efc9-4ac6-a249-95769cbce028
- Commands: clean git archive builds; container check_card_package; private_pilot_api_check; one Results call; focused auth; ops rebuild/backup/restore; normal-login snapshots.
- Evidence: docs/acceptance/assets/private-pilot/

## 成功动作
固定统计来源与数据进入镜像；Postgres真实注册/账号隔离/上传/SSE/12项Card估计；项目原生SSOT两role真实可达；备份恢复实际文件、对象和正文精确核对。

## 失败与边界
首次缺编译器、Debian HTTP502、IPv6健康探针、UTC时间绑定、Nginx缓存旧上游均按原失败场景修复。Docker环境旧provider401保留。首次真实正文review缺pydantic-ai降级，依赖修复后只读typed诊断成功，原章降级状态保留。正常refresh路径失配未修：用户要求浏览器先复现，而浏览器授权硬停。完整浏览器/真人/远端验收未完成。

## 恢复条件
两个pilot project已stop，无卷删除；安全配置和备份在checkout外。继续需先恢复浏览器授权，再处理cookie路径与真实用户旅程；远端目标另需授权。不把API证据当浏览器效果，不把依赖烟测当统计语义全验收。
