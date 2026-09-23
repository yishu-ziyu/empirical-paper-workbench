# econpaper Codex Run Record

- Date: 2026-09-16
- Task ID / state file: STRAY-BRANCH-TRIAGE-1 / `runtime/tasks/20260916-stray-branch-triage.md`
- Commit / Git context: 只读侦察于 `feat/fm-e-build-fold-real-fetch-1` @ `a274d565f1062a8fc406b8ad002ca4d5ae421271`（= `origin/feat/fm-e-build-fold-real-fetch-1`）；`origin/main` = `79c9c915`。未合并 / 未 rebase / 未删除分支 / 未 push。
- Model and tool environment: zsh + `python3 - <<'PY'` 内联脚本（`subprocess.run` 调 git）+ `gh` CLI 只读查询；未启用任何子代理、未启动服务
- Dataset class / research method（不含原始数据）: 不适用。方法 = git 树考古：按分支与最近祖先 ref 的差集定「自己的产物」，再用 `git cat-file -e` 退出码 / `git grep -n` 符号 / blob 哈希在顶端树里复核同一意图
- Task: 判定 2026-09-15 那批里不是集成顶端祖先的 20 个分支，逐个给出 `已重做` / `真缺口` / `待定` 并附顶端可复核证据；三个已知疑点各出独立结论
- Result: pass（契约 C1–C5 全过；20/20 有条目，无 `待定`）
- Session / run ID: 单轮 implementer；无外部服务
- Verification commands:（10 组，逐条列在下面；全部只读）
  - 名单：`git for-each-ref --format='%(refname:short)|%(committerdate:short)' refs/remotes/origin` + 逐个 `git merge-base --is-ancestor <b> origin/feat/fm-e-build-fold-real-fetch-1`
  - 自己的产物：`git log --format='%h %s' <最近的9/15祖先ref>..<branch>` 与 `git diff --name-only <同ref> <branch>`
  - 产物存在性：`git cat-file -e <top>:<路径>`（看退出码，不看 stdout）
  - 符号与行号：`git grep -n <符号> <top> -- <路径>`、`git grep -nE '^def |^class '`、`git grep -l`
  - 内容一致性：`git rev-parse <branch>:<路径>` vs `git rev-parse <top>:<路径>`（blob 比较）
  - 清单对照：`git ls-tree -r --name-only <ref> -- <目录>`
  - GitHub（只读）：`gh issue view 24`、`gh pr view 37`、`gh pr list --state open`
  - 只读边界：`git status --porcelain`、`git diff --stat`
- Output evidence locations: `runtime/STATE.md` 新增「游离分支三分类盘点（STRAY-BRANCH-TRIAGE-1，2026-09-16）」一节（20 行判定表 + C3-1/2/3 + 遗留）；`runtime/tasks/20260916-stray-branch-triage.md`

## 成功动作

- 先用「最近祖先 ref 差集」把每个分支的**自己的产物**切出来，避免把整条 9/15 串行链的继承物重复记账：20 个分支里只有 2 个（`backend-typed-review-dep`、`b-six-chapter-bodies`、`c-ols-export`、`ols-lock-twfe-phrasing`）是从 `main` 起枝，其余都是从链上前一个 ref 起枝。
- 用 blob 相等当最强证据：`feat/fm-e-build-classic-fixtures-1` 的三个夹具文件（`fixtures/classic-5/SOURCE.txt` / `barro1991_growth.csv` / `ck1994_long.csv`）与顶端 `git rev-parse` 完全相同（`beb66616` / `e43e4f61` / `56b0cab3`），直接判「已重做」，不需要读内容。
- 用「同路径符号超集」判「已重做」：`backend/services/classic5_catalog.py`（分支 9 个符号 / 顶端 15 个，含 `rank_entries_for_design`）、`backend/services/data_attach.py`（顶端多 `attach_gate_fields`）、`agent/engine/did_spec.py`（顶端多 `did_spec_applies`）、`backend/tests/test_data_attach.py`（416 行 vs 354 行）。
- 用顶端自己的台账正文而不是分支名来定性「被重切」：顶端 `runtime/tasks/20260915-fm-e-build-did-gate-recut.md` 明写「Did not revive `cursor/did-be-gate-8102` @ `71be39f1`」，与顶端 `docs/contracts/did-narrow-exception-contract.md` 的 superseded 存根互相印证，支撑 `did-be-gate-8102` / `did-narrow-1` 判「已重做」（且说明其旧口径是被主动撤销，不是漏做）。
- 用「顶端合同引用了却不存在的文件」做真缺口的交叉证据：三份顶端合同把 `docs/contracts/data-completion-contract.md` 列为 sister contract，`git cat-file -e` 却 exit 128 —— 悬空引用，比单看路径不存在更有说服力。
- `gh` 只读查询把两个 GitHub 未闭合项坐实（#24 OPEN、#37 OPEN），让 C3-1 / C3-3 有仓库外的独立佐证。

