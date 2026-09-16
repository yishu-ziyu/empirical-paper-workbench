# econpaper Codex Task State

- Task ID: STRAY-GAP-CLOSURE-1
- Status: active
- Git context（分支可选）: `feat/fm-e-build-fold-real-fetch-1` @ `a274d56`。前置任务 STRAY-BRANCH-TRIAGE-1 已完成（validator ACCEPT），其判定见 `runtime/STATE.md` 的「游离分支三分类盘点」节。
- Goal: 把 2026-09-15 那批**未被集成顶端吸收**的 14 条缺口补齐到顶端，使每条都能由命令验证为「已在顶端可用」，且不回归已重做项。
- Hard bar: 每条缺口有可跑的行为证据（测试通过或命令输出），不以「文件存在」当完成；已判 `已重做` 的 6 条所代表的决定不得回退；不推远端；不把游离分支整条 merge 进来。
- Change 来源（用户 2026-09-16 决策）: 「这些都要」——14 条缺口全部补齐；`docs/data-completion-contract.md` 悬空引用按「补文件」处理（该合同在 `docs/fm-e-build-data-complete-1-g0` 上存在）；#24 的锁严格度沿用 `fix/ols-lock-twfe-phrasing` 已定的口径（模块 docstring 第 14 行：`There is intentionally no negation window. Any hit is a TWFE claim.`）。
- Session / run ID:
- Current research stage: 批次 A 开工中（依赖与文书类，加法为主）
- Current review / approval gate: 批次 A 契约 `docs/acceptance/stray-gap-closure-batch-a.md`
- Verified facts:
  - **环境已打通**：两个 venv 唯一缺的包是 `pywinsor2==0.4.3`，2026-09-16 已装入 `agent/.venv` 与 `backend/.venv`；`frontend/node_modules` 已 `npm install`。`pydantic_ai` 两个 venv 已有（此前为跑 `make test` 装的），因此**本机复现不出** #37 的降级，容器路径才是问题所在。
  - **可直搬产物（顶端完全没有、可整文件搬运）**：`agent/engine/ols_lock.py` + `agent/tests/test_ols_lock.py`（来自 `fix/ols-lock-twfe-phrasing`）；`agent/engine/outline_bodies.py` + `agent/tests/test_outline_bodies.py` + `frontend/src/lib/__tests__/outlineBodies.test.ts`（来自 `cursor/fm-e-build-b-six-chapter-bodies`）；`docs/data-completion-contract.md`（来自 `docs/fm-e-build-data-complete-1-g0`）；`docs/bryce-tools-contract.md`（来自 `feat/fm-e-build-bryce-g0`）；`docs/takeaway-math-research-notes.md`（来自 `fix/fm-e-takeaway-g0-contract`）；顶层 `eval/` 6 文件 + `docs/eval-top5.md`（来自 `feat/fm-e-build-eval-top5-1`）；`agent/tests/test_heterogeneity_interaction.py`（来自 `fix/fm-e-build-het-interaction-1`）；`agent/engine/prewrite_gates.py` / `prewrite_preview.py` / `docs/api/prewrite-confirm.md`（来自 `fix/fm-e-build-prewrite-pause-1`）；`feat/dc-fe-gate` 9 个前端新文件、`feat/dc-fe-step-attach-panel` 10 个前端新文件。
  - **必须内容级合并（两边都有、内容不同，不能整文件覆盖）**：`agent/prompts/{methods,results,conclusion}.py`、`agent/nodes/{generate_chapter,export_docx,translate_code,estimate}.py`、`agent/engine/{bind,estimate_agent}.py`、`agent/norms/loader.py`、`agent/design/{spec,propose}.py`、`backend/requirements.txt`。顶端已在这些文件里做了重切（TWFE 落在 `estimate.py:779/:910` 与 `design/spec.py:47`，OLS 标签落在 `design/spec.py:42`），覆盖会回退重切。
  - **两个聚合分支**（`cursor/fm-e-build-merge`、`feat/fm-e-build-data-complete-1`）本身无独立产物，由其组成部分的完成来覆盖。
