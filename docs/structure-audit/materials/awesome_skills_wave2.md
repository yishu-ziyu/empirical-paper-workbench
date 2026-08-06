# Awesome-Agent-Skills Wave2 · Deep Inventory + Thin Gates

> Source: `/Users/mahaoxuan/Desktop/经济学论文/Awesome-Agent-Skills-for-Empirical-Research`  
> Target: `实证论文项目模板` / empirical-paper-workbench  
> Date: 2026-08-06  
> Relation to prior notes:  
> - Wave1 inventory: `docs/structure-audit/materials/awesome_skills_inventory.md`  
> - Wave1 graft notes: `docs/structure-audit/materials/awesome_skills_graft.md`  
> This file is **Wave2**: full skill-dir inventory, top-8 thin gates, and concrete graft plan for `full_pipeline.step_06_writing` + `step_09_replication`.

---

## 0. One-line conclusion

Local Awesome tree holds **49 top-level packages (`skills/00`–`48`)**.  
Workbench should graft **thin binary checklists** into step contracts and quality gates, **not** vendor monorepos.  
Highest ROI for current red gates (`too_thin`, `evidence_integrity_blocked`, lit `verified=0`, design-vs-run drift):

| Priority | Skill (local path) | Gate job |
|----------|-------------------|----------|
| P0 | `27/dont-lie` | Always-on anti-fabrication policy |
| P0 | `27/paper_verification` | Table/body/claim → results JSON |
| P0 | `41/econometrics-check` | Design claim ↔ code alignment |
| P0 | `41/audit-replication` | Expand `REPRO_OK` to package audit |
| P0 | `27/academic_writing` + `econ_intro_writing` | step_06 structure + causal language |
| P0 | `48/chinese-de-aigc` | CN de-AIGC pass after draft |
| P1 | `36` + `41/validate-bib` | Lit section + citation keys |
| P1 | `08/latex-document` | Compile/CJK only when packaging PDF |

**Graft rule:** ≤15 bullets per gate; map to falsifiable fail codes; progressive load full `SKILL.md` only when gate fails.

```text
numbers/cites  >  ID↔code  >  lit verify  >  section structure  >  de-AIGC  >  latex polish
step_06 owns writing structure + dont-lie + de-AIGC hooks
step_09 owns claim-level repro + package 10-check subset
```

---

## 1. Source tree shape

```
Awesome-Agent-Skills-for-Empirical-Research/
├── README.md / README-en.md          # 119 repos / 23k+ skills marketing index
├── docs/01–10-*.md                   # Workflow chapter maps (选题→答辩)
├── scripts/sync-statspai-skill.sh
└── skills/00 … 48                    # Local curated monorepo extracts
```

Each `skills/NN-*` is one upstream repo extract. Nested leaves may be `SKILL.md`, `skill.md`, or whole `.claude/` trees.  
CoPaper.AI / Stanford REAP maintain the index; **not** a runtime dependency of workbench.

---

## 2. Full inventory: every top-level skill package (one-line purpose)

