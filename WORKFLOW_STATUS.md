# WORKFLOW_STATUS

Last updated: 2026-08-07

## Product identity

**Continuous Empirical Loop** — 全自动实证论文工作台。  
SSOT：`docs/PRODUCT.md` · 入口：`README.md` · Agent：`SOUL.md`

目标：题目+数据 → 无人值守多轮 design→estimate→write→reproduce→revise → 论文包。  
审计/质量门 = 环内刹车，不是品牌。

## Current truth

| 项 | 状态 |
|----|------|
| **主路径** | `runtime/continuous_loop.py` · `scripts/41_quality_loop_2h.py` |
| 内环 runner | `runtime/full_pipeline.py`（10 步；L8 可子集重跑） |
| 写稿 | `runtime/course_paper_builder.py` 优先；路径泄漏硬拒绝 |
| 文献 | `runtime/literature_pack.py`（Crossref）+ `runtime/cnki_client.py`（CNKI CDP） |
| L8 | quality/citation 红 → `next_action` + `target_steps`；**禁**红灯 `completed_green` |
| Demo 题 | `parent_education_wage` |
| 文献核验（demo） | verified_count≈25（Crossref 13 + CNKI 12）；citation_gate passed |
| PDF | `runtime/latex_pdf.py` → `Submissions/{slug}_loop_paper.pdf`（gitignore，可重建） |
| 交接 | `docs/superpowers/handoffs/2026-08-07-continuous-loop-literature-cnki-handoff.md` |
| SPEC | `docs/superpowers/specs/2026-08-07-continuous-loop-literature-cnki-spec.md` |

## Quality residual（诚实）

- 正文已去路径；篇幅与「好论文」质感仍可再抬。  
- CNKI 作者清洗/中文 DOI 仍有边角。  
- OLS ≠ LATE 必须保持。  
- Quality loop 长跑依赖网络与（可选）知网未出 captcha。

## Next（只记一件主线）

稳定「文风红线 + 文献核验」下的多轮 loop，并可选补强 CNKI/写厚。

## How to run

见 `README.md`、`docs/TRY_FULL_PIPELINE.md`、`docs/TRY_CONTINUOUS_LOOP.md`，以及最新 handoff。

## 禁止

- 不要把历史 P-phase BDD / product-control 叙事重新写成产品主线。  
- 不要在正文写仓库路径或假文献。  
- 更新本文件时只写 **现在能交付什么 / 还差什么 / 下一步**。
