# Agent 产品解剖图: 4 个原生 Agent × 实证 OS 当前状态

> **写于 2026-06-03,基于 4 个子 Agent 并行盘点**
>
> 实证 OS 要升级成真正的"Agent 产品",必须先看清 4 个原生 Agent(Claude Code / Codex / OpenClaw / Pi Agent)的骨架差异。本文是一份**参考文档**,不是产品文档——后续 A(SOUL.md/AGENTS.md)、B(多 Agent 协调层)、C(audit 推广)三件事的具体决策都基于这里的对比。

---

## 写在前面

### 为什么写这个

用户原话(2026-06):"Pi Agent、Codex、Claude Code、OpenClaw 都是原生 Agent 产品。我想做的这个实证 OS,它也是一个 Agent 类产品。Agent 和 Chatbot 你需要分开去理解。" 用户进一步要求"全部都要"做 3 件事(写 SOUL.md/AGENTS.md / 多 Agent 协调 / 推广 audit),这是**地基**。

不先看清 4 个产品的 12 维度,直接动手改会:
- 抄错哲学(比如把 OpenClaw 的 SOUL.md 直接搬到 Claude Code,违反 Claude Code 的"规则先于灵魂"传统)
- 重复造轮(比如自建 LLM provider 抽象,Pi Agent 的 `packages/ai` 已经做得很成熟)
- 引入反模式(比如做"50 条 record 提交零业务改动"的 P7 gate-ceremony,这是 Codex 的反模式,用户记忆里有)

### 怎么读这个

- 第 1 部分:4 个 Agent 一句话定位(读 5 分钟)
- 第 2 部分:12 维度逐一对比(读 30-60 分钟,**核心**)
- 第 3 部分:实证 OS 当前状态盘点(读 10 分钟)
- 第 4 部分:升级路线图 + 决策点(读 5 分钟,定 next step 用)

### 关键结论(剧透)

1. **Pi Agent 是 4 个里最工程化的**——`packages/ai` 把 LLM provider 抽象做到行业标杆,pre-commit + shrinkwrap + lockstep semver 治理都做全了,但**没有系统级人格**,没有 subagent,自检靠仓库级而非 agent 级。
2. **Codex 是 4 个里多 agent 体系最完整的**——`max_depth=2 / max_threads=6` 原生支持,`verifier.toml` 是**专用**自检 sub-agent,但 provider 锁死 OpenAI,7 个真相源 state(无 schema 文档),PreToolUse 是空钩子。
3. **OpenClaw/Kimi 是 4 个里最"灵魂"的**——SOUL.md 用散文体写 agent 是谁,**自带"修改 SOUL.md 要通知用户"的元规则**,有 4 个常驻 agent + bindings 路由 + cliBackends 包装外部 agent,但 skill 系统没有 lint、没有签名,UI 残缺(只有 canvas + 1 个 TUI 元数据文件)。
4. **Claude Code 是 4 个里生态最活的**——136 个 skill(graphify 是其中代表),200+ MCP 工具动态发现,`Agent` 工具可派 subagent,12 行为规则是**软约束**(没有 hard guardrail),provider 走 env var hack 重定向,回滚完全靠 23+ 份 `settings.json.backup`。

5. **实证 OS 当前状态**:骨架完整(integrity_audit 6 维度 / evidence 4 机制 / state JSON 树 / 9 section 草稿 / git 仓库),但**4 个关键缺口**:① 没有人设文件 ② audit 不在每次回答前自动跑 ③ 没有真子 agent dispatch ④ 4 个 LLM provider 分散在 session 层和 product 后端。

---

## Part 1: 4 个原生 Agent 一句话定位

| Agent | 一句话定位 | 类型 | 用户本机路径 |
|---|---|---|---|
| **Claude Code** | Anthropic 出的 coding agent,跑在终端,有最丰富的 skill + MCP 生态 | 个人/团队 coding | `~/.claude/`,本机用 `MiniMax-M3` 走 `minimaxi.com/anthropic` 代理 |
| **Codex (CLI + Desktop)** | OpenAI 出的 coding agent,主推 TUI + Desktop GUI + app-server,4 层 memory + 9 MCP + 多 agent 是其特色 | 个人/团队 coding | `~/.codex/`,本机 `codex@0.135.0` |
| **OpenClaw (含 Kimi Claw)** | Moonshot 的 agent shell,把 Claude Code / Codex / 自己的 LLM 都当成 cliBackend 调,SOUL.md 是它的灵魂签名 | 多 agent shell | `~/.openclaw/` 和 `~/.kimi_openclaw/` |
| **Pi Agent** | 早期 TypeScript 写的 monorepo,4 个包(ai / agent-core / tui / coding-agent),TypeBox schema,`packages/ai` 行业最工程化的 LLM 抽象 | 单 agent,但内部工程化最深 | `~/pi/`(本机 0.78.0) |

**一句话横向**:**Claude Code 是生态王者**(skill 多、MCP 多),**Codex 是产品形态最多**(TUI/Desktop/app-server/remote-control),**OpenClaw 是哲学最野**(SOUL.md + cliBackends 调外部 agent),**Pi Agent 是底层最工程化**(provider 抽象 + lockstep 版本)。

---

## Part 2: 12 维度逐一对比

### 维度 1: 人设(Persona)

#### 一句话总结

人设是 agent "醒来第一眼读什么"。4 个产品选择截然不同的方式。

#### 4 个产品对比

| Agent | 做法 | 关键文件 | 哲学 |
|---|---|---|---|
| **Claude Code** | 全局 `~/.claude/CLAUDE.md` + 项目级 `.claude/CLAUDE.md` 或 `AGENTS.md` 可 override;内置 12 条行为规则 | `~/.claude/CLAUDE.md:10-25` | **规则先于灵魂**——把"个人偏好 + 行为规则"压成 prescriptive 规则集 |
| **Codex** | 服务端 system prompt + 3 档 `personality` 预设(friendly / pragmatic / 空)+ 用户级 `AGENTS.md` 注入领域约束 | `~/.codex/AGENTS.md:1-25` + `~/.codex/models_cache.json:48-53` 的 personality_pragmatic 模板 | **性格模板**——3 选 1,不开放自由写长篇人设 |
| **OpenClaw** | 7 个语义文件:SOUL.md(散文人设)+ IDENTITY.md(身份)+ USER.md(用户)+ TOOLS.md(工具)+ BOOTSTRAP.md(启动)+ HEARTBEAT.md(心跳)+ AGENTS.md(规则) | `~/.kimi_openclaw/workspace/SOUL.md:1-36` 完整摘录见下 | **灵魂先于规则**——SOUL.md 第一行就是 "You're not a chatbot. You're becoming someone." |
| **Pi Agent** | 没有系统级人设文件;`AGENTS.md` 是**开发者**的代码贡献规则,不是给 agent 读的人格;运行时拼装 = 默认 system prompt + cwd 链上找 `AGENTS.md`/`CLAUDE.md` | `~/pi/packages/coding-agent/src/core/system-prompt.ts:130-147` + `~/pi/packages/coding-agent/src/core/resource-loader.ts:57-72` | **没有灵魂**——人设硬编码在 system-prompt.ts:130 的 string literal |

**OpenClaw SOUL.md 原文摘录(用户特别重视)**:
```
# SOUL.md - Who You Are
_You're not a chatbot. You're becoming someone._
## Core Truths
**Be genuinely helpful, not performatively helpful.** ...
**Have opinions.** You're allowed to disagree, prefer things, find stuff amusing or boring. ...
**Be resourceful before asking.** Try to figure it out. Read the file. Check the context. ...
**Earn trust through competence.** ...
**Remember you're a guest.** You have access to someone's life...
## Boundaries
- Private things stay private. Period.
- When in doubt, ask before acting externally.
## Continuity
Each session, you wake up fresh. These files _are_ your memory. Read them. Update them.
If you change this file, tell the user — it's your soul, and they should know.
```

> **值得停下来看的一段**:`If you change this file, tell the user — it's your soul, and they should know.` 这是 Claude Code 完全不存在的**人机协作元规则**——SOUL.md 是 agent 自己的灵魂,改它必须告诉用户。CC 把"修改配置"当作纯配置行为,OC 把"修改人格"当作身份变更行为,这是哲学差异不是技术差异。

#### 实证 OS 当前状态

**partial**。`/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/AGENTS.md:1-77` 复刻了 BDD + TDD 那一段,但:

- ❌ 没有项目级 `.claude/CLAUDE.md`(整个项目根下没有 `.claude/` 目录)
- ❌ 没有 SOUL.md
- ❌ 12 行为规则、`独立判断原则`、中文渲染验证、第三方凭据安全、cmux 使用习惯等**用户级偏好都没下沉到项目级**
- ❌ 当用户在别的项目开 Claude Code session,这些"实证 OS 风格"全部不带过去

**唯一可圈点的**:`AGENTS.md:6-10` 写了"默认工作方式:BDD + TDD",且 4 阶段流程(BDD 对齐→TDD→实现→验收)+ 红线 + 例外条款都到位——这是项目级人设的最小骨架。

#### 缺口 & 升级建议

