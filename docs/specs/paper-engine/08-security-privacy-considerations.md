# Security & Privacy Considerations

> 上级：[econpaper 论文发动机：数字先于正文](../paper-engine.md)


| 威胁 | 严重度 | 机制 |
| --- | --- | --- |
| 客户端 POST 假 `results` | 高 | 忽略 `TRUTH_KEYS`；要 `produced_by` |
| 模型另画表 2 | 高 | prompt 禁止；`treatment_row` 子串；冲突行失败 |
| OLS 写成因果 | 高 | 结构 + mock 评审 + 主张检查在 rubric 前 |
| 0 星仍写正文 | 高 | 任何 type 的就绪检查 |
| 用 `iv_diag` 当主表 | 高 | 主表只许 `ivreg` |
| 微观 CSV 进 LLM | 中 | 只送摘要与工具表 |
| API key 进日志 | 中 | `ssot.py`；错误截断已有 |

---
