# Book Skills + Evaluation → Empirical Loop Grafts

Date: 2026-08-06  
Source root: `/Users/mahaoxuan/Desktop/AI产品经理/ai-agent-book`  
Body SSOT: `book/chapter{1,2,6,8,10}.md` (Chinese)  
Product: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板` Continuous Empirical Loop  
Related materials: `book_ch11-15_or_eval.md`, `book_ch7-10.md`, `docs/BOOK_HARNESS.md`  
Rule: **do not invent**; chapter numbers follow book (no ch11–15). Skills + Eval map to ch2 / ch6 / ch8.

---

## 0. Path map (facts on disk)

| Theme | Chapter | Body | Experiments |
|-------|---------|------|-------------|
| Model + Harness; Loop engineering | ch1 | `book/chapter1.md` | `chapter1/` |
| Agent Skills progressive disclosure | ch2 | `book/chapter2.md` §「动态提示词与 Agent Skills」~L708+ | `chapter2/agent-skills-ppt/` |
| Evaluation / Rubric / Judge | ch6 | `book/chapter6.md` | `chapter6/` |
| Continuous evolution / verifier root | ch8 | `book/chapter8.md` | `chapter8/` |
| Multi-agent new-info test | ch10 | `book/chapter10.md` | `chapter10/` |

Product anchors already wired:

- Outer loop: `runtime/continuous_loop.py` (`propose→run→evaluate→learn↻→package`)
- Programmatic scorer: `runtime/evolve_evaluator.py` (`score_package`, integrity floor)
- Skills on disk today: `.claude/skills/integrity-audit/SKILL.md` only
- Registry file: `Product/internal_skills/agent_skill_registry.json`
- Quality JSON: `Results/json/parent_education_wage_full_pipeline_quality.json`

```text
Demo formula:  Agent = LLM + context + tools          (README + ch1)
Prod formula:  Agent = Model + Harness
Harness:       context + tools + constrain + verify + correct
Loop (ch8):    online execute (evidence) ∥ offline evolve (candidate→verify→release)
Paper loop:    design → estimate → write → reproduce → revise↻
               evaluate ──learn──┘
