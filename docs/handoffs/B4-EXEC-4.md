# 执行4：批次 4 - 回滚仍含表 + 联调测试文件

你是 cmux 同窗口执行会话。不要问确认。读完就改、跑测试、写 STATUS。

## Goal

回滚只把 `versions[k]` 写回 `content`，**不要再拼一次** `state.results`。
另写一份联调测试：写结果章之后，content 含 `treatment_row`；另造处理行时接地失败。

## Hard bar

1. 已有 `versions = [prose+"\n\n"+table, old]` 时，rollback 到 index 1：`content == old`，且若 old 当时已含表则仍含表；**不会**变成 `old + "\n\n" + 当前 results`。
2. 新建测试：`generate_chapter` 结果章（mock LLM 返回一段不含表的散文）后，`treatment_row` 是 content 子串。
3. 新建测试：mock LLM 正文里写 `| treat | 0.9999 |`（或 `| age | 0.9999 |`），再 `check_grounding` → `invented_number`；同文有 `| N | 1200 |`、`| 常数项 | 1.2300 |` 不得单独导致失败。

## 只许改

- `agent/nodes/rollback.py`（仅当它现在会重拼表；当前实现是直接 `content = versions[k]`，多半不用改）
- `agent/tests/test_rollback.py`（补「含表版本回滚不再拼」）
- 新建 `agent/tests/test_results_table_grounding.py`（联调，只测公开函数，不改产品文件）

## 禁止改

`generate_chapter.py`，`review_chapter.py`，`review_sources/grounding.py`，`prompts/*`。
不要为了让联调先绿去改产品代码。产品绿是执行1/2/3的事。你的测试可以暂时红，但 STATUS 里必须写清哪几条红、对应谁。优先把 rollback 单测写绿（不依赖 grounding 新文件也能绿）。

## 测试

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/econpaper
./agent/.venv/bin/python -m pytest \
  agent/tests/test_rollback.py \
  agent/tests/test_results_table_grounding.py -q --tb=short
```

联调用 `make_write_ready_state` + `outline=[{"type":"results","title":"结果"}]`。

## 做完写

`docs/handoffs/B4-EXEC-4.STATUS.md`

```text
status: done
ran:
changed:
risk:
```

若联调因 1/2 未落地而红：`status: done` 仍可写，但 `ran` 里标明哪些红、哪些绿。rollback 单测必须绿。

现在开工。