| ID | Directory | One-line purpose |
|----|-----------|------------------|
| 00 | `00-StatsPAI_skill` | Agent-native Python causal/econ pipeline (estimand → estimate → diagnose → export). |
| 01 | `01-lishix520-academic-paper-skills` | Strategist (7-dim reviewer sim) + Composer (systematic draft). |
| 02 | `02-luwill-research-skills` | Research proposal, medical imaging review, paper→slides. |
| 03 | `03-K-Dense-AI-claude-scientific-skills` | Hypothesis, lit review, grants, scientific writing (IMRAD). |
| 04 | `04-K-Dense-AI-claude-scientific-writer` | Thin writer suite: lit, citation, peer-review, critical thinking. |
| 05 | `05-kthorn-research-superpower` | Literature search/filter/citation traversal workflow. |
| 06 | `06-fuhaoda-stats-paper-writing` | Stats/econ LaTeX paper writing + check_tex/check_bib/audit. |
| 07 | `07-Orchestra-Research-AI-Research-SKILLs` | Autoresearch loop, ML paper writing, academic plotting. |
| 08 | `08-ndpvt-web-latex-document-skill` | Universal LaTeX create/compile/CJK/bib/latexdiff toolkit. |
| 09 | `09-meleantonio-awesome-econ-ai-stuff` | Econ-focused skills (latex-tables, paper writer, R/Stata). |
| 10 | `10-Jill0099-causal-inference-mixtape` | Mixtape methods + multi-language templates + robustness. |
| 11 | `11-James-Traina-compound-science` | Multi-agent science research orchestration suite. |
| 12 | `12-pedrohcgs-claude-code-my-workflow` | Full econ research `.claude` workflow (compile, QA, repro). |
| 13 | `13-scunning1975-MixtapeTools` | Slide rhetoric + referee-style tools (Cunningham ecosystem). |
| 14 | `14-luischanci-claude-code-research-starter` | Research project starter `.claude` scaffold. |
| 15 | `15-Felpix-Studios-social-science-research` | Social-science write/audit/validate-bib/review-r agents. |
| 16 | `16-hsantanna88-clo-author` | Paper-centric multi-agent + AEA-style replication mindset. |
| 17 | `17-DAAF-Contribution-Community-daaf` | Large domain-adaptive research skill monorepo. |
| 18 | `18-jusi-aalto-stata-accounting-research` | JAR-style accounting empirics Stata pattern library. |
| 19 | `19-CuellarC05-vera-economic-intelligence` | AI-augmented economist narrative/intel skills. |
| 20 | `20-wenddymacro-python-econ-skill` | Python econ workflow (DID 11-step, IV, RD, SCM, DML). |
| 21 | `21-claesbackman-AI-research-feedback` | Econ paper pre-review: causal overclaim + ID audit. |
| 22 | `22-christopherkenny-skills` | Political science / social science skill collection. |
| 23 | `23-Learning-Bayesian-Statistics-baygent-skills` | Bayesian workflow + DAG-first causal inference. |
| 24 | `24-Imbad0202-academic-research-skills` | Full paper pipeline + hallucination detection. |
| 25 | `25-HosungYou-Diverga` | Research branch/fork multi-agent system. |
| 26 | `26-Data-Wise-scholar` | Scholar plugins: arXiv/DOI/BibTeX/method writing. |
| 27 | `27-dariia-m-my_claude_skills` | **dont-lie, paper_verification, academic_writing, econ_intro, event-studies**. |
| 28 | `28-maxwell2732-paper-replicate-agent-demo` | Paper replication agent demo + quality gates. |
| 29 | `29-quarcs-lab-project20XXy` | Project template skills pack. |
| 30 | `30-zirui-song-claude-skills` | Flat md: lit-review, robustness, referee-response. |
| 31 | `31-thalysandratos-claude-code-skills` | Econ `_skills` pack (overlap with 09 family). |
| 32 | `32-dylantmoore-stata-skill` | Comprehensive Stata syntax/econ plugins. |
| 33 | `33-Galaxy-Dawn-claude-scholar` | Full lifecycle scholar suite + Zotero/Obsidian. |
| 34 | `34-andrehuang-research-companion` | Single research-companion skill. |
| 35 | `35-bahayonghang-academic-writing-skills` | Large academic writing toolkit monorepo. |
| 36 | `36-taoyunudt-literature-review-skill` | Chinese five-step literature review writing. |
| 37 | `37-IlanStrauss-ai-skills` | Thin AI research skills (2). |
| 38 | `38-peternka-academic-proofreader` | Micro-econ multi-pass proofread + number cross-check. |
| 39 | `39-vincentarelbundock-marginaleffects` | Estimand language: predictions/comparisons/slopes. |
| 40 | `40-py-econometrics-pyfixest` | pyfixest API + FE/DID + etable LaTeX. |
| 41 | `41-sticerd-eee-sewage-econometrics-check` | Production R project: **econometrics-check, audit-replication, validate-bib**, etc. |
| 42 | `42-wanshuiyin-ARIS` | Paper write/compile, result-to-claim, citation discipline. |
| 43 | `43-wentorai-research-plugins` | Huge plugin sea (writing/templates/etc.). |
| 44 | `44-matsuikentaro1-humanizer_academic` | EN academic de-AI (23 pattern classes). |
| 45 | `45-stephenturner-skill-deslop` | Scientific writing de-slop + 5-dim score. |
| 46 | `46-hardikpandya-stop-slop` | General three-layer slop detection. |
| 47 | `47-conorbronsdon-avoid-ai-writing` | Audit → rewrite → re-audit process. |
| 48 | `48-copaper-ai-chinese-de-aigc` | **CN-only** 17 patterns, 5-step de-AIGC loop. |

### 2.1 Priority nested leaves (inside top packages)

