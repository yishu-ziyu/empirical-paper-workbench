# 验收契约：#40 增量三（后端） —— 方法核查复用三源检索，来源不掺假

Status: accepted

验收记录：一轮独立验收 **ACCEPT**（C1–C7 逐条复跑全 PASS；自报的 `106 passed`
经复跑属实，基线 92 可反推；既有测试文件零改动）。登记一条非阻断残留：
`check_method_literature` 把主查询与各条风险查询的 `source_status` 按「后写覆盖」
汇总，于是某条风险查询瞬时失败时，主查询来的 hit 会被贴上 `degraded:*`。
方向保守（不会把 mock 说成 ok），契约未定义多查询聚合语义，故不改；后续若要修，
按「每个 hit 记录产生它的那次调用的状态」。

来源：外部参谋意见（`/Users/mahaoxuan/Downloads/issue-40-frontend-advisory-cd45d65.md`）
§2.1、§2.3、§7（Q5）、§8、§9 增量三；`docs/specs/frontend-interaction-principles.md` §3 §6 §7。
基线：`cd45d65d952649f84d4c6b19a52f71294d79e5b0`。

## Change

把「方法核查」这一类检索接到已有的三源基础设施（`agent/find_lit/fetch_papers.py`，
OpenAlex + Crossref + Semantic Scholar，DOI 去重，排除 mock/synthetic）上，用**用途**
把查询规划、排序和证据产物分开；同时堵住旧分支的两处来源风险。

用户可观察的结果：

- 检索有显式的用途参数 `purpose = method_check | topic_positioning`：同样是「IV」，
  方法核查问的是「这个方法在这里适用吗、什么时候会失效」，主题定位问的是「谁做过相近的事」。
- **方法核查不需要已确认的设计**。现在 `search_find_lit` 要求
  `design.status == "confirmed"`，而方法核查必须发生在方法定稿**之前**，否则形成
  「确认方法前必须查文献、确认方法后才允许检索」的循环依赖。
- 主题定位的既有权衡不动：`search_find_lit` 的已确认设计门槛**保持不变**。
- 生产路径里**不出现 mock / synthetic 命中**；旧分支里那两个无条件从 mock 语料取出的
  方法锚点，不再被当成核查依据混进真实 API 结果。
- 必查的威胁文献**不会因为总条数上限被静默挤掉**。

## Not this

- **不新建检索源、不建两个数据库**：复用 `fetch_papers` 的三源、去重、来源状态。
- **不改依赖图**：`agent/engine/prewrite.py` 的 `PRWRITE_SEQUENCE` 拓扑保持原样；本增量
  只交付可被调用的后端能力，不新增图节点。
- **不改前端**（首屏三态与帮助入口由主 agent 单独处理）。
- **不做全量 PDF 抓取**：证据只记录「读到哪一层」（元数据 / 摘要 / 原文）。
- **不改 `agent/nodes/identification_verify.py`、`agent/engine/**`、`agent/graph.py`、
  `backend/**`、`frontend/**`** —— 这些由主 agent 并行修改，动了会冲突。
- 不推远端。

## Evaluator

implementer 实现并自检；validator 按 C1–C7 独立复跑。本批无主观项。

## Checks

### C1 用途参数决定查询与排序，且不是贴在消费端的标签

程序：对同一个设计，分别以 `purpose="method_check"` 与 `purpose="topic_positioning"`
调检索入口，打印两次的 `query` 与结果顺序。

预期：两次的 `query` **不同**（方法核查的查询含方法名与适用条件/失效模式词；主题定位的
查询用问题、方法、结果变量、处理变量），且两次结果顺序可以不同。用一个只记录入参的
假 searcher 证明差异来自查询规划，而不是事后重排标签。

### C2 方法核查接受暂定设计；主题定位仍要求已确认

程序：
1. 用 `status="draft"`（或 `confirmed=False`）的设计调方法核查入口 → 有结果、`reason` 为空。
2. 同一份未确认设计调 `search_find_lit` → 仍返回 `empty_find_lit(reason="design_unconfirmed")`。
3. 用已确认设计调 `search_find_lit` → 行为与改动前一致（跑它的既有测试即可）。

预期：1 通过、2 通过、3 的既有测试全绿。

### C3 生产路径不掺 mock，旧锚点不再污染真实结果

程序：
1. 造一个命中带 `source="mock"`（或 `sources=["mock_degraded"]`）的假 searcher，
   `fetch_papers` 返回的 `hits` 里**不得**含它。
2. 让真实源返回若干命中，再走旧的 `agent/nodes/search_literature.py` 分支（未确认设计、
   `literature_source` 非 mock）：结果里**不得**出现 mock 语料的方法锚点条目。
3. 三源全部抛异常时：`source_status` 每个源都是 `degraded:<ExceptionName>`，`hits` 为空，
   **不**回落到 mock 语料。

预期：1、2、3 全过。第 2 条要贴出改动前后同一个输入的对比（改动前 mock DOI 出现在结果里）。

### C4 必查的威胁不会被条数上限挤掉

程序：构造「方法锚 + 常规检索结果」合计已超过 `MAX_LITERATURE_ENTRIES`（20）的情形，
威胁查询另有命中。

预期：威胁条目在结果里**存在**。给出改动前同一输入的对比：改动前威胁条目 0 条。
覆盖情况按「必查风险是否都有对应文献」判断，而不是按总条数或「凑够五张卡」判断。

### C5 每条证据带齐出处字段

程序：取方法核查返回的一条真实命中，打印它。

预期：至少含 `title`、`doi`（或明确 null）、`url`、`source`、`year`，以及本增量新增的
**读取层级**（元数据 / 摘要 / 原文）与**来源状态**。未核对的摘要不得标成已读原文。
检索不到某项风险时，记录里是「未找到」，不得写成「不存在」。

### C6 来源失败保留真实状态，不造结果

程序：让其中一个 searcher 抛异常、另两个正常。

预期：`source_status` 里失败的那一个是 `degraded:<ExceptionName>`，成功的是 `ok`；
结果只来自成功的源；整体不抛异常、不补造条目。

### C7 既有 find_lit 测试不退

程序：`PYTHONPATH=. agent/.venv/bin/python -m pytest -q agent/tests -k "find_lit or literature or card or dedupe"`

预期：全绿，通过数不低于开工前记录（开工前请先跑一次并记数）。若要改既有用例，必须逐条
说明旧断言为何编码了被本增量认定的错误语义。

**不要跑 `make test` / `make check-api-drift`**：主 agent 正在并行改同仓库的其它文件，
全量闸门由主 agent 统一跑。
