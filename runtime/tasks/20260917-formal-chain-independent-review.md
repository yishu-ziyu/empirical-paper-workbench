# 正式确认链独立评审与新流程规格

- Task ID: FORMAL-CHAIN-REVIEW-2
- Status: complete（独立评审与下一批规格完成；产品实现需要修复，未验收通过）
- Git context: `feat/progressive-research-flow@2d83c2c9c716` + 继承修复 + FORMAL-CONFIRMATION-CHAIN-1 未提交实现
- Goal: 独立核对首批实现、证据与反例；落实用户新确认的“研究意图 → 数据可行性 → 可执行设计确认 → 分析”顺序，提供后续执行规范。
- Hard bar: 本轮不改产品代码，不提交、推送或启动其他模型；测试隔离且禁止外部网络；不把新产品取舍追溯算作旧实现缺陷。
- Verified facts: 交付清单 17 个源码/测试文件哈希与当前一致；全量清单排除环境文件后 1007 个文件核对，仅实施任务与索引晚于指纹。基线副本包含 `.env` 与 `.env.docker`，未读取内容，需记录脱敏边界问题。
- Result: REJECT。直接 API 可绕过缺失设计与预览门；设计/数据改变后旧确认仍可生效；迟到确认污染另一会话；编辑后确认旧草稿；#40 confirm 许可未消费；新文案将未知说成通过。模型 mock 被 desk 覆盖为既存缺陷，已用无效占位凭据仅构造配置复现。
- Changed files: `docs/reviews/20260917-formal-confirmation-chain-independent-review.md`、`docs/specs/research-intent-to-design.md`、核心契约与旧规范的顺序替代说明、本任务/执行任务/索引及去敏运行记录。17 个受评源码/测试文件最终 hash 未改变。
- Test evidence: 既有后端 42 passed、前端 38 passed；独立前端 5 个反例全部失败；API/配置 7 个 expected/actual 反例已记录。原截图 06/09/11 已读取。未重跑完整三进程用户链路、全量测试或真人 VoiceOver。
- Failed paths: stdin pytest 在 macOS spawn 下两项失败，改文件入口后 42 通过；临时浏览器故障 harness 的 React 导入失败，改为 Vitest 准确复现，未当产品缺陷。临时 :5193 Vite 已停止；临时树内测试移除并在证据目录归档。
- Data / output evidence locations: `../empirical-paper-workbench-evidence/formal-confirmation-chain-1/review/`
- Next action: 执行者按评审启动 FORMAL-CONFIRMATION-CHAIN-2，先修 mock 隔离与确认完整性；重审通过后实施 INTENT-TO-DESIGN-1。外部模型/依赖/提交/发布仍需另行授权，基线敏感副本不得传播。
- Updated at: 2026-09-17
