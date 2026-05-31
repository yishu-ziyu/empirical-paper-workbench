# CGSS Draft PDF Preflight

## Stage

P6-J9 renders the CGSS exploratory paper draft into a local draft PDF preflight artifact.

User-facing effect: this node gives the product a concrete file the user can open and read as an export candidate, while keeping the result in draft review state.

## BDD Behaviors

### Behavior 1: Renders a PDF from the exploratory paper

Given the exploratory paper Markdown exists
When P6-J9 runs
Then it creates `Submissions/cgss_social_capital_happiness/paper.pdf` and records `pdf_preflight_ready`.

Business rule: after full-paper assembly, the user should be able to inspect an actual rendered artifact, not only Markdown.

### Behavior 2: Records renderer evidence

Given the renderer runs
When the preflight JSON is inspected
Then it records renderer engine, return code, PDF path, existence, and byte size.

Business rule: export readiness must be auditable from local evidence.

### Behavior 3: Falls back to HTML if PDF rendering fails

Given the PDF renderer fails but HTML rendering succeeds
When P6-J9 runs
Then it records `html_preflight_ready_pdf_failed` and routes repair tasks for the PDF environment.

Business rule: the product should preserve a reviewable fallback without pretending PDF export succeeded.

### Behavior 4: Blocks missing paper input

Given the exploratory paper Markdown is missing
When P6-J9 runs
Then it returns `blocked_missing_exploratory_paper` and writes no PDF artifact.

Business rule: export preflight cannot proceed without a source draft.

### Behavior 5: Does not create a formal package

Given P6-J9 completes successfully
When outputs are inspected
Then formal manuscript, verified bibliography, formal package, and `state/product/*` remain unchanged.

Business rule: draft PDF preflight is not final package delivery.

## Boundary Conditions

- Current real run creates `Submissions/cgss_social_capital_happiness/paper.pdf`.
- Current real PDF size is `187318` bytes.
- Current renderer is `pandoc+xelatex` with returncode `0`.
- Current status is `pdf_preflight_ready`.
- The next stage should be human PDF review, method gate review, or revision queue generation, not formal writeback.
