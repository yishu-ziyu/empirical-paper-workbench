# FORMAL-CONFIRMATION-CHAIN-2 独立评审

评审开始于 2026-09-17，本机 2026-09-18 收尾。结论：**REJECT，需要在本批内修复后重审。**

本轮复核的是确认完整性，不用下一批“意图优先”的新界面要求否定本批。前一轮多项反例已被修复，桌面正常路径也已独立跑通；但“确认用户实际看到的那个版本”仍未闭合。

## 1. 对象和边界

- 目录：`/Users/mahaoxuan/Desktop/AI 产品/empirical-paper-workbench`。
- 分支：`feat/progressive-research-flow`；HEAD：`2d83c2c9c716c0708eb5303840e76f51749583d1`，未变。
- 开始写评审状态前，执行者 `final/changed-files-sha256.txt` **37/37 全部匹配**。阅读的是接手基线到当前交付的增量，以及关联的运行、快照和组件代码，不是只看 HEAD diff。
- 本轮不修改受评产品实现，不 commit/push/merge/rebase，不启动其他 Agent。只增加评审文档、任务状态和仓库外的独立测试工件。
- 本轮证据根目录：`../empirical-paper-workbench-evidence/formal-confirmation-chain-2/review/`。
- 测试使用独立临时数据库、合成 CSV、mock 模型；Python 进程使用干净环境和临时 HOME，并阻止非回环连接和读取环境/SSOT 文件。未使用真实模型或凭据。chain-1 的三个敏感副本未读取、未删除、未传播；本轮不扩大清理授权。

## 2. 已成立的修复

显式 mock 的角色覆盖和 reload 测试通过；新正式会话缺失设计的拒绝、无预览/逆序确认、旧跨会话响应、脏编辑确认、#40 三档许可已有对应回归通过。桌面页面中，正文和右侧“下一步”现在同时要求确认样本，不再一处说待确认、另一处说无待办。

本轮独立复跑：后端确认链/outline/design confirm **84 passed**；LLM router **22 passed**；前端确认命令、所有权、幂等和整页路径 **47 passed**。合计 153 项，不是再次跑完执行者的 1072/688/553 全套。

这些通过说明前次修复有效，但没有覆盖下列跨版本反例。

## 3. 剩余问题

### S1 / P1：确认记录绑定了服务端当下版本，没有验证用户所见版本

**实际反例：**模拟窗口 A 已看到预览 A，另一个窗口完成数据变更并生成预览 B。随后 A 发出当前前端实际使用的请求 `{"action":"record_confirms","table1Confirmed":true}`。API 返回 **200**，记录中的 `sample.preview` 等于 **B**，而非 A；`table1Confirmed=true`。

**代码：**`backend/services/formal_binding.py:330 record_confirms` 在接收时直接计算 `preview_identity(out)` 并授予批准；`backend/schemas/responses.py:PrewriteConfirmRequest` 没有用户所见的预览/数据/诊断版本；`workspace.ts:recordPrewriteConfirms` 只发送布尔意图。挂接确认也只有 session ID，没有确认目标数据版本。

前端 `confirmationCommands.ts:datasetSignatureOf/previewVersionOf` 又使用文件名、行数、列名、方程拼出另一套版本，未消费后端 `formal_chain` 的真实身份。两份内容不同但同名同形的数据不能靠这些元信息区分。

**最小修复：**让快照公开权威目标标识，确认请求携带用户所见的设计/数据/预览/诊断标识；在锁住 session 的同一事务中比对并写确认。版本不符返回冲突，不能替用户批准较新的对象。前端消费同一标识，不再自行估算数据版本。已有 snapshot 的 hash/version 字段能表达时优先接上，不另建平行状态系统。

**应先失败的测试：**A 预览→B 更新→A 确认；A 风险诊断→B 更新→A 风险确认；同名、同列、同行数但不同内容的文件替换；确认请求与数据替换并发。都不得批准未展示的新对象。

证据：`review/api_probes.py`、`review/api-probes.json` 的 `approve_unseen_preview`。这是隔离 API 的跨窗口时序模拟，不冒充浏览器完成了双窗口点击复现。

### S2 / P1：秒级时间戳不是可靠版本号，校验与锁定也没有原子化

**实际反例：**连续通过真实设计提出接口生成“教育与工资”（OLS）和“最低工资对就业的影响”（DiD），两份 `proposed_at` 相同。携带第一份的 `expectedRevision` 确认，返回 **200**，锁定的却是第二份设计。

**代码：**`agent/design/propose.py:_utc_now` 去掉微秒；`backend/routers/design.py:ConfirmDesignRequest/confirm_design_endpoint` 将 `expectedRevision` 定义成该时间戳，且可省略。校验 state 和 `facade.confirm_design` 是两个操作；执行者已注明的事务缺口仍然存在，不能把“已注明”当作已豁免。

