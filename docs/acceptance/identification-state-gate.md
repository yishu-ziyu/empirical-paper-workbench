# 验收契约：#40 增量一 —— 统一诊断状态与执行许可

Status: accepted

验收记录：第一轮独立验收 REJECT（四条有实证的缺口）→ 逐条修复 → 第二轮独立复核
**ACCEPT**（R1–R5 全 PASS，含扫描非空证明与旧 PDF 取证）。两轮的命令与输出原文在
验收官报告里；本文件只留结论与修复摘要。

来源：`docs/specs/frontend-interaction-principles.md` §7 待参谋问题；外部参谋意见
（`/Users/mahaoxuan/Downloads/issue-40-frontend-advisory-cd45d65.md`）§2.2、§4、§9 增量一。
基线：`cd45d65d952649f84d4c6b19a52f71294d79e5b0`。

## Change

把「识别诊断」的状态从**一个综合星级**拆成三个独立、可分别消费的问题，并让**所有入口
读同一个判定函数**（`agent/engine/identification_state.py`）：

1. **执行有没有完成**：`completed` / `partial` / `failed` / `not_run`
2. **发现了什么**：`risk_found` / `risk_not_found` / `insufficient_evidence` / `not_applicable`
3. **接下来允许做什么**：显式 `permissions`，每个动作报三档
   `allow` / `confirm` / `forbid`（布尔值分不出「未知」和「禁止」，而这两者完全不同）

判定函数另出两个**明确命名、分别回答不同问题**的档位，避免入口各写一套内联判断：

- `hard_block` —— **流程**停不停。含显式 `identification_failed` 标记与 `star_rating == 0`。
  图的条件边、串行预写路径、章节写入闸门、HTTP Facade 问的都是这一个。
- `untrustworthy` —— **章节绑定**用的保守档，比 `hard_block` 严：额外把
  「跑了但有硬失败项」「diag 根部写着失败状态」算进来。

用户可观察的结果：

- 全是 `warn`（没有任何 `pass`、也没有 `fail`）**不再**被算成 0 星、**不再**触发
  `identification_failed`、**不再**让图走 `hitl_pause`。它变成「有风险、可继续、要披露」。
- 全是 `error` / `skipped`（一条都评不了）时，`identification_diag.passed` 是 `None`
  （未知），**不再**是 `True`（通过）。未知不阻断继续，也不授予因果表述与主结果晋升。
- Callaway–Sant'Anna 的**效应显著性**不再生成 `pass` / `warn`，因此不再参与设计有效性
  判定；缺 p 值不再被当成 0。
- 同一份 state 从图（`route_after_identification`）、Facade 串行路径（`run_prewrite`）、
  章节写入闸门（`readiness`）、绑定层（`bind`）、后端 Facade 五个入口读到的**许可决定一致**。

## Not this

- **不新增一套「统计诊断系统」**：现有 `identification_verify.py` 已经读 CSV 并按方法调
  Bacon / IV / effective-F / McCrary / SCM 安慰剂，本增量只改聚合、状态语义与许可输出。
- **不改 0 星的既有硬阻断语义**（全 `fail` 仍然截断）—— 参谋意见没有要求放开这一档。
- **不改依赖图**：`agent/engine/prewrite.py` 的 `PRWRITE_SEQUENCE` 拓扑保持原样。
- **不改文献检索**：那是增量三。
- **不把 `star_rating` 删掉**：它仍是前端展示与既有测试消费的字段，本增量只是不再让它
  单独决定许可。
- 不推远端。

## Evaluator

implementer 实现并自检；validator 按 C1–C6 独立复跑。C7 是端到端场景，需要真实跑一次节点。

## Checks

### C1 全 warn 不再是硬阻断

程序：构造 diagnostics 全为 `warn` 的最小输入，直接调新的判定函数与 `identification_verify`
节点（用 monkeypatch 替换 StatsPAI 调用，或直接喂 diagnostics 给纯函数）。

