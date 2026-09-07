# 验收契约：PR #32 r3 — Claim 状态映射诚实化、Surprise 消费后端事实、判据阈值不丢失、非空 Results 真实旅程

Status: closed          # validator ACCEPT（r3-validator.md），Evidence 簿记勘误完成，核心画面已归档。

审阅 HEAD（开工时）：e2233d8cbb2789faea0baabd7c4214c474902a56（review/localized-first-study）

## Change

PR #32 的三处展示反例修复 + 一条真实完成旅程：Claim 解释不再把 insufficient/draft/未知状态默认渲染成"支持"；Surprise 观察值只消费后端 evaluate_surprise 的结构化判定（前端不再自选 run/coef）；判据标签完整携带运算对象、右侧常量与 abs/rel tolerance；在隔离会话中真实走完 Card 分析→批准→（mismatch 时显式 promote）→prepare-paper→生成非空 Results→证据回跳。

## Not this

- 不 merge、不进 Phase C、不夹带 issue #30 / DiD / Research Continuity、不重做视觉。
- 不删/弱化 canonical_mismatch 门禁；不自动 Promote 或自动 approve；不改数据库伪造完成；不手工注入正文充当生成证据。
- 不改 Claim 原文、版本、批准状态、统计结果；不写回判据；不改 spec_id/版本。
- 不改估计器；不改 Expected/Unexpected/Unevaluated/Inconclusive 判定语义；不增加研究写入。
- "Paper chrome 单语言"不替代完整旅程。旧截图不算当前画面。
- 不新增 skip；不为让检查过关重写既有测试期望。

## Evaluator

validator 子代理独立复核（只读代码 + 跑程序 + 对照本契约出 ACCEPT/REJECT）；最终返回用户（外部复核人）裁决。

## 侦察结论（实现前已核实的事实，implementer 直接采信）

- 后端 claim `evidence_status` 实际值集合：`supported`（draft payload，ols_coef>0）、`insufficient`（draft payload，ols_coef 缺失或 ≤0）、`draft`（force 重新起草后）、`approved`（approve 后）——见 `backend/services/research_lab.py:1465,1528,1580`；schema 默认 `draft`（`backend/schemas/responses.py:362`）。`conditional`/`unsupported` 当前仅作为展示 wording 分支存在于前端。
- 后端 `evaluate_surprise`（research_lab.py:883）已产出 status/criterion_outcomes/evaluated_criterion_ids/unresolved_criterion_ids；判定只扫 status∈{ok,degraded} 的 run；`_criterion_ref_value`（:742）只解析 `metric=="estimate.coef"`，spec_id 精确匹配、否则 estimator 匹配，取最后一个 completed run。
- 前端反例：`frontend/src/lib/i18nPresentation.ts` — `runCoef`(:148) 忽略 metric、不过滤 run.status、倒序取任何带数字 coef 的 run（含失败 run 残留）；`displayClaimExplanation`(:210) 只认 conditional/unsupported 其余默认 supported；`displayCriterionLabel`(:82) 忽略 tolerance、right 为数字常量时落到 generic。
- Surprise 消费点：`App.tsx:156`（决策栏）、`AgentRail.tsx:230`、`EvidenceLab.tsx:558-559`。判据标签消费点：`ResearchLabPanels.tsx:337`。
- canonical_mismatch：`require_claim_ready_for_paper`（research_lab.py:1304）在 claim.provenance.iv_spec_id ≠ canonical_spec_id 时 409，detail 带 code/canonical_spec_id/required_spec_id/promote_run_id；显式解除 = POST `/sessions/{id}/research/preview/promote`（routers/research.py:296）。
- 后端 criterion schema：kind∈{sign,ordering,distance}；right 为 MetricRef 或 float 常量；distance 有 tolerance{abs,rel}，两者皆空时后端默认 rel=0.25（research_lab.py:853-854）。

## Checks