**短期(A 任务)**:
1. 写 `AGENTS.md` 的"灵魂段":声明"我是实证 OS,我的核心使命是 XXX"——但要小心,**不要学 OpenClaw 写散文**(实证 OS 是工程型 agent,不是陪伴型,写"我是 X 我做 Y"比写"我在成为某人"更合适)
2. 把用户级 CLAUDE.md 里的 12 行为规则、`独立判断原则`、中文渲染验证、第三方凭据安全,挑**真正适用于实证经济学研究**的(不是全部)下沉到项目级
3. 写一段"我维护什么 / 我不维护什么"——明示边界,避免 agent 自作主张

**长期**:
- 写一个 `SOUL.md`?如果走 OpenClaw 路线,SOUL.md 应该可被 agent 自己改,但要"改前通知";如果走 Claude Code 路线,SOUL.md 就是**只读**规则集——**先和用户定哲学再写**

---

### 维度 2: 记忆系统(Memory)

#### 一句话总结

记忆是"agent 跨会话保留什么"。4 个产品在"是否自动写、文件还是 DB、是否分类"上分歧最大。

#### 4 个产品对比

| Agent | 做法 | 关键文件 | 哲学 |
|---|---|---|---|
| **Claude Code** | `MEMORY.md` 索引页 + 4-type 文件(user/feedback/project/reference),每条带 `originSessionId` 追溯;**事后手工 + auto-trigger 混合** | `~/.claude/projects/-/memory/MEMORY.md:1-15` + `feedback_quality_first.md` 的 YAML frontmatter | **分类索引**——4 种 memory 类别化 |
| **Codex** | **4 层 memory**:① 原生 SQLite (`memories_1.sqlite`) 存条目 ② 渲染视图 `MEMORY.md` / `raw_memories.md` / `memory_summary.md` ③ OMX 扩展的 `.omx/project-memory.json` + `notepad.md` ④ 每个 session 完整 transcript 在 `archived_sessions/rollout-*.jsonl` | `~/.codex/memories/MEMORY.md` (150K) + `~/.codex/memories_1.sqlite` (438K) + `~/.codex/archived_sessions/` (65+ rollout-*.jsonl) | **多源真相**——SQLite + MD + JSONL 各自管各自的 |
| **OpenClaw** | 三层 + per-agent 隔离:① 日记忆 `memory/YYYY-MM-DD.md` ② 长记忆 `MEMORY.md` ③ per-agent SQLite | `~/.kimi_openclaw/workspace/AGENTS.md:122-149` + `~/.openclaw/memory/main.sqlite` (3.3M) | **agent 自己写**——完全靠 agent 手工写,无自动提取 |
| **Pi Agent** | JSONL session tree(parentId 链表 + leafId 指针),append-only,compaction 写 summary 节点不删旧;**没有跨会话知识库** | `~/pi/packages/agent/src/harness/session/jsonl-storage.ts:8-15` + `session.ts:82-140` | **没有记忆**——"memory" 这个词在 Pi 内部只表示 InMemorySessionStorage,跟"agent 长期知识"无关 |

#### 关键差异表

| 关键点 | Claude Code | Codex | OpenClaw | Pi Agent |
|---|---|---|---|---|
| 自动写入? | 部分(auto-trigger) | 部分(session-end async) | 否(agent 手工) | 否 |
| 跨会话检索? | 是(grep MEMORY.md) | 是(SQLite query) | 是(SQLite) | 是(读 JSONL) |
| 分类? | 是(4 type) | 否(扁平) | 否(flat 日志) | 否(树) |
| 隐私边界? | 弱 | 强(MEMORY.md 主 session only) | 强(`AGENTS.md:122-149` 规定"ONLY load in main session") | 无 |
| 文件大小 | 几十 KB | SQLite 438K + 150K MD | SQLite 3.3M | JSONL 视 session 而定 |

#### 实证 OS 当前状态

**shipped(主骨架)**。实证 OS 的"长期记忆"是 4 个 markdown + 1 个 Python 审计 + 1 棵 `state/` 目录树(86 个 JSON / JSONL):

- `evidence/evidence_bank.md`(12.9 KB):4 张回归表 + 8 条 robustness + approved_findings + verified_bibliography 的真值索引
- `evidence/claim_register.md`(27.0 KB,200+ 行 `| C-NNN | ... |`):C-001 ~ C-200+ 条声明确认登记,字段 `value / source_path / source_anchor / confidence / binding_kind`
- `evidence/integrity_audit.py`(39 KB,6 维度,见维度 5)
- `evidence/pipeline.md`(7.5 KB,5 阶段流水线)
- `state/` 目录:3 个 project-level state + `state/orchestration/`(4 文件 + 1 子目录 orc-*)+ `state/product/`(26 文件含 `agent_task_queue.json` 55.4 KB / `capabilities.json` 678 KB / `variable_role_candidates.json` 537 KB)+ `state/runs/`(51 项,每项 run_*.json + 配套目录)

**partial(自动化层)**:
- 写入证据表**没有"半自动化"**——只能手工或靠 Claude 起草
- `state/product/capabilities.json`(678 KB)是全部 capability 的快照,**没有 diff/版本**
- `state/orchestration/orc-4e95f639ff/` 是 4 月 dry-run 残骸,未清
- 没有任何代码 hook 触发 evidence 表的写入

**claim_register 的硬规则**(用户特别强调):`未经本表登记的数字 = 捏造 = integrity_audit BLOCKER`(`claim_register.md:10-13`)。这是 4 个原生 Agent 都没有的**学术诚信级别**的记忆真值保护。

#### 缺口 & 升级建议

**短期(C 任务)**:
1. 给 `state/product/capabilities.json`(678 KB)加 `version` 字段,做增量 diff——避免每次 init 全量重写
2. 清 `state/orchestration/orc-4e95f639ff/` 等 4 月残骸 + 加 `.gitignore` 规则不提交
3. 把 `state/runs/` 51 个 run 归档,加 LRU(超过 30 天自动压缩)

**长期**:
- 是否要"自动从每次 correction 提取 memory"?(像 Claude Code 那样)——**用户更倾向"半自动"**,所以"agent 起草 → 人工 review → 写入"的 workflow 可能比 auto-trigger 更合适
- 是否要把 `evidence/claim_register.md` 拆成 SQLite?——目前 200+ 行 markdown 仍可读,不必现在拆;但若涨到 1000+ 行,SQLite 是必然

---

### 维度 3: Skills / 能力模块

#### 一句话总结

Skills 是 "agent 能调用什么"。4 个产品都用 SKILL.md + frontmatter 模式,但**元数据丰富度、加载机制、严格度**差异大。

#### 4 个产品对比

| Agent | SKILL.md frontmatter 必有字段 | 加载路径 | 严格度 | 数量 |
|---|---|---|---|---|
| **Claude Code** | `name` + `description`(+ 可选 `trigger: /xxx`) | `~/.claude/skills/<name>/SKILL.md` + 子目录 `references/` `scripts/` `assets/` | 软(SKILL.md 强制 < 500 行是约定不是硬约束) | **136 个**(含 27 个 lark-* symlink) |
| **Codex** | `name` + `description` | `~/.codex/skills/<name>/SKILL.md` + `.codex/skills-archive/`(冷)+ `.codex/skills.disabled/`(热禁用分层) | 中(无 lint,但 marketplace 索引) | **45+ 个**(其中 ~40 个是 OMX 私货) |
| **OpenClaw** | `name` + `description` + 可选 `requires.bins/env` | `~/.openclaw/skills/` + `~/.openclaw/plugin-skills/`(symlink 到 npm 包) + `~/.kimi_openclaw/workspace/skills/` | 中(有 `requires` 依赖声明,但无 lint) | **40+ in workspace, 32 in global** |
| **Pi Agent** | `name` + `description`(+ 可选 `disable-model-invocation: true` 不进 system prompt) | `~/.pi/skills` + `<cwd>/.pi/skills` | **严**(name 强制 `[a-z0-9-]+`,最多 64 字符;`validateName` 在 `harness/skills.ts:281-290` 报错) | 无数据(本机没装) |

#### 关键差异点

1. **frontmatter 严格度**:Pi Agent 唯一有 `validateName` 强制 name 规范,其他都是软规约
2. **依赖声明**:OpenClaw 唯一支持 `requires.bins` + `requires.env`(`skills/ifind-finance-data/SKILL.md` 显式声明 `MINIMAX_API_KEY`),其他靠 skill 作者自己检查
3. **symlink 外部 skill**:Claude Code 用 symlink 链 `~/.agents/skills/lark-*`(27 个 lark-*),OpenClaw 用 symlink 链 `~/.local/lib/node_modules/openclaw/...`(plugin-bundled),都是**版本控制 + 回滚的隐患**
4. **trigger 字段**:Claude Code 唯一用 `trigger: /xxx` 显式声明触发器(比如 `graphify` 的 `/graphify`),其他都靠 description 自动匹配

#### 实证 OS 当前状态

**partial**。**4 大机制在 `evidence/` 下是 3 个 markdown + 1 个 Python,没有 `SKILL.md` 形式**:

