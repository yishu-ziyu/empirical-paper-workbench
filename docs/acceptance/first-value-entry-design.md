# 验收契约：阶段 C 第一轮展示与首次体验设计

Status: closed

## Change
在合并后的 main（c02eb05a12b99a435def10ba613eb99c5ac18201）上，以 review/first-value-entry 交付完整展示页设计及真人验证方案，供用户确认后再实施。

## Not this
仅首屏、拥挤长图、直接实施 GuidePage/DeskPage 或引擎、用假结果/用户反馈填充、把回放当现场运行、承诺移动端工作台、以 validator 代替真人理解效果。禁止新 Agent 框架、DiD、研究连续性实现、支付、增长后台、公开部署、联系用户或投放。

## Evaluator
implementer 产出设计文件；validator 独立复核证据与设计覆盖，主 agent 查看完整设计的桌面/移动端渲染。真人理解效果未测试，最终视觉与产品选择由用户确认。closed 仅表示本轮设计交付客观检查闭环，不表示页面实施或真人效果通过。

## Checks
- [x] C1 基线与范围：分支起点为指定 merge SHA；产品代码 diff 为空；PR #33 已按验收 HEAD squash；#30 有审阅/merge/死管道/业务反例记录且 CLOSED；独立 #34 根因待查。程序：`git merge-base HEAD origin/main; git diff c02eb05 -- frontend backend agent; gh pr view 33 --json headRefOid,mergeCommit,state; gh issue view 30 --json state,comments; gh issue view 34 --json body,state`。
- [x] C2 产品说明与每条对外能力对应清单条目、证据、适用范围；Card 真结果锚定明确会话/运行/设定，保留复现待核、降级及旧截图限制。程序：审阅 `docs/design/first-value-entry/README.md`、`evidence.md` 与其指向的原始资料，逐项核对，不以关键词出现替代语义复核。
- [x] C3 完整展示设计：价值与入口、真实案例（比较→设定→来源→边界）、能力限制与末尾入口均有；中英文分别完整；桌面和移动展示均可审阅；分屏/分节提供，非一张拥挤长图。程序：本地打开 `docs/design/first-value-entry/index.html`，分别走查 zh/en、1440×900/390×844，留分节截图和交互记录；语言切换不堆叠，移动端无工作台承诺。文件是设计审阅稿，不接 API。
- [x] C4 60–90 秒分镜按指定五段顺序，有画面/讲稿/来源/时段；预计算回放与现场执行明确区分，时长是编辑预算而非运行承诺。程序：审阅 `storyboard.md` 并核算时间合计。
- [x] C5 真人试用任务无前置操作教学；含比较两结果、找到一个来源、说出一条不可作的结论，记录卡点/误解/帮助；空白记录与评估规则、失败后处理、招募与执行审批边界明确。程序：审阅 `user-study.md`，确认没有伪造参与者或反馈；真人结果标未执行。
- [x] C6 交付完整可恢复：本地资源/链接可访问，设计审阅问题明确，验证报告记录通过/未测；runtime 与去敏运行记录更新，git diff --check 通过。程序：`git diff --check`，审阅任务状态与本轮产物清单，validator 输出 ACCEPT/REJECT。

## Evidence
C1：2026-09-08 合并前两次读取均确认 HEAD=0ee17abac7f6f6b72f868a4fdc27306b1adafb8e、base=main、5 项最新检查全部 SUCCESS；`gh pr merge 33 --squash --match-head-commit 0ee17abac7f6f6b72f868a4fdc27306b1adafb8e` 成功，merge=c02eb05a12b99a435def10ba613eb99c5ac18201。fetch origin main 后新建 review/first-value-entry，merge-base 为该 SHA。开始时原工作树 clean，无用户改动需要迁移。

- PR 收口：https://github.com/yishu-ziyu/empirical-paper-workbench/pull/33#issuecomment-5578705118
- #30 关闭记录：https://github.com/yishu-ziyu/empirical-paper-workbench/issues/30#issuecomment-5578705342；closedAt=2026-09-08T03:33:57Z。
- 独立 #34：https://github.com/yishu-ziyu/empirical-paper-workbench/issues/34，OPEN，根因待查。
- 回读留档：`assets/first-value-entry-design/github-state.json`；正文分别留在 github-closeout.md / card-flake-registration.md。
- 本次没有重跑 #33 研究实验，依据已获外部 ACCEPT 的同 SHA 证据收口。
- #33 原正文的 flake 段落同步更正为“根因待查”，REST 更新回读 `body_corrected=true`；没有改变已合并代码。GraphQL 两次 transient EOF 后改用 REST 完成，不影响已完成合并与关闭。

C2：README 产品说明、evidence 能力逐项映射、card-pair.json 同 run 的 OLS/IV 字段已与原始归档核对。原始来源的 hash、设定、公式、协方差与去敏说明均保留；清单的复现待核未被取消。最近 r3 的 mock 成文与归档簿记限制如实记录。

C3：主 agent 真实浏览器检查见 `assets/first-value-entry-design/browser-review.md`、render-matrix.json、interaction-checks.json 及分节截图。12 组合无横向溢出，来源/边界/末尾已滚动可见，整页与分节模式、单语切换、手机展示交接均检查。设计入口无 API，file 方式离线打开即可。

C4：storyboard.md 五段合计 16+18+17+16+13=80 秒，分别有中英文讲稿，顺序为比较→设定→来源→结论边界→桌面交接；明确编辑预算、历史回放、未来现场执行与失败保留。

C5：user-study.md 含三条无操作教学的任务、逐人空白记录、卡点/误解/帮助及独立完成区分；真人试用未执行，未招募或联系任何参与者。

C6：git diff --check 通过；设计文件 hash 留档 design-file-hashes.json；本任务 runtime 与去敏 raw 记录已建立，独立 validator 已出 ACCEPT：`first-value-entry-design-validator.md`，C1–C6 全通过。仅关闭设计交付客观检查；真人理解、视觉选择及页面实施仍待后续。

## Named relaxations
无。
