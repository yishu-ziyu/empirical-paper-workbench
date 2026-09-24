# econpaper Codex Task State

- Task ID: REPLICATION-SCRIPT-1
- Status: complete
- Git context（分支可选）: main @ 84f6f946
- Goal: 用户可下载“实际运行的代码”复现脚本，重跑得到与证据相同的数字
- Hard bar: 见 docs/acceptance/replication-script.md（1–7）
- Session / run ID: 测试内创建 Card 会话
- Current research stage: —
- Current review / approval gate: —
- Verified facts: 原型下载的 analysis.py 在本机重跑 OLS 0.0747(0.0035)/IV 0.1315(0.0550)/F 13.26/F_eff 14.14 与 card-pair 一致；spec_run 直接 read_csv 后 feols/ivreg；现有 code-export 的 py 是 translate_code 生成的翻译版
- Current hypothesis: 从 research_lab.specification_runs 生成脚本即可覆盖 Card 与研究台账路径
- Changed files: backend/services/replication.py, backend/services/spec_run.py, backend/routers/code_export.py, backend/tests/test_replication_script.py, frontend/src/components/CodeExportDialog.tsx(+test), frontend/src/lib/i18n.tsx, openapi 三件, docs（acceptance/api/specs/design）；原型移至 frontend/prototypes/
- Failed paths: —
- Data / output evidence locations: backend/tests/test_replication_script.py
- Test evidence: make test 通过（agent 1072 / backend 727 / frontend 558）；复现包实跑比对通过
- Pending external state: —
- Next action: 无；后续为 Notebook 界面与正式估计主流程的计算记录
- Updated at: 2026-09-24
