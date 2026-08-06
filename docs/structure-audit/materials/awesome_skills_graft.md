# Awesome Agent Skills → Empirical Paper Workbench · Graft Notes

Date: 2026-08-06  
Sources (read in full for this note):

| Tree | Path under `Awesome-Agent-Skills-for-Empirical-Research/skills/` |
|------|------------------------------------------------------------------|
| 08 | `08-ndpvt-web-latex-document-skill` |
| 27 | `27-dariia-m-my_claude_skills` (`dont-lie`, `academic_writing`, `paper_verification`, `econ_intro_writing`) |
| 04 | `04-K-Dense-AI-claude-scientific-writer` (`scientific-writing`, `literature-review`, `peer-review` + `WRITER.md`) |
| 41 | `41-sticerd-eee-sewage-econometrics-check` (focus: `econometrics-check`; also `identify`, `audit-replication`, `validate-bib`, `paper-excellence`) |

Target repo today:

- Skills on disk: only `.claude/skills/integrity-audit/`
- Evidence gates: `evidence/integrity_audit.py`, quality report `evidence_integrity_*`, `REPRO_OK`
- Pain (live E2E): `too_thin`, `evidence_integrity_blocked`, design registers IV but run is OLS-only, literature `verified=0`

**Graft rule:** copy *mechanisms and checklists*, not sewage-project paths, not biomedical mandatory graphics, not “complete entire thesis in one shot” policies.

```text
  优先级:  integrity/numbers  >  ID-code align  >  lit verify  >  writing structure  >  latex package
  落点:    skill 瘦身 + gate 代码 + step contract + 可选 compile 工具
  不做:    整仓 vendoring、平行第二套 manuscript 栈、AI 配图硬配额
```

---

## 0. Map: which source owns which product problem

| Product problem | Best donor | Already have | Graft action |
|-----------------|------------|--------------|--------------|
| Fabricated numbers / citations / APIs | 27 `dont-lie` | partial integrity dimensions | Always-on thin policy + pre-present checklist |
| Section invents coeffs / design drift | 27 `paper_verification` + integrity-audit | 6-dim audit, post_tool hook | Manifest + table audit phases; harden gate |
| Intro thin / wrong lit order | 27 `econ_intro` + `academic_writing` | section word gates | Intro blueprint + causal language rules |
| Lit list not verified | 04 lit-review verification + 41 `validate-bib` | citation quality fields | DOI/Crossref verify + missing-key scan |
| ID claim ≠ code | 41 `econometrics-check` / `identify` | method gate narrative | 4-phase design audit on strategy+scripts |
| Package / REPRO incomplete | 41 `audit-replication` + 27 phase 6 | `REPRO_OK` script print | 10-check replication package |
| Prose is outline not paper | 04 scientific-writing + 27 academic_writing | too_thin verdict | Two-stage write; claim–support–implication |
| PDF/export polish | 08 latex-document | export preflight | Compile+preview scripts only when packaging |
| Pre-submit scoreboard | 41 `paper-excellence` | quality JSON multi-verdict | Weighted score + single priority fix list |

---

## 1. 27 · dont-lie (anti-hallucination) — **P0 always-on**

### Steal (keep short)

1. **Never guess under ~90% confidence** — verify by reading files / running code / searching docs, not “think harder”.
2. **Read before write** — data columns, existing scripts, package APIs, paths.
3. **Run and fix** — do not deliver unexecuted analysis code as “should work”.
4. **Never invent** functions/args, paths, columns, citations, coeffs, p-values, sample sizes, URLs.
5. **Copy numbers from actual output** — no silent re-rounding chains in prose.
6. **Post multi-step verify** — merge N before/after; NA introduction; magnitude sanity.
7. **Pre-present checklist** (binary gates for agent turn end):
   - [ ] Code executed (or explicitly untested)
   - [ ] Paths exist
   - [ ] Functions/args real
   - [ ] Columns real
   - [ ] Numbers match run output
   - [ ] No invented citations
   - [ ] Uncertainty labeled

### Drop / rewrite

- R-only package confusion tables → extend with Python (`statsmodels` vs `linearmodels` vs custom OLS) and Stata if used.
- “ALWAYS activate” as entire skill dump → one **policy file** progressive-disclosed, not full skill each turn.

### Where to land

