# Penguin Harness Deep Read · 五件套自进化模型 → Empirical Workbench

Date: 2026-08-06  
Source (read-only vendor clone):  
`/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/vendor/penguin-harness`  
Upstream: `https://github.com/Prism-Shadow/penguin-harness.git`  
Sibling notes: `docs/structure-audit/materials/penguin_harness.md`（port 面）  
`docs/structure-audit/materials/evolution_landscape.md`（OpenEvolve/Shinka 对照）

This note is **deeper than** `penguin_harness.md`: file-level 五件套 extraction, protocol anti-narration gates, and **exact** map onto current workbench paths that already exist on disk.

---

## 0. One-line conclusion

Penguin’s self-evolution is not a product UI. It is five hard pieces:

```text
Mutable Object  →  Evaluator  →  Search Policy  →  Memory/Archive  →  Selection/Rollback
     │                 │              │                  │                    │
  versioned        private         one Candidate      scoreboard +         strictly ↑
  agent_state/     rubric +        + hypothesis       snapshots +          else restore
                   plain YAML      per round          traces only-accepted
```

Workbench already has partial instances of each piece under `runtime/` + `state/evolve_archive/`.  
What is still weak: versioned mutable slice, pre-edit snapshot restore, protocol-hard evaluator isolation, and reject-not-on-scoreboard discipline.

---

## 1. Source map (what was deep-read)

| Layer | Absolute path under vendor |
|-------|----------------------------|
| Product README | `vendor/penguin-harness/README.md`, `README.zh.md` |
| Self-improvement SSOT | `vendor/penguin-harness/packages/docs/content/self-improvement.en.md` |
| Agent creation (mutable seed) | `vendor/penguin-harness/packages/skills/skills/agent-creation/SKILL.md` |
| Benchmark design (frozen eval) | `vendor/penguin-harness/packages/skills/skills/benchmark-design/SKILL.md` |
| Leaf evaluator (protocol) | `vendor/penguin-harness/packages/skills/skills/agent-evaluation/SKILL.md` |
| Optimizer loop | `vendor/penguin-harness/packages/skills/skills/agent-optimization/SKILL.md` |
| Runnable mini-loop | `vendor/penguin-harness/examples/self-improving-agent/` (`self-improve.ts`, `self-evolve.ts`, `self-evolve-recursive.ts`) |

Roles (from `self-improvement.en.md`):

| Role | Job | Forbidden |
|------|-----|-----------|
| Builder | `agent-creation` → `benchmark-design` → Formal Baseline | Must not “train” Target during design to chase score |
| Target | Run Case in isolated Workspace | Never sees `rubric/` / Gold |
| Evaluator | One Case × one Run; private score; **plain protocol YAML only** | No scoreboard write; no Target edit; no optimizer |
| Optimizer | Diagnose → Candidate → delegate eval → accept/rollback | **Must not read private rubric**; contamination → stop |

Two top-level Sessions: (1) create+calibrate, (2) optimize. Leaf cells only via `run_subagent`.

---

## 2. The five pieces (Penguin authority)

### 2.1 Mutable Object

**What mutates:** files under Target `agent_state/`, not application code.

Typical layout (from skills + configuration docs):

```text
<app_data_dir>/agents/<test_agent_id>/
├── agent_state/
│   ├── AGENTS.md              # primary optimizer edit surface
│   ├── system_config.yaml     # version, name, safe model.thinking_level, …
│   ├── skills/<name>/SKILL.md # reusable target-owned capabilities
│   ├── memory/  tools/
│   └── .vault.toml            # secrets — excluded from snapshots
├── benchmarks/<benchmark_id>/ # frozen after design (not mutable by Optimizer)
├── snapshots/v<N>.tar.gz
├── traces/
└── workspaces/                # per-run isolation
```

Rules that define “mutable”:

- Candidate may edit: `AGENTS.md`, focused Skills, safe `system_config` fields.
- Candidate must **not** edit: frozen Benchmark, `system_prompt` (unless requested), library Skills for target-specific hacks, `model.thinking_level` (runtime frozen by Scoreboard).
- `version` is a monotonic integer on `system_config.yaml`; Candidate version = Reference + 1; rejected versions are never reused.
- Before any State edit: `snapshots/v<Reference>.tar.gz` must exist (atomic archive of `agent_state/`, vault excluded; never overwrite same-version snapshot).

