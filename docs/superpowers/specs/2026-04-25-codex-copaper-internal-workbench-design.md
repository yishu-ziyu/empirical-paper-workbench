# Codex CoPaper Internal Workbench Design

## 1. Decision

This system will be designed with **B as the final architecture target** and **A as the first mandatory user experience**.

- **A experience:** the first working version must run on the user's real thesis repository and make the user feel the end-to-end value immediately.
- **B architecture:** the system must be portable and reusable for future empirical economics projects, not a one-off thesis script.
- **No website requirement:** the product experience lives inside Codex. A browser UI can exist later, but it is not required for the core product.
- **Codex-only driver:** the orchestration assumes Codex is the model driver. No extra external LLM backend is required for the system to be valid.

The practical target is a Codex-native version of a CoPaper-like workflow: from local data and literature to research plan, empirical execution, review, drafting, and Word output.

## 2. Product Goal

The product goal is not "generate text". The product goal is to run an empirical economics paper workflow as an inspectable research operating system.

The user should be able to give Codex:

- a project repository path
- one or more data paths
- one or more literature paths
- optional school or journal formatting rules
- a loose research direction or no fixed topic yet

Then the system should produce:

- source inventory
- literature analysis
- research question candidates
- empirical strategy
- modeling plan
- executable scripts or confirmed existing scripts
- results index
- independent review report
- manuscript draft
- formatted Word output

Every important intermediate artifact must be written to disk.

## 3. First Real Target

The first real target project is:

`/Users/mahaoxuan/Desktop/学术灵感项目_2026-04-07/final`

The first user-facing experience must run against this repository. The system must treat it as the source of truth, not as a template copy.

Known project facts:

- The project is already far along.
- The thesis main line is industrial robots and labor reallocation.
- The empirical strategy is Bartik IV.
- CFPS is the outcome layer.
- CLDS is the mechanism layer.
- CGSS is concept calibration and comparison with Fang-style matching efficiency framing.
- The paper must respect the three-layer matching distinction:
  - strict matching efficiency is not directly identified
  - matching quality proxies can be studied
  - skill-post mismatch and allocation quality can be studied

The workbench must preserve this project logic rather than flattening it into a generic "labor market matching" story.

## 4. Non-Goals

The first implementation will not build:

- a public website
- accounts, billing, teams, or cloud sync
- a general LLM gateway
- a fake all-purpose paper generator that ignores data and evidence
- a new thesis repository that replaces the existing one

The system can later expose a website or graphical shell, but the core product must work from Codex first.

## 5. System Shape

The system has five layers.

### 5.1 Project Adapter Layer

This layer understands a local research project.

Responsibilities:

- detect project layout
- register data paths
- register literature paths
- register manuscript paths
- register output paths
- detect existing scripts and results
- create workspace run folders without damaging the original project

For the first thesis project, the adapter must understand:

- `01_data`
- `02_code`
- `03_results`
- `04_paper`
- `05_reference`
- `06_workspace`
- `literature`
- `state`

For future projects, the adapter should allow explicit mapping in a config file.

### 5.2 Evidence Layer

This layer turns local materials into inspectable evidence packets.

Responsibilities:

- scan datasets without rewriting originals
- summarize variables and file metadata
- scan Zotero, PDF folders, BibTeX, and local literature directories
- deduplicate literature by file hash, title, DOI, and manual aliases when possible
- connect literature evidence to paper sections and empirical claims

Required artifacts:

- `source_inventory.json`
- `dataset_inventory.json`
- `literature_inventory.json`
- `literature_clusters.json`
- `claim_evidence_map.json`

### 5.3 Multi-Agent Workflow Layer

This layer provides the CoPaper-like role separation.

Required agents:

- `Supervisor`
- `PreparationAgent`
- `LiteratureAgent`
- `ResearchStrategistAgent`
- `ModelingAgent`
- `VisualizationAgent`
- `WritingAgent`
- `ReviewerAgent`
- `FormatterAgent`

The existing `Supervisor + 4 agents + Reviewer` prototype is not enough for the final architecture. It must be expanded so that literature analysis, research strategy, formatting, and review are first-class roles.

The core rule is that writing and review must be separated. The `WritingAgent` cannot approve its own output.

### 5.4 Execution Layer

This layer runs empirical work.

Responsibilities:

- call existing project scripts when they already exist
- call StatsPAI when a Python-native analysis is appropriate
- call Stata when the project already depends on Stata `.do` files
- preserve logs, result files, and model diagnostics
- keep every run reproducible through a manifest

Required artifacts:

- `empirical_plan.md`
- `analysis_run_manifest.json`
- `modeling_report.json`
- `results_index.json`
- `diagnostics_report.md`