预期：
- `star_rating` **不是** 0（本契约取 2）。
- `identification_failed` 为 `False`；`hard_block` 为 `False`。
- `assessment == "risk_found"`。
- `permissions["continue_to_estimate"] == "allow"`（不阻断）。
- `permissions["causal_language"] == "confirm"`、`permissions["requires_disclosure"] is True`、
  `promote_main_result == "confirm"`。这是产品已定的「要劝、用户可越（越过留痕）」一档，
  不是「警告即通过」：有风险时主结果晋升不给干净许可。

（本条目在写实现前修订过两次，两次都改在设计定稿前：① 初稿要求全 warn 时
`causal_language` 为假，与 `docs/specs/frontend-interaction-principles.md` §5 的
「要劝、用户可越」冲突 —— 弱工具、平行趋势未检验属于可越档，不是禁止档；② 布尔许可
改为三档，因为布尔值表达不出「未知」与「禁止」的区别。）

### C2 全 error/skipped 是未知，不是通过

程序：`identification_verify` 在 monkeypatch 掉 `import statspai` 后跑 DiD（既有用例
`test_identification_verify_missing_statspai_does_not_raise` 已覆盖同为 error 的场景），
并补一条 all-skipped 用例。

预期：
- `identification_diag["passed"] is None`。
- `identification_diag["assessment"] == "insufficient_evidence"`。
- `identification_diag["execution"] in {"failed", "not_run"}`。
- `identification_failed is False`（不截断），`star_rating is None`。
- 报告文本里**不出现**「检查通过」「该方法不成立」，且出现「尚未核查」类的未知表述。

### C3 显著性与设计有效性分离

程序：monkeypatch `statspai.callaway_santanna` 返回一个 `pvalue=0.001` 的对象，以及一个
`pvalue=None` 的对象，各跑一次 `_diag_did`。

预期：
- 两次调用产生的 `callaway_santanna` 记录**都不带** `status` 值 `pass` / `warn` / `fail`
  （改为 `role: "effect_estimate"`，或 `status: "reported"`），且**不进入**星级计算。
- `pvalue=None` 时记录里保留 `pvalue: None`，**不出现** `0.0`；`significant` 为 `None`
  （未知），不是 `True`。
- 两种情况下 `_diag_did` 返回的 `passed` 一致（设计有效性不受效应显著性影响）。
- **效应估计这一支失败时也是同一支**：`callaway_santanna` 抛异常时，那条 `error`
  记录同样带 `role="effect_estimate"`。它说明「这个稳健估计没算出来」，不等于
  「Goodman-Bacon 那条设计有效性检查没通过」，所以不得把设计有效性降级
  （否则 `machine_claim` 会从 `causal_with_caveat` 掉到 `association`，而旧的
  0-3 星口径并不会这样）。失败本身仍进 `diagnostics` 与 `report` 文本，不隐藏。
  程序：monkeypatch `statspai.callaway_santanna` 抛异常，跑 `_diag_did`，断言
  该记录 `role == "effect_estimate"` 且 `assess_diagnostics` 的 `assessment`
  仍为 `risk_not_found`（Bacon 通过）。

### C4 入口共用同一判定，不再各写一套

程序：对同一组 state 分别调用
`agent.graph.route_after_identification`、`agent.engine.readiness.paper_ready_to_write`、
`agent.engine.bind._identification_failed`、`backend.facade` 的 prewrite 确认入口、
`backend` 的 `/research/preview/promote` 护栏。

测试矩阵至少覆盖四行：
1. `identification_diag` 无（未跑）；
2. 跑完但未知（`assessment=insufficient_evidence`、`star_rating=None`、`passed=None`）；
3. 0 星（`star_rating=0`）；
4. `identification_failed=True` 但没有星级（只有 `star_rating == 0` 的入口会漏掉这一行）。

预期：
- 第 1–4 行里，**流程**问题（`hard_block`）在四个流程入口上答案相同，且都来自
  `identification_state`；
- 第 4 行在四个流程入口上**都是阻断**（这正是旧写法不一致的地方）；
- 章节绑定问的是更严的 `untrustworthy`，它是同函数里的另一个具名字段，不是第二套内联逻辑；
- **`agent/eval/` 也算流程入口**：`eval/run_task.run_pipeline` 自述是
  `route_after_identification` 的手写镜像，`eval/judge._hard_reject` 是评审器的硬拒绝。
  两处都必须调同一个判定函数，并且对第 4 行与真图给出相同答案。
