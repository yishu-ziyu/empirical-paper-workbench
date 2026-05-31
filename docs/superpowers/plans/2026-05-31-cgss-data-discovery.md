# CGSS Data Discovery

## Stage

P6-J2 discovers local CGSS data assets for the social-capital and happiness topic.

User-facing effect: this node tells the product which CGSS dataset can plausibly support the topic. It produces a DatasetBinding draft for human review. It does not decide the formal variables, method, or paper text.

## BDD Behaviors

### Behavior 1: Builds a DatasetBinding draft from readable local data

Given local CGSS `.dta` files are readable
When P6-J2 scans the configured CGSS data root
Then it recommends a dataset, records row count and field count, lists supporting documents, and marks the status as `needs_human_dataset_binding_review`.

Business rule: a new empirical topic must be tied to real local data before paper drafting.

### Behavior 2: Review text tells the human what to check

Given P6-J2 has a recommended dataset
When it renders the Markdown review
Then it asks the human to confirm the dataset, codebook or questionnaire support, and whether to proceed to variable-role review.

Business rule: the product must make the next human decision explicit instead of hiding it in raw JSON.

### Behavior 3: Blocks cleanly when no CGSS data is found

Given no readable CGSS data is available
When P6-J2 builds the report
Then it returns `blocked_no_cgss_dataset`, leaves the recommended dataset empty, and routes to data location tasks.

Business rule: missing data is a product state, not a silent failure.

### Behavior 4: Writes machine and review artifacts

Given P6-J2 has built a report
When it writes outputs
Then it creates both the JSON report and the Markdown review.

Business rule: downstream Agents need structured data, while the user needs a readable review surface.

### Behavior 5: Does not write formal paper state

Given P6-J2 completes successfully
When its outputs are inspected
Then it has not written formal variable roles, DesignSpec, RunPlan, paper text, or `state/product/*`.

Business rule: data discovery is not the same as approved dataset binding.

## Boundary Conditions

- Current real run recommends `CGSS2023.dta`.
- Current real run finds 11326 rows and 439 fields for the recommended dataset.
- Current real run also sees 2021 and 2018 CGSS candidates.
- `needs_human_dataset_binding_review` is a pause state, not a final approval.
- P6-J2 must not advance to variable-role decisions without human review.
