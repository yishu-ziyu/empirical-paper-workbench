# 执行4：编号表为空时，综述不得留下作者-年份

你是 cmux 同窗口执行会话。批次 1–5 已收下。本批只改结构检查。
不要问确认。读完就改、跑测试、写 STATUS。

产品根：`/Users/mahaoxuan/Desktop/经济学论文/econpaper`
设计目标 5：文献综述只引用本次检索列表里的 title/DOI/`[N]`。编号表为空则不得用 `(Author, Year)` 编造。

## 现在错在哪

`check_structure` 的 `lit_review` 只查 `[N]` 是否落在 `citation_indices`。表空且正文写 `Smith (2020)`、没有 `[N]` 时，失败列表是 `[]`。prompt 已禁止空表编造，检查层没接上。

## Goal

编号表为空时，作者-年份引用算 `invented_citation`。表里有编号、正文是 `Smith (2020) [1]` 时不要误杀。

## Hard bar

在 `agent/tests/test_structure_checks.py` 追加：

1. `citation_indices` 为 `{}` 或 `None`，正文含 `Smith (2020) 指出……`（无 `[N]`）→ `invented_citation` 在失败列表里。
2. 同样空表，正文只有研究问题、没有作者-年份、也没有 `[N]`（例如 `现有研究尚未回答该问题。`）→ 失败列表 **不含** `invented_citation`。
3. `citation_indices={"10.1/a": 1}`，正文 `Smith (2020) [1] 指出……` → **不含** `invented_citation`（现有 `test_lit_review_invented_citation_fails` 仍要绿：`[99]` 继续失败）。
4. 空表但正文有 `[1]` → 仍失败（旧逻辑，不要弄丢）。

识别作者-年份即可，不要写论文解析器。够用的形状：

- `Name (2020)` / `Name and Name (2020)`
- `(Author, 2020)` / `（张三, 2020）`

不要因为正文出现「2020 年」四个字就失败。

## 只许改

- `agent/nodes/review_sources/structure_checks.py`
- `agent/tests/test_structure_checks.py`

`review_chapter` 已经调用 `check_structure`。不要改 `review_chapter.py`，不要改 `prompts/lit_review.py`，不要改 `grounding.py`。

## 禁止改

`generate_chapter.py`，`review_chapter.py`，`prompts/*`，`grounding.py`，`graph.py`，估计/稳健性。

## 测试

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/econpaper
./agent/.venv/bin/python -m pytest agent/tests/test_structure_checks.py -q --tb=short
```

## 做完写

`docs/handoffs/B6-EXEC-4.STATUS.md`

```text
status: done
ran:
changed:
risk:
```

现在开工。
