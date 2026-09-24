# econpaper Codex Run Record

- Date: 2026-09-24
- Task ID / state file: METHOD-ADAPTER-1 / runtime/tasks/20260924-method-adapter.md
- Commit / Git context: main @ a0e61089
- Model and tool environment: Claude Code；agent/.venv、backend/.venv（Python 3.12，statspai 本地源码依赖）
- Dataset class / research method（不含原始数据）: ck1994、Card、固定种子生成数据；OLS / IV / DiD / RD / SCM
- Task: 梳理实证链路；第 1 步统一读结果与读设计字段，不改变行为
- Result: pass（第 1 步）；暂停
- Session / run ID: 测试内临时状态
- Verification commands: `make test`；`make docs-check`；`python3 scripts/check_docs.py --changed origin/main`
- Output evidence locations: agent/tests/test_results_reader.py；agent/tests/test_design_fields.py；docs/design/empirical-pipeline.md

## 成功动作

- 用户担心“专门修一种方法会变成硬编码”，先停下修补，做全链路梳理，再按结构问题分步改。
- 重构前写刻画测试：把旧实现原样复制为参照，在真实结果对象上逐值比对，证明切换不改变数值。
- 为“统一优先顺序不改变行为”的前提单独写守护测试，而不是只在文档里声明。

## 失败动作与根因

- 实测时直接把 align_direction 的输出交给 identification_verify，跳过了中间的 set_direction，得出“正式流程识别诊断没有运行”的错误结论，并据此请用户做了决定。根因：探针没有按真实节点顺序执行。发现 enrich_direction 后按真实顺序重测，撤回结论并如实告知用户。

## 可复现条件

- 验证“某阶段读不到字段”一类结论，必须按 PRWRITE_SEQUENCE 的真实顺序串起上游节点。

## 候选模式

- 探针要复现真实调用链，不能拿中间产物直接喂下游节点；得出“产品某功能从未生效”这类强结论前，先找有没有桥接逻辑。
- 结构性重构的第一步用“刻画测试 + 前提守护测试”，比逐个方法修 bug 更能防止回归。