| Artifact | Path suggestion |
|----------|-----------------|
| Always-on skill | `.claude/skills/dont-lie/SKILL.md` (≤120 lines) |
| Agent policy line | `SOUL.md` / agent system: “numbers & citations only from evidence spine” |
| Hook | Already: post_tool on `Manuscripts/sections/*.md`; add same spirit to **results JSON → prose** writers |
| Gate | Map checklist items into `evidence_integrity_checks` failures |

### Acceptance

- Agent cannot write main-results magnitudes without binding to a results artifact path.
- Falsifier: invent a coefficient in draft → integrity or claim gate **BLOCKED**.

---

## 2. 27 · paper_verification — **P0 evidence spine**

### Steal: six phases as product contracts

```text
Phase1 Discovery     → inventory scripts / outputs / paper / data
Phase2 Table Audit   → every table cell vs generator output
Phase3 Inline Claims → body magnitudes vs tables/outputs
Phase4 Code Review   → pipeline + modeling + red flags
Phase5 Manifest      → verification_manifest.json claim graph
Phase6 Replication   → automated compare script + PASS/FAIL report
```

### Steal: tolerances (port to Python)

| Value | Rule |
|-------|------|
| coef / SE | match displayed decimals after rounding |
| N | exact |
| R² | displayed precision |
| t/z | recompute from coef/SE ±0.01 |
| % | recompute; ±0.1pp |
| Manual LaTeX tables | highest risk; flag always |

### Steal: claim ID scheme

- `T1_R2_C3`, `T1_N`, `BODY_S4_P2_S3`, `ABS_1`, `FN_12`, `APP_T_A1_...`
- Chain: **paper claim → table/figure → output file → script → data**

### Steal: common pitfalls (encode as automated or review prompts)

- Stale outputs (code mtime > output mtime)
- SE type mismatch (paper says cluster, code HC1)
- FE / clustering level mismatch vs prose
- Join row explosion
- Silent NA drop → N wrong
- Significance star definition ≠ footnote
- pp vs percent wording
- Hardcoded cutoffs undocumented
- Commented-out “winner” specs (p-hacking smell)

### Drop

- Assume R + stargazer only → support this repo’s actual table emitters (Python/JSON → markdown/LaTeX).
- Force writing full `tests/verify_replication.R` → prefer **Python** `tests/` + existing `REPRO_OK` entrypoints; keep JSON manifest language-agnostic.

### Where to land

| Piece | Land |
|-------|------|
| Manifest schema | `evidence/verification_manifest.schema.json` + writer in full_pipeline / manuscript step |
| Table audit | extend `evidence/integrity_audit.py` (Number Anchoring already partial) with **file-backed** expected values |
| Phase 1 inventory | run workspace `inventory.json` at start of verify step |
| Phase 6 | grow `replication/*` beyond print `REPRO_OK` to claim-level asserts |
| Skill | `.claude/skills/paper-verification/SKILL.md` pointing at scripts, not re-teaching phases in prose only |
| Skill trigger | `/integrity-audit` full mode OR pre-§5/§6 draft (already in integrity-audit description) |

### Concrete graft tickets

1. **Manifest v0:** for E2E parent_education_wage, emit one claim `T_MAIN_parent_education` with `paper_value`, `expected_value`, `source_script`, `tolerance`, `status`.
2. **Stale output check:** fail verify if regression script newer than results JSON without re-run.
3. **Design-vs-run drift:** if design registers IV and only OLS ran → `evidence_integrity_blocked` (matches live red; make explicit rule).
4. **Inline claim scan:** regex magnitudes + “significant at” in `Manuscripts/sections/*.md` must resolve to manifest IDs or UNVERIFIED.

### Acceptance

- Quality report includes `claims_passed / failed / unverified` counts.
- Falsifier: change one table number without re-run → FAIL.

---

## 3. 27 · academic_writing + econ_intro — **P1 manuscript structure**

### Steal: economics section order (default applied micro)

Title → Abstract → Intro → (Institutional bg if needed) → Data → Empirical strategy → Main results → Mechanisms/heterogeneity → Robustness → Conclusion → Refs → Appendix.

No standalone “conceptual framework” section unless theory paper.

### Steal: writing mechanics

- Paragraph: **claim → support → implication**; one claim per paragraph; 3–7 sentences.
- Causal language **matched to design** (RCT/QE: effect/increases; correlational: associated with).
- Placeholders when unknown: `[MAIN EFFECT]`, `[CITATION NEEDED]`, never fake numbers.
- Templates are **scaffolds only** — always rewrite; offer 2–4 phrasings.
- Results paragraphs: introduce table → walk columns → economic magnitude vs baseline → transition.
- “Insignificant ≠ zero effect” → “imprecisely estimated / cannot reject zero”.
- Table notes: SE type, clustering, sample, stars definition.
- Short paper rules (≤5k words, ≤5 main display items) if product has short mode.