Toy proof (`examples/self-improving-agent/self-evolve.ts`):

- Mutable object = demo agent’s `AGENTS.md` (starts blank).
- Script never writes the house convention; the **agent** authors `AGENTS.md` after comparing failed report vs gold-format reference.
- That is the definition of “genome”: identity/behavior files, not the task workspace.

### 2.2 Evaluator

**What evaluates:** isolated execution + **private** rubric + numeric score + session linkage.

Contract (`agent-evaluation/SKILL.md`):

```text
Request (complete or invalid_request):
  protocol_version, case_id, run, expected_version,
  test_agent_id, benchmark_id, provider, model_id

Scored ok YAML only (worker-authored text = this document, nothing else):
  status: ok
  score: 0..100
  cost, duration_ms, session_id
  provider / model_id / thinking_level (actual)

Failure YAML:
  status: failed
  failure_code: invalid_request | benchmark_invalid | version_changed | evaluation_failed
  # never include score on failure
```

Hard isolation:

- Copy only `statement/` into Workspace; Rubric stays private to Evaluator.
- Wrong / missing Target artifact is still a **scored** result (`status: ok` with low score).
- Infrastructure / launch / trace-bind failure → `evaluation_failed`, **not** score zero.
- `version_changed` if State version or thinking_level drifts mid-eval.
- Rubric items total exactly 100 points.

Toy proof (`score()` in `self-evolve.ts`): pure code, 10 atomic points (5 content + 5 convention). No LLM narration can invent a score; the script reads `summary.md` bytes.

Benchmark side (`benchmark-design/SKILL.md`):

- Public `statement/` vs private `rubric/` physical split.
- Pilot 1 Run/Case; unselected Pilots never enter scoreboard.
- Freeze → Formal Baseline is the selected Pilot matrix as-is (no backfill Runs).
- Leak check: public files must not reveal Gold / private scoring conditions.

### 2.3 Search Policy

**Who searches:** Optimizer following `agent-optimization/SKILL.md`.

One round (search unit):

```text
1 Establish Reference  (State version + complete Evaluation on frozen Benchmark)
2 Diagnose             (public statements + scores + score-linked traces)
3 Falsifiable hypothesis  (predict which Case behavior changes)
4 One Candidate        (bounded State edit from Reference)
5 Admissibility        (general; no private eval info; only allowed fields)
6 Evaluate full matrix (Case × runs via parallel agent-evaluation subagents)
7 Decide               (accept iff every cell valid AND mean score strictly > Reference)
8 Persist or rollback  (scoreboard append only on accept)
```

Search constraints:

- Exactly **one** Candidate per round; no mid-flight State edit while cells run.
- `runs` frozen for the optimization Session (not inferred from Baseline).
- Runtime freeze: `(provider, model_id, thinking_level)` must match Reference Evaluation; mismatch → whole matrix invalid, stop.
- Round budget counts only complete valid Candidate Evaluations; format repairs do not consume rounds.
- Rejected Candidates become **evidence** for later hypotheses, never Scoreboard rows.
- Stop: hit target score OR exhaust valid rounds; keep highest accepted Reference.

Toy search (`self-evolve.ts` / recursive):

```text
evaluate baseline → reflectAndEditOwnState → re-evaluate → keep iff mean strictly improved
recursive: state_{n+1} = agent.reflect(state_n, new_evidence)
```

### 2.4 Memory / Archive

Penguin archives are **files**, not chat memory:

| Artifact | Path pattern | Who writes | Retention rule |
|----------|--------------|------------|----------------|
| Scoreboard | `benchmarks/<id>/scoreboard.yaml` | Builder (Baseline) + Optimizer (**accepted only**) | authoritative averages as written; server must not recompute |
| Snapshots | `snapshots/vN.tar.gz` | Optimizer before edit | never overwrite same N; no vault |
| Traces | `traces/...` | runtime Sessions | append-only; scoreboard links via `session_id` |
| Workspaces | `workspaces/<unique>/` | Evaluator per cell | isolation boundary |
| Unselected Pilot | temporary outside `benchmarks/` | Builder | deleted after Freeze |
| Rejected Candidate | files restored; optional evidence in optimizer context | — | **not** on scoreboard |

Scoreboard Evaluation shape (both Baseline and accepted Candidate):

