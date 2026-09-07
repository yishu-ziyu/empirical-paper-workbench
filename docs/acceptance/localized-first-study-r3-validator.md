# r3 validator 报告 — localized-first-study-r3.md

独立复核（与实现隔离）。工作目录 econpaper，分支 review/localized-first-study，范围 e2233d8..HEAD（06de502 / 1a2e902 / 411f9fc / ddc82f1）。
关键程序（C1/C2 前后端/C3、C5 全量）均由 validator 本人复跑，非转述 implementer 输出。

## 验收报告：localized-first-study-r3.md

- C1 Claim 状态映射完整诚实: PASS — 复跑 `cd frontend && npx vitest run src/lib/__tests__/i18nPresentation.test.ts src/components/__tests__/EvidenceLab.test.tsx` → `Test Files 2 passed (2) / Tests 26 passed (26)`。测试内容核实（非仅计数）：纯函数用例覆盖 supported→正向关联、insufficient→`证据不足…`且 `not.toMatch(/正向关联/)`、draft→`草稿`、approved→`已获批准`（注释明确 "Approval is a user action, not stronger evidence"）、undefined/`''`/`some_future_status`/null→`暂无法识别` 且禁止 正向关联/13%/局部因果回报/草稿；组件用例逐状态渲染真实 EvidenceLab→ClaimLedgerSection（`claim-explanation` testid，expect/forbid 双向断言），每例断言 `claim-original`（原文 details）在；英文用例切 en 后 insufficient→`Insufficient evidence` 且 not `positively associated`。源码核实：`CLAIM_STATUS_KEYS` 精确匹配六状态，未知/缺失落 `presentation.claim.card.unknown`，无默认 supported 分支（i18nPresentation.ts:279-296）。
- C2 Surprise 只消费后端判定: PASS — 复跑后端 `backend/.venv/bin/python -m pytest backend/tests -k "surprise or criterion_outcomes" -x -q` → `20 passed, 444 deselected in 3.64s`；复跑前端 4 文件 vitest → `4 passed (4) / 50 passed (50)`。源码核实：`displaySurpriseObserved(surprise, t)` 只遍历 `criterion_outcomes`，unresolved 跳过、无结构化 left.value 则不渲染（i18nPresentation.ts:245-270）；三个消费点 App.tsx:156 / AgentRail.tsx:230 / EvidenceLab.tsx:559 同源；`grep runCoef frontend/src` 零命中（旧 evaluator 已删）。后端 `_criterion_display_facts`（research_lab.py:800）只读、仅挂 resolved 项（:1010-1014，unresolved 保持纯 `{id,outcome}`）；`_resolve_criterion_ref`（:739）非 estimate.coef 一律 None（不伪造）、spec_id 精确匹配。Scene D（languageSwitchDisplayOnly:521）断言 zh→en 观察行重渲染且 restore GET / EventSource / research writes 计数不变。实弹 payload 与 /tmp/econpaper-r3/journey-log-final.json 归档逐字段一致（left iv/iv_region_dummies/run 3d4c6546…:iv_region_dummies/value 0.13150383625543327，right ols/0.074693…）。
- C3 判据标签完整携带阈值与对象: PASS — 复跑 `npx vitest run src/lib/__tests__/i18nPresentation.test.ts src/components/__tests__/ResearchLabPanels.test.tsx` → `2 passed (2) / 26 passed (26)`。源码核实：ordering+右常量 → `IV 估计 < 0.1` 式完整串（displayCriterionLabel:147-150）；`toleranceText`（:117-127）双空→rel=0.25→`±25%`（与后端 `_effective_tolerance` research_lab.py:795-796 同源），abs→`±0.02`、abs+rel→`±0.02 / ±5%`；无法友好展示的组回落 `可检验判定 · <原始label>` 不丢参数（:161-165）；`criterionSpecIdentities`（:174）+ 组件 `criterion-spec-ids` 提供左右 spec_id 可见身份；组件用例断言渲染 display-only（不触发 onSave、快照不变）。
- C4 非空 Results 真实旅程: PASS（附证据记录缺陷两项，见下）— 复核留档自洽性：journey-log-final.json（en 会话 5b4c3539）旅程顺序完整自洽：`POST /demos/card` 202 → upload READY → freeze 200 → spec run 202 → 12 真实 run（含 iv_region_dummies coef=0.13150383625543327、ols_region_dummies coef=0.07469325559311334，全 ok）→ claim 起草 supported/v1/stale=false/approved_by_user=false → 显式 approve 200（approved_by_user=true）→ prepare-paper 409 detail 四元组 `{"code":"canonical_mismatch","canonical_spec_id":null,"required_spec_id":"iv_region_dummies","promote_run_id":"3d4c6546-…:iv_region_dummies"}` → 显式 `POST preview/promote {"run_id": promote_run_id}` 200 → canonical_spec_id=iv_region_dummies → prepare-paper 200 → generate-chapter results len=166，内容含真实 `educ | 0.13150383625543327 | 0.05496367260228859 | 0.016792621884035075` —— 系数/se/p 可追溯到被 promote 的 iv_region_dummies run（runs 列表核对一致）；`GET /evidence` estimate_coef 同值、source_run_id=3d4c6546…（promote producer）。生成模式如实记录：`generation_source=mock, generation_degraded=true, review_source=mock, review_degraded=false`（契约 Named relaxations 已规定如实记录降级模式不算豁免）。uvicorn.log 证实第二遍完整旅程真实发生（会话 e6df83df-2652-48e5-bb96-8b057f1cde1c，行 77-888：approve 200→409→promote 200→prepare 200→generate 200→evidence 200）。无 DB 手工修改：journey.py 仅走公共 API；无自动 approve/promote 代码路径（`approved_by_user = True` 仅在显式 approve 服务函数 research_lab.py:1656；promote 仅显式路由 routers/research.py:296）。UI 组件测试核实：`C4 mismatch notice follows the interface language…`（zh 主提示/en 主提示/按钮 `把支撑设定设为主分析` / `Set the supporting specification as primary`，en 下 not 含中文）与 `mismatch after approve offers explicit promote…`（点击 promote 调 `onPromote('run-iv')`、write-results 调 prepare）均绿。
- C5 全量回归 + 报告: PASS — 复跑 `make test` 全绿：check-api-drift 三项 ✅；agent `819 passed, 1 skipped`；backend `456 passed, 8 skipped`；frontend `Test Files 58 passed (58) / Tests 431 passed (431)`。复跑 `npx tsc --noEmit`（零输出）、`npm run lint`（`Found 6 warnings and 0 errors`，6 条 react(only-export-components) 全在本次未改动文件：MethodSelector.tsx×2、agentCursor/context.tsx、i18n.tsx×2、paperMarkdown.tsx——与 e2233d8 基线一致性由"文件未变"保证）、`npm run build`（exit 0，`✓ built in 1.43s`）。skip 计数 `git grep '\.skip\|skipIf' -- frontend/src backend/tests` = 5 处，与 e2233d8 逐一相同（test_outline×2、postgres_upload_recovery、prewrite_supervisor、s3）。r1/r2 历史文档 diff 为空；本报告即 r3 validator 报告。

