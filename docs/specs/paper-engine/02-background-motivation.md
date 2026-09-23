# Background & Motivation

> 上级：[econpaper 论文发动机：数字先于正文](../paper-engine.md)


## 产品身份

ADR-0010：唯一产品是 `econpaper/` 网页端。StatsPAI 是经过验证的本地源码依赖，
位于 `../dependencies/StatsPAI/`；识别、稳健性和多语言代码导出均由产品自有实现负责。
本设计不碰前台排版。

人做的事：定方向、看 0 星、改大纲要点、批章节、点导出。  
机器做的事：清洗、识别诊断、估计、稳健性、检索、填六章、接地评审、翻译代码、编参考文献、出 tex/pdf/docx。

## 今天两套顺序

图（`build_graph` 边）：

```
upload_data → clean_data → generate_title → set_direction
  → identification_verify
      0 星 → hitl_pause → 回到 identification_verify
      否则 → search_literature → build_citation_graph → estimate
  → generate_outline → generate_chapter ↔ review_chapter
  → robustness_check → translate_code → generate_references → export_docx
```

操作台（`backend/routers/outline.py` + `facade.set_direction_and_outline`）：

```
POST /direction
  → set_direction（写出 main_specification）
  → identification_verify
  → 0 星或 identification_failed：落盘，不生成大纲
  → 否则 estimate → generate_outline
```

`backend/` 不 import `search_literature`。章节写作是另一扇门：`POST /generate-chapter`。稳健性是第三扇门：`POST /robustness`，写作不检查它是否跑过。

`GET /journey` 用 `body_chapters` 非空当作“估计建模已完成”（`progress._infer_journey`）。正文出现被当成数字出现。

上传之后权威状态在 Facade 内存 `_sessions[id]["state"]`。`get_state` 优先内存，其次 PostgresSaver。`run_upload_pipeline` 的 `graph.invoke` 写的是 checkpointer；方向之后的产物若只 `save_state`，再 `graph.invoke` 同一 `thread_id` 看不见估计。这不是一个可 resume 的通道。

## 当前错误如何往下传

| 错位 | 代码 | 下游吃到什么 |
| --- | --- | --- |
| 标题在方向之前 | `graph.py`：`clean_data → generate_title → set_direction` | `generate_title` 只看见列名；`search_literature` 用早产标题拼查询 |
| 稳健性在六章之后 | `route_after_review` 走到 `"translate_code"` 才进 `robustness_check` | 结果章要写稳健性，state 里还没有表 |
| 操作台跳过文献与稳健性 | `set_direction_and_outline` 只串识别 + 估计 + 大纲 | `literature_entries` 空 |
| 门吃不下方法列 | `DirectionRequest` 只有 question/dv/iv/controls/method/template | `identification_verify` 缺 `time_col`/`instrument` 等则 `star_rating=None`；非 OLS 估计无法开工 |
| 主估计一律 OLS 风格 | `estimate._fit`：`statspai.feols` / `smf.ols` | IV/RD/SCM 诊断跑过，主表仍是 `y ~ treat + controls` |
| `DirectionSpec` 公式过窄 | `to_main_specification` | 无 IV/RD/SCM 字段；`cluster_levels` 恒 `[]` |
| 结果章靠顶层 `state.results` | `_collect_render_kwargs` | 空串时模型编系数 |
| HTTP 可注入假表 | `facade.generate_chapter` 把 `render_kwargs` 填进空键 | `test_chapter.py` 已用 `render_kwargs.results="R"` 出结果章 |
| HTTP `chapter.type` 被忽略 | 节点只读 `outline[idx]` | 方向后 `idx=0`，点结果章仍写引言 |
| 方法章把 OLS 写成识别 | `prompts/methods.py` | 模型被指令写成因果 |
| 结构检查逼因果话术 | `check_structure` 对 methods 一律 ≥2 条识别假设；OLS 走 `_DEFAULT_HYPOTHESES` | 按新 prompt 写的关联章结构失败、回炉 |
| mock 评审奖励识别词 | `mock_review_llm`：含「内生」「DID」加分 | pytest / JSON 降级路径把 OLS 章推向因果黑话 |
| 评审 JSON 失败静默 mock | `call_review_llm` except → mock；`test_review_bad_json_falls_back_to_mock` 钉死沉默 | `GET /review` 只有 score，像真审过 |
| 文献默认 mock | `resolve_literature_source` 运行时最后一档 `crossref`；pytest 仍 mock | 文献批次已取代 ADR-0010「默认 mock」 |
| 全图无方向仍往下跑 | `run_upload_pipeline` / `test_graph_has_three_nodes` 调 `graph.invoke` | 查询 `"economics"`，空 `results` 仍出大纲 |

`docs/product/glossary.md` 写正文章含 `discussion`；图与测试钉死的是 `intro / lit_review / data_desc / methods / results / conclusion`。发动机以图为准。discussion 不是第六章。

`protocols.EstimateOutput` 已存在（`results` / `estimate`）。`EconPaperState` 已有这两个键（`results` 在 state 里写了两次，是重复注解，不是两个字段）。新键是 `write_blocked`、`treatment_row`、`degradations`、`review_source` 等。

---