| Nested path | Purpose |
|-------------|---------|
| `27/.../dont-lie` | Always-on anti-hallucination protocol. |
| `27/.../paper_verification` | 6-phase paper↔code↔output audit + manifest. |
| `27/.../academic_writing` | Applied micro structure + claim–support–implication. |
| `27/.../econ_intro_writing` | Evans/Head intro formula. |
| `27/.../event-studies` | Event-study diagnostics & modern extensions. |
| `27/.../abstract` | Abstract drafting skill. |
| `41/.../econometrics-check` | 4-phase ID design audit. |
| `41/.../audit-replication` | AEA-style 10-check replication package. |
| `41/.../validate-bib` | Cite keys vs `.bib` missing/unused/typo. |
| `41/.../identify` | Identification strategy drafting/check. |
| `41/.../draft-paper` / `paper-excellence` | Draft + pre-submit scoreboard. |
| `28/.../replicate-paper` | Replication orchestration skill. |
| `28/.../rules/replication-protocol` | Hard replication process rules. |
| `04/.../literature-review` | Systematic multi-DB lit + DOI verify. |
| `04/.../scientific-writing` | Two-stage scientific draft. |
| `04/.../peer-review` / `scientific-critical-thinking` | Reviewer pass / critical pass. |
| `01/.../composer` / `strategist` | Write + 7-dim review gates. |
| `06/.../stat-writing` | Stats paper LaTeX chapter refs + audits. |
| `09/.../_skills/*` | latex-tables, academic-paper-writer, econometrics variants. |
| `15/.../skills/*` | write-paper, deep-audit, proofread, validate-bib. |
| `20` (root SKILL) | Python DID/IV/RD/SCM/DML step menus. |
| `21/.../Skills/*` | review-paper causal language audit. |
| `36` (root SKILL) | CN lit five-step. |
| `38` (root SKILL) | Academic proofreader. |
| `44–48` | EN/CN humanizers. |

Mega-packages **17 / 33 / 35 / 43** contain hundreds of leaf skills; treat as **search-on-demand**, not bulk graft.

---

## 3. Priority map by product need

```text
                    ┌─────────────────────┐
                    │ workbench full_pipe │
                    └──────────┬──────────┘
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
    step_06 writing      step_05/ID run      step_09 replication
           │                   │                   │
   academic_writing      econometrics-check   paper_verification
   econ_intro            (design↔code)        audit-replication
   chinese-de-aigc       dont-lie numbers     REPRO claim asserts
   dont-lie prose        claim_register       validate-bib (if cite)
           │                   │                   │
           └────────── integrity-audit (existing) ─┘
```

| Need | Best donor | Already in workbench | Gap |
|------|------------|----------------------|-----|
| Anti-fabrication | 27 dont-lie | integrity 6-dim, claim register | Always-on pre-present checklist; prose must bind paths |
| Section numbers | 27 paper_verification | Number Anchoring partial | Manifest + table audit + inline claims |
| Design ≠ code | 41 econometrics-check | method gate narrative | Explicit design-vs-run fail (IV registered, OLS only) |
| Package repro | 41 audit-replication | `REPRO_OK` one-assert script | 10-check subset + multi-claim asserts |
| Thick Chinese draft | 27 academic + econ_intro | step_06 system prompt graft (partial) | Section finish checklist as gate codes |
| CN de-AIGC | 48 chinese-de-aigc | none formal | Post-write optional pass |
| Lit verify | 36 + 04 lit + 41 validate-bib | verified_count field = 0 | DOI/Crossref + forbid fake cites |
| LaTeX/PDF | 08 latex + 06 check_tex | `runtime/latex_pdf.py` XeLaTeX | Compile gate only on export path |

---

## 4. Top 8 skills · thin gates (≤15 bullets each)

**Not full skill copy.** Each bullet is a binary or scorable check graftable into JSON quality reports / step contracts.

### Gate A · `27/dont-lie` (anti-hallucination) — always-on

1. Confidence < ~90% on fact/API/path/column → **verify by read/run**, not re-reason.  
2. Before write: columns/paths/packages exist (read first).  
3. Analysis code presented only if **executed**, else label `UNTESTED`.  
4. No invented functions/args/package APIs.  
5. No invented paths, columns, sample sizes.  
6. No invented citations, DOIs, URLs, journal names.  
7. Magnitudes **copied from run output / facts JSON**, not mental re-round chains.  
8. After merge/join: report N before/after + NA introduced.  
9. Uncertainty stated explicitly when unverified.  
10. Pre-present checklist all PASS or hard-fail turn: executed · paths · funcs · columns · numbers match · no fake cites · uncertainty labeled.  
11. Fail code: `dont_lie_violation`.  
12. Land: `SOUL.md` line + `.claude/skills/dont-lie/SKILL.md` ≤120 lines + integrity mapping.

