# FORMAL-CONFIRMATION-CHAIN-2 独立评审

- Task ID: FORMAL-CHAIN-2-REVIEW
- Status: complete（独立评审结论 REJECT，实施需修复后重审）
- Git context: `feat/progressive-research-flow@2d83c2c9c716c0708eb5303840e76f51749583d1` + 继承的 CHAIN-1/2 未提交实现
- Goal: 核验交付指纹，独立检查旧反例、版本绑定、幂等恢复与真实页面行为；不替执行者修改产品实现。
- Hard bar: 不 commit/push/merge/rebase，不委派其他 Agent，不调用真实模型或读取凭据；仅隔离测试与评审文档。旧敏感基线副本保持未读取、未删除、未传播。
- Verified facts: 交付 `final/changed-files-sha256.txt` 的 37 项全部匹配当前文件（评审写回前），HEAD 和路径一致。
- Evidence: 仓库外 `../empirical-paper-workbench-evidence/formal-confirmation-chain-2/review/`。
- Test evidence: 独立后端 84、router 22、前端 47 项通过；五个新增 API 反例均复现违约；真实三进程桌面链路通过，换数据仍显示旧结果；320×568 完成确认但首轮估计 90 秒超时，同一 run 经 4 次领取约 201 秒后成功，重新打开可恢复，根因待定位。make verify、lint（0 errors/6 existing warnings）、review-mode build 通过。未重跑全部套件或真人 VoiceOver；键盘只核实 focus 后 Enter 激活样本确认，不冒充全程 Tab 顺序验收。
- Review: `docs/reviews/20260917-formal-confirmation-chain-2-independent-review.md`，S1–S4 为 P1、S5 为 P2；原实现保持不变。
- Changed files: 本评审报告、本任务、runtime/STATE.md、实施任务追加独立结论、去敏 raw 记录。脚本/截图/日志在仓库外 review/，无产品源码修改。
- Failed paths: router 首次强制全局 mock 与 5 条非 mock 配置测试的前提冲突；改用干净临时 HOME、无全局预设并阻断外部连接后 22 项通过，原失败日志保留，不记作产品缺陷。
- Next action: 执行者在当前 checkout 修复 S1–S5，补执行器重领时序与代码溯源证据，交相对本次交付的增量和指纹；尚不进入 INTENT-TO-DESIGN-1。旧敏感副本清理仍需授权。
- Updated at: 2026-09-18
