# 执行3：批次 4 - 评审节点调用接地

你是 cmux 同窗口执行会话。不要问确认。读完就改、跑测试、写 STATUS。

## Goal

`review_chapter` 在已有主张检查之后，对**结果章**再跑 `check_grounding`。
另造处理系数必须进 `grounding_failures`，综合分封顶并回炉。

## Hard bar

1. 结果章 content 含真 `treatment_row`、没有另造处理行：不因接地失败回退。
2. content 含 `| age | 0.9999 |` 或 `| treat | 0.9999 |` 且与 `estimate.coef` 不同：`grounding_failures` 含 `invented_number`，分数 ≤ 0.50，回退 `current_chapter_index`。
3. 缺 `treatment_row` 子串：含 `missing_estimate_number`，同样封顶回炉。
4. 引言 / 方法章：不因没表而报 `missing_estimate_number`。

## 约定 API（执行1在写，按这个调）

```python
from nodes.review_sources.grounding import check_grounding
# check_grounding(state, content) -> list[str]
```

若执行1尚未落盘，先按此签名调用。模块暂时缺失时不要改签名去迁就。

## 只许改

- `agent/nodes/review_chapter.py`
- `agent/tests/test_review_chapter.py`（只追加接地用例，不要拆掉 1b / 硬条 6）

## 禁止改

`grounding.py`（那是执行1的），`generate_chapter.py`，`rollback.py`，`prompts/*`，`mock_review.py`。

## 机制

在已有 `causal_claim_forbidden` 检查之后（或合并进同一 `grounding_failures` 列表）：

```python
if chapter_type == "results":
    from nodes.review_sources.grounding import check_grounding
    grounding_failures.extend(check_grounding(state, chapter_content))
```

接地码（`invented_number` / `missing_estimate_number` / `invented_table`）与主张码一样：
`score = min(score, CAUSAL_CLAIM_SCORE_CAP)`（0.50），建议里写明失败码，未达迭代上限则回退 idx。

不要解析识别报告。不要改 `call_review_llm` 的 claim 传参（上一波已收下）。

## 测试

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/econpaper
./agent/.venv/bin/python -m pytest agent/tests/test_review_chapter.py -q --tb=short
```

结果章夹具用 `make_write_ready_state`，`current_chapter_index=1`，`body_chapters` 第 0 项 type=results。

## 做完写

`docs/handoffs/B4-EXEC-3.STATUS.md`

```text
status: done
ran:
changed:
risk:
```

现在开工。
