# Goals & Non-Goals

> 上级：[econpaper 论文发动机：数字先于正文](../paper-engine.md)


## Goals

1. 方向已设且 CSV 含点名列时：任何正文出现之前，`identification_diag` 已在 state 里。`star_rating` 是 `0–3` 的 int，或 `None`（OLS / 未知方法 / 诊断未跑成 → 按关联写）。`None` 不是失败。
2. 结果章生成之前，`state.estimate.produced_by == "estimate"`，`state.results` 是主估计 Markdown，且含 `estimate.treatment_row` 这一行。
3. 结果章生成之前，`robustness_check` 已跑过（`produced_by == "robustness_check"` 或含 `diagnostics` 键），或可见降级。占位 `{"summary_table": "No main specification available"}` 不算已跑。
4. 结果章 `content` 含那一行 `treatment_row`，且没有另一行处理变量表与之冲突。`versions[0] == prose + "\n\n" + results`。
5. 文献综述只引用本次检索列表里的 title/DOI/`[N]`。编号表为空则不得用 `(Author, Year)` 编造。
6. pytest 仍走 mock（`in_pytest()` / `ECONPAPER_LLM=mock`）。运行时仍走本机 MiniMax SSOT。
7. 图与 Facade 预写走同一函数 `run_prewrite`。`generate_chapter` 按章执行就绪检查。HTTP 不得用 `render_kwargs` 注入真值字段。
8. OLS / 关联方法章：不要求识别假设；mock 评审不因缺少「内生/DID」而压分；`causal_claim_forbidden` 在 rubric 之前判定。

## Non-Goals

- 前台视觉、旅程文案润色、新桌面壳。
- 把图换成开放 ReAct 规划器，或拆成 writer/reviewer/estimator/librarian 多智能体并加 A2A。
- 把 MCP 做成产品。
- 在线学习 / DPO / 用用户论文微调。
- 恢复或合并已退役的旧 CLI Git 历史，或推本地 main。
- 训练专用评审模型；替换 ADR-0008 的 generate/review 分配置。
- 让 OLS 获得因果星级（识别节点已经如此；要关的是正文路径）。
- 第一批就编译文献∥估计的扇入扇出。

怎样算完：文末硬条测试全绿，且不能再指出一个本范围内、测试能抓住的功能或设计缺陷。做到就停。

---
