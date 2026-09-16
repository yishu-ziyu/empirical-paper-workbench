# 验收契约：游离分支三分类盘点

Status: accepted（2026-09-16 validator 独立复核 C1–C5 全 PASS；文本保留原样，计数勘误与复核意见见文末）

## Change

对 2026-09-15 那批工作中**不是集成顶端祖先的 20 个分支**逐个给出判定，三选一：
`已重做`（意图已落在顶端，只是换了实现）/ `真缺口`（意图不在顶端）/ `待定`（需要人拍板）。
每条判定必须附可在顶端树里复核的证据，结论写回 `runtime/STATE.md`。

要让"这批活干完了"这句话变成可核的事实，而不是靠分支名、提交数或"看着像"。

## Not this

- 不合并、不 rebase、不删除任何分支，不推远端。本轮只判定，不动手收拾。
- 不把分支名里的 `recut`/`merge`、也不把"顶端台账里有同名任务行"当成"已重做"的证据——必须指出顶端**实现同一意图的文件和符号**。
- 不跑 `make test`：本机两个 venv 的控制台脚本因路径带空格已失效，且顶端新增依赖未装，跑出来的失败不是产品结论。本轮不需要运行任何测试。
- 不改 `docs/acceptance/` 下已有的历史记录，不改任何 `runtime/tasks/2026*` 已有文件。

## Evaluator

implementer 在 `feat/fm-e-build-fold-real-fetch-1` 上只读侦察 + 写台账；validator 不看对话，只按本契约的检查程序独立复核命令输出并出 PASS/FAIL。`待定` 项的最终判定权在用户。

## 范围名单（20 个，必须逐条判定，不得留空）

```
cursor/backend-typed-review-dep-70ab
cursor/dc-be-suggest-classic-5
cursor/did-be-gate-8102
cursor/fm-e-build-b-six-chapter-bodies
cursor/fm-e-build-c-ols-export
cursor/fm-e-build-merge
docs/fm-e-build-data-complete-1-g0
feat/dc-fe-gate
feat/dc-fe-step-attach-panel
feat/fm-e-build-bryce-g0
feat/fm-e-build-classic-fixtures-1
feat/fm-e-build-data-complete-1
feat/fm-e-build-data-complete-1-dc-be-attach
feat/fm-e-build-did-narrow-1
feat/fm-e-build-eval-top5-1
fix/fm-e-build-het-interaction-1
fix/fm-e-build-math-1-docx-typesetting
fix/fm-e-build-prewrite-pause-1
fix/fm-e-takeaway-g0-contract
fix/ols-lock-twfe-phrasing
```

## Checks

### C1 名单可复现

程序：从 `origin` 取 9/9 及其之后的远端分支，逐个判 `git merge-base --is-ancestor <分支> origin/feat/fm-e-build-fold-real-fetch-1`，非祖先者即为名单。
预期：恰好上面 20 个，一个不多一个不少。
（2026-09-16 复核补充：9/09–9/14 之间 `origin` 上零分支，故 `>=2026-09-09` 与 `>=2026-09-15` 算出的集合完全相同，`9/9` 这个下界不影响结果；实际那批全为 9/15。）

### C2 每条判定带证据

程序：20 条判定逐条给出一行证据，形式为下面之一，且必须是**实际命令输出**（贴出命令与输出片段）：

- 判 `已重做` → 给出顶端里实现同一意图的文件路径 + 行号或符号名（`git grep -n <符号> origin/feat/fm-e-build-fold-real-fetch-1 -- <范围>`，或 `git rev-parse <顶端>:<路径>` 的 blob 哈希）。
- 判 `真缺口` → 给出该分支的产物路径，以及该路径在顶端不存在（`git cat-file -e <顶端>:<路径>` 非零退出）。
- 判 `待定` → 写明缺哪个判断依据，以及需要用户回答的具体问题。

预期：20/20 有条目；`已重做` 条目的证据里出现的是顶端的真实文件/符号，不是分支名。

### C3 三个已知疑点必须各有独立结论

不能合并成一条，不能省略：

