# 复现研究能力契约

## 进入主线的位置

“论文复现与可复现研究”进入执行链路，而不是停留在教程材料里。

```text
method_execution_result
-> reproducibility_skill_contract
-> formal_export_preflight
```

含义：模型、表格和图形跑完以后，系统必须先过复现研究门，再进入正式导出预检。

## 产品承诺

1. 原始数据只读，清洗结果写到处理后数据目录。
2. 每次运行记录环境、命令、git 状态和关键文件摘要。
3. 表格、图形、JSON、日志走标准路径，不散落在临时目录。
4. 至少有一个一键复现入口，可以重建核心产物。
5. Auto Mode 可以跑到导出预检，但不能静默把结果提升到正式层。

## 路径映射

| 通用复现结构 | 当前仓库路径 |
| --- | --- |
| raw data | `Data/Raw` |
| processed data | `Data/Final` |
| code | `Program` |
| tables | `Results/tab` |
| figures | `Results/fig` |
| structured results | `Results/json` |
| logs | `Results/logs` |
| paper | `Manuscripts` |
| formal package | `Submissions/formal_package` |

## Agent Skill 编排

| 节点 | Agent | 目标 | 时间盒 |
| --- | --- | --- | --- |
| `repro_env_lock` | VerifierAgent | 锁定 Python/R/Stata、依赖和执行后端 | 20 分钟 |
| `repro_standard_outputs` | ExecutionAgent | 核对表格、图形、JSON、日志是否进入标准路径 | 20 分钟 |
| `repro_one_command` | ExecutionAgent | 生成或验证一键复现入口 | 20 分钟 |
| `repro_audit_manifest` | ReproAgent | 生成复现审计清单和报告 | 20 分钟 |
| `repro_peer_review` | ReviewerAgent | 对复现报告和论文草稿做审稿式质询 | 20 分钟 |

## 验收门

- `raw_data_immutable`: 原始数据未被改写。
- `all_outputs_manifested`: 表格、图形、JSON、日志均进入 manifest。
- `one_command_reproduce_available`: 存在一键复现入口和说明。
- `peer_review_findings_recorded`: 复现报告经过审稿 Agent 质询。
- `human_review_before_formal_export`: 人工确认后才允许进入正式导出。

## 后端接入

- 契约模块：`Product/backend/reproducibility_skill_contract.py`
- 能力目录：`cap_reproducibility_contract`
- 运行态 JSON：`state/product/reproducibility_skill_contract.json`
- 测试：`tests/test_reproducibility_skill_contract.py`
