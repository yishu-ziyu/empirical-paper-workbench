# 执行4：批次 5 运行时 Crossref（pytest 仍 mock）

你是 cmux 同窗口的执行会话。批次 1 已有 `resolve_literature_source`，运行时最后一档仍是 mock。
不要问人确认。读完本文件就改代码、跑测试、写 STATUS。

## Goal

运行时（非 pytest）文献检索最后一档改为 Crossref。
无网或 Crossref 失败必须标 `literature_source=mock_degraded`，不准假装 `crossref` 成功。
pytest / `ECONPAPER_LLM=mock` / `in_pytest()` 仍走 mock。

## Hard bar

1. 在 pytest 里：`search_literature` 默认 `literature_source=="mock"`，不打真网。
2. 显式 `literature_source="crossref"` 且 `crossref_search` 抛 `RuntimeError`：得到 `mock_degraded` + mock 条目，不是 `crossref`。
3. 运行时 resolver 最后一档是 `crossref`（不是 mock）。可用单测直接调 `resolve_literature_source`，把 `in_pytest` monkeypatch 成 False、清空显式 state 与 `LITERATURE_SOURCE` env。
4. 查询串仍不拼标题（批次 1 已改，不要退回去）。

## Improve

文档写明：本批取代 ADR-0010「默认 mock」。只改文献相关文档/注释，不要新开产品。

## 产品与权威

- 根目录：`/Users/mahaoxuan/Desktop/经济学论文/econpaper`
- 设计：`docs/specs/paper-engine.md` 批次 5 + resolver 规则
- 禁止 git commit / push / PR

## 只许改这些文件

- `agent/nodes/search_literature.py`（resolver 最后一档；已有 crossref 分支，改默认）
- `agent/nodes/literature_sources/crossref.py`（若错误路径不够：失败必须 `RuntimeError`，好让节点降级）
- `agent/tests/test_search_literature.py`
- `agent/tests/test_crossref_source.py`
- `docs/adr/0010-one-product-merge.md` 或 `docs/specs/paper-engine.md` 里与默认文献源有关的一句（可选，保持最短）

## 禁止改

`estimate.py`，`robustness_check.py`，`review_chapter.py`，`prompts/*`，
`generate_chapter.py`，`generate_title.py`，`design/spec.py`，`set_direction.py`，
`graph.py`（批次 6 的并行扇出不要做），`facade.py`，`protocols.py`，`state.py`，
`engine/readiness.py`（literature_ran 已认 `mock_degraded` / `literature_produced_by`），
`engine/prewrite.py`，`engine/bind.py`。

## 必须实现的机制

`resolve_literature_source` 顺序必须是：

1. state 里显式 `literature_source`（非空）优先。这样 `disabled` 测试仍绿。
2. `in_pytest()` 或 `ECONPAPER_LLM=mock` → `mock`
3. env `LITERATURE_SOURCE` 若有值 → 用它
4. **最后一档：`crossref`**（批次 1 这里是 mock，本批改掉）

`search_literature` 已写 `literature_produced_by="search_literature"`。不要删。
`_build_query` 不拼 `title_chapter.title`。不要加回去。

无网：`crossref_search` 失败 → 条目走 mock 库，`literature_source="mock_degraded"`。

## 测试怎么跑

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/econpaper
./agent/.venv/bin/python -m pytest \
  agent/tests/test_search_literature.py \
  agent/tests/test_crossref_source.py -q --tb=short
```

不要打真 Crossref 当绿的条件。用 monkeypatch。

## 做完写这个文件

路径：`docs/handoffs/EXEC-4.STATUS.md`

```text
status: done
ran: <命令和 pass/fail>
changed: <文件列表>
risk: <一句失败场景>
```

卡住写 `status: blocked`。现在开工。