- 运行时代码里不再有内联的 `star_rating == 0`（判定函数自身与测试除外）。
  程序：扫 `agent/**` 与 `backend/**` 的 `.py`（跳过 `.venv` / `node_modules` /
  `__pycache__` / 测试目录），匹配 `star_rating") == 0` 或 `star_rating"] == 0`。
  这个扫描必须**非空证明**过：把它指回基线版本的 `agent/graph.py` / `agent/eval/judge.py`
  时应当命中。

### C5 `passed` 的语义收窄，且未知不会被序列化成通过

程序：
1. `git grep -n '\.get("passed")\|\["passed"\]' -- '*.py'`，逐个检查运行时（非测试）的
   消费位置。
2. HTTP 面：对 `POST /sessions/{id}/identification` 与 `GET /sessions/{id}/evidence`
   各查一次未评估状态下的返回值。

预期：
- **没有任何位置把 `None` 当 `True`** —— 这是危险的那一侧，出现即 FAIL。
- 两个 HTTP 面在未评估时都返回 `null`，不返回 `true`。
- 「`None` 折叠成 `False`」只允许出现在**名字明说自己是「是否已验真」的谓词**里
  （`agent/engine/bind.py` 的 `passed is not True`、`agent/eval/run_task.py` 的
  `_identification_passed` 类检查）。这类谓词问的是「够不够格称为已验真」，
  未知按不通过处理是本增量要的方向，不是缺陷。除此之外不允许出现这种折叠。

（`backend/routers/analysis.py` 的 `IdentificationResponse.passed` 因此从 `bool` 改成
`Optional[bool]`，`make gen-api` 已重生成 `openapi.json` 与 `types/api.ts`。）

### C9 未知不会被星级抬成「已评估」

程序：构造 `{"star_rating": 3, "identification_diag": {"strategy": "did",
"star_rating": 3, "diagnostics": [{"test": "bacon_decomposition", "status": "skipped"}]}}`，
调 `identification_decision`；再构造只有 `star_rating` 没有明细的 state 对照。

预期：
- 有明细却全 `skipped` → `assessment == insufficient_evidence`、`passed is None`、
  `causal_language == "forbid"`、`promote_main_result != "allow"`、
  `requires_disclosure is True`。**不能被 3 星抬成干净通过。**
- 只有星级、完全没有明细 → 仍按星级回填（早期会话快照与既有夹具靠它），
  `star_rating=2` 时 `assessment == risk_found`、`causal_language == "confirm"`。
- 一条通过 + 一条没跑成（`error` 或 `skipped`）→ `passed is None`、
  `assessment == insufficient_evidence`、`execution == "partial"`。

### C6 既有测试基线不退

程序：`make test`（`check-api-drift` + `test-agent` + `test-backend` + `test-frontend`）。

开工前基线（`cd45d65`，同一台机器实测）：agent `1027 passed, 2 skipped`；
backend `629 passed, 8 skipped`；frontend `472 passed`。

预期：四项全绿，且三个分项的通过数**不低于**基线。若既有用例断言与新语义冲突，必须
逐条说明是哪条、为什么旧断言本身编码了被本增量认定的错误语义，不允许直接改测试迁就实现。

**注意**：开工时 `agent/tests` 里已经有一批本增量带来的新用例（增量三
`test_find_lit_purpose.py` 14 条 + 增量一 `test_identification_state_gate.py` 16 条），
所以期望值是基线 **加上**新增条数，不是等于基线。

### C8 前端不把「尚未核查」写成「通过」

程序：`cd frontend && npx vitest run src/components/__tests__/EvidenceView.test.tsx`

预期：三条断言过 ——
- `passed=null` / `assessment=insufficient_evidence` → 面板显示「尚未核查」，**不含**「通过」；
- `assessment=risk_found` / `star_rating=2` → 显示「有风险，需披露」，**不含**「通过」；
- `assessment=risk_not_found` / `star_rating=3` → 才显示「通过」。

### C7 端到端：真实数据 → 状态与许可

