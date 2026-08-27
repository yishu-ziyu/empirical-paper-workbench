# 执行1：批次 4 - 接地函数（只写 grounding 模块）

你是 cmux 同窗口执行会话。批次 1–3 和 Crossref 已收下。本批做结果章数字接地。
不要问确认。读完就改、跑测试、写 STATUS。

## Goal

新增纯函数：判断结果章正文有没有主估计那一行，有没有另造处理系数。

## Hard bar

`check_grounding(state, content)` 返回失败码列表：

1. `estimate.treatment_row` 不是 `content` 的子串 → 含 `missing_estimate_number`
2. 正文另有一行 `| treat | 0.9999 |`（或处理变量名）且与 `estimate.coef` 绝对差 > 1e-4 → 含 `invented_number`
3. 同一夹具里还有 `| N | 1200 |` 和 `| 常数项 | 1.2300 |` → **不得**因此失败
4. 不解析 `identification_diag.report` 里的小数

## 约定 API（执行3/4会按这个调，不要改名）

```python
# agent/nodes/review_sources/grounding.py
def check_grounding(state: dict, content: str) -> list[str]:
    """Return zero or more of:
    missing_estimate_number, invented_number, invented_table
    """
```

规则（设计原文，照做）：

- `invented_number` 只打处理行。正则找 `| <label> | <float> |`。
- 规范化 label 属于 `{estimate.treatment, ATT, RD, SCM_gap}`（大小写不敏感；`treat` / `treatment` 视为 `estimate.treatment` 的别名）**并且**该行第一个 float 与 `estimate.coef` 差 > 1e-4，才记 `invented_number`。
- 不标记：`N`、`观测`、`常数项` / `intercept` / `_cons`、控制变量行、稳健性里其它聚类水平行。
- 可选：正文出现**第二张**完整表头 `| 变量 | 系数 | SE | p |`（工具表那一张之外）→ `invented_table`。
- `estimate.status != "ok"` 或没有 `treatment_row`：不要误报 invented_number；缺行时只报 `missing_estimate_number`（若本应有主表）。结果章以外也可被调用：没有 treatment_row 则返回 `[]`，不要对引言乱报。

建议：仅当 `chapter` 不在 state 或调用方传入的是结果章正文、且 `estimate.status=="ok"` 时检查 missing。函数签名只有 `(state, content)`。实现：若没有 `estimate.treatment_row`，返回 `[]`。有 treatment_row 但不在 content 里 → `missing_estimate_number`。

## 只许改

- 新建 `agent/nodes/review_sources/grounding.py`
- 新建 `agent/tests/test_grounding.py`

## 禁止改

`generate_chapter.py`，`review_chapter.py`，`rollback.py`，`prompts/*`，`estimate.py`，其它测试。

## 测试

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/econpaper
./agent/.venv/bin/python -m pytest agent/tests/test_grounding.py -q --tb=short
```

夹具用 `conftest.make_write_ready_state`。`treatment_row` 现为 `| age | 0.1234 | 0.0456 | 0.0078 |`，`treatment=age`，`coef=0.1234`。

必须覆盖：真表过关；缺行失败；`| age | 0.9999 |` 或 `| treat | 0.9999 |` 失败；N / 常数项不过度杀。

## 做完写

`docs/handoffs/B4-EXEC-1.STATUS.md`

```text
status: done
ran:
changed:
risk:
```

现在开工。
