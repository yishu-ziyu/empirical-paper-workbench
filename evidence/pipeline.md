# evidence/pipeline.md — 论文写作的 5 阶段强制流水线

> **本文件定义了 main-results.md（以及后续其他 8 个 section）从"草稿"到"可投递"的 5 阶段流程。**
>
> **核心承诺**：audit 阶段是**硬门禁**（hard gate），通过 = CLEAN，失败 = BLOCKED。
> 任何 BLOCKED 状态下的稿件 **禁止** 进入翻译 / 投递 / LaTeX 编译。

---

## 1. 流水线总览

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Stage 1 │   │  Stage 2 │   │  Stage 3 │   │  Stage 4 │   │  Stage 5 │
│ RESEARCH │ → │  CITE    │ → │  WRITE   │ → │  AUDIT   │ → │TRANSLATE │
│ (找证据)  │   │ (建库)   │   │ (写文)   │   │ (硬门禁) │   │ (英/中)  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
```

| Stage | 输入 | 产出 | 守门员 | 失败后果 |
|-------|------|------|--------|----------|
| 1. RESEARCH | 选题 / 研究问题 | `Results/json/regression_tables.json`<br>`Results/json/analysis_result.json`<br>`Results/json/approved_findings.json` | 实证工作流（已自动跑） | 缺数据 → 流程终止 |
| 2. CITE | 文献检索 | `Data/literature/processed/verified_bibliography.csv`<br>`Manuscripts/references.bib` | `mcp__paper-search` 核验 | 未核验引用 → 学术风险 |
| 3. WRITE | evidence_bank + 引用库 | `evidence/evidence_bank.md`<br>`evidence/claim_register.md`<br>`Manuscripts/sections/*.md` | 人类 / Agent 写手 | 写出来不靠 evidence → 论文可信度归零 |
| 4. AUDIT | 上一阶段全部产物 | `evidence/integrity_audit_<section>.md` | `evidence/integrity_audit.py` | **BLOCKED → 必须改稿后才能翻译** |
| 5. TRANSLATE | CLEAN 后的稿件 | `Manuscripts/en/...` 或 `Manuscripts/zh/...` | 翻译 Agent | 翻译覆盖度不达 100% → 投递受阻 |

---

## 2. 各阶段的强制约束

### Stage 1 — RESEARCH

**目的**：从数据 / 模型 / 实证结果里抽出一份"数字真值"清单。

**产物**：
- `Results/json/regression_tables.json`（4 张回归表，22 个 coefficient_rows）
- `Results/json/analysis_result.json`（8 条 robustness findings）
- `Results/json/approved_findings.json`（人工核准的 finding）

**约束**：
- ✅ 所有数字必须可在 `Program/` 下的某个脚本里**重跑**得到（不能是手工键入）
- ✅ approved_finding 必须由用户人工 review 后进入

### Stage 2 — CITE

**目的**：建立已核验的引用库（避免 LLM 杜撰文献）。

**产物**：
- `Data/literature/processed/verified_bibliography.csv`（14 条已核验）
- `Manuscripts/references.bib`（BibTeX 同步）

**约束**：
- ✅ 每条 BibTeX key 必须在 CSV 中存在
- ✅ 任何"在论文里出现但 CSV 之外"的引用 → 走 `mcp__paper-search` 二次核验

### Stage 3 — WRITE

**目的**：按 evidence 写文，每写一条数字登记到 claim_register。

**执行步骤**（按顺序）：

1. **写前**：读 `evidence/evidence_bank.md`，确认要引用的所有数字 / 事实都在表 1-5 中。
2. **写中**：每写一条数字声明 → 同时在 `evidence/claim_register.md` 加一行：
   - `claim_id` 唯一编号
   - `source_path` + `source_anchor`（精确到 JSONPath / 行号）
   - `confidence`：approved / derived / gap
3. **写后**：检查 `evidence/evidence_bank.md §6 gap 列表` 是否有对应声明：
   - 是 → 在文中显式写"待 §6 补充"或"未在本文档实证"
   - 否 → 必须先在 evidence_bank.md §6 加 gap 条目，**禁止** 静默写"待补"

**禁止行为**（红线）：
- 🚫 写"约 0.5% 弹性"这类无 evidence 来源的数字
- 🚫 写"Acemoglu 报告 X"但 references.bib 没有该文献
- 🚫 写"我们做过了 Y 检验"但 Results/json 没有对应 record
- 🚫 改 approved_findings 但不更新 claim_register

### Stage 4 — AUDIT（**硬门禁**）

**目的**：自动捕获捏造、确保数字可追溯。

**执行**：

```bash
python3 evidence/integrity_audit.py --section <name> --markdown --write
# 退出码 0 = CLEAN，1 = BLOCKED
```

**5 个审计维度**：

1. **Required Files** — 4 个必备文件 (evidence_bank / claim_register / pipeline / section md) 存在
2. **Number Anchoring** — 文中 4 位以上小数**必须**在 claim_register.md 或 evidence_bank.md 出现
3. **Forbidden Patterns** — 18 条历史捏造指纹、E-value=1.18、Acemoglu 0.5%、OLS 被高估方向错误等
4. **Source-of-Truth Drift** — 4 张回归表的 22 个 coefficient_rows 至少 verbatim / narrative 出现在文中
5. **Gap Honesty** — evidence_bank §6 列的 8 个 gap 在文中均显式声明

**每个发现 6 字段**（PaperSpine 教学风格）：

- `severity` ∈ {BLOCKER, WARNING, INFO}
- `what_was_found` — 抓到了什么
- `root_cause` — 为什么会出现
- `fix_action` — 具体怎么改
- `downstream_impact` — 不改的后果
- `teaching_note` — 为什么这类错是 LLM 典型错

**门禁规则**：

- BLOCKER ≥ 1 → **禁止翻译 / 投递**，必须改稿后重跑
- WARNING 任意条 → 强烈建议修复（部分可接受）
- 全部 CLEAN → 进入 Stage 5

**禁止行为**（红线）：
- 🚫 在 BLOCKED 状态下走"先翻译，audit 之后再说"流程
- 🚫 删 evidence_bank.md / claim_register.md 让 audit 通过
- 🚫 篡改 approved_findings.json 让数字"通过"
- 🚫 写"audit 没扫到 = 通过"（这是 LLM 经典 rationalization）

### Stage 5 — TRANSLATE

**目的**：把 CLEAN 后的稿件翻译成英文 / 中文（按目标期刊要求）。

**执行**：见 `Program/run_paper.py` 或 `Product/workspaces/...` 的翻译 workflow。

**约束**：
- ✅ 必须 Stage 4 退出码 = 0
- ✅ 翻译时**不**得改数字 / 不**得**改引用键
- ✅ 翻译完成后必须保留原 claim_id 标记（便于交叉查证）

---

## 3. 完整流程脚本（一键走完）

```bash
# Stage 1+2：实证已跑（见 Program/ 下脚本）
# Stage 3：写稿 + 维护 evidence/
# Stage 4：硬门禁
python3 evidence/integrity_audit.py --section main-results --write
if [ $? -ne 0 ]; then
  echo "[BLOCKED] integrity_audit failed; do NOT translate."
  exit 1
fi
# Stage 5：翻译（仅在 CLEAN 后）
# python3 Program/paper_translation.py ...
```

---

## 4. 关键决策记录

| 决策 | 理由 | 时间 |
|------|------|------|
| audit 必须是硬门禁 | 2026-06-02 的 18 条捏造就是因为没有 gate | 2026-06-02 |
| evidence_bank + claim_register 用纯 markdown | 比 JSON 易读、易手动维护、易 git diff | 2026-06-02 |
| integrity_audit.py 独立可运行（不依赖 workbench） | 论文写手 / Agent 在没有完整项目环境时也能跑 | 2026-06-02 |
| 历史捏造指纹进 FORBIDDEN_NUMERIC_PATTERNS | 同一错 LLM 重复犯的概率高，禁词是最便宜的护栏 | 2026-06-02 |
| 8 个 gap 必须在文中显式声明 | 诚实比"显得完整"重要；审稿人最恨"做过了未呈现" | 2026-06-02 |

---

## 5. 维护日志

- 2026-06-02 初版：基于 2026-06-02 论文捏造事件，落地 PaperSpine 5 阶段流水线
- TODO：把 audit 跑测加到 `tests/test_integrity_audit.py`（已规划）
- TODO：把 audit 接入 `paper_supervisor.py` 流水线作为 export gate
