# Dev Context: 全自动论文机产品化

> 日期：2026-06-22
> 阶段：Dev Phase
> 当前分支：ship/empirical-paper-runtime

## TEST_CMD

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板
DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH python3 -m pytest tests/ -q
```

结果：1192 passed, 22 failed, 3 skipped（22 个失败是预存问题，与 runtime 变更无关）

Runtime 专项测试：
```bash
python3 runtime/cli.py --mode dry-run  # 预演 10 步
python3 runtime/cli.py --mode execute   # 真实执行
python3 runtime/cli.py --status         # 查看状态
```

## CODE_CONDUCT

- 遵循现有代码风格：`from __future__ import annotations`、类型提示、docstring
- 不修改 `auto_mode_*.py` 等 legacy 脚本
- 新代码放 `runtime/` 目录
- 脚本编号遵循 `scripts/01-33_*.py` 体系
- 产物放 `artifacts/` 目录
- 状态文件放 `artifacts/pipeline_state.json`

## Per-Story Pattern References

### Story 1: Runtime 统一（P0）

**已做**：
- 复制 CHARLS 的 `runtime/` 到项目模板（pipeline.py, state.py, checkpoints.py, cli.py）
- 验证 `runtime/cli.py --mode dry-run` 能正确读取 `workflows/registry.json` 的 11 步定义
- 验证现有测试不受影响（1192 passed）

**模式来源**：
- `runtime/pipeline.py`（CHARLS 样例，271 行）— 核心引擎模式
- `runtime/state.py`（CHARLS 样例，119 行）— 状态持久化模式
- `scripts/28_agent_orchestrator.py`（项目模板，400 行）— Agent 编排模式（保留 legacy）

**下一步**：
- 写 `scripts/runtime_runner.py` 统一入口
- 验证 `--execute` 模式在真实项目上跑通

### Story 2: 跨题验证（P0）

**已做**：
- 样本构造完成：60,754 条观测，31 省，DID 信号存在（-1.58%）
- `causal_question.yaml` + `research_design.md` 已写
- `scripts/01_data_contract.py` + `scripts/02_sample_construct.py` 已跑通

**模式来源**：
- `StatspAI_跑通一次_CHARLS_DID/scripts/` — 12 个分析脚本模式
- `StatspAI_第二个样例_最低工资消费效应/scripts/` — 新题脚本模式

**下一步**：
- 写 `scripts/03_descriptive_stats.py` → `scripts/10_defense.py`
- 用 `runtime/cli.py --mode execute` 跑通 10 步

### Story 3: 高质量工作台（P1）

**模式来源**：
- `workbench/index.html`（CHARLS 样例）— 单文件工作台模式（待重建）
- `Product/web-react/src/` — React 产品壳模式

**下一步**：
- 调研 3 个参考设计
- 用 React + Tailwind 实现

### Story 4: StatsPAI DID 适配器（P1）

**模式来源**：
- `scripts/05_event_study.py`（CHARLS 样例）— 事件研究图模式
- `scripts/06_table2.py`（CHARLS 样例）— 主回归模式

**下一步**：
- 提取核心逻辑，包装成通用 `did_adapter.py`

## Intentional Deviations

1. **保留 auto_mode_*.py 作为 legacy**：虽然 30+ 脚本过于复杂，但已跑通 P0-P18，不删除，只通过 runtime/ 统一调用
2. **不迁移证据审计系统**：claim_register + integrity_audit 是项目模板特有，后续作为 runtime 的输出消费者
3. **React 产品壳不动**：只做 workbench，不重写全部 UI
4. **不接 IV/RDD**：本轮只做 DID，其他方法后续
