# 验收契约：游离缺口补齐·批次 A（依赖与文书）

Status: open

Parent task: `runtime/tasks/20260916-stray-gap-closure.md`（STRAY-GAP-CLOSURE-1）
前置：`docs/acceptance/stray-branch-triage.md`（已闭环，validator ACCEPT）

## Change

把 4 类「顶端完全没有、且是整文件可直搬」的缺口补到 `feat/fm-e-build-fold-real-fetch-1` 上，
使后端运行时能真正走到类型化评审（不再静默降级）、顶层离线评估台架可用、两份被引用的合同文件不再悬空。
覆盖盘点名单里的 4 个分支：`cursor/backend-typed-review-dep-70ab`、`feat/fm-e-build-eval-top5-1`、
`docs/fm-e-build-data-complete-1-g0`、`feat/fm-e-build-bryce-g0`、`fix/fm-e-takeaway-g0-contract`。

## Not this

- **不整条 merge / cherry-pick 游离分支**，也不用游离分支的整文件去覆盖顶端已有文件。唯一例外是 `backend/requirements.txt`：只允许**追加**依赖行，不得改动或删除任何已有行。
- **不碰批 B–F 归属的文件**：`agent/prompts/*.py`、`agent/nodes/{generate_chapter,export_docx,translate_code,estimate}.py`、`agent/engine/{ols_lock,outline_bodies,bind,estimate_agent}.py`、`agent/norms/*`、`frontend/src/**`。本批只做加法与依赖声明。
- 不以「文件已存在」当完成：每条要有可跑的命令输出。
- 不改 `docs/acceptance/` 下既有记录；不改 STRAY-BRANCH-TRIAGE-1 的三份交付物。
- 不推远端。

## Evaluator

implementer 实现并自检；validator 按 C1–C6 独立复跑命令；本批无主观项，不需用户介入。

## Checks

### C1 测试基线（开工前 + 改后都必须绿）

程序：在顶端 `a274d56` 上跑 `make test`（目标：`check-api-drift` + `test-agent` + `test-backend` + `test-frontend`），记录四个分项数字。
预期：四项全绿。批 A 改完后重跑，仍全绿，且各分项通过数**不少于**开工前记录。

**前置修复（主 agent 已直接完成，非本批实现内容）**：`Makefile:14` 的 `PYPATH` 原为未加引号的 `PYTHONPATH=$(CURDIR):$(CURDIR)/backend`。工作区路径含空格（`AI 产品`），`/bin/sh` 在空格处截断并把 `产品/empirical-paper-workbench:/Users/mahaoxuan/Desktop/AI` 当命令执行，`make test` 第一步即 `Error 127`。已改为 `PYTHONPATH="$(CURDIR):$(CURDIR)/backend"`，并加注释说明缘由。证据：修复前 `/tmp/econpaper-baseline.log` 的 `Error 127` 原文，修复后同命令四项绿。

### C2 后端运行时能走到类型化评审（#37）

程序：三处安装路径都必须声明该依赖，且新增/扩展一条**守卫测试**把它钉住（本机 venv 早已装有该包，因此「装上没有」在本机无法证伪，只能靠声明一致性与守卫测试）：

1. `git grep -n "pydantic-ai-slim" backend/requirements.txt` → 有命中，且与 `agent/requirements.txt` 的 pin 一致（同为 `2.35.3`）。
2. `Makefile` 的 `install-backend` 目标会安装它。
3. `backend/Dockerfile` 的依赖安装层会安装它。
4. 守卫测试：在 `backend/tests/` 下新增用例，断言上述三处都声明了该 pin（任一缺失即失败），使「静默降级」不能靠漏声明复发。

预期：1–3 全部命中；4 的用例通过。`make test` 总分项数上升。

口径依据：顶端 `agent/nodes/review_chapter.py` 的 `build_review_agent` 惰性 `from pydantic_ai import Agent`，异常被兜成 `review_source="mock_fallback"` + `review_degraded=True`，所以缺依赖不报错、只降级。

### C3 顶层 EVAL-top5 台架可用且保持隔离

程序：从 `feat/fm-e-build-eval-top5-1` 搬入顶层 `eval/`（`harness.py`、`slots.json`、`pytest.ini`、`top5-set.submodule`、`tests/test_eval_top5.py`、`README.md`）与 `docs/eval-top5.md`。搬后执行：

1. `agent/.venv/bin/python -m pytest eval/tests -q` → 用例通过（数字记录）。
2. 隔离性：`git grep -n -E "from eval|import eval|eval\.harness" -- agent backend frontend` → **0 命中**，即产品运行时不得 import 它。
3. `eval/harness.py` 的「classic-5 目录 id 永不作 gold」拒绝规则（`FORBIDDEN_GOLD_IDS` / `refuse_catalog_gold`）在搬运后仍存在。

预期：3 项全过。注意：`eval/` 与顶端既有 `agent/eval/` 是两套东西，**不得合并或改名**（盘点 C3-2 已确认无文件重合）。

### C4 `docs/data-completion-contract.md` 落地，三处悬空引用成立

程序：从 `docs/fm-e-build-data-complete-1-g0` 搬入 `docs/data-completion-contract.md`，然后逐处复核引用它的一方所声称的内容在该文件里成立：

- `docs/find-data-lit-contract.md:8` 与 `:502`
- `docs/infer-design-contract.md:320` 与 `:478`
- `docs/real-fetch-contract.md:583`

预期：文件存在；上述 5 处引用处，每处把「引用原文」与「被引文件对应章节」成对贴出，逐处判定成立或不成立并给出结论。**若某处声称的内容在搬入文件里并不存在，必须如实报告该处仍不成立，不得改引用原文去迁就。**

### C5 `docs/bryce-tools-contract.md` 落地，「四件 IN」逐件可证

程序：从 `feat/fm-e-build-bryce-g0` 搬入 `docs/bryce-tools-contract.md`，并对契约声明的四件逐件在顶端给出实现证据（命令 + 命中位置），至少覆盖：FL 复用、CL winsor、NORMS 闸门、OLS 标签。
预期：文件存在；四件逐件有命中；无法在顶端找到实现的那件如实标为不成立。

### C6 takeaway 数学研究笔记落地，且其 BLOCKED 状态不被改写

程序：从 `fix/fm-e-takeaway-g0-contract` 搬入 `docs/takeaway-math-research-notes.md`。
预期：文件存在；其记录的「MATH-1 在真机 Word 里公式仍是转义 LaTeX」保持 **BLOCKED/OPEN** 原状，**不得**改写成已完成——批 F（C10 Word 公式排版）才是处理它的地方，本批只还原记录。

## Evidence

- 契约本文件；`make test` 修复前后两次的输出（含四分项数字）。
- C2：三处命中行 + 守卫测试用例名与运行结果。
- C3：`eval/tests` 通过数字 + 隔离性 grep 的 0 命中输出 + 拒绝规则存在证据。
- C4：5 处引用逐条对照结论。
- C5：四件逐件命中位置。
- C6：文件存在 + BLOCKED 原文保留。

## Named relaxations

1. **容器侧检查本轮不执行**：本机 Docker 守护进程未运行（`docker ps` 无法连接 `~/.docker/run/docker.sock`），故 C2 第 3 项（`backend/Dockerfile`）**只做静态声明检查，不构建镜像**。该未跑项不得写成通过；待 Docker 可用后补。
2. **`make verify` 不以替代品计入**：它需前后端服务在跑，本批不启动服务，故不执行、也不用于替代 C1。