```yaml
- time: <ISO-8601 UTC>
  version: <Agent State version>
  provider: <provider>
  model_id: <model_id>
  thinking_level: <thinking_level>
  summary_title: ...
  summary: ...
  score: <avg Case scores, 2 decimals>
  cost: <avg or null>
  duration_ms: <avg integer>
  cases:
    - case: <case_id>
      score: ...
      runs:
        - score: ...
          session_id: <Test Session id>
```

Auditable end-to-end: every score → `session_id` → full Trace (`self-improvement.en.md`).

### 2.5 Selection / Rollback

Acceptance predicate (hard):

```text
accept ⇔ admissible
       ∧ Evaluation complete and every cell valid
       ∧ top-level average score STRICTLY higher than Reference
else → restore Reference files + version; delete Candidate-created files; verify restore
```

Rollback layers:

1. **In-round fast path:** original file contents retained before edit; restore on reject.
2. **Snapshot restore:** `vN.tar.gz` whole State.
3. **Version pin:** Evaluator request carries `expected_version`; drift → `version_changed`.
4. **Contamination stop:** if private rubric/Gold enters Optimizer context → restore Candidate, **stop** Session (not “half accept”).

Toy honesty (`self-evolve.ts` lines 224–232): if N+1 mean ≤ baseline, write blank `AGENTS.md` again. Weak models that “narrate a fix” but regress get rolled back; that is the loop working.

---

## 3. Protocol YAML / score gates that prevent narration-as-score

These are the anti-Goodhart / anti-bluff mechanisms. Port them as **code invariants**, not skill prose.

### 3.1 Plain protocol only (Evaluator)

From `agent-evaluation/SKILL.md` + Optimizer/Builder dispatch rules:

1. Across all streamed and final responses, **only** worker-authored text is the final plain protocol YAML.
2. Forbidden: narration, headings, Markdown fences, summaries, private scoring details, optimization advice on failure.
3. Caller (Builder/Optimizer) **must** verify “exactly one plain protocol YAML document” **before** reading `status` or `score`.
4. If format invalid: same Evaluator **resends clean YAML from existing result**; do **not** rerun Target; do **not** extract YAML from polluted text yourself.
5. Transport metadata from `run_subagent` is not worker-authored text.

Effect: an LLM cannot “talk its way” into a score. Narration is not a score channel.

### 3.2 Score domain gates

| Gate | Rule |
|------|------|
| Scale | Every Run/Case score on fixed `0..100`; no `max_score` field |
| Finite | Non-finite or out-of-range → `evaluation_failed`, not a fake 0 |
| Failure ≠ zero | `evaluation_failed` repairs the cell; never record infrastructure failure as quality 0 |
| Runtime match | Actual `(provider, model_id, thinking_level)` must equal frozen Reference; else matrix invalid |
| Version match | `expected_version` must equal live State version |
| Strict accept | Only strictly higher mean score promotes Candidate |
| Scoreboard purity | Rejected Candidates never written to `scoreboard.yaml` |
| Authority | Stored averages are authoritative; no server/UI recompute that can launder scores |
| Private split | Target never sees rubric; Optimizer never sees rubric (contamination halt) |

### 3.3 Benchmark design gates (evaluation validity, not score inflation)

- Separating decision: intended behavior vs shortcut must produce **different scored outcomes**.
- Do not pad points for format/checklist floors unless that **is** the capability.
- Gold fixed before seeing answer; never rewrite private standard after evaluation.
- Leak check before dispatch.

### 3.4 Toy loop’s numeric gate (script-level)

`score()` in `self-evolve.ts` is pure string/byte checks. Keep/rollback is `evolved > baseline` only. No prose “looks better” path.

---

## 4. Map each piece → Empirical Workbench (real paths)

