# CGSS Reviewer Revision Loop

## Stage

P6-L turns the CGSS exploratory paper, method gate, evidence package, and literature draft packet into a reviewer-style revision loop.

User-facing effect: this node changes the product from "the paper has method risks" to "the paper has a concrete human-reviewable revision queue." It does not approve the paper or write formal manuscript state.

## BDD Behaviors

### Behavior 1: Builds a reviewer report across required areas

Given the exploratory paper, paper assembly, P6-K method gate, result evidence, and literature packet are ready
When P6-L runs
Then it creates a reviewer report covering paper structure, literature, data, identification, results, robustness, submission standards, and human judgment.

Business rule: method risk must become readable reviewer feedback, not remain a hidden machine flag.

### Behavior 2: Builds a revision queue from method risks

Given the P6-K gate flags reverse causality and omitted-variable risks
When P6-L builds the queue
Then it creates draft-layer tasks for WriterAgent, LiteratureAgent, DataAgent, MethodAgent, and ReviewerAgent.

Business rule: every major paper risk should have an owner and an expected output before further promotion.

### Behavior 3: Generates Rev1 as a draft artifact

Given the current exploratory paper is available
When P6-L runs
Then it writes a Rev1 Markdown draft with reviewer notes, result bindings, method boundary, and revision tasks.

Business rule: Rev1 is a review artifact, not a formal manuscript writeback.

### Behavior 4: Writes only revision-loop artifacts

Given P6-L completes
When outputs are inspected
Then it writes only the reviewer report, revision task queue, and Rev1 draft.

Business rule: the revision loop must not mutate formal sections, product state, DesignSpec, RunPlan, or verified bibliography.

### Behavior 5: Blocks if the method gate is not ready

Given the method gate is missing or blocked
When P6-L runs
Then it returns `blocked_revision_loop_inputs_not_ready` and does not generate Rev1.

Business rule: the review loop cannot proceed before the method gate has produced a reviewable state.

## Boundary Conditions

- Current real run status is `needs_human_revision_review`.
- Current queue status is `needs_human_revision_queue_review`.
- Current output count is 1 reviewer report, 1 revision task queue, and 1 Rev1 draft.
- Current revision task count is `6`.
- Current reviewer finding areas count is `8`.
- Current Rev1 stays draft-layer and formal writeback remains false.
- Current revision queue path is reused from the existing output contract: `Reviews/cgss_social_capital_happiness_revision_task_queue.md`.