### 5.5 Manuscript Assembly Layer

This layer writes and formats the paper.

Responsibilities:

- generate Markdown manuscript drafts
- generate LaTeX when useful as an intermediate format
- export stable Word documents
- apply school formatting rules for the thesis project
- preserve citations and result references
- write review comments and revision logs

Required artifacts:

- `paper_draft.md`
- `paper_draft.tex`
- `paper_draft.docx`
- `review_report.md`
- `revision_plan.md`
- `formatting_report.md`

## 6. Run Folder Contract

Each full workbench run must create a folder:

`06_workspace/runs/<run_id>/`

For projects without `06_workspace`, the adapter may create:

`workspace/runs/<run_id>/`

The first thesis project must use `06_workspace/runs/<run_id>/`.

Required structure:

```text
06_workspace/runs/<run_id>/
├── 00_intake/
│   ├── project_profile.json
│   └── user_goal.md
├── 01_sources/
│   ├── source_inventory.json
│   ├── dataset_inventory.json
│   └── literature_inventory.json
├── 02_literature/
│   ├── literature_clusters.json
│   ├── core_literature_brief.md
│   └── claim_evidence_map.json
├── 03_strategy/
│   ├── research_plan.md
│   ├── identification_plan.md
│   └── empirical_plan.md
├── 04_modeling/
│   ├── analysis_run_manifest.json
│   ├── modeling_report.json
│   └── diagnostics_report.md
├── 05_results/
│   ├── results_index.json
│   ├── table_plan.md
│   └── figure_plan.md
├── 06_writing/
│   ├── paper_draft.md
│   └── section_status.json
├── 07_review/
│   ├── review_report.md
│   ├── revision_plan.md
│   └── reviewer_decision.json
├── 08_final/
│   ├── paper_draft.tex
│   ├── paper_draft.docx
│   └── formatting_report.md
└── run_manifest.json
```

This folder is the main observable product experience inside Codex.

## 7. Handoff Schema

Every agent must write a handoff packet.

Required fields:

```json
{
  "run_id": "2026-04-25T120000",
  "agent": "LiteratureAgent",
  "stage": "02_literature",
  "inputs": [],
  "outputs": [],
  "claims": [],
  "risks": [],
  "next_agent": "ResearchStrategistAgent",
  "status": "completed"
}
```

Agent-specific packets may add fields, but the shared fields must remain stable.

## 8. Supervisor Policy

The `Supervisor` is responsible for:

- creating the run folder
- selecting the next agent
- checking that required artifacts exist
- stopping the run when a blocking condition appears
- writing `run_manifest.json`
- keeping review separate from writing
- recording whether the run is exploratory, drafting, revision, or formatting

The `Supervisor` must not silently skip failed stages. Failed stages should produce a failure packet that explains the blocking file, command, or missing input.

## 9. Agent Responsibilities

### PreparationAgent

Builds the project profile.

Inputs:

- project path
- optional user goal
- existing `state` files
- known source registry

Outputs:

- `project_profile.json`
- `user_goal.md`
- `preparation_handoff.json`

### LiteratureAgent

Builds the literature evidence base.

Inputs:

- `literature`
- Zotero path if registered
- PDF folders if registered
- existing reference files

Outputs:

- `literature_inventory.json`
- `literature_clusters.json`
- `core_literature_brief.md`
- `claim_evidence_map.json`
- `literature_handoff.json`

### ResearchStrategistAgent

Turns sources and literature into research direction.

Inputs:

- `project_profile.json`
- `dataset_inventory.json`
- `core_literature_brief.md`
- existing thesis logic

Outputs:

- `research_plan.md`
- `identification_plan.md`
- `empirical_plan.md`
- `strategy_handoff.json`

### ModelingAgent

Runs or audits empirical execution.

Inputs:

- `empirical_plan.md`
- existing code
- available data
- StatsPAI or Stata availability

Outputs:

- `analysis_run_manifest.json`
- `modeling_report.json`
- `diagnostics_report.md`
- `modeling_handoff.json`

### VisualizationAgent

Organizes results into publication-ready tables and figures.

Inputs:

- `modeling_report.json`
- existing `03_results`
- existing figure scripts and outputs

Outputs:

- `results_index.json`
- `table_plan.md`
- `figure_plan.md`
- `visualization_handoff.json`

### WritingAgent

Writes the manuscript draft from evidence and results.

Inputs:

- `research_plan.md`
- `identification_plan.md`
- `results_index.json`
- `claim_evidence_map.json`

Outputs:

- `paper_draft.md`
- `section_status.json`
- `writing_handoff.json`

### ReviewerAgent

Reviews the draft independently.

