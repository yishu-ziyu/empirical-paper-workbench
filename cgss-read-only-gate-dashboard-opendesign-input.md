# CGSS read-only Gate Dashboard - OpenDesign input package

## Product target

Design the first product prototype for Empirical Paper Workspace v1.

This is not a paper writing tool.

This is not an AI chat product.

This is not a generic analytics dashboard.

It is an artifact-first, gate-aware workspace for empirical economics research.

The user opens an existing empirical research project and must immediately understand the current evidence chain.

The screen should answer these questions within 30 seconds:

1. What data does this research use?
2. Are the sample and variables auditable?
3. Which gate is currently blocking stronger claims?
4. What is the strongest allowed claim strength?
5. Which artifact should be fixed next?

## Concrete proof case

Use the CGSS Internet and Happiness project as the first proof case.

The app project is:

`/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`

The proof-case research workspace is:

`/Users/mahaoxuan/Desktop/经济学论文/CGSS_Internet_Happiness/`

Treat the proof case as a mixed existing workspace.

Do not treat it as idea-only.

Do not treat it as a finished paper because a PDF exists.

Do not make the PDF the hero.

## First slice scope

Design only a read-only first slice.

Do not design upload.

Do not design variable editing.

Do not design rerunning models.

Do not design manuscript writing.

Do not design journal submission.

Do not design publishing a replication package.

The purpose is to show the artifact graph, first failing gate, claim boundary, result facts, and replication readiness.

## Required landing screen modules

### 1. Workspace Overview

Show one natural-language state sentence.

Example:

`Current strongest allowed claim: descriptive. MethodGate is blocked because cluster level and sample construction are not fully auditable.`

The overview must make the research state discussable, not merely pretty.

### 2. Entry Routing

Show that this is a mixed existing workspace.

Show discovered material types:

- manuscript draft
- variable dictionary
- tables
- figures
- scripts
- review report
- replication files

The point is to explain why the system starts with Artifact Inventory instead of writing.

### 3. Artifact Inventory

Show the 9 first-class artifacts:

- DataContract
- SampleAudit
- MeasurementAudit
- DesignRegister
- MethodGate
- ResultObject
- EvidenceLedger
- ClaimAudit
- ReplicationPackage

Each artifact card must show:

- status
- missing fields
- whether it can support claims
- stale or mismatch risk
- click target to open an evidence panel

### 4. First Failing Gate

Highlight the first gate that blocks stronger claims.

Show:

- gate name
- blocking reason
- missing artifacts
- claim consequence
- one next action

This should be more prominent than generic progress.

### 5. Strongest Allowed Claim

Show exactly one of these values:

- causal
- qualified_causal
- descriptive
- exploratory
- no_claim

The value must be visibly tied to MethodGate and evidence state.

### 6. Blocked Claims

Show claims that cannot be written yet.

Each row should show:

- Claim ID
- original sentence
- why it is blocked
- allowed wording
- forbidden wording
- linked gate or artifact

Example:

Original: `Internet use improves subjective happiness.`

Allowed wording: `Internet use is associated with higher subjective happiness in the current CGSS sample.`

Forbidden wording: `Internet use improves happiness.`

### 7. Number Mismatches

Show conflicts between manuscript text, tables, and ResultObject.

If a mismatch exists, show:

- Claim ID
- ResultObject ID
- exhibit locator
- manuscript value
- result value
- resolution path

Example:

`Claim C-003 cites 0.083, but ResultObject R-007 records 0.071.`

### 8. Replication Readiness

Show whether the project can clean rerun.

A folder existing does not mean ready.

If any of these are missing, status must be not_ready or clean_rerun_required:

- run_all or master script
- environment capture
- logs
- manifest
- checksums
- data availability statement
- table or figure to script map
- clean rerun status

### 9. One Recommended Next Action

The landing screen must show only one primary CTA.

The CTA must come from the first failing gate.

Good CTA examples:

- Confirm cluster level
- Add drop reason
- Normalize main_results.json
- Bind Claim C-003 to ResultObject R-007
- Mark exhibit as diagnostic preview

Bad CTA examples:

- Generate paper
- Optimize expression
- Complete all
- Continue pipeline
- Fix everything

## Required secondary screens

Design the landing page first.

Then define how the user reaches these secondary screens:

1. Artifact Inventory
2. Data and Sample Audit
3. Design Register
4. MethodGate and Claim Boundary
5. ResultObject Viewer
6. EvidenceLedger
7. ClaimAudit Inbox
8. Exhibit Map
9. Replication Readiness

## Evidence panel interaction

Clicking any artifact card should open an evidence panel.

The panel should show:

- artifact name
- status
- source locator
- mapped files or outputs
- missing fields
- why this matters in empirical economics
- consequence for claim strength
- exact next action

## State model

Use these artifact states:

- unknown
- found
- draft
- complete
- blocked
- diagnostic_only
- claim_ready
- stale
- mismatch
- clean
- not_ready
- clean_rerun_required

Use these claim strength states:

- no_claim
- exploratory
- descriptive
- qualified_causal
- causal

Every state must attach to an artifact, gate, claim, result, exhibit, or replication object.

Never attach state to vague project progress.

## Copy rules

Use domain language.

Do not use productivity language.

Good copy:

- `MethodGate blocked because cluster level is missing.`
- `Strongest allowed claim: descriptive association.`
- `Claim C-003 cannot say improves because the current design does not support causal language.`
- `Replication Readiness: not_ready because run_all has not rebuilt Table 2 from a clean derived-output state.`

Banned copy:

- done
- ready
- generated
- pipeline complete
- AI checked
- paper score
- completion percent
- optimize expression
- generate paper
- one-click paper
- P0-P18
- agent task queue as the main progress model

## Visual direction

The visual style should feel like a research archive plus evidence-chain console.

It should not feel like an enterprise SaaS dashboard.

It should not feel like a generic analytics template.

Use warm paper surfaces, restrained borders, clear status tags, and sparse accent color.

Use mono typography for status labels, Claim ID, ResultObject ID, paths, coefficients, standard errors, p-values, N, and script locators.

Use serif typography for claim excerpts and manuscript snippets.

Do not use heavy box shadows.

Do not use bright white as the dominant surface.

Do not use colorful gradients.

Do not make KPI cards the main visual language.

## Suggested tokens

- bg.canvas: `#F7F4EE`
- bg.panel: `#FFFFFF`
- text.primary: `#1F2933`
- text.secondary: `#5B6472`
- border.default: `#D8D2C8`
- status.clean: `#2F7D32`
- status.draft: `#6B7280`
- status.blocked: `#B42318`
- status.warning: `#B7791F`
- status.mismatch: `#8B1E3F`
- status.claimReady: `#1F6FEB`
- status.diagnostic: `#6D5BD0`
- link.artifact: `#245C7A`

Use an 8px base spacing grid.

Use 16px panel spacing.

Use 24px screen gutters.

## Components to produce

Please define or render these components:

- GateBanner
- ArtifactStatusGrid
- ArtifactCard
- ArtifactInventoryRow
- EvidencePanel
- SampleFlow
- VariableCard
- ClaimBoundaryPanel
- ResultObjectTable
- MismatchCallout
- EvidenceLedgerRow
- ClaimAuditRow
- ExhibitMapCard
- ReplicationReadinessPanel
- SingleNextActionBar

## Validation tests

A good design passes these tests.

### Gate comprehension test

A PM or economist sees the overview for 30 seconds and can answer:

- what data is used
- what is blocked
- what claim strength is allowed
- what one artifact action comes next

### Claim boundary test

The sentence `internet use improves happiness` must be visibly blocked or downgraded unless MethodGate allows causal language.

The UI must show allowed wording and forbidden wording.

### Artifact traceability test

Clicking a status or claim must reveal source locator, mapped artifact, missing fields, ResultObject or exhibit binding, and consequence for claim strength.

### Number mismatch test

If Claim C-003 cites 0.083 while ResultObject R-007 is 0.071, the UI must show both values, Claim ID, result_id, and resolution path.

### Replication readiness test

A replication folder without clean rerun, manifest, or checksums must show not_ready or clean_rerun_required.

### No generic dashboard test

The design fails if it shows completion percent, P0-P18 progress, generic chat, PDF hero, word count, AI checked, pipeline complete, or multi-CTA task queues as primary UI.

### Read-only first-slice test

The first CGSS path must not have upload, edit variable, rerun model, publish package, or write manuscript as primary actions.

It may only show readiness and evidence gaps.