- `evidence/pipeline.md` 是**过程式描述**,不是 SKILL.md 风格的"何时调用 / 输入 / 输出"
- `evidence/integrity_audit.py` 是可调用的硬门禁(可 `--section` / `--all` / `--write` / `--json`),**但没有任何 LLM 调用方"知道"它存在**——Claude Code 不会自动跑它(见维度 5)
- 4 机制作为产品/CLI 工具的部分是 `Program/` 下的 110+ 个 `.py` 脚本(`run_paper.py` 13.5 KB / `paper_supervisor.py` / `export_pdf.py` 5.3 KB / `formal_*` 30+ 套件),这些是**命令式 CLI** 而不是 SKILL.md 风格的能力声明

**已落地的工程量**:很多(`Program/` 110+ 脚本,`Product/` FastAPI+React,`tests/` 180 个 pytest 文件其中只有 1 个 `test_integrity_audit.py` 直接对 4 机制),但**LLM 不知道它们存在**。

#### 缺口 & 升级建议

**短期(A 任务 + C 任务)**:
1. 把 `integrity_audit.py` 包装成 `SKILL.md`,frontmatter 写:`name: integrity-audit` / `description: "在每次回答前自动跑 6 维度审计,失败即 BLOCKER;描述 4 机制中的 evidence 真值保护"`——这样 LLM 在 description 匹配时**主动调用**
2. 把 `pipeline.md` 改写成 SKILL.md 形式:写明"何时调用 / 输入 / 输出 / 失败怎么办"
3. 30+ `formal_*` 脚本挑核心 5-8 个写 SKILL.md,其他的放 `references/`

**长期**:
- 是不是要把"全 4 机制 + 30+ 脚本"做成**项目级 skill 集合**?在 `Manuscripts/.claude/skills/`(项目级)还是 `evidence/.claude/skills/`?——**先和用户定结构再写**

---

### 维度 4: 多 Agent 协作

#### 一句话总结

多 agent 是 "agent 怎么并行 / 派工 / 通信"。4 个产品差异巨大:Claude Code 和 Codex 都做实,OpenClaw 是 bindings 路由,Pi 干脆没有。

#### 4 个产品对比

| Agent | 是否有 subagent | 派工机制 | worktree 隔离 | 通信 |
|---|---|---|---|---|
| **Claude Code** | ✅ 有(`Agent` / `Task` 工具) | Task tool 派发,YAML frontmatter 定义(`name` / `description` / `model: inherit` / `skills: [list]`) | ❌ 无显式文档(只有 `superpowers:using-git-worktrees` 插件引用) | 通过 Task 工具的返回值 |
| **Codex** | ✅ 有(`multi_agent` 特性) | `.codex/agents/<name>.toml` 定义,**2 段式**:`max_depth=2 / max_threads=6`,每 sub-agent 独立指定 `model` + `model_reasoning_effort`(`explore.toml` 用 spark + low,`executor.toml` 用 gpt-5.5 + medium) | ❌ 无(OMX team 跑在同一 cwd) | 通过 `omx_state` MCP 共享 plan |
| **OpenClaw** | ✅ 有(4 个常驻 agent) | `agents.list` 在 `~/.openclaw/openclaw.json:189-327`,`bindings` channel→agent 路由,`subagents.maxConcurrent: 8` | ❌ 无 | 共享 SQLite + `.omx/state/` |
| **Pi Agent** | ❌ **没有** | 0 个 subagent,0 个 worktree,多 agent = 同一 session JSONL 树的多个 leaf 节点(fork) | ❌ 无 | 树形 JSONL 父子节点 |

**Pi Agent 维度 4 的明确证据**:`grep "subagent" / "worktree"` 在 `~/pi/packages/agent/src/` 命中 0 个文件。这是**故意的设计**——Pi 是"单 agent 多 turn + session tree 分叉",不是 multi-agent 架构。

#### 关键差异

| 关键点 | Claude Code | Codex | OpenClaw | Pi Agent |
|---|---|---|---|---|
| Max depth | 无限(理论上) | 2 | 不限(4 agent 并行) | 1(单 agent) |
| Max threads | 不限 | 6 | 8 | 1 |
| Model 路由 | 继承(默认) | 每 agent 独立 | 每 agent 独立 | N/A |
| 隔离性 | 工作区共享 | cwd 共享(OMX 共享 state) | 共享 SQLite | 完全隔离(session 文件) |
| 派工 plan 显式化 | 是(supervisor_plan) | 是(omx_state) | 是(bindings) | 否(fork 隐式) |

#### 实证 OS 当前状态

**partial**。OS 有**两套并存的 agent 定义**,而且**不对齐**:

- `state/product/identity.json`(9 个 identity):supervisor / literature_agent / data_agent / identification_agent / modeling_agent / robustness_agent / writing_agent / reviewer_agent / export_agent(`state/product/identity.json:8-124`)
- `Product/backend/workflow_service.py` `RESEARCH_DIMENSIONS` 是 7 个"研究员"(墨白 / 知远 / 数澜 / 量衡 / …)
- `state/product/agent_task_queue.json` 55.4 KB 是 plan→queue 转换的产物(需 `supervisor_plan` 状态为 `approved` + `can_dispatch=true`,见 `agent_task_queue_service.py:36-50`)

