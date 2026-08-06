# L8 / Continuous Loop 落地记录

Date: 2026-08-06

## 结构变化

| 项 | 之前（审计） | 现在 |
|----|--------------|------|
| L1 Outer SSOT | MISSING | **PRESENT** `runtime/continuous_loop.py` |
| L8 evaluate→learn | MISSING | **PRESENT** evaluate JSON → learn plan → target_steps re-run |
| 红灯 completed | 可 | **禁止** `completed_green`（仅 ready_for_review+REPRO） |
| 主 CLI | full-pipeline | `continuous-loop` · `agent-pi --loop` |
| Pi | 旁路 chat | `--pi-assist` / `agent-pi --loop` 接环 |

## 已验证

### no-llm max_rounds=2

- loop_id: `continuous_loop_parent_education_wage_20260806_220316`
- r1 full 10 → L8 rewrite tail
- r2 expand+degrade → `halted_honest`（仍 too_thin 等）
- **未**出现红灯 `completed_green`

### llm max_rounds=3

- loop_id: `continuous_loop_parent_education_wage_20260806_220338`
- 3 轮 L8 回炉写稿
- status: `halted_honest` + package
- Pi binary: `~/.local/bin/pi` 可用

## 仍未过总结构 bar

- 双栈 `orchestrator` / `product_control_*` 尸体仍在
- 课程绿（ready_for_review）未在 demo 上打到
- H8 cross-run evolution 未接
- claim 强制 bind-or-block 未成统一 runtime 对象

## 主命令

```bash
PYTHONPATH=. python3 -m Product.cli continuous-loop --llm --max-rounds 3
PYTHONPATH=. python3 -m Product.cli agent-pi --loop --max-rounds 3 "..."
```
