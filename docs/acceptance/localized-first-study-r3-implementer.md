# PR #32 r3 implementer 报告 — Claim 状态诚实化 / Surprise 消费后端事实 / 判据阈值完整 / 非空 Results 真实旅程

HEAD 开工：e2233d8cbb2789faea0baabd7c4214c474902a56（review/localized-first-study）
HEAD 收工：411f9fc（本报告提交前的最后实现提交）
契约：docs/acceptance/localized-first-study-r3.md（Checks 未改动，Evidence 已填，Status 保持 open）

## 改动清单

| 文件 | 说明 |
|---|---|
| backend/services/research_lab.py | 新增 `_resolve_criterion_ref`（value+run_id 一体解析）、`_effective_tolerance`（双空→rel=0.25，判定与展示共用）、`_criterion_display_facts`（resolved 判据的只读结构化展示事实）；`evaluate_surprise` 仅在 outcome≠unresolved 时挂这些字段 |
| backend/schemas/responses.py | `CriterionOutcomeResponse` 加 `extra=allow`，docstring 写明展示字段契约（unresolved 项保持纯 `{id, outcome}`） |
| backend/tests/test_card_spec_run.py | 新增 5 个结构化字段测试（含右常量、生效 tolerance、failed run 不入展示、部分 unresolved、非 estimate.coef 不伪造） |
| frontend/src/lib/i18nPresentation.ts | C1 `displayClaimExplanation` 完整状态映射；C2 `displaySurpriseObserved(surprise, t)` 只消费 criterion_outcomes、删除 `runCoef`；C3 `displayCriterionLabel` 携带右常量/abs/rel tolerance/原始条件兜底 + 新增 `criterionSpecIdentities` |
| frontend/src/lib/i18nWorkbench.ts | zh/en 新增 claim.insufficient / claim.draft / claim.approved / claim.unknown 词条 |
| frontend/src/App.tsx, components/AgentRail.tsx, components/EvidenceLab.tsx | 三处 surprise observed 消费点统一改为 `displaySurpriseObserved(research.surprise, t)` |
| frontend/src/components/ResearchLabPanels.tsx | 判据列表项渲染可见 `criterion-spec-ids` 标签（spec 身份可查） |
| frontend/openapi.json, docs/api/openapi.json, frontend/src/types/api.ts | `make gen-api` 再生成 |
| frontend 测试 ×5 | i18nPresentation.test.ts（C1/C2/C3 纯函数）、EvidenceLab.test.tsx（C1 组件 + C2 反例 + C4 mismatch zh/en）、ResearchLabPanels.test.tsx（C3 组件）、AgentRail.test.tsx（fixture 换结构化 outcomes）、languageSwitchDisplayOnly.test.tsx（Scene D：切语言无写入） |

提交（本地小步，未 push）：06de502 fix(backend)、1a2e902 fix(i18n)、411f9fc test(i18n)。

## 每条 Check 的结果

- **C1 done** — 程序 `npx vitest run src/lib/__tests__/i18nPresentation.test.ts src/components/__tests__/EvidenceLab.test.tsx` → 2 files / 26 tests 全绿。insufficient 绝不显示"在当前证据下，教育与工资呈正向关联"（组件 forbid 断言）；draft 显示草稿语义；missing/unknown 中性；approved 不显示更强结论；claim 原文 details 保留；zh/en 双语。
- **C2 done** — 后端 `-k "surprise or criterion_outcomes"` 20 passed（含 5 个新增）；前端 4 files / 50 tests 全绿。反例全覆盖：a) 正常对比显示后端指定 run 真实数值（实弹 payload 见契约 Evidence）；b) 非 estimate.coef metric 同 spec 有 coef run 也不显示（后端+前端测试）；c) 追加 status=failed 带 coef 的 run 展示不变；d) 部分 unresolved 不填充；e) 切语言零写入零请求（Scene D）。`runCoef` 已删。判定语义与估计器未动（既有 15 个 surprise 语义测试原样通过）。
- **C3 done** — 程序 2 files / 26 tests 全绿。`IV 估计 < 0.1` 不落 generic；`±5%`≠`±25%`；`±0.02 / ±5%` 分别格式化；双空显示后端默认 `±25%`（与 `_effective_tolerance` 同源）；同 estimator 不同 spec 由 `criterion-spec-ids` 可见标签区分；无法友好展示的组合保留原始条件（`可检验判定 · <label>`）；无写回（payload 保留测试全绿）。
- **C4 done** — 真实后端+runner（DEBUG=true, ECONPAPER_LLM=mock, 127.0.0.1:8010），zh/en 两个隔离会话各走完整旅程：boot→freeze→12 真实 run→claim 显式 approve→prepare-paper 409 canonical_mismatch（四元组 + claim version/stale/based_on_evidence_revision 已记录）→显式 preview/promote→prepare-paper 200→generate-chapter results 非空且含真实系数 0.13150383625543327（promote 的 IV run 的 coef/se/p）→evidence/snapshot 回跳可取。生成实际模式：**generation_source=mock / generation_degraded=true**（按运行配方 ECONPAPER_LLM=mock；results 表来自真实 canonical estimate，prose 为 mock 占位——`agent/nodes/generate_chapter.py` results 章节 = prose + state.results）。UI mismatch 多语言与显式 promote 按钮由组件测试断言（无浏览器，以 DOM 断言+API 留档替代截图）。完整请求/响应留档 /tmp/econpaper-r3/journey-log-final.json（重启后消失，摘录已固化进契约 Evidence）。
- **C5 done** — `make test` 全绿（drift 三项 ✅；agent 819 passed/1 skipped；backend 456 passed/8 skipped；frontend 431 passed）；`npx tsc --noEmit`、`npx tsc -b` 零错误；`npm run lint` 0 errors（6 条 warning 与 e2233d8 基线逐一相同）；`npm run build` ✓。skip 计数 5 与基线一致。r1/r2 文档未动。

## 遗留问题 / 备注

1. **mock 模式下的 results prose**：本机契约运行配方规定 ECONPAPER_LLM=mock，章节 prose 是占位串；接真模型后 prose 会由 LLM 生成，结果表路径不变。非阻塞。
2. **CriterionOutcomeResponse 的展示字段走 `extra=allow`**：曾尝试在 pydantic 模型上显式声明字段 + wrap serializer 丢弃 None，但 FastAPI 对深层嵌套模型的 clone 会把带自定义 serializer 的模型 schema 打成空 object（复现于 ResearchLabResponse 嵌套场景），故退回与 SurpriseResponse 一致的 extra=allow 模式；字段契约写在 docstring，前端用本地结构类型消费。若后续想要强类型 OpenAPI 描述，需先解决 FastAPI 该行为。
3. **/tmp 留档易失**：journey 完整 log 在 /tmp/econpaper-r3/，机器重启即失；载荷性内容（mismatch 四元组、results 章节、surprise payload）已摘录进契约 Evidence 与本报告。
4. **未 push**：三个本地提交待 orchestrator 收尾统一处理。
