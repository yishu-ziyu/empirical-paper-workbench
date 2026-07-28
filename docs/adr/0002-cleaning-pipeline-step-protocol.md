# ADR-0002: Cleaning pipeline Step protocol

- **Status**: accepted
- **Date**: 2026-07-28
- **Decision**: 为清洗管道 8 个子步骤引入统一 `CleaningStep` Protocol，签名 `(datasets, config) → (datasets, step_report)`，每步独立写 sidecar，orchestrator 统一聚合 report

## Context

T-04/T-05 完成后，清洗管道 8 个子步骤存在三类不一致：

- **签名不一致**：profiling 接收 single dict，其余接收 list；balance/audit 返回 dict，其余返回 list
- **副作用不一致**：missing/outliers 写 `.cleaned.csv` sidecar；transform/filter 直接覆盖 path；profiling/balance/audit 不写盘
- **report 碎片化**：`cleaning_report` 只含 5 key，`outliers_winsorized: True` 丢失详情；step 2/3/4/5/6 产物散落在 dataset meta，消费者需在两处拼凑

外加：
- transform/filter 链式覆盖 path，出错无法回退
- error handling 不统一（前 4 步部分无保护，后 4 步全 `except + pass` 静默吞错）
- audit 步骤名与实际执行脱节（读固定 8 步列表，不读实际执行记录）
- `__init__.py` stale（只导出 4/8 模块）
- HITL 暂停点 spec 要求但代码未实现（本 ADR 不含 HITL 实现，只为 HITL 预留接缝）

架构评审（improve-codebase-architecture session 2，2026-07-28）识别为次高优先级深化机会。

## Decision

### 1. 引入 `CleaningStep` Protocol

```python
from typing import Protocol

class CleaningStep(Protocol):
    name: str  # 步骤名，如 "profiling" / "merge" / "missing" ...

    def run(self, datasets: list[dict], config: dict) -> tuple[list[dict], dict]:
        """执行清洗子步骤。

        Args:
            datasets: 数据集 meta list（每个 dict 含 path/format/...）
            config: 该步骤的配置 dict（如 missing_strategy / transform_config）

        Returns:
            (updated_datasets, step_report):
                - updated_datasets: 更新后的数据集 meta list
                - step_report: 该步骤的产物 report（dict），由 orchestrator 聚合
        """
        ...
```

Protocol（duck typing），不强制继承。每步实现 `run` 方法 + `name` 属性即可。

### 2. 每步独立写 sidecar

每步产物写独立文件：`<workspace>/<step_name>_<index>.csv`（如 `02_missing_0.csv`）。

dataset meta 记录 `step_paths: list[str]`（按步骤顺序追加），不再链式覆盖 `path` 字段。原始数据路径始终保留在 `ds["original_path"]`。

### 3. orchestrator 统一编排 + 聚合 report

```python
def clean_data(state):
    steps: list[CleaningStep] = [ProfilingStep(), MergeStep(), MissingStep(), ...]
    datasets = state.get("uploaded_datasets", [])
    reports: list[StepReport] = []

    for step in steps:
        started_at = datetime.now()
        try:
            datasets, report = step.run(datasets, _step_config(state, step.name))
            status = "success"
        except Exception as e:
            report = {"error": str(e)}
            status = "failed"
        reports.append({
            "name": step.name,
            "status": status,
            "started_at": started_at,
            "duration": (datetime.now() - started_at).total_seconds(),
            "report": report,
        })

    cleaning_report = {"steps": reports}
    return {"cleaned_datasets": datasets, "cleaning_report": cleaning_report}
```

### 4. `cleaning_report.steps: list[StepReport]` 统一结构

```python
StepReport = {
    "name": str,           # "profiling" / "merge" / ...
    "status": str,         # "success" / "failed" / "skipped" / "paused"
    "started_at": str,     # ISO timestamp
    "duration": float,     # seconds
    "report": dict,        # 步骤产物详情（每步自由结构）
}
```

消费者遍历 `cleaning_report["steps"]` 即可拿到所有步骤状态，不再拼凑 dataset meta。

### 5. audit 从 `cleaning_report.steps` 读实际执行步骤

不再读固定 `_all_steps()` 列表。audit 步骤只记录 `status == "success"` 的步骤。

### 6. HITL 接缝预留（不含实现）

`StepReport.status` 支持 `"paused"` 值，未来 HITL 暂停时 orchestrator 写 `paused` 状态。本 ADR 不实现 HITL，但接口已预留。

## Consequences

### 正面

- **Locality**：每步实现 + report 聚合在各自模块内，orchestrator 只编排
- **Depth**：统一签名 `(datasets, config) → (datasets, report)`，新加步骤只需实现 `CleaningStep`
- **Testability**：每步可独立测（传 list + config，断言返回值），不再依赖整个 clean_data
- **可回退**：每步 sidecar 独立保留，链式覆盖消除
- **可审计**：`cleaning_report.steps` 统一结构，消费者一处遍历
- **error 透明**：失败记入 `step.status=failed`，不再静默吞错
- **HITL 预留**：`status=paused` 接缝已留

### 负面

- **破坏性**：8 个子步骤全部重写签名，测试同步更新
- **迁移成本**：dataset meta 新增 `step_paths` 字段，下游节点需适配
- **HITL 仍未实现**：本 ADR 只预留接缝，HITL 实现单独 spec

## Alternatives considered

1. **保持函数式，只统一签名** — cleaning_report 拼装逻辑仍散在 orchestrator，未解决碎片化
2. **引入 `Pipeline` 类 + 注册表** — 违反 YAGNI，LangGraph state 是 dict，类增加无谓抽象
3. **class-per-step 强制继承** — 过度抽象，Protocol 足够
4. **不写 sidecar，全内存** — 数据集可能很大，内存不可控

## Implementation

- 新建 `agent/cleaning/step.py`：定义 `CleaningStep` Protocol + `StepReport` TypedDict
- 8 个子步骤模块各定义 `<Name>Step` 类实现 Protocol
- 每步写独立 sidecar：`<workspace>/<order>_<step_name>_<index>.csv`
- `clean_data.py` 重写为 step list 编排 + 统一 try/except + 聚合 report
- `audit.py` 从 `cleaning_report["steps"]` 读实际执行步骤
- 删 `cleaning/__init__.py` 的 stale 导出
- profiling 遍历所有 datasets + merge 后再 profile
- 所有相关测试同步更新

## References

- 架构评审：improve-codebase-architecture session 2（2026-07-28）
- 词汇表：[CONTEXT.md](../../CONTEXT.md) — CleaningStep / StepReport / CleaningPipeline
- 前序 ADR：[ADR-0001](0001-split-title-and-body-chapters-in-state.md)（chapters 拆分，同一架构评审周期）