Root: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`

### 4.1 Mutable Object → what learn may rewrite

| Penguin | Workbench today | Path |
|---------|-----------------|------|
| `agent_state/AGENTS.md` | Paper markdown draft | `Manuscripts/generated/parent_education_wage_full_pipeline_paper.md` |
| Skills / method policy | expand/degrade flags + learn notes into pipeline | `runtime/full_pipeline.py` (`expand_mode`, `degrade_mode`, `learn_notes`) |
| `system_config.version` | **Missing as integer version on mutable blob** | should live under `state/runs/continuous_loop_*/` |
| Safe knobs | provider/model freeze at loop construct | `runtime/continuous_loop.py` `ContinuousEmpiricalLoop.__init__` |
| Workspace outputs | Results tables / quality JSON (mostly immutable after write) | `Results/json/parent_education_wage_full_pipeline_*.json` |

`LearnPlan` (`runtime/continuous_loop.py`) is the **search operator surface** over mutable slice:

- `target_steps` e.g. `REWRITE_TAIL` = `06_writing` … `10_defense`
- `expand_mode` / `degrade_mode` / `next_action` ∈ `{rewrite_expand, degrade_and_rewrite, halt_honest, package_green}`

Gap vs Penguin: no explicit versioned mutable directory + pre-edit tar; paper path is overwritten in place across rounds.

### 4.2 Evaluator → `runtime/evolve_evaluator.py` + in-loop gates

Two evaluator layers (do not confuse):

**A. L8 in-loop gate** — `runtime/continuous_loop.py`

- `BLOCKING_VERDICTS` / `SOFT_VERDICTS` frozensets
- `evaluate_after_pipeline(pipe)` → structured dict: `verdict`, `blocking`, `soft`, `repro_ok`, `is_green`
- `has_blocking_quality` hard-forbids `completed_green` when blocking reds remain
- Sources: `Results/json/{slug}_full_pipeline_quality.json`, citation gate JSON, step status for REPRO

**B. Package fitness** — `runtime/evolve_evaluator.py`

```text
score_package() components (weights sum 100):
  repro        25   # main results + reproduce_*.py + REPRO_OK in report
  quality      25   # inverse of blocking severity; integrity floor → 0
  substance    15   # CN char length / heading hints
  latex_pdf    20   # Submissions/{slug}_loop_paper.pdf size > 5k
  honesty      10   # causal_claim_allowed / overclaim heuristics
  loop_status   5   # completed_green / halted_honest / max_rounds / failed
```

Integrity anti-bluff (programmatic, not narration):

```text
if evidence_integrity_blocked in verdict:
  quality component = 0
  total score forced = 0
  flags.integrity_floor = True
```

This is the workbench analogue of “private rubric + numeric scale”: **gate code** is the rubric; writers must not rewrite gate thresholds to “optimize”.

Call sites:

- `ContinuousEmpiricalLoop._score_and_archive` → after package artifacts (incl. LaTeX PDF)
- `scripts/41_quality_loop_2h.py` outer H8-ish loop: run continuous-loop → `score_package` → `maybe_update_best`

### 4.3 Search Policy → `runtime/continuous_loop.py` (+ outer 2h script)

```text
ContinuousEmpiricalLoop.run():
  for round_i in 1..max_rounds:
    FullPaperPipeline.run(only_steps, expand, degrade, learn_notes)
    evaluation = evaluate_after_pipeline(...)
    plan = build_learn_plan(evaluation, round_i, max_rounds)
    persist round_{i}_evaluate.json / round_{i}_learn.json
    optional Pi assist rewrite on paper md
    if package_green / halt_honest → _package + break
    else re-enter with target_steps = plan.target_steps
  safety net: demote completed_green if blocking remains
