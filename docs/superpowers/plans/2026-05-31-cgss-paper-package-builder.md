# CGSS Paper Package Builder

## Stage

P6-M collects the current CGSS Rev1 draft, rendered PDF, evidence package, literature packet, method gate, reviewer report, revision queue, reproducibility README, and manifest into one reviewable paper package.

User-facing effect: this node gives the product a single folder that a human can open for acceptance review, instead of asking them to inspect scattered files across Manuscripts, Results, Reviews, and Submissions.

## BDD Behaviors

### Behavior 1: Builds a manifest for a reviewable package

Given the Rev1 draft, PDF, evidence package, literature packet, method gate, reviewer report, and revision queue exist
When P6-M runs
Then it records `needs_human_paper_package_review`, `rendered_artifact=paper.pdf`, and 9 package files.

Business rule: the user should receive a concrete review package with a manifest, not only a list of internal artifacts.

### Behavior 2: Writes only workspace package files

Given P6-M completes
When outputs are inspected
Then it writes files under `workspace/paper_packages/cgss_social_capital_happiness/` without formal manuscript or `state/product/*` writeback.

Business rule: package assembly is not formal acceptance.

### Behavior 3: Falls back to HTML when PDF is missing

Given the PDF is missing but an HTML preview exists
When P6-M runs
Then it records `preview.html` and warns that the PDF was missing.

Business rule: the product can still provide a reviewable artifact without pretending PDF export passed.

### Behavior 4: Blocks when review artifacts are missing

Given a required review artifact is missing
When P6-M runs
Then it records `blocked_missing_package_inputs` and names the missing target.

Business rule: a package cannot be called reviewable if the evidence or review chain is incomplete.

### Behavior 5: Marks artifact roles in the manifest

Given the package is built
When the manifest is inspected
Then it separates real-run artifacts, draft-layer artifacts, and human-review-required artifacts.

Business rule: users and agents must know which files are evidence, which are drafts, and which require human judgment.

## Boundary Conditions

- Current real run status is `needs_human_paper_package_review`.
- Current rendered artifact is `paper.pdf`.
- Current package contains 9 files.
- Current package directory is `workspace/paper_packages/cgss_social_capital_happiness/`.
- Current manifest has no missing targets.
- Current package remains draft-layer and formal writeback remains false.
