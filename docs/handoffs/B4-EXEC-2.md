# 执行2：批次 4 - 结果章把工具表拼进 versions[0]

你是 cmux 同窗口执行会话。不要问确认。读完就改、跑测试、写 STATUS。

## Goal

结果章 `content` 和 `versions[0]` 必须是：

```text
<模型写的解读>


<state["results"] 那张主表>
```

读者在正文末尾能看到 `estimate.treatment_row` 这一行。模型自己再画表也不许顶掉这张工具表。

## Hard bar

1. `type=="results"` 且 `estimate.status=="ok"`：`content == prose + "\n\n" + state["results"]`
2. `versions[0] == content`（即已含表）
3. regenerate：重新 `call_llm`，再拼**当前** `state.results`；旧 versions 保留且已含当时的表
4. 非 results 章、或 `estimate.status` 不是 `ok`：不要拼表（保持现在只写 prose）

## 只许改

- `agent/nodes/generate_chapter.py`（在 `content = call_llm(...)` 之后拼表；不要改开写门、不要改 bind）
- `agent/tests/test_generate_chapter.py`（结果章断言会从「content == MOCK」变成含主表）
- `agent/tests/test_generate_chapter_versions.py`
- 若 `test_estimate.py` 里结果章 user prompt 测试被你的断言连带打破，只改断言、不改估计节点

## 禁止改

`review_sources/grounding.py`，`review_chapter.py`，`rollback.py`，`prompts/*`，`estimate.py`。

## 机制

```python
prose = call_llm(system, user)
est = state.get("estimate") or {}
if str(chapter_type) == "results" and isinstance(est, dict) and est.get("status") == "ok":
    table = (state.get("results") or "").strip()
    content = prose + "\n\n" + table if table else prose
else:
    content = prose
versions = [content] + existing_versions
```

rollback 由执行4看。你不要在 rollback 里再拼一次。

现有六章循环测试用 `make_write_ready_state`，结果章也会被拼表。更新断言：`versions[0] == content`，且 results 那一章 `treatment_row` 或 `| age |` 在 content 里。

## 测试

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/econpaper
./agent/.venv/bin/python -m pytest \
  agent/tests/test_generate_chapter.py \
  agent/tests/test_generate_chapter_versions.py \
  agent/tests/test_graph_six_chapters.py \
  agent/tests/test_estimate.py -q --tb=short
```

## 做完写

`docs/handoffs/B4-EXEC-2.STATUS.md`

```text
status: done
ran:
changed:
risk:
```

现在开工。
