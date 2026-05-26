# North Star Plan: CLI-first Empirical Research OS

日期：2026-05-26

## 结论

当前主线改为先把本地 CLI 工作流做扎实，再把同一套状态和证据模型接到云端产品。原因很直接：如果本地无法用真实数据、真实方法、真实日志跑完一条研究链路，前端再漂亮也只是在展示空壳。

本计划不放弃云端产品。它把本地版和云端版统一成同一个 Research OS，只是入口不同：

- 本地版：CLI、真实本地文件、本地模型、本地日志和 Git 化论文状态。
- 云端版：上传对象存储、云模型、云执行沙盒、同一套状态机和审计证据。

## 北极星目标

用户输入一个研究题目后，系统应该完成以下闭环：

```text
题目输入
-> 递归研究搜索
-> 数据和变量发现
-> 变量角色候选
-> 方法设计和前置条件检查
-> 执行计划
-> 真实统计后端执行
-> evaluator 检查
-> 研究报告和 exploratory 论文草稿
-> Journal Skill 审稿标准检查
-> 导出预检
-> 人工决定是否进入正式层
```

核心约束：

- Auto Mode 可以生成和修改草案层。
- Auto Mode 不能静默覆盖正式层。
- 正式层包括 canonical `VariableRoleSet`、`DesignSpec`、`RunPlan`、正文、导出包和 Journal Skill canonical 规则。
- 所有结果默认是 `exploratory / draft / needs_human_review`。
- 只有人工确认后的状态才能进入 formal / approved / exportable。

## 两条交付线

### 1. 本地高效工作流

本地工作流是第一版主线，面向用户本人和少数熟人。

必须具备：

- 可以直接读取本地数据目录和本地配置。
- 可以接入 StatsPAI、Python、StataMCP 或 stata-code 作为执行后端。
- 可以使用本地 Codex Supervisor 或其他本地模型生成研究计划和 patch proposal。
- 可以把每一轮结果写入 `workspace/runs/<run_id>/`。
- 可以把正式状态写入 `state/product/`。
- 可以把论文草稿和导出预检写入 `Manuscripts/`、`Results/`。
- 可以用 Git 思路保护正式层，不让 Agent 静默覆盖。

### 2. 云端产品

云端产品后续必须做，但不应和本地工作流割裂。

云端版只替换执行环境：

- 本地路径换成上传对象和 cloud dataset id。
- 本地模型换成云模型 provider。
- 本地执行换成云沙盒。
- 本地 `workspace/runs` 换成云端 run storage。

不替换的部分：

- `ResearchIntent`
- `VariableRoleSet`
- `DesignSpec`
- `RunPlan`
- `CapabilityRegistry`
- `JournalSkillRegistry`
- `RunManifest`
- `EvidenceGap`
- `ArtifactPolicy`
- `needs_human_review` 边界

## 当前真实 CLI 证据

本轮已经完成一次真实数据 CLI 运行，不再只是 UI 或 mock。

### 数据

- 数据文件：`Data/Final/cfps_robot_reallocation.csv`
- 规模：34,315 行，16 列
- 题目：工业机器人暴露是否影响劳动收入再配置？
- outcome：`ln_wage`
- treatment：`ln_robot`
- controls：`edu_last`、`age`、`female`、`urban`

### 运行命令

```bash
python3 Program/run_paper.py \
  --project-root . \
  --paper-config Program/config/paper_real_cfps_robot.yaml \
  --run-id run_cli_real_cfps_robot_20260526_isolated
```

### 关键输出

- 配置：`Program/config/paper_real_cfps_robot.yaml`
- 状态：`state/cfps_robot_project_state.json`
- 结果索引：`Results/cfps_robot_index.json`
- 分析结果：`Results/json/cfps_robot_analysis_result.json`
- 项目快照：`Results/json/cfps_robot_project_snapshot.json`
- 运行日志：`Results/logs/cfps_robot_run_paper.log`
- Markdown 草稿：`Manuscripts/generated/cfps_robot_paper_draft.md`
- LaTeX 草稿：`Manuscripts/generated/cfps_robot_paper_draft.tex`
- 可观察运行：`state/runs/run_cli_real_cfps_robot_20260526_isolated/`

