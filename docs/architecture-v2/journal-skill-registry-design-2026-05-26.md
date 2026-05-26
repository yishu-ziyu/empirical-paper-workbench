# Journal Skill Registry Design

日期：2026-05-26

## 目标

把 AER-Skills、Awesome Journal Skills、Awesome Agent Skills for Empirical Research 这类专业技能库接入本项目，但不把它们粗暴复制成静态规则，也不允许 Auto Mode 静默改写正式规则。

这层能力在产品里叫做“审稿标准”，在内部叫做 `JournalSkillRegistry`。

MVP 首先支持：

- `AER-like 顶刊标准`
- 适用阶段：`Method Design` 和 `Review & Export`
- 作用：提醒、检查、阻断正式导出
- 不作用：不替代人类判断，不保证投稿成功，不直接改写正文或正式研究状态

## 已核对外部来源

2026-05-26 通过 `git ls-remote` 核对：

- `https://github.com/brycewang-stanford/AER-skills.git`
  - main：`7e9c44d363c185edf27859096268b6a8256c4a2b`
- `https://github.com/brycewang-stanford/awesome-journal-skills.git`
  - main：`22ee5589d13f3cca617c32cc18dac80f0a6c5c09`
- `https://github.com/brycewang-stanford/Awesome-Agent-Skills-for-Empirical-Research.git`
  - main：`e03ff8cf62f1ce8739c4181cead149da5dd84b11`

当前设计只记录来源和导入边界，不把外部内容直接视为本项目已 review 的 canonical 规则。

## 用户可见语义

产品不直接暴露“插件”“仓库”“规则 YAML”等工程词。用户看到的是：

- 审稿标准：默认建议开启
- 标准选项：`AER-like 顶刊标准`
- 状态：`未开启`、`已建议`、`草案检查中`、`需要补证据`、`通过导出预检`

入口位置：

- Task Brief 页：用户选择是否启用 `AER-like 顶刊标准`
- Method Design 页：显示当前方法需要补哪些识别和稳健性证据
- Review & Export 页：作为正式导出前的审稿门

## 系统边界

### Auto Mode 可以做

- 读取外部 Skills 仓库。
- 抽取候选规则。
- 生成 patch proposal。
- 标记规则来源、证据强度、适用方法、阻断等级。
- 在草案层提示“这个设计按 AER-like 标准可能缺什么”。
- 生成 reviewer scorecard 或 desk-reject 风险说明。

### Auto Mode 不可以做

- 不可把 proposal 直接合入 canonical 规则库。
- 不可直接覆盖已人工确认的 `VariableRoleSet`。
- 不可直接覆盖已人工确认的 `DesignSpec`。
- 不可直接覆盖已人工确认的 `RunPlan`。
- 不可把 exploratory 结果升级为 formal finding。
- 不可绕过人工确认导出正式 docx。

### 人工 review 后才可以做

- 将某条外部规则合并到 `Program/methodology/canonical/`。
- 将某条规则标记为 `blocks_formal_export=true`。
- 将某条规则设为某类方法的默认前置条件。

## 目录设计

```text
Program/methodology/
  README.md
  external_sources/
    aer-skills/
      source.yml
      sync_notes.md
  proposals/
    2026-05-26-aer-skills-import/
      proposal.yml
      extracted_rules.yml
      review.md
  canonical/
    journal/
      aer/
        registry.yml
        identification.yml
        robustness.yml
        replication.yml
        submission.yml
```

MVP 阶段只允许创建 `proposals/` 和文档。`canonical/` 目录可以存在，但不能写入未 review 的正式规则。

## 状态文件设计

### 项目级状态

路径：

```text
state/product/journal_review.json
```

职责：

- 记录当前项目是否启用 Journal Skill。
- 记录启用的是哪个标准。
- 记录哪些规则检查已经运行。
- 记录哪些 formal export gate 被阻断。

示例：

```json
{
  "project_id": "default",
  "selected_standard": "aer_like",
  "status": "needs_human_review",
  "enabled_by_user": true,
  "recommended_by_supervisor": true,
  "canonical_registry_version": null,
  "proposal_refs": [
    "Program/methodology/proposals/2026-05-26-aer-skills-import/proposal.yml"
  ],
  "formal_export": {
    "can_export": false,
    "blocking_reasons": [
      "journal_rules_not_reviewed",
      "identification_checks_missing"
    ]
  }
}
```

### Run 级状态

路径：

```text
workspace/runs/<run_id>/journal_review.json
```

职责：

- 记录某次 run 使用了哪些审稿规则。
- 记录哪些结果或草稿段落触发了审稿风险。
- 记录是否可以进入 formal export。

示例：

```json
{
  "run_id": "run_xxx",
  "standard": "aer_like",
  "source": "proposal",
  "checks": [
    {
      "id": "aer_like.did.staggered_twfe_bias",
      "method_family": "did",
      "severity": "high",
      "status": "not_applicable",
      "blocks_execution": false,
      "blocks_formal_export": false
    }
  ],
  "can_promote_to_formal": false
}
```

## 规则模型

每条规则需要以下字段：

```yaml
id: aer_like.did.staggered_treatment_requires_modern_estimator
standard: aer_like
source:
  repo: https://github.com/brycewang-stanford/AER-skills.git
  commit: 7e9c44d363c185edf27859096268b6a8256c4a2b
  status: external_unreviewed
method_family: did
applies_when:
  - staggered_treatment_timing
claim:
  zh: 交错处理 DID 不能只依赖传统 TWFE。
required_evidence:
  - modern_did_estimator
  - twfe_bias_diagnostic
severity: high
blocks_execution: false
blocks_formal_export: true
review_status: proposal_only
reviewed_by: null
reviewed_at: null
```

