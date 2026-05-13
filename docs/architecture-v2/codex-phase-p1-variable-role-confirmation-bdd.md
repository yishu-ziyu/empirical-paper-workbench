# P1-E VariableRoleSet Confirmation BDD

Date: 2026-05-13

## Context

The product reset moved the workbench away from technical panels and toward a research lifecycle. The immediate P1 gap is that `workflow_contract` still treats `VariableRoleSet` as unconfirmed even when the user is ready to confirm or adjust roles.

This phase makes variable roles a real product object, not only metadata inside a run log.

## Reference Lessons Applied

- RStudio/JupyterLab: keep the workbench shell organized around stage workspace, inspector, and execution evidence.
- Deepnote: treat each research decision as a structured block, not as free-form chat.
- OSF/DVC-like project management: preserve research objects as versioned project assets.
- MLflow/GitHub Actions: keep run logs and artifacts observable, but do not make them the primary research decision surface.
- Overleaf/Quarto: later draft writing must bind claims and sections to confirmed evidence.

## Behavior 1: API returns unconfirmed role state before save

Given a project has a local dataset but no saved VariableRoleSet  
When the frontend reads `GET /api/v1/projects/{project_id}/variable-roles`  
Then the response includes a draft role proposal from the dataset schema  
And `status` is `draft`  
And `evidence_level` is `local_file`  
And the response identifies the selected dataset path.

Business rule: the Data & Variables page must show a real role-confirmation object before execution starts.

## Behavior 2: User can save a confirmed VariableRoleSet

Given the project has a local dataset  
When the user submits outcome, treatment, controls, instruments, fixed effects, clustering unit, and a note  
Then the system writes a versioned VariableRoleSet under the project state directory  
And the saved object has `status=approved`  
And the saved object has `evidence_level=local_file`  
And the response includes a decision event with actor, action, timestamp, and note.

Business rule: variable-role confirmation must be auditable and durable across sessions.

## Behavior 3: Workflow contract reads saved VariableRoleSet

Given the project has an approved VariableRoleSet  
When the frontend reads the project overview  
Then `workflow_contract.canonical_stages.variable_roles.status` is `completed`  
And `workflow_contract.run_readiness.blockers` no longer includes `variable_roles_unconfirmed`  
And the next action moves to research design confirmation.

Business rule: the homepage and execution preflight must be driven by real project state, not hard-coded blockers.

## Behavior 4: Data & Variables renders the confirmation editor

Given the Data & Variables page opens  
When variable role state is loaded  
Then the page shows editable fields for outcome, treatment, controls, instruments, fixed effects, clustering, and note  
And the save action calls the variable-role API  
And after save it refreshes the overview contract and variable-role state.

Business rule: the user can complete the first real research decision without opening run logs or Agent chat.

## Behavior 5: Execution preflight reflects partial readiness

Given variable roles are approved but design and Run Plan are not  
When the Execution page renders preflight  
Then it still blocks full execution  
And it only shows `design_unconfirmed` and `run_plan_missing` as blockers.

Business rule: the system should visibly progress one research gate at a time.

## Boundary Conditions

- This phase does not implement the full DesignSpec editor.
- This phase does not infer perfect variable roles from arbitrary data. It only proposes roles from schema/name heuristics and lets the user confirm or adjust.
- This phase keeps evidence at `local_file` because the confirmed roles come from local dataset inspection and user decision, not a finished empirical run.
- This phase stores project-local state in `state/product/variable_roles.json`, leaving existing run observability files unchanged.