```

| Penguin Search | Workbench |
|----------------|-----------|
| One Candidate / round | One `LearnPlan` per round |
| Falsifiable hypothesis | **Weak**: `notes` string only; no required “expected verdict extinguished” field |
| Full matrix | Re-run rewrite tail steps; not multi-seed REPRO matrix yet |
| Strictly higher score | L8 uses absolute green/halt; package score uses `>` best in archive (cross-loop) |
| Parallel cells | Optional Pi assist; claim auditors not yet parallel protocol workers |
| Runtime freeze | Constructor binds provider/model; not re-validated mid-matrix |

Outer search (time-bounded, multi-loop):

- `scripts/41_quality_loop_2h.py` — until wall clock, keep launching inner loops, archive best score
- CLI: `PYTHONPATH=. python3 -m Product.cli quality-loop --hours 2` (and script above)

### 4.4 Memory / Archive → `state/evolve_archive/` + run dirs

**Cross-loop archive (exists):**

```text
/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/state/evolve_archive/
├── best.json            # current best PackageScore dict
├── best_pointers.json   # paper + pdf relative paths + score + saved_at
└── history.jsonl        # every scored attempt (accepted best + rejected lower)
```

`maybe_update_best` (`runtime/evolve_evaluator.py`):

- Always append to `history.jsonl`
- Update `best.json` / `best_pointers.json` **only if** `score > best.score` (strictly higher; ties lose)
- Sets `better_than_best` flag on returned `PackageScore`

Observed sample (live disk at write time of this note):

- `best.json` score `68.66` with `quality_green: false`, integrity-related verdicts still in notes
- Later history rows `66.13`, `66.53` correctly marked `better_than_best: false` (not promoted)

**Per-loop archive (exists):**

```text
state/runs/continuous_loop_{slug}_{stamp}/
├── loop_state.json
├── LOOP_SUMMARY.md
├── package_manifest.json
├── package_score.json          # from _score_and_archive
├── latex_pdf_result.json
├── round_k_evaluate.json
└── round_k_learn.json
```

**Penguin Scoreboard analogue gaps:**

- Workbench `history.jsonl` logs **all** scores (including non-improvements) — closer to attempts log than pure accepted-only scoreboard.
- `best.json` is the accepted Reference for package fitness.
- No `snapshots/vN.tar.gz` of mutable paper/state before learn apply.
- Trace append: `artifacts/agent_trace_log.jsonl` (loop status lines); product runs also under `state/runs/run_*/run_events.jsonl`.

**Latest pointer for product surfaces:**

- `Results/json/parent_education_wage_continuous_loop_latest.json`

### 4.5 Selection / Rollback → accept rules on disk

| Decision | Code location | Behavior |
|----------|---------------|----------|
| Absolute green | `evaluate_after_pipeline` `is_green` | only `ready_for_review` (or empty) + REPRO + no blocking |
| Refuse green-on-red | `has_blocking_quality` + `_package` + run() safety net | force `halted_honest` |
| Honest halt | `build_learn_plan` max_rounds / hard step fail | package with residual reds, no lie |
| Package best keep | `maybe_update_best` | strictly higher scalar only |
| Toy-style State rollback | **Not implemented** for paper md | weaker models can regress draft in place; only score archive refuses to crown regress |

Workbench strength: **cannot bluff completed_green** while blocking quality remains.  
Workbench gap: no file-level restore of Reference paper when Candidate rewrite lowers fitness mid-loop.

---

## 5. Side-by-side diagram (territory)

```text
Penguin                                      Empirical Continuous Loop
─────────────────────────────────────────────────────────────────────────
Mutable: agent_state/ + version              Mutable: paper.md + expand/degrade
                                             + LearnPlan (version MISSING)

Evaluator: agent-evaluation YAML             evaluate_after_pipeline (L8)
           + private rubric/                 + score_package (fitness)
           + failure_code ≠ 0                + integrity_floor total=0

Search: agent-optimization rounds            ContinuousEmpiricalLoop.run
        one Candidate, hypothesis            build_learn_plan → target_steps
        Case×runs subagents                  (+ 41_quality_loop_2h outer)

Archive: scoreboard.yaml accepted-only       state/evolve_archive/best.json
         snapshots/vN.tar.gz                 history.jsonl (all attempts)
         traces + session_id                 state/runs/continuous_loop_*/

Select:  score strictly ↑                    maybe_update_best: score >
         else restore State                  L8: green only if gates pass
                                             rollback of files: GAP
