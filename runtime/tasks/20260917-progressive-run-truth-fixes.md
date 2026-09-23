# econpaper Codex Task State

- Task ID: PROGRESSIVE-RUN-TRUTH-1
- Status: complete
- Git context（分支可选）: `feat/progressive-research-flow` @ `2d83c2c9c716` + uncommitted fixes（已合入 `origin/main@d2f5533`，未 push）
- Goal: 修复渐进研究流评审中确认的运行归属、blocked/终态语义、恢复接线、事件截断、无障碍与流程闸门问题。
- Hard bar: 底栏只展示当前 run；所有文案只陈述浏览器真实收到的事件与后端已确认的终态；不得伪造完成、用户接管或精确进度。
- Session / run ID: none（本任务只改代码与测试）
- Current research stage: complete — frontend run observability / recovery + runner authority hardening
- Current review / approval gate: 用户已采纳独立评审中的全部建议；实现与自动化验证完成。
- Verified facts: `main` 已通过 merge commit `2d83c2c9c716` 整合；#40 与渐进披露同时存在；底栏状态具备 run ownership；六条 wait 路径共用真实事件接缝；spec_run 保留专属 k/total；原未跟踪文件 `frontend/public/_tmp-choice-progressive.html` 保留且未改。
- Current hypothesis: confirmed — run-scoped progress state 消除了旧 run 污染、恢复缺失和迟到事件覆盖；650ms 慢探针窗口消除了全套测试中的假失权，同时保留持续 authority failure <1s 取消。
- Changed files: frontend progress model/component/workspace/App + tests；`backend/runner.py` + authority tests；PR template/checker/CI；交互基线、WIRING、acceptance；runtime state；run record。
- Failed paths: 首次 `make test` 在 `test_ws_streams_title_chunks` 留下 `RUNNING`；独立复跑通过。第二次完整 backend 在 `test_post_direction_endpoint` 以同症状失败，定位为 200ms authority probe timeout 在 SQLite 全套负载下误设 `lease_lost`。曾尝试把 grace 放宽到 5s，因会放宽旧 <1s 安全要求而撤回；最终改为 650ms 单次 probe timeout + 500ms 连续失败门槛，并从 probe 开始时计时。
- Data / output evidence locations: `docs/acceptance/progressive-run-truth-fixes.md`; `frontend/src/lib/runSteps.ts`; `frontend/src/lib/workspace.ts`; `backend/runner.py`; 对应测试文件。
- Test evidence: `make test` PASS（Agent 1066/2 skip；Backend 636/8 skip/13 subtests；Frontend 504）；最终 `make test-backend` PASS；frontend tsc/lint/build PASS；handoff/YAML/diff checks PASS。
- Pending external state: 浏览器 320×568、键盘、VoiceOver、真实方向 run 尚未真人复验；GitHub branch protection 是否把新 job 设为 required 需仓库侧确认；服务未启动，未运行 `make verify`。
- Next action: 等待用户决定是否将未提交修复 commit/push；不自动 push。
- Updated at: 2026-09-17

不得写入凭据、用户原始数据、未公开论文正文、私人对话或隐藏推理。