### Steal: intro skeleton (Evans / Head / Sahm aligned)

1. Motivation / puzzle (1–2¶) — **not** lit dump  
2. Research question (1¶) — specific estimand language  
3. Empirical approach (1¶)  
4. Results with magnitudes (3–4¶)  
5. Value-added vs closest lit (1–3¶) — **after** results  
6. Optional policy / limits  
7. Short roadmap  

Checklist: care? question clear? ID visible? magnitudes? YOUR work front-loaded? ≤ ~5 pp double-spaced equivalent? non-specialist can state contribution?

### Drop

- Forcing 10–15 top-journal paragraphs on every auto draft (will worsen `too_thin` vs quality if agent pads fluff).
- Copy-paste sentence banks into manuscript.

### Where to land

| Piece | Land |
|-------|------|
| Section contracts | already 9 section names in integrity-audit — align word targets with academic_writing short/regular |
| Skill | `.claude/skills/econ-academic-writing/SKILL.md` (merge intro + section scaffolds) |
| ManuscriptAgent prompt | two-stage: outline → prose; ban bullet finals in §intro/results/conclusion |
| Quality | keep `too_thin` but add **structure checklist** (question early, results in intro, causal verbs) as soft then hard |

### Acceptance

- Auto intro contains question + design + ≥1 magnitude bound to evidence, or placeholders explicit.
- Causal verb audit fails if OLS-associational run uses “causes/increases” without design flag.

---

## 4. 04 · scientific-writing / literature-review / peer-review — **P1–P2 selective**

### Steal from scientific-writing

- **Two-stage process:** outline with research-lookup → full paragraphs (never ship bullets as manuscript).
- IMRAD awareness (map to econ outline above; do not replace econ order with generic IMRAD blindly).
- Draft order: tables/figures spine → methods/strategy → results → discussion/robustness → intro → abstract last.
- Citation metadata completeness (volume, pages, DOI) before package.
- Reporting guidelines **as optional checklists** when design matches (STROBE for observational; not CONSORT by default).
- Venue adaptation as later layer (field journal applied micro default).

### Steal from literature-review

- Search **documented**: database, date, query string, hit count (reproducible lit step).
- Dedup by DOI then title.
- Screen stages: title → abstract → full text; keep exclude reasons.
- **Thematic synthesis**, not paper-by-paper laundry list (aligns with academic_writing §8).
- **Citation verification step** (DOI resolve / Crossref) — critical for `verified=0`.
- Citation chaining (forward/backward) for gap framing.
- Multi-source: for econ prefer RePEc/IDEAS, Google Scholar, NBER, SSRN, OpenAlex/Semantic Scholar — **not** PubMed-first.

### Steal from peer-review

- Report shape: summary → major → minor → questions; constructive tone.
- Stages usable as **internal ReviewGates**: soundness, stats, reproducibility, figure integrity, overclaim scan.
- Red flags: overstated conclusions, causal from correlational, missing limitations, selective reporting.
- Presentation review: **PDF → images → inspect** (same as latex skill) — useful for export QA.

### Drop hard

- Mandatory graphical abstract + 5–8 AI figures for every empirical paper (wrong field norms; wastes run; conflicts with evidence-first).
- Parallel API / `PARALLEL_API_KEY` as sole web stack (repo has its own LLM/search wiring).
- “Complete 100% without stopping / unlimited tokens” WRITER policy (conflicts with step budgets and L8 loop).
- Biomedical database skill graph (gget, bioservices) unless topic is health-econ micro with those sources.
- Nature/Cell venue cosplay as default.

### Where to land

| Piece | Land |
|-------|------|
| Lit verify tool | `evidence/verify_citations.py` or step in literature pipeline; fill `verified` counts |
| Lit skill | `.claude/skills/literature-review-econ/SKILL.md` (thematic + verify; search log in run dir) |
| Peer review skill | `.claude/skills/peer-review-internal/SKILL.md` used by ReviewGates / paper excellence |
| sources/ audit trail | optional `runs/<id>/sources/` for search dumps (idea from WRITER.md) without forcing Parallel |

### Acceptance

