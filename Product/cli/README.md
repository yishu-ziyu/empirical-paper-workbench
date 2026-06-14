# Codex CoPaper CLI v0.3 — gray-box, modular

> **TL;DR**: 6 subcommands, 1 demo, 跑通 7-agent loop 端到端。
> 实测 2026-06-14: `run-workbench --mode dry-run` 跑通 8 stage, **33 产物 / 344K** (vs sub-agent 跑的 CHARLS 28 产物 / 308K)。

## 快速开始

```bash
# 1. 一键 tour 最新一个 run (PM/新人入口)
python3 Product/cli.py demo

# 2. 列出所有 run
python3 Product/cli.py inspect --target runs

# 3. 整链路跑 (dry-run 是骨架, live 才会出真 LLM 内容)
python3 Product/cli.py run-workbench --project-root . --mode dry-run

# 4. 跑真的 (会烧 token, 5-10 min)
python3 Product/cli.py run-workbench --project-root . --mode live --user-goal "你的研究问题"
```

## 6 个子命令

| Subcommand | 干啥 | 用法 |
|---|---|---|
| `run-workbench` | 整链路 8 stage (00→08) 跑一遍 | `cli.py run-workbench --project-root . --mode live --user-goal "..."` |
| `auto-research` | 自动研究入口 (递归 topic → literature → data → method) | `cli.py auto-research --topic "..." --max-iterations 5` |
| `run-agent` | **单跑某 agent** + 灰盒 (a/e/v/r/s 5 选项) | `cli.py run-agent --project-root workspace/runs/X --agent execution` |
| `resume` | 从 last checkpoint 续跑 | `cli.py resume --project-root workspace/runs/X` |
| `inspect` | 列 run / agent / checkpoint / paper | `cli.py inspect --target paper --run run_charls_did_20260614_001` |
| `demo` | 一键 tour 最新 run (PM 友好) | `cli.py demo [--run RUN_ID]` |

## 灰盒 5 选项 (`run-agent` 内部)

每个 agent 跑完后弹:
```
[graybox] Stage 'execution' (agent: execution) finished.
  artifacts: 06_writing/paper_draft.md, ...
  [a]pprove  /  [e]dit ($EDITOR)  /  [v]iew (cat first file)  /  [r]eject  /  [s]kip
  >
```

| 按键 | 行为 | 写 checkpoint 状态 |
|---|---|---|
| `a` | 批准当前输出 | `approved` |
| `e` | 用 `$EDITOR` 打开产物文件, 改完回主菜单 | `modified` |
| `v` | `cat` 第 1 个产物前 50 行, **不退出**灰盒 | (不写) |
| `r` | 拒绝, 整个 run 标 fail | `rejected` |
| `s` | 跳过审阅, 继续下个 agent | `modified` (软跳过) |

`$EDITOR` 默认 `vim`, 可改 `export EDITOR=nano`。

## 8-segment 目录约定 (跟 workbench 一致)

```
workspace/runs/<run_id>/
├── 00_intake/      ← Supervisor 产物
├── 01_sources/     ← Data 产物
├── 02_literature/  ← Literature 产物
├── 03_strategy/    ← Design 产物
├── 04_modeling/    ← Execution 产物
├── 05_results/     ← Manuscript results index
├── 06_writing/     ← Manuscript draft (paper_draft.md)
├── 07_review/      ← Verifier 产物
└── 08_final/       ← Manuscript final (paper_draft.tex)
```

## Walk-through example (用本次 CHARLS run)

```bash
# 1. 看历史
python3 Product/cli.py inspect --target runs
# → 列出 13 个 run, 包括我们今天做的 run_charls_did_20260614_001

# 2. tour 它
python3 Product/cli.py demo --run run_charls_did_20260614_001
# → 13 run 摘要 / 9 agent segment / paper_draft.md 前 25 行 / 4 next steps

# 3. 看 paper
python3 Product/cli.py inspect --target paper --run run_charls_did_20260614_001
# → 15,968 chars / 335 lines / 前 30 + 后 10 行

# 4. 重跑某个 agent (灰盒会弹)
python3 Product/cli.py run-agent \
  --project-root workspace/runs/run_charls_did_20260614_001 \
  --agent execution
# → 调 orchestrator._run_stage(execution) → 弹 5 选项 prompt → 写 checkpoint
```

## CLI vs Web 选型

