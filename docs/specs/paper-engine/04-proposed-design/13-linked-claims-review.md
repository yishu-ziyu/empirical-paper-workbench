# 关联主张必须在评审栈里关上

> 上级：[Proposed Design](../04-proposed-design.md)


只改 `prompts/methods.py` 不够。同一批改三处，顺序如下。

1. **`causal_claim_forbidden` 在 rubric 之前。** `review_chapter` 在 `call_review_llm` 之前跑接地里的主张检查。命中则 `grounding_failures` 含该码，综合分直接 0.50 封顶并回炉。不等 rubric。

   关联章禁用子串（当作**本文主张**）：`本文识别了因果`、`因果效应显著`、`识别策略成立`、`解决内生性`。允许：`无法做因果识别`、`仅解释为相关`。

2. **`check_structure` 看 `claim_mode`。** `association` 的 methods：仍要求 `$...$` 方程；**不**要求识别假设菜单。`causal_with_caveat`：维持方程 + ≥2 条假设。`star is None` 的 DiD 按 association（与 `claim_mode` 一致），不逼平行趋势词。

3. **`mock_review_llm` 看 `claim_mode`，分数写死。** 签名增加 `claim: str`。`causal_with_caveat` 保持现关键词规则。`association` **不要**沿用 else=0.4（综合分会低于 0.7，硬条 6 必红）。钉死：

   | 维 | 无禁用主张 | 命中 `因果` / `识别策略` / `解决内生性` / `本文识别了因果` |
   | --- | --- | --- |
   | endogeneity | **0.7** | **0.2** |
   | identification | **0.7** | **0.2** |
   | robustness | **0.7**（不要求「稳健」词） | 0.7 |
   | contribution | **0.7**（不要求「贡献」词） | 0.7 |
   | readability | `len>=200` → 0.8；`>=100` → 0.6；否则 0.3 | 同左 |

   命中禁用主张时另写 `causal_claim_forbidden`，综合分封顶 0.50。

4. **方法章权重（association）。** `weights_for_chapter("methods", claim="association")`：`endogeneity=0`, `identification=0.1`, `robustness=0.25`, `contribution=0.25`, `readability=0.4`。代入上表无禁用 + ≥200 字：`0 + 0.07 + 0.175 + 0.175 + 0.32 = 0.74 >= 0.7`。不回炉。

5. **`prompts/methods.py`。** `{claim}` 为 association 时：写相关 / 条件关联；禁止“该策略如何解决内生性”。DiD/IV/RD/SCM 且 `causal_with_caveat` 才写识别假设。

6. **硬条 6 测试夹具（写死）。** 方法章同时满足：(a) `len(content) >= 200`；(b) 含 `$y_i=\\alpha+\\beta D_i+u_i$`；(c) 不含 `因果` / `识别策略` / `解决内生性`。断言：`check_structure == []`；`mock_review_llm` 给出 endogeneity=0.7、identification=0.7；`review_chapter` 综合分 ≥ 0.7；**不**回退 `current_chapter_index`。

`prompts/results.py` SYSTEM 改为：主表已在文末，只解读，禁止再画表，禁止「见表 2」另造基准表。USER 仍给 `{results}` 与 `{robustness_table}` 供解读。

`prompts/lit_review.py`：删除「编号表为空则仍使用 (Author, Year)」。改为：表空则不得编造篇名与年份。

---
