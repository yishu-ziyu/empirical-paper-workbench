# econpaper Codex Run Record

- Date: 2026-09-24
- Task ID / state file: REPLICATION-SCRIPT-1（第二轮）/ runtime/tasks/20260924-replication-script.md
- Commit / Git context: main，基于 ca9862b5
- Model and tool environment: Claude Code；backend/.venv（Python 3.12，statspai 本地源码依赖）
- Dataset class / research method（不含原始数据）: ck1994（OLS）、Card（IV）、固定种子生成数据（RD、SCM）
- Task: 固定分派主估计纳入复现脚本；估计器在调用处记录 call
- Result: pass
- Session / run ID: 测试内临时状态
- Verification commands: `make test`；`python3 scripts/check_docs.py --changed origin/main`
- Output evidence locations: backend/tests/test_replication_script.py；docs/acceptance/replication-script.md（第二轮）

## 成功动作

- 放弃“从 formula 字符串反推参数”，改为在估计器调用处记录 {function, data, args, kwargs}，复现只做渲染。
- 复现测试坚持“实际运行 + 比对数值”，因此抓到 RD/SCM/CS 报 ok 却没有系数的真 bug；先补失败断言，再改根因。

## 失败动作与根因

- 直接在 backend 环境跑探针脚本被启动配置（JWT、模型配置）拦下；改用 pytest 内探针。

## 可复现条件

- statspai 版本的 CausalResult 带 params 属性（本机源码依赖）。

## 候选模式

- “导出/披露”类功能的测试同时是对计算链路的回归测试：实跑能暴露“状态 ok 但数字缺失”一类静默错误。
- 发现范围外的问题（DiD TWFE 聚类未传入）只记录、不顺手修，交给单独任务。
