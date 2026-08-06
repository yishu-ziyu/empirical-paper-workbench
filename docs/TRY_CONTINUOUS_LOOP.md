# 试用：Continuous Empirical Loop（主路径）

## 主命令

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板
set -a; source .env.local; set +a
export MINIMAX_CN_API_KEY="${MINIMAX_API_KEY:-$MINIMAX_CN_API_KEY}"

# 主路径：evaluate→learn 回炉（默认 3 轮）
# 默认 LLM = Grok 4.5（provider=grok）
PYTHONPATH=. python3 -m Product.cli continuous-loop --llm --max-rounds 3

# Pi 能拍多少拍多少（loop 内写稿仍走 Grok；Pi 仅 learn 助攻/收尾）
PYTHONPATH=. python3 -m Product.cli agent-pi --loop --max-rounds 3 "跑通父母教育工资论文 Continuous Loop"
```

鉴权见 `docs/SETUP_GROK.md`。


确定性（无 LLM，仍有 L8 expand fallback）：

```bash
PYTHONPATH=. python3 -m Product.cli continuous-loop --no-llm --max-rounds 2
```

## 状态语义（禁止红灯 completed_green）

| status | 含义 |
|--------|------|
| `completed_green` | quality=`ready_for_review` 且 REPRO_OK |
| `halted_honest` | 诚实停（残红 / 硬失败 / 熔断）+ 仍给 package |
| `max_rounds` | 轮次用尽仍未绿 |
| `failed` | 无包可交 |

## 产物

- `state/runs/continuous_loop_*/loop_state.json`
- `state/runs/continuous_loop_*/round_*_evaluate.json` / `round_*_learn.json`
- `Results/json/parent_education_wage_continuous_loop_latest.json`
- 论文：`Manuscripts/generated/parent_education_wage_full_pipeline_paper.md`

## 与线性 full-pipeline

`full-pipeline` 是内环 10 步 runner。
产品主路径是 `continuous-loop`（L8）。