- [ ] C1 Claim 状态映射完整诚实 — 程序: `cd econpaper/frontend && npx vitest run src/lib/__tests__/i18nPresentation.test.ts src/components/__tests__/EvidenceLab.test.tsx` — 预期: 全绿；对 supported/insufficient/draft/missing（字段缺失）/unknown（未来状态值）各有断言：insufficient 不含"在当前证据下，教育与工资呈正向关联"等正向关联文案；draft 显示草稿语义而非支持/不支持；missing/unknown 保守中性（不自动肯定或否定），不显示 supported 文案；approved 不显示比后端状态更强的结论；测试渲染真实 Claim 组件（ClaimLedgerSection / claim-explanation testid），不只测字典存在；zh 与 en 均覆盖；claim_text 原文仍可查看（details 原文保留）。
- [ ] C2 Surprise 只消费后端判定 — 程序: 后端 `cd econpaper && .venv/bin/python -m pytest backend/tests -k surprise -x -q`（或等价）+ 前端 vitest（i18nPresentation / AgentRail / EvidenceLab / App 相关） — 预期: 后端为 surprise 的 criterion_outcomes 项增加最小、只读、向后兼容的结构化展示字段（含 criterion_id、outcome、实际 metric/ref/run_id、resolved value、右侧对象或常量的 resolved 值；schema extra=allow 已有，新增需带单测）；前端 displaySurpriseObserved 及其三个消费点改为消费该结构化字段，删除前端自选 run/coef 的 evaluator 逻辑；反例回归：a) 正常对比仍显示后端指定 run 的真实数值；b) 未支持 metric（非 estimate.coef）即使同 spec_id 有带 coef 的 run 也不显示观察值（保持未解析）；c) 同 spec 后追加 status=failed 的 run（带残留 coef），展示不变（与后端解析一致）；d) 部分 unresolved 时未解析项明确保持未解析，不拿其它指标 coef 填充；e) 切换语言不产生新网络请求或研究写入（沿用 r2 的 display-only 断言方式）；Compare 的 why 解释不在本地化层另作研究判断。判定语义（Expected/Unexpected/Unevaluated/Inconclusive）与估计器不变。
- [ ] C3 判据标签完整携带阈值与对象 — 程序: `cd econpaper/frontend && npx vitest run src/lib/__tests__/i18nPresentation.test.ts src/components/__tests__/ResearchLabPanels.test.tsx` — 预期: 纯函数 + 真实组件回归，zh/en 双语：a) ordering + right=0.1 常量显示"IV < 0.1"式完整串（不落到"可检验判定"generic）；b) distance + tolerance.rel=0.05 与 0.25 产出可区分文案（±5% ≠ ±25%）；c) tolerance.abs 与 rel 分别正确格式化；d) 同 estimator 不同 spec_id 的引用有可查看的明确身份（如 spec 短标签/spec_id 可见）；e) 无法友好展示的组合保留原始条件/技术详情，不悄悄省略关键参数；f) 不写回判据对象、不改 spec_id/版本（现有判据快照不变）。
- [ ] C4 非空 Results 真实旅程（隔离会话，真实后端+前端） — 程序: `make dev` 起真实服务，隔离新会话（不污染现有会话数据），浏览器/API 实弹 — 预期: 运行真实 Card 分析 → 核对并显式批准当前结论（claim approve）→ 若 prepare-paper 返回 canonical_mismatch：mismatch 主提示按界面语言显示（技术码在详情可查），记录 detail（required_spec_id/canonical_spec_id/promote_run_id/claim version/stale/based_on_evidence_revision），显式调用/点击"把支撑设定设为主分析"（preview/promote）→ prepare-paper 200 → 通过现有生成路径产出非空 Results 章节（非空 = 章节内容含真实系数/表格，非模板占位空串）→ 正文/证据入口回跳到对应结论与证据；全程无数据库手工修改、无手工注入正文；zh 与 en 各走一遍（语言切换不触发新研究写入）；报告记录本次生成实际模式（模型/模板/降级路径，标注是哪一种）。若显式 Promote 后仍被阻塞：记录实际请求/响应四元组定位断点再最小修复，不得绕过门禁。
- [ ] C5 全量回归 + 报告 — 程序: `cd econpaper && make test && cd frontend && npx tsc --noEmit && npm run lint && npm run build`，API drift 检查按仓库现有程序，CI 用最新 HEAD — 预期: 全绿、无新增 skip（`git grep -n '\.skip\|skipIf' -- frontend/src backend/tests` 与开工前一致或更少）；r1 REJECT 与 r2 ACCEPT 历史文档不动，新增 r3 implementer/validator 报告；三个展示反例的修复前后对照（C1 insufficient、C2 伪观察值、C3 阈值丢失）有最新源码构建的画面或 DOM/网络断言证据，不用陈旧截图。