- Literature step cannot exit green with `verified=0` if citations claimed.
- ReviewGates emit major/minor list compatible with `recommended_next_tasks`.

---

## 5. 41 · econometrics-check (+ identify, audit-replication, validate-bib, paper-excellence) — **P0–P1**

### Steal: 4-phase causal audit (generalize off sewage)

```text
Phase1 Claim ID   → design class, estimand, treatment, comparison
Phase2 Validity   → assumptions + threats per design family
Phase3 Inference  → SE/cluster/multiplicity + code-theory align
Phase4 Polish     → robustness plan, sensitivity, citation fidelity
Early stop if Phase2 CRITICAL
```

Design family checklist to **parameterize** (not hardcode spills):

| Family | Must check |
|--------|------------|
| OLS / selection on observables | controls/FE sufficiency, OVB narrative honesty |
| DiD / event study | parallel trends stated+tested; staggered adoption |
| IV | relevance, exclusion threats, first-stage F, LATE language |
| RDD | continuity, manipulation, bandwidth |
| FE / panel | within variation, time-varying confounders |
| Matching / weighting | common support, balance |

### Steal: identify skill memo as **Method Gate artifact**

Strategy memo fields:

1. Design + estimand (ATT/ATE/LATE)  
2. Estimating equation + symbol defs  
3. Assumptions + defenses  
4. Pseudo-code for implementation  
5. Ordered robustness plan  
6. Falsification tests (expected nulls)  
7. Top referee objections + replies  

**Contract:** approved memo is what analysis scripts must implement; mismatch → integrity fail.

### Steal: audit-replication 10 checks

1. Script syntax  
2. File references resolve  
3. No orphan scripts/outputs  
4. Output freshness  
5. Inventory + master entrypoint  
6. Dependencies locked/documented  
7. Data provenance  
8. Path hygiene (no absolute `setwd`)  
9. Every table/figure → script  
10. README (AEA-shaped)

Map 4+9+10 onto existing `REPRO_OK` and export package gates.

### Steal: validate-bib workflow

- Extract cite keys from md/tex  
- Missing keys CRITICAL  
- Unused informational  
- Fuzzy typo keys  
- Entry quality (author/title/year/journal)

### Steal: paper-excellence aggregation

Weights (adapt): Econometrics 30% · Manuscript 35% · Code 15% · Bib 5% · Polish 15%.  
Single priority fix list; gate bands (≥90 submit / ≥80 commit / &lt;80 block).  
Parallel agents OK only if real separate IO (book H7); else sequential tools same process.

### Drop

- Sewage paths (`docs/overleaf`, spill radii, LSOA, PostGIS).
- Project-specific treatment variable names in skill body → inject from run’s design JSON.
- R+fixest as only stack → Python OLS/HC1 and future adapters.

### Where to land

| Piece | Land |
|-------|------|
| Skill | `.claude/skills/econometrics-check/SKILL.md` + `references/design_families.md` |
| Method step | design run plan / method gate writes `strategy_memo.md` |
| Gate | `code_theory_align` in quality JSON: paper claims design D, execution log methods M |
| Replication | expand package audit checklist in `docs/workflows/reproducibility-skill-contract.md` |
| Bib | wire validate-bib into literature + export preflight |
| Excellence | optional `scripts/*_paper_excellence.py` wrapping existing quality JSON |

### Acceptance

- Live bug class fixed: **IV in design, OLS only in run** → blocked with explicit repair task “align design registry or run IV”.
- Falsifier: change clustering in code not in strategy section → Phase3 FAIL.

---

## 6. 08 · latex-document-skill — **P2 package/export only**

### Steal

- Compile wrapper: engine auto-detect (CJK → xelatex), latexmk multi-pass, bibtex/biber, `--preview` PNG pages, `--pdfa` optional, quiet/verbose.
- **Never review PDF as text** — `pdftoppm` / pdf-to-images then visual inspect (shared with peer-review presentations).
- Long-form anti-patterns: prose over bullet walls; escape text-mode `<>`; limit needless `\newpage`; figures ~0.75–0.85 textwidth.
- Scaling OCR/conversion only if product does PDF→tex (not core E2E today).
- Bib fetch by DOI utility when packaging.
- latexdiff for revision packages (nice-to-have).

### Drop

- 50+ document types, ATS resumes, mail merge, fillable forms, cheat sheets as always-on skill surface.
- Auto-install full texlive from agent (ops risk); document deps in SETUP instead.
- Competing manuscript authoring stack beside `Manuscripts/sections/*.md`.

