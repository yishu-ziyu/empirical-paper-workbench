# Wave A impl note — continuous_loop + evolve_evaluator (2026-08-06)

Scope: NOW items from `00_SYNTHESIS_ACTION.md` that were **not** already fully wired into the loop package path.

## Done

### 1. Never `completed_green` with blocking quality (hardened)

| Layer | Where | Behavior |
|-------|-------|----------|
| Evaluate | `evaluate_after_pipeline` | `is_green` only when status=completed + REPRO_OK + **no** `BLOCKING_VERDICTS` + verdict empty/`ready_for_review` |
| Helper | `has_blocking_quality` | Shared check on `evaluation.blocking` or raw verdict |
| Decision | `run` · `package_green` branch | If blocking or not `is_green` → force `halted_honest`, still package |
| Package | `_package` | Refuses to emit `status=completed_green` when blocking remains |
| Safety net | end of `run` | If status still green + blocking → demote + re-package |

Falsifier: any path that leaves `LoopResult.status == "completed_green"` while `final_verdict ∩ BLOCKING_VERDICTS ≠ ∅`.

### 2. After each package → evolve score + `package_manifest` with score

`_package` always calls `_score_and_archive`:

1. `score_package(project_root, slug, loop_state)`
2. `maybe_update_best` → `state/evolve_archive/`
3. Writes `state/runs/<loop_id>/package_score.json`
4. Embeds full score payload in `package_manifest.json` and `*_continuous_loop_latest.json` under key `score`
5. Package dict carries `score` (string) + `score_path` + `manifest`

### 3. Integrity floor (`evidence_integrity_blocked` → total 0)

In `runtime/evolve_evaluator.py` `score_package`:

- quality component forced to `0.0`
- **total score forced to `0.0`** (not just quality weight)
- flags: `integrity_floor=True`
- notes: `integrity_floor: evidence_integrity_blocked → quality=0` + `integrity_floor: total=0`

Anti-Goodhart: cannot trade substance/latex/repro for dirty evidence.

## Files touched

- `runtime/continuous_loop.py`
- `runtime/evolve_evaluator.py`
- this note

## Explicitly not in this wave

- mutable snapshot / rollback / strictly_better accept gate
- LearnPlan.hypothesis required fields
- verification_manifest v0 / dont-lie skill
- weight remap to synthesis §2.2 (0.40/0.40/0.20) — kept existing multi-component weights; only integrity floor + package wiring

## Local check

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板
python3 -c "
from runtime.continuous_loop import (
    BLOCKING_VERDICTS, has_blocking_quality, evaluate_after_pipeline,
    build_learn_plan, ContinuousEmpiricalLoop,
)
from runtime.evolve_evaluator import score_package, maybe_update_best

# blocking helper
assert has_blocking_quality(['too_thin'])
assert has_blocking_quality(evaluation={'blocking': ['evidence_integrity_blocked'], 'verdict': []})
assert not has_blocking_quality(['ready_for_review'])
assert not has_blocking_quality(evaluation={'blocking': [], 'verdict': ['ready_for_review']})

# integrity floor on live quality JSON (has evidence_integrity_blocked)
sc = score_package(loop_state={'status': 'halted_honest'})
assert sc.score == 0.0, sc
assert sc.flags.get('integrity_floor') is True
assert sc.components.get('quality') == 0.0
print('SMOKE_OK', sc.score, sc.flags, sc.notes[:3])
"
```

Expected: `SMOKE_OK 0.0 ... integrity_floor ...`

## Residual risk

- Full end-to-end continuous_loop run not re-executed in this edit (expensive LLM path).
- Score still uses pre-existing multi-component weights; synthesis §2.2 pure 3-weight map is deferred.
- `maybe_update_best` still may record score=0 as first best if archive empty (history truth; not a green claim).
