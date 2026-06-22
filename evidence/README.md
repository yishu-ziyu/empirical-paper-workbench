# evidence/ — 论文写作的反幻觉护栏（PaperSpine 4 大机制落地）

> 本目录是论文写作过程的"反幻觉护栏"。它把 PaperSpine (WUBING2023/PaperSpine) 的
> 4 大核心机制落地到本项目，作为写作前/中/后 3 个阶段的强制约束。

## 缘起

2026-06-02 在扩写 `Manuscripts/sections/main-results.md` 的过程中，模型捏造了 18 处数字
（包含 E-value 1.18、Acemoglu 美国 0.5% 弹性、Sobel 30/70% 中介分解、2005-2007 基期等），
触发了"我操！你他妈捏造数据，更过分了！"的用户反馈。

根因复盘：

1. **测试激励错位**：长度下限 + 内容压力 → 模型倾向于"补足"以达到字数。
2. **证据池未约束**：模型不知道"哪些数字有源、哪些没源"，自由发挥空间大。
3. **自审不可靠**：让 LLM 自己核对自己的输出 → 复述幻觉，不是审计。
4. **缺乏强制流水线**：没有"写作前必须有 evidence_bank、写作中必须更新 claim_register、写作后必须 audit"的硬约束。

PaperSpine 的 4 大机制恰好覆盖这 4 个根因。本目录把它们落到本项目。

## 4 大机制

| # | 机制 | 文件 | 在流水线中的位置 | 反幻觉作用 |
|---|------|------|------------------|------------|
| 1 | **evidence_bank.md** | `evidence/evidence_bank.md` | 写作前 | 提供"证据池"约束，列出所有可用证据与对应位置 |
| 2 | **claim_register.md** | `evidence/claim_register.md` | 写作中 / 写作后 | 把每个数字 / 事实声明显式绑定到 evidence_bank 的位置 |
| 3 | **integrity_audit.py** | `evidence/integrity_audit.py` | 写作后（gate） | 自动扫描 main-results.md 是否含未绑定声明、可疑 p-value、孤儿引用等 |
| 4 | **mandatory pipeline** | `evidence/pipeline.md` | 全程 | 把上面 3 个机制串成 5 阶段流水线，audit 是翻译前的硬门禁 |

## 与现有脚本的关系

本目录**不替换** `Program/workbench/` 里已有的脚本；它消费它们的输出，并提供
**人类可读** + **结构化审计** 视图：

| 现有脚本 / 产物 | evidence/ 如何消费 |
|----------------|---------------------|
| `Program/manuscript_section_evidence_bindings.py` → `Results/json/manuscript_section_evidence_bindings.json` | 27 条 section→evidence 绑定，作为 `evidence_bank.md` 第 2 层的来源 |
| `Program/manuscript_section_claim_ledger.py` → `Results/json/manuscript_section_claim_ledger.json` | 1 条 approved claim，作为 `claim_register.md` 的种子 |
| `Program/paper_quality.py` → `Results/json/paper_quality_report.json` | 论文级别长度 / 章节完整性，作为 `integrity_audit.py` 维度 1 的输入 |
| `Results/json/regression_tables.json` | 4 张回归表，是 `claim_register.md` 的数字真值源 |
| `Results/json/analysis_result.json` | 8 条 robustness findings（Oster delta*=23.47、Sensemakr RV=0.139、e-value 失败 等） |
| `Results/json/approved_findings.json` | 1 条 approved finding (ln_robot IV 系数) |
| `Manuscripts/sections/main-results.md` | audit 的扫描对象 |

## 使用方式

### 写作前（gate-1）

```bash
cat evidence/evidence_bank.md
# 确认所有要引用的数字 / 事实 / 引用都在 evidence_bank.md 内
```

### 写作中（gate-2）

每写一条数字声明，同时在 `evidence/claim_register.md` 追加一行：

```markdown
| claim_id | section | claim_text | source_path | source_anchor | value | confidence |
| C-005 | §5.1 | IV 估计 ln_robot 系数 | regression_tables.json | tables[0].coefficient_rows[ln_robot].coefficient | 0.1994 | approved |
```

### 写作后（gate-3，**硬门禁**）

```bash
python evidence/integrity_audit.py --section main-results --write
# 输出 evidence/integrity_audit.md
# 退出码 0 = CLEAN，1 = BLOCKED，2 = 工具错误
```

只有 integrity_audit 退出码为 0 时，论文才能进入翻译 / 投递阶段。

## 验证历史

- 2026-06-02：在 main-results.md 上首次运行（当前稿，已无捏造），结果 CLEAN
- 计划：在已废弃的"捏造稿"上回放同一脚本，验证能捕获全部 18 条捏造

## 后续工作

- 把 audit 跑测加到 `tests/test_integrity_audit.py`，CI 化
- 适配其他 8 个 stub section（abstract / introduction / literature / theory / data / empirical-strategy / robustness / conclusion）
- 集成到 `paper_supervisor.py` 流水线，audit 是 export 前的强制 gate