Inputs:

- `paper_draft.md`
- evidence packets
- result packets
- formatting rules

Outputs:

- `review_report.md`
- `revision_plan.md`
- `reviewer_decision.json`
- `review_handoff.json`

The reviewer can return:

- `approve`
- `revise_minor`
- `revise_major`
- `block`

### FormatterAgent

Exports the final document.

Inputs:

- approved or revised draft
- formatting rules
- citation files

Outputs:

- `paper_draft.tex`
- `paper_draft.docx`
- `formatting_report.md`
- `formatter_handoff.json`

## 10. Review Loop

The review loop must support at least two iterations.

Minimum loop:

1. `WritingAgent` writes `paper_draft.md`.
2. `ReviewerAgent` writes `review_report.md`.
3. If reviewer returns `revise_minor` or `revise_major`, `WritingAgent` writes a revised draft.
4. `ReviewerAgent` reviews the revised draft.
5. `Supervisor` records the final decision.

The first implementation may cap the loop at two review passes.

## 11. Codex Experience

The product should feel like this inside Codex:

```text
User: Run the full workbench on my thesis project.

Codex:
1. Creates a run folder.
2. Scans sources.
3. Reads literature inventory.
4. Builds research and empirical plans.
5. Runs or audits empirical scripts.
6. Writes a draft.
7. Runs independent review.
8. Exports Word.
9. Reports exact files and blockers.
```

The user should not need to click through a website for this first experience.

## 12. A Experience Acceptance Criteria

The first usable A version is complete only when it can run on:

`/Users/mahaoxuan/Desktop/学术灵感项目_2026-04-07/final`

and produce a full run folder with:

- `00_intake/project_profile.json`
- `01_sources/source_inventory.json`
- `01_sources/dataset_inventory.json`
- `01_sources/literature_inventory.json`
- `02_literature/literature_clusters.json`
- `02_literature/core_literature_brief.md`
- `03_strategy/research_plan.md`
- `03_strategy/identification_plan.md`
- `03_strategy/empirical_plan.md`
- `04_modeling/modeling_report.json`
- `04_modeling/diagnostics_report.md`
- `05_results/results_index.json`
- `06_writing/paper_draft.md`
- `07_review/review_report.md`
- `07_review/revision_plan.md`
- `08_final/paper_draft.docx`
- `run_manifest.json`

The run is not accepted if it only creates placeholder files.

## 13. B Architecture Acceptance Criteria

The architecture is B-ready only when:

- project paths are configurable
- project layout mapping is explicit
- agents communicate through stable handoff packets
- runs are stored under a stable run folder contract
- literature and data inventory logic does not depend on one hard-coded thesis
- the thesis project is implemented as the first adapter profile, not as the whole system
- tests can create a temporary project and execute a full dry run

## 14. Integration with Existing Prototype

Existing prototype pieces should be reused where useful:

- `Product/backend/orchestrator.py`
- `Product/backend/orchestration_schema.py`
- `Product/backend/run_store.py`
- `Program/run_paper.py`
- `Program/export_docx.py`
- `Program/workbench/*`

But the current prototype must be upgraded in three ways:

- expand from four agents to the full research workflow roles
- support a real local project path, especially the thesis repository
- write run artifacts into the target project workspace, not only the template product repository

## 15. Implementation Order

The implementation should proceed in four phases.

### Phase 1: Core Run Contract

Build the run folder, manifest, project adapter, and source inventory.

This phase makes the workbench observable.

### Phase 2: Research Intelligence

Build literature inventory, literature clusters, research plan, and empirical plan.

This phase makes the workbench useful before modeling.

### Phase 3: Execution and Results

Connect existing scripts, StatsPAI, Stata/Python execution, result indexing, and diagnostics.

This phase makes the workbench empirically grounded.

### Phase 4: Writing, Review, and Word

Build draft assembly, independent review loop, revision plan, and Word export.

This phase makes the workbench feel like CoPaper inside Codex.

## 16. Testing Requirements

The first plan must include tests for:

- project adapter detects the thesis layout
- run folder is created with expected directories
- handoff packets validate against schema
- supervisor stops on missing required inputs
- dry run completes without real data mutation
- reviewer cannot be the same logical agent as writer
- Word export path is recorded even if formatting is incomplete

Tests must not mutate the user's original raw data.

## 17. Quality Bar

The system is not done when it "runs". It is done when the user can inspect the run folder and understand:

- what evidence was used
- what data was available
- what literature supported the claims
- what strategy was recommended
- what models were run or audited
- what results were produced
- what the reviewer rejected or approved
- where the Word document is

This is the standard needed to approach CoPaper-level usefulness without building a website.