### Gate B · `27/paper_verification` (reproducibility / integrity spine)

1. Phase1 inventory exists: scripts, outputs, paper, data, orphan flags.  
2. Every main table cell traces to generator script + output file.  
3. Coef/SE match displayed decimals; **N exact**; R² at displayed precision.  
4. Inline magnitudes in body map to table/JSON or `UNVERIFIED`.  
5. Claim IDs: `T1_R2_C3`, `BODY_S4_...`, `ABS_1`.  
6. Manifest JSON: paper_value, expected_value, source_script, tolerance, status.  
7. Stale output: script mtime > output mtime → FAIL.  
8. SE type in prose matches code (HC1 vs cluster level).  
9. FE/clustering level in prose matches code.  
10. Stars footnote matches actual p thresholds.  
11. Silent NA drop flagged if N drifts.  
12. Phase6 automated compare must print PASS/FAIL per claim (not only one coef).  
13. Fail codes: `table_mismatch`, `inline_unverified`, `stale_output`, `se_type_mismatch`.  
14. Land: extend `evidence/integrity_audit.py` + `verification_manifest.json` writer in pipeline.  
15. Drop R-only assumptions; use Python JSON tables this repo already emits.

### Gate C · `41/econometrics-check` (ID / design audit)

1. Phase1: stated design, estimand (ATE/ATT/LATE/association), treatment, comparison group.  
2. Phase2: design-specific assumptions **stated** (PT for DiD, exclusion for IV, continuity for RD, etc.).  
3. Code implements the design named in manuscript (no silent downgrade).  
4. **Design-vs-run drift:** design registers IV but run is OLS-only → `design_run_drift` BLOCKED.  
5. Inference: SE type and clustering level documented and coded.  
6. Multiple testing awareness when many radii/specs/outcomes.  
7. Phase4: robustness present proportional to threats (not checklist theater).  
8. Methodological citations present only if verified or placeholder.  
9. Output: SOUND / MINOR / MAJOR / CRITICAL + priority fix list (≤5).  
10. Early stop on CRITICAL design failure before polish.  
11. Fail codes: `id_assumption_missing`, `design_run_drift`, `se_mismatch`, `estimand_unclear`.  
12. Land: step_05 / method gate packet + pre-step_06 hard check.  
13. Drop sewage-project variables; keep phase structure only.

### Gate D · `41/audit-replication` (package reproducibility)

1. Repro entry script exists and is ordered (master or documented order).  
2. Script syntax / import graph clean (Python: compile/import check).  
3. All `read_csv`/`Path` inputs exist or documented restricted.  
4. No orphan scripts; no orphan outputs without producer.  
5. Output freshness: outputs ≥ sources.  
6. Deps documented (`requirements` / lock / versions used in report).  
7. Data provenance: source, access date, restrictions.  
8. Path hygiene: no machine-absolute paths that break other machines.  
9. Every main table/figure maps to a script.  
10. README: how to run, data availability, compute requirements (AEA-lite).  
11. Overall PASS only if checks 1–5 + 9 green (submit bar can require 6–10).  
12. Fail codes: `repro_script_missing`, `input_missing`, `stale_output`, `path_hygiene`, `readme_incomplete`.  
13. Land: grow `step_09_replication` beyond single assert.  
14. Read-only audit mode first; fix loop max 3 iterations optional.

### Gate E · `27/academic_writing` + `econ_intro_writing` (academic writing structure)

