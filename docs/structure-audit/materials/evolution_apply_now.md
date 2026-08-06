# Evolution Apply Now · Next 2 Hours (This Repo Only)

Date: 2026-08-06  
Window: 2h quality loop (`scripts/41_quality_loop_2h.py`)  
Sources operationalized:

- `docs/structure-audit/materials/evolution_landscape.md` (OpenEvolve / Shinka / EvoAgentX)
- User notes: OpenEvolve-style five parts; DeepSearch-Evolve / SCORE / SESA **as patterns only**
- Book dual-loop: `/Users/mahaoxuan/Desktop/AI产品经理/ai-agent-book/book/chapter8.md`
- Synthesis: `docs/structure-audit/materials/00_SYNTHESIS_ACTION.md`

**Hard ban:** `pip install openevolve` · `pip install shinka-evolve` · `pip install evoagentx`  
**Hard ban:** LLM as sole fitness · red `completed_green` · mutate `evolve_evaluator.py` from agent writes

---

## 0. One-line plan

**Do not install external evolve frameworks.** Harden the already-landed OpenEvolve-*style* loop already in this repo: programmatic evaluator → archive best → history → **rollback** → outer 2h runner keeps scoring packages from `ContinuousEmpiricalLoop`.

```text
  External idea                 Steal for next 2h                 Do NOT do
  ─────────────                 ─────────────────                 ────────
  OpenEvolve evaluate()         score_package + cascade gates     pip install
  OpenEvolve archive/islands    state/evolve_archive/*            MAP-Elites DB
  Shinka job+verifier           REPRO script as cheap verifier    Slurm/Hydra
  EvoAgentX workflow evo        (defer)                           topology search
  DeepSearch-Evolve             search = expand/rewrite candidates only
  SCORE                         multi-dim score already in PackageScore
  SESA (eval co-train)          keep judge code-first; no train   weight updates
```

Five parts (user force) → concrete files:

| Part | This repo now | 2h delta |
|------|---------------|----------|
| Mutable object | paper md + expand/degrade + learn notes | snapshot before each rewrite |
| Evaluator | `runtime/evolve_evaluator.py` | rollback + anti-Goodhart caps |
| Search policy | continuous_loop learn plan + outer 41 loop | keep pop=1; expand targets from quality JSON |
| Memory/Archive | `state/evolve_archive/{best,history,best_pointers}` | `previous_best` + optional paper/pdf copy |
| Selection/Rollback | `maybe_update_best` (score > best only) | restore pointers on regression |

---

## 1. Current territory (do not re-invent)

| Piece | Path |
|-------|------|
| Continuous L8 loop | `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/runtime/continuous_loop.py` |
| Full 10-step pipeline | `.../runtime/full_pipeline.py` |
| Scorer | `.../runtime/evolve_evaluator.py` |
| LaTeX PDF | `.../runtime/latex_pdf.py` → `Submissions/parent_education_wage_loop_paper.pdf` |
| 2h outer runner | `.../scripts/41_quality_loop_2h.py` |
| Archive | `.../state/evolve_archive/best.json` |
| History | `.../state/evolve_archive/history.jsonl` |
| Pointers | `.../state/evolve_archive/best_pointers.json` |
| Hour board | `.../.hour-loop/STATUS.md`, `MISSION_2H.md` |
| Quality reds source | `.../Results/json/parent_education_wage_full_pipeline_quality.json` |

**Best score on disk (as of archive):** `81.08`  
Components: repro 1.0 · quality 0.47 · substance 0.7718 · latex_pdf 1.0 · honesty 1.0 · loop_status 0.55  
Verdict still red: `too_thin`, `section_length_gate_required`, `needs_review_loop`  
cn_chars ~7718 (target band 10000+ for substance=1.0)

History trajectory (scores): 68.66 → 66.13 → 66.53 → 76.13 → **81.08**

---

## 2. What each external note means *here* (not install recipes)

### 2.1 OpenEvolve (pattern only)

Public shape: mutate program → `evaluate(path) → metrics` → keep best / islands.  
**Here:**

- genome = writing flags + paper content under `Manuscripts/generated/parent_education_wage_full_pipeline_paper.md`
- evaluate = `score_package(...)` reading repro / quality JSON / PDF size / honesty
- LLM is **mutation only** (expand rewrite / Pi assist), never score

Cascade early-fail (steal): if pipeline failed or `repro_ok` false → skip substance gaming; already partially via weights.

### 2.2 ShinkaEvolve (defer engine)

Useful later when genome is **estimation/replication code** with a cheap verifier.  
Next 2h: treat `replication/reproduce_parent_education_wage_full_pipeline.py` + `REPRO_OK` as the Shinka-like validator **without** job runner.

### 2.3 EvoAgentX (defer)

Evolves multi-agent **workflow topology**. Fixed 10-step spine is still SSOT. Do not import.

