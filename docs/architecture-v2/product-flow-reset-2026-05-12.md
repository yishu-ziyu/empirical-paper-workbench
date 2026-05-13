# Product Flow Reset

Date: 2026-05-12

## Why This Reset Exists

The current product is drifting because pages, APIs, and execution artifacts are being added as separate panels. That makes the system observable, but not understandable. A user should not have to infer the research workflow from run ids, JSON files, gates, and scattered cards.

The product should be designed as an empirical paper workflow, not as a dashboard of backend objects.

## Product Definition

This product is a local-first empirical paper workbench.

Its job is to help a researcher move from data to a defensible paper draft while preserving evidence, decisions, execution traces, and reproducibility.

It is not primarily:

- a generic agent dashboard
- a static project overview
- a file browser for artifacts
- a pretty wrapper around script output
- a run log viewer

The product promise is:

> Upload or select data, define the research question and variable roles, confirm an identification strategy, run the empirical workflow, review results, and export a paper plus replication package. Every claim stays traceable to data, code, model, agent, and user decision.

## Reference Product Lessons

### CoPaper

CoPaper is useful as a workflow model: it guides the user through research decisions instead of exposing raw execution machinery first. The key lesson is not visual style; it is that users should always know which decision they are making now and what the next research step is.

### StatsPAI

StatsPAI is useful as a method-engine model: statistical methods should be invoked through stable, structured APIs and return structured results. The UI must distinguish the research agent's decision from the statistical engine's output.

### Stata PAI

Stata PAI is useful as an interaction model: the user should be able to ask for analysis in research language, but the system must translate that into explicit data checks, variables, commands, outputs, and interpretation. Conversational convenience cannot replace auditability.

## Product Spine

Everything should attach to this spine:

1. Project
2. Dataset
3. Variable roles
4. Research question
5. Identification strategy
6. Model specification
7. Execution run
8. Results and diagnostics
9. Paper draft
10. Review and export
11. Replication package

If a feature does not clearly attach to one of these nodes, it is probably UI noise.

## Core User Flow

### 1. Start or Open Project

User intent: I want to work on one empirical paper.

The screen should show:

- research title or placeholder
- current stage
- next required decision
- available datasets
- latest verified output

Primary action:

- continue the next required step

Avoid:

- showing all technical panels at once
- making run selection the first visible concept

### 2. Provide Dataset

User intent: I want the system to read my data.

The screen should show:

- selected dataset
- file evidence level
- rows and columns
- variable preview
- missingness and obvious type issues
- whether this data is ready for variable-role assignment

Primary action:

- inspect variables

Required evidence:

- `evidence_level=local_file`
- file path
- file fingerprint or modification metadata
- schema snapshot

### 3. Confirm Variable Roles

User intent: I want to tell the system what each variable means in my paper.

The screen should show:

- outcome
- treatment or main explanatory variable
- controls
- instruments
- fixed effects
- clustering unit
- sample restrictions
- role confidence and source

Primary action:

- confirm or adjust roles

This is a product-level gate, not a run-log detail.

### 4. Define Research Design

User intent: I want a credible empirical strategy.

The screen should show:

- research question
- causal claim
- proposed identification strategies
- assumptions
- required tests
- model formula candidates
- data requirements

Primary action:

- approve a design plan

Avoid:

- running models before the user sees the design implications
- hiding assumptions inside metadata boxes

### 5. Preflight Execution Plan

User intent: I want to know what the system is about to run.

The screen should show:

- ordered run plan
- scripts or method calls to be generated
- expected artifacts
- HITL stops
- estimated cost or runtime
- evidence level

Primary action:

- start execution

Execution should not start from a dataset card alone once the product matures. Dataset-card run launch is acceptable only as a temporary development shortcut.

### 6. Execute and Observe

User intent: I want to monitor the run and intervene if needed.

The screen should show:

- current run status
- active step
- event stream
- blocking gates
- produced artifacts
- errors and recovery actions

Primary action:

- resolve the current blocking gate or inspect output

This is where the current execution page belongs. It should be a subordinate stage in the workflow, not the whole product center.

### 7. Review Results

User intent: I want to understand whether the empirical result is usable.

The screen should show:

