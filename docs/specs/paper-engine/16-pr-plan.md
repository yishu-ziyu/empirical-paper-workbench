# PR Plan

> 上级：[econpaper 论文发动机：数字先于正文](../paper-engine.md)


按抽走测试排序。每一批可单独审。做到该批怎样算完就停。

## 批次 1 - 预写线性路径 + 按章开写 + 文献(mock) + 门上数字

- **依赖：** 无  
- **文件：**  
  - 新：`agent/engine/readiness.py`，`agent/engine/prewrite.py`  
  - `agent/graph.py`（线性边：无方向 `END`；有方向走 `run_prewrite` 的节点序；**不**加 `wait_*`；六章不编进预写图）  
  - `backend/facade.py`（`set_direction_and_outline` → `run_prewrite`；忽略 `TRUTH_KEYS`；`write_blocked`→409；**成功写章后调用 `review_chapter`**；import `search_literature` / `build_citation_graph` / `robustness_check` / `review_chapter`）  
  - `backend/routers/outline.py` + `schemas/responses.py`（`DirectionResponse` 增 `results/estimate/claim/literature_source/degradations/write_blockers`）  
  - `backend/routers/progress.py` + `backend/tests/test_journey.py`（第 4/5 站看估计/稳健性）  
  - `agent/nodes/generate_chapter.py`（按章就绪；`_resolve_slot` 认 `current_chapter.type`；results 尚不追加工具表）  
  - `agent/nodes/estimate.py`（OLS 路径补 `produced_by` + `treatment_row`，分派仍可先 OLS）  
  - `agent/nodes/robustness_check.py`（写 `produced_by` + `diagnostics`）  
  - `agent/nodes/search_literature.py`（`resolve_literature_source`；查询不拼标题；第一批最后一档 mock）  
  - `agent/state.py`，`agent/protocols.py`（`GenerateChapterOutput.write_blocked/write_blockers`；`LiteratureOutput` / state 增加 `literature_produced_by`、`literature_query`）  
  - `conftest.py`：`make_write_ready_state`  
  - 上表全部 `generate_chapter(` 测试文件 + `test_facade.py` 调用序 + `test_graph.py`  
- **改什么：** 估计在文献前。文献节点进 Facade（mock）。上传 invoke 洗完即停。  
- **怎样算完：** 硬条 1–3（OLS：`star_rating is None` 算过）；`POST /direction` JSON 里能看见 `results`；无识别时 intro 409；无 `produced_by` 的假 `results` 写不进结果章；`test_set_direction_and_outline_calls_both_nodes` 调用序含 estimate、robustness、search_literature（需 mock 这些节点）；`facade.generate_chapter` 成功后 `review_chapter` 被调用（可用 monkeypatch 计数）。

## 批次 1b - 假审可见 + 写路径上的评审字段

- **依赖：** 批次 1（写章已调用 `review_chapter`）  
- **文件：** `review_chapter.py`（写 `review_source` / `review_degraded` / `grounding_failures`），`protocols.py`（`ReviewOutput` 加这三键），`state.py`，`facade.get_review`，`schemas/review.py`，`schemas/responses.py`（`GenerateChapterResponse` 带 score / auto_decision / review_source），`record_degradation`，`test_review_weights_and_channel.py`，**`backend/tests/test_review.py`（POST generate-chapter 之后 GET /review，是调用不是只读）**  
- **改什么：** 假审可见；响应与 GET 投影同一批；改钉死沉默的测试。  
- **怎样算完：** 经 Facade 写一章后 `GET /review` 有 `review_source`；坏 JSON 时值为 `mock_fallback`；回退 idx 时 `auto_decision=="fail"` 且 HTTP 200。

## 批次 2 - 关联主张关上 + prompt + bind

- **依赖：** 批次 1  
- **文件：** `prompts/methods.py`，`prompts/results.py`，`prompts/lit_review.py`，`prompts/outline.py`，`review_sources/structure_checks.py`，`review_sources/mock_review.py`，`review_chapter.py`（rubric 前跑主张检查；association 权重），`agent/engine/bind.py`，`generate_chapter.py`（用 bind kwargs），`generate_title.py`（可读估计），相关 prompt/结构/mock 测试，**OLS 方法章硬条测试**  
- **怎样算完：** 硬条 6；方法章 association 的 system 不含“解决内生性”；综述 prompt 不再允许空表时编 (Author, Year)。

## 批次 3 - 方法分派 + 门上的列 + 稳健性分派

- **依赖：** 批次 1  
- **文件：** `backend/routers/outline.py`（`DirectionRequest` 显式方法字段 + `extra="allow"`），`design/spec.py`，`set_direction.py`（投影 `charls_config` / 面板列），`estimate.py`（上表五个调用；**禁止 `iv_diag` 主表**），`robustness_check.py`（同表），`test_estimate.py`，`test_direction_spec.py`，`test_robustness_check.py`，`test_identification_verify.py`（有 `time_col` 才能出星）  
- **怎样算完：** IV fixture 的 `estimator=="statspai.ivreg"` 且有 `treatment_row`；缺 instrument → `status=error`、无假系数；SCM/RD 主表不是 `y ~ treat` 的 OLS；稳健性在 IV 上不跑 `feols(y~treat)`，否则 `reason="ols_battery_on_non_ols"`。

## 批次 4 - 接地 + 工具表进 `versions[0]`

- **依赖：** 批次 2、3  
- **文件：** `review_sources/grounding.py`，`generate_chapter.py`（results：`content = prose + "\n\n" + results`），`review_chapter.py`，`test_grounding.py`，`test_generate_chapter_versions.py`  
- **怎样算完：** 硬条 4；另造系数表失败；rollback 的 `versions[k]` 仍含表。

## 批次 5 - 运行时 Crossref

- **依赖：** 批次 1（resolver 已在）  
- **文件：** `search_literature.py`（最后一档 `crossref`），`test_search_literature.py`，`test_crossref_source.py`；文档写明**取代 ADR-0010 默认 mock**  
- **怎样算完：** pytest 仍 mock；无网运行时 `literature_source` 为 `mock_degraded`，不是假装成功的 `crossref`。

## 批次 6 - 可选并行

- **依赖：** 批次 1、5  
- **文件：** `graph.py`，新测试：`generate_title` 在扇入后只跑一次（LangGraph 0.2.50）  
- **改什么：** 仅识别后文献∥估计。Facade 可仍串行 `run_prewrite`。  
- **怎样算完：** 该测试绿。未绿则保持线性。