```

---

## 1. Skills grafts (ch2) for empirical loop

### 1.1 Three-layer progressive disclosure (must keep)

Source: `book/chapter2.md` L717–L753.

| Layer | Content | Token intent | Empirical landing |
|-------|---------|--------------|-------------------|
| L1 metadata | `SKILL.md` frontmatter `name` + `description` | hundreds of tokens, always visible | Catalog in registry / system reminder only |
| L2 core flow | Full `SKILL.md` via skill tool when needed | enters trajectory as tool result | Load when step enters estimate / write / repro / audit |
| L3 resources | scripts / templates / checklists | on-demand only | e.g. expand section targets, REPRO checklist |

Book quote (paraphrase-safe rule): do **not** dump all domain knowledge into the system prompt; load on demand.

`description` must be a **routing condition** with **negative examples** (“Use when / Don’t use when”). Wide blurbs (“help with empirical paper”) cause false triggers.

### 1.2 Production placement (way 3)

Book rejects pure system-append (kills KV cache on every skill swap) and pure mid-context file-read as sole pattern (weak instruction following on some models). Production pattern:

1. Metadata list visible without rewriting stable prefix.
2. Full skill loaded only when selected.
3. Route ≠ execute.

**Graft for this repo:**

| Do | Don’t |
|----|-------|
| Keep `integrity-audit` as L1 name+desc always | Paste full Awesome/AERS skill trees into continuous-loop system prompt |
| Stage skills: data-gate / econometrics-check / expand-sections / dont-lie / REPRO | One mega-skill for whole 10-step spine |
| New skills enter **candidate** zone first (ch8 release gate) | Auto-overwrite stable skills after one green score |
| Skill tool result carries path + version | Invisible “I know the skill” without loading |

### 1.3 Skill candidates mapped to loop steps

| Loop stage | Skill intent | Suggested path (thin, not yet required) | Verifier (not LLM alone) |
|------------|--------------|----------------------------------------|---------------------------|
| 04 data | field/sample construction discipline | future `.claude/skills/data-contract/` | `Results/json/*_data_gate*` |
| 05 estimate | OLS vs design method alignment | graft from AERS econometrics-check checklists | main_results JSON + design.json |
| 06–07 write | section length + claim language | ManuscriptAgent expand targets from quality JSON | `section_length_checks` |
| 08–09 citation/repro | verified bib + REPRO_OK | integrity-audit + replication script | `replication/*_repro_report.md` |
| always | no fabricated numbers/cites | `.claude/skills/integrity-audit/` | `evidence_integrity_*` |

Existing integrity skill: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/.claude/skills/integrity-audit/SKILL.md`.

### 1.4 Skills × evolution (ch8)

Skill candidates must include: when to load, preconditions, steps, pitfalls, verification method, source trajectory. Prefer **patch existing skill** over library bloat (`book/chapter8.md` ~L128). Release only after boundary-set improves and hold-out set does not regress → canary, not silent overwrite.

**Rule for 2h window:** do not invent a skill OS. Keep progressive disclosure as architecture constraint while `evolve_evaluator` and expand gates do the scoring work.

---

## 2. Evaluation grafts (ch6 + ch8) for empirical loop

### 2.1 Object of evaluation = Model + Harness

Source: `book/chapter6.md` opening (~L15).

- Ablation: turn off a Harness piece (e.g. integrity floor) → locate component.
- Model swap: fix Harness, swap Grok/MiniMax → bottleneck model vs harness.
- Product implication: score **package + loop behavior**, not “Grok wrote nice prose.”

### 2.2 Three-layer verification (ch8 fig 8-2)

| Layer | Question | Book | Code today |
|-------|----------|------|------------|
| Result | Did the world change correctly? | env / tools | `repro_ok`, main_results JSON exists, script exit |
| Process | Allowed path? | rules / permissions | `evidence_integrity_*`, citation gate, no fake bib |
| Quality | Good enough? | Rubric | quality verdict, section lengths, honesty heuristic |

Lower layers must be **code/env truth**. LLM Judge only for hard-to-formalize upper quality, and never as sole fitness.

### 2.3 Rubric four criteria + veto (ch6 L289–L341)

1. Expert-grounded facts/steps, not “fluency.”
2. Full coverage including **pitfalls**.
3. Weights + **veto** (hallucination / integrity → zero regardless of other dims).
4. Self-contained, behavior-checkable criteria (ban “shows deep understanding”).

**Already in code:**

```text
runtime/evolve_evaluator.py
  evidence_integrity_blocked → quality component 0 AND total score 0
  hard verdicts include too_thin, missing_sections, section_length_gate_required, ...
```

**Must keep:** integrity floor cannot be mutated by writing agent / Pi assist (ch8 L295: safety mechanisms not self-modifiable).

### 2.4 Anti patterns the book forbids (map to loop)

| Forbidden | Source | Loop rule |
|-----------|--------|-----------|
| Same model “reviews” own paper as multi-agent | ch10 L73 | integrity-audit ≠ author self-praise |
| Pass@k as regression stability | ch6 | package accept needs reliable green, not 1/5 luck |
| Fuzzy total hides veto | ch8 exp 8-1 | integrity_floor total=0 |
| Verifier rewritten by business agent | ch8 L295 | whitelist exclude `evolve_evaluator.py` from mutate surface |
| Length bias / keyword stuffing | ch6 Goodhart | `substance` caps; cannot beat repro+integrity |
| “Looks like research output” only | ch8 L272–L274 | PDF exist ≠ ready_for_review |

### 2.5 Concrete grafts onto existing files

#### A. `runtime/continuous_loop.py`

Keep invariants (already mostly present):

| ID | Rule | Anchor |
|----|------|--------|
| CL-1 | Any blocking → never `completed_green` | `has_blocking_quality` + `_package` demote |
| CL-2 | Evaluate returns multi-dim diagnosis | `evaluate_after_pipeline` blocking/soft/repro_ok |
| CL-3 | Learn lands on `target_steps` | `build_learn_plan` + `REWRITE_TAIL` |
| CL-4 | max_rounds → `halt_honest` | fuse in learn plan |
| CL-5 | Fail on 04/05/09 → halt, not infinite rewrite | hard step branch |
| CL-6 | Pi/LLM mutates paper only, not scorer | assist path vs `score_package` |

Incremental grafts (next, still book-aligned):

1. Explicit three-layer fields in evaluate artifact: `result` / `process` / `quality`.
2. Optional `judge_provider_id` ≠ write provider (heterogeneous judge; ch6 multi-source).
3. Negative results (`halted_honest`) indexed same as green for offline learning.
4. Evidence pointers in notes: path + predicate + pass/fail (ch8 structured diagnosis).

#### B. `runtime/evolve_evaluator.py`

Already aligned: programmatic components; integrity floor; archive `best.json` + `history.jsonl`.

Next grafts:

1. `previous_best.json` on update → one-shot rollback pointer (ch8 release/rollback).
2. Cap total when `repro < 0.85` (anti “10k chars without REPRO”).
3. `loop_status` bonus only if `repro_ok` and no integrity floor (anti gaming completion bit).
4. Expand `notes` → `evidence: [{component, path, predicate, pass}]`.
5. Score code out of mutate whitelist.

#### C. Skills loading in agent runtime

When Product agent loads skills:

- L1: scan `Product/internal_skills/agent_skill_registry.json` + `.claude/skills/*/SKILL.md` frontmatter.
- L2: only on step match (write phase loads expand/integrity; estimate phase does not load full manuscript skill).
- Never inject full Auto-Empirical / Awesome trees (see `awesome_skills_graft.md`).

---

## 3. Continuous evolution dual loop (ch8) → what “graft” means here

> Online execute records evidence and does **not** rewrite the official agent; offline evolve aggregates trajectories, diagnoses, generates candidates, verifies gates, then releases.  
> — `book/chapter8.md` ~L231

> Evolution starts from **evaluation**, not “summary.”  
> — `book/chapter8.md` L21

Three trust boundaries (ch8 ~L289–L295):

1. Evidence isolated from instructions.
2. Candidate skills ≠ formal skills.
3. Verifier / tests / release gates / audit logs / stable backups **not self-modified**.

**Empirical translation for next 2h:**

```text
online  = ContinuousEmpiricalLoop + FullPaperPipeline
offline = score_package + maybe_update_best + (future) previous_best rollback
mutable = paper md, expand/degrade flags, learn notes
immutable fitness code = evolve_evaluator + BLOCKING_VERDICTS
```

Do **not** wait for full offline skill ship pipeline this window. Land evaluator archive + rollback hooks first; skill canary is Wave B.

---

## 4. Multi-agent graft (ch10) — only when new information enters

Core test (`book/chapter10.md` ~L73): does collaboration introduce information a single agent cannot obtain at generation time?

| Pattern | New info? | Use on paper loop? |
|---------|-----------|--------------------|
| Same model re-reads own draft | No | No |
| Role debate on same text | No | No |
| Writer + Stata exit code / table hash / claim audit tool | Yes | Yes |

Cost note: multi-agent research systems can be ~15× tokens (ch10). Without tool-grounded new info, do not add personas.

---

## 5. Acceptance checklist (structure-audit)

- [ ] Agent defined as Model+Harness in product docs (see `docs/BOOK_HARNESS.md`).
- [ ] Green package requires REPRO + no blocking; model cannot self-declare done.
- [ ] Fitness is file/JSON/script based; integrity veto can zero total.
- [ ] Skills: metadata catalog + on-demand full text; no full-tree dump.
- [ ] Multi-agent only with independent IO / external verify.
- [ ] Mutate surface excludes evaluator and quality gate definitions.
- [ ] Archive best + history exist; rollback pointer recommended next.

---

## 6. Quote / line index (jump table)

| Theme | Location |
|-------|----------|
| Model+Harness | `book/chapter1.md` ~L250–L298 |
| Skills progressive disclosure | `book/chapter2.md` L708–L769 |
| Eval object Model+Harness | `book/chapter6.md` L15 |
| Rubric + veto | `book/chapter6.md` L289–L341 |
| Goodhart / same-family judge | `book/chapter6.md` L380–L388 |
| Save ≠ learn; eval starts evolution | `book/chapter8.md` L7, L21 |
| Three-layer verify | `book/chapter8.md` L27 |
| Judge ≠ rewriter | `book/chapter8.md` L49 |
| Dual loop online/offline | `book/chapter8.md` L231 |
| Verifier not self-modify | `book/chapter8.md` L295 |
| Multi-agent new-info test | `book/chapter10.md` L73–L86 |

---

## 7. Boundary vs other materials

| File | Covers | This file adds |
|------|--------|----------------|
| `book_ch1-3.md` | full ch1–3 extract | actionable skills layering only |
| `book_ch4-6.md` | tools + eval inventory | Rubric/veto → evaluator grafts |
| `book_ch7-10.md` | post-train + multi-agent | skills+eval graft list for continuous_loop |
| `book_ch11-15_or_eval.md` | theme map ch6/8 | **skills+eval focused** operational grafts |
| `evolution_apply_now.md` | 2h code plan | consumes this graft list as book justification |

---

*Done when: ≥60 lines; all paths absolute or repo-relative real; no invented chapter numbers; grafts map to existing runtime files.*