程序：用 built-in 数据跑一次真实节点（不需要 LLM）：
`statspai.california_prop99()` 落 CSV，`research_direction.method="did"` 带齐四列，
调 `identification_verify`，打印 `execution` / `assessment` / `star_rating` / `passed` / `permissions`。

预期：真实跑出 `completed` + `risk_not_found` + 3 星 + `passed is True` +
`causal_language is True`。这条用来证明「全部通过」这一档没有被上面的改动弄坏。

## 一轮验收后补做的修复（记录，供复核）

第一轮独立验收给了 REJECT，四条有实证的缺口，已逐条修：

1. **判定入口没收拢**：`agent/eval/run_task.py` 的 `run_pipeline` 自述是
   `route_after_identification` 的手写镜像，却内联 `star_rating == 0`；
   `agent/eval/judge.py` 的 `_hard_reject` 同样。两处改成调 `identification_hard_block`，
   并把「不内联星级」的扫描从 4 个文件扩到整棵 `agent/**` + `backend/**`。
2. **C5 措辞被证伪**：`bind.py` 与 `eval/run_task.py` 的两处谓词确实把 `None` 折叠成
   `False`。两处都是「够不够格称为已验真」，方向正确，因此**保留实现、改写契约措辞**
   （见 C5）：禁止的是 `None → True`，以及这两处之外任何位置的折叠。
3. **`_from_star` 回填过宽**：明细里有 `error`/`skipped` 时不该用星级抬成已评估。
   收紧为「完全没有明细才回填」，并给 `permissions_for` 的 `clean` 档加上
   `assessment == risk_not_found` 条件（否则一个 3 星、明细全 skipped 的 state 仍会
   拿到干净因果许可）。新增 C9 与三条用例。
4. **`skipped` 没按 docstring 生效**：`assess_diagnostics` 的注释说 `skipped` 会把
   `passed` 置 `None`，实现只对 `error` 生效。改成两档都算「没跑成」。

同时堵掉一处**未申报的行为变化**（不是 REJECT 项，但验收官要求确认）：真实 DiD 里
`callaway_santanna` 抛异常时，那条 `error` 记录原先不带 role，于是被算成设计有效性
缺口，把 `machine_claim` 从 `causal_with_caveat` 打成 `association`。既然效应估计
已与设计有效性分离，它的失败路径也该同属一支 —— 已给它加上
`role="effect_estimate"`，失败仍进 `diagnostics` 与报告文本。

## 本增量发现、但不在本增量范围内（未修，登记）

- **`agent/eval/run_task.py` 在 import 期写进程环境**：模块顶部执行
  `os.environ["ECONPAPER_LLM"] = "mock"`（离线评测强制 mock，是它自己的设计），
  但这是进程级副作用 —— 同进程里先 import 它，后面 `test_llm_router` 那批依赖
  `GENERATE_LLM_PROVIDER` 的用例全部退化成 mock。本增量新增的用例是第一个
  import 它的测试，因此在测试里用 autouse fixture 清干净，没有改该模块本身。
  这是个仍埋在仓库里的顺序依赖，建议单独开一条。
- **`docs/specs/frontend-interaction-principles.md` 原有的 Shapiro 引号句**：
  "应用型研究问题由经济学驱动，不由经济学文献驱动"在 Wayback 版原 PDF 全文里
  找不到（两轮均为独立取证：`driven/drive/driver` 命中 0 次）。2026-09-17 已去掉
  引号降为意译（见该文件），但**这条不属于本增量**，属于上一轮写下原则文档时的
  引用习惯问题，值得整体复查一遍。
- **跨面读数张力（基线继承）**：真实 DiD 里 `callaway_santanna` 抛异常时，
  证据面板（走 `identification_decision`）报「通过（★★★）」，而方法章节提示词里的
  `identification_status` 写「未验证/未提供」。两侧问的不是同一个问题（面板报设计
  有效性、绑定问够不够格称已验真），且**旧树同样如此**——本增量是把该情形恢复到
  基线配对，不是新造矛盾。但对外看确实互相打架，建议另开一条口径统一议题。

## 主观项

无。本增量是后端口径与许可逻辑，可由命令判定。
