# P7-V Auto Mode Formal Target Adapter Candidate Promotion Execute Gate

## Component Effect

P7-V is the explicit execution gate after P7-U. It can promote verified candidate targets into the formal package only when the preflight is ready and the command is explicitly confirmed.

## BDD Behaviors

1. Given P7-U is ready and candidate files match the approved checks
   When the command runs in confirmed promote mode
   Then it copies candidate files into formal target paths and writes a promotion manifest.

   业务规则：只有明确确认后，候选成果才进入正式成果位置。

2. Given P7-U is ready
   When the command runs in dry-run mode
   Then it shows the promotion operations but does not copy files.

   业务规则：默认只预演，不写正式成果。

3. Given the current real P7-U output is blocked
   When the CLI runs with default paths
   Then it stays blocked and does not promote anything.

   业务规则：当前真实链路仍等待审批，不能跳过。

4. Given promote mode is missing confirmation, reviewer, or note
   When the execute gate runs
   Then it blocks before copying files.

   业务规则：正式提升必须有明确授权记录。

5. Given a candidate file is missing, changed, or the formal target already exists
   When the execute gate runs
   Then it blocks before copying files.

   业务规则：执行前必须保护候选来源和正式目标。

6. Given any P7-V report is written
   When outputs are generated
   Then only the confirmed promote path writes formal target files and manifest; it never writes `state/product/*`.

   业务规则：正式成果写入和产品状态写入分离。

## Boundary Conditions

- Default mode is dry-run.
- Confirmed promote may write only paths listed by P7-U.
- Existing formal targets are not overwritten.
- Product state remains untouched.

## Checklist

- [x] RED: add first confirmed-promote behavior test.
- [x] GREEN: implement minimal workbench execute path.
- [x] Add dry-run, blocked, metadata, file-safety, and CLI tests.
- [x] Run real blocked-state command.
- [x] Update `Tasks/todo.md` with component effect and next hop.
