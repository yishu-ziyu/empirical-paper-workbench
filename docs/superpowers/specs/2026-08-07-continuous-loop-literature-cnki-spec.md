# SPEC · Continuous Loop 论文成文 + 文献核验（含 CNKI）

Date: 2026-08-07  
Status: active  
Demo topic: `parent_education_wage`  
Product SSOT: `docs/PRODUCT.md`

## Goal

把 Continuous Empirical Loop 从「能跑通 10 步 + REPRO」推进到：

1. **人读得进的中文应用微论文**（非工程审计日志）。
2. **文献可核验再进正文**（Crossref DOI + CNKI 页面核验）。
3. **证据绑定留在复现侧**，正文不写仓库路径。
4. **外环可多轮 evaluate → learn → package**，质量环可无人值守跑。

## Non-goals

- 不恢复 P0–P18 / product-control 朝代叙事。
- 不在正文宣称已闭合 IV/LATE 因果（demo 仍是 OLS+HC1 关联）。
- 不自动解知网滑块验证码；遇 captcha 等人手。
- 不把 `vendor/penguin-harness` 大改当本切片目标。

## Architecture (current)

```text
Product.cli / scripts/41_quality_loop_2h.py
        │
        ▼
runtime/continuous_loop.py          # outer: propose→run→evaluate→learn↻→package
        │
        ▼
runtime/full_pipeline.py            # inner 10 steps
  02_literature → literature_pack (+ merge CNKI disk pack)
  05_causal     → OLS+HC1, tables/
  06_writing    → course_paper_builder (primary) + optional LLM polish
  08_citation   → citation_gate from verified_count
  09_replication→ REPRO_OK
        │
        ▼
runtime/latex_pdf.py → Submissions/{slug}_loop_paper.pdf
runtime/evolve_evaluator.py → state/evolve_archive/
```

## Acceptance criteria

### A. Manuscript style (hard)

Given a generated `Manuscripts/generated/{slug}_full_pipeline_paper.md`  
When a human reads the body  
Then:

- No `tables/` / `Results/` / `(证据：…)` / claim register / Continuous Loop jargon in prose.
- Tables referred as 表1/表2; coefficients use readable decimals.
- Path/product tokens only in claim register / JSON / replication.

### B. Literature verification (hard)

Given `step_02_literature`  
When Crossref resolves seed DOIs and optional CNKI pack exists on disk  
Then:

- `Results/json/{slug}_literature_pack.json` has `verified_count >= 1`.
- `Results/json/{slug}_full_pipeline_citation_gate.json` status is `passed` iff verified_count > 0.
- Body may use author–year only for verified entries.
- `references.bib` rebuilt from verified works.
- CNKI entries marked `cnki_page_verified` (not invented).

### C. CNKI client

Given Chrome CDP on `http://127.0.0.1:9333` (or configured)  
When running multi-query search via Playwright  
Then:

- Results land under `litreview/cnki/`.
- Captcha returns `error: captcha` and does not invent papers.
- `step_02` merges `litreview/cnki/cnki_{slug}_verified.json` or default parent_education pack without wiping Crossref.

### D. Continuous loop honesty

Given L8 quality red  
When package is written  
Then status is not `completed_green`; `next_action` + `target_steps` present.

Given OLS demo  
When writing conclusions  
Then causal LATE / policy effect language is blocked (`causal_claim_allowed=false`).

## Key modules

| Path | Role |
|------|------|
| `runtime/full_pipeline.py` | 10-step runner; writing sanitize; lit merge |
| `runtime/course_paper_builder.py` | Deterministic academic Chinese body |
| `runtime/literature_pack.py` | Crossref DOI verify + bib/matrix/section |
| `runtime/cnki_client.py` | CNKI search over CDP (cookjohn-style) |
| `runtime/latex_pdf.py` | Markdown → ctexart PDF; no path footer |
| `runtime/continuous_loop.py` | Outer loop + package |
| `runtime/evolve_evaluator.py` | Score; path-leak kills craft |
| `scripts/41_quality_loop_2h.py` | Multi-hour outer runner |

## Demo evidence (as of 2026-08-07)

| Artifact | Note |
|----------|------|
| verified_count | 25 (Crossref 13 + CNKI 12) |
| PDF | `Submissions/parent_education_wage_loop_paper.pdf` (gitignored; rebuildable) |
| Lit section | Crossref classics + 知网补充段 |
| Claim C4 | literature bound when verified_count > 0 |

## Commands

```bash
# Literature only
PYTHONPATH=. python3 -m runtime.literature_pack

# CNKI (Chrome CDP must be up)
# Google Chrome --remote-debugging-port=9333 --user-data-dir=$HOME/.cache/cnki-chrome-profile-9333
PYTHONPATH=. python3 -c "from runtime.cnki_client import search_queries; search_queries(['父母教育 子女收入'])"

# Full pipeline writing without LLM
PYTHONPATH=. python3 - <<'PY'
from runtime.full_pipeline import FullPaperPipeline
# or continuous loop / quality loop
PY

# Quality loop (long)
PYTHONPATH=. python3 -u scripts/41_quality_loop_2h.py --hours 12 --provider grok --model grok-4.5
```

## Open risks

1. CNKI captcha blocks unattended re-scrape.
2. LLM polish can reintroduce path leaks → must reject and keep builder.
3. `step_02` re-Crossref every loop (network); offline fallback not fully hardened.
4. Substance score still rewards length; craft now penalizes paths but style ≠ “long”.
5. Author-name cleaning for CNKI affiliations still imperfect for multi-affil strings.

## Next product steps (ordered)

1. Harden CNKI author cleaning + optional DOI resolve for CNKI journals.
2. Wire quality loop learn_notes to expand academic thickness without paths.
3. Optional: Zotero export path from `cnki-export` skill.
4. Dashboard shows verified_count / path-leak flag next to PDF.
5. Second demo topic without reintroducing product-control IA.