## Evidence

<implementer 填：每条检查的真实输出摘录 / 截图路径 / DOM 断言；validator 结论>

### C1 — Claim 状态映射完整诚实

程序 `cd econpaper/frontend && npx vitest run src/lib/__tests__/i18nPresentation.test.ts src/components/__tests__/EvidenceLab.test.tsx`：

```
 Test Files  2 passed (2)
 Tests       26 passed (26)
```

- 纯函数 `i18nPresentation.test.ts > C1 claim explanation maps the full backend status set honestly (zh + en)`：supported→正向关联；insufficient→`证据不足：现有结果还不足以支持或否定教育与工资的关联。` 且 `not.toContain('在当前证据下，教育与工资呈正向关联')`、`not.toMatch(/正向关联/)`；draft→`草稿` 且不含支持/不支持文案；approved→`已获批准`（不出现 `正向关联`，不比后端状态更强）；missing/`''`/`some_future_status`/null→`结论状态暂无法识别…`（不含 正向关联/13%/局部因果回报/草稿）；zh+en 均覆盖；非 card 教学案例返回 null。
- 真实组件 `EvidenceLab.test.tsx > C1 claim explanation renders honest wording per backend status in the real Claim component (zh)`：逐状态渲染 EvidenceLab→点击 `evidence-review-claim` 展开 ClaimLedgerSection，对 `claim-explanation` testid 断言 expectRe/forbidRe；`claim-original`（details 原文）每例都在。英文用例 `... in English too`（LangPills 切 en 后 insufficient 显示 `Insufficient evidence`，不显示 `positively associated`）。

### C2 — Surprise 只消费后端判定

后端 `backend/.venv/bin/python -m pytest backend/tests -k "surprise or criterion_outcomes" -x -q`：

```
20 passed, 444 deselected in 4.03s
```

前端 `npx vitest run src/lib/__tests__/i18nPresentation.test.ts src/components/__tests__/AgentRail.test.tsx src/components/__tests__/EvidenceLab.test.tsx src/__tests__/languageSwitchDisplayOnly.test.tsx`：

```
 Test Files  4 passed (4)
 Tests       50 passed (50)
```