1. `fix/ols-lock-twfe-phrasing` 针对 issue #24 的两个漏法——`不是……而是……` 否定跨度、以及 `加入州固定效应与年份固定效应` 这种不带"双向固定效应"字面的写法——顶端是否有等价实现。程序：在顶端树里查这两类处理，并给出该分支测试文件里的用例名单作对照。注意 GitHub issue #24 当前仍是 open 状态。
2. `feat/fm-e-build-eval-top5-1` 的顶层 `eval/`（`harness.py`/`slots.json`/`top5-set.submodule`/`tests/test_eval_top5.py`）与顶端 `agent/eval/`（`judge.py`/`personas.py`/`packets.py`/`run_task.py`）是不是同一件事。程序：分别列出两边的目录清单再比。
3. `cursor/backend-typed-review-dep-70ab`（PR #37）对 `backend/requirements.txt` 的改动，顶端是否已含。程序：打印顶端 `backend/requirements.txt` 里所有 pydantic 相关行。

### C4 台账写回

程序：检查以下三处存在且内容自洽：

- `runtime/STATE.md` 新增一节，列出 20 条判定（分支名 + 判定 + 证据指向）。
- `runtime/tasks/20260916-stray-branch-triage.md` 按 `runtime/tasks/TEMPLATE.md` 建好，字段不留空。
- `agent-learning/raw/2026-09-16_stray-branch-triage.md` 按 `agent-learning/raw/TEMPLATE.md` 建好。

预期：三处文件都存在，且 `runtime/STATE.md` 原有的 31 行任务索引一行未删、一行未改。（原文误记为 29 行，2026-09-16 按 validator 复核实测改正：`git show HEAD:runtime/STATE.md` 中以 `|` 开头 33 行，去表头/分隔后 31 条数据行。）

### C5 只读边界

程序：`git status --porcelain` 与 `git diff --stat`。
预期：改动只涉及 C4 的三个文件（如走独立提交，则为该提交的文件清单）；没有任何分支被删除，没有执行 `git push`，`origin/*` 引用未变。

## Evidence

- 判定表：并入 `runtime/STATE.md` 的新节（20 行）。
- 任务文件与运行记录：见 C4。
- 命令输出：随判定逐条内联在证据里，不另存大日志。

## Named relaxations

无。本轮不做任何合并与清理动作；判 `真缺口` 的分支保持现状等待用户决定。

## 复核后的勘误与说明（2026-09-16）

validator 独立复核结论 ACCEPT（C1–C5 全 PASS，6 条 `已重做` 与 14 条 `真缺口` 全部逐条复跑）。以下为复核报出的非载荷瑕疵及处理，原检查项一条未放宽、一条未删：

1. **C4 计数勘误**：原文写「原有的 29 行任务索引」，实测为 31 条数据行。已在 C4 内改正并注明出处。不影响 C4 判定（复核为「31 行全部按原序保留、modified/deleted = 0」）。
2. **C1 下界措辞**：`9/9` 在 `origin` 上无对应分支，与 `9/15` 等价。已在 C1 内注明，检查程序与预期集合未变。
3. **证据行的第二个计数错误**（在 `runtime/STATE.md` 判定表内，非本契约文本）：`feat/fm-e-build-classic-fixtures-1` 一行原写 `catalog.json` 分支 79 行，实测 103 行（顶端 133 行）。已改。该行判定 `已重做` 的依据是三个夹具文件 blob 完全相同，不受此计数影响。
4. **「意译当逐字引文」**：`runtime/STATE.md` C3-1 原把一句中译放在引号里呈现为分支源码原文；源码实为英文 `There is intentionally no negation window. Any hit is a TWFE claim.`。已替换为原文并注明系复核后更正。判定方向 `真缺口` 不变。
5. **C5 的变更路径枚举**：C5 原写「改动只涉及 C4 的三个文件」，实际还有本契约文件自身（派发方在开工前写成，属输入工件）。已在任务文件 `Changed files` 中补为 4 个。
6. **未覆盖的既成事实**：契约 `Not this` 只禁「合并 / rebase / 删除 / push」，未覆盖**本地指针 reset**。2026-09-16 开工前，本地 8 个旧分支已 reset 到各自 `origin` 同名分支（目的：消除历史重写造成的假分叉）。复核确认：7 个分支新旧 tree 完全相同；`main` 由 `452a8954` → `79c9c915` 为 23 个文件的纯新增（仅 `docs/local-runner.md` 含 +46/−12），旧 tip 已不可从任何 ref 到达（只存于 reflog），**内容层无损失**。该项已登记在任务文件 `Git context` 与其学习记录里，供后续会话知悉。