- Current hypothesis: 缺口按写集可切成 7 批，批间文件不重叠或按序串联；加法批先做，能立刻产出可验证结果。
- 可运行性修复（2026-09-16，主 agent 直接完成，属一行级配置修复，非本批契约的实现内容）:
  搬家把本机可运行性打断了，逐项修复并验证：
  1. `Makefile` 顶部 `PYPATH` 未加引号 → 空格路径被 `/bin/sh` 截断，`make test` 第一步 `Error 127`。加引号。**证据：修复前 `/tmp/econpaper-baseline.log` 的 Error 127 原文；修复后 `make test` exit 0。**
  2. `dev-backend` 用裸 `uvicorn`、`install-*` 用裸 `pip` → venv 控制台脚本 shebang 指向搬家前路径（`~/Desktop/经济学论文/econpaper/...`），报 `bad interpreter`；而路径含空格时 shebang 本身无法修复。改为 `.venv/bin/python -m uvicorn` / `python -m pip`。
  3. `DEPENDENCY_ROOT` 默认 `../dependencies` → 搬家后 StatsPAI 在 `AI 产品/经济学论文/dependencies`，默认值指向不存在的路径。默认改为绝对路径 `$(CURDIR)/../经济学论文/dependencies`。
  4. `smoke-agent` 与 `verify` 末行未带 `$(PYPATH)` → 因 `agent/engine/did_spec.py:15` 与 `agent/norms/loader.py` 会 `from services.allow_did import ...`（后端包，由 9/15 的 `61733fd feat(did): hard-block missing treat×period` 引入），报 `ModuleNotFoundError: No module named 'services'`。两处补 `$(PYPATH)`。
  5. `ECONPAPER_DEPENDENCY_ROOT` **不可全局 export**：`agent/upstream.py` 的默认值设计就是「未配置时取 workspace/dependencies」，全局导出会改掉模块级 `DEPENDENCY_ROOT`，直接打挂 `agent/tests/test_upstream.py::test_default_dependency_root_is_workspace_dependencies`（实测 `1 failed, 969 passed, 1 skipped`）。改为只在 `verify-deps` 两条命令里临时传。**证据：`/tmp/econpaper-test-after-makefile.log` 的失败原文 vs 收窄后 `/tmp/econpaper-test-final.log` 的 `969 passed, 2 skipped`。**
  - 验证结果：`make test` exit 0（agent 969/2skip、backend 595/8skip、frontend 448/60files、check-api-drift 3 项）；`make verify` exit 0（含 frontend 200、backend health `{"status":"ok"}`、agent graph ok）—— **该目标是本仓库 `make verify` 在顶端首次真正跑通**（那批工作的运行记录写的是「`make verify` skipped (services down)」）。
  - 另：`eval/` 与 `frontend/node_modules` 已就位；两个 venv 补装 `pywinsor2==0.4.3`（唯一缺件）。
- 批次计划（每批一份契约，不写包住全部的巨型契约）:
  - **批 A｜依赖与文书（加法为主）** — C2 后端评审依赖（#37，含 Makefile/Dockerfile）、C11 EVAL-top5 台架、C12 data-completion 合同、C13 bryce 契约 + takeaway 笔记。契约：`docs/acceptance/stray-gap-closure-batch-a.md`
  - 批 B｜OLS 线 — C3 OLS 锁（#24）、C5 OLS 导出代码转换。碰 `prompts/`、`generate_chapter.py`、`translate_code.py`、`bind.py`
  - 批 C｜六章正文 — C4。碰 `export_docx.py`
  - 批 D｜前端 — C6 dataAttached 闸门、C7 挂接面板
  - 批 E｜闸门与推断 — C8 prewrite 闸门、C9 异质性推断。碰 `norms/loader.py`、`estimate_agent.py`
  - 批 F｜Word 公式排版 — C10。碰 `export_docx.py`（须排在批 C 之后）
  - 批 G｜全量回归 — C14 不回归已重做的 6 条 + `make test` 全绿
- Changed files:（本文件、`runtime/STATE.md` 登记行、批次 A 契约；实现改动见各批契约的 Changed files）
- Failed paths: 无产品失败。环境侧：`make verify` 需前后端服务在跑，本轮不以它替代静态与测试检查；Docker 守护进程未运行，容器侧检查本轮**无法执行**，将记为该检查的未跑项而非通过项。
- Data / output evidence locations: 各批契约的 Evidence 节；`make test` 输出按批留档
- Test evidence: 待批次 A 完成后记录；基线数字见下方「基线」条
- 基线: `make test` 于 2026-09-16 在顶端 `a274d56` 上**独立复现已全绿**（exit 0）：`check-api-drift` 3 项 ✅；agent **969 passed / 2 skipped**；backend **588 passed / 8 skipped**；frontend **448 passed / 60 files**。与那批工作自报数字完全一致，盘点报告里「未被本工作区独立复现」的欠账就此关闭。跑通前需先修 `Makefile:14` 的 `PYPATH` 引号（空格路径导致 `Error 127`，主 agent 已直接修复）。
- Pending external state: 用户对前端交互与公式排版的观感验收（批 D / 批 F 完成后）；顶端是否开 PR 未定
- Next action: 批 A 派 implementer；完成后 validator 复核，再进批 B
- Updated at: 2026-09-16

不得写入凭据、用户原始数据、未公开论文正文、私人对话或隐藏推理。
