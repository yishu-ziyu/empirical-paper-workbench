# P2-AB Topic-first Auto Research CLI BDD

## 目标

把本地高效工作流主入口固定为 `auto-research`：用户给出一个研究题目，系统创建一次可审计 run，尽可能调用当前机器可用的能力，并把不可用能力写成显式降级证据。

## 行为 1：题目优先创建 Auto Research Run

Given 用户在当前项目根目录运行 `python3 Product/cli.py auto-research --topic "人工智能是否影响劳动收入差距"`

When CLI 执行成功

Then 系统必须创建新的 `workspace/runs/{run_id}` 或 `06_workspace/runs/{run_id}`，写入 `00_intake/research_intent.json` 和 `run_manifest.json`。

业务规则：本地工作流必须从研究题目开始，而不是要求用户先理解 UI 或后端目录结构。

## 行为 2：默认 best-available，而不是 fallback-first

Given 用户没有显式传入 `--mode dry-run`

When CLI 运行 `auto-research`

Then `run_manifest.json` 必须声明 `mode=auto`、`execution_policy=best_available`，并记录 LLM、StatsPAI、CNKI、Web、agentmemory、本地数据等能力的 `capability_status`。

业务规则：系统默认追求当前机器能达到的最高质量；不可用能力只局部降级，不能把整次 run 降成空壳。

## 行为 3：不可用能力必须留下证据

Given 某个能力不可用、未登录、验证码阻塞、provider 报错或实现尚未接入

When Auto Research Run 继续执行可用部分

Then 对应能力必须写入 `status`、`reason`、`evidence_level`、`can_promote=false`，不能静默失败，也不能伪装成成功。

业务规则：研究系统可以降级，但每个降级都必须可审计。

## 行为 4：递归研究搜索第一版写入候选层

Given 用户给出题目

When 系统生成第一轮递归研究搜索计划

Then 必须写入 `01_sources/recursive_search_plan.json`、全局 `state/orchestration/literature_clues.jsonl` 和 run 快照 `01_sources/literature_inventory.json`。

业务规则：CNKI/Web/Zotero/本地文献只能先产生 `LiteratureClue` 候选，不能直接成为正式引用。

## 行为 5：自动产物默认不能晋升正式层

Given Auto Research Run 生成变量候选、方法候选、证据缺口、研究报告和探索性论文草稿

When 产物写入 run 文件夹

Then 它们必须默认标记为 `exploratory`、`draft`、`needs_human_review`，且 `can_promote=false`，不能改写 `state/product/variable_roles.json`、`design_spec.json` 或 `run_plan.json`。

业务规则：Auto Mode 可以生成草案层，但不能静默覆盖正式层。

## 待确认边界

- 第一版可以先写 capability detection 和 run artifacts，再逐步接入真实 CNKI 浏览器执行、StatsPAI 方法执行和 LLM Supervisor 调用。
- agentmemory 是可选增强层；不可用时不能阻断 CLI。
- CNKI 第一版默认手工辅助检索；遇到验证码或未登录时写入 `blocked_by_captcha` / `blocked_by_login`。