**最小修复：**独立的不可重复 revision 或基于规范内容的版本标识；新正式会话确认必须带所见版本，旧兼容仅对明确 legacy 生效。版本比对与实际锁定使用同一事务/CAS。仅提高时间精度不能修复事务竞态。

**应先失败的测试：**同一秒两份不同草稿；缺失 expected revision；读取版本之后、提交确认之前另一窗口修改。只能锁定所见版本或返回冲突。

证据：`review/api-probes.json` 的 `design_revision_second_collision`，使用实际连续请求，未伪造时钟或调用模型。

### S3 / P1：执行内容对齐只覆盖四项，已批准的方法参数仍能被替换

**实际反例：**设计已确认 `method=rd, running_var=score, cutoff=0`；请求保留方法和 Y/X，却提交 `cutoff=20`。`/direction` 返回 **202**，入队 payload 的 cutoff 是 **20.0**。

**代码：**`backend/services/formal_binding.py:577 align_direction` 只校验 iv、dv、method、controls。该模块的设计指纹纳入了 cutoff、instruments、cluster、交互项等字段，但执行对齐没有消费同一个规范化投影。

**最小修复：**按当前方法将所有实际影响执行的字段规范化到已有设定结构，从批准版本派生执行参数，或对请求逐项核对；覆盖别名、零值、空值以及方法特有参数。不要为了这个修复另写一套估计器或放宽方法能力。

**应先失败的测试：**RD cutoff 0→20；IV 已批准工具 z1→z2；聚类/时间/个体列或交互项改变；等价别名不得被误拒绝。已有非 OLS 入口也须保持这个约束。

证据：`review/api-probes.json` 的 `approved_cutoff_not_enforced`，直接查询入队记录。

### S4 / P1：替换数据撤销了预览，却仍把旧估计展示成当前结果

**实际浏览器反例：**先在桌面完成真实估计，系数 **31.96311475409846**。随后从可见 Data 入口上传并确认 `replacement.csv`。侧栏已变为新数据，证据页仍直接展示旧系数 **31.9631**、“当前主张”和旧稳健性状态，没有旧版/失效标记。新文件相同设定下独立复算系数为 **94.96311475409836**；这里只要求标清旧结果，不要求上传后自动重算。

**代码：**`formal_binding.py:398 supersede` 的 `_PREVIEW_FIELDS` 清理预览与确认，未撤销/标旧 `estimate/results/robustness_results/identification_diag` 等依赖数据的当前产物；`supersede_dataset:430` 延续这些 live 字段。snapshot 和 EvidenceView 因而仍将它们作为当前结果消费。

**最小修复：**保留旧运行和工件，撤销受影响产物作为“当前结果”的资格，或投影明确的历史/待重算状态；数据/设计换版后，正文、侧栏、下一动作和证据必须一致。普通研究完整结论账本仍属后续任务，本项不要求提前实现它。

**应先失败的测试：**估计 A→替换并确认数据 B→查看 evidence；检查旧数字不再被标为当前且历史可查。覆盖改样本规则和设计执行字段；纯界面语言/排版不失效研究。

证据：`review/browser_replace.mjs`、`review/browser/replacement-report.json`、`review/browser/replaced-data-old-evidence.png`（本轮已读取图片）；另有独立 API 反例 `replaced_dataset_old_result_still_live`。

### S5 / P2：幂等键没有校验动作与输入，可能接回另一阶段的 run

**实际反例：**同一个 key 先请求 `/direction`，随后请求 `continue_estimate`。两次都返回 **202** 和同一 run ID，但 run 的 phase 是 **direction**，不是 estimate。第二次请求并没有取得它声称接受的那个动作。

**代码：**`backend/routers/outline.py` 两处提前调用 `find_run_by_key(session, "prewrite", key)` 后直接返回，没有比较 phase、规范化 payload 或确认目标。`formal_binding.py:request_replay/remember_request` 对同 key 不同确认 payload 也没有显式冲突规则。

**最小修复：**以 session+动作+目标版本+规范输入指纹定义意图；相同 key 同意图返回原回执，相同 key 不同意图返回明确冲突，不覆盖原请求台账。未知投递的重试继续使用原凭证。不要仅靠前端通常生成不同 UUID 证明 API 正确。

**应先失败的测试：**同 key 跨 phase、同 phase 改 payload/目标版本；相同请求在处理中和结束后重放；接受后丢响应再恢复。前端同名同形数据的凭证归属与 S1 一起修。

证据：`review/api-probes.json` 的 `idempotency_phase_collision`。这是 API 契约反例，未声称正常页面每次都会复用错 key。

## 4. 本轮浏览器与运行验证

