# Snapshot / Rollback (Penguin port) · Continuous Empirical Loop

Date: 2026-08-06  
Authority: `docs/structure-audit/materials/penguin_harness_deep.md` §2.5 Selection/Rollback  
Code: `runtime/continuous_loop.py`, `runtime/evolve_evaluator.py`

## One-line

Before expand/degrade rewrites the paper, snapshot it; after score, if the candidate is not better than best **and** score dropped, restore paper bytes and write `rollback.json`. `history.jsonl` keeps every attempt; `best.json` only moves strictly up.

## What was missing

Penguin Optimizer keeps Reference State via pre-edit snapshots and restores on reject.  
Workbench already had:

- L8 red-not-green (`has_blocking_quality` → never `completed_green` on blocking)
- `score_package` + `integrity_floor` (evidence block → total 0)
- `maybe_update_best` (history all attempts; best only on `score > best`)

Gap: paper.md was overwritten in place across rewrite rounds with no file restore.

## Behavior (minimal)

```text
round N with expand|degrade:
  1. copy Manuscripts/generated/{slug}_full_pipeline_paper.md
       → state/runs/{loop_id}/mutable_snapshot/round_N_paper.md
  2. FullPaperPipeline rewrite tail (Candidate)

package / score:
  3. score_package → maybe_update_best
       history.jsonl  += attempt   (always)
       best.json      = payload    (only if score strictly > best)
       best_paper.md  = paper bytes (only on promote)
  4. if not better_than_best AND cand_score < reference_score:
       restore paper from:
         loop accepted_paper.md
         → last pre-edit round_N_paper.md
         → state/evolve_archive/best_paper.md
       write loop_dir/rollback.json
       keep rejected bytes under mutable_snapshot/rejected_*_paper.md
```

Reference score = loop `_accepted_score` if set, else `state/evolve_archive/best.json` score.  
Ties (`cand == ref`) do **not** restore files (scoreboard still refuses promote; only regressions roll back bytes).

## Paths

| Artifact | Path |
|----------|------|
| Pre-edit snapshot | `state/runs/continuous_loop_*/mutable_snapshot/round_N_paper.md` |
| Accepted Reference (loop) | `.../mutable_snapshot/accepted_paper.md` |
| Rollback audit | `state/runs/continuous_loop_*/rollback.json` |
| Attempts log | `state/evolve_archive/history.jsonl` |
| Best score only ↑ | `state/evolve_archive/best.json` |
| Best paper bytes | `state/evolve_archive/best_paper.md` |
| Best pointers | `state/evolve_archive/best_pointers.json` |

## Invariants kept (do not weaken)

- `integrity_floor`: `evidence_integrity_blocked` → quality component 0 and total score 0
- Red-not-green: blocking verdicts forbid `completed_green` (`has_blocking_quality` + package safety net)
- Rollback never rewrites quality JSON, verdicts, or gate thresholds

## Smoke (2026-08-06)

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板
# unit helpers
PYTHONPATH=. python3 -c "..."   # UNIT_SMOKE_PASS (snapshot + rollback + archive)

# full loop no LLM
PYTHONPATH=. python3 -c "
from runtime.continuous_loop import ContinuousEmpiricalLoop
ContinuousEmpiricalLoop(max_rounds=2, use_llm=False).run()
"
# Observed: pre-rewrite snapshot at round 2; status halted_honest;
# score 87.5 better_than_best=false with no rollback (score did not drop vs best)
```

## Not in this slice

- tar.gz whole-state snapshots
- mid-round score before LaTeX (package-time score only; PDF component needs package)
- scoreboard purity (history still logs rejects; best.json is the accepted board)
- version integer on mutable blob
