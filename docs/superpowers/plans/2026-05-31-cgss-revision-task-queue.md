# CGSS Revision Task Queue

## Stage

P6-I12 builds a draft-layer reviewer-style revision task queue from the CGSS literature seed package, literature review draft packet, and method structure gate packet.

User-facing effect: this node turns pending literature, method, writing, and review work into a structured task board for four agent roles. It does not execute the tasks, create agent packet files, or write product state.

## BDD Behaviors

### Behavior 1: Build four-agent draft-layer queue

Given all revision input packets are reviewable
When P6-I12 builds the revision queue
Then it emits LiteratureAgent, MethodAgent, WriterAgent, and ReviewerAgent packets with queued draft-layer tasks.

Business rule: downstream agent work should be visible as a queue before execution.

### Behavior 2: Route literature inputs to LiteratureAgent

Given literature seed sources, open dependencies, and paragraph blocks exist
When P6-I12 builds the queue
Then LiteratureAgent receives source verification and literature block review tasks.

Business rule: source and literature cleanup should be owned explicitly before drafting continues.

### Behavior 3: Route method gates to MethodAgent

Given method claim gates include allowed claims and blocked methods
When P6-I12 builds the queue
Then MethodAgent receives primary-model and blocked-causal-method review tasks without permission to update DesignSpec, RunPlan, or product state.

Business rule: method decisions need review, but formal design state stays protected.

### Behavior 4: Route writing and review work without formal writes

Given section standards and claim boundaries exist
When P6-I12 builds WriterAgent and ReviewerAgent tasks
Then the tasks target review artifacts only and remain draft-layer work.

Business rule: writers and reviewers can prepare briefs, but they cannot write formal manuscript sections at this stage.

### Behavior 5: Block when required inputs are missing

Given a required literature, method, or structure input is missing or not ready
When P6-I12 runs
Then it blocks and emits no agent task queue.

Business rule: the revision queue must not be built from incomplete packets.

### Behavior 6: Preserve approval boundary

Given P6-I12 runs successfully
When it writes outputs
Then it writes only JSON/Markdown review artifacts and does not write `state/product/agent_task_queue.json` or agent packet files.

Business rule: this stage creates a queue for human approval, not executable work orders.

## Boundary Conditions

- P6-I12 consumes the literature seed package, literature review draft packet, and method structure gate packet.
- P6-I12 emits four agent packets and eight queued draft-layer tasks.
- P6-I12 keeps `promotion.allowed=false`.
- P6-I12 requires human approval before agent packet files or work orders can be generated.
- P6-I12 must not write formal manuscript, verified bibliography, DesignSpec, RunPlan, `state/product/*`, `state/product/agent_task_queue.json`, or `Reviews/agent_packets/...`.
