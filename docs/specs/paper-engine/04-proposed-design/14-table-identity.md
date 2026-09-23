# 表同一：`treatment_row` + 文末工具表

> 上级：[Proposed Design](../04-proposed-design.md)


`generate_chapter` 在 `type=="results"` 且估计 `status=="ok"` 时：

```python
prose = call_llm(system, user)
table = state["results"]
content = prose + "\n\n" + table
versions = [content] + existing_versions
```

`versions[0]` **定义为** `prose + "\n\n" + results`。rollback 取旧 `versions[k]`，那一串已含表，不要再拼一次。regenerate 重新 `call_llm` 再拼当前 `state.results`。

接地（`review_sources/grounding.py`）：

1. `estimate.treatment_row` 是 `content` 的子串。否则 `missing_estimate_number`。  
2. **`invented_number` 只打处理行。** 正则找 `| <label> | <float> |`。仅当规范化后的 label 属于 `{estimate.treatment, ATT, RD, SCM_gap}`（大小写不敏感；`treat`/`treatment` 视为 `estimate.treatment` 的别名）**并且**该行第一个 float 与 `estimate.coef` 的绝对差 **> 1e-4**，才记 `invented_number`。  
   **不**标记：`N`、`观测`、`常数项` / `intercept` / `_cons`、控制变量行、稳健性里其它聚类水平行。  
   可选附加：正文出现**第二张**完整表头 `| 变量 | 系数 | SE | p |`（工具表那一张之外）→ `invented_table`。  
3. 不解析识别报告里的 3 位小数。

测试：mock LLM 输出第二张 `| treat | 0.9999 |` 且与 `treatment_row` 不同 → `invented_number`。夹具里同时有 `| N | 1200 |` 和 `| 常数项 | 1.2300 |` → **不得**失败。

---