1. Outline → paragraph plan → full prose (not bullet wall as main text).  
2. Paragraph = one claim; claim → support → implication.  
3. Causal verbs only if `causal_claim_allowed=true`; else association language.  
4. No invented estimates/N/cites; placeholders `[CITATION NEEDED]` / facts only.  
5. Intro order: motivation → question → approach → results w/ magnitudes → contribution → roadmap.  
6. No literature dump in paragraph 1.  
7. Estimand explicit in ID section; threats named.  
8. Results: introduce table → walk columns → economic magnitude vs baseline → limit.  
9. “Insignificant” ≠ “no effect” → “imprecise / cannot reject zero”.  
10. Every table/figure introduced in text with takeaway.  
11. Finish checklist structure/econ/causal/evidence/writing all pass or `too_thin`/`structure_fail`.  
12. CN length bands (course paper): abstract≥200, intro≥800, data+method≥1000, results+rob≥800, conclusion≥300 (chars).  
13. Fail codes: `too_thin`, `causal_overclaim`, `missing_estimand`, `table_dump`.  
14. Land: harden `step_06_writing` system prompt + post-write structure scorer.  
15. Templates are scaffolds only; never verbatim paste into manuscript.

### Gate F · `48/chinese-de-aigc` (CN academic de-AI)

1. Run **after** draft solid; do not co-write with de-AIGC.  
2. Scan 17 pattern classes; emit hit table before rewrite.  
3. Section-differentiated intensity (methods/results light; lit/discussion heavy).  
4. Kill 四字套话 density (e.g. 综上所述/毋庸置疑 spam).  
5. Cut leading 此外/因此/而且 glue; use semantic handoff.  
6. Absolute 证明/必然 → 证据/一致/可能.  
7. Force sentence-length variance in long paragraphs.  
8. Add verifiable grain (dataset years, N, method name) not vague 本研究.  
9. Never alter numbers, conclusions, or citations for style.  
10. Five-dim score (具体性/节奏/谨慎/隐衔接/研究者语气); weighted <35 rework.  
11. Second pass: coherence · factual integrity · style consistency.  
12. Fail code: `aigc_score_low` (soft gate unless journal track).  
13. Land: optional post-step_06 skill; not block E2E until Chinese journal track.  
14. Pair with EN humanizer (44/45) only for bilingual abstracts.

### Gate G · Literature (`36` CN lit + `04` verify spirit + `41/validate-bib`)

1. Lit organized by question/method/gap, not author laundry list.  
2. Each cluster: what known → uncertainty → this paper adds.  
3. `literature_verified_count=0` → no real-looking published citations.  
4. Allowed: `[CITATION NEEDED]` or explicit “未核验，待补”.  
5. When cites exist: every in-text key ∈ bibliography.  
6. Missing bib entry = CRITICAL; unused = info.  
7. Bib quality: author/title/year/venue required fields.  
8. Prefer DOI resolve (Crossref) before marking verified.  
9. Contribution claims (“first/novel”) soft unless supported.  
10. Fail codes: `fake_citation`, `verified_zero_with_cites`, `bib_missing_key`.  
11. Land: step_02 lit pipeline + step_06 lit section guard (already partial).  
12. Drop mandatory AI schematics from K-Dense lit skill.

### Gate H · `08/latex-document` (LaTeX/PDF packaging)

1. Engine: Chinese manuscript → XeLaTeX + ctex (align `runtime/latex_pdf.py`).  
2. Font fallback chain documented (PingFang → STSong → Songti).  
3. Compile via scripted multi-pass or latexmk when bib present.  
4. Escape then bold `**...**` → `\textbf` (existing improve note).  
5. Strip outer ````markdown` fence before convert.  
6. booktabs tables; notes include SE type, sample, stars.  
7. Bib present only if cites exist; else skip biber fail.  
8. Log filter: errors only in CI mode.  
9. Package check before compile for missing sty.  
10. Fail codes: `latex_compile_fail`, `cjk_font_missing`, `bib_orphan`.  
11. Land: export/preflight only; **not** step_06 blocking.  
12. Do not vendor full resume/invoice template zoo.

---

## 5. Graft plan · `step_06_writing` (`runtime/full_pipeline.py`)

### 5.1 Current territory (what exists)

- `step_06_writing` builds `facts` from main OLS + data_gate.  
- System prompt already grafts: dont-lie numbers, no fake cites, causal downgrade, intro skeleton, claim→support→implication, length bands.  
- LLM thin → `_fallback_paper` / `_expand_fallback` course builder.  
- Writes `Manuscripts/generated/{slug}_full_pipeline_paper.md` + section splits.  
- Live pain: `too_thin`, integrity blocked, lit verified=0, IV in design but OLS-only.

### 5.2 Target architecture (thin gates only)

```text
facts JSON (numbers SSOT)
    → draft (LLM or course_builder)
    → Gate E structure scorer (section lengths + outline roles)
    → Gate A prose scan (forbidden invent patterns; evidence path tags)
    → Gate C language check (causal verbs vs causal_claim_allowed)
    → Gate G lit section guard (verified_count)
    → optional Gate F chinese-de-aigc (journal track)
    → integrity-audit --all (existing 6-dim)
    → quality JSON codes