## 红线检查（Not this）

- canonical_mismatch 门禁未弱化: 通过 — `git diff e2233d8..HEAD -- backend/services/research_lab.py` 中含 promote/approve/canonical_mismatch/require_claim/409 的增删行为零条；`require_claim_ready_for_paper`（research_lab.py:1382-1410）完整保留 unapproved 409 / stale 409 / mismatch 409 三道，detail 带 code/canonical_spec_id/required_spec_id/promote_run_id；`prepare_card_paper_state` docstring "Never promotes" 且先过门禁。
- r1/r2 文档未动: 通过 — `git diff e2233d8..HEAD -- docs/acceptance/localized-first-study.md docs/acceptance/localized-first-study-r2-implementer.md docs/acceptance/localized-first-study-r2-validator.md` = 0 行。
- 无新增 skip: 通过 — 5 处与基线完全一致（见 C5）。
- 未夹带 DiD / Research Continuity: 通过 — 范围 diff 中 "did" 仅两处实质出现：test_card_spec_run.py 新测试用 `estimator:"did"` 作"未支持 metric 必须保持 unresolved"的反例探针（正是 C2 要求的方向），及契约文档文字；无任何 DiD 功能代码或 Research Continuity 改动。

## 诚实性细节

- a) `presentation.claim.card.approved` 文案: 通过 — zh `结论已获批准，以批准时点的证据版本为准（依据见下方运行记录）。` / en `Approved conclusion: it rests on the evidence version at approval time (see the run record below).` 只陈述"用户已批准 + 证据版本锚定"，无正向关联/因果强度断言（正向关联文案仅在 supported 词条）。组件测试 forbid `/正向关联/`。
- b) insufficient/unknown 无正向关联断言: 通过 — zh `证据不足：现有结果还不足以支持或否定教育与工资的关联。` / `结论状态暂无法识别：请以原始结论与下方证据记录为准。`；en `Insufficient evidence: current results neither support nor refute…` / `Claim status unavailable…`。纯函数与组件测试双向断言（含 `not.toContain('在当前证据下，教育与工资呈正向关联')`、`not.toMatch(/正向关联/)`）。
- c) displaySurpriseObserved 无自选 run/coef: 通过 — `grep -rn runCoef frontend/src` 零命中；函数体只读 criterion_outcomes 结构化字段。
- d) 判定语义测试期望未翻转: 通过 — `git diff e2233d8..HEAD -- backend/tests/` 仅 test_card_spec_run.py +183 行纯新增、0 行删除，既有后端测试一个字未动；前端 i18nPresentation.test.ts 删改的 7 行属旧 runCoef 行为用例被其**反向**断言替换（`expect(...).not.toMatch(/IV estimate/)`），即契约 C2 明令的行为变更所必需，非为过关弱化既有语义。