Browser 插件未提供；使用本机已安装的 Playwright/Chrome。只启动隔离 backend `127.0.0.1:8483`、frontend `127.0.0.1:5323` 和 runner；数据库与文件在 `/tmp/fcc2-browser-review-rB2ljb/`。前端使用 `--mode review`，不加载日常 development 环境文件。

- **桌面 1440×900：通过本轮正常路径。** 从空桌可见入口提出/确认设计→上传/确认挂接→真实预览→确认样本/设定→真实估计→证据页→刷新恢复同一 session。主确认动作未用 API 预先替用户完成。
- **数值核对：**合成 60 行，系统 β=31.96311475409846、SE=0.15123105929246342；独立用原 CSV 和普通最小二乘公式复算 β=31.96311475409836、SE=0.15123105929246333、N=60。不是模型理解质量或真实研究数据验收。
- **小屏 320×568：确认操作走通，首次完整路径仍记录 FAIL。** 在真实估计处等待 90 秒超时；后续数据库显示同一 run 经四次领取（attempt=4）最终成功，总耗时约 201 秒。重新打开同一研究能恢复结果，恢复页无横向溢出。保留原 FAIL，不用后续成功覆盖它。
- **运行问题待定位：**本轮不能确定四次领取来自本批改动、继承的租约/进程恢复问题，还是隔离运行负载；不能据此宣布“小屏布局导致后端失败”。完整时序在 `browser/mobile-runtime-state.json`，应补执行器/租约证据，而非单纯加长浏览器超时。
- **键盘范围：**实际用 Enter 激活样本确认，但测试用 `focus()` 定位，不把它写成整条 Tab 顺序已验。VoiceOver 真人播报未验。
- **页面与控制台：**正常页面身份正确、非空、无框架错误遮罩；采集的 pageerror 为空。匿名模式 `/auth/me` 401 单列，不计作无网络错误。截图已实际读取：desktop-preview、replaced-data-old-evidence、mobile-failed、mobile-recovered-evidence。
- **执行代码溯源：**当前证据页仍显示 5/6，代码层为空。数值可复算与页面代码溯源不是同一验收项，本轮未把它写成完整通过，也未扩大成论文导出任务。

`make verify` 在上述隔离服务上通过。`npm run lint` 0 errors/6 条既有 Fast Refresh warning；`npm run build -- --mode review` 通过（仍有大 chunk 提示）。本轮没有安装依赖。

## 5. 测试证据索引与边界

| 工件 | 含义 |
|---|---|
| `review/existing-backend.log` | 独立 84 项后端测试通过 |
| `review/router-tests-config-isolated.log` | 独立 22 项角色配置测试通过 |
| `review/existing-frontend.log` | 独立 47 项前端测试通过 |
| `review/api-probes.json`、`api_probes.py` | 五个新增反例的 expected/actual 与可复跑脚本；脚本 exit 0 只表示采集完成，不表示反例通过 |
| `review/browser/report.json`、`browser_path.mjs` | 桌面通过、小屏首轮超时的原始记录及动作脚本 |
| `review/browser/replacement-report.json`、`browser_replace.mjs` | 真实换数据后旧结果仍为当前的浏览器复现 |
| `review/browser/mobile-runtime-state.json`、`mobile-recovered.json` | 小屏超时后的后台领取/终态与同会话恢复证据 |
| `review/make-verify.log`、`frontend-build.log` | 隔离健康/依赖检查和 review-mode 构建 |

初次给所有 router 测试强制注入全局 mock，导致 5 条本来验证显式非 mock 配置的测试失败。更正测试环境为干净临时 HOME、不预设全局 mock、阻断外部连接后 22/22 通过。原日志 `router-tests.log` 保留；这是评审启动条件冲突，不算产品回归，也未靠反复重跑挑绿。

## 6. 下一步执行边界

在本批修复 S1–S5，并定位小屏那次运行的重领时序；再独立复核。暂不进入 `INTENT-TO-DESIGN-1`，也不为解决这些正确性问题重设计全站。

优先收束一条规则：**请求携带所见目标，后端在同一事务核对目标并确认/入队，前端只消费后端权威身份。** 复用已有 formal_binding、snapshot 和确认命令模块；不要继续在 workspace 各分支复制版本猜测。当前 workspace 仍有 3100 行，局部模块的价值在于规则复用，而不是只把工具函数移到另一文件。

修复验收包含本报告反例、受影响回归、桌面真实路径，以及换数据后的状态一致性；小屏超时保留并解释，不能仅把 90 秒改成更长就算修复。完成后提供相对当前交付的增量与指纹，停止修改再交 review。

不授权 commit/push/merge/部署、不授权真实模型或进一步委派；敏感副本清理仍需用户明确范围。原实施报告保留，本评审作为独立结论追加。