- 后端新增（`backend/services/research_lab.py` `_criterion_display_facts`）：satisfied/violated 的 criterion_outcomes 项带只读结构化字段 `kind/operator/left/right/tolerance`，left/right 为 `{source: metric|constant, metric, estimator, spec_id, run_id, value}`（run_id 即判定实际读的那次 run），distance 的 tolerance 为实际生效值（双空→rel=0.25）。unresolved 项保持纯 `{id, outcome}`。`CriterionOutcomeResponse` 加 `extra=allow`；openapi/api.ts 已再生成，`make test` 的 check-api-drift 三项 ✅。
- 新增后端测试（test_card_spec_run.py）：`test_criterion_outcomes_carry_structured_resolution_facts`、`..._constant_right_and_effective_tolerance`（右常量 `{"source":"constant","value":0.1}`；双空 tolerance=`{abs:None, rel:0.25}`，显式 rel=0.05 原样）、`..._sign_has_no_right_and_failed_runs_do_not_feed_display`（同 spec 追加 status=failed 带 coef 的 run，展示 facts 仍指 ok run）、`..._partial_unresolved_keeps_plain_entry`、`..._unsupported_metric_never_fabricates_even_with_coef_runs`（非 estimate.coef metric 即使同 spec_id 有带 coef 的 run 也纯 unresolved）。
- 前端 `runCoef` evaluator 已删除（git 1a2e902）；`displaySurpriseObserved(surprise, t)` 只消费 criterion_outcomes；App.tsx / AgentRail.tsx / EvidenceLab.tsx 三处同一数据源。反例回归见 `i18nPresentation.test.ts`（unresolved 不填充、无结构化字段→null 不伪造、常量右、仅 sign）与 `EvidenceLab.test.tsx > C2 observed values render from backend outcomes only...`（Inconclusive 下仅显示已解析比较，ATT 项不出现）。切语言无新请求/写入：`languageSwitchDisplayOnly.test.tsx > Scene D`（zh→en→zh 观察行逐语言重渲染，restore GET / EventSource / research writes 计数不变）。
- 实弹 payload（真实后端，隔离会话 5b4c3539-abf6-423e-9186-8fc950bc2983）：

```json
{"id":"criterion.seed.iv-below-ols","outcome":"violated","kind":"ordering","operator":"lt",
 "left":{"source":"metric","metric":"estimate.coef","estimator":"iv","spec_id":"iv_region_dummies",
          "run_id":"3d4c6546-…:iv_region_dummies","value":0.13150383625543327},
 "right":{"source":"metric","metric":"estimate.coef","estimator":"ols","spec_id":"ols_region_dummies",
          "run_id":"3d4c6546-…:ols_region_dummies","value":0.07469325559311334}}
```

### C3 — 判据标签完整携带阈值与对象

程序 `npx vitest run src/lib/__tests__/i18nPresentation.test.ts src/components/__tests__/ResearchLabPanels.test.tsx`：

```
 Test Files  2 passed (2)
 Tests       26 passed (26)
```

- 纯函数（`i18nPresentation.test.ts > C3 criterion label carries constants, tolerance, and spec identity`）：a) ordering+右常量 → `IV 估计 < 0.1` / `IV estimate < 0.1`（非 generic）；b) `±5%` ≠ `±25%`；c) abs→`±0.02`，abs+rel→`±0.02 / ±5%`；双空→`±25%`（与后端 research_lab.py `_effective_tolerance` 默认一致）；distance+常量右 → `IV estimate ≈ 0.1 ±25%`；e) 无法友好展示（kind=ratio）→ `可检验判定 · IV/OLS ratio < 1.2`（保留原始条件），无 label 时 `可检验判定`；d) `criterionSpecIdentities` 返回左右 spec_id。
- 真实组件（ResearchLabPanels.test.tsx）：`C3 approx criterion label...`（ExpectationEditor 内 `IV 估计 ≈ OLS 估计 ±5%`，双空默认渲染 `±25%`）；`C3 ordering against a numeric constant...`（`IV 估计 < 0.1` 不落 generic）；`C3 same-estimator different-spec refs...`（`criterion-spec-ids` 可见 tag 同时显示 `iv_nearc4_full` 与 `iv_region_dummies`）；`C3 criteria block stays display-only`（渲染不触发 onSave、spec 快照不变——既有 payload 保留测试亦全绿）。zh/en 均覆盖（纯函数 en 用例 + 组件 zh）。

### C4 — 非空 Results 真实旅程（真实后端 + runner，ECONPAPER_LLM=mock，DEBUG=true，隔离新会话）

zh 与 en 各走一遍（两个独立新会话，无数据库手工修改、无手工注入正文；全程走公共 API）。en 会话 5b4c3539-abf6-423e-9186-8fc950bc2983；zh 会话 e6df83df-2652-48e5-bb96-8b057f1cde1c（勘误：初稿误记为 f53900e0-…，validator 独立核验 uvicorn.log 后更正）。两遍步骤一致：