### 2.4 DeepSearch-Evolve / SCORE / SESA (distill only)

From session notes (not a local package install):

| Idea | Distill into 2h code |
|------|----------------------|
| DeepSearch-Evolve | “Search” = propose different expand targets / section priorities from `recommended_next_tasks` in quality JSON, not web crawl |
| SCORE | Multi-component score already: repro/quality/substance/latex/honesty/loop_status; keep dimensions visible in archive |
| SESA (eval co-train) | **Do not train** a judge model. Keep code gates; optional later: calibrate scorer on golden packages offline |

---

## 3. Concrete code changes (ordered, this repo only)

### P0 — Evaluator harden (`runtime/evolve_evaluator.py`)

**P0.1 previous_best + rollback helpers**

After a successful better update:

1. If `best.json` exists, copy to `previous_best.json` before overwrite.
2. Mirror `best_pointers.json` → `previous_best_pointers.json`.
3. Add:

```python
def rollback_to_previous(archive_dir: Path) -> dict | None:
    """Restore previous_best* over best* if present. Return restored payload or None."""
```

**P0.2 anti-Goodhart caps**

- If `comps["repro"] < 0.85`: `total = min(total, 40.0)` and note `cap:repro`.
- If integrity floor: keep total 0 (already).
- `loop_status` bonus: only apply if `flags["repro_ok"]` and not integrity_floor.
- `substance`: already capped at 1.0 via `min(1.0, n/10000)`; keep; never let substance outweigh repro+quality combined in narrative claims.

**P0.3 optional evidence list**

Extend `PackageScore` with optional `evidence: list[dict]` entries:

```text
{component: "repro", path: "replication/..._repro_report.md", predicate: "contains REPRO_OK", pass: true}
{component: "latex_pdf", path: "Submissions/..._loop_paper.pdf", predicate: "size>5000", pass: true}
```

Non-breaking: default empty list; archive still writes `to_dict()`.

**P0.4 tests**

Add or extend under `tests/`:

- fixture with `evidence_integrity_blocked` → score 0
- better score updates best + writes previous
- rollback restores previous
- repro fail caps total

Do not require live LLM.

### P1 — Archive artifacts (`state/evolve_archive/`)

| File | Action |
|------|--------|
| `best.json` | keep |
| `history.jsonl` | keep append-only |
| `best_pointers.json` | keep paper/pdf paths |
| `previous_best.json` | **add** via P0.1 |
| `previous_best_pointers.json` | **add** |
| `snapshots/score_<ts>/` | optional: copy paper md + pdf when better_than_best (size-aware; skip if >5MB thrash) |

Snapshot rule: only on `better_than_best`; path recorded in pointers under `snapshot_dir`.

### P2 — Continuous loop accept/rollback hooks (`runtime/continuous_loop.py`)

Current: `_score_and_archive` always archives via `maybe_update_best` (higher score wins).  

2h add:

1. After score, if `not sc.better_than_best` and previous snapshot exists for **mutable paper**, optionally restore last accepted paper bytes when score dropped by >ε (e.g. 3.0) **and** expand just ran.  
   - Safer minimal: **log only** `rollback_suggested=true` in `package_score.json` this window; full file restore next if time.
2. Never call completed_green when blocking (already).
3. Ensure `PYTHONPATH=.` when scripts invoke imports (fix recent `ModuleNotFoundError: runtime` in `.hour-loop/quality_loop_latest.json`).

### P3 — 2h runner (`scripts/41_quality_loop_2h.py`)

Already correct structure: loop → score → maybe_update_best → jsonl.

2h fixes:

1. Ensure script always inserts ROOT on `sys.path` **before** imports (already does) — verify cwd when launched from cron/agent: run as  
   `cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板 && PYTHONPATH=. python3 scripts/41_quality_loop_2h.py --hours 2`
2. On `better_than_best`, write one-line summary to `.hour-loop/STATUS.md` or `quality_loop_latest.json` (latest already).
3. On exception `No module named 'runtime'`, fail row already logged; outer loop continues — good.
4. Do **not** add openevolve CLI wrapper this window.

### P4 — Genome mutation that actually attacks reds

Current reds: `too_thin` + `section_length_gate_required` + soft `needs_review_loop`.

Mutation policy (search):

1. Read `Results/json/parent_education_wage_full_pipeline_quality.json` → `section_length_checks.summary.too_short_sections`.
2. Priority expand order (Chinese char deficits largest first):  
   Main Results (596/3000) → Robustness (499/2200) → Introduction (996/2800) → Empirical Strategy (909/1800) → Literature (751/1500) → Data (794/1200) → Institutional (861/1200) → Conclusion (328/800).
