# P2 Real Data CLI Full Run BDD

日期：2026-05-26

## 背景

当前产品层已经证明了 topic-first、Agent Task Queue 和执行观测界面，但严肃实证系统不能只停留在 UI 或候选层。下一阶段必须先证明本地 CLI 能读取真实数据配置并跑完一次可复查的分析流程，再继续推进产品层视觉和交互。

本阶段不覆盖云端上传，也不把真实数据静默写入正式论文状态。目标是为本地高效工作流建立一个可复现的真实数据入口。

## 行为 1：CLI 可以指定独立 paper config

**Given** 项目根目录存在默认 `paper.yaml`
**And** 另有一个真实数据配置文件 `Program/config/paper_real_cfps_robot.yaml`
**When** 用户运行 `python3 Program/run_paper.py --project-root . --paper-config Program/config/paper_real_cfps_robot.yaml`
**Then** pipeline 必须读取指定配置，而不是默认 `paper.yaml`
**And** 生成的 state、results index、draft、snapshot 必须写入该配置声明的路径
**And** observability 的 `config_load` step 必须记录实际使用的 paper config 路径。

业务规则：真实数据运行不能覆盖或篡改默认教学/样例配置；不同研究任务应通过独立配置和独立输出路径隔离。

## 行为 2：真实 CFPS/机器人数据可以完成 CLI live run

**Given** 项目中存在 `Data/Final/cfps_robot_reallocation.csv`
**And** 配置声明 outcome=`ln_wage`、treatment=`ln_robot`、controls=`edu_last, age, female, urban`
**When** 用户运行 live mode 的 `run_paper.py`
**Then** 系统必须调用当前可用的 StatsPAI paper workflow
**And** 写出 `analysis_result.json`、run log、project snapshot、Markdown/LaTeX 草稿和 observability 文件
**And** 所有结果仍标记为 exploratory / local execution evidence，不自动进入正式论文层。

业务规则：真实数据结果只能证明本地执行链路可用；是否进入论文正式论断仍要经过变量角色、研究设计、RunPlan、审稿标准和人工确认。

## 行为 3：真实运行证据必须可复盘

**Given** 一次真实数据 CLI run 已结束
**When** 用户或 Agent 查看 `Tasks/manifest.md` 和 `Tasks/todo.md`
**Then** 能看到 run id、使用的数据、配置文件、关键输出路径和剩余风险
**And** 不能把“已找到真实数据”误写成“已完成正式论文研究”。

业务规则：长程开发必须把执行证据外化，避免跨 session 后只记得“跑过”但无法复盘跑了什么、用了哪个数据、结果能不能信。

## 本轮边界

- 不复制外部原始大文件进仓库。
- 不把外部数据路径写成默认 `paper.yaml`。
- 不自动批准 VariableRoleSet、DesignSpec、RunPlan 或论文正文。
- 不承诺因果识别成立；本轮只验证真实数据执行链路。