- baseline table
- robustness status
- diagnostics
- assumptions checked or unchecked
- result interpretation
- risks and limitations

Primary action:

- accept results for writing or request rerun

Avoid:

- treating artifact existence as result acceptance

### 8. Generate Paper Draft

User intent: I want a paper draft grounded in the confirmed evidence.

The screen should show:

- chapter outline
- generated sections
- linked tables and figures
- claims with provenance
- missing evidence warnings

Primary action:

- review and edit section

Markdown remains the source of truth; Word is an export target.

### 9. Review and Export

User intent: I want a defensible final package.

The screen should show:

- unresolved review issues
- claim-to-evidence checks
- replication checklist
- export targets

Primary action:

- export paper and replication package

## Product Object Model

The UI and API should stabilize around these objects:

| Object | Meaning | Evidence Level |
| --- | --- | --- |
| `Project` | one empirical paper workspace | local_file |
| `Dataset` | a concrete data file and schema snapshot | local_file |
| `VariableRoleSet` | user's confirmed variable-role configuration | local_file or local_execution |
| `ResearchQuestion` | the paper's question and hypothesis | local_file |
| `DesignSpec` | identification strategy, assumptions, model specs | local_file |
| `RunPlan` | ordered execution plan before running | local_file |
| `Run` | one execution attempt | local_execution |
| `Step` | one unit of execution | local_execution |
| `Gate` | one user decision checkpoint | local_execution |
| `Artifact` | generated table, figure, draft, log, package | local_file or local_execution |
| `DraftSection` | editable manuscript section | local_file |
| `ReviewIssue` | unresolved quality or evidence issue | local_file |

Current code exposes `Run`, `Step`, `Gate`, and `Artifact` before it has properly elevated `VariableRoleSet`, `DesignSpec`, and `RunPlan`. That is why the product feels inverted.

## New Information Architecture

The UI should have five primary workspaces, not many loosely related pages:

1. `Workspace Home`
   - project status
   - next required decision
   - latest verified result

2. `Data and Design`
   - dataset
   - schema
   - variable roles
   - research question
   - identification strategy
   - model specification

3. `Execution`
   - run plan
   - active run
   - gates
   - logs
   - artifacts

4. `Results and Draft`
   - tables
   - figures
   - diagnostics
   - interpretation
   - manuscript sections

5. `Review and Export`
   - evidence audit
   - replication package
   - Word/LaTeX/Markdown export

The current seven-page navigation can remain internally during migration, but the product should be redesigned around these five workspaces.

## Screen Layout Rule

Every main screen should use the same three-zone logic:

1. Left or top: stage progress and next decision
2. Center: the current decision or work object
3. Right or bottom: evidence, audit trail, and artifacts

This prevents the current failure mode: every API response gets its own big card.

## Development Reset

Do not continue directly into P1-E implementation yet.

First create a product-level workflow contract that defines:

- canonical stages
- allowed state transitions
- required user decisions
- evidence files written at each transition
- UI workspace for each object

Then implement P1-E only inside that contract.

## Next BDD Set

The next BDD should not be "variable role adjust button works". It should be:

1. Given a project has a dataset but no confirmed variable roles,
   when the user opens the workbench,
   then the primary next action is variable-role confirmation, not run selection.

2. Given variable roles are unconfirmed,
   when the user tries to start a full empirical run,
   then the system blocks the run and shows the role-confirmation gate.

3. Given the user adjusts variable roles,
   when they save the adjustment,
   then the system writes a versioned `VariableRoleSet` and appends a decision event.

4. Given variable roles and research design are confirmed,
   when the user opens execution,
   then the system shows a preflight run plan before starting execution.

5. Given a run finishes,
   when the user opens results,
   then the primary view is result interpretation and diagnostics, with logs available as evidence, not as the main object.

## Non-Goals For The Next Iteration

- Do not add more visual panels to the current execution page.
- Do not implement arbitrary upload before the dataset object model is stable.
- Do not make Agent Console the product center.
- Do not add another run selector as a primary workflow element.
- Do not show mock states without explicit `evidence_level=mock`.

## Immediate Next Step

Write `docs/architecture-v2/product-workflow-contract-bdd.md`, then translate it into tests around journey status, next action selection, and run blocking before implementation.