```

### 5.3 Concrete code landings (surgical)

| Item | Where | Action |
|------|-------|--------|
| Facts contract | `step_06_writing` `facts` dict | Add `se_type`, `design_registered`, `design_executed`, `claim_ids[]`, `baseline_mean` if available |
| System prompt | same | Keep; add explicit Gate E finish checklist as “post self-check” lines; ban em dash if CN style requires |
| Structure scorer | new `evidence/writing_structure_gate.py` or extend quality report | Measure CN chars per section; fail `too_thin` with section list |
| Evidence path regex | integrity or writing gate | Require `(证据: ...)` or path token on numeric sentences |
| Causal verb banlist | integrity Forbidden Patterns | 导致/提高/降低/政策效应/LATE when `causal_claim_allowed=false` |
| Lit guard | writing gate | If body matches author-year pattern and verified=0 → BLOCK |
| Section splits | existing | Ensure headings map to integrity section names |
| Expand mode | existing | Preserve all evidence paths; only thicken structure |
| Optional de-AIGC | post-write hook | Only if `track=cn_journal`; never mutate numbers |

### 5.4 Acceptance for step_06

- Doing full-pipeline writing: every main coef in prose equals facts JSON within display precision.  
- Falsifier: inject fake Author (2099) → gate BLOCKED.  
- Falsifier: write “提高工资” when causal false → BLOCKED.  
- Structure: intro ≥800 CN chars without bullet-wall main body.  
- Design drift sentence must appear if `design_registered != design_executed`.

### 5.5 What not to graft into step_06

- Full 27 academic_writing essay (490 lines).  
- Full 48 patterns.md (load on demand).  
- K-Dense mandatory schematics.  
- 08 full latex zoo.

---

## 6. Graft plan · `step_09_replication`

### 6.1 Current territory

- Generates `replication/reproduce_{slug}_full_pipeline.py`.  
- Re-runs OLS HC1 on interim CSV.  
- Asserts one coef + nobs vs `Results/json/..._main_results.json`.  
- Prints `REPRO_OK`; writes short markdown report.  
- Hard fail raises if not OK.

### 6.2 Target (from Gates B + D)

```text
write repro script (multi-claim)
    → run script
    → claim-level asserts (coef, se, nobs, r2 optional)
    → package audit subset (inputs exist, paths relative, outputs fresh)
    → optional manifest emit/update
    → report.md + JSON machine summary
    → REPRO_OK only if all critical asserts pass