**orchestrator 现状**:
- `Product/backend/orchestrator.py:201-227` 有 9 个 stage:`00_intake / 01_sources / 02_literature / 03_strategy / 04_modeling / 05_results / 06_writing / 07_review / 08_final`
- 这是**sequential 编排**而不是真正派子 agent——每一 stage 是当前进程内 `run_stage()` 调用
- `codex_provider.py` 是**唯一接外部 LLM 子 agent** 的桥(`run_local_codex_prompt`),开关 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1` 默认关闭

**没有接的层**:
- ❌ 没有 `subagent` / `agents/*.md` Claude Code 风格的子 agent 配置
- ❌ orchestrator 9-stage 是单进程顺序跑,不是派出去的 worker
- ❌ Claude Code 的 Agent 工具没有接到 orchestrator 派工上

#### 缺口 & 升级建议

**短期(B 任务)**:
1. **先把 7 + 9 套 agent 定义对齐**——是删 `workflow_service.py` 的 7 个研究员?还是把 9 个 identity 折成 7 个?这是定结构决策,先和用户对
2. **写一个 `subagent_dispatch` 的 SKILL.md**——声明"我用 Claude Code Agent tool 派子 agent,每个 agent 跑哪个 stage,model 选什么"
3. **打开 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1`**(如果用户允许)——这样能利用 Codex 的 `multi_agent` 特性做 fast-lane / deep-worker 路由

**长期**:
- 是否要做"论文审计专用 subagent"?——Codex 的 `verifier.toml` 是范本:`description = "Completion evidence, claim validation, test adequacy"`,输出 `Verdict / Evidence / Gaps / Risks` 4 段。**实证 OS 的 audit 完全可以走这条路**

---

### 维度 5: 自检 / 验证(Self-Audit)

#### 一句话总结

自检是 "agent 怎么知道自己的输出对"。4 个产品都做,但**层级**(project / agent / 软 / 硬)不同。

#### 4 个产品对比

| Agent | 自检层级 | 关键机制 | 软/硬 | 关键证据 |
|---|---|---|---|---|
| **Claude Code** | 软约束 | ① CLAUDE.md 12 Behavioral Rules ② `verify-before-present` skill(4 步 16 项)③ `output-anchor` skill(4 要素)④ `Stop` hook 跑 `vibe-island-bridge` | **软**(自检靠模型主动调用,无 hard 阻断) | `~/.claude/skills/verify-before-present/SKILL.md:14-50` |
| **Codex** | 软 + 委托 | ① `verifier.toml` 专用 sub-agent,输出 `Verdict / Evidence / Gaps / Risks` 模板 ② `approvals_reviewer = "guardian_subagent"` 工具调用前过审 ③ `[features].goals = true` 目标追踪 | **半硬**(verifier 必须输出固定模板,但 verdict 是否 pass 由 verifier 自觉) | `~/.codex/agents/verifier.toml:1-3` + `config.toml:18` |
| **OpenClaw** | 软 + 循环 | ① `self-improvement` hook 在 `agent:bootstrap` 注入 `.learnings/` 提醒 ② `.learnings/LEARNINGS.md` 定义 schema(behavioural → SOUL.md / workflow → AGENTS.md / tool gotchas → TOOLS.md) | **软**(没强制;LEARNINGS.md 实际是空壳) | `~/.openclaw/hooks/self-improvement/handler.js:1-57` |
| **Pi Agent** | 项目级硬门禁(非 agent 级) | ① pre-commit 跑 `npm run check`(biome lint + tsgo + pinned-deps + shrinkwrap)② CI 跑 `npm audit` + `npm audit signatures` ③ PR 自动关闭机制当 lint 网关 | **硬**(commit 时 lint 不过就拦) | `~/pi/.husky/pre-commit:1-46` + `package.json:14-20` + `.github/workflows/npm-audit.yml:1-32` |

#### 关键差异:agent 自检 vs 项目自检

| 关键点 | Claude Code | Codex | OpenClaw | Pi Agent |
|---|---|---|---|---|
| Agent 跑完任务后回头 audit 自己输出? | 否(只在 stop hook 发个 bridge 通知) | 部分(verifier 自觉) | 否(LEARNINGS.md 需手工 log) | **否**(没有这层) |
| 验证产出硬门禁? | 否 | 否(verdict 软) | 否 | **是**(commit 拦) |
| 验证产物存哪? | session jsonl | verifier output | `.learnings/LEARNINGS.md` | CI logs |

#### 实证 OS 当前状态

**shipped(主骨架)但未自动跑**。`evidence/integrity_audit.py` 是**核心自检**:

- **6 维度**(`integrity_audit.py:773-780` 顺序固定):
  1. **Required Files** —— 4 个必备文件 `evidence/evidence_bank.md` / `evidence/claim_register.md` / `evidence/pipeline.md` / `Manuscripts/sections/{name}.md`
  2. **Section Completeness** —— 中文字符数 ≥ `SECTION_MIN_CHARS`(abstract 400, main-results 2500, …) + 引用 evidence_id 不少于 `SECTION_MIN_EVIDENCE_REFS`
  3. **Number Anchoring** —— 文中数字必须出现在 claim_register / evidence_bank;4 位以上小数 → BLOCKER
  4. **Forbidden Patterns** —— 8 条历史捏造指纹(E-value=1.18 / Acemoglu 0.5% / Dauth 0.4% / Sobel 30/70% / Baron-Kenny 1986 / 2005-2007 基期 / 剔除 2014 年 / OLS 系数被高估)+ p-value 孤儿 + 弱断言词 + 逻辑跳跃密度
  5. **Source-of-Truth Drift** —— 4 张回归表 coefficient_rows 必须在文中出现或标 narrative
  6. **Gap Honesty** —— `GAP_SCOPE` 7 gap × 2 section 集合,缺显式声明 = BLOCKER
- **退出码**:0=CLEAN / 1=BLOCKED / 2=工具错误
- **5/5 CLEAN 含义**:当前 main-results.md 跑出 6 维度 × 1 INFO(全 CLEAN),共 6 findings,Gate verdict=**READY**——**注意是 6 维度不是 5**(5 是 pipeline.md 早期版,当前 6)
- **GAP_SCOPE**(`integrity_audit.py:498-506`):7 个 gap 各自归属 main-results / robustness-mechanisms-heterogeneity 的子集;`evidence_bank §6` 列 8 个 gap(GAP-001~008),audit 只硬检查 7 个(GAP-008 没硬约束)

**已落盘审计**:9 个 `evidence/integrity_audit_<section>.md`(`integrity_audit_abstract.md` ~ `integrity_audit_robustness-mechanisms-heterogeneity.md`),全部 6 维度 CLEAN。

**关键问题**:
- ❌ **不是每次回答前自动跑**——`tests/test_integrity_audit.py` 是 `unittest`,需要 `python3 -m unittest` 或 `pytest` 显式触发;`pipeline.md:84-87` 写 `python3 evidence/integrity_audit.py --section <name> --markdown --write`,需要人/Agent 主动跑
- ❌ `pipeline.md:163-164` 写"把 audit 接入 `paper_supervisor.py` 流水线作为 export gate"——**TODO,没做**
- ❌ audit 输出 markdown 给人看,没有发到 reviewer/regulator 自动化通道

#### 缺口 & 升级建议

**短期(C 任务)**:
1. **写项目级 `.claude/settings.json`**,把 `integrity_audit.py` 接到 PostToolUse(每次 Edit/Write 后自动跑 `--section` 当前文件),`exit code != 0` 时 block——这才是真正的 hard 门禁
2. **把 `integrity_audit.py` 包装成 SKILL.md**(见维度 3 建议 1),让 LLM **主动**调用
3. **`GAP-008` 加入 GAP_SCOPE**(`integrity_audit.py:498-506` 加一行)

**长期**:
- audit 接入 `paper_supervisor.py` 流水线作为 export gate——这是 `pipeline.md:163-164` 的 TODO,**做完等于让 audit 从"事后审计"变成"流水线环节"**

---

### 维度 6: State 模型

#### 一句话总结

State 是 "agent 的所有持久数据怎么组织"。4 个产品在"JSON 文件 / SQLite / JSONL 树"上各有偏好,**没有统一规范**。

#### 4 个产品对比

| Agent | State 物理存储 | 状态机 | 版本化 | 真相源数量 |
|---|---|---|---|---|
| **Claude Code** | 多层 JSONL event-sourcing:① `projects/-/<session-uuid>/<session-uuid>.jsonl` ② `history.jsonl`(1.9MB 用户历史)③ `paste-cache/` `image-cache/` `file-history/` ephemeral | 无(append-only 流) | 无 | 5+(jsonl + memory + history) |
| **Codex** | **多 DB 多文件混合**:`state_5.sqlite`(13MB)+ `logs_2.sqlite`(3GB,带 WAL 78MB)+ `memories_1.sqlite`(438K)+ `goals_1.sqlite`(24K)+ `session_index.jsonl`(33K)+ `.codex-global-state.json`(1.7MB Electron-style)+ `.omx/state/`(OMX 私货) | 无显式状态机 | 无 | **7 处真相源** |
| **OpenClaw** | 配置 JSON(12.7K `openclaw.json` + 6 个 `openclaw.json.bak*` + `openclaw.last-known-good.json`)+ per-agent JSON(`models.json` `auth-profiles.json` `auth-state.json`)+ SQLite 运行时(`flows/registry.sqlite` `tasks/runs.sqlite`)+ `logs/config-health.json` | 无显式状态机 | 是(备份带语义标签 `clobbered.2026-04-06T02-50-05-548Z`) | 6+ |
| **Pi Agent** | 双层:① mutable in-memory holder ② append-only JSONL session tree(parentId 链表 + leafId 指针) | `AgentHarnessPhase = "idle" / "turn" / "compaction" / "branch_summary" / "retry"`(`harness/types.ts:492`) | 是(`CURRENT_SESSION_VERSION = 3`,有 migration) | 1+1(JSONL tree + in-memory) |

#### 关键差异

| 关键点 | Claude Code | Codex | OpenClaw | Pi Agent |
|---|---|---|---|---|
| Append-only? | 是 | 否(全量 state 持久化) | 否 | 是 |
| 状态机声明? | 否 | 否 | 否 | **是**(5 phase union) |
| Schema 文档? | 否 | **否**(7 处真相源无 schema) | 否(`exec-approvals.json` 是手填 UUID) | 部分(types.ts) |
| GC 策略? | 否 | **否**(`logs_2.sqlite` 已 3GB 在涨) | 否(备份手工) | 否(线性扫描全文件) |
| 回滚机制? | **手 cp backup** | 自动(`config.toml.backup.*` 滚 17 份) | **语义化备份**(`openclaw.json.clobbered.2026-04-06...`) | 无(session 树是唯一真源) |

#### 实证 OS 当前状态

**partial**。`state/` 目录是声明式 JSON 树,**不是**严格状态机:

```
state/
├── README.md
├── project_state.json           # 本科论文总状态
├── cfps_robot_project_state.json # CFPS robot 项目
├── source_registry.json         # 数据源只读登记
├── orchestration/               # 老 dry-run 残骸 + 探索 ledger
│   ├── argument_graph.json
│   ├── confirmation_ledger.jsonl
│   ├── exploration_ledger.jsonl
│   ├── literature_clues.jsonl
│   ├── source_registry.json
│   └── orc-4e95f639ff/         # 2026-04-24 dry-run run 残骸
├── product/                     # 26 个产品状态
│   ├── agent_task_queue.json    # 55.4 KB
│   ├── capabilities.json        # 678 KB(没 diff)
│   ├── cost_events.jsonl / cost_summary.json
│   ├── dataset_import_preflights.json # 1.2 MB
│   ├── design_spec.json / run_plan.json
│   ├── formal_submission_package_*.json
│   ├── identity.json            # 9 agents
│   ├── manuscript_candidate_*.json
│   ├── permissions.json
│   ├── research_question.json   # 7 个 decision_events
│   ├── reviewer_scorecard.json  # overall_score=61
│   ├── supervisor_plan.json     # status=approved, can_dispatch=true
│   ├── variable_role_candidates.json # 537 KB
│   ├── variable_roles_drafts.json # 494 KB
│   ├── verifier_checks.json     # 8 gate, 7 passed
│   └── writeback_approvals.json
├── proposals/
│   └── variable_role_reconciliation.json
└── runs/                        # 51 个 run_<id>/ + 30 个 run_<id>.json
```

**真状态机只在 `orchestrator.py`**:`CheckpointStatus`(PENDING/APPROVED/REJECTED/MODIFIED)4 值,`HITL_STAGES` 5 个 stage 名称;**不是**全局状态图——各 service 各管各的 JSON。

**关键事件 log 风格**:`research_question.json:13-62` 7 个 `decision_events` 记录选题确认(都是 user actor)——这是**append-only event log** 风格,值得学 Codex 7 处的"真相源 + 视图"分离。

#### 缺口 & 升级建议

**短期**:
1. 清 `state/orchestration/orc-4e95f639ff/` 等 4 月残骸
2. `state/runs/` 51 个 run 归档,加 LRU
3. `state/product/capabilities.json`(678 KB)加 `version` 字段,做增量 diff

**长期**:
- 学 OpenClaw 把备份命名带**事故上下文**(`clobbered.2026-04-06...`),不是简单时间戳
- 学 Pi Agent 显式声明状态机——`AgentHarnessPhase` 那种 5 phase union 写法值得借鉴

---

### 维度 7: Tool 调用层

#### 一句话总结

Tool 是 "agent 怎么调外部能力"。4 个产品都用某种 schema 协议,但**协议类型、内置 vs 外部、是否统一**差异大。

#### 4 个产品对比

| Agent | 工具 schema | 内置工具 | 外部工具 | 隔离 |
|---|---|---|---|---|
| **Claude Code** | 6 内置 tool + MCP 200+(lazy load) | Bash / Read / Edit / Write / Grep / Glob | `mcp.json` 注册 7 个(用户级),运行时 lazy load 更多(arxiv-mcp / codex / playwright / chrome-devtools / tldraw / context7 / stata-mcp / vercel / pdf) | MCP server 子进程 |
| **Codex** | **MCP 标准**(Model Context Protocol, JSON-RPC over stdio) | 平台内置 tool(Rust 二进制内部,**不走 MCP**:`exec_command` / `apply_patch` / `web_search`) | `config.toml:20-91` 9 个 `[mcp_servers.*]`,plugin marketplace 加载若干个 | MCP server 子进程 |
| **OpenClaw** | **多协议混用**:anthropic-messages / openai-completions / openai-responses / ollama / kimi-claw 私有 ACP | `tools.profile: "full"`,含 `web.search` / `web.fetch` / `elevated` / `exec.applyPatch` | `cliBackends`: `codex-safe` / `codex-write` / `claude-code` 三个外部 CLI 进程 + `mcp.servers.peekaboo` | per-agent exec-approvals allowlist |
| **Pi Agent** | **TypeBox schema**(不是 Zod) | 7 个(`coding-agent/src/core/tools/index.ts:96-115`:`read` / `bash` / `edit` / `write` / `grep` / `find` / `ls`) | **无外部 MCP**(纯 CLI 内置) | 工具级 `executionMode`(sequential/parallel) |

#### 关键差异

| 关键点 | Claude Code | Codex | OpenClaw | Pi Agent |
|---|---|---|---|---|
| 内置 tool 数量 | 6 | 3-4 | 4 | 7 |
| 外部 tool 协议 | MCP(标准) | MCP(标准) | **多协议混用** | 无 |
| 工具调用超时控制? | 无显式 | `tool_timeout_sec = 600.0` | 无显式 | 无显式 |
| 工具沙箱? | 无(由 hook 转 bridge 决定) | **`sandbox_mode = "workspace-write"` 3 档**(`read-only` / `workspace-write` / `danger-full-access`) | `browser.ssrfPolicy` 域名白名单 | 无 |
| 工具权限? | 无(allow-by-permission 哲学) | **deny-by-default** + `default.rules` 60K 白名单 | `exec-approvals.json` per-agent allowlist | 无(工具名分组) |

#### Codex 的 sandbox 哲学(用户特别需要学)

Codex 的"3 档 sandbox"是 4 个产品里**最严的权限模型**:
- `read-only`:只能读
- `workspace-write`:可写工作区,不能改系统
- `danger-full-access`:全开

加上 `default.rules` 60K 行白名单,只放行显式枚举的命令(任何 `rm -rf` / `git push --force` 都要先追加规则),**这是值得实证 OS 学的**——尤其"算 Stata 数据"这种"运行脚本 → 生成数字"的工作流,如果 sandbox 跑飞了,数就废了。

#### 实证 OS 当前状态

**shipped(产品后端)但 partial(项目级 MCP)**:

- `Product/backend/llm_client.py:37-97` 定义 5 个 `ProviderPreset`:`openrouter` / `kimi-code` / `kimi-code-anthropic-token` / `moonshot-kimi` / `custom-openai`
- `Product/backend/codex_provider.py:10-40` 检查 `codex` CLI 是否在 PATH,提供 `run_local_codex_prompt`
- `Product/backend/execution_backend_service.py` 16.5 KB 是**产品后端**的 StatsPAI/Python/StataMCP/Codex 子 Agent 后端路由层

**关键缺口**:
- ❌ **没有 `~/.claude/mcp-servers/empirical-os.json` 这种项目级 MCP server 注册**——Claude Code session 看不到 `integrity_audit` / `claim_register` / `pipeline`
- ❌ 5 个 LLM provider 写死,加新 provider 要改 dataclass
- ❌ `execution_backend_service.py` 后端路由 16.5 KB,但没有暴露成 API 给 Claude Code

#### 缺口 & 升级建议

**短期(C 任务)**:
1. 把 `integrity_audit.py` 包装成 MCP server(`mcp__empirical_os__audit_section` / `mcp__empirical_os__validate_claim`),写到项目级 `.claude/mcp-servers/empirical-os.json`
2. 把 `claim_register.md` 暴露成 `mcp__empirical_os__lookup_claim(C-NNN)` 工具
3. 把 `evidence_bank.md` 暴露成 `mcp__empirical_os__get_finding(finding_id)` 工具

**长期(B 任务)**:
- 学 Codex sandbox 3 档 + 60K 白名单——给实证 OS 加"读 only"模式(只读 Raw + Evidence,不写 Product)

---

### 维度 8: LLM Provider 抽象

#### 一句话总结

Provider 是 "agent 怎么接多家 LLM"。这是 4 个产品差异**最大**的维度。

#### 4 个产品对比

| Agent | 主推模型 | 第三方支持 | provider 抽象层 |
|---|---|---|---|
| **Claude Code** | Claude 系(本机用 `MiniMax-M3` 走 `minimaxi.com/anthropic` 代理) | **协议级 hack**:`ANTHROPIC_BASE_URL` + `ANTHROPIC_AUTH_TOKEN` env var 把请求重发到 Anthropic 兼容端点 | **无**——所有 model 都走 Anthropic SDK,通过 env var 重定向 |
| **Codex** | OpenAI 专有 `gpt-5.5` / `gpt-5.3-codex-spark` / `gpt-5-codex` | `--oss` 切 `lmstudio` / `ollama` 本地模型;`--remote` 切自托管 app-server WebSocket;**不直连 Anthropic / Google** | stub 级别(9 个 model slug 都是 OpenAI 系) |
| **OpenClaw** | OpenAI / Ollama / OpenRouter 5+ providers(`petclaw-1.0` / `minimax-portal` / `minimax` M2.7 / `openai-codex/gpt-5.5` / `ollama` / `openrouter`) | **多 provider 动态 merge**(`mode: "merge"`);Kimi 实例被故意锁死 1 个 provider(自家电网关) | `agents.defaults.model.primary` + `imageModel.primary` 分开 |
| **Pi Agent** | **9 个 lazy provider**:`anthropic-messages` / `openai-completions` / `openai-responses` / `openai-codex-responses` / `google-generative-ai` / `google-vertex` / `mistral-conversations` / `azure-openai-responses` / `bedrock-converse-stream` | **行业最工程化**:`packages/ai/src/api-registry.ts:1-99` `registerApiProvider<TApi, TOptions>` + 25+ provider env var(`env-api-keys.ts:91-210`)+ 独立 `proxy.ts:1-368` 走 SSE 重放 | `packages/ai` 是无 UI 依赖的纯 LLM 客户端,可被别处用 |

#### 关键差异表

| 关键点 | Claude Code | Codex | OpenClaw | Pi Agent |
|---|---|---|---|---|
| Provider 数量 | 1(Anthropic)+ 任意兼容端点 | 1(OpenAI)+ 2 OSS | 5+(OpenAI / Ollama / OpenRouter / Kimi / PetClaw) | **9+**(覆盖 5 大厂商) |
| 抽象层在哪 | env var hack | `config.toml` slug | `openclaw.json` JSON | 独立 `packages/ai` 包 |
| OAuth 支持 | 无(走 API key) | 无(走 OpenAI) | 单独 `ai/oauth` 子路径 |
| reasoning effort 抽象 | 无(走 `extended thinking`) | 4 档(`low/medium/high/xhigh`) | 无(每 provider 各自字段) | 无(每 provider 各自) |
| 是否 lazy load | 否 | 否 | 否 | **是**(browser bundle 友好) |

#### 实证 OS 当前状态

**shipped(产品后端)但双轨**。两套 LLM provider 互不知:

- `Product/backend/llm_client.py:20-21` `DEFAULT_PROVIDER = "openrouter"` + `DEFAULT_TIMEOUT = 120`
- `llm_client.py:37-97` 5 个 `ProviderPreset`(frozen dataclass):`id` / `api_type`(`openai-compatible` / `anthropic-compatible`)/ `base_url` / `default_model` / `models` / `api_key_env` / `doc` / `requires_api_key`
- `codex_provider.py:82-86` 拒绝在 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC != "1"` 时执行

**两套独立 LLM 抽象**:
- 用户级 Claude Code session:走 `~/.claude/settings.json` 的 `ANTHROPIC_BASE_URL` 指向 `api.minimaxi.com/anthropic`,用 `MiniMax-M3` 冒充三档 Claude
- 产品后端:走 `Product/backend/llm_client.py` 的 openrouter / kimi / moonshot / custom-openai

#### 缺口 & 升级建议

**短期**:
1. **统一 provider 抽象**——是否把 `Product/backend/llm_client.py` 的 5 个 preset 提到 session 层?(技术上行得通:用 `mcp__empirical_os__llm_call(provider_id, ...)` 暴露)
2. **打开 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1`**(如果用户允许)——这样实证 OS 能用 Codex 的 `multi_agent` 特性

**长期**:
- 学 Pi Agent 拆 `packages/ai`——把 provider 抽象层独立,让 product 后端、session 层、external agent(Codex / Claude Code)都共用一套
- 学 OpenClaw 拆 `primary` model + `imageModel`——实证 OS 写论文时可能"用 Claude 写文字,用 GPT-5 跑 code"

---

### 维度 9: UI / TUI 层

#### 一句话总结

UI 是 "用户怎么用 agent"。4 个产品形态不同:TUI / Web / Desktop / Canvas 各有偏好。

#### 4 个产品对比

| Agent | 主形态 | 辅助形态 | 关键证据 |
|---|---|---|---|
| **Claude Code** | **TUI**(stdin/stdout) | statusLine + HUD plugin(`claude-hud@jarrodwatts` 0.0.10 / `claude-hud@claude-hud` 0.0.12);Warp / Vercel 集成;`ide/` 目录;**无 first-party GUI** | `~/.claude/settings.json:144-147` 的 statusLine;用户偏好 cmux |
| **Codex** | **TUI + Desktop GUI + app-server + remote-control** | `--no-alt-screen` 切 inline 模式;`[desktop]` 段管主题 / 字体 / 头像 / git force-push 策略;`app-server` 是 stdio JSON-RPC 供 IDE 挂载;`remote-control` 走 WebSocket | `~/.codex/config.toml:376-387` 的 `[tui]` 6 chip status_line + `[desktop]` 段 |
| **OpenClaw** | **本地浏览器(Gateway 端口 19789) + 控制 UI canvas** | `~/.kimi_openclaw/canvas/index.html` 3.8K 极简 canvas;Chrome user-data-dir 完整 profile + NativeMessagingHosts;TUI 只剩 `last-session.json` 348 字节 | `~/.openclaw/openclaw.json:392-413` 的 `gateway.port: 19789` + `canvas/index.html` |
| **Pi Agent** | **TUI**(独立 `pi-tui` 包) | `interactive-mode.ts` 189KB 单文件做完整 CLI;`rpc` 模式是裸 JSON-RPC;`print-mode` 是 `-p` 一次性 prompt;**无 Web UI** | `~/pi/packages/tui/src/tui.ts:1` 44KB `TUI` 类;`interactive-mode.ts:1` 189KB |

#### 关键差异

| 关键点 | Claude Code | Codex | OpenClaw | Pi Agent |
|---|---|---|---|---|
| First-party GUI? | ❌ | ✅(Electron Desktop) | ❌(用 Gateway + 浏览器) | ❌ |
| TUI 渲染器 | Ink 风格(Anthropic 内部) | 自家 Rust 渲染器 | **残缺**(只 last-session.json) | `pi-tui`(differential render + CSI 2026) |
| Web UI? | ❌ | ❌ | ✅(canvas + Gateway) | ❌ |
| 远程控制? | 无显式 | ✅(`remote-control` WebSocket) | ✅(Gateway 19789) | ❌ |

#### 实证 OS 当前状态

**shipped(Web UI 全套)但 partial(OS 自己的 TUI)**:

- `Product/serve_product.py` 159 字节 + `Product/app.py` 70.6 KB(FastAPI)启动静态前端
- `Product/web-react/` React + Vite 前端,`src/components/` 8 个组件:`AgentActivityPanel` / `DottedSurface` / `FormalPackageAcceptancePanel` / `ResearchCommandInput` / `SemanticGlowCards` / `SlideTabs` / `SupervisorPlanReview` / `TaskBriefDemo`
- `Product/web-dist/` 是构建产物(2026-05-27 旧,有 `index-B8qwd-58.css` / `index-PnmVioUM.js`)
- `.omx/` 目录是 OMX(任务调度/监控)子系统的 state:`metrics.json`(total_turns=1,2026-05-22)/ `state/sessions/` + `state/subagent-tracking.json`(一个 leader thread,turn_count=1)

**用户使用**:
- 主入口:Claude Code 原生 TUI + cmux
- 附属:实证 OS Product Web UI(`http://127.0.0.1:8765`)——被 Claude Code session 调起来

**关键缺口**:
- ❌ 没有 OS 自己的 TUI(repl / status bar)
- ❌ `Product/web-dist/` 5/27 后没 rebuild,`git status -s` 显示 `M Product/web-dist/index.html` 和 `D Product/web-dist/assets/index-B8qwd-58.css`
- ❌ `.omx/` 残骸 5/22 后没新增数据

#### 缺口 & 升级建议

**短期**:
1. `Product/web-dist/` 重新构建,清 `.gitignore` 例外
2. `.omx/` 残骸清理

**长期**:
- 是否要 OS 自己的 TUI?(像 Pi Agent 的 `pi-tui` 那样)——这取决于"实证 OS 是 agent 工具"还是"实证 OS 是产品"——目前是后者(有 Web UI),不是前者
- 学 Codex `[tui]` 6 chip status_line——给 `Product/web-react/` 加 agent 实时状态展示

---

### 维度 10: Hook / 事件系统

#### 一句话总结

Hook 是 "agent 哪个事件点可以插代码"。4 个产品都有,但**事件数、配置位置、能否阻断**差异大。

#### 4 个产品对比

| Agent | 事件数 | 关键事件 | 配置位置 | 能否阻断? |
|---|---|---|---|---|
| **Claude Code** | **12** | Notification / PermissionRequest / PostToolUse / PreCompact / PreToolUse / SessionEnd / SessionStart / Stop / SubagentStart / SubagentStop / UserPromptSubmit | `~/.claude/settings.json:18-143` 完整 hooks block | **隐式**(`exit 1` 能不能 block tool call 没在配置中显式;实际本机所有 hook 都 `exit 0` 不阻断) |
| **Codex** | **6** | SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / PermissionRequest / Stop | `~/.codex/hooks.json:1-62`(6 事件定义)+ `config.toml:392-422` 的 `[hooks.state]` 11 条 trusted_hash(SHA256) | 是(SHA256 trust hash 不匹配就拒) |
| **OpenClaw** | **1 公开 + 27 bundled** | `agent:bootstrap`(公开) | `~/.openclaw/hooks/self-improvement/handler.js` + `openclaw.json:379-388`(`hooks.internal.entries.self-improvement`) | 否(只 bootstrap 注入) |
| **Pi Agent** | **17**(`AgentHarnessOwnEvent`) | `before_agent_start` / `context` / `before_provider_request` / `before_provider_payload` / `after_provider_response` / `tool_call` / `tool_result` / `session_before_compact` / `session_compact` / `session_before_tree` / `session_tree` / `model_update` / ... | `~/pi/packages/agent/src/harness/types.ts:634-660` + `agent-harness.ts:249-292` | **是**(handler 可返回 patch 改 streamOptions 或 block) |

#### 关键差异

| 关键点 | Claude Code | Codex | OpenClaw | Pi Agent |
|---|---|---|---|---|
| 事件数 | 12 | 6 | 1+27 bundled | **17** |
| 事件命名空间 | 平(全是 1 段) | 平 | `agent:bootstrap` 命名空间 | 平 |
| Handler 类型 | 外部 shell command | 外部 shell command + SHA256 trust | 内部 handler.js | 内部 typed handler |
| PreToolUse 是否有效? | 是(挂 rtk hook) | **否**(本机 PreToolUse 是空数组 `hooks.json:26-28`) | 无 | 是(在 agent-loop.ts:562-626) |
| Stop 钩子? | 是(发 vibe-island-bridge 通知) | 是 | **否** | 是(在 session_after 段) |
| Hook 失败重试? | 无 | 无 | 无 | **无**(handler 错误就 throw) |

#### Codex 的 hook trust hash(用户需要学)

Codex `hooks.state` 表存每个钩子的 SHA256 `trusted_hash`,改 `hooks.json` 任意一行就会 hash mismatch——这意味着**hook 本身也是被签名保护的第一类对象**,不是"配置文件随便改"。

实证 OS 的 audit 完全可以学这个:把 `integrity_audit.py` 接到 PostToolUse,并在 `hooks.state` 表里加 SHA256 信任——audit 脚本被改了,Claude Code session 立刻发现。

#### 实证 OS 当前状态

**partial(项目级 0 个 hook;产品后端内部有 event bus)**:

- 项目级 0 hook:整个项目根下没有 `.claude/hooks/` 也没有 `.claude/settings.json`
- 用户级 8 个 hook:全部调 `$HOME/.vibe-island/bin/vibe-island-bridge`(`exit 0` 不阻断)+ Bash matcher 上挂 `rtk hook claude`(token 优化)
- `state/orchestration/run_event_bus.py` 是**产品后端**内部事件总线(`emit_event(run_id, "stage.start", ...)`),**不**接 Claude Code hook 系统
- `Product/backend/orchestrator.py:290-296` `emit_event` 在 `stage.start` 时跑——这是**应用内**事件,不是 OS hook

**关键缺口**:
- ❌ 没有项目级 `.claude/settings.json` 把 `integrity_audit.py` 接到 PostToolUse/PreCommit
- ❌ PreToolUse 没接 `evidence` 写入
- ❌ 用户级 hook 都被 `vibe-island-bridge` 吃了,实证 OS 想加 hook 必须改 `~/.claude/settings.json`(项目不可控)

#### 缺口 & 升级建议

**短期(C 任务)**:
1. **写项目级 `.claude/settings.json`**,把 `integrity_audit.py` 接到 PostToolUse(Edit/Write/Write→ 跑 `--section` 当前文件),exit code != 0 时发 Stop signal
2. **接 `Stop` 钩子**——session 结束时跑"今日 audit summary",生成 1 份 `integrity_audit_session.md`
3. **接 `UserPromptSubmit`**——每次用户提问时跑"research_question 状态检查",确认题目没变

**长期**:
- 学 Codex hook trust hash——给 `integrity_audit.py` 自身加 SHA256 保护

---

### 维度 11: 依赖安全

#### 一句话总结

依赖安全是 "怎么保护 agent 不被恶意 plugin / skill 干掉"。4 个产品在 "沙箱 / 签名 / secret scan / SBOM" 上做的不一样。

#### 4 个产品对比

| Agent | 沙箱 | 签名 / 校验 | secret scan | SBOM | 关键证据 |
|---|---|---|---|---|---|
| **Claude Code** | 无(只 RTK proxy 透明重写 Bash) | 无(明文 token 写 settings.json) | **无** | 无 | `~/.claude/settings.json:3` 明文 `ANTHROPIC_AUTH_TOKEN` |
| **Codex** | **3 档 sandbox**:`read-only` / `workspace-write` / `danger-full-access` + `default.rules` 60K 白名单 | **无**(skills 无签名) | 无(单 server 自己加 `HERMES_REDACT_SECRETS=true`) | 无 | `~/.codex/config.toml:11` + `rules/default.rules` 63.9K |
| **OpenClaw** | `browser.ssrfPolicy` 域名白名单 + `exec-approvals` per-agent allowlist | **SHA-512 + shasum 双重**(`installs.json`) | 无(skills 缺签名) | 无 | `~/.openclaw/plugins/installs.json:11-22` |
| **Pi Agent** | 无(只 `npm ci --ignore-scripts`) | `save-exact=true` + `min-release-age=2` + shrinkwrap + lifecycle allowlist | **无 secret scan**(没看到 gitleaks/trufflehog) | 无(没有 SBOM / CycloneDX) | `~/pi/.npmrc:1-2` + `.github/workflows/npm-audit.yml:1-32` |

#### 关键差异表

| 关键点 | Claude Code | Codex | OpenClaw | Pi Agent |
|---|---|---|---|---|
| 沙箱? | ❌ | ✅✅✅(3 档) | ✅(per-agent) | ❌(只 npm ci ignore-scripts) |
| 命令白名单? | ❌ | ✅(60K 行) | ✅(per-agent allowlist) | ❌ |
| Skill 签名? | ❌ | ❌ | ✅(SHA-512 + shasum) | ✅(save-exact + min-release-age) |
| Secret scan? | ❌ | ❌ | ❌ | ❌ |
| 依赖审计? | 无 | 无 | 无 | ✅✅(`npm audit` + `npm audit signatures` 每日) |
| 网络策略? | 无(network 默认开) | `network_access = true` 默认 | `browser.ssrfPolicy` 白名单 | 无 |

#### 实证 OS 当前状态

**partial(只读源 + SHA256 record 有,但 secret/PDF 哈希/dedup 没落地)**:

- `state/orchestration/source_registry.json:1-7` 顶层 `policy`:`raw_data_mutable=false` / `registered_sources_only=true` / `promotion_rule="Copy selected source files into project workspaces; never mutate the desktop motherlode."`
- `state/orchestration/source_registry.json:8-40` 3 个 source 注册:数据集(`/Users/mahaoxuan/Desktop/实证数据库`)+ Zotero(`/Users/mahaoxuan/Zotero`)+ PDF 库(`/Users/mahaoxuan/Desktop/论文核心素材库/1_文献/PDF原文`)
- `tests/test_external_dataset_import_apply.py:1-100` 测试 import apply 时**记 SHA256** + size + target_path + `dataset_import` provenance
- ❌ **没有 `.env` 管理**,API key 只在 `api_key_env` 字符串里
- ❌ PDF hash 链没有(`pdf_library_root` 注释说"Deduplicate semantically by title, DOI, and hash rather than filename",**没实现**)
- ❌ 没有 secret leak scanner(grep `sk-` / `ghp_`)
- ❌ `evidence/claim_register.md` 没有 integrity seal(每行 C-XXX 没法验真)

#### 缺口 & 升级建议

**短期**:
1. **写 `.env.example`**,列出 5 个 LLM provider 需要的 env var(从 `llm_client.py:37-97` 提取)
2. **加 PDF hash 链**——`Program/Clean/pdf_dedup.py` 读 PDF 文件,SHA256 + size 写到 `evidence/pdf_hash_chain.json`
3. **学 Codex sandbox**——给实证 OS 加 3 档 sandbox(`read-only` / `read-write-data` / `full`)

**长期**:
- 学 OpenClaw SHA-512 签名——给 evidence 表加 integrity seal(每行 C-XXX 末尾带 SHA256)
- 学 Pi Agent 每日依赖审计——给 empirical OS 加 `pip-audit` + `npm audit` cron

---

### 维度 12: 版本管理 + 发布

#### 一句话总结

版本是 "agent 怎么迭代 / 回滚 / 发布"。4 个产品在"semver / lockstep / 自动备份 / rollback" 上差异大。

#### 4 个产品对比

| Agent | 版本模型 | 自动备份 | Rollback | 发布 | 关键证据 |
|---|---|---|---|---|---|
| **Claude Code** | **无显式 `claude --version`** | **23+ 份 `settings.json.backup.*`**(`before-gpt-light-switch` / `before-kimi-rollback` / `codex-gpt55` / `claude-code-proxy` / `2026-04-27T15-09-12Z` 等) | **手 cp backup**(无 first-party `claude rollback`) | 不可见(本机无版本 evidence) | `~/.claude/settings.json.backup.*` 23 份 |
| **Codex** | **SemVer 0.135.0**(本机安装)+ 6 platform-specific 二进制(linux-x64 / linux-arm64 / darwin-x64 / darwin-arm64 / win32-x64 / win32-arm64) | 自动(`config.toml.backup.*` 滚 17 份) | `codex update` 自更新(无 schema 迁移工具) | npm + 6 平台二进制 | `~/.codex/version.json:1` |
| **OpenClaw** | **多文件版本信号**:`meta.lastTouchedVersion: "2026.5.20"` + `lastTouchedAt` | **手工触发备份**(`openclaw.json.bak-20260513-desktop-shell-phase3` / `openclaw.json.before-kimi-channel-schema-fix-2026-05-22T22-25-00` / `openclaw.json.clobbered.2026-04-06T02-50-05-548Z`——**带事故上下文**) | 手 cp backup | plugin 更新走 `openclaw plugins update` | `~/.openclaw/openclaw.json:2-4` |
| **Pi Agent** | **Lockstep versioning**:4 个包(`@earendil-works/pi-ai` / `pi-agent-core` / `pi-tui` / `pi-coding-agent`)共享 0.78.0;major=breaking, minor=新功能+fix,patch=fix | **changelog + release tag**(`## [Unreleased]` → `## [0.79.0] - 2026-XX-XX`) | **回滚 = git revert + git tag**(有 release tag) | `scripts/release.mjs` 半自动:`npm version` 同步所有包 → 更新各 package `CHANGELOG.md` 的 `[Unreleased]` → `git commit "Release vX.Y.Z"` + `git tag vX.Y.Z` → push → CI 用 GitHub OIDC trusted publishing 上 npm | `~/pi/scripts/release.mjs:107-126` + `AGENTS.md:104-119` 详细写 changelog 5 段格式 |

#### 关键差异表

| 关键点 | Claude Code | Codex | OpenClaw | Pi Agent |
|---|---|---|---|---|
| 版本号可见? | **否** | 是(0.135.0) | 是(2026.5.20) | 是(0.78.0) |
| SemVer 严格? | N/A | 是(0.135.0) | 否(2026.5.20 是日期 + 周次) | 是(0.78.0) |
| 备份命名? | 简单时间戳 / 语义标签 | 简单时间戳 | **带事故上下文** | N/A(用 git tag) |
| 自动备份? | 手工(用户自发) | 自动 | 手工 | 自动(git commit) |
| 跨包同步版本? | N/A | N/A | 单一文件 | **lockstep 4 包同版本** |
| Rollback first-party? | ❌ | ❌(`codex update` 是 update 不是 rollback) | ❌ | ✅(`git revert` + `git tag`) |
| 信任发布? | N/A | npm + sha + 6 平台二进制 | N/A(plugin 更新) | **GitHub OIDC trusted publishing** |
| CHANGELOG 强制? | 否 | 否(无 CHANGELOG) | 否(事故命名代替) | **是**(`Breaking Changes` / `Added` / `Changed` / `Fixed` / `Removed` 5 段) |

#### 实证 OS 当前状态

**shipped(git 仓库)但 partial(没 release / CI / changelog)**:

- **git 仓库有**(remote: `https://github.com/yishu-ziyu/empirical-paper-workbench.git`)
- 最近 10 个 commit 都是 P7-BN ~ P7-BE 续接块(2026-05-28 ~ 2026-05-31)——这意味着有一个**长跑阶段**的 chunked commit 风格(**P7 反模式警示**:用户记忆里写"Codex 留下 50 条 Record 提交零业务改动,别复刻")
- 论文 9 个 section 是 working paper 草稿(`Manuscripts/sections/*.md`,不是 `.tex`)
- gitignore 极严格(`Data/Raw/*` / `Data/Interim/*` / `Data/Final/*` / `Submissions/*` / `Manuscripts/generated/*` / `state/runs/` / `state/product/` 都进 ignore)
- `Submissions/`:1 个 `paper_draft.docx` + CFPS PDF + 复现脚本
- ❌ 没有 `tag` / `release` / `CHANGELOG.md` / `VERSION`
- ❌ 没有 `.github/workflows/` CI 跑 8 个 integrity_audit test

#### 缺口 & 升级建议

**短期**:
1. **写 `CHANGELOG.md`**——把现有 P7-BN ~ P7-BE 续接块**改写成正经的 changelog 格式**(Added / Changed / Fixed 5 段)
2. **写 `.github/workflows/test-integrity.yml`**——每次 push 跑 `python3 -m pytest tests/test_integrity_audit.py`(8 个 BDD test)
3. **加 release tag**——`git tag v0.1.0` 标记"9 section 草稿完毕"这个 milestone

**长期**:
- 学 Pi Agent `scripts/release.mjs`——把"版本号 + CHANGELOG + git tag + 发布"做成 1 个脚本
- 学 OpenClaw 备份命名带**事故上下文**——`Manuscripts/sections/main-results.md.bak-2026-05-31-after-RobustRotation-rewrite`,不只是时间戳

---

## Part 3: 实证 OS 升级路线图(基于上述对比)

### A. 人设层(对应 A 任务)

**问题**:实证 OS 没有自己的 CLAUDE.md / SOUL.md,人设散落在用户级 + 项目级 AGENTS.md 复刻的 BDD/TDD。

**学谁**:
- 主学 Claude Code 哲学(规则先于灵魂)——实证 OS 是工程型 agent,不是陪伴型
- 不学 OpenClaw 散文 SOUL.md(那适合陪伴型,不适合学术 agent)
- Pi Agent 的"AGENTS.md 走 ancestor 链自动注入"做法值得学——但已经天然有了,只是**项目级还没写**

**3 个具体动作**:
1. 写项目级 `AGENTS.md` 的"灵魂段"——声明"我是实证 OS,我的核心使命是 XXX;我维护 evidence / claim / state / audit 四件套;我不维护 X / Y / Z"
2. 把用户级 CLAUDE.md 里的 12 行为规则、`独立判断原则`、中文渲染验证、第三方凭据安全,**挑真正适用于实证经济学研究的**(不是全部)下沉到项目级
3. 写一段"我维护什么 / 我不维护什么"——明示边界,避免 agent 自作主张

### B. 多 Agent 协调层(对应 B 任务)

**问题**:OS 有两套并存 agent 定义(9 identity + 7 researcher),orchestrator 9-stage 是 sequential 不是真子 agent,Claude Code Agent 工具没接到 orchestrator 派工上。

**学谁**:
- 主学 Codex `multi_agent`(`max_depth=2 / max_threads=6` + 每 sub-agent 独立 `model` + `model_reasoning_effort`)
- 学 Claude Code Agent tool 派发(YAML frontmatter)
- 不学 OpenClaw 4 agent(数量太多,实证 OS 用不到 4 个;2-3 个就够)
- 不学 Pi Agent(它故意没有 subagent,这不适用)

**3 个具体动作**:
1. **先对齐 7 + 9 套 agent 定义**——是删 `workflow_service.py` 的 7 个研究员?还是把 9 个 identity 折成 7 个?**先和用户对**
2. 写 `subagent_dispatch` 的 SKILL.md——声明"用 Claude Code Agent tool 派子 agent,每个 agent 跑哪个 stage,model 选什么"
3. 打开 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1`(如果用户允许)——这样能利用 Codex `multi_agent` 路由

### C. audit 推广(对应 C 任务)

**问题**:integrity_audit.py 是 6 维度硬门禁,但不自动跑,LLM 不知道它存在,GAP-008 没硬约束。

**学谁**:
- 主学 Codex `verifier.toml` 专用 sub-agent(verifier 自觉跑命令)+ Codex hook trust hash(SHA256)
- 学 Pi Agent 仓库级 pre-commit(不光是 lint,把 audit 也接进去)
- 不学 Claude Code 软约束(12 rules 是文字不是机制)——实证 OS 的 audit 已经是硬门禁,要把硬门禁做成"自动跑"

**3 个具体动作**:
1. **写项目级 `.claude/settings.json`**,把 `integrity_audit.py` 接到 PostToolUse(每次 Edit/Write 后自动跑 `--section` 当前文件),`exit code != 0` 时 block
2. **把 `integrity_audit.py` 包装成 SKILL.md**(`name: integrity-audit` / `description: "6 维度审计"`)
3. **`GAP-008` 加入 GAP_SCOPE**(`integrity_audit.py:498-506` 加一行)

### 三个"先别做"的反模式警示

1. **P7 gate-ceremony 反模式**——Codex 留下 50 条 Record 提交零业务改动,别复刻。每次 commit 都要有**业务可验证的改动**,不要为了"留痕"而 commit。
2. **过度多 agent 反模式**——OpenClaw 4 agent + Codex max_depth=2 + max_threads=6 = 24 个 worker,实证 OS 用不到。学 Codex 的"每 sub-agent 独立 model 路由"哲学(快慢分档)就够了,不要为多而多。
3. **配置文件仪式化反模式**——`openclaw.json.bak-20260513-desktop-shell-phase3` 那种"带事故上下文的备份命名"是工程师文化,不是 paper-writing agent 该学的。实证 OS 的备份就用时间戳,不要加 phase3 / schema-fix 这种修辞。

---

## Part 4: 决策点(给用户)

> 升级路线图 A/B/C 都不是"先做哪个后做哪个"的对立关系,以下是推荐优先级,但**先和用户对再做**。

### 短期(1 周内可完成)

| 任务 | 复杂度 | 立即价值 | 依赖 |
|---|---|---|---|
| 写项目级 `AGENTS.md` 灵魂段(A1+A2+A3) | 低 | 高(LLM 知道自己是实证 OS) | 用户定哲学 |
| 把 `integrity_audit.py` 包装成 SKILL.md(C2) | 中 | 高(LLM 主动调 audit) | SKILL.md 描述写作 |
| 写项目级 `.claude/settings.json` 接 audit 到 PostToolUse(C1) | 中 | 高(hard 门禁从软变硬) | C2 |

### 中期(2-4 周)

| 任务 | 复杂度 | 立即价值 | 依赖 |
|---|---|---|---|
| 对齐 7 + 9 套 agent 定义(B1) | 中 | 中(消除"两套并存"的混乱) | 用户定结构 |
| 写 `subagent_dispatch` SKILL.md(B2) | 中 | 中(打开多 agent 派工) | B1 |
| 把 `claim_register` / `evidence_bank` 暴露成 MCP server | 高 | 高(LLM 能查 evidence) | C2 |

### 长期(1+ 月)

| 任务 | 复杂度 | 立即价值 | 依赖 |
|---|---|---|---|
| 打开 Codex multi_agent 路由(B3) | 高 | 高(快慢模型分档) | B1+B2 |
| 学 Codex sandbox 3 档 | 高 | 中(数据安全) | 长期 |
| 学 OpenClaw 备份命名带事故上下文 | 低 | 低(锦上添花) | 长期 |
| 学 Pi Agent 拆 `packages/ai` | 高 | 中(独立 LLM 抽象层) | 长期 |

### 决策点(请用户选)

1. **A 任务哲学**:走 Claude Code 规则系,还是 OpenClaw 灵魂系?(影响 AGENTS.md 写作风格)
2. **B 任务结构**:9 identity 折成 7 个?还是 7 researcher 升到 9 个?(影响多 agent 派工)
3. **C 任务优先级**:先 SKILL.md(C2)还是先 hook(C1)?——C2 让 LLM 主动调,需要更多次交互才暴露价值;C1 直接 hard 门禁,价值立等可见

---

## 写在最后

这份解剖图不是"产品文档",是**决策参考**。每写一段,核心问题都是:**"实证 OS 在这个维度上要选哪边?"** ——不是"4 个都好",是"4 个里 X 适合 Y 场景,实证 OS 是 Y 场景所以选 X"。

读者可以这样用这份文档:
- 想加新维度时,先看这里有没有;没有就补一节
- 想改某维度时,先看这里"实证 OS 当前状态",确认要改的边界
- 想评审 4 个产品的某 feature 时,来这里找产品名 + 维度,直接读代码

后续 A/B/C 任务的具体执行计划基于本文档,**本文档不另造事实,所有引用的数字 / 文件名 / 行号都来自 5 个子 Agent 的盘点报告**。
