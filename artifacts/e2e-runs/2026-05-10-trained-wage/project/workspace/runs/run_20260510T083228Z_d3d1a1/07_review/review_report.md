# Review Report

## Review Object

- mode: dry-run
- source_markdown: section-assembled
- source_policy: sections_v21 and 论文v2.1_完整版.md are the current writing sources; word_hqu_format is an export-chain source.

## Decision

revise_major

## Findings

- P0 source_of_truth: 写作源必须以 sections_v21 或 论文v2.1_完整版.md 为准，word_hqu_format 只作为旧 Word 导出链参考。
- P1 concept_boundary: 匹配效率、匹配质量代理、技能岗位错配三层边界需要在摘要、文献述评和结论中保持一致。
- P1 clds_causal_rank: CLDS 机制结果不是 Bartik IV 主识别，必须写成补充机制证据，不能和 CFPS+Bartik IV 同等因果等级。
- P1 bartik_exclusion_boundary: Bartik 排他性需要说明产业结构可能反映制造业基础、开放程度和发展路径，不能写成天然外生。
- P1 result_claim_alignment: 每个核心结论需要挂到表格、图形或结果索引。

## Checks

- P0 source_of_truth: FAIL - 写作源必须以 sections_v21 或 论文v2.1_完整版.md 为准，word_hqu_format 只作为旧 Word 导出链参考。
- P1 concept_boundary: FAIL - 匹配效率、匹配质量代理、技能岗位错配三层边界需要在摘要、文献述评和结论中保持一致。
- P1 weak_iv_caution: PASS - Bartik IV 需要保留第一阶段和弱 IV 口径，不能写成已经彻底解决。
- P1 clds_causal_rank: FAIL - CLDS 机制结果不是 Bartik IV 主识别，必须写成补充机制证据，不能和 CFPS+Bartik IV 同等因果等级。
- P1 bartik_exclusion_boundary: FAIL - Bartik 排他性需要说明产业结构可能反映制造业基础、开放程度和发展路径，不能写成天然外生。
- P1 result_claim_alignment: FAIL - 每个核心结论需要挂到表格、图形或结果索引。
- P2 part_time_zero_result: PASS - 兼职变量如果不显著，不能反向解释为支持正规就业导向。
- P2 reference_completeness: PASS - 参考文献不能保留“暂无中文核心文献，待补充”等未完成标记。

## Revision Requests

- 写作源必须以 sections_v21 或 论文v2.1_完整版.md 为准，word_hqu_format 只作为旧 Word 导出链参考。
- 匹配效率、匹配质量代理、技能岗位错配三层边界需要在摘要、文献述评和结论中保持一致。
- CLDS 机制结果不是 Bartik IV 主识别，必须写成补充机制证据，不能和 CFPS+Bartik IV 同等因果等级。
- Bartik 排他性需要说明产业结构可能反映制造业基础、开放程度和发展路径，不能写成天然外生。
- 每个核心结论需要挂到表格、图形或结果索引。
