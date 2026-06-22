# Code Review — empirical-paper-runtime dev phase

## Findings

### P2: `--auto` flag lost during runtime copy; pipeline hangs at every human checkpoint

- File: `runtime/cli.py:23-32` and `runtime/pipeline.py:105,159`
- Trigger: `cli.py` has no `--auto` argument; `Pipeline.__init__` has no `auto` parameter; checkpoint at line 159 always blocks on `input()` regardless of mode
- Impact: AC2 (cross-project validation) requires running the CFPS minimum-wage project end-to-end without manual intervention. Without `--auto`, the pipeline stops at every human checkpoint (11 times) and cannot be used in CI, cron, or batch mode. The dev-phase claim "11 steps pass with --auto" is no longer true — the flag was lost when the CHARLS runtime was copied as a fresh file set.
- Fix: **FIXED in commit 8fb52dc**. Added `--auto` to `cli.py` argument parser; added `auto: bool = False` to `Pipeline.__init__`; skip `checkpoint()` when `self.auto is True`. Also added `self.save()` to `set_running()`, `set_done()`, `set_blocked()` so `pipeline_state.json` is persisted after each step, and `_write_report()` after each successful step so `pipeline_report.md` exists for downstream gates.

### P3: Event study uses binary treatment column as `treat_time` instead of actual treatment year

- File: `runtime/adapters/did_adapter.py:142`
- Trigger: `df[treat_time_col] = df[treatment]` assigns 0/1 (binary indicator) to `__treat_time`, which `sp.event_study` then interprets as calendar years
- Impact: `sp.event_study` computes `relative_time = time - treat_time`. With binary `treat_time`, relative_time becomes `year - 0` or `year - 1`, which is meaningless. The event study either fails or produces garbage coefficients. The `treatment_year` parameter (passed correctly by CFPS scripts as 2012) is only used in the plot title, never in the calculation.
- Fix: **FIXED in commit c003ebf**. Replaced `df[treat_time_col] = df[treatment]` with `np.where(df[treatment] == 1, treatment_year, 0)` (matching the CHARLS reference at `scripts/05_event_study.py:36`). The `treatment_year` parameter is now threaded through `_run_event_study_statspai`'s signature.

## Diagnosis

The P2 and P3 findings share one root cause: **the runtime files were copied from CHARLS as originals, not from the modified versions that had been validated**. The `--auto` flag was added to cli.py/pipeline.py during the earlier fix session, but the subagent that implemented Stories 3+4 copied fresh CHARLS originals, overwriting those changes. Similarly, the adapter's `_run_event_study_statspai` was written from scratch and made the same binary-vs-year mistake that had already been fixed in the CFPS scripts.