## 失败动作与根因

- `gh issue view 24 --repo yishu-ziyu/econpaper` 失败（GraphQL: Could not resolve to a Repository）。根因：仓库名是我按上下文猜的，没先读 remote。改法：先 `git remote -v` 拿到 `yishu-ziyu/empirical-paper-workbench` 再查。
- `git log <b> --not A --not B ...` 把全部 refs 都当作包含项，输出 20 行无关提交。根因：git 的 `--not` 是「翻转其后所有 revision 前缀」的开关，第二个 `--not` 又把语义翻回来了。改法：改用 `^<ref>` 前缀逐个排除。
- 参照集只用 20 个非祖先分支时，`feat/fm-e-build-bryce-g0` 的差集被算成 72 个文件、32 个提交（把顶端已有的 `did-spec-recut-1` 整条链都算成它的）。根因：它的起枝点 `bf695715`（= `did-spec-recut-1` tip）不在那 20 个 ref 里，而在顶端的祖先集合里。改法：参照集扩到 9/15 全部 49 个 ref + 顶端 + main，bryce-g0 收敛为只加 `docs/contracts/bryce-tools-contract.md`。
- 其余为只读查询，无失败。

## 可复现条件

- 需能读 `origin/*` 全部引用（本地已有）；需 `gh` 已登录（本轮用它只读查 issue #24 / PR #37 / open PR 列表）。不联网也能复跑 C1–C5 的 git 部分，只有 C3-1 / C3-3 的 GitHub 状态行会缺。
- 无需装依赖、无需启动服务、无需跑测试：本轮所有判据都来自 git 树、blob 哈希、`git cat-file` 退出码、`git grep` 命中与 `gh` 只读 JSON。
- 复跑顺序：先 `git for-each-ref` 取 9/15 名单 → `merge-base --is-ancestor` 定 20 个 → 对每个分支取「最近 9/15 祖先 ref」→ 差集得自己的产物 → 对每个产物在顶端做 `cat-file -e` / `grep -n` / `rev-parse` 比较。

## 候选模式

- **「自己的产物」要用最近祖先差集来切，不能用 merge-base 对 main 的差集**。这批分支全部以 `origin/main` 为 merge-base，直接 `git diff main..branch` 会把整条串行链的继承物都算进每个分支，20 个分支里 15 个看起来「改了 30–70 个文件」，实际各自只加 1–2 个文件。
- **判「已重做」优先用 blob 相等或同路径符号超集，不用「看着像」**。前者一句话可复核（`git rev-parse` 两个哈希相同），后者能落到文件+符号+行号。
- **「顶端合同引用了却不存在的文件」是文档层缺口的强证据**，比单纯列缺失路径更容易被接受，因为它说明顶端自己承诺了该文件。
- **退出码优先于 stdout**：`git cat-file -e` / `git grep` 判存在与命中时只看返回码，`git rev-parse <rev>:<path>` 不存在时会向 stderr 报错而不是空 stdout。
