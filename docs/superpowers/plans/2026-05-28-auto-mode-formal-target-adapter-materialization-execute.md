# Auto Mode Formal Target Adapter Materialization Execute Gate Plan

Date: 2026-05-28

## Node Goal

P7-Q consumes the P7-P adapter materialization preflight and provides an explicit `dry-run/materialize` command gate.

This is the first node that can create candidate target files, but only when the preflight is ready and the command is explicitly confirmed with reviewer metadata. Candidate targets remain outside `state/product` and do not mutate the formal manuscript sources, bibliography, project bibliography, DesignSpec, RunPlan, PDFs, DOCX, model outputs, or statistical execution artifacts.

## BDD Behaviors

### Behavior 1: Ready preflight supports dry-run materialization planning

Given P7-P materialization preflight is ready
When Auto Mode runs adapter materialization execute in `dry-run` mode
Then the status is `adapter_materialization_dry_run_ready`
And materialization operations are listed
And no candidate target is written.

Business rule: ready preflight 仍然必须先能 dry-run 审阅，不能默认创建 target。

### Behavior 2: Current blocked preflight blocks materialization

Given the current P7-P preflight is blocked
When Auto Mode runs adapter materialization execute
Then the status is `blocked_by_materialization_preflight`
And no materialization operations are produced.

Business rule: P7-Q 不能绕过 P7-P/P7-O 的 manifest 阻断。

### Behavior 3: Materialize requires explicit confirmation

Given P7-P preflight is ready
When Auto Mode runs in `materialize` mode without `--confirm-materialize`
Then it blocks with a missing confirmation reason.

Business rule: 真实 candidate target 写入必须有显式确认。

### Behavior 4: Materialize requires reviewer and note

Given P7-P preflight is ready
And `--confirm-materialize` is present
But reviewer or note is missing
When Auto Mode runs in `materialize` mode
Then it blocks with materialization metadata reasons.

Business rule: 产生 candidate target 文件必须留下可追溯的人和说明。

### Behavior 5: Confirmed materialize writes candidate targets and manifest only

Given P7-P preflight is ready
And source artifacts exist
And `--confirm-materialize`, reviewer, and note are present
When outputs are written
Then candidate target files and a materialization manifest are written
And no formal state or `state/product` file is written.

Business rule: P7-Q 只把已审阅 source materialize 到 candidate target 目录，不把它提升为正式产品状态。

### Behavior 6: Missing source or existing target blocks materialization

Given P7-P preflight is ready
But a source artifact is missing or a candidate target already exists
When Auto Mode builds materialization execute
Then it blocks before writing any target file.

Business rule: materialization 不能覆盖已有 target，也不能从缺失 source 猜内容。

### Behavior 7: CLI default reflects current blocked preflight

Given the current repository has a blocked P7-P materialization preflight
When the CLI runs with default paths
Then it writes a blocked materialization execute report
And it creates no candidate target files.

Business rule: 当前真实状态继续停在 P7-P blocked，不产生 candidate target 或正式层副作用。

## Boundary Conditions

- Requires `p7.auto_mode_formal_target_adapter_materialization_preflight.v1`.
- Requires `status=ready_for_adapter_materialization_review`.
- Requires `can_request_adapter_materialization=true`.
- Requires `requires_explicit_materialize_command=true`.
- Requires `mode=materialize`, `--confirm-materialize`, reviewer, and note before candidate target writes.
- Requires source artifact paths to exist and candidate target paths not to exist.
- Candidate targets can be written only under the paths declared by preflight.
- No `state/product/*` writeback.
- No PDF/DOCX render.
- No model execution or statistical artifact overwrite.

## Verification

- RED: `python3 -m unittest tests.test_auto_mode_formal_target_adapter_materialization_execute -v` fails before implementation because `Program.workbench.auto_mode_formal_target_adapter_materialization_execute` does not exist.
- GREEN: target tests pass after minimal materialization execute implementation.
- Real run writes `Results/json/auto_mode_formal_target_adapter_materialization_execute.json` and `Reviews/auto_mode_formal_target_adapter_materialization_execute.md` with current status blocked by P7-P preflight.