1. `POST /demos/card`（Idempotency-Key）→202→runner 真实跑完 upload pipeline→`upload_readiness=READY`。
2. freeze specification-space →200；`POST .../specification-space/run` →202→12 个真实 OLS/IV run（如 iv_region_dummies coef=0.13150383625543327, ols_region_dummies coef=0.07469325559311334, status=ok）。
3. claim 自动起草：`evidence_status=supported, version=1, stale=false, based_on_evidence_revision=1, approved_by_user=false` → `POST .../claims/claim.card.education-earnings/approve` → `evidence_status=approved, approved_by_user=true`（显式批准，无自动 approve）。
4. `POST .../research/prepare-paper` → 409，detail 四元组：

```json
{"code":"canonical_mismatch",
 "message":"当前 Claim 依赖 IV specification，但正式主规格不是该 IV。",
 "canonical_spec_id":null,
 "required_spec_id":"iv_region_dummies",
 "promote_run_id":"3d4c6546-cadb-4b3a-a7b6-0bb101492f58:iv_region_dummies"}
```

   （claim version=1 / stale=false / based_on_evidence_revision=1 同步记录。门禁未删未弱化。）
5. 显式 `POST .../research/preview/promote {"run_id": promote_run_id}` →200，`canonical_spec_id=iv_region_dummies`。
6. 再 `prepare-paper` →200。
7. `POST /generate-chapter {"chapter":{"type":"results","title":"结果"}}` →200。章节内容（len=166）：

```
Placeholder chapter content from LLM

# 主结果

| 变量 | 系数 | SE | p |
|------|------|----|---|
| educ | 0.13150383625543327 | 0.05496367260228859 | 0.016792621884035075 |
```

   真实系数=被 promote 的 IV run 的 coef/se/p（`state.results` 由 canonical estimate 的 treatment_row 拼出，非空串占位）。
8. 回跳验证：`GET /evidence` → `available=true, estimate.coef=0.13150383625543327, estimate.source_run_id=<promote 的 producer run>`；`GET /sessions/{id}` → `results` 非空（len=128）。
9. **生成实际模式（如实标注）**：`generation_source="mock", generation_degraded=true, review_source="mock", review_degraded=false` —— 本机按运行配方用 `ECONPAPER_LLM=mock`，正文 prose 为 mock 占位，结果表为真实 canonical estimate 数字（generate_chapter.py: results 章节 = prose + state.results 表）。非降级模板路径之外的伪造。
10. UI 层断言（组件测试，代浏览器走查）：`EvidenceLab.test.tsx > C4 mismatch notice follows the interface language...`（mismatch 主提示 zh `当前结论依赖的设定，并不是现在的主分析。` / en `This claim depends on a specification that is not the current primary analysis.`；显式按钮 `把支撑设定设为主分析` / `Set the supporting specification as primary`）；`> mismatch after approve offers explicit promote and still allows write results`（promote 调用 `run-iv`、write-results 调 prepare）。切语言不触发研究写入：`languageSwitchDisplayOnly.test.tsx`（r2 断言方式，Scene D）。
11. 请求/响应留档（勘误，validator 指出后更正）：/tmp/econpaper-r3/journey-log-final.json 仅含 en 一遍的完整调用留档（每次调用的 status+response）——zh 遍的 JSON 留档被随后的 en-only 重跑覆盖；zh 遍真实发生由服务端 /tmp/econpaper-r3/uvicorn.log 的完整请求序列独立证实（validator 逐条核验，含 boot/freeze/approve/409/promote/200/generate/回跳）。
12. **补充实弹（validator ACCEPT 后，主 agent 收尾轮）**：`make dev` 标准配方（8000/5173，backend/.env 的真实 LLM 配置生效）再走一遍完整旅程（会话 07c446cc-6eb9-4c87-9fb1-d0df73fa8ad1），同一门禁序列：12 run → approve → prepare 409 canonical_mismatch（required_spec_id=iv_region_dummies）→ 显式 promote → prepare 200 → Results 章节。**本轮生成模式：`generation_source="llm", generation_degraded=false, review_source="llm", review_degraded=false`（真实模型，非 mock 非降级）**，Results 含 1750 字符真实中文 prose（基准回归/稳健性/异质性）+ 主结果表 educ coef=0.13150383625543327。故 C4 两种模式均已实测：implementer 轮 mock（prose 占位、结果表真实）+ 收尾轮真实 LLM（prose 与结果表均真实生成）。