### Where to land

| Piece | Land |
|-------|------|
| Scripts | `tools/latex/compile_latex.sh`, `pdf_to_images` if not present |
| Export step | full_pipeline / export package: md→tex→pdf optional path |
| Skill | thin `.claude/skills/latex-compile/SKILL.md` triggered only on export/PDF QA |

### Acceptance

- `Product.cli` export can produce PDF + page previews when tex template present.
- Falsifier: CJK manuscript compiles with xelatex path documented.

---

## 7. Progressive skill tree for this repo (recommended)

Do **not** load all donor skills every turn. Stage by pipeline step:

```text
Always:     dont-lie (thin)
Intent:     econ-academic-writing (outline only)
Literature: literature-review-econ + validate-bib rules
Method:     econometrics-check + identify memo
Execution:  dont-lie + code-run verify
Results:    paper-verification phases 2–3
Manuscript: econ-academic-writing + scientific two-stage
Review:     peer-review-internal + integrity-audit --all
Package:    audit-replication checks + latex-compile
```

Maps to progressive disclosure (book H3) and existing 10-step spine.

---

## 8. Priority implementation order (actionable)

### Wave A — stop integrity reds (this week)

1. Add `.claude/skills/dont-lie/SKILL.md` (rules 1–10 compressed + pre-present checklist).  
2. Extend quality gate: **design methods ⊆ executed methods**; else `evidence_integrity_blocked`.  
3. Emit `verification_manifest.json` v0 from full_pipeline with main coef claim(s).  
4. Citation verify pass: DOI/metadata or mark unverified; block “ready” if claimed cites verified=0.

### Wave B — writing thickness without fabrication

5. `.claude/skills/econ-academic-writing/SKILL.md` (intro blueprint + section scaffolds + causal language).  
6. ManuscriptAgent: outline→prose; placeholders for missing evidence; bind results section to manifest IDs.  
7. Intro must include magnitudes only if manifest PASS; else placeholder + gap honesty (integrity Gap Honesty dim).

### Wave C — econometrics + package

8. `.claude/skills/econometrics-check/SKILL.md` generalized 4-phase + design_families.  
9. Method gate writes strategy_memo; execution must read it.  
10. Replication package 10-check script; upgrade `REPRO_OK` to claim-level where possible.

### Wave D — export polish

11. Thin latex compile + pdf page image QA.  
12. Optional paper-excellence aggregator over existing quality JSON.

---

## 9. Explicit non-goals (anti-graft)

- Vendoring full Awesome trees into `.claude/skills` (noise, license copy surface, wrong defaults).  
- Biomedical figure quotas / graphical abstract mandatory.  
- Sewage-house-prices path constants.  
- Second orchestrator “writer OS” (`writing_outputs/` only) parallel to full_pipeline.  
- Methodology slogan skills without binding to gates (map ≠ territory).  
- Replacing `integrity-audit` — **extend** it; keep post_tool hook.

---

## 10. Traceability: donor → repo file (target state)

| Donor | Target skill / code |
|-------|---------------------|
| 27 dont-lie | `.claude/skills/dont-lie/SKILL.md` |
| 27 paper_verification | `.claude/skills/paper-verification/` + `evidence/verification_manifest*` + replication asserts |
| 27 academic_writing + econ_intro | `.claude/skills/econ-academic-writing/SKILL.md` |
| 04 scientific-writing (subset) | same writing skill + two-stage policy in ManuscriptAgent |
| 04 literature-review (verify/thematic) | lit step + `evidence/verify_citations.py` |
| 04 peer-review (report shape) | ReviewGates / `.claude/skills/peer-review-internal/` |
| 41 econometrics-check + identify | `.claude/skills/econometrics-check/` + strategy_memo in method gate |
| 41 audit-replication | package/REPRO checks |
| 41 validate-bib | export + lit preflight |
| 41 paper-excellence | quality aggregator script |
| 08 latex-document | `tools/latex/*` + export-only skill |
| existing | `.claude/skills/integrity-audit/` remains SSOT for section 6-dim audit |

---

## 11. One-line graft thesis

**Wire donor checklists into evidence gates and thin progressive skills; keep economics structure and causal honesty; leave biomedical packaging and universal LaTeX OS outside the main loop.**

Next implement step (if executing): Wave A items 1–3 in this repo only.
