# 执行1：批次 1b + 评审主张检查（只动评审可见性）

你是 cmux 同窗口的执行会话。协调员已开工批次 1。你不要重做批次 1。
不要问人确认。读完本文件就改代码、跑测试、写 STATUS。

## Goal

经 Facade 写完一章后，`GET /review` 能看见这是假审还是真审。
坏 JSON 降级必须写出 `review_source=mock_fallback`，不能假装审过。
回退章节索引时 HTTP 仍 200，`auto_decision=fail`。

本会话顺带把批次 2 里**只属于 `review_chapter.py` 的主张检查**做掉
（`causal_claim_forbidden` 在 rubric 前；association 权重）。
prompt / bind / structure_checks / mock_review 正文规则由执行2做。
你只改评审节点如何读这些结果。

## Hard bar

1. `facade.generate_chapter` 写 intro 成功后，`GET /sessions/{id}/review` 的 JSON 含 `review_source`。
2. `call_review_llm` 收到坏 JSON / 抛错时：不崩；有 rubric；`review_source=="mock_fallback"`；`review_degraded is True`。
3. 评审回退 `current_chapter_index` 时，写章 HTTP 仍 200，`auto_decision=="fail"`。
4. `ReviewOutput` 新键 ⊆ `EconPaperState`（`test_schema_consistency` 绿）。

## Improve

`test_review_bad_json_falls_back_to_mock` 不再把沉默降级当契约。

## 产品与权威

- 根目录：`/Users/mahaoxuan/Desktop/经济学论文/econpaper`
- 设计：`docs/specs/paper-engine.md` 批次 1b + 「可见降级」+ 主张检查第 1、4 条
- 批次 1 已落地：写章后 Facade 已调用 `review_chapter_node`
- 禁止 git commit / push / PR
- 禁止改执行2/3/4 的文件（见下）

## 只许改这些文件

- `agent/nodes/review_chapter.py`
- `agent/protocols.py`（只给 `ReviewOutput` 加键，不动其它 Output）
- `agent/state.py`（只加 `review_source` / `review_degraded` / `grounding_failures`）
- `backend/facade.py`（`get_review`、`record_degradation(..., visible=False)`；不要改 `run_prewrite` / 估计 / 文献）
- `backend/schemas/review.py`（`ReviewInfoResponse` 加三字段）
- `backend/schemas/responses.py`（`GenerateChapterResponse` / `RegenerateResponse` 加 `score` / `auto_decision` / `review_source` / `review_degraded` / `grounding_failures`）
- `backend/routers/chapter.py`（把上述字段填进写章响应；查找章仍按 type，评审回退 idx 时不要拿空槽）
- `backend/routers/review.py`（若需要把新字段传出）
- `agent/tests/test_review_chapter.py`
- `agent/tests/test_review_weights_and_channel.py`
- `backend/tests/test_review.py`（必须加：POST generate-chapter 之后 GET /review，不是只读手写 state）

## 禁止改

`prompts/*`，`engine/bind.py`，`generate_chapter.py`，`generate_title.py`，
`review_sources/structure_checks.py`，`review_sources/mock_review.py`，
`estimate.py`，`robustness_check.py`，`search_literature.py`，`design/spec.py`，
`set_direction.py`，`graph.py`，`engine/readiness.py`，`engine/prewrite.py`。

若你需要 `mock_review_llm` 的 `claim` 参数：先做兼容（缺省旧签名），
不要改 mock_review 的分数表。执行2 拥有那个文件。

## 必须实现的机制

`review_chapter` 写出：

```python
review_source = "mock" | "llm" | "mock_fallback"
review_degraded = bool
grounding_failures = list  # 1b 可先空列表；若你做主张检查，命中则含 causal_claim_forbidden
```

`call_review_llm` 失败或坏 JSON 时仍可回 `mock_review_llm`，但必须标记 `mock_fallback` + `review_degraded=True`，
并 `facade.record_degradation(session_id, node="review_chapter", reason=..., fallback="mock_review_llm", visible=True)`。
若节点里拿不到 facade，把 degradations 写进返回的 state 列表，Facade 再 record。

主张检查（本文件职责，因为在 `review_chapter` 里）：
- `call_review_llm` **之前**跑禁用子串：`本文识别了因果` / `因果效应显著` / `识别策略成立` / `解决内生性`
- 允许：`无法做因果识别` / `仅解释为相关`
- 命中：`grounding_failures` 含 `causal_claim_forbidden`，综合分封顶 0.50，回炉
- `weights_for_chapter("methods", claim="association")`：
  endogeneity=0, identification=0.1, robustness=0.25, contribution=0.25, readability=0.4

`get_review` 与 `ReviewInfoResponse` 必须投影 `review_source` / `review_degraded` / `grounding_failures`。

## 测试怎么跑

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/econpaper
./agent/.venv/bin/python -m pytest \
  agent/tests/test_review_chapter.py \
  agent/tests/test_review_weights_and_channel.py \
  agent/tests/test_schema_consistency.py -q --tb=short
./backend/.venv/bin/python -m pytest backend/tests/test_review.py -q --tb=short
```

backend 虚拟环境没有 psycopg / jinja2。不要为了绿而去装无关包，也不要改上传图。

## 做完写这个文件

路径：`docs/handoffs/EXEC-1.STATUS.md`

```text
status: done
ran: <你跑过的命令和 pass/fail>
changed: <文件列表>
risk: <一句失败场景>
```

卡住写 `status: blocked` 和缺什么。不要改别人的 STATUS。
现在开工。
