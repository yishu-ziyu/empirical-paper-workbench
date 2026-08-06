# Handoff · 2026-08-07 Continuous Loop + Literature/CNKI

Read this first when re-entering the project.  
Product identity: `docs/PRODUCT.md`. Spec detail: `docs/superpowers/specs/2026-08-07-continuous-loop-literature-cnki-spec.md`.

## One-line status

**Continuous Empirical Loop can produce an academic Chinese OLS paper for `parent_education_wage` with Crossref+CNKI verified bibliography, path-free prose, LaTeX PDF, and a long quality loop.** Causal LATE is still correctly blocked.

## Where things live

| What | Path |
|------|------|
| Outer loop | `runtime/continuous_loop.py` |
| Inner 10 steps | `runtime/full_pipeline.py` |
| Academic writer | `runtime/course_paper_builder.py` |
| Crossref lit pack | `runtime/literature_pack.py` |
| CNKI CDP client | `runtime/cnki_client.py` |
| PDF | `runtime/latex_pdf.py` |
| Evaluator | `runtime/evolve_evaluator.py` |
| 2h/12h runner | `scripts/41_quality_loop_2h.py` |
| CNKI scrape dump | `litreview/cnki/` |
| Combined section | `litreview/parent_education_wage_literature_section.md` |
| Bib | `references.bib` |
| Claim register | `evidence/parent_education_wage_claim_register_full_pipeline.md` |
| Session log | `notes/session-logs/2026-08-07-continuous-loop-style-lit-cnki.md` |
| Status board | `WORKFLOW_STATUS.md` · `Tasks/current-stage.md` |

Generated (often gitignored):  
`Manuscripts/generated/*`, `Results/json/*`, `Submissions/*_loop_paper.pdf`, `state/runs/`, `.hour-loop/`.

## What we shipped this slice

1. **Style fix (user-critical):** manuscript must not contain repo paths / `(证据：tables/…)` / product jargon. Sanitizer + path-leak reject; course builder primary; expand_fallback path appendix killed; evaluator craft fails on path leaks.
2. **Literature:** Crossref seed DOIs (Card/Black/Oreopoulos/China returns etc.) → verified pack + bib + matrix + section.
3. **CNKI:** cookjohn-style CDP search; multi-query; detail scrape; 12 Chinese papers merged; `step_02` re-merges CNKI disk pack so loops do not wipe it.
4. **PDF:** ctexart, rounded table cells, no Continuous Loop author branding / Results/json footer.
5. **Loop:** quality loop can run multi-hour with Grok 4.5.

## Demo numbers (last known good)

- Main OLS: parent_education ≈ 0.059 (se ≈ 0.008), n = 12582, HC1, R² ≈ 0.174.
- Literature: verified_count **25** (Crossref **13** + CNKI **12**).
- PDF rebuild: `Submissions/parent_education_wage_loop_paper.pdf`.

## How to continue in 15 minutes

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板
# 1) rebuild paper from builder + existing facts
PYTHONPATH=. python3 -m runtime.literature_pack   # if network OK
# 2) optional CNKI refresh (needs Chrome CDP :9333)
# 3) continuous loop one shot
PYTHONPATH=. python3 -m Product.cli continuous-loop --help  # check CLI
# or
PYTHONPATH=. python3 -u scripts/41_quality_loop_2h.py --hours 1 --provider grok --model grok-4.5
```

If quality loop was left running:

```bash
# pid file if present
cat .hour-loop/cnki_quality_loop.pid
tail -f .hour-loop/cnki_quality_loop.log
# stop
kill $(cat .hour-loop/cnki_quality_loop.pid)
```

## Hard rules (do not regress)

1. **Body = human academic prose.** Paths and claim IDs stay in register/JSON/replication only.
2. **No fake bibliography.** verified_count=0 ⇒ no author–year masquerade.
3. **OLS ≠ causal.** Keep `causal_claim_allowed=false` for this demo until real IV executes.
4. **Default LLM = Grok 4.5** for real calls (`docs/SETUP_GROK.md`).
5. **Captcha:** pause and ask human; never invent CNKI rows.

## Recommended next work (pick one)

1. **Lit quality:** clean remaining CNKI author strings (e.g. multi-affil bleed); resolve real DOIs for Chinese journals when available; add 2–3 CSSCI hits via advanced search.
2. **Writer:** expand academic thickness without path padding; optional LLM polish only on clean seed.
3. **Product surface:** dashboard tile for verified_count + path-leak + PDF open.
4. **Second topic:** prove loop is not parent_education-only without reviving product-control IA.

## Known debt

- `Tasks/handoff.md` historically deleted with old P-phase docs; this file is the SSOT handoff under `docs/superpowers/handoffs/`.
- Large cleanup of `docs/product-control/*` and old BDD tickets may be in the same working tree; do not resurrect them as product identity.
- Vendor `penguin-harness` is large; treat as reference, not daily edit surface.
- Quality loop may re-Crossref every round (latency/SSL flakes → course builder fallback).

## Done when (next milestone suggestion)

- [ ] PDF abstract + 文献节 pass human read without engineering smell.
- [ ] verified_count stable across loop rounds (CNKI not wiped).
- [ ] One green or explicit residual list with next_action only.
- [ ] Second topic dry-run or dashboard shows loop status without CLI archaeology.