## C4 证据记录缺陷（不改变裁决，要求下轮修正契约 Evidence 文字）

1. **zh 会话 id 不可追溯**：契约 Evidence 写 "zh 会话 f53900e0-8e34-46cd-8925-a424ed8717b2"，该 id 在全部留档（journey-log-final.json、runner.log、uvicorn.log）中零出现。实际第二遍旅程会话为 **e6df83df-2652-48e5-bb96-8b057f1cde1c**（uvicorn.log 完整里程碑序列佐证旅程真实发生两遍）。
2. **"含两遍旅程"与归档不符**：journey-log-final.json 确为 15374 行，但 summaries 仅 1 条（label=en，session 5b4c3539），19 个 calls 全属该会话；zh 侧请求/响应留档被最终 en-only 运行覆盖（journey.py:204 的 argv 设计 + journey-log.json 与 final 逐字节相同）。
3. 附注：journey.py 的 label 参数不进入任何请求，API 层面的 "zh/en 各走一遍" 是名义标签；语言维度实际由组件测试与 Scene D 承担（Evidence 第 10 条已如实披露此替代方式）。

上述属证据簿记失准（写错会话 id、留档被覆盖后未更新描述），非实现缺陷、非门禁绕过、非伪造旅程（第二遍旅程在服务器日志中有完整独立佐证）。按"检查实质已由可验证留档证明"裁 PASS，但 Evidence 文字须在下轮修正，不得留错误会话 id 入库。

## 环境备注

- vitest 必须在 `econpaper/frontend` 下运行：从仓库根运行会丢失 jsdom 环境配置，报 `localStorage is not defined`（validator 首跑自误，复跑已按契约目录）。
- backend pytest 用 `backend/.venv/bin/python`（仓库根无 .venv），带 `--basetemp`（Makefile 注释要求的沙箱规避）。

## 结论

**ACCEPT** — C1–C5 五条检查程序经 validator 独立复跑全绿，红线四项全部守住，诚实性四细节全部核实；唯一问题是 C4 契约 Evidence 里 zh 会话 id 记错且"两遍留档"描述与实际归档不符（旅程本身经 uvicorn.log 证实真实跑了两遍），属证据文字失准，要求下轮修正后闭环，不构成 REJECT 根因。