3. Learn plan `target_steps` stay on `REWRITE_TAIL` (`06_writing`…`10_defense`) until blocking clears.
4. Expand must bind numbers only from:  
   `Results/json/parent_education_wage_full_pipeline_main_results.json`, tables under `tables/`, `Data/literature/processed/verified_bibliography.csv`.

This is the DeepSearch-like “search over section deficits,” not web search.

### P5 — Explicitly out of scope for 2h

- MAP-Elites islands / multi-island DB
- `runtime/evolution/pipeline_evolve.py` full skeleton from landscape note (optional stub only if P0–P3 green)
- Training any SESA-style judge
- Switching method family IV/OLS in fitness
- Vendoring Shinka/EvoAgentX/OpenEvolve code trees

---

## 4. Accept / reject rules (selection)

```text
accept  iff  new_score > best_score  (strict)
         and  not integrity_floor
         and  repro component computed from real files

reject  →  keep best.json unchanged
         →  append history.jsonl anyway (transparency)
         →  optional: rollback_suggested if score << best

halt_honest  is a valid loop status; may still update best if package score rose
completed_green  only when evaluate_after_pipeline.is_green (no blocking)
```

Weights (current code, keep unless tests demand tweak):

| Component | Weight |
|-----------|--------|
| repro | 25 |
| quality | 25 |
| substance | 15 |
| latex_pdf | 20 |
| honesty | 10 |
| loop_status | 5 |

Do not reweight mid-loop without logging a version field (`score_schema_version`).

---

## 5. Commands (copy-paste)

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板

# single score of current package
PYTHONPATH=. python3 -c "
from runtime.evolve_evaluator import score_package, load_best
from pathlib import Path
sc = score_package()
print(sc.to_dict())
print('best', load_best(Path('state/evolve_archive/best.json')))
"

# one continuous loop (Grok 4.5 default if env set)
PYTHONPATH=. python3 -m Product.cli continuous-loop --max-rounds 3

# outer 2h quality loop
PYTHONPATH=. python3 scripts/41_quality_loop_2h.py --hours 2 --max-inner-rounds 3 --provider grok --model grok-4.5

# LaTeX PDF re-render only
PYTHONPATH=. python3 -c "
from pathlib import Path
from runtime.latex_pdf import render_markdown_paper_to_pdf
r = render_markdown_paper_to_pdf(
  Path('Manuscripts/generated/parent_education_wage_full_pipeline_paper.md'),
  slug='parent_education_wage',
)
print(r.to_dict())
"
```

---

## 6. Done criteria for this 2h evolution slice

Observable, not aspirational:

1. `state/evolve_archive/best.json` score **≥ previous best** or honest plateau with longer cn_chars.
2. `previous_best.json` exists after at least one improvement.
3. PDF openable: `Submissions/parent_education_wage_loop_paper.pdf` (size > 5KB).
4. Verdict progress: clear `missing_sections` (already cleared in latest quality JSON); reduce `too_short_sections` count; target exit `too_thin` when cn_chars ≥ 10000 **and** section mins met.
5. No `pip` of evolve frameworks in environment.
6. integrity still floors total to 0 if blocked.
7. 2h runner jsonl shows `ok: true` rows (fix ModuleNotFound by correct PYTHONPATH).

---

## 7. Wave map

```text
  Now (this file)
    evaluator rollback + caps
    archive previous_best
    expand against section_length deficits
    2h runner keeps scoring

  Next
    population_size>1 only if write-only eval cheap
    snapshot paper/pdf on best
    optional score_after_pipeline shared helper

  Later
    openevolve/shinka only if genome is fast pure code
    EvoAgentX if multi-agent topology becomes product SSOT
```

---

## 8. Risk register

| Risk | Failure scene | Mitigation |
|------|---------------|------------|
| Expand adds fluff without evidence | score up, integrity later red | bind expand to main_results + verified bib only |
| Score games loop_status | max_rounds halt still “bonus” | P0.2 gate bonus on repro_ok |
| Archive best without paper snapshot | cannot rollback prose | P1 snapshots |
| Runner cwd wrong | `No module named runtime` | always `cd` repo + PYTHONPATH=. |
| Install thrash | half-broken openevolve deps | ban install; document only |

---

## 9. File touch list (max surgical)

| File | Change |
|------|--------|
| `runtime/evolve_evaluator.py` | previous_best, rollback_to_previous, caps, evidence optional |
| `runtime/continuous_loop.py` | optional rollback_suggested log; no green on blocking (verify) |
| `scripts/41_quality_loop_2h.py` | only if path/status write needs fix |
| `tests/test_evolve_evaluator*.py` | new unit tests (create if missing) |
| `state/evolve_archive/*` | written at runtime, not hand-edited |

Do **not** hand-edit `best.json` to fake progress.

---

*Apply-now document for implementers. Patterns from OpenEvolve/Shinka/EvoAgentX/DeepSearch/SCORE/SESA translated into this repo’s paths only. No external evolve package.*