```

### 6.3 Concrete landings

| Item | Action |
|------|--------|
| Multi-claim asserts | Assert parent_education coef **and** se; nobs; optionally r2; optionally constant if needed |
| Tolerance table | coef/se: 1e-6 absolute or display-decimal; N exact |
| Script generation | Parameterize from `self.SLUG`, data path, formula, cov_type - not hardcode forever |
| Inputs check | DATA path exists; results JSON exists before assert |
| Freshness | If analysis script mtime > results JSON → fail or force re-run step_05 |
| Path hygiene | Repro script uses `Path(__file__).resolve().parents[1]` only (already) |
| Report | Table of checks 1–N PASS/FAIL (audit-replication style) |
| Manifest hook | Write/update `Results/json/{slug}_verification_manifest.json` with claim IDs |
| Restricted data | Document in README if raw data not shippable; still assert on interim |
| Fail codes | `repro_assert_fail`, `repro_input_missing`, `stale_results` |

### 6.4 Acceptance for step_09

- Mutate results JSON coef by 0.01 → step_09 fails (no silent REPRO_OK).  
- Delete interim CSV → clear `input_missing` in report.  
- Report lists ≥5 binary checks, not only stdout paste.  
- Future: main table all cells in manifest; step_09 consumes manifest.

### 6.5 What not to graft

- Full AEA Data Editor human process.  
- R `verify_replication.R` template as primary (Python first).  
- Sewage project path conventions.

---

## 7. Implementation sequence (workbench)

```text
Wave2a (integrity/numbers)     : Gate A always-on + Gate B manifest v0 for main coef
Wave2b (design drift)          : Gate C design_run_drift on step_05→06 boundary
Wave2c (writing structure)     : Gate E scorer wired into quality JSON (fixes too_thin visibility)
Wave2d (replication)           : Gate D subset + multi-claim in step_09
Wave2e (lit)                   : Gate G hard ban fake cites; verified pipeline separate
Wave2f (polish)                : Gate F optional; Gate H on PDF export only
```

Do **not** block shipping E2E on Wave2f.  
Current honest reds that should stay red until fixed: `verified=0`, IV not run, thin sections if scorer strict.

---

## 8. Mapping to existing integrity-audit

| integrity dim | Wave2 gate reinforcement |
|---------------|--------------------------|
| Required Files | Gate D inventory |
| Section Completeness | Gate E structure scorer |
| Number Anchoring | Gate B table + inline |
| Forbidden Patterns | Gate A + Gate C causal verbs |
| Source-of-Truth Drift | Gate C design_run_drift + Gate B stale |
| Gap Honesty | Gate G verified=0 honesty + limitations |

`integrity-audit` remains the **user-facing skill**; Wave2 gates feed the same `evidence/integrity_audit.py` and quality JSON.

---

## 9. File / skill landing checklist (when implementing)

| Artifact | Suggested path |
|----------|----------------|
| dont-lie thin skill | `.claude/skills/dont-lie/SKILL.md` |
| paper-verification thin skill | `.claude/skills/paper-verification/SKILL.md` |
| econometrics-check thin skill | `.claude/skills/econometrics-check/SKILL.md` |
| writing structure gate | `evidence/writing_structure_gate.py` |
| replication audit | `evidence/replication_audit.py` or expand step_09 |
| manifest schema | `evidence/verification_manifest.schema.json` |
| quality codes doc | `docs/structure-audit/` or `AGENTS.md` Lessons |
| Keep only | `.claude/skills/integrity-audit/` as meta entry |

Progressive disclosure: agent loads full Awesome source only when a gate fails and needs diagnosis detail.

---

## 10. Residual risks

| Risk | Scene | Mitigation |
|------|-------|------------|
| Gate theater | Checklists never fail | Wire to exit codes / quality JSON |
| Over-block E2E | Course paper always red | Split hard vs soft gates; de-AIGC soft |
| Prompt bloat | Full skill in every LLM call | ≤15 bullets in system; refs on fail |
| Language mix | EN humanizer on CN body | CN track → 48 only |
| False SE match | Only coef asserted | Add se assert in step_09 |
| Design fiction | IV in design forever | design_run_drift until 2SLS real |

---

## 11. Next single action

Implement **Wave2a**: emit `verification_manifest.json` for `parent_education` main claim in full_pipeline, and make `step_09` assert **coef + se + nobs** with a 5-row check table in the repro report.

---

## 12. Source path index (absolute)

| Role | Path |
|------|------|
| Awesome root | `/Users/mahaoxuan/Desktop/经济学论文/Awesome-Agent-Skills-for-Empirical-Research` |
| dont-lie | `.../skills/27-dariia-m-my_claude_skills/dont-lie/SKILL.md` |
| paper_verification | `.../skills/27-dariia-m-my_claude_skills/paper_verification/SKILL.md` |
| academic_writing | `.../skills/27-dariia-m-my_claude_skills/academic_writing/SKILL.md` |
| econ_intro | `.../skills/27-dariia-m-my_claude_skills/econ_intro_writing/SKILL.md` |
| econometrics-check | `.../skills/41-sticerd-eee-sewage-econometrics-check/skills/econometrics-check/SKILL.md` |
| audit-replication | `.../skills/41-sticerd-eee-sewage-econometrics-check/skills/audit-replication/SKILL.md` |
| validate-bib | `.../skills/41-sticerd-eee-sewage-econometrics-check/skills/validate-bib/SKILL.md` |
| chinese-de-aigc | `.../skills/48-copaper-ai-chinese-de-aigc/SKILL.md` |
| latex-document | `.../skills/08-ndpvt-web-latex-document-skill/SKILL.md` |
| CN lit | `.../skills/36-taoyunudt-literature-review-skill/SKILL.md` |
| full_pipeline | `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/runtime/full_pipeline.py` |
| integrity-audit | `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/.claude/skills/integrity-audit/SKILL.md` |
| this note | `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/docs/structure-audit/materials/awesome_skills_wave2.md` |

---

*End of Wave2 inventory. Graft mechanisms, not monorepos.*
