# P7-W Auto Mode Formal Target Adapter Promoted Package Verification Gate

## Component Effect

P7-W verifies the formal package after P7-V has promoted candidate targets. It does not copy, repair, render, or rerun anything; it only confirms that promoted formal files exist and match the promotion manifest.

## BDD Behaviors

1. Given P7-V completed promotion and a valid promotion manifest
   When the verification gate runs
   Then it verifies each formal target path, byte count, and SHA256 hash.

   业务规则：正式成果必须能被复验，不能只相信执行命令说成功。

2. Given the current real P7-V output is blocked
   When the CLI runs with default paths
   Then it stays blocked and writes only verification report/review outputs.

   业务规则：当前真实链路未提升，不能伪造正式包已验证。

3. Given the promotion manifest is missing or invalid
   When verification runs after a completed execute report
   Then it blocks before verifying formal targets.

   业务规则：没有提升清单就不能证明正式成果来自哪次提升。

4. Given the execute report is not a completed promotion
   When verification runs
   Then it blocks before reading formal targets.

   业务规则：dry-run 或 blocked execute 不能进入正式包验证。

5. Given a promoted formal target is missing or changed
   When verification runs
   Then it reports the exact target group mismatch.

   业务规则：正式成果被删改时必须显式暴露。

6. Given execute or manifest boundary flags show unrelated writes
   When verification runs
   Then it blocks the verification result.

   业务规则：正式包验证只接受 P7-V 预期的 formal writeback，不接受 product/render/model 等越界副作用。

7. Given any P7-W report is written
   When outputs are generated
   Then it writes JSON/Markdown review only and never writes `state/product/*`.

   业务规则：验证节点不产生产品状态或新的正式内容。

## Boundary Conditions

- Expected P7-V formal writeback flags are allowed.
- Product state, rendering, model reruns, DesignSpec, RunPlan, and statistical execution writes remain blocked.
- Verification does not repair missing or changed formal targets.

## Checklist

- [x] RED: add promoted formal package verification behavior tests.
- [x] GREEN: implement minimal workbench verification path.
- [x] Add blocked, manifest, target mismatch, boundary, and CLI tests.
- [x] Run real blocked-state command.
- [x] Update `Tasks/todo.md` with component effect and next hop.