### 当前结果边界

StatsPAI 可执行，运行成功，样本量为 15,697 个 complete-case 观测。基准 OLS 结果中，`ln_robot` 系数为 0.1039，稳健标准误为 0.0059。

这个结果只能作为本地执行链路证据，不能作为正式因果结论。原因是当前设计被自动判定为 observational，仍缺少正式的变量角色确认、识别设计、RunPlan、Journal Skill 审稿门和人工确认。

## Auto Research 证据

命令：

```bash
python3 Product/cli.py auto-research \
  --project-root . \
  --topic "工业机器人暴露是否影响劳动收入再配置？使用 CFPS 与工业机器人暴露数据" \
  --mode auto \
  --max-depth 2 \
  --max-iterations 5
```

最新可用 run：

- run id：`run_20260526T024212Z_b1cfec`
- run root：`workspace/runs/run_20260526T024212Z_b1cfec`
- 变量候选：`workspace/runs/run_20260526T024212Z_b1cfec/03_strategy/variable_candidates.json`
- 研究报告：`workspace/runs/run_20260526T024212Z_b1cfec/06_writing/research_report.md`
- exploratory 草稿：`workspace/runs/run_20260526T024212Z_b1cfec/06_writing/paper_draft_exploratory.md`

本轮修正点：

- Auto Research 不再默认选择 `analysis_sample.csv`。
- 当题目包含 CFPS 和机器人线索时，优先选择 `Data/Final/cfps_robot_reallocation.csv`。
- 变量匹配不再把 `ln_wage` 误认为 `age` control。

当前能力状态：

- `local_data`：available
- `statspai`：available
- `web_search`：available
- `cnki`：blocked_by_browser_session，需要人工辅助或浏览器会话
- `agentmemory`：unavailable，本机未发现 executable
- `llm_supervisor`：unavailable，`EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC` 未开启

## Task 和 Goal 的配合方式

本项目之后按以下规则运转：

- `Goal`：保存当前北极星阶段目标，不随单轮实现缩小。
- `Tasks/todo.md`：保存可执行任务队列。
- `Tasks/round-log.md`：保存每轮迭代、证据路径、瓶颈和下一步策略。
- `Tasks/decision-log.md`：保存不可逆或重要边界决策。
- `Tasks/manifest.md`：保存新文件、API、命令和产物入口。

每一轮必须有一个明确结尾：

```text
做了什么
用什么数据或状态验证
输出在哪里
哪些东西仍然不能进入正式层
下一轮先做什么
```

## MVP 出口标准

CLI-first MVP 至少需要完成：

- [x] Topic-first Auto Research 生成 run workspace。
- [x] Auto Research 能按题目选择真实数据集。
- [x] `run_paper.py` 支持独立 paper config。
- [x] 真实 CFPS/机器人数据可以跑完 live CLI。
- [x] 运行产物有独立 state、index、snapshot、analysis_result、draft 和 observability。
- [ ] StatsPAI Capability Registry 在启动时索引可用函数 schema。
- [ ] Journal Skill Registry 支持 AER-like 顶刊标准。
- [ ] Method Design 能读 Journal Skill rules 生成前置检查。
- [ ] Review & Export 能用 Journal Skill rules 阻断正式导出。
- [ ] 本地 Codex Supervisor 能生成持久化 research execution plan。
- [ ] Auto Mode 能从计划跑到导出预检，但正式层仍需人工确认。

## 下一步顺序

1. 建立 Journal Skill Registry 的状态和目录边界。
2. 将 AER-like 顶刊标准先作为 proposal 引入，不直接写入 canonical。
3. 增加 StatsPAI Capability Registry，使 Supervisor 和 executor 可以按 schema 选择函数。
4. 让 Auto Research 的 method candidates 读取 Capability Registry 和 Journal Skill Registry。
5. 将 Review & Export 的 verifier gates 扩展为 journal-aware gates。
6. 再让前端接真实状态，而不是继续做空壳 UI。