```

```text
L8 (in one continuous_loop)     H8 (across loops / skills)
────────────────────────────    ──────────────────────────
rounds of rewrite/evaluate      quality_loop_2h + best.json
halted_honest fuse              promote skill only after canary (not wired)
maps to Optimizer rounds        maps to accepted State promotion
```

---

## 6. Concrete file checklist (copy into implement tickets)

| Piece | Penguin authority files | Workbench implement/touch files |
|-------|-------------------------|----------------------------------|
| Mutable Object | `packages/skills/skills/agent-creation/SKILL.md` | `runtime/continuous_loop.py` LearnPlan; `Manuscripts/generated/*_paper.md`; future `state/runs/.../mutable_vN/` |
| Evaluator | `packages/skills/skills/agent-evaluation/SKILL.md`, `benchmark-design/SKILL.md` | `runtime/continuous_loop.py` (`evaluate_after_pipeline`, verdict sets); `runtime/evolve_evaluator.py`; quality JSON under `Results/json/` |
| Search Policy | `packages/skills/skills/agent-optimization/SKILL.md` | `runtime/continuous_loop.py` `run()`; `scripts/41_quality_loop_2h.py` |
| Memory/Archive | `packages/docs/content/self-improvement.en.md` scoreboard/snapshots | `state/evolve_archive/*`; `state/runs/continuous_loop_*/*`; `artifacts/agent_trace_log.jsonl` |
| Selection/Rollback | Optimizer decide step + `self-evolve.ts` keep/rollback | `maybe_update_best`; green safety net; **add** snapshot restore API |

Related product PDF path scored by evaluator:

- `Submissions/parent_education_wage_loop_paper.pdf`
- LaTeX builder: `runtime/latex_pdf.py` → `Submissions/latex_build/parent_education_wage/`

---

## 7. Port priorities (structure only; not a feature wishlist)

Already landed (keep):

1. Blocking verdict hard-stop on `completed_green` (`continuous_loop.py`).
2. Programmatic multi-component package score + integrity floor (`evolve_evaluator.py`).
3. Strictly higher update of `state/evolve_archive/best.json` + full history.
4. Per-round evaluate/learn JSON on disk.

Highest-value missing Penguin invariants:

1. **Versioned mutable slice + pre-learn snapshot + restore on non-improvement** (Selection/Rollback completeness).
2. **Accepted-only scoreboard** separate from `history.jsonl` attempts (or mark decision field).
3. **Hypothesis field** on `LearnPlan` with expected extinguished verdicts (Search Policy).
4. **Runtime/gate freeze record** in `loop_meta` (provider, model, quality schema hash, data hash).
5. **Produce vs Evaluate context isolation** (writer never loads integrity-audit gold / private thresholds as prompt cheatsheet) — integrity-audit skill already exists at `.claude/skills/integrity-audit/SKILL.md`.

Non-goals (do not port):

- Penguin desktop/Web evaluation center, OmniMessage wire protocol, AgentHub catalog, installers.
- LLM-only scoring without file/gate anchors.

---

## 8. Verification sketch (how to know the five pieces are real)

```text
1 Mutable: change only paper md / learn flags; estimates/json hashes unchanged across rewrite-only round
2 Evaluator: with evidence_integrity_blocked, score_package.score == 0.0 always
3 Search: one LearnPlan per round; round_k_learn.json exists for each k
4 Archive: history.jsonl grows every package; best.json only moves on strict score increase
5 Rollback: (after implement) reject Candidate restores paper bytes to pre-edit snapshot
```

Smoke paths already used in project memory:

```bash
PYTHONPATH=. python3 -m Product.cli quality-loop --hours 2
# or
PYTHONPATH=. python3 scripts/41_quality_loop_2h.py --hours 2 --max-inner-rounds 3
```

Logs: `.hour-loop/quality_loop_2h.jsonl`, archive under `state/evolve_archive/`.

---

## 9. Glossary (Penguin term → workbench term)

| Penguin | Workbench |
|---------|-----------|
| Target Agent State | Versioned paper + policy mutable slice |
| Formal Baseline | First complete evaluate on frozen quality/REPRO contracts |
| Reference | Best accepted loop package (`best.json` + pointers) |
| Candidate | One `LearnPlan` + applied rewrite |
| Scoreboard | Ideal: accepted-only; today: `best.json` + `history.jsonl` |
| Rubric | Gate code + integrity-audit rules |
| Statement | Topic, data cards, pipeline task inputs |
| Snapshot | Missing tar; need pre-learn mutable snapshot |
| Contamination | Writer prompt loading private gate gold |
| Strictly higher | `float(score) > float(best.score)` in `maybe_update_best` |

---

## 10. Source citations (local)

- Self-improvement: `vendor/penguin-harness/packages/docs/content/self-improvement.en.md`
- Optimization loop: `vendor/penguin-harness/packages/skills/skills/agent-optimization/SKILL.md` (v9)
- Evaluation protocol: `vendor/penguin-harness/packages/skills/skills/agent-evaluation/SKILL.md` (v5)
- Benchmark freeze: `vendor/penguin-harness/packages/skills/skills/benchmark-design/SKILL.md` (v7)
- Agent state seed: `vendor/penguin-harness/packages/skills/skills/agent-creation/SKILL.md` (v7)
- Runnable 五件套 toy: `vendor/penguin-harness/examples/self-improving-agent/self-evolve.ts` (score + keep/rollback)
- Workbench loop: `runtime/continuous_loop.py`
- Workbench fitness: `runtime/evolve_evaluator.py`
- Workbench archive: `state/evolve_archive/{best.json,best_pointers.json,history.jsonl}`
- Outer evolve driver: `scripts/41_quality_loop_2h.py`

End of deep read. Port the **invariants**, not the desktop product.