| 场景 | 用 CLI | 用 Web (`web-react/`) |
|---|---|---|
| **CI/CD / 批处理** | ✅ 一行命令 | ✗ 需起前端 |
| **服务器 / SSH 远程** | ✅ 无浏览器 | ✗ 需 X11/端口转发 |
| **demo 给新人** | △ 看 `demo` 输出 (纯文本) | ✅ 实时看 8 stage 进度条 |
| **改 prompt / 看 raw LLM 流** | ✅ `--mode live` 一切尽在 stdout | △ 通过 web console |
| **单 agent 重跑 + 灰盒** | ✅ `run-agent` 5 选项 prompt | ✅ web L5 execute tab |
| **大批 run 批量巡检** | ✅ `inspect --target runs` 1 行 | △ 一个一个点 |

**默认**: 开发 / 批处理用 CLI; 给 PM / 老师 / 投资人 demo 用 Web。

## 已知限制

- `run-agent` 当前调 `orchestrator._run_stage()` 是 **blocking** — 跑长任务不 progress 心跳, 只能等 P2 加 polling
- `inspect` 不递归, 只能看 8 segment 一层
- `resume` 只检查 `.checkpoints/state.json` 存在, 不解析 `run_workbench()` 内部 status
- `demo` 不会自动 run `last` — 只看文件系统排序

## 内部架构

```
Product/cli.py (薄壳, 12 行)
└── Product/cli/ (7 个文件, 234 行)
    ├── __init__.py     文档
    ├── _common.py      AGENT_ROLES, helpers, save_checkpoint
    ├── graybox.py      run-agent + 5 选项 prompt
    ├── inspect_mod.py  inspect (4 target)
    ├── resume.py       resume
    ├── demo.py         demo
    └── __main__.py     argparse + main
```

复用 workbench backend (不重写):
- `Product.backend.orchestrator.run_workbench()` — 8 stage 主入口
- `Product.backend.orchestrator._run_stage()` — 单 stage 入口
- `Product.backend.orchestrator.Checkpoint` + `load_checkpoints` / `save_checkpoint` — 灰盒状态

## 版本

- **v0.1** (历史): `run-workbench` + `auto-research` 2 命令
- **v0.2** (今日): 加 `run-agent` + `resume` + `inspect` 3 命令 + 灰盒 a/e/v/r/s
- **v0.3** (今日): 拆模块 (`cli/` 包) + P1 (修 inspect ts) + P2 (progress timing) + P3 (`demo`)

## 验证记录

- 2026-06-14 — v0.3 上线
  - `dry-run` 跑通 8 stage, 33 产物 / 344K (vs sub-agent 跑的 CHARLS 28 产物 / 308K)
  - P0-P3 全完成 (拆模块 / 修 ts / progress / demo)
  - `live` 模式实测中, 待补结果 → 见下方 "live 验证结果" 节 (待 A 跑完补)

---

**provenance**:
- produced_by: main_agent (claude opus 4.6)
- evidence_level: local_file (实测, 跑过)
- status: draft
- created_at: 2026-06-14T04:00:00Z
- run_id: cli_v0.3_readme

---

## live 验证结果（2026-06-14 跑通, 但有 caveat）

✅ **end-to-end orchestration 跑通**: `run-workbench --mode live` 8 stage 全 completed, 33 产物 / 828K, paper_draft.md 5106 行 / 485K, modeling_report.json 71K, review loop `revise_minor` 完成。

⚠️ **topic caveat**: 我传了 `--user-goal "CHARLS 城乡居民基本医疗保险整合..."`, 但 orchestrator 用的是 `state/project_state.json` 里**陈旧**的 project_profile (上一轮的 robot/wage 项目), 没读 CLI 的 user_goal。

| 指标 | 实测值 | StatsPAI benchmark | 评估 |
|---|---|---|---|
| 8 stage 全完成 | ✅ | n/a | OK |
| 产物数 | 33 files / 828K | 12 scripts / 6 tables / 7 figures / 14-page paper | OK (结构等价, 形式不同) |
| paper_draft.md | 5106 行 / 485K | ~1000 行 / 25K (14 页) | paper 长度超额完成, 但**内容 topic 不对** |
| M5 系数 | 不存在 (paper 是 robot/wage, 不是 CHARLS DiD) | +0.081 (CHARLS) | ❌ 验证失败, 跑错 topic |
| Topic | 工业机器人 / 劳动收入 (CFPS) | 城乡居民医保整合 (CHARLS) | ❌ topic 错位 |

**根因**: orchestrator 把 `state/project_state.json` 当作 source of truth, `--user-goal` 只写进 `00_intake/user_goal.md` 但 agent prompt 读的是 project_profile。要修两个地方:

1. **P0 fix**: 跑 live 前先 `state/project_state.json` 切到 CHARLS (或任何目标 topic), 或者
2. **P0 fix**: orchestrator 让 `--user-goal` override project_profile.research_question (推荐, 才是 CLI 正确语义)

下次 live run 之前必须先修这个, 否则跑出来什么 topic 完全看 `state/project_state.json` 上次的状态。