## 严重等级

| severity | 含义 | 默认动作 |
| --- | --- | --- |
| `info` | 方法提示，不阻断 | 只展示 |
| `warning` | 可能影响可信度 | 在 Method Design 提醒 |
| `high` | 可能导致审稿风险 | Review & Export 要求说明 |
| `blocking` | 缺失时不能正式导出 | 阻断 formal export |

注意：`blocking` 只能来自 canonical 且已人工 review 的规则。Proposal 规则最多只能标记为 high。

## AER-like MVP 规则范围

第一版只覆盖四类检查：

### 1. Identification

- DID：交错处理不能只用 TWFE，需要现代 DID 估计器或偏误诊断。
- IV：弱工具变量不能只报告常规 first stage，需要弱工具稳健推断。
- RDD：需要带宽敏感性和协变量处理说明。
- SCM/Bartik：需要来源、权重、平衡和敏感性说明。

### 2. Robustness

- 安慰剂检验
- 异质性分析
- 机制检验
- 敏感性分析
- 可观测选择偏误检查

### 3. Replication

- README 是否能复现主结果。
- 数据来源和权限是否清楚。
- 代码入口是否明确。
- 运行环境是否记录。

### 4. Submission

- 摘要字数要求。
- 利益冲突和 disclosure。
- 匿名化要求。
- cover letter 和投稿前 checklist。

## 与现有模块的关系

### Task Brief

用户选择：

```text
审稿标准：AER-like 顶刊标准
```

系统记录到 `state/product/journal_review.json`，但不运行正式阻断。

### Method Design

读取：

- 当前 `DesignSpec`
- 当前 `RunPlan`
- 当前方法候选
- `JournalSkillRegistry`

输出：

- 方法前置条件提示
- 需要补的证据
- 不适用的规则
- 需要人工确认的高风险规则

### Review & Export

读取：

- approved findings
- draft sections
- export package manifest
- replication manifest
- journal review state

输出：

- `can_export_docx`
- blocking reasons
- journal-aware verifier checks

只有 canonical 且 review 过的规则可以阻断正式导出。未 review 的 AER-Skills proposal 只能生成高风险提示，不能直接变成正式阻断。

## 与 Agent 分工的关系

| Agent | 作用 |
| --- | --- |
| Supervisor | 推荐是否启用 Journal Skill，分派检查任务 |
| Method Agent | 读取 identification 和 robustness 规则，生成方法补证据任务 |
| Data Agent | 根据规则补数据和变量证据 |
| Execution Agent | 根据规则触发可执行诊断 |
| Reviewer Agent | 生成 desk-reject 风险和 scorecard |
| Verifier Agent | 在 Review & Export 阶段检查 formal export gate |

## BDD 行为

### 行为 1：用户只在需要顶刊标准时启用 AER-like

**Given** 用户在 Task Brief 页输入研究题目
**When** 系统建议启用 `AER-like 顶刊标准`，用户选择启用
**Then** 系统写入 `state/product/journal_review.json`
**And** 状态为 `needs_human_review`
**And** 不直接修改变量角色、设计方案或运行计划。

业务规则：审稿标准是研究流程的约束，不是 Agent 自动替用户做学术判断的权限。

### 行为 2：外部 AER-Skills 只能先进入 proposal

**Given** 系统可以访问 AER-Skills 外部仓库
**When** Auto Mode 抽取规则
**Then** 规则只能写入 `Program/methodology/proposals/...`
**And** `review_status=proposal_only`
**And** 不允许写入 canonical 规则库。

业务规则：专业方法库必须主导，但正式规则必须经人工 review 后才能成为本项目的审稿门。

### 行为 3：Method Design 读取规则但不阻断探索

**Given** 用户启用了 AER-like 标准
**And** 当前方法候选包含 DID、IV、RDD 或 OLS
**When** 系统生成 Method Design 检查
**Then** 页面显示缺失证据和建议诊断
**And** 探索性运行仍可继续
**And** 输出保持 `exploratory / needs_human_review`。

业务规则：早期探索应该高效，不能被未确认规则过早卡死。

### 行为 4：Review & Export 使用 canonical 规则阻断正式导出

**Given** 某条 Journal Skill 规则已经人工 review 并进入 canonical
**And** 该规则标记 `blocks_formal_export=true`
**When** 用户尝试正式导出 docx
**Then** Verifier 必须检查该规则
**And** 缺失 required evidence 时 `can_export_docx=false`
**And** 页面说明缺什么证据和下一步任务。

业务规则：正式导出是最严格的门，不能让缺证据的论文以正式稿形式输出。

## 下一步实现验收标准

第一轮实现只算完成，如果同时满足：

- [ ] 新增 `JournalSkillRegistry` 读取器，能读 proposal 和 canonical。
- [ ] 新增 `state/product/journal_review.json` 的读写服务。
- [ ] Task Brief 能保存用户选择的审稿标准。
- [ ] Method Design 能显示 AER-like 缺失证据提示。
- [ ] Review & Export 能读取 journal-aware verifier checks。
- [ ] Proposal 规则不能阻断 formal export。
- [ ] Canonical reviewed blocking 规则可以阻断 formal export。
- [ ] 所有行为有 BDD 文档和自动化测试。

## 当前不做

- 不复制完整外部仓库。
- 不自动安装到 `~/.claude/skills`。
- 不把 AER-like 当作唯一审稿标准。
- 不把规则库做成 UI 主模块。
- 不承诺 AER 投稿成功。
- 不把当前 CFPS/机器人 OLS 结果说成已达到 AER 标准。
