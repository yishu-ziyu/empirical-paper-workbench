# 执行2：批次 2 的 prompt + bind + 结构/mock 分数（不动评审节点）

你是 cmux 同窗口的执行会话。协调员已完成批次 1。你不要重做预写图。
不要问人确认。读完本文件就改代码、跑测试、写 STATUS。

## Goal

OLS / 关联论文的方法章不再被指令写成因果识别。
综述编号表为空时不得编造 (Author, Year)。
结果章 system 只解读文末主表，禁止再画表、禁止「见表 2」。
`bind_chapter_kwargs` 成为章节 prompt 的真值入口。

## Hard bar

1. `{claim}` 为 association 时，`prompts/methods.py` 的 system **不含**「解决内生性」。
2. `prompts/lit_review.py` 不再写「编号表为空则仍使用 (Author, Year)」。表空则不得编篇名与年份。
3. 夹具方法章：`len(content) >= 200`，含 `$y_i=\alpha+\beta D_i+u_i$`，不含 `因果` / `识别策略` / `解决内生性`。
   - `check_structure(content, "methods", claim="association") == []`
   - `mock_review_llm(..., claim="association")` 的 endogeneity=0.7、identification=0.7
4. `generate_chapter` 渲染用 `bind_chapter_kwargs` 覆盖同名空键。真值来自 state 节点产物，不来自 HTTP。

硬条 6 里「`review_chapter` 综合分 ≥ 0.7 且不回退 idx」由执行1改 `review_chapter.py`。
你写测试覆盖 check_structure + mock_review + prompt 文本。不要去改 `review_chapter.py`。

## Improve

association 的 mock 分数不再走 else=0.4（那会让综合分 < 0.7）。

## 产品与权威

- 根目录：`/Users/mahaoxuan/Desktop/经济学论文/econpaper`
- 设计：`docs/specs/paper-engine.md` 批次 2 + 「主张模式」+ 「投影进 prompt」
- 禁止 git commit / push / PR

## 只许改这些文件

- `agent/prompts/methods.py`
- `agent/prompts/results.py`
- `agent/prompts/lit_review.py`
- `agent/prompts/outline.py`（若 outline 仍写因果套话）
- `agent/engine/bind.py`（新建）
- `agent/nodes/generate_chapter.py`（调用 bind；不要改开写门 `paper_ready_to_write`）
- `agent/nodes/generate_title.py`（标题可读估计/方向，不要点名未跑过的发现）
- `agent/nodes/review_sources/structure_checks.py`
- `agent/nodes/review_sources/mock_review.py`
- `agent/tests/test_prompts.py`
- `agent/tests/test_structure_checks.py`
- `agent/tests/test_mock_review_llm.py`
- 新建 `agent/tests/test_association_methods.py`（硬条 6 的 prompt/结构/mock 部分）

## 禁止改

`review_chapter.py`，`protocols.py`，`state.py`，`facade.py`，`schemas/*`，
`estimate.py`，`robustness_check.py`，`search_literature.py`，`design/spec.py`，
`set_direction.py`，`graph.py`，`engine/readiness.py`，`engine/prewrite.py`，
`backend/routers/outline.py`，`backend/tests/test_review.py`。

## 必须实现的机制

### bind.py

```python
def bind_chapter_kwargs(state, chapter_spec) -> dict:
    rd = state.get("research_direction") or {}
    rob = state.get("robustness_results") or {}
    return {
        "research_question": rd.get("question") or state.get("research_question") or "",
        "method": chapter_spec.get("method") or rd.get("method") or "",
        "results": state.get("results") or "",
        "robustness_table": rob.get("summary_table") or "",
        "key_references": format_entries(state.get("literature_entries") or []),
        "citation_indices": state.get("citation_indices") or {},
        "star_rating": state.get("star_rating"),
        "claim": claim_mode(state),
        "identification_report": (state.get("identification_diag") or {}).get("report") or "",
    }
```

`claim_mode` 从 `engine.readiness` 导入，不要复制一份。
`generate_chapter` 用这份 kwargs 覆盖 `_collect_render_kwargs` 的同名键。

### methods prompt

`{claim}` = association：写相关 / 条件关联；禁止「该策略如何解决内生性」。
只有 `causal_with_caveat` 且方法是 did/iv/rd/scm 才写识别假设。

### results prompt

SYSTEM：主表已在文末，只解读，禁止再画表，禁止「见表 2」另造基准表。
USER 仍给 `{results}` 与 `{robustness_table}`。

### lit_review prompt

删除「编号表为空则仍使用 (Author, Year)」。表空不得编造篇名与年份。

### check_structure

看 `claim_mode`。association 的 methods：仍要 `$...$` 方程；**不要**识别假设菜单。
causal_with_caveat：方程 + ≥2 条假设。
`star is None` 的 DiD 按 association，不逼平行趋势词。

### mock_review_llm

签名增加 `claim: str`（缺省 `"causal_with_caveat"` 以保旧测试，或按设计看 claim_mode）。
association 钉死：

| 维 | 无禁用主张 | 命中 因果/识别策略/解决内生性/本文识别了因果 |
| --- | --- | --- |
| endogeneity | 0.7 | 0.2 |
| identification | 0.7 | 0.2 |
| robustness | 0.7（不要求「稳健」词） | 0.7 |
| contribution | 0.7（不要求「贡献」词） | 0.7 |
| readability | len>=200 → 0.8；>=100 → 0.6；否则 0.3 | 同左 |

不要沿用 else=0.4。

## 测试怎么跑

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/econpaper
./agent/.venv/bin/python -m pytest \
  agent/tests/test_prompts.py \
  agent/tests/test_structure_checks.py \
  agent/tests/test_mock_review_llm.py \
  agent/tests/test_association_methods.py \
  agent/tests/test_generate_chapter.py \
  agent/tests/test_generate_title.py -q --tb=short
```

## 做完写这个文件

路径：`docs/handoffs/EXEC-2.STATUS.md`

```text
status: done
ran: <命令和 pass/fail>
changed: <文件列表>
risk: <一句失败场景>
```

卡住写 `status: blocked`。现在开工。
