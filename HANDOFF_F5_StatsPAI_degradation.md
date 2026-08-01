# Handoff: F5 - StatsPAI 降级单元测试

## 目标
为 cleaning 模块的 StatsPAI 降级场景编写单元测试，确保 StatsPAI 不可用时 pipeline 正确回退到 pandas 且记录日志警告。

## 背景
- cleaning 模块（balance.py, outliers.py, missing.py）使用 lazy import + try/except 模式
- 当 StatsPAI 不可用时静默降级到 pandas，上次修复已添加 `logging.warning` 和 `stats_pai_used` 字段
- 现有测试在 `agent/tests/test_balance.py` 等文件中，但未覆盖 StatsPAI 降级场景

## 具体改动

### 1. 新建测试文件
在 `agent/tests/` 下创建 `test_stats_pai_degradation.py`，覆盖：

- **测试 A：balance.py StatsPAI 降级**
  - mock `sp.balance_panel` 抛出异常
  - 验证 `BalanceStep.run()` 回退到 pandas
  - 验证报告中有 `stats_pai_used: false`

- **测试 B：outliers.py StatsPAI 降级**
  - mock `sp.winsorize` 抛出异常
  - 验证 `OutliersStep.run()` 回退到 pandas
  - 验证报告中有 `stats_pai_used: false`

- **测试 C：missing.py StatsPAI 降级**
  - mock `sp.impute` 抛出异常
  - 验证 `MissingStep.run()` 回退到 pandas
  - 验证报告中有 `stats_pai_used: false`

- **测试 D：StatsPAI 正常路径**
  - 不 mock StatsPAI（真实调用）
  - 验证 `stats_pai_used: true`
  - 注意：此测试在 StatsPAI 未安装的 CI 环境中可能跳过

### 2. 运行测试
```bash
cd agent && source .venv/bin/activate && python -m pytest tests/test_stats_pai_degradation.py -v
```

### 3. 确认所有现有测试通过
```bash
cd agent && source .venv/bin/activate && python -m pytest tests/ -q
```

## 依赖
- 前置：无（独立任务，只涉及 agent/tests/ 目录）
- 不影响其他 F1-F4 任务

## 验收标准
- [ ] 测试 A 通过：balance.py StatsPAI 降级到 pandas 并记录 stats_pai_used: false
- [ ] 测试 B 通过：outliers.py StatsPAI 降级到 pandas 并记录 stats_pai_used: false
- [ ] 测试 C 通过：missing.py StatsPAI 降级到 pandas 并记录 stats_pai_used: false
- [ ] 测试 D 通过或跳过（StatsPAI 可用时通过）
- [ ] 所有 agent 端测试（342+）仍然通过