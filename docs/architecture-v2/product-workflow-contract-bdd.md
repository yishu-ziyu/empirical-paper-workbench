# Product Workflow Contract BDD

Date: 2026-05-12

## Purpose

This contract resets the product around the empirical-paper workflow rather than raw backend observability objects.

The UI must guide the user through research decisions in this order:

1. Dataset
2. VariableRoleSet
3. ResearchQuestion
4. DesignSpec
5. RunPlan
6. Run
7. Results
8. Draft
9. Review and Export

## Behavior 1: Home Shows Next Research Decision

Given a project has a local dataset
And variable roles have not been confirmed
When the user opens Workspace Home
Then the primary next action is "confirm_variable_roles"
And the page does not make run selection the primary action.

Business rule: the product must guide the researcher to the next required decision, not expose run logs first.

## Behavior 2: Workflow Contract Blocks Full Run Before Required Decisions

Given a project has no confirmed VariableRoleSet
And no confirmed DesignSpec
When the API returns project overview
Then `workflow_contract.run_readiness.can_start_full_run` is false
And blockers include `variable_roles_unconfirmed`, `design_unconfirmed`, and `run_plan_missing`.

Business rule: execution cannot be the user's main path until data/design decisions are explicit.

## Behavior 3: Data And Design Is A Single Product Workspace

Given the user opens the data workspace
When datasets are available
Then the primary action is to inspect and confirm variable roles
And the dataset card does not directly start a run as the primary workflow.

Business rule: dataset selection feeds role/design confirmation before execution.

## Behavior 4: Execution Starts With Run Plan Preflight

Given required decisions are incomplete
When the user opens Execution
Then the page shows Run Plan preflight and blockers before run logs
And starting a run is presented as blocked or development-only, not the main product action.

Business rule: users must see what will be run before execution starts.

## Behavior 5: Logs Are Evidence, Not Product Center

Given a run exists
When the user views Execution
Then Step Board and Event Stream are available as evidence
But the primary screen context remains the run plan, blockers, gates, and current decision.

Business rule: observability supports the workflow; it does not replace the workflow.

## Boundary Conditions

- A dry-run may remain available as a development shortcut, but it must not be the main product CTA when required decisions are missing.
- Existing observability logic can be reused, but it must sit below the workflow contract.
- Mock data must still show `evidence_level=mock`.
- Local files must show `evidence_level=local_file`.
- Real runs must show `evidence_level=local_execution`.
