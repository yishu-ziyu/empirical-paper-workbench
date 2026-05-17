# P2-V Agent Task Dispatch Audit BDD

## 背景

Agent Task Queue 是把已批准的 SupervisorPlan 拆成可执行任务的草案，但创建队列不等于允许执行。每个任务必须经过人工派工审阅，才能进入后续执行后端选择和真实运行。派工审阅只改变 `state/product/agent_task_queue.json`，不能篡改 ResearchQuestion、VariableRoleSet、DesignSpec、RunPlan 或 SupervisorPlan。

## 行为用例

### Scenario 1: Queue item cannot be dispatched before human audit

Given an Agent Task Queue exists with task "data_profile"  
And the task status is "queued"  
When the user requests task dispatch status  
Then the task is blocked by "dispatch_review_required"  
And no execution backend is called

业务规则：队列草案只是派工建议，不是执行许可。默认状态必须明确告诉用户“还差人工派工审阅”。

### Scenario 2: User approves a queue item for dispatch

Given an Agent Task Queue exists with task "data_profile"  
And the task has input evidence and output requirements  
When the user approves dispatch with note "数据画像任务可以执行"  
Then the task status becomes "reviewed_for_dispatch"  
And the dispatch review records reviewer, note, timestamp, and evidence level "local_file"

业务规则：批准派工必须留下本地文件证据，后续执行后端只能消费已审阅任务。

### Scenario 3: User rejects a queue item

Given an Agent Task Queue exists with task "design_review"  
When the user rejects dispatch with note "识别策略不完整"  
Then the task status becomes "blocked"  
And the task cannot be executed until a new review decision is made

业务规则：人工可以阻断任务，阻断原因必须出现在任务摘要层，而不是藏在审计日志里。

### Scenario 4: Dispatch audit does not mutate research state

Given ResearchQuestion, VariableRoleSet, DesignSpec, RunPlan, and SupervisorPlan files exist  
When a queue item is approved for dispatch  
Then none of those files are modified

业务规则：派工审阅只审阅任务，不替用户改变量角色、识别设计或执行计划。

### Scenario 5: Frontend keeps task details collapsed by default

Given the queue contains multiple tasks  
When the Overview page renders the Agent Task Queue  
Then each task shows status, owner, blockers, and one dispatch action area  
And input evidence, output requirements, risk flags, and audit log remain collapsed by default

业务规则：默认只显示用户做决策所需的摘要信息，避免把证据 JSON、日志和长风险说明铺满屏幕。

## 边界条件

- P2-V 不启动真实执行后端。
- P2-V 不修改 ResearchQuestion / VariableRoleSet / DesignSpec / RunPlan / SupervisorPlan。
- P2-V 允许 `approve`、`reject`、`needs_revision` 三类人工派工结论。
- `reviewed_for_dispatch` 表示通过派工审阅，但仍需要后续 P2 阶段绑定实际执行后端。