### C5 — 全量回归 + 报告

```
$ cd econpaper && make test
[check-api-drift] ✅ openapi.json 与后端代码同步
[check-api-drift] ✅ docs/api/openapi.json 与后端代码同步
[check-api-drift] ✅ types/api.ts 与 openapi.json 同步
819 passed, 1 skipped, 4 warnings in 37.47s          # agent
456 passed, 8 skipped, 32 warnings in 125.59s        # backend
 Test Files  58 passed (58)
 Tests       431 passed (431)                        # frontend
[test] agent + backend + frontend 全部通过

$ cd frontend && npx tsc --noEmit && npx tsc -b   # 均无输出
$ npm run lint    # Found 6 warnings and 0 errors（6 条 react/only-export-components 与 e2233d8 基线逐一相同）
$ npm run build   # ✓ built in 1.78s
```

- 无新增 skip：`git grep -n '\.skip\|skipIf' -- frontend/src backend/tests` = 5 处，与 e2233d8 基线完全一致（test_outline×2、test_postgres_upload_recovery、test_prewrite_supervisor、test_s3，均原有）。
- r1/r2 历史文档未动；本文件为 r3 契约（开工前已存在，未改 Checks），新增 `docs/acceptance/localized-first-study-r3-implementer.md`。
- 三个展示反例修复前后对照（当前源码的 DOM/网络断言而非截图）：C1 insufficient（EvidenceLab 组件断言 forbid `正向关联`）；C2 伪观察值（Scene D + 后端 unsupported-metric/failed-run 测试 + 实弹 payload）；C3 阈值丢失（`±5%`≠`±25%`、`IV 估计 < 0.1`、默认 `±25%` 组件断言）。修复前行为由 git 历史承载（runCoef/displayClaimExplanation 旧实现见 e2233d8）。
- **最新构建核心画面（收尾轮实弹，dev server 5173 + 会话 07c446cc，sips 核对 1479×966 PNG）**：`docs/acceptance/shots/r3/` 四张——`zh-evidence.png`（C1 approved zh：`结论已获批准，以批准时点的证据版本为准…` + 原文查看；C2 zh：`观察到: IV 估计 0.1315 > OLS 估计 0.0747`）、`zh-question-criteria.png`（C3：判据标签 `IV 估计 < OLS 估计` + spec 身份 `iv_region_dummies · ols_region_dummies` + distance 选项 `IV ≈ OLS（±25%）`）、`zh-paper-results.png`（C4：非空 Results 正文含基准回归/稳健性 + 主结果表 0.1315… + 「查看研究结论与证据」入口）、`en-evidence.png`（C1/C2 en：`Approved conclusion…` / `Observed: IV estimate 0.1315 > OLS estimate 0.0747`，同一份后端事实）。证据回跳在实弹中点击验证：Results 章节入口 → 研究结论 claim-ledger。
- validator 独立复核：`docs/acceptance/localized-first-study-r3-validator.md` — C1–C5 全 PASS，红线全守，结论 **ACCEPT**（要求修正 Evidence 簿记两处失准，已按实更正：zh 会话 id、JSON 留档覆盖描述）。

## Named relaxations

无。（若 C4 生成路径为降级模式，如实记录模式即可，不算豁免。）
