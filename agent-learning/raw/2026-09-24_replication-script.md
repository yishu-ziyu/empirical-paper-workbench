# econpaper Codex Run Record

- Date: 2026-09-24
- Task ID / state file: REPLICATION-SCRIPT-1 / runtime/tasks/20260924-replication-script.md
- Commit / Git context: main，基于 84f6f946
- Model and tool environment: Claude Code；backend/.venv（Python 3.12，statspai 本地源码依赖）；vitest
- Dataset class / research method（不含原始数据）: Card (1995) 教学案例；OLS、IV、有效 F 检验
- Task: 从研究台账的设定运行生成“实际运行的代码”复现脚本与复现包，并在导出对话框中置顶
- Result: pass
- Session / run ID: 测试内临时会话，测试结束即删除
- Verification commands: `make test`；`make docs-check`；`python3 scripts/check_docs.py --changed origin/main`
- Output evidence locations: backend/tests/test_replication_script.py；frontend/src/components/__tests__/CodeExportDialog.test.tsx；docs/acceptance/replication-script.md

## 成功动作

- 先读实际调用链（spec_run → estimate._fit / _estimate_iv → effective_f_test），再写生成器；把第一阶段参数提成 spec_run 的模块常量，生成器直接引用，避免两边漂移。
- 验收测试实际执行下载的脚本并逐条比对记录值，而不是比对字符串。

## 失败动作与根因

- 原型放在 frontend/src 下，提交前只跑了原型检查，没跑前端全量，导致已推送的 main 上 `cardCanonicalLiterals` 守卫失败。根因：把“原型不进产品包”误当成“原型不受产品源码约束”。修复：移出 src，不放宽测试。
- 原型阶段写过不存在的 StatsPAI 接口（sp.datasets.card1995 等）；以真实调用链为准后改正。

## 可复现条件

- 需要 statspai 与 Card 34 列数据可用（与 test_card_spec_run 相同的前置条件）。

## 候选模式

- 任何“披露/导出代码”的功能，验收都应执行导出物并比对数值。
- 提交前端相关改动（包括原型）前跑一次 vitest 全量。
