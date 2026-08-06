# 试用：全流程 Continuous Empirical Loop

## 一次跑通

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板
set -a; source .env.local; set +a
export MINIMAX_CN_API_KEY="${MINIMAX_API_KEY}"

PYTHONPATH=. python3 scripts/40_full_paper_pipeline_e2e.py --model MiniMax-M3
# 或
PYTHONPATH=. python3 -m Product.cli full-pipeline --llm --model MiniMax-M3
```

无 LLM：

```bash
PYTHONPATH=. python3 scripts/40_full_paper_pipeline_e2e.py --no-llm
```

## 已验证 run

- `run_id`: `full_pipeline_parent_education_wage_20260806_212153`
- 10/10 steps passed · `REPRO_OK`
- 论文：`Manuscripts/generated/parent_education_wage_full_pipeline_paper.md`
- 主结果：`Results/json/parent_education_wage_full_pipeline_main_results.json`
- 复现：`python3 replication/reproduce_parent_education_wage_full_pipeline.py`
- 摘要：`Reviews/parent_education_wage_full_pipeline_summary.md`

## 10 步合同

| 步 | 内容 |
|----|------|
| 01 design | 研究设计 / 风险 |
| 02 literature | 文献（未核验红线） |
| 03 paper_reading | 阅读协议 |
| 04 data_gate | 真实 CSV + Table1 |
| 05 causal | 真实估计 + 稳健 |
| 06 writing | 正文 + claim register |
| 07 revision | 质量门 → 修订信号 |
| 08 citation | 引用诚实门 |
| 09 replication | 独立复现 |
| 10 defense | 答辩提纲 |

## 诚实边界

- 跑通 ≠ 期刊 submission ready。  
- 文献未核验 / 识别弱 → 主张降级，不是假 PASS。  
- 产品目标是 **自动回炉** 直到课程绿，不是停在红标清单。

产品定义：`docs/PRODUCT.md`
