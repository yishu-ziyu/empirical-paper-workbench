# Current stage

**Product**: Continuous Empirical Loop（全自动实证论文工作台）  
**SSOT**: `docs/PRODUCT.md`  
**Updated**: 2026-08-07

## Now

主路径已具备：

- 10 步内环 + 外环 continuous loop + LaTeX PDF  
- 正文学术化（禁止路径/证据戳）  
- 文献：Crossref DOI + CNKI 页面核验（demo `parent_education_wage` verified_count≈25）  
- 因果语言对 OLS demo 仍关闭  

## Next（只记一件主线）

在不回退文风红线的前提下，把文献中文侧与写厚质量再抬一轮（CNKI 作者/DOI 清洗 + 学术扩写），并让 quality loop 多轮后 verified_count 稳定不丢 CNKI。

## Run

```bash
# 文献包
PYTHONPATH=. python3 -m runtime.literature_pack

# 质量环（Grok 4.5）
PYTHONPATH=. python3 -u scripts/41_quality_loop_2h.py --hours 1 --provider grok --model grok-4.5

# CNKI（需 Chrome CDP :9333）
# 见 docs/superpowers/handoffs/2026-08-07-continuous-loop-literature-cnki-handoff.md
```

## Docs for re-entry

- Spec: `docs/superpowers/specs/2026-08-07-continuous-loop-literature-cnki-spec.md`
- Handoff: `docs/superpowers/handoffs/2026-08-07-continuous-loop-literature-cnki-handoff.md`
- Log: `notes/session-logs/2026-08-07-continuous-loop-style-lit-cnki.md`

## Not this stage

- 不恢复 P0–P18 / product-control 叙事。  
- 不把 OLS 写成 LATE。  
- 不在正文写仓库路径。
