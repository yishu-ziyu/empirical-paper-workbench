# Todo

## 2026-05-28 P7-A Dataset Motherlode Index

- [x] 节点目标：把用户本地公开实证数据库母库接入 Empirical Research OS 的 DataAgent 起点，形成只读、可搜索、可人工审阅的数据源 manifest。
- [x] BDD/TDD：新增 `tests/test_dataset_motherlode_index.py`，覆盖只读数据源登记、数据族 metadata 扫描、工业机器人/劳动力题目匹配、嵌套路径关键词提示、隐藏系统文件过滤、JSON/Markdown 输出。
- [x] 实现范围：新增 `Program/workbench/dataset_motherlode_index.py` 和 `Program/dataset_motherlode_index.py`；新增计划 `docs/superpowers/plans/2026-05-28-dataset-motherlode-index.md`。
- [x] 真实运行：`python3 Program/dataset_motherlode_index.py --project-root . --data-root "/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库" --topic "工业机器人对劳动力市场匹配效率的影响"` 写出 `Results/json/dataset_motherlode_index.json` 与 `Reviews/dataset_motherlode_index.md`。
- [x] 真实输出：状态为 `needs_human_dataset_index_review`；候选首位为 `外部源数据`，匹配理由包括 `ifr`、`robot`、`工业机器人`、`机器人`；同时返回 CLDS、CFPS、CGSS、CMDS 等候选数据族。
- [x] 正式层边界：本节点不修改原始数据、不写正式 manuscript、不写正式 bibliography、不写 RunPlan、不写 `state/product/*`。
- [x] 验证：`python3 -m unittest tests.test_dataset_motherlode_index -v` 通过 6 项；`python3 -m py_compile Program/dataset_motherlode_index.py Program/workbench/dataset_motherlode_index.py tests/test_dataset_motherlode_index.py` 通过；scoped `git diff --check` 通过。
- [x] 下一步 P7-B：已进入 Literature Discovery / Project Bibliography seed。

## 2026-05-28 P7-B Literature Discovery / Project Bibliography Seed

- [x] 节点目标：把“参考文献从哪里来”产品化为 LiteratureAgent 种子层：查询计划、来源注册表、候选检索记录、project bibliography 状态链和人工审阅包。
- [x] BDD/TDD：新增 `tests/test_literature_discovery_seed.py`，覆盖中英文查询扩展、Dataset Motherlode Index 上下文注入、来源注册表、候选记录 claim 门禁、JSON/Markdown 输出。
- [x] 实现范围：新增 `Program/workbench/literature_discovery_seed.py` 和 `Program/literature_discovery_seed.py`；新增计划 `docs/superpowers/plans/2026-05-28-literature-discovery-bibliography-seed.md`。
- [x] 真实运行：`python3 Program/literature_discovery_seed.py --project-root . --topic "工业机器人对劳动力市场匹配效率的影响" --dataset-index Results/json/dataset_motherlode_index.json` 写出 `Results/json/literature_discovery_seed.json` 与 `Reviews/literature_discovery_seed.md`。
- [x] 真实输出：状态为 `needs_human_literature_discovery_review`；生成 13 条查询、8 类来源入口、13 条候选检索记录；包含 IFR、CLDS、CFPS、CMDS、CGSS 等数据上下文查询。
- [x] 正式层边界：本节点不执行网络检索、不下载全文、不写正式 bibliography、不写正式 manuscript、不写 project bibliography、不写 `state/product/*`。
- [x] 验证：`python3 -m unittest tests.test_literature_discovery_seed -v` 通过 5 项；`python3 -m py_compile Program/literature_discovery_seed.py Program/workbench/literature_discovery_seed.py tests/test_literature_discovery_seed.py` 通过；scoped `git diff --check` 通过。
- [x] 下一步 P7-C：已实现 Level 3 Manuscript Quality Gate。

## 2026-05-28 P7-C Level 3 Manuscript Quality Gate

- [x] 节点目标：把 Auto Mode 是否交付 Level 3 可人工审阅论文包转成可执行门禁，覆盖结构、长度、候选引用标记、paper package 信任层和正式层边界。
- [x] BDD/TDD：新增 `tests/test_level3_manuscript_quality_gate.py`，覆盖完整论文通过结构/长度最低门、不完整论文阻断、候选引用必须标记待人工核验、manifest 区分真实运行/草稿层/人工审阅、JSON/Markdown 输出。
- [x] 实现范围：新增 `Program/workbench/level3_manuscript_quality_gate.py` 和 `Program/level3_manuscript_quality_gate.py`；新增计划 `docs/superpowers/plans/2026-05-28-level3-manuscript-quality-gate.md`。
- [x] 真实运行：`python3 Program/level3_manuscript_quality_gate.py --project-root . --paper workspace/paper_packages/cgss_social_capital_happiness/paper.md --package-manifest workspace/paper_packages/cgss_social_capital_happiness/manifest.json` 写出 `Results/json/level3_manuscript_quality_gate.json` 与 `Reviews/level3_manuscript_quality_gate.md`。
- [x] 真实输出：状态为 `needs_human_level3_quality_review`；`gate_status=red`；当前 CGSS 包结构完整、长度达标，但参考文献候选条目未逐条标记“候选/待人工核验”，需要 `mark_candidate_references_for_human_review`。
- [x] 正式层边界：本节点只生成质量门禁 JSON 和审阅报告，不改写论文、不改写正式 bibliography、不改写 project bibliography、不写 `state/product/*`。
- [x] 验证：`python3 -m unittest tests.test_level3_manuscript_quality_gate -v` 通过 5 项；`python3 -m py_compile Program/level3_manuscript_quality_gate.py Program/workbench/level3_manuscript_quality_gate.py tests/test_level3_manuscript_quality_gate.py` 通过；scoped `git diff --check` 通过。
- [x] 下一步 P7-D：已串成首版 Auto Mode acceptance chain。

## 2026-05-28 P7-D Auto Mode Acceptance Chain

- [x] 节点目标：把 P7-A 数据母库索引、P7-B 文献发现 seed、P7-C Level 3 质量门串成一个 Auto Mode package readiness 和 repair queue 入口。
- [x] BDD/TDD：新增 `tests/test_auto_mode_acceptance_chain.py`，覆盖 red Level 3 gate 生成修复队列、yellow ready gate 进入 `needs_human_final_review`、组件状态聚合、信任层聚合、缺失输入阻断、JSON/Markdown 输出。
- [x] 实现范围：新增 `Program/workbench/auto_mode_acceptance_chain.py` 和 `Program/auto_mode_acceptance_chain.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-acceptance-chain.md`。
- [x] 真实运行：`python3 Program/auto_mode_acceptance_chain.py --project-root . --dataset-index Results/json/dataset_motherlode_index.json --literature-seed Results/json/literature_discovery_seed.json --level3-gate Results/json/level3_manuscript_quality_gate.json` 写出 `Results/json/auto_mode_acceptance_chain.json` 与 `Reviews/auto_mode_acceptance_chain.md`。
- [x] 真实输出：状态为 `needs_auto_mode_repair`；修复队列包含 `mark_candidate_references_for_human_review` 和 `human_review_level3_package_artifacts`；组件状态和信任层均已聚合展示。
- [x] 正式层边界：本节点只写验收链路 JSON 和 Markdown，不写正式论文、不写正式 bibliography、不写 project bibliography、不写 `state/product/*`。
- [x] 验证：`python3 -m unittest tests.test_auto_mode_acceptance_chain -v` 通过 5 项；P7-A/B/C/D 回归 21 项通过；`python3 -m py_compile` 通过；scoped `git diff --check` 通过。
- [x] 下一步 P7-E：按 repair queue 生成草稿层 patch proposal，为 `paper.md` 的参考文献候选逐条追加“候选/待人工核验”标记，但仍不改正式层。

## 2026-05-28 P7-E Reference Marker Patch Proposal

- [x] 节点目标：把 P7-D repair queue 中的 `mark_candidate_references_for_human_review` 做成草稿层 patch proposal，修复 Level 3 引用标记缺口，但不覆盖原 paper package。
- [x] BDD/TDD：新增 `tests/test_reference_marker_patch_proposal.py`，覆盖未标记候选引用补标记、已标记引用幂等、JSON/Markdown/候选稿输出、正式层边界、缺少候选参考文献节阻断。
- [x] RED 记录：`python3 -m unittest tests.test_reference_marker_patch_proposal -v` 首次失败原因为缺少 `Program.workbench.reference_marker_patch_proposal`。
- [x] 实现范围：新增 `Program/workbench/reference_marker_patch_proposal.py` 和 `Program/reference_marker_patch_proposal.py`；新增计划 `docs/superpowers/plans/2026-05-28-reference-marker-patch-proposal.md`。
- [x] 真实运行：`python3 Program/reference_marker_patch_proposal.py --project-root . --source-paper workspace/paper_packages/cgss_social_capital_happiness/paper.md --candidate-paper Manuscripts/generated/cgss_social_capital_happiness_paper_reference_marked.md --output-report Results/json/reference_marker_patch_proposal.json --output-review Reviews/reference_marker_patch_proposal.md`。
- [x] 真实输出：状态为 `needs_human_reference_marker_review`；候选稿路径为 `Manuscripts/generated/cgss_social_capital_happiness_paper_reference_marked.md`；8 条参考文献候选均追加 `（候选，待人工核验）`。
- [x] 候选稿复验：`python3 Program/level3_manuscript_quality_gate.py --project-root . --paper Manuscripts/generated/cgss_social_capital_happiness_paper_reference_marked.md --package-manifest workspace/paper_packages/cgss_social_capital_happiness/manifest.json --output-report Results/json/level3_manuscript_quality_gate_reference_marker_candidate.json --output-review Reviews/level3_manuscript_quality_gate_reference_marker_candidate.md` 输出 `gate_status=yellow`、`ready_for_level3_review=true`。
- [x] 验收链复验：`python3 Program/auto_mode_acceptance_chain.py --project-root . --dataset-index Results/json/dataset_motherlode_index.json --literature-seed Results/json/literature_discovery_seed.json --level3-gate Results/json/level3_manuscript_quality_gate_reference_marker_candidate.json --output-report Results/json/auto_mode_acceptance_chain_reference_marker_candidate.json --output-review Reviews/auto_mode_acceptance_chain_reference_marker_candidate.md` 输出 `package_readiness=needs_human_final_review`，repair queue 为空。
- [x] 正式层边界：本节点只写 proposal JSON、审阅报告和草稿层候选稿；不覆盖 `workspace/paper_packages/cgss_social_capital_happiness/paper.md`，不写正式 manuscript，不写正式 bibliography，不写 project bibliography，不写 `state/product/*`。
- [x] 验证：目标测试 5 OK；P7-A/B/C/D/E 回归 26 OK；Python 编译通过；P7-E 相关文件 scoped `git diff --check` 通过。
- [x] 下一步 P7-F：已转入 Method Knowledge Base，把 `Program/methodology` proposal/canonical 边界做成可查询 CLI 知识库。

## 2026-05-28 P7-F Method Knowledge Base

- [x] 节点目标：把 MethodAgent 可用的方法规则来源产品化为 CLI-first Method Knowledge Base，读取 `Program/methodology` 的 README、proposal 和 canonical 规则，输出可审阅方法检查。
- [x] BDD/TDD：新增 `tests/test_method_knowledge_base.py`，覆盖 canonical/proposal 分层、CGSS OLS + Ordered Logit 查询、AER-like profile 不越权阻断、JSON/Markdown 输出、缺少方法库来源阻断。
- [x] RED 记录：`python3 -m unittest tests.test_method_knowledge_base -v` 首次失败原因为缺少 `Program.workbench.method_knowledge_base`。
- [x] 实现范围：新增 `Program/workbench/method_knowledge_base.py` 和 `Program/method_knowledge_base.py`；新增计划 `docs/superpowers/plans/2026-05-28-method-knowledge-base.md`。
- [x] 真实运行：`python3 Program/method_knowledge_base.py --project-root . --query "CGSS 主观幸福感 社会资本 OLS Ordered Logit 横截面 AER-like" --profile aer_like` 写出 `Results/json/method_knowledge_base.json` 与 `Reviews/method_knowledge_base.md`。
- [x] 真实输出：状态为 `needs_human_method_kb_review`；当前项目有 1 个 AER-like proposal 来源、0 个 canonical 规则、0 个 reviewed canonical blocking 规则；返回 6 个 CGSS OLS + Ordered Logit 方法检查。
- [x] 正式层边界：本节点不联网、不同步外部仓库、不提升 proposal 到 canonical，不写正式 manuscript、正式 bibliography、project bibliography、DesignSpec、RunPlan 或 `state/product/*`。
- [x] 验证：目标测试 5 OK；P7-A/B/C/D/E/F 回归 31 OK；Python 编译通过；P7-F 相关文件 scoped `git diff --check` 通过。
- [x] 下一步 P7-G：已实现 Statistical Adapter Contract，把 OLS/Ordered Logit/IV/DID 等执行结果标准化为 Auto Mode 可消费的统计适配器契约。

## 2026-05-28 P7-G Statistical Adapter Contract

- [x] 节点目标：把已有统计执行产物统一成 Auto Mode 可消费的统计结果契约，避免论文包、方法门和写作代理分别猜测后端字段。
- [x] BDD/TDD：新增 `tests/test_statistical_adapter_contract.py`，覆盖本地 OLS/IV 执行结果规范化、CGSS OLS + Ordered Logit 证据规范化、capability/missing-field matrix、JSON/Markdown 输出、缺少统计来源阻断。
- [x] RED 记录：`python3 -m unittest tests.test_statistical_adapter_contract -v` 首次失败原因为缺少 `Program.workbench.statistical_adapter_contract`。
- [x] 实现范围：新增 `Program/workbench/statistical_adapter_contract.py` 和 `Program/statistical_adapter_contract.py`；新增计划 `docs/superpowers/plans/2026-05-28-statistical-adapter-contract.md`。
- [x] 真实运行：`python3 Program/statistical_adapter_contract.py --project-root . --method-execution Results/json/method_execution_result.json --cgss-results-evidence workspace/paper_packages/cgss_social_capital_happiness/results_evidence_package.json` 写出 `Results/json/statistical_adapter_contract.json` 与 `Reviews/statistical_adapter_contract.md`。
- [x] 真实输出：状态为 `needs_human_statistical_adapter_review`；生成 6 个 normalized results，其中 OLS 2 个、Ordered Logit 1 个、IV 3 个，capability matrix 均为 `contract_ready`。
- [x] 正式层边界：本节点只读取已有执行/证据 JSON，不重跑模型、不调用 StatsPAI/Stata/Python 后端、不覆盖执行产物，不写正式 manuscript、正式 bibliography、DesignSpec、RunPlan 或 `state/product/*`。
- [x] 验证：目标测试 5 OK；P7-A/B/C/D/E/F/G 回归 36 OK；Python 编译通过；P7-G 相关文件 scoped `git diff --check` 通过。
- [x] 下一步 P7-H：已把 Method KB 和 Statistical Adapter Contract 接入 Auto Mode acceptance chain，使最终 package readiness 能同时读取方法规则和统计结果 contract。

## 2026-05-28 P7-H Auto Mode Method + Statistical Contract Chain

- [x] 节点目标：把 P7-F Method Knowledge Base 与 P7-G Statistical Adapter Contract 接入 P7-D Auto Mode acceptance chain，让最终 package readiness 同时读取数据、文献、Level 3 论文门、方法规则和统计结果契约。
- [x] BDD/TDD：扩展 `tests/test_auto_mode_acceptance_chain.py`，覆盖五组件聚合、method/stat review-ready 进入人工终审、缺失 method/stat 输入阻断并路由修复、统计契约不完整触发 repair、method/stat readiness summary、JSON/Markdown 输出。
- [x] RED 记录：`python3 -m unittest tests.test_auto_mode_acceptance_chain -v` 首次失败原因为 `build_auto_mode_acceptance_chain()` 尚不接受 `method_knowledge_base` 和 `statistical_adapter_contract` 参数。
- [x] 实现范围：扩展 `Program/workbench/auto_mode_acceptance_chain.py` 与 `Program/auto_mode_acceptance_chain.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-method-stat-chain.md`；新增审阅输出 `Reviews/auto_mode_acceptance_chain_method_stat_integrated.md`。
- [x] 真实运行：`python3 Program/auto_mode_acceptance_chain.py --project-root . --dataset-index Results/json/dataset_motherlode_index.json --literature-seed Results/json/literature_discovery_seed.json --level3-gate Results/json/level3_manuscript_quality_gate_reference_marker_candidate.json --method-kb Results/json/method_knowledge_base.json --statistical-contract Results/json/statistical_adapter_contract.json --output-report Results/json/auto_mode_acceptance_chain_method_stat_integrated.json --output-review Reviews/auto_mode_acceptance_chain_method_stat_integrated.md`。
- [x] 真实输出：状态为 `needs_human_final_review`；五个组件均纳入 `component_statuses`；Method KB summary 显示 6 个推荐检查、1 个 proposal 来源、0 个 reviewed canonical blocking rules；Statistical Adapter Contract summary 显示 6 个 normalized results、6 个 contract-ready results，观测方法为 IV、OLS、Ordered Logit；repair queue 为空。
- [x] 正式层边界：本节点只写验收链路 JSON 和 Markdown，不重跑模型、不提升 proposal 到 canonical，不覆盖统计执行产物，不写正式论文、正式 bibliography、project bibliography、DesignSpec、RunPlan 或 `state/product/*`。
- [x] 验证：目标测试 8 OK；P7-A/B/C/D/E/F/G/H 回归 39 OK；Python 编译通过；P7-H tracked scoped `git diff --check` 通过。
- [x] 下一步 P7-I：已把 `needs_human_final_review` 转成一个可人工签收的 final review packet / promotion decision router，默认 `defer` 且不写正式层。

## 2026-05-28 P7-I Auto Mode Final Review Packet

- [x] 节点目标：把 P7-H 五组件 `needs_human_final_review` 验收链和 CGSS paper package manifest 汇总成可人工签收的 final review packet，并提供 `defer/approve/revise/reject` 决策路由。
- [x] BDD/TDD：新增 `tests/test_auto_mode_final_review_packet.py`，覆盖 ready chain + package manifest 生成终审 packet、上游 repair queue 阻断终审、默认 defer 不写正式层、approve 必须有 reviewer/note、approve 只进入 formal promotion preflight、revise/reject 不允许 promotion、CLI 默认写出 packet/router 审阅产物。
- [x] RED 记录：`python3 -m unittest tests.test_auto_mode_final_review_packet -v` 首次失败原因为缺少 `Program.workbench.auto_mode_final_review_packet`。
- [x] 实现范围：新增 `Program/workbench/auto_mode_final_review_packet.py` 和 `Program/auto_mode_final_review_packet.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-final-review-packet.md`；新增审阅输出 `Reviews/auto_mode_final_review_packet.md` 与 `Reviews/auto_mode_final_review_decision.md`。
- [x] 真实运行：`python3 Program/auto_mode_final_review_packet.py --project-root . --acceptance-chain Results/json/auto_mode_acceptance_chain_method_stat_integrated.json --package-manifest workspace/paper_packages/cgss_social_capital_happiness/manifest.json --decision defer --output-packet Results/json/auto_mode_final_review_packet.json --output-packet-review Reviews/auto_mode_final_review_packet.md --output-decision Results/json/auto_mode_final_review_decision.json --output-decision-review Reviews/auto_mode_final_review_decision.md`。
- [x] 真实输出：packet 状态为 `awaiting_human_final_review`，可请求人工终审决策；evidence summary 包含 5 个组件、6 个方法检查、6 个 contract-ready 统计结果和 9 个 package 文件；decision 状态为 `waiting_for_human_final_review_decision`，route 为 `wait_for_human_confirmation`。
- [x] 正式层边界：本节点只写终审 packet/router JSON 和 Markdown；默认 `defer`，不批准、不写正式论文、正式 bibliography、project bibliography、DesignSpec、RunPlan、`state/product/*`，不重跑模型、不覆盖统计执行产物。
- [x] 验证：目标测试 7 OK；P7-A/B/C/D/E/F/G/H/I 回归 46 OK；Python 编译通过；P7-I staged `git diff --cached --check` 通过。
- [x] 下一步 P7-J：已实现 formal promotion preflight；当前真实状态因 P7-I `decision=defer` 阻断，正式写回仍需单独明确授权。

## 2026-05-28 P7-J Auto Mode Formal Promotion Preflight

- [x] 节点目标：在 P7-I 人工终审 `approve` 之后，生成 formal promotion preflight ledger；本节点只判断是否可请求下一道正式写回审批，不直接写正式论文、bibliography、DesignSpec、RunPlan、`state/product/*`、PDF/DOCX 或统计产物。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_promotion_preflight.py`，覆盖终审 approve 后进入正式写回审批预检、当前 defer 阻断、approve 缺少 reviewer/note 阻断、package manifest 缺口阻断、只写 JSON/Markdown、CLI 默认读取当前 defer 决策并写 blocked preflight。
- [x] RED 记录：`python3 -m unittest tests.test_auto_mode_formal_promotion_preflight -v` 首次失败原因为缺少 `Program.workbench.auto_mode_formal_promotion_preflight`。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_promotion_preflight.py` 和 `Program/auto_mode_formal_promotion_preflight.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-promotion-preflight.md`；新增审阅输出 `Reviews/auto_mode_formal_promotion_preflight.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_promotion_preflight.py --project-root . --final-review-decision Results/json/auto_mode_final_review_decision.json --final-review-packet Results/json/auto_mode_final_review_packet.json --package-manifest workspace/paper_packages/cgss_social_capital_happiness/manifest.json --output-report Results/json/auto_mode_formal_promotion_preflight.json --output-review Reviews/auto_mode_formal_promotion_preflight.md`。
- [x] 真实输出：状态为 `blocked_by_final_review_decision`；`can_request_formal_writeback_approval=false`、`formal_writeback_allowed=false`、`can_write_product_state=false`；阻断原因包括 `final_review_decision_not_approved_for_preflight`、`final_review_decision_not_approve`、`final_review_route_not_formal_promotion_preflight`、`final_review_decision_not_approved` 和 `final_review_promotion_not_allowed`。
- [x] 正式层边界：本节点只写 formal promotion preflight JSON 和 Markdown；不把 `defer` 当作批准，不写正式 manuscript、正式 bibliography、project bibliography、DesignSpec、RunPlan、`state/product/*`，不渲染 PDF/DOCX，不重跑模型，不覆盖统计执行产物。
- [x] 验证：目标测试 6 OK；P7-A/B/C/D/E/F/G/H/I/J 回归 52 OK；Python 编译通过；P7-J scoped `git diff --check` 通过。
- [x] 下一步 P7-K：已实现 auto-mode formal writeback approval ledger；当前真实状态因 P7-J preflight blocked 而继续阻断，未批准、未写正式层。

## 2026-05-28 P7-K Auto Mode Formal Writeback Approval Ledger

- [x] 节点目标：在 P7-J formal promotion preflight ready 之后，记录单独的人类 formal writeback approval；本节点只生成审批账本并授权下一道执行预检，不直接写正式论文、bibliography、DesignSpec、RunPlan、`state/product/*`、PDF/DOCX 或统计产物。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_writeback_approval.py`，覆盖 ready preflight + approve 记录可生效审批、defer 等待、P7-J blocked 不可绕过、approve 缺 reviewer/note 阻断、revise/reject 不启用写回、只写 JSON/Markdown、CLI 默认读取当前 blocked preflight 并禁止正式写回。
- [x] RED 记录：`python3 -m unittest tests.test_auto_mode_formal_writeback_approval -v` 首次失败原因为缺少 `Program.workbench.auto_mode_formal_writeback_approval`。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_writeback_approval.py` 和 `Program/auto_mode_formal_writeback_approval.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-writeback-approval.md`；新增审阅输出 `Reviews/auto_mode_formal_writeback_approval.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_writeback_approval.py --project-root . --formal-promotion-preflight Results/json/auto_mode_formal_promotion_preflight.json --decision defer --output-approval Results/json/auto_mode_formal_writeback_approval.json --output-review Reviews/auto_mode_formal_writeback_approval.md`。
- [x] 真实输出：状态为 `blocked_by_formal_promotion_preflight`；`approved=false`、`formal_writeback_allowed=false`、`can_enter_formal_writeback_execution_preflight=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；阻断原因包括 `formal_promotion_preflight_not_ready`、`formal_promotion_preflight_cannot_request_approval` 和 `formal_promotion_scope_missing`。
- [x] 正式层边界：本节点只写 formal writeback approval JSON 和 Markdown；不把 `defer` 或 blocked preflight 当作批准，不写正式 manuscript、正式 bibliography、project bibliography、DesignSpec、RunPlan、`state/product/*`，不渲染 PDF/DOCX，不重跑模型，不覆盖统计执行产物。
- [x] 验证：目标测试 7 OK；P7-A/B/C/D/E/F/G/H/I/J/K 回归 59 OK；Python 编译通过；P7-K scoped `git diff --check` 通过。
- [x] 下一步 P7-L：已实现 formal writeback execution preflight；当前真实状态因 P7-K approval 未生效而 blocked，不执行正式写回。

## 2026-05-28 P7-L Auto Mode Formal Writeback Execution Preflight

- [x] 节点目标：消费 P7-K formal writeback approval ledger，把生效审批转成可审阅的正式写回执行计划；本节点只做执行预检，不直接写正式论文、bibliography、DesignSpec、RunPlan、`state/product/*`、PDF/DOCX 或统计产物。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_writeback_execution_preflight.py`，覆盖生效 approval 生成 execution plan、当前 approval 未生效阻断、approved scope 缺失阻断、上游边界越界阻断、只写 JSON/Markdown、CLI 默认读取当前 blocked approval 并不执行写回。
- [x] RED 记录：`python3 -m unittest tests.test_auto_mode_formal_writeback_execution_preflight -v` 首次失败原因为缺少 `Program.workbench.auto_mode_formal_writeback_execution_preflight`。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_writeback_execution_preflight.py` 和 `Program/auto_mode_formal_writeback_execution_preflight.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-writeback-execution-preflight.md`；新增审阅输出 `Reviews/auto_mode_formal_writeback_execution_preflight.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_writeback_execution_preflight.py --project-root . --formal-writeback-approval Results/json/auto_mode_formal_writeback_approval.json --output-preflight Results/json/auto_mode_formal_writeback_execution_preflight.json --output-review Reviews/auto_mode_formal_writeback_execution_preflight.md`。
- [x] 真实输出：状态为 `blocked_by_formal_writeback_approval`；`can_request_formal_writeback_execution=false`、`formal_writeback_executed=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；阻断原因包括 `formal_writeback_approval_not_effective`、`formal_writeback_approval_decision_not_approve`、`formal_writeback_approval_metadata_incomplete` 和 `approved_scope_missing`。
- [x] 正式层边界：本节点只写 formal writeback execution preflight JSON 和 Markdown；不把 blocked approval 当作批准，不写正式 manuscript、正式 bibliography、project bibliography、DesignSpec、RunPlan、`state/product/*`，不渲染 PDF/DOCX，不重跑模型，不覆盖统计执行产物。
- [x] 验证：目标测试 6 OK；P7-A/B/C/D/E/F/G/H/I/J/K/L 回归 65 OK；Python 编译通过；P7-L scoped `git diff --check` 通过。
- [x] 下一步 P7-M：已实现显式 formal writeback execute dry-run/apply 分离；当前真实状态因 P7-L blocked 而 blocked，未记录 apply manifest，未写正式层。

## 2026-05-28 P7-M Auto Mode Formal Writeback Execute Dry-Run/Apply Gate

- [x] 节点目标：消费 P7-L formal writeback execution preflight，提供显式 `dry-run/apply` 执行门；默认 dry-run 只生成计划审阅，确认 apply 也只记录 apply manifest，不直接写正式层。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_writeback_execute.py`，覆盖 ready preflight dry-run、当前 P7-L blocked 阻断、apply 必须显式确认、apply 必须有 reviewer/note、confirmed apply 只写 manifest、CLI 默认读取当前 blocked preflight。
- [x] RED 记录：`python3 -m unittest tests.test_auto_mode_formal_writeback_execute -v` 首次失败原因为缺少 `Program.workbench.auto_mode_formal_writeback_execute`。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_writeback_execute.py` 和 `Program/auto_mode_formal_writeback_execute.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-writeback-execute.md`；新增审阅输出 `Reviews/auto_mode_formal_writeback_execute.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_writeback_execute.py --project-root . --execution-preflight Results/json/auto_mode_formal_writeback_execution_preflight.json --mode dry-run --output-execute Results/json/auto_mode_formal_writeback_execute.json --output-review Reviews/auto_mode_formal_writeback_execute.md --apply-manifest workspace/formal_writeback_apply/auto_mode/formal_writeback_apply_manifest.json`。
- [x] 真实输出：状态为 `blocked_by_execution_preflight`；`mode=dry-run`、`can_apply_with_confirmation=false`、`apply_manifest_recorded=false`、`formal_writeback_executed=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；未生成 apply manifest。
- [x] 正式层边界：本节点只写 execute dry-run/apply gate JSON 和 Markdown；当前真实 dry-run 不写 apply manifest。即使 confirmed apply，也只记录 apply manifest，不执行 formal target adapters，不写正式 manuscript、正式 bibliography、project bibliography、DesignSpec、RunPlan、`state/product/*`，不渲染 PDF/DOCX，不重跑模型，不覆盖统计执行产物。
- [x] 验证：目标测试 6 OK；P7-A/B/C/D/E/F/G/H/I/J/K/L/M 回归 71 OK；Python 编译通过；P7-M scoped `git diff --check` 通过。
- [x] 下一步 P7-N：已实现 formal target adapter readiness/mapping；当前真实状态因 apply manifest 未记录而 blocked，未生成 adapter mappings，未写正式层。

## 2026-05-28 P7-N Auto Mode Formal Target Adapter Readiness Mapping

- [x] 节点目标：消费 P7-M apply manifest 和 CGSS paper package manifest，把 6 类 `writeback_target_group` 映射到具体候选写回目标；本节点只做 readiness/mapping，不执行 target adapter。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_target_adapter_readiness.py`，覆盖 ready apply manifest 映射 6 类 target group、当前缺少 apply manifest 阻断、未知 target group 阻断、缺少 package artifact 阻断、apply manifest 边界越界阻断、只写 report/review 不创建 candidate target、CLI 默认 blocked。
- [x] RED 记录：`python3 -m unittest tests.test_auto_mode_formal_target_adapter_readiness -v` 首次失败原因为缺少 `Program.workbench.auto_mode_formal_target_adapter_readiness`。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_target_adapter_readiness.py` 和 `Program/auto_mode_formal_target_adapter_readiness.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-target-adapter-readiness.md`；新增审阅输出 `Reviews/auto_mode_formal_target_adapter_readiness.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_target_adapter_readiness.py --project-root . --apply-manifest workspace/formal_writeback_apply/auto_mode/formal_writeback_apply_manifest.json --package-manifest workspace/paper_packages/cgss_social_capital_happiness/manifest.json --target-root Submissions/auto_mode --output-report Results/json/auto_mode_formal_target_adapter_readiness.json --output-review Reviews/auto_mode_formal_target_adapter_readiness.md`。
- [x] 真实输出：状态为 `blocked_by_apply_manifest`；`adapter_mappings=0`、`can_request_target_adapter_execution=false`、`formal_target_adapters_executed=false`、`formal_writeback_executed=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；未创建 `Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md`。
- [x] 正式层边界：本节点只写 target adapter readiness JSON 和 Markdown；不执行 adapter，不复制 package artifact，不写正式 manuscript、正式 bibliography、project bibliography、DesignSpec、RunPlan、`state/product/*`，不渲染 PDF/DOCX，不重跑模型，不覆盖统计执行产物。
- [x] 验证：目标测试 7 OK；P7-A/B/C/D/E/F/G/H/I/J/K/L/M/N 回归 78 OK；Python 编译通过；P7-N scoped `git diff --check` 通过。
- [x] 下一步 P7-O：已实现 formal target adapter execution gate；当前真实状态因 P7-N readiness blocked 而 blocked，不记录 execution manifest，不执行 adapter，不写正式层。

## 2026-05-28 P7-O Auto Mode Formal Target Adapter Execution Gate

- [x] 节点目标：消费 P7-N target adapter readiness，提供显式 `dry-run/execute` 执行门；默认 dry-run 只生成执行计划审阅，确认 execute 也只记录 execution manifest，不直接 materialize candidate targets。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_target_adapter_execution.py`，覆盖 ready readiness dry-run、当前 P7-N blocked 阻断、execute 必须显式确认、execute 必须有 reviewer/note、confirmed execute 只写 manifest、bad adapter mapping 阻断、CLI 默认 blocked。
- [x] RED 记录：`python3 -m unittest tests.test_auto_mode_formal_target_adapter_execution -v` 首次失败原因为缺少 `Program.workbench.auto_mode_formal_target_adapter_execution`。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_target_adapter_execution.py` 和 `Program/auto_mode_formal_target_adapter_execution.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-target-adapter-execution.md`；新增审阅输出 `Reviews/auto_mode_formal_target_adapter_execution.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_target_adapter_execution.py --project-root . --target-adapter-readiness Results/json/auto_mode_formal_target_adapter_readiness.json --mode dry-run --output-execution Results/json/auto_mode_formal_target_adapter_execution.json --output-review Reviews/auto_mode_formal_target_adapter_execution.md --execution-manifest workspace/formal_target_adapter_execution/auto_mode/formal_target_adapter_execution_manifest.json`。
- [x] 真实输出：状态为 `blocked_by_target_adapter_readiness`；`adapter_execution_plan=0`、`execution_manifest_recorded=false`、`formal_target_adapters_executed=false`、`formal_writeback_executed=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；未生成 execution manifest，未创建 `Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md`。
- [x] 正式层边界：本节点只写 target adapter execution gate JSON 和 Markdown；不执行 adapter，不创建 candidate target，不写正式 manuscript、正式 bibliography、project bibliography、DesignSpec、RunPlan、`state/product/*`，不渲染 PDF/DOCX，不重跑模型，不覆盖统计执行产物。
- [x] 验证：目标测试 7 OK；P7-A/B/C/D/E/F/G/H/I/J/K/L/M/N/O 回归 85 OK；Python 编译通过；P7-O scoped `git diff --check` 通过。
- [x] 下一步 P7-P：已实现 adapter materialization preflight；当前真实状态因 P7-O blocked 且未记录 execution manifest 而 blocked，不 materialize、不写正式层。

## 2026-05-28 P7-P Auto Mode Formal Target Adapter Materialization Preflight

- [x] 节点目标：消费 P7-O target adapter execution report 和 execution manifest，生成 adapter materialization preflight；本节点只判断是否可请求下一道显式 materialize 命令，不创建 candidate target。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_target_adapter_materialization_preflight.py`，覆盖 recorded execution manifest 生成 materialization plan、当前 P7-O blocked 阻断、missing/invalid manifest 阻断、execution report 未进入 recorded-manifest 状态阻断、bad adapter execution plan 阻断、CLI 默认 blocked、只写 report/review 不 materialize。
- [x] RED 记录：`python3 -m unittest tests.test_auto_mode_formal_target_adapter_materialization_preflight -v` 首次失败原因为缺少 `Program.workbench.auto_mode_formal_target_adapter_materialization_preflight`。
- [x] Agent Team：未调用；本节点是单一 schema/CLI 小切片，主要风险可由 P7-O/P7-P 目标测试和全链路回归覆盖，拆 sidecar 不会明显提升质量或速度。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_target_adapter_materialization_preflight.py` 和 `Program/auto_mode_formal_target_adapter_materialization_preflight.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-target-adapter-materialization-preflight.md`；新增审阅输出 `Reviews/auto_mode_formal_target_adapter_materialization_preflight.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_target_adapter_materialization_preflight.py --project-root . --target-adapter-execution Results/json/auto_mode_formal_target_adapter_execution.json --execution-manifest workspace/formal_target_adapter_execution/auto_mode/formal_target_adapter_execution_manifest.json --output-preflight Results/json/auto_mode_formal_target_adapter_materialization_preflight.json --output-review Reviews/auto_mode_formal_target_adapter_materialization_preflight.md`。
- [x] 真实输出：状态为 `blocked_by_target_adapter_execution`；`materialization_plan=0`、`can_request_adapter_materialization=false`、`requires_explicit_materialize_command=false`、`candidate_targets_materialized=false`、`formal_target_adapters_executed=false`、`formal_writeback_executed=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；未生成 execution manifest，未创建 `Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md`。
- [x] 正式层边界：本节点只写 materialization preflight JSON 和 Markdown；不 materialize candidate target，不执行 target adapter，不写正式 manuscript、正式 bibliography、project bibliography、DesignSpec、RunPlan、`state/product/*`，不渲染 PDF/DOCX，不重跑模型，不覆盖统计执行产物。
- [x] 验证：目标测试 7 OK；P7-A/B/C/D/E/F/G/H/I/J/K/L/M/N/O/P 回归 92 OK；Python 编译通过；P7-P scoped `git diff --check` 通过。
- [x] 下一步 P7-Q：已实现显式 adapter materialization execute gate；默认因 P7-P blocked 而 blocked，不创建 candidate target、不写正式层。

## 2026-05-28 P7-Q Auto Mode Formal Target Adapter Materialization Execute Gate

- [x] 节点目标：消费 P7-P materialization preflight，提供显式 `dry-run/materialize` 命令门；ready + confirmed `materialize` 才把 source artifacts 复制到 candidate targets，且不提升为正式层。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_target_adapter_materialization_execute.py`，覆盖 ready preflight dry-run、当前 P7-P blocked 阻断、materialize 必须显式确认、materialize 必须有 reviewer/note、confirmed materialize 只写 candidate targets 和 manifest、缺 source/target 已存在阻断、CLI 默认 blocked。
- [x] RED 记录：`python3 -m unittest tests.test_auto_mode_formal_target_adapter_materialization_execute -v` 首次失败原因为缺少 `Program.workbench.auto_mode_formal_target_adapter_materialization_execute`。
- [x] Agent Team：未调用；本节点是单一 materialization gate 小切片，主要风险由 ready/blocked/confirmed materialize 单测和 P7 回归覆盖，拆 sidecar 不会明显提升质量或速度。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_target_adapter_materialization_execute.py` 和 `Program/auto_mode_formal_target_adapter_materialization_execute.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-target-adapter-materialization-execute.md`；新增审阅输出 `Reviews/auto_mode_formal_target_adapter_materialization_execute.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_target_adapter_materialization_execute.py --project-root . --materialization-preflight Results/json/auto_mode_formal_target_adapter_materialization_preflight.json --mode dry-run --output-execute Results/json/auto_mode_formal_target_adapter_materialization_execute.json --output-review Reviews/auto_mode_formal_target_adapter_materialization_execute.md --materialization-manifest workspace/formal_target_adapter_materialization/auto_mode/formal_target_adapter_materialization_manifest.json`。
- [x] 真实输出：状态为 `blocked_by_materialization_preflight`；`materialization_operations=0`、`can_materialize_with_confirmation=false`、`materialization_manifest_recorded=false`、`candidate_targets_materialized=false`、`formal_target_adapters_executed=false`、`formal_writeback_executed=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；未生成 materialization manifest，未创建 `Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md`。
- [x] 正式层边界：本节点只在 confirmed materialize 且 preflight ready 时写 candidate targets 与 materialization manifest；不写正式 manuscript、正式 bibliography、project bibliography、DesignSpec、RunPlan、`state/product/*`，不渲染 PDF/DOCX，不重跑模型，不覆盖统计执行产物。
- [x] 验证：目标测试 7 OK；P7-A/B/C/D/E/F/G/H/I/J/K/L/M/N/O/P/Q 回归 99 OK；Python 编译通过；P7-Q scoped `git diff --check` 通过。
- [x] 下一步 P7-R：已实现 materialized candidate target verification gate；默认因 P7-Q blocked 而 blocked，不提升正式层。

## 2026-05-28 P7-R Auto Mode Formal Target Adapter Candidate Verification Gate

- [x] 节点目标：消费 P7-Q materialization execute report 和 materialization manifest，验证 materialized candidate targets 是否存在且与 manifest byte count 一致；本节点只验证，不创建、不修复、不提升正式层。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_target_adapter_candidate_verification.py`，覆盖 completed materialization 验证 candidate targets、当前 P7-Q blocked 阻断、missing/invalid manifest 阻断、execute report 未 completed/materialized 阻断、target 缺失或 bytes 不一致阻断、boundary violation 阻断、CLI 默认 blocked、只写 report/review 不写正式层。
- [x] RED 记录：`python3 -m unittest tests.test_auto_mode_formal_target_adapter_candidate_verification -v` 首次失败原因为缺少 `Program.workbench.auto_mode_formal_target_adapter_candidate_verification`。
- [x] Agent Team：未调用；本节点是单一 verification gate 小切片，主要风险由 target 存在性/bytes/边界单测和 P7 回归覆盖，拆 sidecar 不会明显提升质量或速度。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_target_adapter_candidate_verification.py` 和 `Program/auto_mode_formal_target_adapter_candidate_verification.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-target-adapter-candidate-verification.md`；新增审阅输出 `Reviews/auto_mode_formal_target_adapter_candidate_verification.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_target_adapter_candidate_verification.py --project-root . --materialization-execute Results/json/auto_mode_formal_target_adapter_materialization_execute.json --materialization-manifest workspace/formal_target_adapter_materialization/auto_mode/formal_target_adapter_materialization_manifest.json --output-verification Results/json/auto_mode_formal_target_adapter_candidate_verification.json --output-review Reviews/auto_mode_formal_target_adapter_candidate_verification.md`。
- [x] 真实输出：状态为 `blocked_by_materialization_execute`；`candidate_targets_verified=false`、`target_verification_records=0`、`formal_target_adapters_executed=false`、`formal_writeback_executed=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；未生成 materialization manifest，未创建 `Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md`，未写 `state/product/auto_mode_formal_target_adapter_candidate_verification.json`。
- [x] 正式层边界：本节点只写 candidate verification JSON 和 Markdown；不创建/修复 candidate target，不写正式 manuscript、正式 bibliography、project bibliography、DesignSpec、RunPlan、`state/product/*`，不渲染 PDF/DOCX，不重跑模型，不覆盖统计执行产物。
- [x] 验证：目标测试 8 OK；P7-A/B/C/D/E/F/G/H/I/J/K/L/M/N/O/P/Q/R 回归 107 OK；Python 编译通过；P7-R scoped `git diff --check` 通过。
- [x] 下一步 P7-S：已实现 verified candidate promotion preflight；默认因 P7-R blocked 而 blocked，不提升正式层。

## 2026-05-28 P7-S Auto Mode Formal Target Adapter Candidate Promotion Preflight

- [x] 节点目标：消费 P7-R candidate verification report，把已验证 candidate targets 转成可审阅的 verified candidate promotion preflight；本节点只判断是否可请求后续提升审批/显式执行，不提升候选目标。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_target_adapter_candidate_promotion_preflight.py`，覆盖 verified candidates 生成 promotion preflight plan、当前 P7-R blocked 阻断、missing/invalid schema 阻断、逐项 verification record 必须 verified/auto_mode/SHA256、boundary violation 阻断、CLI 默认 blocked、只写 report/review 不提升 candidate。
- [x] RED 记录：`python3 -m unittest tests.test_auto_mode_formal_target_adapter_candidate_promotion_preflight -v` 首次失败原因为缺少 `Program.workbench.auto_mode_formal_target_adapter_candidate_promotion_preflight`；扩展 CLI 行为后第二次 RED 为缺少 `Program/auto_mode_formal_target_adapter_candidate_promotion_preflight.py`。
- [x] Agent Team：未调用；本节点是单一 preflight gate 小切片，主要风险由 P7-R ready/blocked/record/boundary 单测和 P7 回归覆盖，拆 sidecar 不会明显提升质量或速度。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_target_adapter_candidate_promotion_preflight.py` 和 `Program/auto_mode_formal_target_adapter_candidate_promotion_preflight.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-target-adapter-candidate-promotion-preflight.md`；新增审阅输出 `Reviews/auto_mode_formal_target_adapter_candidate_promotion_preflight.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_target_adapter_candidate_promotion_preflight.py --project-root . --candidate-verification Results/json/auto_mode_formal_target_adapter_candidate_verification.json --output-preflight Results/json/auto_mode_formal_target_adapter_candidate_promotion_preflight.json --output-review Reviews/auto_mode_formal_target_adapter_candidate_promotion_preflight.md`。
- [x] 真实输出：状态为 `blocked_by_candidate_verification`；`can_request_verified_candidate_promotion_approval=false`、`promotion_plan=0`、`candidate_targets_promoted=false`、`formal_writeback_executed=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；未创建 `Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md`，未创建 `Submissions/formal_package/manuscript/paper.md`，未写 `state/product/auto_mode_formal_target_adapter_candidate_promotion_preflight.json`。
- [x] 正式层边界：本节点只写 candidate promotion preflight JSON 和 Markdown；不复制/覆盖/提升 candidate target，不写正式 manuscript、正式 bibliography、project bibliography、DesignSpec、RunPlan、`state/product/*`，不渲染 PDF/DOCX，不重跑模型，不覆盖统计执行产物。
- [x] 验证：目标测试 7 OK；P7-A/B/C/D/E/F/G/H/I/J/K/L/M/N/O/P/Q/R/S 回归 114 OK；Python 编译通过。
- [x] 下一步 P7-T：已实现 verified candidate promotion approval gate；默认因 P7-S blocked 而 blocked，不提升正式层。

## 2026-05-28 P7-T Auto Mode Formal Target Adapter Candidate Promotion Approval Gate

- [x] 节点目标：消费 P7-S candidate promotion preflight，记录 `approve/defer/revise/reject` 人工决策；本节点只生成 candidate promotion approval ledger，不提升候选目标。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_target_adapter_candidate_promotion_approval.py`，覆盖 ready preflight + approve 只授权下一道 execution preflight、defer 等待、P7-S blocked 阻断、approve 必须有 reviewer/note、revise/reject 不启用 promotion、CLI 默认 blocked、只写 report/review 不提升 candidate。
- [x] RED 记录：`python3 -m unittest tests.test_auto_mode_formal_target_adapter_candidate_promotion_approval -v` 首次失败原因为缺少 `Program.workbench.auto_mode_formal_target_adapter_candidate_promotion_approval`；扩展 CLI 行为后第二次 RED 为缺少 `Program/auto_mode_formal_target_adapter_candidate_promotion_approval.py`。
- [x] Agent Team：未调用；本节点是单一 approval gate 小切片，主要风险由 ready/blocked/decision/metadata 单测和 P7 回归覆盖，拆 sidecar 不会明显提升质量或速度。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_target_adapter_candidate_promotion_approval.py` 和 `Program/auto_mode_formal_target_adapter_candidate_promotion_approval.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-target-adapter-candidate-promotion-approval.md`；新增审阅输出 `Reviews/auto_mode_formal_target_adapter_candidate_promotion_approval.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_target_adapter_candidate_promotion_approval.py --project-root . --candidate-promotion-preflight Results/json/auto_mode_formal_target_adapter_candidate_promotion_preflight.json --decision defer --output-approval Results/json/auto_mode_formal_target_adapter_candidate_promotion_approval.json --output-review Reviews/auto_mode_formal_target_adapter_candidate_promotion_approval.md`。
- [x] 真实输出：状态为 `blocked_by_candidate_promotion_preflight`；`approved=false`、`verified_candidate_promotion_allowed=false`、`can_enter_verified_candidate_promotion_execution_preflight=false`、`approved_promotion_plan=0`、`candidate_targets_promoted=false`、`formal_writeback_executed=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；未创建 `Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md`，未创建 `Submissions/formal_package/manuscript/paper.md`，未写 `state/product/auto_mode_formal_target_adapter_candidate_promotion_approval.json`。
- [x] 正式层边界：本节点只写 candidate promotion approval JSON 和 Markdown；不复制/覆盖/提升 candidate target，不写正式 manuscript、正式 bibliography、project bibliography、DesignSpec、RunPlan、`state/product/*`，不渲染 PDF/DOCX，不重跑模型，不覆盖统计执行产物。
- [x] 验证：目标测试 7 OK；P7-A/B/C/D/E/F/G/H/I/J/K/L/M/N/O/P/Q/R/S/T 回归 121 OK；Python 编译通过。
- [x] 下一步 P7-U：已实现 verified candidate promotion execution preflight；默认因 P7-T blocked 而 blocked，不提升正式层。

## 2026-05-28 P7-U Auto Mode Formal Target Adapter Candidate Promotion Execution Preflight

- [x] 组件效果：把 P7-T 的“已批准候选目标提升”转成下一步可执行前检查清单；下游可以直接读取 `promotion_execution_plan` 来决定后续显式 execute gate 是否能跑。
- [x] 当前真实效果：仓库里的 P7-T 仍是 blocked/defer，所以本节点输出 `blocked_by_candidate_promotion_approval`，没有执行清单，不允许 promotion。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.py`，覆盖有效审批生成执行预检、blocked 审批阻断、坏清单阻断、边界越界阻断、CLI 默认 blocked、只写 JSON/Markdown。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_target_adapter_candidate_promotion_execution_preflight`；新增 CLI 行为后失败为缺少 `Program/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.py`。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.py` 和 `Program/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-target-adapter-candidate-promotion-execution-preflight.md`；新增审阅输出 `Reviews/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.py --project-root . --candidate-promotion-approval Results/json/auto_mode_formal_target_adapter_candidate_promotion_approval.json --output-preflight Results/json/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.json --output-review Reviews/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.md`。
- [x] 真实输出：`can_request_verified_candidate_promotion_execution=false`、`requires_explicit_promotion_execute_command=false`、`promotion_execution_plan=0`、`candidate_targets_promoted=false`、`formal_writeback_executed=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；未创建 `Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md`，未创建 `Submissions/formal_package/manuscript/paper.md`，未写 `state/product/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.json`。
- [x] 正式层边界：本节点只写 execution preflight JSON 和 Markdown；不复制/覆盖/提升 candidate target，不写正式 manuscript、正式 bibliography、project bibliography、DesignSpec、RunPlan、`state/product/*`，不渲染 PDF/DOCX，不重跑模型，不覆盖统计执行产物。
- [x] 验证：目标测试 6 OK；P7-A/B/C/D/E/F/G/H/I/J/K/L/M/N/O/P/Q/R/S/T/U 回归 127 OK；Python 编译通过。
- [x] 下一步 P7-V：已实现显式 verified candidate promotion execute gate；默认因 P7-U blocked 而 blocked，不提升正式层。

## 2026-05-28 P7-V Auto Mode Formal Target Adapter Candidate Promotion Execute Gate

- [x] 组件效果：把 P7-U 的执行前检查清单接成显式 promote 命令；只有 ready + confirm + reviewer/note + 文件校验通过时，才把 candidate 文件复制到 formal package。
- [x] 当前真实效果：仓库里的 P7-U 仍是 blocked，所以本节点输出 `blocked_by_candidate_promotion_execution_preflight`，没有写正式成果。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_target_adapter_candidate_promotion_execute.py`，覆盖 confirmed promote、dry-run、blocked preflight、缺确认/元数据、候选缺失/变更/目标已存在、CLI 默认 blocked。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_target_adapter_candidate_promotion_execute`；新增 CLI 行为后失败为缺少 `Program/auto_mode_formal_target_adapter_candidate_promotion_execute.py`。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_target_adapter_candidate_promotion_execute.py` 和 `Program/auto_mode_formal_target_adapter_candidate_promotion_execute.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-target-adapter-candidate-promotion-execute.md`；新增审阅输出 `Reviews/auto_mode_formal_target_adapter_candidate_promotion_execute.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_target_adapter_candidate_promotion_execute.py --project-root . --promotion-execution-preflight Results/json/auto_mode_formal_target_adapter_candidate_promotion_execution_preflight.json --mode dry-run --output-execute Results/json/auto_mode_formal_target_adapter_candidate_promotion_execute.json --output-review Reviews/auto_mode_formal_target_adapter_candidate_promotion_execute.md --promotion-manifest workspace/formal_target_adapter_candidate_promotion/auto_mode/formal_target_adapter_candidate_promotion_manifest.json`。
- [x] 真实输出：`status=blocked_by_candidate_promotion_execution_preflight`、`can_promote_with_confirmation=false`、`promotion_operations=0`、`candidate_targets_promoted=false`、`formal_writeback_executed=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；未生成 promotion manifest，未创建 `Submissions/formal_package/manuscript/paper.md`，未写 `state/product/auto_mode_formal_target_adapter_candidate_promotion_execute.json`。
- [x] 正式层边界：confirmed promote 可写 formal package target 和 promotion manifest；默认/current blocked 不写；不写 `state/product/*`，不渲染 PDF/DOCX，不重跑模型。
- [x] 验证：目标测试 6 OK；P7-A/B/C/D/E/F/G/H/I/J/K/L/M/N/O/P/Q/R/S/T/U/V 回归 133 OK；Python 编译通过。
- [x] 下一步 P7-W：已实现 promoted formal package verification gate；默认因 P7-V blocked 而 blocked，确认正式成果文件和 manifest 后再进入后续 package verification/export。

## 2026-05-28 P7-W Auto Mode Formal Target Adapter Promoted Package Verification Gate

- [x] 组件效果：把 P7-V 的 promotion manifest 接成正式包复验节点；只有 P7-V completed 且 formal target 文件存在、bytes 和 SHA256 全匹配时，才标记 formal package verified。
- [x] 当前真实效果：仓库里的 P7-V 仍是 blocked，所以本节点输出 `blocked_by_candidate_promotion_execute`，没有验证正式包。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_target_adapter_promoted_package_verification.py`，覆盖 completed promotion 复验、当前 blocked、manifest 缺失/错误、execute 未完成、正式目标缺失/变更/越界、边界越界、CLI 默认 blocked、只写 report/review。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_target_adapter_promoted_package_verification`。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_target_adapter_promoted_package_verification.py` 和 `Program/auto_mode_formal_target_adapter_promoted_package_verification.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-target-adapter-promoted-package-verification.md`；新增审阅输出 `Reviews/auto_mode_formal_target_adapter_promoted_package_verification.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_target_adapter_promoted_package_verification.py --project-root . --candidate-promotion-execute Results/json/auto_mode_formal_target_adapter_candidate_promotion_execute.json --promotion-manifest workspace/formal_target_adapter_candidate_promotion/auto_mode/formal_target_adapter_candidate_promotion_manifest.json --output-verification Results/json/auto_mode_formal_target_adapter_promoted_package_verification.json --output-review Reviews/auto_mode_formal_target_adapter_promoted_package_verification.md`。
- [x] 真实输出：`status=blocked_by_candidate_promotion_execute`、`formal_package_verified=false`、`promoted_formal_targets_verified=false`、`formal_target_verification_records=0`、`formal_writeback_executed=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；未生成 promotion manifest，未创建 `Submissions/formal_package/manuscript/paper.md`，未写 `state/product/auto_mode_formal_target_adapter_promoted_package_verification.json`。
- [x] 正式层边界：本节点只验证 P7-V 已提升的 formal package target；不复制/修复/覆盖正式成果，不写 `state/product/*`，不渲染 PDF/DOCX，不重跑模型。
- [x] 验证：目标测试 8 OK；P7-A/B/C/D/E/F/G/H/I/J/K/L/M/N/O/P/Q/R/S/T/U/V/W 回归 141 OK；Python 编译通过。
- [x] 下一步 P7-X：已实现 verified formal package export/acceptance preflight；默认因 P7-W blocked 而 blocked，只有正式包复验通过后才进入导出或终态验收。

## 2026-05-28 P7-X Auto Mode Formal Package Export / Acceptance Preflight

- [x] 组件效果：把 P7-W 的正式包复验结果接成导出/终态验收预检；只有 `formal_package_verified=true` 且 formal target 记录完整时，才生成 PDF、DOCX、包 manifest、人工验收四类下一步计划。
- [x] 当前真实效果：仓库里的 P7-W 仍是 blocked，所以本节点输出 `blocked_by_promoted_package_verification`，没有导出/验收计划。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_package_export_acceptance_preflight.py`，覆盖 verified package 生成计划、当前 blocked、报告缺失/错误/未 verified、target 记录缺失/未验证/越界、边界越界、CLI 默认 blocked、只写 report/review。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_package_export_acceptance_preflight`。
- [x] Agent Team：未调用；本节点是单一只读 preflight 小切片，主要风险由 P7-W ready/blocked/target/boundary 单测和 P7 回归覆盖，拆 sidecar 不会明显提升质量或速度。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_package_export_acceptance_preflight.py` 和 `Program/auto_mode_formal_package_export_acceptance_preflight.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-package-export-acceptance-preflight.md`；新增审阅输出 `Reviews/auto_mode_formal_package_export_acceptance_preflight.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_package_export_acceptance_preflight.py --project-root . --promoted-package-verification Results/json/auto_mode_formal_target_adapter_promoted_package_verification.json --output-preflight Results/json/auto_mode_formal_package_export_acceptance_preflight.json --output-review Reviews/auto_mode_formal_package_export_acceptance_preflight.md`。
- [x] 真实输出：`status=blocked_by_promoted_package_verification`、`can_enter_formal_package_export_acceptance=false`、`requires_explicit_export_or_acceptance_command=false`、`export_acceptance_plan=0`、`export_or_acceptance_executed=false`、`rendered_pdf=false`、`rendered_docx=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；仓库已有旧 `paper.pdf/paper.docx`，本节点未改动它们，未写 `state/product/auto_mode_formal_package_export_acceptance_preflight.json`。
- [x] 正式层边界：本节点只写导出/验收预检 JSON 和 Markdown；不渲染 PDF/DOCX，不生成最终包 manifest，不修复/覆盖正式成果，不写 `state/product/*`，不重跑模型。
- [x] 验证：目标测试 7 OK；P7-A/B/C/D/E/F/G/H/I/J/K/L/M/N/O/P/Q/R/S/T/U/V/W/X 回归 148 OK；Python 编译通过。
- [x] 下一步 P7-Y：已实现 explicit formal package export/acceptance command router；默认因 P7-X blocked 而 blocked，只有预检 ready 且显式确认后才允许进入具体导出或人工验收动作。

## 2026-05-28 P7-Y Auto Mode Formal Package Export / Acceptance Router

- [x] 组件效果：把 P7-X 的导出/验收预检接成显式人为路由；只有预检 ready + confirm + reviewer/note + decision 命中 plan 时，才记录下一步路由。
- [x] 当前真实效果：仓库里的 P7-X 仍是 blocked，所以本节点输出 `blocked_by_export_acceptance_preflight`，没有记录导出/验收路线。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_package_export_acceptance_router.py`，覆盖 defer、confirmed pdf route、当前 blocked、未知/缺失计划动作、缺确认/元数据、边界越界、CLI 默认 blocked、只写 report/review。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_package_export_acceptance_router`。
- [x] Agent Team：未调用；本节点是单一 router 小切片，主要风险由 ready/blocked/decision/boundary 单测和 P7 回归覆盖，拆 sidecar 不会明显提升质量或速度。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_package_export_acceptance_router.py` 和 `Program/auto_mode_formal_package_export_acceptance_router.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-package-export-acceptance-router.md`；新增审阅输出 `Reviews/auto_mode_formal_package_export_acceptance_router.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_package_export_acceptance_router.py --project-root . --export-acceptance-preflight Results/json/auto_mode_formal_package_export_acceptance_preflight.json --decision defer --output-router Results/json/auto_mode_formal_package_export_acceptance_router.json --output-review Reviews/auto_mode_formal_package_export_acceptance_router.md`。
- [x] 真实输出：`status=blocked_by_export_acceptance_preflight`、`can_route_export_or_acceptance=false`、`route_recorded=false`、`routed_action=`、`export_or_acceptance_executed=false`、`rendered_pdf=false`、`rendered_docx=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；未写 `state/product/auto_mode_formal_package_export_acceptance_router.json`，仓库已有旧 PDF/DOCX，本节点未修改它们。
- [x] 正式层边界：本节点只写 router JSON 和 Markdown；不渲染 PDF/DOCX，不生成最终包 manifest，不执行人工验收，不修复/覆盖正式成果，不写 `state/product/*`，不重跑模型。
- [x] 验证：目标测试 8 OK；P7-A/.../Y 回归 156 OK；Python 编译通过。
- [x] 下一步 P7-Z：已实现 selected route execution preflight（按 P7-Y routed_action 拆到 PDF/DOCX/package/acceptance 的具体执行预检）；默认因 P7-Y blocked 而 blocked。

## 2026-05-28 P7-Z Auto Mode Formal Package Selected Route Execution Preflight

- [x] 组件效果：把 P7-Y 已记录的人为路线拆成单条执行预检；PDF、DOCX、package manifest、manual acceptance 会分别映射到不同的后续显式执行命令。
- [x] 当前真实效果：仓库里的 P7-Y 仍是 blocked，所以本节点输出 `blocked_by_export_acceptance_router`，没有生成 selected route execution plan。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_package_selected_route_execution_preflight.py`，覆盖 PDF 路由、DOCX/package/manual 路由分流、当前 blocked、router 缺失/错误/未记录、未知/错配路线、selected plan 合约错误、边界越界、CLI 默认 blocked、只写 report/review。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_package_selected_route_execution_preflight`。
- [x] Agent Team：未调用；本节点是单一 selected-route preflight 小切片，主要风险由 ready/blocked/route-mapping/contract/boundary 单测和 P7 回归覆盖，拆 sidecar 不会明显提升质量或速度。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_package_selected_route_execution_preflight.py` 和 `Program/auto_mode_formal_package_selected_route_execution_preflight.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-package-selected-route-execution-preflight.md`；新增审阅输出 `Reviews/auto_mode_formal_package_selected_route_execution_preflight.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_package_selected_route_execution_preflight.py --project-root . --export-acceptance-router Results/json/auto_mode_formal_package_export_acceptance_router.json --output-preflight Results/json/auto_mode_formal_package_selected_route_execution_preflight.json --output-review Reviews/auto_mode_formal_package_selected_route_execution_preflight.md`。
- [x] 真实输出：`status=blocked_by_export_acceptance_router`、`can_request_selected_route_execution=false`、`requires_explicit_route_execute_command=false`、`selected_route_execution_plan=0`、`selected_route_executed=false`、`export_or_acceptance_executed=false`、`rendered_pdf=false`、`rendered_docx=false`、`package_manifest_generated=false`、`manual_acceptance_performed=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；仓库已有旧 PDF/DOCX/manifest，本节点未修改它们，未写 `state/product/auto_mode_formal_package_selected_route_execution_preflight.json`。
- [x] 正式层边界：本节点只写 selected route preflight JSON 和 Markdown；不渲染 PDF/DOCX，不生成 package manifest，不执行人工验收，不修复/覆盖正式成果，不写 `state/product/*`，不重跑模型。
- [x] 验证：目标测试 9 OK；P7-A/.../Z 回归 165 OK；Python 编译通过。
- [x] 下一步 P7-AA：已实现 selected route explicit execute gate（按 P7-Z plan 提供 dry-run/execute 门）；默认因 P7-Z blocked 而 blocked，不导出、不验收。

## 2026-05-28 P7-AA Auto Mode Formal Package Selected Route Execute Gate

- [x] 组件效果：把 P7-Z 的 selected route preflight 接成 dry-run/execute 门；ready 时 dry-run 展示将要执行的单条路线，confirmed execute 只记录 selected route execute manifest，不渲染/生成/验收最终成果。
- [x] 当前真实效果：仓库里的 P7-Z 仍是 blocked，所以本节点输出 `blocked_by_selected_route_execution_preflight`，没有生成执行操作，也没有记录 execute manifest。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_package_selected_route_execute.py`，覆盖 dry-run、四类路线映射、当前 blocked、preflight 缺失/未 ready、execute 缺确认、execute 缺 reviewer/note、plan 合约错误、confirmed execute 只写 manifest、CLI 默认 blocked。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_package_selected_route_execute`。
- [x] Agent Team：未调用；本节点是单一 execute gate 小切片，主要风险由 ready/blocked/mode/metadata/contract 单测和 P7 回归覆盖，拆 sidecar 不会明显提升质量或速度。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_package_selected_route_execute.py` 和 `Program/auto_mode_formal_package_selected_route_execute.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-package-selected-route-execute.md`；新增审阅输出 `Reviews/auto_mode_formal_package_selected_route_execute.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_package_selected_route_execute.py --project-root . --selected-route-preflight Results/json/auto_mode_formal_package_selected_route_execution_preflight.json --mode dry-run --output-execute Results/json/auto_mode_formal_package_selected_route_execute.json --output-review Reviews/auto_mode_formal_package_selected_route_execute.md --execute-manifest workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json`。
- [x] 真实输出：`status=blocked_by_selected_route_execution_preflight`、`can_execute_selected_route_with_confirmation=false`、`selected_route_execute_manifest_recorded=false`、`selected_route_execute_operations=0`、`selected_route_executed=false`、`export_or_acceptance_executed=false`、`rendered_pdf=false`、`rendered_docx=false`、`package_manifest_generated=false`、`manual_acceptance_performed=false`、`this_command_wrote_formal_state=false`、`can_write_product_state=false`；仓库已有旧 PDF/DOCX/manifest，本节点未修改它们，未写 `state/product/auto_mode_formal_package_selected_route_execute.json`。
- [x] 正式层边界：本节点只写 selected route execute JSON/Markdown；只有 ready + confirmed execute 时才写 execute manifest；不渲染 PDF/DOCX，不生成正式 package manifest，不执行人工验收，不修复/覆盖正式成果，不写 `state/product/*`，不重跑模型。
- [x] 验证：目标测试 9 OK；P7-A/.../AA 回归 174 OK；Python 编译通过。
- [x] 下一步 P7-AB：已实现 route-specific artifact executor（按 execute manifest 分别执行 PDF/DOCX/package/manual 的真实动作）；默认因 P7-AA blocked 而 blocked。

## 2026-05-28 P7-AB Auto Mode Formal Package Route-Specific Artifact Executor

- [x] 组件效果：把 P7-AA execute manifest 接成 route-specific artifact executor；ready + confirmed execute 时按 route type 分发到现有 PDF、DOCX、package manifest 或 manual acceptance 命令。
- [x] 当前真实效果：仓库里的 P7-AA 仍是 blocked 且没有 execute manifest，所以本节点输出 `blocked_by_selected_route_execute`，没有运行 delegated command，也没有写任何正式包产物。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_package_route_specific_artifact_executor.py`，覆盖 dry-run dispatch、当前 blocked、report/manifest 缺失或错误、operation 合约错误、execute 缺确认/元数据、PDF/DOCX 真实命令、package/manual 真实命令、CLI 默认 blocked。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_package_route_specific_artifact_executor`。
- [x] Agent Team：未调用；本节点是单一 selected-route dispatcher 小切片，主要风险由 manifest/contract/request/四类 delegated command 单测和 P7 回归覆盖，拆 sidecar 不会明显提升质量或速度。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_package_route_specific_artifact_executor.py` 和 `Program/auto_mode_formal_package_route_specific_artifact_executor.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-package-route-specific-artifact-executor.md`；新增审阅输出 `Reviews/auto_mode_formal_package_route_specific_artifact_executor.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_package_route_specific_artifact_executor.py --project-root . --selected-route-execute Results/json/auto_mode_formal_package_selected_route_execute.json --execute-manifest workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json --mode dry-run --output-executor Results/json/auto_mode_formal_package_route_specific_artifact_executor.json --output-review Reviews/auto_mode_formal_package_route_specific_artifact_executor.md`。
- [x] 真实输出：`status=blocked_by_selected_route_execute`、`route_specific_command_executed=false`、`route_specific_artifact_executed=false`、`delegated_status=`、`selected_route_executed=false`、`export_or_acceptance_executed=false`、`rendered_pdf=false`、`rendered_docx=false`、`package_manifest_generated=false`、`manual_acceptance_performed=false`、`can_write_product_state=false`；没有 execute manifest，未运行 delegated command，未写 `state/product/auto_mode_formal_package_route_specific_artifact_executor.json`。
- [x] 正式层边界：当前真实 blocked 不写产物；ready + confirmed execute 时只调用所选路线对应的既有命令。PDF/DOCX/package 会写各自正式包产物或 manifest；manual acceptance 会写既有人工验收 report/state；不重跑模型，不修改 DesignSpec/RunPlan/统计产物。
- [x] 验证：目标测试 8 OK；P7-A/.../AB 回归 182 OK；Python 编译通过。
- [x] 下一步 P7-AC：已实现 route-specific artifact verification gate（读取 P7-AB 和 delegated report，核验所选产物是否真正存在且指纹/状态一致）；默认因 P7-AB blocked 而 blocked。

## 2026-05-28 P7-AC Auto Mode Formal Package Route-Specific Artifact Verification

- [x] 组件效果：把 P7-AB route-specific artifact executor 接成验证门；只有 P7-AB 完成且 delegated report 与真实文件路径、bytes、sha256 一致时，才输出 route-specific artifact verified。
- [x] 当前真实效果：仓库里的 P7-AB 仍是 `blocked_by_selected_route_execute`，所以本节点输出 `blocked_by_route_specific_artifact_executor`，没有验证任何产物，也没有写 product state。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_package_route_specific_artifact_verification.py`，覆盖 PDF 指纹复验、当前 blocked、executor/delegated report 缺失或错误、executor completion contract、PDF/DOCX 路径和指纹、package manifest、manual acceptance state、CLI 默认 blocked。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_package_route_specific_artifact_verification`。
- [x] Agent Team：未调用；本节点是单一 route artifact verifier 小切片，主要风险由四类路线的 report/file/state 指纹单测和 P7 回归覆盖，拆 sidecar 不会明显提升质量或速度。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_package_route_specific_artifact_verification.py` 和 `Program/auto_mode_formal_package_route_specific_artifact_verification.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-package-route-specific-artifact-verification.md`；新增审阅输出 `Reviews/auto_mode_formal_package_route_specific_artifact_verification.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_package_route_specific_artifact_verification.py --project-root . --route-specific-artifact-executor Results/json/auto_mode_formal_package_route_specific_artifact_executor.json --output-verification Results/json/auto_mode_formal_package_route_specific_artifact_verification.json --output-review Reviews/auto_mode_formal_package_route_specific_artifact_verification.md`。
- [x] 真实输出：`status=blocked_by_route_specific_artifact_executor`、`route_type=`、`verified_route_type=`、`delegated_status=`、`route_specific_artifact_verified=false`、`selected_route_executed=false`、`export_or_acceptance_executed=false`、`can_write_product_state=false`；artifact verification records 为空，未写 `state/product/auto_mode_formal_package_route_specific_artifact_verification.json`。
- [x] 正式层边界：本节点只写 P7-AC verification JSON/Markdown；不执行 delegated command，不导出 PDF/DOCX，不生成 package manifest，不执行人工验收，不写 `state/product/*`，不修改 DesignSpec/RunPlan/统计产物。
- [x] 验证：目标测试 8 OK；P7-A/.../AC 回归 190 OK；Python 编译通过。
- [x] 下一步 P7-AD：已实现 verified route completion ledger（把通过 P7-AC 的单路线验证结果登记为可进入下一 Auto Mode gate 的只读账本）；默认因 P7-AC blocked 而 blocked。

## 2026-05-28 P7-AD Auto Mode Formal Package Verified Route Completion Ledger

- [x] 组件效果：把 P7-AC 已验证的单路线产物登记为只读完成账本；下游可以读取 `route_completion_records` 判断这条 PDF/DOCX/package/manual 路线是否能进入下一 Auto Mode gate。
- [x] 当前真实效果：仓库里的 P7-AC 仍是 `blocked_by_route_specific_artifact_executor`，所以本节点输出 `blocked_by_route_specific_artifact_verification`，没有登记完成账本，也不允许进入下一关。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_package_verified_route_completion_ledger.py`，覆盖 verified PDF route 登记、当前 blocked、schema/status 缺失、verified 报告内部矛盾、路线 flags 错配、package manifest 多 artifact 证据保留、边界越界、CLI 默认 blocked。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_package_verified_route_completion_ledger`。
- [x] Agent Team：未调用；本节点是单一只读 ledger 小切片，主要风险由 P7-AC verified/blocked/contract/boundary 单测和 P7 回归覆盖，拆 sidecar 不会明显提升质量或速度。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_package_verified_route_completion_ledger.py` 和 `Program/auto_mode_formal_package_verified_route_completion_ledger.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-package-verified-route-completion-ledger.md`；新增审阅输出 `Reviews/auto_mode_formal_package_verified_route_completion_ledger.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_package_verified_route_completion_ledger.py --project-root . --route-specific-artifact-verification Results/json/auto_mode_formal_package_route_specific_artifact_verification.json --output-ledger Results/json/auto_mode_formal_package_verified_route_completion_ledger.json --output-review Reviews/auto_mode_formal_package_verified_route_completion_ledger.md`。
- [x] 真实输出：`status=blocked_by_route_specific_artifact_verification`、`route_completion_ledger_recorded=false`、`can_enter_next_auto_mode_gate=false`、`route_completion_records=0`、`can_write_product_state=false`；未写 `state/product/auto_mode_formal_package_verified_route_completion_ledger.json`。
- [x] 正式层边界：本节点只写 P7-AD ledger JSON 和 Markdown；不执行 delegated command，不导出 PDF/DOCX，不生成 package manifest，不执行人工验收，不提升 candidate target，不写 `state/product/*`，不修改 DesignSpec/RunPlan/统计产物。
- [x] 验证：目标测试 8 OK；P7-A/.../AD 回归 198 OK；Python 编译通过；P7-AD scoped `git diff --check` 通过。
- [x] 下一步 P7-AE：已实现 verified route completion next gate router（只消费 P7-AD ledger，决定能否进入下一 Auto Mode gate）；默认因 P7-AD blocked 而 blocked。

## 2026-05-28 P7-AE Auto Mode Formal Package Verified Route Next Gate Router

- [x] 组件效果：把 P7-AD 的只读完成账本转成下一关路由记录；PDF/DOCX/package manifest 完成后回到导出/验收路由循环，manual acceptance 完成后进入正式包交付完成门。
- [x] 当前真实效果：仓库里的 P7-AD 仍是 `blocked_by_route_specific_artifact_verification`，所以本节点输出 `blocked_by_verified_route_completion_ledger`，没有记录下一关路由，也不允许进入下一关。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_package_verified_route_next_gate_router.py`，覆盖 ready PDF 路由、当前 blocked、schema/status 缺失、completion record 合约、未知 route type、manual acceptance 终态路由、边界越界、CLI 默认 blocked。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_package_verified_route_next_gate_router`。
- [x] Agent Team：未调用；本节点是单一只读 router 小切片，主要风险由 P7-AD ready/blocked/contract/boundary 单测和 P7 回归覆盖，拆 sidecar 不会明显提升质量或速度。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_package_verified_route_next_gate_router.py` 和 `Program/auto_mode_formal_package_verified_route_next_gate_router.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-package-verified-route-next-gate-router.md`；新增审阅输出 `Reviews/auto_mode_formal_package_verified_route_next_gate_router.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_package_verified_route_next_gate_router.py --project-root . --verified-route-completion-ledger Results/json/auto_mode_formal_package_verified_route_completion_ledger.json --output-router Results/json/auto_mode_formal_package_verified_route_next_gate_router.json --output-review Reviews/auto_mode_formal_package_verified_route_next_gate_router.md`。
- [x] 真实输出：`status=blocked_by_verified_route_completion_ledger`、`next_gate_route_recorded=false`、`can_enter_routed_next_gate=false`、`routed_next_gate=`、`can_write_product_state=false`；未写 `state/product/auto_mode_formal_package_verified_route_next_gate_router.json`。
- [x] 正式层边界：本节点只写 P7-AE router JSON 和 Markdown；不进入下一关，不执行 delegated command，不导出 PDF/DOCX，不生成 package manifest，不执行人工验收，不写 `state/product/*`，不修改 DesignSpec/RunPlan/统计产物。
- [x] 验证：目标测试 8 OK；P7-A/.../AE 回归 206 OK；Python 编译通过；P7-AE scoped `git diff --check` 通过。
- [x] 下一步 P7-AF：已实现 routed next gate entry preflight（只消费 P7-AE router，ready 时生成下一关进入计划）；默认因 P7-AE blocked 而 blocked。

## 2026-05-28 P7-AF Auto Mode Formal Package Routed Next Gate Entry Preflight

- [x] 组件效果：把 P7-AE 的“下一关路由”转成可对接的“下一关进入预检计划”；如果 P7-AE ready，会告诉后续命令该进入 `auto_mode_formal_package_export_acceptance_router` 还是 `auto_mode_formal_package_delivery_completion_gate`。
- [x] 当前真实效果：仓库里的 P7-AE 仍是 `blocked_by_verified_route_completion_ledger`，所以本节点输出 `blocked_by_verified_route_next_gate_router`，没有生成进入计划，也不允许进入下一关。
- [x] 对接方式：下游只需要读取 `Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json`；只有 `can_request_routed_next_gate_entry=true` 且 `next_gate_entry_plan` 非空时，才允许进入下一关命令。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_package_routed_next_gate_entry_preflight.py`，覆盖 ready PDF 进入计划、当前 blocked、schema/status 缺失、route 合约、未知 gate/action、manual acceptance 终态、边界越界、CLI 默认 blocked。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_package_routed_next_gate_entry_preflight`。
- [x] Agent Team：未调用；本节点是单一只读 preflight 小切片，主要风险由 ready/blocked/contract/boundary 单测和 P7 主链路回归覆盖。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_package_routed_next_gate_entry_preflight.py` 和 `Program/auto_mode_formal_package_routed_next_gate_entry_preflight.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-package-routed-next-gate-entry-preflight.md`；新增审阅输出 `Reviews/auto_mode_formal_package_routed_next_gate_entry_preflight.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_package_routed_next_gate_entry_preflight.py --project-root . --verified-route-next-gate-router Results/json/auto_mode_formal_package_verified_route_next_gate_router.json --output-preflight Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json --output-review Reviews/auto_mode_formal_package_routed_next_gate_entry_preflight.md`。
- [x] 真实输出：`status=blocked_by_verified_route_next_gate_router`、`can_request_routed_next_gate_entry=false`、`next_gate_entry_plan=0`、`routed_next_gate=`、`can_write_product_state=false`；未写 `state/product/auto_mode_formal_package_routed_next_gate_entry_preflight.json`。
- [x] 正式层边界：本节点只写 P7-AF preflight JSON 和 Markdown；不进入下一关，不执行 delegated command，不导出 PDF/DOCX，不生成 package manifest，不执行人工验收，不写 `state/product/*`，不修改 DesignSpec/RunPlan/统计产物。
- [x] 验证：目标测试 8 OK；P7-A/.../AF 回归 214 OK；Python 编译通过。
- [x] 下一步 P7-AG：已实现 explicit routed next gate entry execute gate（只消费 P7-AF preflight，ready 且显式确认后才记录进入下一关 manifest）；默认因 P7-AF blocked 而 blocked。

## 2026-05-28 P7-AG Auto Mode Formal Package Routed Next Gate Entry Execute

- [x] 组件效果：把 P7-AF 的“下一关进入预检计划”转成显式 entry execute gate；dry-run 可预览下一关入口，execute 模式必须带 `confirm-entry`、reviewer 和 note 才写 entry manifest。
- [x] 当前真实效果：仓库里的 P7-AF 仍是 `blocked_by_verified_route_next_gate_router`，所以本节点输出 `blocked_by_routed_next_gate_entry_preflight`，entry operation 为 0，没有写 entry manifest，也没有进入下一关。
- [x] 对接方式：下游只消费 `workspace/formal_package_routed_next_gate_entry/auto_mode/routed_next_gate_entry_manifest.json`；只有 `routed_next_gate_entry_manifest_recorded=true` 时，才允许后续节点读取 manifest 并决定是否运行下一关命令。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_package_routed_next_gate_entry_execute.py`，覆盖 ready PDF dry-run、当前 blocked、schema/status 缺失、execute 确认、reviewer/note 元数据、entry plan 合约、manual acceptance manifest、CLI 默认 blocked。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_package_routed_next_gate_entry_execute`。
- [x] Agent Team：未调用；本节点是单一只读/manifest gate 小切片，主要风险由 ready/blocked/contract/metadata/manifest 单测和 P7 主链路回归覆盖。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_package_routed_next_gate_entry_execute.py` 和 `Program/auto_mode_formal_package_routed_next_gate_entry_execute.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-package-routed-next-gate-entry-execute.md`；新增审阅输出 `Reviews/auto_mode_formal_package_routed_next_gate_entry_execute.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_package_routed_next_gate_entry_execute.py --project-root . --routed-next-gate-entry-preflight Results/json/auto_mode_formal_package_routed_next_gate_entry_preflight.json --output-execute Results/json/auto_mode_formal_package_routed_next_gate_entry_execute.json --output-review Reviews/auto_mode_formal_package_routed_next_gate_entry_execute.md --entry-manifest workspace/formal_package_routed_next_gate_entry/auto_mode/routed_next_gate_entry_manifest.json`。
- [x] 真实输出：`status=blocked_by_routed_next_gate_entry_preflight`、`can_enter_routed_next_gate_with_confirmation=false`、`routed_next_gate_entry_manifest_recorded=false`、`routed_next_gate_entry_operations=0`、`next_gate_entered=false`、`can_write_product_state=false`；未写 entry manifest，未写 `state/product/auto_mode_formal_package_routed_next_gate_entry_execute.json`。
- [x] 正式层边界：本节点只写 P7-AG execute JSON 和 Markdown；只有 ready+确认时写 workspace entry manifest；不运行下一关命令，不导出 PDF/DOCX，不生成 package manifest，不执行人工验收，不写 `state/product/*`，不修改 DesignSpec/RunPlan/统计产物。
- [x] 验证：目标测试 8 OK；P7-A/.../AG 回归 222 OK；Python 编译通过。
- [x] 下一步 P7-AH：已实现 manifested routed next gate command preflight（只消费 P7-AG entry manifest，生成下一关命令调用计划）；默认因 P7-AG blocked 而 blocked。

## 2026-05-28 P7-AH Auto Mode Formal Package Manifested Routed Next Gate Command Preflight

- [x] 组件效果：把 P7-AG 的 entry manifest 转成“下一关命令调用计划”；如果输入 manifest 是 ready，就能明确下游该调用 export/acceptance router 还是 delivery completion gate。
- [x] 当前真实效果：仓库里没有 `workspace/formal_package_routed_next_gate_entry/auto_mode/routed_next_gate_entry_manifest.json`，所以本节点输出 `blocked_by_routed_next_gate_entry_manifest`，命令计划数为 0，不允许运行下一关命令。
- [x] 对接方式：下游只读取 `Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.json`；只有 `can_request_manifested_next_gate_command_execution=true` 且 `next_gate_command_call_plan` 非空时，后续 execute gate 才能运行计划中的命令。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_package_manifested_routed_next_gate_command_preflight.py`，覆盖 ready PDF 命令计划、当前 missing manifest 阻断、invalid/unmanifested 阻断、边界越界阻断、operation contract、manual acceptance 路由、只写 report/review、CLI 默认 blocked。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_package_manifested_routed_next_gate_command_preflight`。
- [x] Agent Team：未调用；本节点是单一 manifest-consumer preflight 小切片，主要风险由 ready/blocked/contract/boundary 单测和 P7 主链路回归覆盖。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.py` 和 `Program/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-package-manifested-routed-next-gate-command-preflight.md`；新增审阅输出 `Reviews/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.py --project-root . --routed-next-gate-entry-manifest workspace/formal_package_routed_next_gate_entry/auto_mode/routed_next_gate_entry_manifest.json --output-preflight Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.json --output-review Reviews/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.md`。
- [x] 真实输出：`status=blocked_by_routed_next_gate_entry_manifest`、`can_request_manifested_next_gate_command_execution=false`、`next_gate_command_call_plan=0`、`next_gate_command_executed=false`、`can_write_product_state=false`；未创建 `workspace/formal_package_routed_next_gate_command`，未写 `state/product/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.json`。
- [x] 正式层边界：本节点只写 P7-AH preflight JSON 和 Markdown；不运行下一关命令，不进入下一关，不导出 PDF/DOCX，不生成 package manifest，不执行人工验收，不写 `state/product/*`，不修改 DesignSpec/RunPlan/统计产物。
- [x] 验证：目标测试 8 OK；P7-A/.../AH 回归 230 OK；Python 编译通过。
- [x] 下一步 P7-AI：已实现 manifested routed next gate command execute gate（只消费 P7-AH command preflight，ready 且显式确认后才运行下一关命令）；默认因 P7-AH blocked 而 blocked。

## 2026-05-28 P7-AI Auto Mode Formal Package Manifested Routed Next Gate Command Execute

- [x] 组件效果：把 P7-AH 的“下一关命令计划”转成真正的 execute gate；`dry-run` 只展示 delegated command，`execute` 必须显式确认、reviewer 和 note 才会调用下游 CLI。
- [x] 当前真实效果：仓库里的 P7-AH 仍是 `blocked_by_routed_next_gate_entry_manifest`，所以本节点输出 `blocked_by_manifested_routed_next_gate_command_preflight`，delegated command 为 0，没有运行任何下一关命令。
- [x] 对接方式：下游只读取 `Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_execute.json`；只有 `status=manifested_next_gate_command_executed` 且 `next_gate_command_executed=true` 时，才允许继续审阅 delegated next-gate 输出。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_package_manifested_routed_next_gate_command_execute.py`，覆盖 ready PDF dry-run、当前 blocked、invalid/not-ready preflight、命令计划合约、execute 确认和元数据、confirmed PDF delegated command、缺失下游命令文件、CLI 默认 blocked。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_package_manifested_routed_next_gate_command_execute`。
- [x] Agent Team：未调用；本节点是单一 command execute gate 小切片，主要风险由 ready/blocked/confirmed execute/unavailable command 单测和 P7 主链路回归覆盖。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_package_manifested_routed_next_gate_command_execute.py` 和 `Program/auto_mode_formal_package_manifested_routed_next_gate_command_execute.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-package-manifested-routed-next-gate-command-execute.md`；新增审阅输出 `Reviews/auto_mode_formal_package_manifested_routed_next_gate_command_execute.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_package_manifested_routed_next_gate_command_execute.py --project-root . --manifested-routed-next-gate-command-preflight Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_preflight.json --mode dry-run --output-execute Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_execute.json --output-review Reviews/auto_mode_formal_package_manifested_routed_next_gate_command_execute.md`。
- [x] 真实输出：`status=blocked_by_manifested_routed_next_gate_command_preflight`、`can_execute_manifested_next_gate_command_with_confirmation=false`、`delegated_command=0`、`next_gate_command_executed=false`、`this_command_ran_next_gate_command=false`、`can_write_product_state=false`；未写 `state/product/auto_mode_formal_package_manifested_routed_next_gate_command_execute.json`。
- [x] 正式层边界：本节点只写 P7-AI execute JSON 和 Markdown；只有 ready+确认时才运行 delegated next-gate command；当前真实运行不运行下游命令、不进入下一关、不导出 PDF/DOCX、不生成 package manifest、不执行人工验收、不写 `state/product/*`。
- [x] 验证：目标测试 8 OK；P7-A/.../AI 回归 238 OK；Python 编译通过。
- [x] 下一步 P7-AJ：已实现 manifested next-gate command result review（只消费 P7-AI execute report，审阅 delegated next-gate 输出是否可继续）；默认因 P7-AI blocked 而 blocked。

## 2026-05-28 P7-AJ Auto Mode Formal Package Manifested Next Gate Command Result Review

- [x] 组件效果：把 P7-AI 的 execute report 和 delegated next-gate report 转成可审阅的结果判断；只有 delegated schema、status、path contract 都匹配时才允许继续。
- [x] 当前真实效果：仓库里的 P7-AI 仍是 `blocked_by_manifested_routed_next_gate_command_preflight`，所以本节点输出 `blocked_by_manifested_next_gate_command_execute`，delegated result record 为 0，不能继续。
- [x] 对接方式：下游只读取 `Results/json/auto_mode_formal_package_manifested_next_gate_command_result_review.json`；只有 `can_continue_after_delegated_next_gate=true` 且 `delegated_next_gate_result_reviewed=true` 时，才允许继续后续 next-gate workflow。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_package_manifested_next_gate_command_result_review.py`，覆盖已执行 PDF delegated 输出 ready、当前 P7-AI blocked、execute report 缺失/未完成、route/report/status contract、delegated report schema/status/blocker、只写 result review、CLI 默认 blocked。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_package_manifested_next_gate_command_result_review`。
- [x] Agent Team：未调用；本节点是单一 result review 小切片，主要风险由 execute/contract/delegated report 单测和 P7 主链路回归覆盖。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_package_manifested_next_gate_command_result_review.py` 和 `Program/auto_mode_formal_package_manifested_next_gate_command_result_review.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-package-manifested-next-gate-command-result-review.md`；新增审阅输出 `Reviews/auto_mode_formal_package_manifested_next_gate_command_result_review.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_package_manifested_next_gate_command_result_review.py --project-root . --manifested-next-gate-command-execute Results/json/auto_mode_formal_package_manifested_routed_next_gate_command_execute.json --output-result-review Results/json/auto_mode_formal_package_manifested_next_gate_command_result_review.json --output-review Reviews/auto_mode_formal_package_manifested_next_gate_command_result_review.md`。
- [x] 真实输出：`status=blocked_by_manifested_next_gate_command_execute`、`can_continue_after_delegated_next_gate=false`、`delegated_result_records=0`、`next_gate_command_executed=false`、`this_command_ran_next_gate_command=false`、`can_write_product_state=false`；未写 `state/product/auto_mode_formal_package_manifested_next_gate_command_result_review.json`。
- [x] 正式层边界：本节点只写 P7-AJ result review JSON 和 Markdown；不运行 delegated command、不进入下一关、不导出 PDF/DOCX、不生成 package manifest、不执行人工验收、不写 `state/product/*`。
- [x] 验证：目标测试 7 OK；P7-A/.../AJ 回归 245 OK；Python 编译通过。
- [x] 下一步 P7-AK：已实现 next-gate workflow continuation preflight（只消费 P7-AJ result review，ready 时生成后续工作流 continuation plan）；默认因 P7-AJ blocked 而 blocked。

## 2026-05-28 P7-AK Auto Mode Formal Package Next Gate Workflow Continuation Preflight

- [x] 组件效果：把 P7-AJ 的“delegated 结果已审阅且可继续”转成后续 workflow continuation plan；ready 时会指向 `auto_mode_formal_package_selected_route_execution_preflight`，但本节点不运行它。
- [x] 当前真实效果：仓库里的 P7-AJ 仍是 `blocked_by_manifested_next_gate_command_execute`，所以本节点输出 `blocked_by_manifested_next_gate_command_result_review`，continuation plan 为 0，不能继续。
- [x] 对接方式：下游只读取 `Results/json/auto_mode_formal_package_next_gate_workflow_continuation_preflight.json`；只有 `can_request_next_gate_workflow_continuation=true` 且 `workflow_continuation_plan` 非空时，才允许后续命令进入 selected route execution preflight。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_package_next_gate_workflow_continuation_preflight.py`，覆盖已审阅 export router 输出生成 continuation plan、当前 P7-AJ blocked、P7-AJ 缺失/无效/未 ready、delegated result record 合约、未知 gate/route、只写 report/review、CLI 默认 blocked。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_package_next_gate_workflow_continuation_preflight`。
- [x] Agent Team：未调用；本节点是单一 continuation preflight 小切片，主要风险由 result-review/contract/blocked 单测和 P7 主链路回归覆盖。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_package_next_gate_workflow_continuation_preflight.py` 和 `Program/auto_mode_formal_package_next_gate_workflow_continuation_preflight.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-package-next-gate-workflow-continuation-preflight.md`；新增审阅输出 `Reviews/auto_mode_formal_package_next_gate_workflow_continuation_preflight.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_package_next_gate_workflow_continuation_preflight.py --project-root . --manifested-next-gate-command-result-review Results/json/auto_mode_formal_package_manifested_next_gate_command_result_review.json --output-preflight Results/json/auto_mode_formal_package_next_gate_workflow_continuation_preflight.json --output-review Reviews/auto_mode_formal_package_next_gate_workflow_continuation_preflight.md`。
- [x] 真实输出：`status=blocked_by_manifested_next_gate_command_result_review`、`can_request_next_gate_workflow_continuation=false`、`requires_explicit_workflow_continuation_command=false`、`workflow_continuation_plan=0`、`workflow_continuation_executed=false`、`this_command_ran_continuation=false`、`can_write_product_state=false`；未写 `state/product/auto_mode_formal_package_next_gate_workflow_continuation_preflight.json`。
- [x] 正式层边界：本节点只写 P7-AK continuation preflight JSON 和 Markdown；不运行 continuation command、不执行 selected route preflight、不导出 PDF/DOCX、不生成 package manifest、不执行人工验收、不写 `state/product/*`。
- [x] 验证：目标测试 7 OK；P7-A/.../AK 回归 252 OK；Python 编译通过。
- [x] 下一步 P7-AL：已实现 next-gate workflow continuation execute gate（只消费 P7-AK preflight，ready 且显式确认后才运行 continuation command）；默认因 P7-AK blocked 而 blocked。

## 2026-05-28 P7-AL Auto Mode Formal Package Next Gate Workflow Continuation Execute

- [x] 组件效果：把 P7-AK continuation preflight 转成显式 execute gate；dry-run 只展示 continuation command，execute 必须显式确认、reviewer 和 note 才运行 selected route execution preflight。
- [x] 当前真实效果：仓库里的 P7-AK 仍是 `blocked_by_manifested_next_gate_command_result_review`，所以本节点输出 `blocked_by_next_gate_workflow_continuation_preflight`，continuation command 为 0，没有运行后续 preflight。
- [x] 对接方式：下游只读取 `Results/json/auto_mode_formal_package_next_gate_workflow_continuation_execute.json`；只有 `status=next_gate_workflow_continuation_executed` 且 `workflow_continuation_executed=true` 时，才允许审阅 selected route execution preflight 输出。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_package_next_gate_workflow_continuation_execute.py`，覆盖 ready dry-run、当前 blocked、P7-AK 缺失/无效/未 ready、continuation plan 合约、execute 确认和元数据、confirmed continuation preflight、缺失 continuation command 文件、CLI 默认 blocked。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_package_next_gate_workflow_continuation_execute`。
- [x] Agent Team：未调用；本节点是单一 continuation execute gate 小切片，主要风险由 dry-run/blocked/confirmed execute/command unavailable 单测和 P7 主链路回归覆盖。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_package_next_gate_workflow_continuation_execute.py` 和 `Program/auto_mode_formal_package_next_gate_workflow_continuation_execute.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-package-next-gate-workflow-continuation-execute.md`；新增审阅输出 `Reviews/auto_mode_formal_package_next_gate_workflow_continuation_execute.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_package_next_gate_workflow_continuation_execute.py --project-root . --next-gate-workflow-continuation-preflight Results/json/auto_mode_formal_package_next_gate_workflow_continuation_preflight.json --mode dry-run --output-execute Results/json/auto_mode_formal_package_next_gate_workflow_continuation_execute.json --output-review Reviews/auto_mode_formal_package_next_gate_workflow_continuation_execute.md`。
- [x] 真实输出：`status=blocked_by_next_gate_workflow_continuation_preflight`、`continuation_command=0`、`workflow_continuation_executed=false`、`this_command_ran_continuation=false`、`selected_route_executed=false`、`export_or_acceptance_executed=false`、`can_write_product_state=false`；未写 `state/product/auto_mode_formal_package_next_gate_workflow_continuation_execute.json`。
- [x] 正式层边界：本节点只写 P7-AL execute JSON 和 Markdown；只有 ready+确认时才运行 selected route execution preflight；当前真实运行不运行 continuation、不导出 PDF/DOCX、不生成 package manifest、不执行人工验收、不写 `state/product/*`。
- [x] 验证：目标测试 8 OK；P7-A/.../AL 回归 260 OK；Python 编译通过。
- [x] 下一步 P7-AM：已实现 continuation result review（只消费 P7-AL execute report，审阅 selected route execution preflight 输出是否可继续）；默认因 P7-AL blocked 而 blocked。

## 2026-05-28 P7-AM Auto Mode Formal Package Next Gate Workflow Continuation Result Review

- [x] 组件效果：把 P7-AL continuation execute report 和 selected route execution preflight 转成只读结果审阅；只有 continuation 已真实执行、preflight ready、路径/状态/计划合约都匹配时，才允许继续到 selected route execute。
- [x] 当前真实效果：仓库里的 P7-AL 仍是 `blocked_by_next_gate_workflow_continuation_preflight`，所以本节点输出 `blocked_by_next_gate_workflow_continuation_execute`，selected route preflight records 为 0，不能继续执行路线。
- [x] 对接方式：下游只读取 `Results/json/auto_mode_formal_package_next_gate_workflow_continuation_result_review.json`；只有 `status=next_gate_workflow_continuation_result_review_ready` 且 `can_continue_to_selected_route_execution=true` 时，才允许进入后续 explicit selected route execute。
- [x] BDD/TDD：新增 `tests/test_auto_mode_formal_package_next_gate_workflow_continuation_result_review.py`，覆盖 ready continuation result、当前 blocked、P7-AL 缺失/无效/未完成、continuation result contract、selected route preflight clean gate、只写 result review、CLI 默认 blocked。
- [x] RED 记录：首次目标测试失败为缺少 `Program.workbench.auto_mode_formal_package_next_gate_workflow_continuation_result_review`。
- [x] Agent Team：未调用；本节点是单一 continuation result review 小切片，主要风险由 execute/result/preflight contract 单测和 P7 主链路回归覆盖。
- [x] 实现范围：新增 `Program/workbench/auto_mode_formal_package_next_gate_workflow_continuation_result_review.py` 和 `Program/auto_mode_formal_package_next_gate_workflow_continuation_result_review.py`；新增计划 `docs/superpowers/plans/2026-05-28-auto-mode-formal-package-next-gate-workflow-continuation-result-review.md`；新增审阅输出 `Reviews/auto_mode_formal_package_next_gate_workflow_continuation_result_review.md`。
- [x] 真实运行：`python3 Program/auto_mode_formal_package_next_gate_workflow_continuation_result_review.py --project-root . --next-gate-workflow-continuation-execute Results/json/auto_mode_formal_package_next_gate_workflow_continuation_execute.json --output-result-review Results/json/auto_mode_formal_package_next_gate_workflow_continuation_result_review.json --output-review Reviews/auto_mode_formal_package_next_gate_workflow_continuation_result_review.md`。
- [x] 真实输出：`status=blocked_by_next_gate_workflow_continuation_execute`、`workflow_continuation_result_reviewed=false`、`can_continue_to_selected_route_execution=false`、`selected_route_execution_preflight_records=0`、`workflow_continuation_executed=false`、`selected_route_executed=false`、`export_or_acceptance_executed=false`、`can_write_product_state=false`；未写 `state/product/auto_mode_formal_package_next_gate_workflow_continuation_result_review.json`。
- [x] 正式层边界：本节点只写 P7-AM result review JSON 和 Markdown；不运行 continuation、不执行 selected route、不导出 PDF/DOCX、不生成 package manifest、不执行人工验收、不写 `state/product/*`。
- [x] 验证：目标测试 7 OK；P7-A/.../AM 回归 267 OK；Python 编译通过。
- [ ] 下一步 P7-AN：实现 selected route execute gate（只消费 P7-AM result review，ready 且显式确认后才执行 selected route command）；默认因 P7-AM blocked 而 blocked。

## 2026-05-27 Global Node Execution Contract

- [x] 小节点时间上限：P4/P5/P6 以及后续所有形如 `P*-A/B/C/D`、`P*-G1/G2/H1/H2` 的小节点，单节点最多 20 分钟。
- [x] 超时处理：任何小节点超过 20 分钟，不继续硬拖；必须立即拆成更小节点，或判定当前路线错误并回退调整。
- [x] 质量边界：20 分钟限制不是降低质量，而是强制把任务拆到可验证粒度；每个节点必须有明确输入、输出、验证命令和是否写正式层的边界。
- [x] Agent Team 规则：节点开始前判断是否有可并行的调研、只读复核、测试定位或审计任务；能提高质量或速度时必须派出 Agent Team，回收后由主 Agent 集成和验证。
- [x] 记录规则：每个节点完成后在本文件记录实际产物、验证结果、Agent Team 调用/回收点和下一节点；不能只在聊天里说明。

## 2026-05-27 P6-I7 CGSS Literature Seed Package

- [x] 节点目标：为“社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析”生成可审阅文献综述种子包，先补齐理论、测量、CGSS 场景、中文文献队列和有序因变量方法支持。
- [x] BDD/TDD：新增 `tests/test_cgss_literature_seed_package.py`，先确认缺少 `Program.workbench.cgss_literature_seed_package` 的 RED，再实现最小核心模块和 CLI。
- [x] Agent Team 调用：Literature sidecar 调研 CGSS 官方说明、社会资本经典理论、主观幸福感测量、中文 CGSS 文献和 ordered outcome 方法；Explorer sidecar 只读定位现有 `literature_package`、CNKI 人工队列、paper quality 和 AER proposal 接入点。
- [x] 实现范围：新增 `Program/workbench/cgss_literature_seed_package.py` 和 `Program/cgss_literature_seed_package.py`；生成 10 条种子文献、变量支持、机制地图、方法支持、CNKI 人工检索队列和后续任务。
- [x] 真实运行：写出 `Results/json/cgss_social_capital_happiness_literature_seed_package.json` 和 `Reviews/cgss_social_capital_happiness_literature_seed_package.md`；状态为 `needs_human_literature_review`。
- [x] 正式层边界：本节点不修改正式 bibliography、正式 manuscript、正式 variable roles、DesignSpec、RunPlan 或 `state/product/*`。
- [x] P6-I8 BDD/TDD：新增 `tests/test_cgss_literature_source_verification_preflight.py`，先确认缺少来源校验预检模块的 RED，再实现最小 CLI。
- [x] P6-I8 实现：新增 `Program/workbench/cgss_literature_source_verification_preflight.py` 和 `Program/cgss_literature_source_verification_preflight.py`，把 10 条 seed sources 转成 candidate bibliography、CNKI 队列、Zotero/Scholar 队列和引用绑定目标。
- [x] P6-I8 真实运行：写出 `Results/json/cgss_social_capital_happiness_literature_source_verification_preflight.json` 和 `Reviews/cgss_social_capital_happiness_literature_source_verification_preflight.md`；状态为 `needs_source_verification`。
- [x] P6-I8 正式层边界：本节点不写 `verified_bibliography.csv`、不写 contribution matrix、不写正式 manuscript、不写 `state/product/*`。
- [x] P6-I9 BDD/TDD：新增 `tests/test_cgss_verified_bibliography_candidates.py`，先确认缺少 `Program.workbench.cgss_verified_bibliography_candidates` 的 RED，再实现候选参考文献和引用绑定模块。
- [x] P6-I9 实现：新增 `Program/workbench/cgss_verified_bibliography_candidates.py` 和 `Program/cgss_verified_bibliography_candidates.py`，把来源预检推进为 7 条可审阅参考文献候选、3 条人工/数据库辅助核验队列和 7 条引用绑定候选。
- [x] P6-I9 真实运行：写出 `Results/json/cgss_social_capital_happiness_verified_bibliography_candidates.json` 和 `Reviews/cgss_social_capital_happiness_verified_bibliography_candidates.md`；状态为 `needs_human_bibliography_approval`。
- [x] P6-I9 正式层边界：本节点不写 `verified_bibliography.csv`、不写 contribution matrix、不写正式 manuscript、不写 `state/product/*`。
- [x] P6-I10 BDD/TDD：新增 `tests/test_cgss_literature_review_draft_packet.py`，先确认缺少 `Program.workbench.cgss_literature_review_draft_packet` 的 RED，再实现待批准文献综述草稿包。
- [x] P6-I10 实现：新增 `Program/workbench/cgss_literature_review_draft_packet.py` 和 `Program/cgss_literature_review_draft_packet.py`，生成理论基础、变量测量、中国经验和方法衔接 4 个综述段落块。
- [x] P6-I10 真实运行：写出 `Results/json/cgss_social_capital_happiness_literature_review_draft_packet.json` 和 `Reviews/cgss_social_capital_happiness_literature_review_draft_packet.md`；状态为 `needs_human_literature_review_draft_approval`。
- [x] P6-I10 正式层边界：本节点不写 `Manuscripts/sections/literature-and-contribution.md`、不写正式参考文献、不写 `state/product/*`。
- [x] P6-I11 BDD/TDD：新增 `tests/test_cgss_method_structure_gate_packet.py`，先确认缺少 `Program.workbench.cgss_method_structure_gate_packet` 的 RED，再实现方法规范和论文结构门禁包。
- [x] P6-I11 实现：新增 `Program/workbench/cgss_method_structure_gate_packet.py` 和 `Program/cgss_method_structure_gate_packet.py`，把 OLS/Ordered Logit 结果、方法边界、DID/IV/RDD/PSM/DML 暂不进入条件和章节长度标准统一成审阅文件。
- [x] P6-I11 真实运行：写出 `Results/json/cgss_social_capital_happiness_method_structure_gate_packet.json` 和 `Reviews/cgss_social_capital_happiness_method_structure_gate_packet.md`；状态为 `needs_human_method_structure_approval`。
- [x] P6-I11 正式层边界：本节点不写正式 manuscript、不写 DesignSpec/RunPlan、不写 `state/product/*`。
- [x] P6-I12 BDD/TDD：新增 `tests/test_cgss_revision_task_queue.py`，先确认缺少 `Program.workbench.cgss_revision_task_queue` 的 RED，再实现审稿式修订任务队列。
- [x] P6-I12 实现：新增 `Program/workbench/cgss_revision_task_queue.py` 和 `Program/cgss_revision_task_queue.py`，把文献种子包、文献综述草稿包和方法结构门禁包转成 LiteratureAgent / MethodAgent / WriterAgent / ReviewerAgent 四类草案层任务。
- [x] P6-I12 正式层边界：本节点不写正式 manuscript、不写 verified bibliography、不写 DesignSpec/RunPlan、不写 `state/product/*`、不写 `state/product/agent_task_queue.json`。
- [x] P6-I12 真实运行：写出 `Results/json/cgss_social_capital_happiness_revision_task_queue.json` 和 `Reviews/cgss_social_capital_happiness_revision_task_queue.md`；schema 为 `p6.cgss_revision_task_queue.v1`，状态为 `needs_human_revision_queue_approval`，共 8 条草案层任务；不写 `state/product/agent_task_queue.json`。
- [x] P6-I13 BDD/TDD：新增 `tests/test_cgss_revision_work_orders.py`，先确认缺少 `Program.workbench.cgss_revision_work_orders` 的 RED，再实现批准门和队列到工单 adapter。
- [x] P6-I13 实现：新增 `Program/workbench/cgss_revision_work_orders.py` 和 `Program/cgss_revision_work_orders.py`；只有 queue 带有 `human_approval.status=approved`、`decision=human_approve_cgss_revision_task_queue` 且状态为 `approved_for_agent_work_orders` 时，才把 `task_id/output_target` 映射成草案工单。
- [x] P6-I13 真实运行：当前真实队列输出 `status=blocked_revision_queue_not_approved`、`work_orders=0`、`written_work_orders=0`，写出 `Results/json/cgss_social_capital_happiness_revision_work_orders.json` 与 `Reviews/cgss_social_capital_happiness_revision_work_orders.md`；没有创建 `Reviews/agent_packets/...` 工单文件。
- [x] P6-I13 正式层边界：本节点不写正式 manuscript、不写 DesignSpec/RunPlan、不写 `state/product/*`、不写 `state/product/agent_task_queue.json`；未批准时硬阻断，而不是只靠文案提醒。
- [x] P6-I13 验证：目标队列/工单测试 12 OK；P6-I CGSS 链路回归 48 OK；Python 编译通过；真实 CLI 运行通过。
- [x] P6-I14 Agent Team：尝试派发只读 verifier 复核 approval sidecar 设计，当前环境返回 `agent thread limit reached`；主 Agent 按 P6-I13 已确认的硬门禁继续实现，不等待空转。
- [x] P6-I14 BDD/TDD：新增 `tests/test_cgss_revision_queue_approval.py`，先确认缺少 `Program.workbench.cgss_revision_queue_approval` 的 RED，再实现人工决策记录模块。
- [x] P6-I14 实现：新增 `Program/workbench/cgss_revision_queue_approval.py` 和 `Program/cgss_revision_queue_approval.py`；支持 `defer/approve/revise/reject`，其中 `approve` 必须带 reviewer 和 note，才生成 `Results/json/cgss_social_capital_happiness_revision_task_queue_approved.json`。
- [x] P6-I14 真实运行：默认 `defer` 写出 `Results/json/cgss_social_capital_happiness_revision_queue_approval.json` 与 `Reviews/cgss_social_capital_happiness_revision_queue_approval.md`；状态为 `pending_human_revision_queue_decision`，未生成 approved queue。
- [x] P6-I14 验证：approval/queue/work-order 目标测试 17 OK；P6-I CGSS 链路回归 53 OK；Python 编译通过；真实 CLI 运行通过。
- [x] P6-I15 Agent Team：派发 Hume 负责审批路由器实现；主 Agent 回收后补齐机器可读 router JSON、复核正式层边界并运行回归验证。
- [x] P6-I15 BDD/TDD：新增 `tests/test_cgss_revision_approval_router.py`，覆盖 `defer/revise/reject/approve` 四种人工决策路由；未批准时不写 Agent 工单，批准且存在 approved queue 时才展开草案层工单。
- [x] P6-I15 实现：新增 `Program/workbench/cgss_revision_approval_router.py` 和 `Program/cgss_revision_approval_router.py`；默认读取 `Results/json/cgss_social_capital_happiness_revision_queue_approval.json`，写出 router JSON 与审阅 Markdown。
- [x] P6-I15 真实运行：当前真实 approval 为 `decision=defer`，路由状态为 `waiting_for_human_revision_queue_decision`，`work_orders=0`，不写 `Reviews/agent_packets/...`、不写正式 manuscript、不写 `state/product/*`。
- [ ] 下一步 P6-I16：若用户明确 `approve`，用 approved queue 进入 Agent 草案工单执行；若选择 `revise/reject`，先修订或重建任务队列，不展开工单。
- [x] P6-J1 BDD/TDD：扩展 `tests/test_topic_to_paper_capability_audit.py`，要求新 CGSS 题目输出人话版验收目标、五类缺口矩阵和 Agent Team 路由；先确认缺少 `paper_package_acceptance_target` 的 RED，再实现。
- [x] P6-J1 实现：扩展 `Program/workbench/topic_to_paper_capability_audit.py`，新增 `plain_language_summary`、`paper_package_acceptance_target`、`capability_gap_matrix` 和 `agent_team_routing`；新题目只返回 CGSS 接入任务，不混入旧 CFPS/机器人论文修订项。
- [x] P6-J1 真实运行：用“社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析”生成 `Results/json/topic_to_paper_capability_audit.json` 和 `Reviews/topic_to_paper_capability_audit.md`；状态为 `new_topic_requires_data_binding`，第一调用 Agent 为 DataAgent。
- [x] P6-J1 正式层边界：本节点只写审阅报告和 JSON audit，不生成新论文、不改写正式 package、不接受 package、不改写 `state/product/*`。
- [x] P6-J2 Agent Team：派发 Archimedes 只读定位现有 CGSS metadata / dataset binding 复用点；回收结论为优先复用 `cgss_topic_variable_discovery.py` 的 `.dta` metadata 读取和候选变量分类，不重造大数据读取链路。
- [x] P6-J2 BDD/TDD：新增 `tests/test_cgss_data_discovery.py`，先确认缺少 `Program.workbench.cgss_data_discovery` 的 RED，再实现 DatasetBinding 草案模块和 CLI。
- [x] P6-J2 实现：新增 `Program/workbench/cgss_data_discovery.py` 和 `Program/run_cgss_data_discovery.py`；扫描本地 CGSS `.dta`，记录年份、路径、文件大小、样本量、字段数、可读性、证据等级、同年份编码表/问卷和字段画像预览。
- [x] P6-J2 真实运行：用本机 `A004CGSS中国综合社会调查` 目录生成 `Results/json/cgss_social_capital_happiness_data_discovery.json` 与 `Reviews/cgss_social_capital_happiness_data_discovery.md`；推荐 `CGSS2023.dta`，样本量 11326，字段数 439，状态为 `needs_human_dataset_binding_review`。
- [x] P6-J2 正式层边界：本节点只写数据发现 JSON 和审阅 Markdown，不写正式变量角色、不改 DesignSpec/RunPlan、不生成论文、不写 `state/product/*`。
- [x] P6-J2 验证：目标测试 4 OK；相邻 topic audit / variable discovery 回归合计 9 OK；Python 编译通过；真实 CLI 运行通过。
- [x] P6-J3 Agent Team：派发 Gibbs 只读定位 DatasetBinding -> 变量角色草案的最小接入点；回收结论为优先做草案层 DatasetBinding 约束过滤，不能改 `state/product/variable_roles.json`、DesignSpec、RunPlan 或正式包。
- [x] P6-J3 BDD/TDD：新增 `tests/test_cgss_dataset_bound_variable_role_draft.py`，先确认缺少 `Program.workbench.cgss_dataset_bound_variable_role_draft` 的 RED，再实现 DatasetBinding 约束后的变量角色草案模块和 CLI。
- [x] P6-J3 实现：新增 `Program/workbench/cgss_dataset_bound_variable_role_draft.py` 和 `Program/run_cgss_dataset_bound_variable_role_draft.py`；只读取推荐数据集 CGSS2023 对应的候选变量，输出因变量、社会资本多维题项和控制变量的选择理由。
- [x] P6-J3 真实运行：写出 `Results/json/cgss_social_capital_happiness_dataset_bound_variable_role_draft.json` 与 `Reviews/cgss_social_capital_happiness_dataset_bound_variable_role_draft.md`；状态为 `needs_human_dataset_bound_role_review`，推荐数据为 CGSS2023，样本量 11326，字段数 439。
- [x] P6-J3 变量草案：因变量为 `happiness <- a36`；社会资本草案为 `a33/a31a/a31b/a311` 多维结构；控制变量候选为 `a2/a3a/a7a/a7b/a15/a18/a21/a8a/a8b/s41`；2021/2018 候选只保留为排除计数和后续稳健性候选，不进入主草案。
- [x] P6-J3 正式层边界：本节点不写正式变量角色、不改 DesignSpec/RunPlan、不生成论文、不写 `state/product/*`；`promotion.allowed=false`。
- [x] P6-J3 验证：目标测试 4 OK；真实 CLI 运行通过；审阅 Markdown 已包含数据绑定、变量理由、审阅门禁和正式层边界。
- [x] P6-J4 Agent Team：派发 Mill 只读定位现有 DesignSpec/RunPlan 入口；回收结论为正式层由 `Product/backend/design_spec_service.py` 写 `state/product/*`，本节点只能新增草案层，不走正式保存服务。
- [x] P6-J4 BDD/TDD：新增 `tests/test_cgss_design_spec_draft.py`，先确认缺少 `Program.workbench.cgss_design_spec_draft` 的 RED，再实现 CGSS 研究设计草案模块和 CLI。
- [x] P6-J4 实现：新增 `Program/workbench/cgss_design_spec_draft.py` 和 `Program/run_cgss_design_spec_draft.py`；把已绑定 CGSS2023 数据和变量角色草案转成横截面 OLS / Ordered Logit 设计说明、识别边界、方法族门禁和审阅门禁。
- [x] P6-J4 真实运行：写出 `Results/json/cgss_social_capital_happiness_design_spec_draft.json` 与 `Reviews/cgss_social_capital_happiness_design_spec_draft.md`；状态为 `needs_human_design_spec_review`。
- [x] P6-J4 方法边界：当前可以进入 OLS 基准模型和 Ordered Logit 有序模型；DID/IV/RDD/PSM/DML 因缺少处理时间、工具变量、断点、二元处理定义或因果处理设定，暂不进入运行计划。
- [x] P6-J4 正式层边界：本节点不写正式 DesignSpec、不写 RunPlan、不写正式变量角色、不生成论文、不写 `state/product/*`；`promotion.allowed=false`，批准后才允许进入 RunPlan 草案。
- [x] P6-J4 验证：目标测试 5 OK；CGSS 数据发现/变量发现/数据绑定/DesignSpec 状态机/方法门禁相邻回归 27 OK；Python 编译通过；真实 CLI 运行通过；scoped `git diff --check` 通过。
- [x] P6-J5 Agent Team：派发 Herschel 后台执行 RunPlan seed 收尾；主 Agent 回收后复核输出、修正中文命令可读性并重新验证。
- [x] P6-J5 BDD/TDD：新增 `tests/test_cgss_run_plan_seed.py`，先确认缺少 `Program.workbench.cgss_run_plan_seed` 的 RED，再实现 CGSS RunPlan seed 模块和 CLI。
- [x] P6-J5 实现：新增 `Program/workbench/cgss_run_plan_seed.py` 和 `Program/run_cgss_run_plan_seed.py`；把 CGSS DesignSpec 草案转成可审阅 RunPlan seed，明确原始字段到执行变量的构造规则、OLS/Ordered Logit 命令、预期产物和失败解释。
- [x] P6-J5 真实运行：写出 `Results/json/cgss_social_capital_happiness_run_plan_seed.json` 与 `Reviews/cgss_social_capital_happiness_run_plan_seed.md`；状态为 `needs_human_run_plan_seed_review`。
- [x] P6-J5 正式层边界：本节点不写正式 RunPlan、不写正式 DesignSpec、不写正式变量角色、不运行模型、不生成论文、不写 `state/product/*`；`promotion.allowed=false`，批准后才允许进入执行节点。
- [x] P6-J5 验证：目标测试 5 OK；CGSS DesignSpec/OLS/Ordered Logit 相邻回归 13 OK；Python 编译通过；真实 CLI 运行通过。
- [x] P6-J6a BDD/TDD：新增 `tests/test_cgss_run_plan_seed_approval.py`，先确认缺少 `Program.workbench.cgss_run_plan_seed_approval` 的 RED，再实现 RunPlan seed 人工审阅决策模块和 CLI。
- [x] P6-J6a 实现：新增 `Program/workbench/cgss_run_plan_seed_approval.py` 和 `Program/cgss_run_plan_seed_approval.py`；支持 `defer/approve/revise/reject`，其中 `approve` 必须带 reviewer 和 note，才生成 approved RunPlan seed sidecar。
- [x] P6-J6a 真实运行：默认 `defer` 写出 `Results/json/cgss_social_capital_happiness_run_plan_seed_approval.json` 与 `Reviews/cgss_social_capital_happiness_run_plan_seed_approval.md`；状态为 `pending_human_run_plan_seed_decision`，未生成 approved seed。
- [x] P6-J6a 正式层边界：本节点不写正式 RunPlan、不运行模型、不写 `state/product/*`；批准后的 sidecar 仍只允许进入草案执行。
- [x] P6-J6a 验证：目标测试 5 OK；CGSS RunPlan/DesignSpec/OLS/Ordered Logit 相邻回归 18 OK；Python 编译通过；真实 CLI 运行通过。
- [x] P6-J6b BDD/TDD：新增 `tests/test_cgss_run_plan_seed_executor.py`，先确认缺少 `Program.workbench.cgss_run_plan_seed_executor` 的 RED，再实现 approved seed 执行器和 CLI。
- [x] P6-J6b 实现：新增 `Program/workbench/cgss_run_plan_seed_executor.py` 和 `Program/cgss_run_plan_seed_executor.py`；未批准时生成阻断记录，批准后执行 OLS、Ordered Logit，并合并 `cgss_social_capital_happiness_results_evidence_package`。
- [x] P6-J6b 真实运行：先验证无 approved seed 时 `status=blocked_run_plan_seed_not_approved`；随后用目标模式继续指令记录草案层 approve sidecar，再真实执行 CGSS OLS 与 Ordered Logit，输出 `Results/json/cgss_social_capital_happiness_run_plan_seed_execution.json` 与 `Reviews/cgss_social_capital_happiness_run_plan_seed_execution.md`。
- [x] P6-J6b 正式层边界：本节点仍不写正式 RunPlan、不写 `state/product/*`、不把结果升级为正式结论；模型结果进入 `completed_needs_human_result_review`，证据包进入 `ready_for_paper_draft_input`。
- [x] P6-J7 BDD/TDD：新增 `tests/test_cgss_manuscript_section_router.py`，先确认缺少 `Program.workbench.cgss_manuscript_section_router` 的 RED，再实现结果证据包到论文章节草案的路由器。
- [x] P6-J7 实现：新增 `Program/workbench/cgss_manuscript_section_router.py` 和 `Program/cgss_manuscript_section_router.py`；把结果证据包和文献综述草稿包转成 4 个可审阅章节：文献综述与研究贡献、数据与变量、实证策略、主要实证结果。
- [x] P6-J7 真实运行：写出 `Reviews/cgss_social_capital_happiness_manuscript_sections.md` 和 `Manuscripts/generated/cgss_social_capital_happiness_sections/*.md`；状态为 `needs_human_manuscript_section_review`，4 个章节均达到最低中文字符门槛，合计 2996 字符。
- [x] P6-J7 正式层边界：本节点只写草案层章节和审阅报告，不写正式 manuscript、不写正式 bibliography、不写 `state/product/*`；`Results/json/cgss_social_capital_happiness_manuscript_sections.json` 受 `.gitignore` 忽略，作为本地运行产物保留。
- [x] P6-J7 验证：目标测试 3 OK；相邻 CGSS 结果证据包 / RunPlan seed 执行器 / 文献综述草稿包回归 15 OK；Python 编译通过；P6-J7 相关文件 scoped `git diff --check` 通过。全局 `git diff --check` 被无关前端测试文件 `tests/test_p3_task_brief_demo.py` 的历史尾随空格阻断，未纳入本节点。
- [x] P6-J8 BDD/TDD：新增 `tests/test_cgss_exploratory_paper_assembler.py`，先确认缺少 `Program.workbench.cgss_exploratory_paper_assembler` 的 RED；随后收紧薄输入样例，确认完整论文不足 5000 中文字符会被测试抓住，再补足组装正文。
- [x] P6-J8 实现：新增 `Program/workbench/cgss_exploratory_paper_assembler.py` 和 `Program/cgss_exploratory_paper_assembler.py`；把 4 个分节草稿、结果证据包和文献综述草稿包组装为完整探索性论文 Markdown，包含摘要、引言、文献综述、数据变量、实证策略、主要结果、稳健性计划、结论、参考文献候选和人工审阅清单。
- [x] P6-J8 真实运行：写出 `Manuscripts/generated/cgss_social_capital_happiness_paper.md`、`Results/json/cgss_social_capital_happiness_paper_assembly.json` 和 `Reviews/cgss_social_capital_happiness_paper_assembly.md`；状态为 `needs_human_exploratory_paper_review`，正文中文字符数 5399，超过最低 5000 门槛。
- [x] P6-J8 正式层边界：本节点只生成草案层完整稿、assembly JSON 和审阅报告；不写正式 manuscript、不写正式 bibliography、不写 `state/product/*`。`Manuscripts/generated/*` 与 `Results/json/*` 仍按 `.gitignore` 作为本地运行产物保留。
- [x] P6-J8 验证：目标测试 3 OK；相邻 CGSS 章节路由 / 结果证据包 / 文献综述草稿包回归 15 OK；Python 编译通过；真实 CLI 运行通过；P6-J8 相关文件 scoped `git diff --check` 通过。
- [x] P6-J9 BDD/TDD：新增 `tests/test_cgss_pdf_preflight.py`，先确认缺少 `Program.workbench.cgss_pdf_preflight` 的 RED，再实现草案 PDF/HTML 预检器。
- [x] P6-J9 实现：新增 `Program/workbench/cgss_pdf_preflight.py` 和 `Program/cgss_pdf_preflight.py`；读取 `Manuscripts/generated/cgss_social_capital_happiness_paper.md`，优先用 `pandoc + xelatex` 生成 PDF，失败时回退 HTML 并记录渲染诊断。
- [x] P6-J9 真实运行：写出 `Submissions/cgss_social_capital_happiness/paper.pdf`、`Results/json/cgss_social_capital_happiness_pdf_preflight.json` 和 `Reviews/cgss_social_capital_happiness_pdf_preflight.md`；状态为 `pdf_preflight_ready`，PDF 大小 187320 bytes。
- [x] P6-J9 正式层边界：本节点只做草案 PDF 预检，不写正式 manuscript、不写正式 package、不写 `state/product/*`。`Submissions/*` 与 `Results/json/*` 仍按 `.gitignore` 作为本地运行产物保留。
- [x] P6-J9 验证：目标测试 3 OK；PDF / paper assembly / section router 相邻回归 9 OK；Python 编译通过；真实 CLI 运行通过；`file Submissions/cgss_social_capital_happiness/paper.pdf` 确认为 PDF document version 1.7。
- [x] P6-K BDD/TDD：新增 `tests/test_cgss_method_gate.py`，先确认缺少 `Program.workbench.cgss_method_gate` 的 RED，再实现 CGSS AER-like 方法规范门。
- [x] P6-K 实现：新增 `Program/workbench/cgss_method_gate.py` 和 `Program/cgss_method_gate.py`；默认 `working_paper` 只建议方法门，`--profile aer_like` 强制输出人工审阅 gate。
- [x] P6-K 真实运行：`python3 Program/cgss_method_gate.py --profile aer_like` 写出 `Results/json/cgss_social_capital_happiness_method_gate.json` 和 `Reviews/cgss_social_capital_happiness_method_gate.md`；状态为 `needs_human_method_gate_review`，`gate_status=yellow`。
- [x] P6-K 方法检查：覆盖变量定义、OLS + Ordered Logit 适配、社会资本理论/文献依据、基础控制变量、稳健性/异质性/机制计划、反向因果和遗漏变量风险；结果数字绑定到 `cgss_social_capital_happiness_results_evidence_package.json`。
- [x] P6-K 正式层边界：本节点只写草案层方法门 JSON 和人工审阅报告，不写正式 manuscript、不写正式 bibliography、不写 DesignSpec/RunPlan、不写 `state/product/*`。
- [x] P6-L BDD/TDD：新增 `tests/test_cgss_reviewer_revision_loop.py`，先确认缺少 `Program.workbench.cgss_reviewer_revision_loop` 的 RED，再实现审稿式修订循环。
- [x] P6-L 实现：新增 `Program/workbench/cgss_reviewer_revision_loop.py` 和 `Program/cgss_reviewer_revision_loop.py`；消费探索性论文、paper assembly、P6-K 方法门、结果证据包和文献综述草稿包。
- [x] P6-L 真实运行：`python3 Program/cgss_reviewer_revision_loop.py` 写出 `Reviews/cgss_social_capital_happiness_reviewer_report.md`、`Reviews/cgss_social_capital_happiness_revision_task_queue.md` 和 `Manuscripts/generated/cgss_social_capital_happiness_paper_rev1.md`；状态为 `needs_human_revision_review`，生成 6 条修订任务。
- [x] P6-L 审稿覆盖：覆盖论文结构、文献综述、数据和变量、识别策略、结果解释、稳健性缺口、投稿规范缺口和需要人类判断的问题。
- [x] P6-L 正式层边界：本节点只写草案层审稿报告、修订任务队列和 Rev1 草稿；不写正式 manuscript、不写正式 bibliography、不写 DesignSpec/RunPlan、不写 `state/product/*`。
- [x] P6-M BDD/TDD：新增 `tests/test_cgss_paper_package_builder.py`，先确认缺少 `Program.workbench.cgss_paper_package_builder` 的 RED，再实现可验收 paper package builder。
- [x] P6-M 实现：新增 `Program/workbench/cgss_paper_package_builder.py` 和 `Program/cgss_paper_package_builder.py`；汇总 Rev1 paper、PDF/HTML 预检产物、结果证据包、文献综述草稿包、方法门、审稿报告、修订队列、复现 README 和 manifest。
- [x] P6-M 真实运行：`python3 Program/cgss_paper_package_builder.py` 写出 `workspace/paper_packages/cgss_social_capital_happiness/`；状态为 `needs_human_paper_package_review`，`rendered_artifact=paper.pdf`，共 9 个文件。
- [x] P6-M 验收边界：manifest 标记真实运行产物、草稿层产物和需要人工审阅产物；本节点不写正式 manuscript、不写正式 bibliography、不写 `state/product/*`。
- [ ] 下一步人工审阅：打开 package 下的 `paper.md`、`paper.pdf`、`method_gate.md`、`reviewer_report.md`、`revision_task_queue.md` 和 `manifest.json`，决定是否批准进入正式层或继续 Rev2 修订。

## 2026-05-26 North Star：CLI-first Real Empirical Flow + Journal Skill Registry

- [x] 明确主线：先把本地 CLI 高效工作流跑通，再把同一套状态和证据模型接到云端产品。
- [x] 新增北极星计划：`docs/architecture-v2/north-star-cli-first-research-os-plan-2026-05-26.md`。
- [x] 新增真实数据 CLI 行为文档：`docs/architecture-v2/codex-phase-p2-real-data-cli-full-run-bdd.md`。
- [x] 让 `Program/run_paper.py` 支持 `--paper-config`，避免真实数据运行覆盖默认 `paper.yaml` 输出。
- [x] 新增真实 CFPS/机器人配置：`Program/config/paper_real_cfps_robot.yaml`。
- [x] 完成真实 CLI live run：`run_cli_real_cfps_robot_20260526_isolated`。
- [x] 真实运行写出独立 state、results index、snapshot、analysis result、run log、Markdown/LaTeX 草稿和 observability。
- [x] 修复 Auto Research 数据选择：题目包含 CFPS/机器人时优先选择 `Data/Final/cfps_robot_reallocation.csv`，不再使用 demo `analysis_sample.csv`。
- [x] 修复启发式变量匹配：不再把 `ln_wage` 因为包含 `age` 而误放入 controls。
- [x] 新增 Journal Skill Registry 设计：`docs/architecture-v2/journal-skill-registry-design-2026-05-26.md`。
- [x] 新增方法库边界：`Program/methodology/README.md`。
- [x] 新增 AER-like proposal 入口：`Program/methodology/proposals/2026-05-26-aer-skills-import/proposal.yml`。
- [ ] 下一步实现 `JournalSkillRegistry` 读取器：能区分 proposal 和 canonical，并保证 proposal 不能阻断 formal export。
- [ ] 下一步实现 `state/product/journal_review.json` 的读写服务和 API。
- [ ] 下一步把 Task Brief 的“审稿标准：AER-like 顶刊标准”选择接入后端状态。
- [ ] 下一步把 Method Design 的缺失证据提示接入 Journal Skill rules。
- [ ] 下一步把 Review & Export 的 verifier gates 扩展为 journal-aware gates。

## 2026-05-26 P4-A Paper Package Quality Upgrade

- [x] 记录用户修正：研究产出按“草稿 -> 审阅 -> 终稿”推进，不再使用防御式自我贬低措辞。
- [x] P4 节点节奏规则：P4-A/B/C/D 以及后续 P4-I1/I2/I3 等每个小节点最多 20 分钟；超过 20 分钟必须拆成更小节点，或判定当前路径需要调整。
- [x] P4 节点协作规则：每个节点必须写明 Agent Team 何时派出、何时收回、下一次何时再派；主 Agent 负责集成、测试、提交和风险边界。
- [x] 新增论文包质量标准：`docs/architecture-v2/paper-package-quality-standard-2026-05-26.md`。
- [x] 新增文献综述闭环方案：`docs/architecture-v2/literature-review-closed-loop-2026-05-26.md`。
- [x] 新增方法规范门方案：`docs/architecture-v2/method-gate-standard-2026-05-26.md`。
- [x] P4-A BDD：写 `docs/architecture-v2/codex-phase-p4-paper-package-quality-bdd.md`，锁定长篇正文、文献包、方法门、修订记录、PDF 导出质量报告和 LLM Supervisor 上下文包。
- [x] P4-A TDD：新增 CLI quality report / paper package 测试，先证明当前 `run_paper.py/export_pdf.py` 只证明导出链路，不足以证明论文包完整。
- [x] P4-A 实现：增加 `Program/workbench/paper_quality.py`，读取草稿、bibliography、method gate、manifest 并写出 `Results/json/paper_quality_report.json`。
- [x] P4-A 实现：增加 `Program/paper_package.py` 和 `Program/workbench/paper_package.py`，生成 `paper_expansion_plan.json`、结构化论文包草稿和 `paper_supervisor_context.json`。
- [x] P4-A 真实运行：对 `Manuscripts/generated/cfps_robot_paper_draft.md` 生成质量报告、扩写计划、结构化草稿和 LLM Supervisor 上下文包。
- [x] P4-A 架构边界：明确 Python/StatsPAI/StataMCP 是执行层，local Codex / LLM Supervisor 是研究中控和 Agent 派工层。
- [x] P4-A LLM 中控入口：新增 `Program/paper_supervisor.py` 和 `Program/workbench/paper_supervisor.py`，启用 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1` 后调用本地 Codex 生成可审阅 Supervisor 运行产物。
- [x] P4-A 真实 Supervisor 运行：生成 `Results/json/paper_supervisor_run.json` 和 `docs/workflows/paper_package_supervisor/supervisor_round.md`，状态为 `needs_human_review`，不改写正式层 `research_question/variable_roles/design_spec/run_plan`。
- [x] P4-A Agent Team 调度记录：确认后续 P4 阶段必须写明并行 Agent Team 介入点、回收点和主线集成验收点，避免串行低效和多 Agent 各自写散。
- [x] P4-B：完成 DataAgent 变量角色调和，把真实 CFPS/机器人研究线索与旧 `wage/trained` 合成样例拆开；输出 proposal，不直接覆盖正式 `variable_roles.json`。
- [x] P4-B BDD/TDD：新增行为 9 和 `tests/test_variable_role_reconciliation.py`，先确认缺少 CLI 入口的 RED，再实现最小 proposal CLI。
- [x] P4-B 实现：新增 `Program/variable_role_reconcile.py` 和 `Program/workbench/variable_role_reconcile.py`，写出 `state/proposals/variable_role_reconciliation.json` 与 `Results/json/variable_role_reconciliation_report.json`。
- [x] P4-B 真实运行：识别当前正式层两个冲突：旧 dataset `Data/Final/analysis_sample.csv` 与真实 dataset `Data/Final/cfps_robot_reallocation.csv` 冲突；旧 roles `wage/trained/edu/experience` 与真实 roles `ln_wage/ln_robot/female/age/edu_last/urban/bartik_iv/year/provcd` 冲突。
- [x] P4-B Agent Team 调度：并行调用 DataAgent 做状态/数据映射，调用 Method/Literature sidecar 做变量证据门调研；回收后由主 Agent 集成到 proposal 的 `agent_team_schedule` 和 `role_evidence_matrix`。
- [x] P4-C：实现 LiteratureAgent 的 `candidate_literature.csv`、`verified_bibliography.csv`、`contribution_matrix.md` 最小闭环。
- [x] P4-C BDD/TDD：新增行为 10 和 `tests/test_literature_package.py`，先确认缺少 `Program/literature_package.py` 的 RED，再实现最小文献包 CLI。
- [x] P4-C Agent Team 调研：调用 Literature sidecar 做英文核心文献、DOI/官方来源、证据角色和 CNKI 人工检索队列；回收后并入 seed literature package。
- [x] P4-C 实现：新增 `Program/literature_package.py` 和 `Program/workbench/literature_package.py`，生成 9 条候选/已校验英文文献、贡献矩阵、CNKI 人工检索队列和 Agent Team 调用节奏。
- [x] P4-C 真实运行：写出 `Data/literature/processed/candidate_literature.csv`、`verified_bibliography.csv`、`contribution_matrix.md`、`Results/json/literature_package_report.json`；`paper_quality_after_literature_package.json` 显示 `citation_status=passed`、`verified_count=9`、`closest_or_method_count=6`。
- [x] P4-D：实现 MethodGate baseline 报告，把当前 Bartik IV/2SLS 设计写成 `green/yellow/red` 审阅报告。
- [x] P4-D BDD/TDD：新增行为 11 和 `tests/test_method_gate_cli.py`，先确认缺少 `Program/method_gate.py` 的 RED，再实现最小方法门 CLI。
- [x] P4-D Agent Team 调研：并行调用 MethodAgent、ExecutionAgent explorer、ReviewerAgent sidecar；MethodAgent 给出 IV/Bartik 缺失证据，ExecutionAgent 定位执行层挂载点，ReviewerAgent 给出审稿式 scorecard 接入点。
- [x] P4-D 实现：新增 `Program/method_gate.py` 和 `Program/workbench/method_gate.py`，读取已批准 `DesignSpec` / `RunPlan`，只写 `Results/json/method_gate_report.json`，不改写正式层。
- [x] P4-D 真实运行：当前 Bartik IV 方法门为 `yellow`，已记录 first-stage F 和 partial R2，同时列出 reduced form、弱工具稳健推断、shift-share 诊断、Rotemberg weights、leave-one-out 等下一轮证据要求。
- [x] P4-D2：实现真实方法诊断 CLI，把 MethodGate 的 yellow 缺口推进为可复算的 2SLS、一阶段、reduced form、OLS 对照、样本一致性和 artifact binding 报告。
- [x] P4-D2 BDD/TDD：新增行为 12 和 `tests/test_method_diagnostics_cli.py`，先确认缺少 `Program/method_diagnostics.py` 的 RED，再实现最小真实诊断 CLI。
- [x] P4-D2 Agent Team 调研：并行调用 MethodAgent、ExecutionAgent explorer、ReviewerAgent；MethodAgent 明确哪些 IV/Bartik 诊断必须真实跑、哪些需要 share/shock 组件，ExecutionAgent 定位执行层复用边界，ReviewerAgent 明确 scorecard 读取字段。
- [x] P4-D2 实现：新增 `Program/method_diagnostics.py` 和 `Program/workbench/method_diagnostics.py`，并让 `Program/workbench/method_gate.py` 读取 `Results/json/method_diagnostics_report.json`。
- [x] P4-D2 真实运行：在 `Data/Final/cfps_robot_reallocation.csv` 上重新估计 `ln_wage ~ (ln_robot ~ bartik_iv) + controls + year FE`，写出 `Results/json/method_diagnostics_report.json`；样本 15,697，聚类 30，2SLS 系数 0.1994，一阶段 F 14.52，partial R2 0.4834，reduced form 系数 0.1400。
- [x] P4-D2 方法门刷新：`Results/json/method_gate_report.json` 已读取诊断报告，reduced form、robust first-stage、result artifact binding 从 missing 变为 recorded；剩余 yellow 集中在弱工具稳健区间和 Bartik share/shock 组件诊断。
- [ ] P4-D3：扩展 MethodGate 到 DID/RDD/PSM/DML 的专属 `green/yellow/red` 规则，并接入 Journal Skill Registry / AER-like 方法规则。
- [x] P4-D4：让 Reviewer Scorecard 读取 `method_diagnostics_report.json`，把方法诊断变成审稿评分和 revision tasks。
- [x] P4-D4 BDD/TDD：新增行为 13 和 `tests/test_reviewer_scorecard_cli.py`，先确认缺少 `Program/reviewer_scorecard.py` 的 RED，再实现 Reviewer Scorecard CLI。
- [x] P4-D4 Agent Team 复核：调用 MethodAgent/ReviewerAgent sidecar 复核五维 scorecard、yellow 项转 revision task、以及不阻断草稿层的判定规则。
- [x] P4-D4 实现：新增 `Program/reviewer_scorecard.py` 和 `Program/workbench/reviewer_scorecard.py`，并让 `Program/workbench/paper_quality.py` 识别 `Results/json/reviewer_scorecard_report.json`。
- [x] P4-D4 真实运行：对当前真实 CFPS/机器人方法诊断生成 Reviewer Scorecard，并刷新 paper quality report；当前总分 61，允许草稿继续，阻断强因果表述和正式导出。
- [x] P4-E：让 PDF export manifest 读取 quality report 和 reviewer scorecard，导出后显示“论文包审阅入口”、export gate、下一轮自动任务和 Agent Team 调用节奏。
- [x] P4-F：让 `Program/paper_package.py --source-manifest` 读取 PDF export manifest，把 `next_review_tasks` 合并进 `paper_expansion_plan.json` 和 `paper_supervisor_context.json` 的 Supervisor / Agent 队列。
- [x] P4-F BDD/TDD：新增行为 15 和 `tests/test_paper_package_quality.py` 覆盖 export manifest 的下一轮任务进入队列、保留来源证据、写入 Agent Team 调用节奏。
- [x] P4-F 真实运行：基于 `Submissions/cfps_robot_pdf_export_manifest.json` 重新生成 `Results/json/paper_expansion_plan.json`、`Manuscripts/generated/paper_package_draft.md` 和 `Results/json/paper_supervisor_context.json`；当前合并后 `agent_task_queue=11`，其中 6 条来自 PDF 预检 manifest。
- [x] P4-G：把 `paper_expansion_plan.json.agent_task_queue` 转成审稿式修订轮次，生成 `Results/json/paper_revision_round.json` 和 `Reviews/paper_revision_round.md`。
- [x] P4-G BDD/TDD：新增行为 16 和 `tests/test_paper_package_quality.py` 覆盖 revision round、Agent packet、正式层不改写和 Agent Team 调用节奏；目标测试已从缺少 CLI 的 RED 进入 GREEN。
- [x] P4-G 真实运行：基于当前真实 `Results/json/paper_expansion_plan.json` 生成 11 条 revision items、6 个 Agent packets；`formal_writeback_allowed=false`、`draft_layer_only=true`、`formal_state_guard.changed=false`。
- [x] P4-H：消费 `paper_revision_round.json`，按 Agent packet 生成可执行补证任务包；每个 queued task 必须产出草案层证据文件或明确 `needs_manual_review`，不能停在自然语言建议。
- [x] P4-H BDD/TDD：新增行为 17 和 `tests/test_paper_revision_evidence_packets.py`，先确认缺少 `Program/paper_revision_evidence_packets.py` 的 RED，再实现 evidence packet CLI。
- [x] P4-H 真实运行：基于当前真实 `Results/json/paper_revision_round.json` 生成 `Results/json/paper_revision_evidence_packets.json`、`Reviews/paper_revision_evidence_packets.md` 和 11 个 `Reviews/agent_packets/*/*.md`；当前 10 条 `evidence_packet_ready`，1 条 `needs_manual_review`（文献包缺 `verified_bibliography.csv` 和 `contribution_matrix.md`），`formal_writeback_allowed=false`、`formal_state_guard.changed=false`。
- [x] P4-I：重跑 `paper_quality_report.json`、`method_gate_report.json`、`reviewer_scorecard_report.json` 和 PDF preflight manifest；每条上一轮任务必须标记 `cleared`、`still_blocking` 或 `manual_review_required`。
- [x] P4-J：生成 formal writeback preview，列出会改哪些章节、引用、方法叙述、结果表和复现说明；只做预检，不自动写正式层。
- [ ] P5：人工批准后生成正式 paper package，包含正文、PDF/PDF 预检、verified bibliography、contribution matrix、method diagnostics、reviewer scorecard、revision log、replication README、manifest 和复现命令。
- [ ] P6：生成投稿级复现交付包；Verifier 能按 manifest 复跑关键命令，确认表、图、主结果、样本口径和代码版本一致，并输出最终审计报告。
- [ ] 知识资产化：抽象复用 Agent Team schedule schema、Agent task schema、formal state guard、quality gate vocabulary、Journal/Method Skill Registry 和 verification evidence contract，避免 P4-H 到 P6 重复手写。
- [x] P6-F2 节点节奏规则升级：P4/P5/P6 的 A/B/C/D 等任意小节点最多 20 分钟；超时必须拆解为更小节点，或判定路线错误并回退，不再硬拖。
- [x] P6-F2 Agent Team 调用：Rawls 只读探查 React 工作流、AgentActivityPanel 挂载点和 P3 契约测试；主 Agent 负责 BDD/TDD、集成、浏览器验收、提交。
- [x] P6-F2 BDD/TDD：新增行为 41，新增 `tests/test_p6_formal_package_acceptance_surface.py`，先确认缺少正式包验收台的 RED，再实现最小 UI 接面。
- [x] P6-F2 实现：新增 `FormalPackageAcceptancePanel`，在 Agent 账本真实执行授权后读取 `GET /api/v1/projects/{project_id}/formal-submission-package-summary`，展示只读验收摘要、PDF/DOCX 打开目标、人工验收清单、一致性检查和阻断原因。
- [x] P6-F2 验证：目标测试、相邻回归、React build、`git diff --check` 和 Playwright 浏览器验收通过；截图写入 `artifacts/ui-checks/p6-formal-package-acceptance.png`。
- [x] P6-G1 节点节奏：本节点限定为 20 分钟内完成“逐章长度 quality gate”，不扩展 UI、PDF 或正式写回。
- [x] P6-G1 Agent Team 调用：Franklin 只读定位 paper quality/BDD/test 挂载点，Mill 调研 AEA/AER/AEJ 可机器化长度与结构规则；主 Agent 回收后只落地逐章长度 gate。
- [x] P6-G1 BDD/TDD：新增行为 2.1 和目标测试，先确认“全文够长但核心章节过薄”不会被现有 quality gate 抓住的 RED。
- [x] P6-G1 实现：`paper_quality_report.json` 新增 `section_length_checks`，逐章记录英文词数、中文字符数、目标区间和状态；`verdict` 新增 `section_length_gate_required`；`recommended_next_tasks` 新增 `expand_underdeveloped_sections`。
- [x] P6-G1 真实运行：当前 CFPS/机器人草稿被点名 Data、Empirical Strategy、Main Results、Robustness 四个章节过薄，已写入 `Results/json/paper_quality_report.json`，供下一轮 ManuscriptAgent 扩写。
- [x] P6-G2 BDD/TDD：给 `expand_underdeveloped_sections` 增加 `section_expansion_packet` 验收，先验证缺包失败，再实现通过。
- [x] P6-G2 实现：`section_expansion_packet` 逐章交付目标篇幅、证据要求、草案输出路径和正式层写回边界；`too_long` 章节不再进入扩写包，后续单独走压缩节点。
- [x] P6-G3 节点规则：本节点限定 20 分钟内完成“章节扩写包进入 paper package”，不写章节正文、不调用正式写回、不扩展 UI。
- [x] P6-G3 Agent Team：Sartre 只读复核 `paper_package` 队列契约，指出 `normalize_agent_task_queue()` 丢失 `section_expansion_packet`；主 Agent 回收后只修白名单透传和章节任务展开。
- [x] P6-G3 BDD/TDD：在 `test_bdd_8_builds_expansion_plan_and_structured_manuscript` 中增加 `section_expansion_packet` 和 `manuscript_section_task_packets` 验收，先确认 RED，再做最小实现。
- [x] P6-G3 实现：`paper_expansion_plan.json.agent_task_queue` 保留 ManuscriptAgent 的 `section_expansion_packet`，并新增 `manuscript_section_task_packets`，逐章暴露 section、output_path、required_evidence、draft/formal 写回边界和 verification。
- [x] P6-G4 节点规则：本节点限定 20 分钟内完成“章节任务包物化为可打开工单”，不写章节正文、不改正式层、不扩展 UI。
- [x] P6-G4 Agent Team：Lovelace 只读复核测试挂载点和正式层保护边界；主 Agent 同步写 RED 测试和最小实现。
- [x] P6-G4 BDD/TDD：新增行为 16.1 和测试 `test_bdd_11_1_revision_round_materializes_manuscript_section_work_orders`，先确认 revision round 缺少 `manuscript_section_work_orders` 的 RED。
- [x] P6-G4 实现：`paper_revision_round.py` 消费 `manuscript_section_task_packets`，写出 `manuscript_section_work_orders` 和 `Reviews/agent_packets/manuscriptagent/sections/*.md` 草案层工单。

### Agent Team 调用节奏

- P4-B 已执行并行介入：DataAgent 读取真实数据字段和现有变量角色；Method/Literature sidecar 调研变量角色最低证据门、IV 风险和复现规范。三路只提供证据，不直接写正式层。
- P4-B 已执行回收点：主 Agent 汇总 sidecar 输出，形成 `state/proposals/variable_role_reconciliation.json` 和 `Results/json/variable_role_reconciliation_report.json`；正式 `state/product/variable_roles.json`、`design_spec.json`、`run_plan.json` 未被改写。
- P4-C 已执行并行介入：LiteratureAgent 调研英文核心文献、DOI、官方来源、证据角色和 CNKI 人工检索路径；主 Agent 同步写 BDD/TDD 和 CLI 契约，没有等待在原地。
- P4-C 已执行回收点：主 Agent 将调研结果收敛为 processed 文献包，生成 `candidate_literature.csv`、`verified_bibliography.csv`、`contribution_matrix.md` 和 `literature_package_report.json`；未改写 `state/product` 正式层。
- P4-D 已执行并行介入：MethodAgent 跑 IV/Bartik 方法规范门；ExecutionAgent explorer 定位执行层挂载点和只写报告的边界；ReviewerAgent 准备审稿式 scorecard 接入方式。三路共享已批准 `DesignSpec` / `RunPlan`，但不直接写正式层。
- P4-D 已执行回收点：主 Agent 将三路结果收敛为 `Results/json/method_gate_report.json`，把当前 Bartik IV 标为 `yellow`，并写入下一轮 Agent Team 调用节奏。
- P4-D2 已执行并行介入：ExecutionAgent 负责真实方法诊断设计与执行边界；MethodAgent 负责 IV/Bartik 规范和 manual-review 边界；ReviewerAgent 负责后续 scorecard 字段和不阻断草稿层的 revision task 规则。
- P4-D2 已执行回收点：主 Agent 关闭三路 Agent，合并为 BDD 行为 12、`Program/method_diagnostics.py`、`Results/json/method_diagnostics_report.json` 和 MethodGate 读取逻辑；正式 `state/product/*` 未被改写。
- P4-D2 已执行验证点：真实 CFPS/机器人数据完成 2SLS、一阶段、reduced form、OLS 对照和样本一致性诊断；MethodGate 刷新后 reduced form、robust first-stage、result artifact binding 已变为 recorded。
- P4-D4 已执行并行介入：MethodAgent 复核 `method_diagnostics_report.json` 的 yellow/needs_manual_review 项；ReviewerAgent 把诊断报告转成审稿式 scorecard；主 Agent 同步写 BDD/TDD 和 scorecard CLI，不等待在原地。
- P4-D4 已执行回收点：主 Agent 将 sidecar 输出收敛为行为 13、`Program/reviewer_scorecard.py`、`Results/json/reviewer_scorecard_report.json` 和 paper quality 的 scorecard detection；正式 `state/product/*` 未被改写。
- P4-D4 下一次 Agent Team 调用点：只有在进入 ManuscriptAgent 扩写或 ExportAgent 预检前，再调用 ReviewerAgent/VerifierAgent 审核 scorecard、revision tasks 和 PDF/manifest 阻断条件。
- P4-E 已执行调用点：ExportAgent 在 PDF preflight 前读取 paper quality report 和 reviewer scorecard，相当于调用 ReviewerAgent/VerifierAgent 做导出门审阅；调用范围只限 manifest、review doc 和 reproduce scripts。
- P4-E 已执行回收点：主 Agent 将 quality verdict、scorecard、export gate 和 next review tasks 合并进 `Submissions/cfps_robot_pdf_export_manifest.json` 与 `Submissions/cfps_robot_pdf_first_review.md`；正式 `state/product/*` 和论文正式层未被改写。
- P4-E 下一次 Agent Team 调用点：用户批准进入正式层写回或最终 PDF export 前，再调用 ReviewerAgent/VerifierAgent 复核 `export_gate.can_export_pdf`、revision tasks 是否清零，以及是否允许生成正式包。
- P4-E 串行收口：ManuscriptAgent 只在方法门和文献包存在后生成草稿层章节；ExportAgent 在 reviewer scorecard 通过前只生成 PDF/README/manifest 预检包，不提升正式层状态。
- P4-F 已执行调用点：在 `paper_package --source-manifest` 读取 PDF export manifest 前，调用 ReviewerAgent/VerifierAgent 解释 `next_review_tasks`、`export_gate` 和上一轮 preflight 边界；同时调用 LiteratureAgent/MethodAgent/ManuscriptAgent 判断每条任务应归属哪个执行角色。
- P4-F 已执行回收点：主 Agent 收回各路判断后，只把 manifest 任务合并到草案层 `paper_expansion_plan.json.agent_task_queue` 和 `paper_supervisor_context.json.agent_task_queue`；不改写正式 `state/product/*`、变量角色、DesignSpec、RunPlan 或正式论文层。
- P4-F 下一次 Agent Team 调用点：进入正式层写回或最终 PDF export 前，再调用 ReviewerAgent/VerifierAgent 复核 `reviewer_scorecard_task_cleared`、`export_gate_recomputed` 和 `updated_section_or_diagnostic_artifact`，确认每条 manifest 任务已有证据闭环。
- P4-F 串行收口：主 Agent 是 integration owner；Agent Team 负责证据解释和角色分工，最终队列去重、排序、写盘和测试验证由主 Agent 完成。
- P4-G 已执行调用点：生成 revision round 前调用 ReviewerAgent/VerifierAgent/MethodAgent 复核任务来源、证据要求和正式层边界；同时调用 DataAgent、LiteratureAgent、ManuscriptAgent、ExecutionAgent 作为任务归属方。
- P4-G 已执行回收点：主 Agent 将 11 条任务收敛为 `Results/json/paper_revision_round.json` 和 `Reviews/paper_revision_round.md`；只写草案层审阅产物，不改写 `state/product/*`。
- P4-G 下一次 Agent Team 调用点：P4-H 执行任务或 P4-J 正式写回预检前，再调用 ReviewerAgent/VerifierAgent 复核每条任务是否已有 `updated_section_or_diagnostic_artifact`、`reviewer_scorecard_task_cleared` 和 `export_gate_recomputed`。
- P4-H 已执行调用点：按 `paper_revision_round.json.agent_packets` 并行调用 LiteratureAgent、DataAgent、MethodAgent、ExecutionAgent、ManuscriptAgent；每个 Agent 只写自己的 evidence packet，写出后立刻收回，由 MainAgent 统一合并状态。
- P4-H 已执行回收点：主 Agent 将 11 条任务合并为 `Results/json/paper_revision_evidence_packets.json` 和 `Reviews/paper_revision_evidence_packets.md`；10 条有结构化本地 artifact/hash/schema 证据，1 条文献包任务进入 `needs_manual_review`，正式 `state/product/*` 未被改写。
- P4-H 下一次 Agent Team 调用点：P4-I 重跑质量门、方法门、审稿门和 PDF preflight 前，调用 ReviewerAgent/VerifierAgent 复核每条 evidence packet，并把状态更新为 `cleared`、`still_blocking` 或 `manual_review_required`。
- P4-I1 已执行：消费 `paper_revision_evidence_packets.json`，生成质量门复核账本 `Results/json/paper_revision_gate_recompute.json` 和 `Reviews/paper_revision_gate_recompute.md`；真实结果为 0 条 cleared、10 条 still_blocking、1 条 manual_review_required。
- P4-I1 BDD/TDD：新增行为 18 和 `tests/test_paper_revision_gate_recompute.py`，先确认缺少 `Program/paper_revision_gate_recompute.py` 的 RED，再实现 gate recompute ledger CLI。
- P4-I1 Agent Team 回收点：ReviewerAgent/VerifierAgent 复核状态规则后收回；下一次只在 formal writeback preflight 前再次调用。
- P4-I2 已执行：让 `Program/paper_package.py --source-manifest` 消费 `Results/json/paper_revision_gate_recompute.json`，下一轮任务生产器不再把上一轮 `evidence_packet_ready` 的任务重新塞回队列。
- P4-I2 真实运行：当前真实队列从 11 条收敛为 1 条，只保留 `build_literature_package`，来源 `paper_revision_gate_recompute`，状态 `manual_review_required`，缺口为 `verified_bibliography.csv` 和 `contribution_matrix.md`。
- P4-I2 BDD/TDD：新增行为 19 和 `tests/test_paper_package_quality.py::test_bdd_19_gate_producer_consumes_recompute_without_requeueing_evidence_ready_tasks`；RED 为 `run_method_gate` 被错误重复入队，GREEN 后只保留人工补证任务。
- P4-I2 Agent Team 回收点：Wegener 定位任务生产器与门控生产者，Kant 定位测试锚点和 RED 断言；主 Agent 合并最小实现、跑验证并收回两路结果。
- P4-I3 已执行：修复证据包收集层对文献包 canonical 路径的识别，`verified_bibliography.csv` 和 `contribution_matrix.md` 现在映射到 `Data/literature/processed/*`，不再被误判为缺失。
- P4-I3 真实运行：重跑 `paper_revision_evidence_packets.py` 后 11 条任务全部为 `evidence_packet_ready`、`needs_manual_review=0`；重跑 `paper_revision_gate_recompute.py` 后 11 条均为 `still_blocking`（当前 gate artifacts 仍引用这些任务），`manual_review_required=0`；重跑 `paper_package.py --source-manifest` 后 `agent_tasks=0`。
- P4-I3 BDD/TDD：新增行为 20 和 `tests/test_paper_revision_evidence_packets.py::test_bdd_20_literature_short_names_resolve_to_canonical_processed_artifacts`；RED 为文献任务仍是 `needs_manual_review`，GREEN 后绑定 processed 文献证据路径。
- P4-I3 Agent Team 回收点：Hooke 定位路径归一化缺陷，Noether 给出 CNKI/文献证据包第一版字段和人工辅助检索边界；主 Agent 合并为最小路径修复，没有扩展文献重写或正式层写回。
- P4-I4 已执行：让 `paper_revision_gate_recompute.py` 消费已就绪 evidence packet 对旧 gate 任务引用的回应；gate 输入齐全且 `evidence_packet_ready` 的任务进入 `cleared`，旧 `recommended_next_tasks` / `next_review_tasks` 引用写入 `consumed_gate_matches` 作为审计线索，不再形成重复阻塞。
- P4-I4 真实运行：重跑 `paper_revision_gate_recompute.py` 后 11 条任务全部 `cleared`、`still_blocking=0`、`manual_review_required=0`，`next_action=formal_writeback_preflight`，共消费 39 条旧 gate 引用；重跑 `paper_package.py --source-manifest` 后 `agent_tasks=0`，`paper_supervisor_context.json` 继续包含 `Results/json/paper_revision_gate_recompute.json`。
- P4-I4 BDD/TDD：新增行为 21 和 `tests/test_paper_revision_gate_recompute.py::test_bdd_21_ready_evidence_packets_consume_stale_gate_task_references`；RED 为 report 仍是 `needs_revision_work`，GREEN 后进入 `ready_for_formal_writeback_preflight`。
- P4-I4 Agent Team 回收点：Erdos 只读复核下游 `paper_package.py` 消费者逻辑，确认 P4-I4 不破坏“ready 任务不重新入队”的消费者契约；主 Agent 合并 gate recompute 最小语义变更。
- P4-I 计划调用点：质量门和审稿门重跑前调用 ReviewerAgent/VerifierAgent；重跑完成后收回并把每条任务状态更新为 cleared/still_blocking/manual_review_required。
- P4-J1 已执行：新增 `Program/formal_writeback_preflight.py`，消费 `Results/json/paper_revision_gate_recompute.json`，生成正式写回预检账本 `Results/json/formal_writeback_preflight.json`、审阅稿 `Reviews/formal_writeback_preflight.md` 和预览稿 `Manuscripts/generated/previews/formal_writeback_preflight.md`。
- P4-J1 真实运行：当前状态为 `ready_for_human_approval`，写回范围 5 类：章节、引用/文献、方法叙述、结果表、复现说明；`formal_writeback_allowed=false`、`requires_human_approval=true`、`formal_state_guard.changed=false`。
- P4-J1 BDD/TDD：新增行为 22 和 `tests/test_formal_writeback_preflight.py`；RED 为缺少 `Program/formal_writeback_preflight.py`，GREEN 后覆盖 ready 和 blocked 两条路径。
- P4-J1 Agent Team 回收点：Mencius 只读复核 P4-J 上下游、正式层保护文件和 `state/product/*` 审批边界；主 Agent 合并为最小预检实现，没有改写正式 ResearchQuestion、VariableRoleSet、DesignSpec、RunPlan 或正式论文层。
- P4-J 后续 20 分钟节点规则：P5/P6 的每个子节点必须控制在 20 分钟内；超时即拆成更小节点或回退路线，不允许继续堆大黑箱。
- P5-A 已执行：新增 `Program/formal_writeback_approval.py`，消费 `Results/json/formal_writeback_preflight.json`，把人工批准记录写入 `state/product/writeback_approvals.json` 的 `formal_preflight_approvals`，并生成 `Results/json/formal_writeback_approval.json` 与 `Reviews/formal_writeback_approval.md`。
- P5-A 真实运行：当前批准状态为 `approved_for_p5`，`can_enter_p5=true`，写回范围 5 类：sections、citations、method_narrative、result_tables、reproducibility；本命令不生成正式论文包、不导出 docx、不改写正式层 state。
- P5-A BDD/TDD：新增行为 23 和 `tests/test_formal_writeback_approval.py`；RED 为缺少 `Program/formal_writeback_approval.py`，GREEN 后覆盖 approve、needs_revision、preflight blocked 三条路径。
- P5-A Agent Team 回收点：Averroes 只读复核现有 writeback approval / docx preflight / formal guard 锚点；主 Agent 复用 `writeback_approvals.json` 语义，只追加 formal preflight approval，不重造产品 API。
- P5/P6 计划调用点：正式 package 和复现交付阶段调用 VerifierAgent、ExportAgent、ReviewerAgent；manifest 复跑和最终审计完成后收回，云端产品化前不再扩展 UI。

## 2026-05-22 Long-run Optimization Protocol

- [x] 定位项目根目录：`/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`。
- [x] 读取项目 `AGENTS.md`、`Tasks/workflow.md`、`Tasks/long-run-iteration-plan.md`、`Tasks/manifest.md`、`Tasks/decision-log.md`，确认本轮只做流程文档固化。
- [x] 新增 `docs/architecture-v2/long-run-optimization-protocol.md`，定义平台期触发、策略跃迁、打破-修复和证据验收规则。
- [x] 新增 `Tasks/round-log.md`，作为长程研发轮次账本。
- [x] 将协议挂载到 `Tasks/long-run-iteration-plan.md`、`Tasks/workflow.md`、`Tasks/manifest.md`、`Tasks/decision-log.md`。
- [ ] 下一轮 P2-AA、方法执行、论文生成或产品状态机任务开始前，按 `Tasks/round-log.md` 模板记录本轮目标、平台期判断和策略选择。

## 2026-05-25 P2-AB 质量收口：Topic-first Auto Research + 前端契约修复

- [x] 按 BDD/TDD 完成 `auto-research` CLI：用户只给研究题目即可生成本地 Auto Research Run。
- [x] Auto Mode 默认 `best_available`，写入 `local_data`、`statspai`、`cnki`、`web_search`、`agentmemory`、`llm_supervisor` 能力状态；不可用能力显式记录原因。
- [x] 自动产出 `research_report.md` 和 `paper_draft_exploratory.md`，但标记 `needs_human_review` / `can_promote=false`，不能静默覆盖正式层。
- [x] 修复前端契约漂移：工作台首页恢复 topic-first 产品路径，工作台细节在确认选题后展开。
- [x] 修复 Agent Console 交互：Agent 行支持点击/键盘激活，详情只在右侧 drawer 展开，不再在主工作区重复铺开。
- [x] 浏览器验收：Playwright 截图 `journey-final-verify.png`、`journey-agent-drawer-clean-verify.png`；drawer 打开后 `inlinePanelsAfter=0`、`drawerOpen=true`。
- [x] 全量验证：`python3 -m unittest discover -s tests -v`，282 tests OK，skipped=1；`node --check Product/web/assets/app.js`、Python 编译和 scoped `git diff --check` 通过。
- [ ] 下一步 P2-AC：把 Auto Research Run 的候选层接到真实执行后端选择，优先实现 StatsPAI/Python execution adapter 的“计划 -> 执行 -> evaluator checks -> 人工审阅”闭环。

## 2026-05-25 P3 React Input And Slide Tabs

- [x] 按用户指定的两个 UI 参考，先只做研究输入器和阶段滑动导航，不扩展其他模块。
- [x] 新增 BDD：`docs/architecture-v2/codex-phase-p3-react-input-tabs-bdd.md`，锁定黑白灰、输入器、附件预览、模式选择、阶段导航和独立 React 入口。
- [x] 新增 RED 测试：`tests/test_p3_react_input_tabs.py` 首次 5 failures，原因是 `Product/web-react`、输入器、SlideTabs、样式和 App 组合入口不存在。
- [x] 新增独立 React/Vite 前端：`Product/web-react`，构建输出 `Product/web-dist`，旧 `Product/web` 保留。
- [x] 实现 `ResearchCommandInput`：题目输入、文件选择/拖拽、长文本粘贴卡片、模式选择和提交状态。
- [x] 实现 `SlideTabs`：任务书、递归搜索、数据变量、方法设计、执行实验；支持点击、hover 和键盘方向键。
- [x] 新增 `/react` FastAPI 预览入口，避免覆盖旧首页。
- [x] 视觉约束：新增 React CSS 只使用黑白灰色阶，不引入彩色强调色。
- [x] 验证：P3 单测、`npm run build`、`Product/app.py` 编译、scoped `git diff --check`、Playwright 视觉截图和全量回归通过。
- [x] 用户反馈修正：删除首屏解释性长句和“React 切片/不展开 Agent”防守性文案，改成更少、更产品化的状态提示。
- [x] 用户反馈修正：把黑白灰对比从纯黑纯白降到柔和灰阶，并接入 Three.js `DottedSurface` 点阵背景。
- [x] P3-B：新增 React Workbench 设计契约，先规范其余模块的 UI / 交互规则，再接具体业务工作流。
- [x] P3-B 设计契约锁定 10 个模块：研究入口、任务队列、递归搜索、数据与变量、方法设计、执行实验、结果解释、论文草稿、复现导出、Agent 审计。
- [x] P3-B 设计契约锁定信息披露规则：主屏只承载当前决策，默认只显示 3-5 个关键信号，详情进入右侧 Drawer 或按需展开。
- [x] P3-B 设计契约锁定视觉规则：黑白灰、低对比、DottedSurface、禁止防守性文案、不做普通 SaaS landing page。
- [x] P3-D 审阅：用 Kimi WebBridge 恢复真实浏览器检查，并用 Playwright 复现 Task Brief 页。
- [x] P3-D 审阅：确认当前 Task Brief 页的主要问题是缺少“下一步决策引导”，而不是单纯视觉 polish。
- [x] P3-D 交接：新增 `docs/architecture-v2/p3-task-brief-guided-action-review-2026-05-25.md`，把返工方向交给 Gemini/Kimi。
- [ ] 下一步 P3-C：按设计契约实现右侧审计 Drawer 和任务队列首个真实模块，不把 Agent 队列、证据台、全模块 IA 一次性铺开。

## 当前目标

把实证系统从静态阶段页推进到真实执行过程可观察：前端能选择/展示真实 run_id，读取 observability API，并渲染 run steps、events、HITL gates、产物证据、执行者和证据等级。

## 2026-05-17 P2-V Human Dispatch Audit For Agent Task Queue

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-dispatch-audit-bdd.md`，定义 Agent Task Queue item 必须先经过人工派工审阅。
- [x] TDD：新增 `tests/test_agent_task_dispatch_audit.py`，先确认缺少 `can_execute`、dispatch-review API 404、前端缺少 `reviewDispatch` 的 RED。
- [x] 后端：新增 `Product/backend/task_dispatch_service.py`，支持 `approve`、`reject`、`needs_revision` 三种派工审阅动作。
- [x] 后端：扩展 `Product/backend/agent_task_queue_service.py`，让新旧队列都显式包含 `can_execute=false`、`next_action`、`dispatch_readiness`、`dispatch_review`。
- [x] API：新增 `PUT /api/v1/projects/{project_id}/agent-task-queue/tasks/{task_id}/dispatch-review`。
- [x] 前端：在首页 Agent Task Queue 中显示派工审阅区，默认折叠输入证据、输出要求、风险和审计日志。
- [x] 验证：目标测试、相邻回归、全量 unittest、Python/JS 静态检查、`git diff --check` 和浏览器自动化点击验收通过。
- [x] 安全边界：批准派工只进入 `reviewed_for_dispatch`，仍然 `can_execute=false`，不会直接调用 StatsPAI/StataMCP/Python 或改写研究状态。
- [x] P2-W：把真实 CFPS 字段候选推进到正式 VariableRoleSet 草稿链路；正式写入仍需用户在变量角色编辑器中保存。
- [x] P2-X：给 DesignSpec/RunPlan 增加方法工作流 checklist，区分 OLS/DID/IV/RDD/PSM/DML 的可执行前置条件。
- [x] P2-Y：把审稿意见产品化为 Reviewer Scorecard；评分理由和后续任务默认折叠，低分建议不会自动写入 Agent Task Queue。

## 2026-05-17 P2-W Real VariableRoleCandidate Promotion

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-real-variable-role-promotion-bdd.md`，定义真实字段候选只能先生成可编辑草稿，不能直接成为正式研究状态。
- [x] TDD：新增 `tests/test_real_variable_role_promotion.py`，先确认 promote API 404、正式状态未受保护、前端候选/正式区分缺失的 RED。
- [x] 后端：扩展 `Product/backend/variable_role_service.py`，新增 `state/product/variable_roles_drafts.json` 读写、promotion、draft applied 标记和 provenance。
- [x] API：新增 `POST /api/v1/projects/{project_id}/variable-role-candidates/{candidate_id}/promote`，返回 `201` 和 `variable_role_set_draft`。
- [x] 前端：在候选卡上新增 `基于候选创建变量角色草稿`，保留 `仅载入编辑器` 兼容路径；正式编辑器显示 `正式变量角色`，保存时才写入 `state/product/variable_roles.json`。
- [x] 验证：目标测试、相邻回归、全量 unittest、Python/JS 静态检查、`git diff --check` 和浏览器自动化点击验收通过。
- [x] 安全边界：promotion 只写 draft 状态；不覆盖 approved VariableRoleSet，不重建 DesignSpec/RunPlan，不触发执行后端。

## 2026-05-17 P2-X Method Workflow Checklist

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-method-workflow-checklist-bdd.md`，定义 OLS/DID/IV/RDD/PSM/DML 的前置条件、诊断和阻塞规则。
- [x] TDD：新增 `tests/test_method_workflow_checklist.py`，先确认 `/method-workflows` API 404、blocked DID RunPlan 仍可保存、前端缺少方法工作流面板的 RED。
- [x] 后端：新增 `Product/backend/method_workflow_service.py`，把已确认 DesignSpec 转换为方法工作流 readiness、required inputs、diagnostics、blockers。
- [x] API：新增 `GET /api/v1/projects/{project_id}/method-workflows`，并让 `PUT /api/v1/projects/{project_id}/run-plan` 对 blocked 方法返回 409 `method_workflow_blocked`。
- [x] 前端：在 Research Design 和 Execution 页面显示方法工作流卡片；摘要显示可执行/缺什么，诊断和要求默认折叠在 `查看方法要求`。
- [x] 验证：目标测试、相邻回归、全量 unittest、Python/JS 静态检查、`git diff --check` 和 Playwright 浏览器验收通过。
- [x] 安全边界：P2-X 只做方法准入 checklist；DID/IV/RDD/PSM/DML 没有真实 StatsPAI/StataMCP/Python 执行产物，不标记 `local_execution`。

## 2026-05-17 P2-Y Reviewer Scorecard And Follow-Up Task Suggestions

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-reviewer-scorecard-bdd.md`，定义审稿意见必须结构化为评分、证据、理由和后续任务建议。
- [x] TDD：新增 `tests/test_reviewer_scorecard.py`，先确认缺少 `/reviewer-scorecard` API、状态文件和前端评分面板的 RED。
- [x] 后端：新增 `Product/backend/reviewer_score_service.py`，从 successful full run 的 `results-draft` 生成 `deterministic_baseline` Reviewer Scorecard。
- [x] API：新增 `GET /api/v1/projects/{project_id}/reviewer-scorecard` 和 `POST /api/v1/projects/{project_id}/reviewer-scorecard`。
- [x] 前端：Review & Export 页面新增 `审稿评分` 面板；五个维度摘要默认可扫读，理由、证据和后续任务通过 `查看理由与后续任务` 按需展开。
- [x] 安全边界：后续任务只显示 `加入任务队列草案` 入口提示，不自动改写 `state/product/agent_task_queue.json`。
- [x] 验证：目标测试、相邻回归、全量 unittest、Python/JS 静态检查、`git diff --check` 和 Playwright 浏览器验收通过。

## 2026-05-17 P2-Z Verifier Gates For Results, Manuscript, And Export

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-verifier-export-gates-bdd.md`，定义最终导出前必须显式通过结果绑定、复现产物、正文证据和 docx 预检。
- [x] TDD：新增 `tests/test_verifier_export_gates.py`，先确认 `/verifier-checks` API 404、缺少状态文件和前端 verifier 面板的 RED。
- [x] 后端：新增 `Product/backend/verifier_service.py`，从 export package、run plan、method execution、result artifact、draft preview 和 evidence levels 生成 verifier checks。
- [x] API：新增 `GET /api/v1/projects/{project_id}/verifier-checks` 和 `POST /api/v1/projects/{project_id}/verifier-checks/run`；没有 export package 时返回 409 `export_candidate_required`。
- [x] 前端：Review & Export 页面新增 `导出核验门` 面板，放在评分卡之后、导出包之前；每个 gate 显示状态、证据和下一步，docx 最终导出按钮受 `can_export_docx` 控制。
- [x] 安全边界：preview-ready export package 不能等同于最终导出；docx 预检仍 blocked 时，最终 docx 导出按钮保持 disabled。
- [x] 验证：目标测试、相邻回归、全量 unittest、Python 编译、JS 语法、`git diff --check` 和 Playwright 浏览器验收通过。

## 2026-05-17 Pipeline MVP Review

- [x] 全量回归：`python3 -m unittest discover -s tests -v` 已通过，258 tests OK，skipped=1。
- [x] 静态检查：`python3 -m py_compile Product/app.py Product/backend/*.py`、`node --check Product/web/assets/app.js`、`git diff --check` 已通过。
- [x] 浏览器验收：Playwright 打开 `http://127.0.0.1:8768/?v=20260517-pipeline-mvp-review-final2`，10 项主流程检查全部通过，`errors=[]`、`badResponses=[]`。
- [x] 截图留档：`artifacts/ui-checks/pipeline-mvp-home.png`、`pipeline-mvp-data-variables.png`、`pipeline-mvp-execution.png`、`pipeline-mvp-review-export.png`。
- [x] UI 修复：approved SupervisorPlan 即使缺旧版 `human_review.action`，前端也显示 `人工审批 已批准`，不再误显示 `尚未审批`。
- [x] UI 修复：`docx 最终导出` 按钮新增稳定 id `verifier-final-export-button`，浏览器验收可直接确认 disabled 状态。
- [x] 缓存治理：`Product/web/index.html` 静态资源版本更新为 `20260517-pipeline-mvp-review`。
- [ ] 下一步 P2-AA：把已人工派工审阅的 Agent Task Queue 接到真实执行后端选择；优先做 StatsPAI/Python/StataMCP backend selection BDD/TDD，仍不得自动改写变量角色、研究设计、RunPlan 或论文正文。

## 状态机

- [x] 读取项目 AGENTS.md、architecture-v2 契约、Kimi handoff、Phase A BDD
- [x] 运行基线测试：`python3 -m unittest discover -s tests -v`
- [x] 阅读 StatsPAI Agent 时代文章及其关键子链接
- [x] 固化 StatsPAI/CoPaper 方法论到项目设计依据
- [x] 为 P0 可观察执行页写 BDD 行为
- [x] 为 P0 前端行为写失败测试：首次运行 6 条失败，后续新增历史 run 缺观测文件边界测试先失败
- [x] 实现最小前端闭环：选择/展示 run_id、加载 observability、渲染 steps/events/gates/artifacts/evidence
- [x] 运行相关测试并确认通过
- [x] 启动本地服务，用浏览器验证真实页面
- [x] 更新 handoff、manifest、decision-log、review
- [x] P1 后端：增加 gate resolve API 的 BDD、失败测试和最小实现
- [x] P1-A 前端：写 HITL gate resolve 行为文档
- [x] P1-A 前端：补失败测试，覆盖 confirm/reject/adjust、note、刷新和错误提示
- [x] P1-A 前端：实现 gate resolve 最小交互
- [x] P1-A 前端：运行单测、全量回归、JS/Python 编译检查
- [x] P1-A 前端：浏览器手动验收真实 run 的 gate resolve
- [x] P1-A 交接：更新 handoff、manifest、decision-log、review
- [x] P1-B 规划：写数据集选择 -> 启动真实 run -> 查看报告 BDD
- [x] P1-B 测试：覆盖 datasets API 本地文件证据、run dataset_source、非法路径拒绝、前端数据集启动按钮
- [x] P1-B 实现：datasets API 扫描 Data 目录并标记 local_file；run 创建接收 dataset_path 并持久化 dataset_source
- [x] P1-B 前端：数据与变量页显示本地数据文件、路径、shape、role、evidence，并可启动试运行
- [x] P1-B 验证：单测、全量回归、Python/JS 语法检查、浏览器手动验收
- [x] P1-B 交接：更新 handoff、manifest、decision-log、review
- [x] P1-C 规划：写 run 数据源进入实证执行页的 BDD
- [x] P1-C 测试：覆盖 observability 顶层 dataset_source、CSV shape、执行页数据源面板
- [x] P1-C 实现：observability 返回 run 级 dataset_source，run source 增加 row_count/column_count/role
- [x] P1-C 前端：实证执行页显示 Run 数据源、路径、shape、file_type、role、evidence
- [x] P1-C 验证：目标测试、全量回归、Python/JS 语法检查、浏览器手动验收
- [x] P1-C 交接：更新 handoff、manifest、decision-log、review
- [x] P1-D 规划：写变量角色确认面板 BDD
- [x] P1-D 测试：覆盖 observability 顶层 variable_roles、gate 状态绑定、前端变量角色面板
- [x] P1-D 实现：从 dataset_intake step 提取 key_variables，并绑定 gate_dataset_fields 状态
- [x] P1-D 前端：实证执行页显示 outcome/treatment/controls/instruments 与确认 gate 状态
- [x] P1-D 验证：目标测试、全量回归、Python/JS 语法检查、浏览器手动验收
- [x] P1-D 交接：更新 handoff、manifest、decision-log、review
- [x] P1-UI 规划：写实证执行页紧凑控制台 BDD，回应当前面板过于糟糕的问题
- [x] P1-UI 测试：先让紧凑控制台布局测试失败，再实现最小 UI 修正
- [x] P1-UI 实现：运行选择、run 摘要、数据源、变量角色合并为紧凑执行上下文；执行页改用 scoped system font、小圆角、低内边距
- [x] P1-UI 验证：前端测试、全量回归、Python/JS 语法检查、桌面/移动浏览器验收
- [x] P1-UI 交接：更新 handoff、manifest、decision-log、review
- [x] 产品重置：暂停继续堆 P1-E 实现，重新梳理端到端实证论文工作台主流程
- [x] 产品重置：新增 `docs/architecture-v2/product-flow-reset-2026-05-12.md`
- [x] 产品重置下一步：写 `docs/architecture-v2/product-workflow-contract-bdd.md`，定义 canonical stages、next action、状态转移和 run blocking 行为
- [x] 产品重置实现：后端 `GET /overview` 返回 `workflow_contract`，包含 canonical stages、next action、run readiness blockers
- [x] 产品重置前端：一阶导航收敛为 5 个工作区，首页显示下一步研究决策和 workflow spine
- [x] 产品重置前端：Data & Design 先进入变量角色确认，不再从数据卡片直接启动 run
- [x] 产品重置前端：Execution 先显示 Run Plan 预检和阻塞项，再显示 run 证据
- [x] 产品重置验证：目标行为测试、全量回归、Python/JS 语法检查、桌面/移动浏览器验收
- [x] 产品重置交接：更新 handoff、manifest、decision-log、review
- [x] P1-E 规划：写 VariableRoleSet 确认闭环 BDD，把变量角色作为产品级状态对象
- [x] P1-E TDD：新增 API/前端契约测试，并确认首次失败原因是 API 404 和前端编辑器缺失
- [x] P1-E 实现：新增 VariableRoleSet 读取/保存服务与 API
- [x] P1-E 实现：让 `workflow_contract` 读取已确认 VariableRoleSet 并解除 `variable_roles_unconfirmed`
- [x] P1-E 前端：Data & Variables 显示变量角色编辑器，保存后刷新 contract
- [x] P1-E 验证：目标测试、回归测试、全量 unittest、py_compile、node --check、浏览器验收
- [x] P1-E 交接：更新 handoff、manifest、decision-log、review
- [x] P1-F 规划：DesignSpec 确认 API + UI + 持久化状态，使 workflow contract 从 `confirm_design_spec` 推进到 RunPlan
- [x] P1-F/P1-G BDD：新增 DesignSpec/RunPlan 状态机行为文档
- [x] P1-F/P1-G TDD：新增 API/前端契约测试，并确认首次失败是缺少 design-spec/run-plan API 与 UI
- [x] P1-F/P1-G 实现：新增 DesignSpec/RunPlan 产品状态服务与 API
- [x] P1-F/P1-G 实现：`workflow_contract` 读取 DesignSpec/RunPlan approval，并推进到 `start_full_run`
- [x] P1-F/P1-G 前端：Data & Design 增加 DesignSpec 编辑器，Execution 增加 RunPlan 编辑器
- [x] P1-F/P1-G 验证：目标测试、相邻回归、全量 unittest、py_compile、node --check、浏览器验收
- [x] P1-F/P1-G 交接：更新 handoff、manifest、decision-log、review
- [x] P1-H 规划：把 `start_full_run` 接到真实 full run 路径，读取 approved RunPlan 并生成 `local_execution` 证据
- [x] P1-H BDD：新增 full run from RunPlan 行为文档，明确 Feynman 只作为 callable external research engine 参考
- [x] P1-H TDD：新增 API/前端契约测试，并确认首次失败是 `/runs/full` 405 和前端缺 full-run 主按钮
- [x] P1-H 实现：新增 `POST /api/v1/projects/{project_id}/runs/full`
- [x] P1-H 实现：full run 读取 approved RunPlan，写入 `plan_binding`、`research_engine`、`execution_evidence_level`
- [x] P1-H 前端：Execution ready 后显示“启动完整实证执行”主按钮并调用 full-run API
- [x] P1-H 验证：目标测试、相邻回归、全量 unittest、py_compile、node --check、浏览器真实 full-run 验收
- [x] P1-H 交接：更新 handoff、manifest、decision-log、review
- [x] P1-I 规划：把 full-run 结果推进到 Results & Draft，形成 FindingCard / Draft evidence binding 的最小闭环
- [x] P1-I BDD：新增 Results & Draft evidence binding 行为文档，明确没有 successful full-run 时不得伪造结果
- [x] P1-I TDD：新增 API/前端契约测试，并确认首次失败是 `/results-draft` 404 和前端缺 evidence binding 容器
- [x] P1-I 实现：新增 `GET /api/v1/projects/{project_id}/results-draft`
- [x] P1-I 实现：从最新 successful full-run 读取 `Results/json/analysis_result.json` 和 run manifest，生成最小 FindingCard
- [x] P1-I 前端：Results & Draft 页面显示 FindingCard 和 DraftSection evidence binding
- [x] P1-I 验证：目标测试、相邻回归、全量 unittest、py_compile、node --check、浏览器验收
- [x] P1-J 规划：基于 FindingCard 增加 claim review / accept-for-writing 状态，决定哪些结果可以进入论文正文
- [x] P1-K 规划：让 Manuscript 阶段只消费 `can_write_to_draft=true` 的 approved FindingCard，生成可审阅段落而不是直接覆盖正文
- [x] P1-K BDD：新增 Manuscript consumption 行为文档，定义 approved finding、provenance、空状态和前端容器
- [x] P1-K TDD：新增失败测试，确认首次失败是 `/manuscript-candidates` API 404 和前端缺少 candidate 容器/API/渲染函数
- [x] P1-K 实现：新增 Manuscript candidate 服务和 API，从 approved FindingCard 派生正文候选
- [x] P1-K 前端：Results & Draft 显示 Manuscript candidates 和 source/result/review provenance
- [x] P1-K 验证：目标测试、相邻回归、全量 unittest、py_compile、node --check、API 和浏览器验收
- [x] P1-L 规划：给 Manuscript candidate 增加人工审阅/确认状态，再考虑 promote/write-back/export
- [x] P1-L BDD：新增 Manuscript candidate review 行为文档，定义 candidate review、can_promote、非法 action/candidate 和前端操作
- [x] P1-L TDD：扩展 `tests/test_manuscript_consumption.py`，确认首次失败是缺少 `review_status/can_promote`、review API 404、前端缺少 candidate review 操作
- [x] P1-L 实现：新增 candidate review 持久化到 `state/product/manuscript_candidate_reviews.json`
- [x] P1-L 前端：Manuscript candidate 卡片显示 review_status/can-promote、审阅备注和 approve/needs_revision/reject 操作
- [x] P1-L 验证：目标测试、相邻回归、全量 unittest、py_compile、node --check、API 和浏览器验收
- [ ] P1-M 规划：approved candidate 的 promote/write-back/export preflight
- [ ] P2-L：把字段画像推进为“字段审阅 / VariableRoleSet 候选生成”状态机，但仍必须人工确认，不允许自动改写研究状态。

## Review

- 新增 `tests/test_observable_execution_frontend.py`，覆盖 7 条 P0 前端行为。
- 扩展 `tests/test_observable_execution.py`，覆盖 P1 gate resolve 写回 gates、追加 events、更新 manifest、拒绝非法 action。
- P1-A 扩展 `tests/test_observable_execution_frontend.py` 到 10 条行为，覆盖 gate resolve 前端交互。
- 最终回归：`python3 -m unittest discover -s tests -v`，59 tests OK，skipped=1，最终一次耗时 5.570s。
- P1-B 最终回归：`python3 -m unittest discover -s tests -v`，65 tests OK，skipped=1，耗时 11.121s。
- P1-C 最终回归：`python3 -m unittest discover -s tests -v`，67 tests OK，skipped=1，耗时 36.309s。
- P1-D 最终回归：`python3 -m unittest discover -s tests -v`，69 tests OK，skipped=1，耗时 8.408s。
- P1-UI 最终回归：`python3 -m unittest discover -s tests -v`，70 tests OK，skipped=1，耗时 5.553s。
- Python 编译检查和 JS 语法检查通过。
- 浏览器验收使用 `http://127.0.0.1:8877`，真实 run `run_3ffe1e6c1f53` 可渲染完整 observability；历史 run `run_c617f095b232` 缺少观测文件时显示可恢复提示。
- 浏览器验收使用 `http://127.0.0.1:8765/?v=20260512-p1a`，真实 run `run_3ffe1e6c1f53` 的 `gate_dataset_fields` 已通过页面 confirm，显示 action/note/resolved_at，并刷新出 resolved 事件。
- P1-B 浏览器验收使用 `http://127.0.0.1:8765/?v=20260512-p1b3`：数据页显示 `analysis_sample.csv`、`本地文件`、`12 行 · 4 列 · csv · configured_final_dataset`、`Data/Final/analysis_sample.csv`；点击“用此数据启动试运行”后生成 `run_fc725d15b3c0`，manifest 写入 `dataset_source.evidence_level=local_file`。
- P1-C 浏览器验收使用 `http://127.0.0.1:8765/?v=20260512-p1c`：从数据页启动新 run `run_641c9770a1a8`，实证执行页 Run 数据源显示 `analysis_sample.csv`、`Data/Final/analysis_sample.csv`、`本地文件`、`12 行 · 4 列`、`csv`、`configured_final_dataset`；console errors/warnings=0。
- P1-D 浏览器验收使用 `http://127.0.0.1:8765/?v=20260512-p1d`：`run_641c9770a1a8` 的变量角色确认面板显示 `gate=gate_dataset_fields · status=open`、`outcome=wage`、`treatment=trained`、`controls=edu, experience`、`instruments=未识别`；console errors/warnings=0。
- P1-UI 浏览器验收使用 `http://127.0.0.1:8765/?v=20260512-p1ui3`：执行页 font 为 `-apple-system` 系统字体、panel radius `8px`、padding `12px`、桌面无横向溢出；移动端 390x844 下 `overflowCount=0`，metadata 使用 `pre-wrap`。
- 产品重置 TDD 失败证据：`python3 -m unittest tests.test_product_workflow_contract -v` 最初 2 条 API 测试因 `KeyError: workflow_contract` 报错，4 条前端测试因缺少 5 个工作区、`renderWorkflowContract`、`data-open-design-action`、`renderExecutionPreflight` 失败。
- 产品重置目标测试：`python3 -m unittest tests.test_product_workflow_contract tests.test_dataset_frontend tests.test_observable_execution_frontend -v`，23 tests OK。
- 产品重置最终回归：`python3 -m unittest discover -s tests -v`，76 tests OK，skipped=1，耗时 6.385s。
- 产品重置编译/语法：`python3 -m py_compile Program/run_paper.py Program/workbench/observability.py Product/backend/observability_service.py Product/backend/project_service.py Product/backend/overview_service.py Product/app.py` 通过；`node --check Product/web/assets/app.js` 通过。
- 产品重置浏览器验收使用 `http://127.0.0.1:8765/?v=20260512-flow2`：Workspace Home 显示 5 个工作区、下一步 `confirm_variable_roles`、9 个 workflow spine 阶段；Data & Design 显示 `analysis_sample.csv` 和“检查并确认变量角色”，无“用此数据启动试运行”；Execution 显示 `can_start_full_run=false` 和 `variable_roles_unconfirmed/design_unconfirmed/run_plan_missing`，桌面和 390x844 移动端均无横向溢出，console errors/warnings=0。
- P1-E TDD 失败证据：`python3 -m unittest tests.test_variable_role_confirmation -v` 首次 5 条失败，原因是 `GET/PUT /api/v1/projects/{project_id}/variable-roles` 返回 404，且前端缺少 `variable-role-confirmation-form`、`renderVariableRoleEditor` 和保存 API。
- P1-E 目标测试：`python3 -m unittest tests.test_variable_role_confirmation -v`，5 tests OK。
- P1-E 目标回归：`python3 -m unittest tests.test_variable_role_confirmation tests.test_product_workflow_contract tests.test_dataset_frontend tests.test_observable_execution_frontend tests.test_api_contract_v2 -v`，39 tests OK。
- P1-E 最终回归：`python3 -m unittest discover -s tests -v`，81 tests OK，skipped=1，耗时 8.594s。
- P1-E 编译/语法：`python3 -m py_compile Product/app.py Product/backend/overview_service.py Product/backend/variable_role_service.py Product/backend/project_service.py Product/backend/observability_service.py Program/run_paper.py Program/workbench/observability.py` 通过；`node --check Product/web/assets/app.js` 通过。
- P1-E 浏览器验收使用 `http://127.0.0.1:8765/?v=20260513-p1e`：Data & Variables 显示 VariableRoleSet 编辑器，保存后状态为 `approved · local_file`，`workflow_contract.next_action.id=confirm_design_spec`，blockers 只剩 `design_unconfirmed/run_plan_missing`；Execution preflight 仍正确阻止 full run；console errors/warnings=0，桌面无横向溢出。
- P1-F/P1-G TDD 失败证据：`python3 -m unittest tests.test_design_run_plan_state_machine -v` 首次 7 条失败；5 条 API 测试因 `/design-spec`、`/run-plan` 返回 404，2 条前端测试因缺少 DesignSpec/RunPlan 表单、渲染函数和保存 API 失败。
- P1-F/P1-G 目标测试：`python3 -m unittest tests.test_design_run_plan_state_machine -v`，7 tests OK。
- P1-F/P1-G 目标回归：`python3 -m unittest tests.test_design_run_plan_state_machine tests.test_variable_role_confirmation tests.test_product_workflow_contract tests.test_dataset_frontend tests.test_observable_execution_frontend tests.test_api_contract_v2 -v`，46 tests OK。
- P1-F/P1-G 编译/语法：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/overview_service.py Product/backend/variable_role_service.py Product/backend/design_spec_service.py Product/backend/project_service.py Product/backend/observability_service.py Program/run_paper.py Program/workbench/observability.py` 通过。
- P1-F/P1-G 浏览器验收使用 `http://127.0.0.1:8765/?v=20260513-p1fg`：保存 DesignSpec 后状态为 `approved · local_file`，`workflow_contract.next_action.id=confirm_run_plan`，blockers 只剩 `run_plan_missing`；保存 RunPlan 后状态为 `approved · local_file`，`next_action.id=start_full_run`，blockers 为空，`can_start_full_run=true`；console errors/warnings=0，执行页无横向溢出。
- P1-F/P1-G 最终回归：`python3 -m unittest discover -s tests -v`，88 tests OK，skipped=1，耗时 83.833s。
- P1-H TDD 失败证据：`python3 -m unittest tests.test_full_run_from_run_plan -v` 首次 3 条失败；2 条 API 测试因 `POST /runs/full` 返回 405，1 条前端测试因缺少 `observable-run-full-button`、`v2api.runs.startFull`、`createFullRunFromPlan` 失败。
- P1-H 目标测试：`python3 -m unittest tests.test_full_run_from_run_plan -v`，3 tests OK。
- P1-H 目标回归：`python3 -m unittest tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_v1_local tests.test_observable_execution tests.test_observable_execution_frontend tests.test_product_workflow_contract -v`，39 tests OK。
- P1-H 编译/语法：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/project_service.py Product/backend/design_spec_service.py Product/backend/overview_service.py Product/backend/observability_service.py` 通过。
- P1-H 浏览器验收使用 `http://127.0.0.1:8765/?v=20260513-p1h`：Execution preflight 显示 `start_full_run` ready；点击“启动完整实证执行”生成 `run_c424d6a11af7`，run mode=`full-run`、status=`succeeded`、`execution_evidence_level=local_execution`；manifest 写入 `run_plan_binding.evidence_level=local_file` 和 `research_engine.embedded=false/integration_mode=callable_external`；console errors/warnings=0。
- P1-H 最终回归：`python3 -m unittest discover -s tests -v`，91 tests OK，skipped=1，耗时 6.591s。
- P1-I TDD 失败证据：`python3 -m unittest tests.test_results_draft_evidence_binding -v` 首次有效失败为 4 条；3 条 API 测试因 `/api/v1/projects/{project_id}/results-draft` 返回 404，1 条前端测试因缺少 `results-findings-list`、`draft-evidence-sections`、`v2api.resultsDraft.get`、`renderResultsDraftEvidence` 失败。
- P1-I 目标测试：`python3 -m unittest tests.test_results_draft_evidence_binding -v`，4 tests OK。
- P1-I 目标回归：`python3 -m unittest tests.test_results_draft_evidence_binding tests.test_full_run_from_run_plan tests.test_design_run_plan_state_machine tests.test_product_workflow_contract tests.test_api_contract_v2 -v`，31 tests OK。
- P1-I 编译/语法：`node --check Product/web/assets/app.js` 通过；`python3 -m py_compile Product/app.py Product/backend/results_draft_service.py Product/backend/draft_service.py Product/backend/project_service.py` 通过。
- P1-I API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/results-draft` 返回 `latest_run_id=run_c424d6a11af7`、`findings[0].treatment=trained`、`estimate=1.8505076802915557`、`artifact_path=Results/json/analysis_result.json`、`draft_sections` 绑定 `claim_evidence_level=local_execution`。
- P1-I 浏览器验收使用 `http://127.0.0.1:8765/?v=20260513-p1i`：Results & Draft 显示 `trained effect on wage`、`run_id=run_c424d6a11af7`、`run_plan_version=1`、`Results/json/analysis_result.json`；Draft evidence binding 显示 `Manuscripts/generated/paper_draft.md`、本地文件证据和真实执行证据；overflowCount=0，console errors/warnings=0。
- P1-I 全量回归：`python3 -m unittest discover -s tests -v`，95 tests OK，skipped=1，耗时 6.788s。

## 2026-05-13 P1-E VariableRoleSet 确认闭环

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-variable-role-confirmation-bdd.md`，把变量角色确认定义为真实产品对象。
- [x] TDD：新增 API/前端契约测试，先确认失败原因是功能未实现。
- [x] 实现：新增 VariableRoleSet 读取/保存服务与 API。
- [x] 实现：让 `workflow_contract` 读取已确认 VariableRoleSet 并解除 `variable_roles_unconfirmed`。
- [x] 实现：Data & Variables 显示变量角色编辑器，保存后刷新 contract。
- [x] 验证：运行目标测试、全量 unittest、py_compile、node --check、浏览器验收。

## 2026-05-13 P1-F/P1-G DesignSpec 与 RunPlan 状态机

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-design-run-plan-bdd.md`，定义 DesignSpec/RunPlan 的产品级确认行为。
- [x] TDD：新增 `tests/test_design_run_plan_state_machine.py`，先确认 API 404 和前端缺表单/函数的失败。
- [x] 实现：新增 `Product/backend/design_spec_service.py`，读写 `state/product/design_spec.json` 与 `state/product/run_plan.json`。
- [x] 实现：新增 `GET/PUT /api/v1/projects/{project_id}/design-spec` 和 `GET/PUT /api/v1/projects/{project_id}/run-plan`。
- [x] 实现：`workflow_contract` 读取 approved VariableRoleSet、DesignSpec、RunPlan，依次推进到 `confirm_design_spec`、`confirm_run_plan`、`start_full_run`。
- [x] 前端：Data & Design 增加 DesignSpec 确认表单；Execution 增加 RunPlan 确认表单。
- [x] 验证：目标测试 7 OK、目标回归 46 OK、全量回归 88 OK、Python/JS 静态检查通过、浏览器保存链路通过。

## 2026-05-13 P1-H Full Run From RunPlan

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-full-run-from-run-plan-bdd.md`，定义 full run 必须从 approved RunPlan 启动。
- [x] TDD：新增 `tests/test_full_run_from_run_plan.py`，先确认 `/runs/full` 和前端 full-run 主按钮未实现。
- [x] 实现：新增 `execute_full_run_from_run_plan()` 和 `POST /api/v1/projects/{project_id}/runs/full`。
- [x] 实现：full run response 与 manifest 绑定 `plan_binding`、`research_engine`、`execution_evidence_level`。
- [x] 前端：Execution 页面新增 `observable-run-full-button`，ready 后调用 `v2api.runs.startFull()`。
- [x] 验证：目标测试 3 OK、目标回归 39 OK、全量回归 91 OK、Python/JS 静态检查通过、浏览器真实 full-run 通过。

## 2026-05-13 P1-I Results & Draft Evidence Binding

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-results-draft-evidence-binding-bdd.md`，定义 FindingCard / DraftSection evidence binding。
- [x] TDD：新增 `tests/test_results_draft_evidence_binding.py`，先确认 API 404 和前端缺少 evidence binding 容器/渲染函数。
- [x] 实现：新增 `Product/backend/results_draft_service.py`，从最新 successful full-run、`analysis_result.json`、`paper_draft.md` 组装 evidence binding。
- [x] 实现：新增 `GET /api/v1/projects/{project_id}/results-draft`，无 full-run 时返回 409 `full_run_required`。
- [x] 前端：Results & Draft 页面显示 FindingCard 与 DraftSection evidence binding，区分 `local_execution` 与 `local_file`。
- [x] 验证：目标测试 4 OK、目标回归 31 OK、全量回归 95 OK、Python/JS 静态检查通过、浏览器真实结果绑定通过。

## 2026-05-13 P1-J Claim Review / Accept-for-writing

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-claim-review-bdd.md`，定义 FindingCard 人工审阅与 accept-for-writing 行为。
- [x] TDD：扩展 `tests/test_results_draft_evidence_binding.py`，先确认缺少 `review_status`、review API 404、前端缺少 review 操作。
- [x] 实现：扩展 `Product/backend/results_draft_service.py`，把 review 状态保存到 `state/product/finding_reviews.json`。
- [x] 实现：新增 `PUT /api/v1/projects/{project_id}/results-draft/findings/{finding_id}/review`，支持 `approve`、`reject`、`needs_revision`。
- [x] 前端：FindingCard 显示 `review_status`、`accept-for-writing`、审阅备注、approve/needs_revision/reject 操作。
- [x] 验证：目标测试 8 OK、目标回归 35 OK、全量回归 99 OK、Python/JS 静态检查通过、浏览器真实 approve 验收通过。
- [x] P1-K 规划：让 Manuscript 阶段只消费 `can_write_to_draft=true` 的 approved FindingCard，生成可审阅段落而不是直接覆盖正文。

## 2026-05-13 P1-K Manuscript Consumption

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-manuscript-consumption-bdd.md`，定义 Manuscript candidate 只消费 approved FindingCard。
- [x] TDD：新增 `tests/test_manuscript_consumption.py`，首次运行 5 条失败，原因是 `/api/v1/projects/{project_id}/manuscript-candidates` 返回 404，前端缺少 `manuscript-candidates-list`、`v2api.manuscriptCandidates.get`、`renderManuscriptCandidates`。
- [x] 实现：新增 `Product/backend/manuscript_candidate_service.py`，从 `GET /results-draft` 的 `can_write_to_draft=true`、`review_status=approved` FindingCard 派生正文候选。
- [x] 实现：新增 `GET /api/v1/projects/{project_id}/manuscript-candidates`，空状态返回 `approved_finding_required`，不修改 `Manuscripts/generated/paper_draft.md`。
- [x] 前端：Results & Draft 页面新增 `manuscript-candidates-list`，显示候选段落、finding/run/run_plan 绑定，以及 `source_draft`、`result_artifact`、`review_decision` provenance。
- [x] 验证：目标测试 5 OK、相邻回归 40 OK、全量回归 104 OK、Python/JS 静态检查通过、API 和浏览器真实验收通过。
- [x] P1-L：新增 Manuscript candidate review/promote 状态机。

## 2026-05-13 P1-L Manuscript Candidate Review

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-manuscript-candidate-review-bdd.md`，定义正文候选必须独立人工审阅。
- [x] TDD：扩展 `tests/test_manuscript_consumption.py` 到 10 条行为；首次运行失败原因是 candidate 缺少 `review_status`、review API 404、前端缺少 candidate review 操作。
- [x] 实现：扩展 `Product/backend/manuscript_candidate_service.py`，新增 `save_project_manuscript_candidate_review()`、`load_candidate_reviews()` 和 `candidate_review` provenance。
- [x] 实现：新增 `PUT /api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/review`。
- [x] 前端：Results & Draft candidate 卡片显示 `review_status`、`can-promote`、candidate review 备注与 approve/needs_revision/reject 操作。
- [x] 验证：目标测试 10 OK、相邻回归 45 OK、全量回归 109 OK、Python/JS 静态检查通过、API 和浏览器真实验收通过。
- [x] P1-M：approved candidate 的 promote/write-back/export preflight。
- [x] P1-N：ready_for_export candidate 生成 write-back preview 和 export package manifest，不直接覆盖源草稿。

## 2026-05-13 P1-M Manuscript Promote Preflight

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-manuscript-promote-preflight-bdd.md`，定义 promote 只是导出前检查，不直接覆盖 `paper_draft.md`。
- [x] TDD：扩展 `tests/test_manuscript_consumption.py` 到 15 条行为；首次运行失败原因是 `/promote` API 404、前端缺少 `promotion_status`、`promoteManuscriptCandidate` 和 `data-candidate-promote-action`。
- [x] 实现：扩展 `Product/backend/manuscript_candidate_service.py`，新增 `save_project_manuscript_candidate_promotion()`、promotion state 读写和 `promotion_state` provenance。
- [x] 实现：新增 `POST /api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/promote`，未 approved candidate 返回 409 `candidate_review_required`。
- [x] 前端：Results & Draft candidate 卡片显示 `promotion_status`、`can_write_back`、promotion evidence 和“进入导出前检查”操作。
- [x] 验证：目标测试 15 OK、相邻回归 50 OK、全量回归 114 OK、Python/JS 静态检查通过、API 和浏览器真实验收通过。
- [x] P1-N：为 `ready_for_export` candidate 设计 write-back draft / export package manifest，不直接覆盖源草稿。

## 2026-05-13 P1-N Export Preflight Preview

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-export-preflight-bdd.md`，定义 export preflight 只生成预览和 manifest。
- [x] TDD：扩展 `tests/test_manuscript_consumption.py` 到 19 条行为；首次运行失败原因是 `/export-preflight` API 404、前端缺少 `export_status`、`preview_ready`、`writeback_preview_path`、`exportPreflightManuscriptCandidate` 和 `data-candidate-export-preflight-action`。
- [x] 实现：扩展 `Product/backend/manuscript_candidate_service.py`，新增 `save_project_manuscript_candidate_export_preflight()`、preview 文件生成、export package manifest 读写和 `export_package` provenance。
- [x] 实现：新增 `POST /api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/export-preflight`，未 `ready_for_export` candidate 返回 409 `candidate_promotion_required`。
- [x] 前端：Results & Draft candidate 卡片显示 `export_status`、`writeback_preview_path`、`export_manifest_path`、export evidence 和“生成写回预览”操作。
- [x] 验证：目标测试 19 OK、相邻回归 54 OK、全量回归 118 OK、Python/JS 静态检查通过、API 验收通过；浏览器插件最终传输中断，已用 API/DOM/static fallback 复核。
- [x] P1-O：把 export preflight 接入 Review & Export 页面，形成导出包验收台、evaluator checks 和 Frontier-Eng iteration log。

## 2026-05-13 P1-O Review & Export Package Workbench

## 2026-05-16 P2-R ResearchQuestion / TopicSession 持久化

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-research-question-topic-session-bdd.md`，定义首页确认选题后必须生成可跨 Session 恢复的 ResearchQuestion 状态。
- [x] TDD：新增 `tests/test_research_question_topic_session.py`，并扩展 `tests/test_product_workflow_contract.py`，首次运行失败原因是 `/research-question/current` API 404 和前端只依赖本地状态。
- [x] 实现：新增 `Product/backend/research_question_service.py`，读写 `state/product/research_question.json`，未确认时只返回 project seed draft，不创建状态文件。
- [x] 实现：新增 `GET/PUT /api/v1/projects/{project_id}/research-question/current`。
- [x] 实现：`GET /overview` 暴露 `research_question_state`，并让 `workflow_contract` 中 ResearchQuestion 阶段按 confirmed 状态推进。
- [x] 前端：首页“进入研究判断”调用后端保存 ResearchQuestion，保存后刷新 overview；静态资源版本更新到 `20260516-p2r-topic-session1`。
- [x] 验证：目标测试 15 OK，核心回归 36 OK，全量回归 219 OK、skipped=1，Python/JS 静态检查通过，浏览器验收通过。
- [x] 交接：更新 `Tasks/handoff.md`、`Tasks/decision-log.md`、`Tasks/manifest.md`、`Tasks/review.md`。
- [ ] P2-S：把 ResearchQuestion 作为 SupervisorPlan 输入，生成人工可审阅的 plan artifact，不自动改写 VariableRoleSet、DesignSpec 或 RunPlan。

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-review-export-package-bdd.md`，定义 Review & Export 必须读取 `preview_ready` export package，并显示 evaluator、证据路径和下一轮迭代。
- [x] TDD：新增 `tests/test_review_export_package.py`；首次运行 4 条失败，失败原因是 `/api/v1/projects/{project_id}/export-package` 404，前端缺少 `export-package-workbench`、`export-evaluator-checks`、`frontier-iteration-log` 和返回 Results & Draft 的入口。
- [x] 实现：扩展 `Product/backend/manuscript_candidate_service.py`，新增 `get_project_export_package()`，把 export preflight manifest 组装为 Review & Export 包。
- [x] 实现：扩展 `Product/app.py`，新增 `GET /api/v1/projects/{project_id}/export-package`。
- [x] 前端：Review & Export 页面新增 `export-package-workbench`，显示 candidate/run/section、`export_status=preview_ready`、`evaluator=passed`、writeback preview、manifest、result artifact、`can_write_back=false`。
- [x] 前端：新增 Frontier-Eng 式 `objective -> baseline -> evaluator -> feedback -> next_iteration` 迭代日志，并提供“回到 Results & Draft 查看候选来源”。
- [x] 验证：目标测试 4 OK、相邻回归 31 OK、全量回归 122 OK、Python/JS 静态检查通过、Chrome 可视化验收通过。
- [x] 交接：更新 handoff、manifest、decision-log、review、current-stage、workflow。

## 2026-05-13 P1-Q Chinese Copy + Archive Interface

- [x] 中文化 BDD：新增 `docs/architecture-v2/codex-phase-p1-chinese-copy-bdd.md`，定义用户可见页面文案改为同义中文，API 字段和证据枚举不翻译。
- [x] 中文化 TDD：新增 `tests/test_frontend_chinese_copy.py`，并更新相邻前端契约测试，先锁定一级导航、阶段标题、执行/导出页面中文文案。
- [x] 中文化实现：更新 `Product/web/index.html` 与 `Product/web/assets/app.js`，把核心页面、按钮、状态说明和 workflow 文案切换为中文展示。
- [x] 档案界面 BDD：新增 `docs/architecture-v2/codex-phase-p1-archive-interface-bdd.md`，定义研究档案身份、相邻笔记、证据图例、收藏架和交互状态。
- [x] 档案界面 TDD：新增 `tests/test_archive_interface_visual_contract.py`；首次运行 4 条失败，原因是页面缺少 `研究档案`、`archive-inspector`、`archive-ledger`、hover/focus/loading/empty/error 状态标识。
- [x] 实现：在 `Product/web/index.html` 增加 `archive-shell` 和右侧 `archive-inspector`；在 `Product/web/assets/app.js` 增加 `archivePageNotes`、`mountArchiveInspector()`、`updateArchiveInspector()`；在 `Product/web/assets/styles.css` 增加纸张网格、档案条目、相邻笔记、证据 ledger、hover/focus/loading/empty/error 状态。
- [x] 验证：`python3 -m unittest tests.test_archive_interface_visual_contract -v` 5 tests OK；`python3 -m unittest discover -s tests -v` 132 tests OK，skipped=1；`node --check Product/web/assets/app.js` 通过；Python 编译检查通过；Safari 可视化验收 `http://127.0.0.1:8765/?v=20260513-archive1` 通过。
- [x] 交接：更新 handoff、manifest、decision-log、review、current-stage、workflow。

## 2026-05-13 P1-P Writeback Approval + DOCX Preflight

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-writeback-docx-preflight-bdd.md`，定义显式写回审批、docx 导出预检和 Review & Export 证据验收台。
- [x] TDD：扩展 `tests/test_review_export_package.py` 到 9 条行为；首次运行失败原因是导出包缺少 `writeback_approval`/`docx_preflight` 状态、POST API 404、前端缺少 clean evidence bench 结构。
- [x] 实现：扩展 `Product/backend/manuscript_candidate_service.py`，新增 `writeback_approvals.json` 与 `docx_export_preflight.json` 两类本地状态；审批只写状态，不覆盖 `Manuscripts/generated/paper_draft.md`。
- [x] 实现：扩展 `Product/app.py`，新增 `POST /api/v1/projects/{project_id}/export-package/{candidate_id}/writeback-approval` 与 `POST /api/v1/projects/{project_id}/export-package/{candidate_id}/docx-preflight`。
- [x] 前端：把 Review & Export 改成 `review-export-evidence-bench`，用证据表、写回审批面板、docx 预检面板替代拥挤的路径卡片堆。
- [x] 验证：目标测试 9 OK；相邻回归 36 OK；全量回归 142 OK，skipped=1；Python 编译和 JS 语法检查通过。
- [x] 可视化验收：重启 8765 旧服务后，Safari + Computer Use 验证“批准写回 -> 运行 docx 预检”闭环，页面显示 `写回：已审批` 和 `预检通过`。
- [x] 交接：更新 handoff、manifest、decision-log、review。

## 2026-05-13 P1-R Clean Workbench Visual Pass

- [x] 参考研究：读取 JupyterLab / Grafana / OpenMetadata 的公开产品文档，提炼为“主工作区 + 属性检查器 + 信息面板/记录，而不是装饰卡片堆叠”。
- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-clean-workbench-bdd.md`，定义清洁工作台、变量角色入口不重叠、右侧属性检查器、record/list 替代大卡片。
- [x] TDD：新增 `tests/test_clean_workbench_visual_contract.py`；首次运行 4 失败 1 通过，失败原因是仍存在纸格背景、auto 双列、右侧档案索引过重、缺少 record/list 结构。
- [x] 实现：去掉 archive shell 的纸格噪声和厚重阴影，右侧 `archive-inspector` 调整为 `inspector-rail`，变量角色确认入口改为单列 `research-record-card` + `research-step-list`。
- [x] 实现：修复截图中的重叠根因，`.variable-role-workflow-layout` 不再使用 `minmax(0, 1fr) auto`，长路径使用 `overflow-wrap:anywhere`。
- [x] 验证：目标视觉契约测试 15 OK，全量回归 137 OK，Python 编译检查通过，`node --check Product/web/assets/app.js` 通过。
- [x] 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-clean1`，数据与设计页变量角色入口无重叠，右侧为属性检查器，整体背景变干净。
- [x] 交接：更新 handoff、manifest、decision-log、review、current-stage、workflow。

## 2026-05-13 P1-R Clean Workbench Visual Pass

- [x] 参考研究：读取 JupyterLab / Grafana / OpenMetadata 的公开产品文档，提炼为“主工作区 + 属性检查器 + 信息面板/记录，而不是装饰卡片堆叠”。
- [x] BDD：新增 `docs/architecture-v2/codex-phase-p1-clean-workbench-bdd.md`，定义清洁工作台、变量角色入口不重叠、右侧属性检查器、record/list 替代大卡片。
- [x] TDD：新增 `tests/test_clean_workbench_visual_contract.py`；首次运行 4 失败 1 通过，失败原因是仍存在纸格背景、auto 双列、右侧档案索引过重、缺少 record/list 结构。
- [x] 实现：去掉 archive shell 的纸格噪声和厚重阴影，右侧 `archive-inspector` 调整为 `inspector-rail`，变量角色确认入口改为单列 `research-record-card` + `research-step-list`。
- [x] 实现：修复截图中的重叠根因，`.variable-role-workflow-layout` 不再使用 `minmax(0, 1fr) auto`，长路径使用 `overflow-wrap:anywhere`。
- [x] 验证：目标视觉契约测试 15 OK，全量回归 137 OK，Python 编译检查通过，`node --check Product/web/assets/app.js` 通过。
- [x] 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-clean1`，数据与设计页变量角色入口无重叠，右侧为属性检查器，整体背景变干净。
- [x] 交接：更新 handoff、manifest、decision-log、review、current-stage、workflow。

## 2026-05-13 P1-Q Chinese Copy + Archive Interface

- [x] 中文化 BDD：新增 `docs/architecture-v2/codex-phase-p1-chinese-copy-bdd.md`，定义用户可见页面文案改为同义中文，API 字段和证据枚举不翻译。
- [x] 中文化 TDD：新增 `tests/test_frontend_chinese_copy.py`，并更新相邻前端契约测试，先锁定一级导航、阶段标题、执行/导出页面中文文案。
- [x] 中文化实现：更新 `Product/web/index.html` 与 `Product/web/assets/app.js`，把核心页面、按钮、状态说明和 workflow 文案切换为中文展示。
- [x] 档案界面 BDD：新增 `docs/architecture-v2/codex-phase-p1-archive-interface-bdd.md`，定义研究档案身份、相邻笔记、证据图例、收藏架和交互状态。
- [x] 档案界面 TDD：新增 `tests/test_archive_interface_visual_contract.py`；首次运行 4 条失败，原因是页面缺少 `研究档案`、`archive-inspector`、`archive-ledger`、hover/focus/loading/empty/error 状态标识。
- [x] 实现：在 `Product/web/index.html` 增加 `archive-shell` 和右侧 `archive-inspector`；在 `Product/web/assets/app.js` 增加 `archivePageNotes`、`mountArchiveInspector()`、`updateArchiveInspector()`；在 `Product/web/assets/styles.css` 增加纸张网格、档案条目、相邻笔记、证据 ledger、hover/focus/loading/empty/error 状态。
- [x] 验证：`python3 -m unittest tests.test_archive_interface_visual_contract -v` 5 tests OK；`python3 -m unittest discover -s tests -v` 132 tests OK，skipped=1；`node --check Product/web/assets/app.js` 通过；Python 编译检查通过；Safari 可视化验收 `http://127.0.0.1:8765/?v=20260513-archive1` 通过。
- [x] 交接：更新 handoff、manifest、decision-log、review、current-stage、workflow。
## 2026-05-13 P2-A Dataset Quality Profile

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-data-quality-profile-bdd.md`，定义数据集必须先生成本地文件证据级质量画像，再进入变量角色/研究设计。
- [x] TDD：新增 `tests/test_dataset_quality_profile.py`；首次运行失败原因是 `/datasets` 返回的数据集缺少 `quality_profile`，前端缺少数据质量画像面板。
- [x] 实现：扩展 `Product/backend/overview_service.py`，CSV 数据集返回 `quality_profile`，包含行列数、缺失单元格、缺失率、数值/文本字段数、字段画像和检查项；暂不支持的真实文件保留 `evidence_level=local_file` 并标记 `not_profiled`。
- [x] 前端：扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，数据与设计页新增“数据质量画像”，并把数据集、质量画像、变量角色编辑器改成纵向 clean workbench 顺序，避免与右侧属性检查器挤压。
- [x] 中文化修正：扩展 `tests/test_frontend_chinese_copy.py`，防止 `dataset_quality_profile` / `confirm_variable_roles` 这类内部标签重新出现在可见 eyebrow 文案。
- [x] 验证：`python3 -m unittest discover -s tests -v`，148 tests OK，skipped=1；Python 编译检查通过；`node --check Product/web/assets/app.js` 通过。
- [x] 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2a`，进入“数据与设计”后可见 `analysis_sample.csv`、`数据质量画像`、样本 12、缺失率 0%、字段画像和中文标签；布局不再出现两列挤压。
- [x] P2-B：设计 StatsPAI/CoPaper 式方法技能集目录，把 OLS/DID/IV/RDD/PSM/DML 等方法的前置变量要求和可执行状态接入 RunPlan。

## 2026-05-13 P2-B Method Skill Catalog

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-method-skill-catalog-bdd.md`，定义 RunPlan 必须暴露方法技能集、前置变量、阻塞原因和默认可执行方法。
- [x] TDD：新增 `tests/test_method_skill_catalog.py`；首次运行失败原因是 RunPlan 缺少 `method_catalog`、任务缺少 `method_id`、前端缺少 `method-skill-catalog-panel`。
- [x] 实现：扩展 `Product/backend/design_spec_service.py`，从已确认 DesignSpec / VariableRoleSet 派生 OLS、DID、IV、RDD、PSM、DML 方法目录；所有条目标记 `evidence_level=local_file`。
- [x] 实现：默认 RunPlan 只加入当前 ready 的 OLS baseline 任务，DID/IV/RDD 等方法只展示阻塞原因，不伪装为已执行。
- [x] 前端：研究设计页新增“方法技能集”，显示 StatsPAI/CoPaper 前置条件、方法可执行状态、执行者、证据等级、前置要求和阻塞原因。
- [x] 视觉修正：方法目录改为纵向 clean workbench 证据清单，避免双列卡片在 Safari 中继续拥挤。
- [x] 验证：`python3 -m unittest discover -s tests -v`，152 tests OK，skipped=1；Python 编译和 JS 语法检查通过；API / Safari 可视化验收通过。
- [x] P2-C：把方法目录推进到真实方法执行适配器设计，优先选择一个最小 OLS/StatsPAI/Stata 执行路径，并把结果写成 `local_execution` 证据。

## 2026-05-13 P2-C OLS Execution Adapter

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-ols-execution-adapter-bdd.md`，定义 approved OLS RunPlan 必须生成本地方法执行结果、绑定 RunPlan/数据集/公式、写入 manifest，并拒绝 unsupported 方法。
- [x] TDD：新增 `tests/test_ols_execution_adapter.py`；首次运行 4 条中 3 条失败，原因是 `Results/json/method_execution_result.json`、`run.method_execution` 和 manifest `method_execution` 尚不存在；unsupported method 已在实现初版后通过。
- [x] 实现：扩展 `Product/backend/project_service.py`，新增本地 `python_ols_adapter`，从 approved RunPlan 读取 OLS task、公式和本地 CSV，计算 OLS 系数并写入 `Results/json/method_execution_result.json`。
- [x] 实现：扩展 `Product/app.py`，对 unsupported method 返回 409 `unsupported_run_plan_method`，对数据不足、公式不可估、共线设计返回 409 `method_execution_failed`，避免后端 500。
- [x] 契约修复：`run.plan_binding.tasks[].method_id` 现在回退到 estimator，真实样例不会再出现 `method_id=null`。
- [x] 验证：目标测试 5 OK；相邻回归 20 OK；全量回归 157 OK，skipped=1；Python 编译和 JS 语法检查通过。
- [x] API 验收：真实项目 `POST /api/v1/projects/proj_undergraduate_thesis/runs/full` 生成 `run_4c62f1721afb`，status=`succeeded`，`plan_binding.tasks[0].method_id=ols`，`method_execution.evidence_level=local_execution`，`treatment_coefficient=1.8505076803`。
- [x] 可视化验收：Safari + Computer Use 打开本地页面，研究设计细节页可正常加载；P2-C 为后端执行证据能力，下一步需要把 `method_execution` 更清晰地接入 Execution / Findings UI。
- [x] P2-D：把 `Results/json/method_execution_result.json` 接入 Execution / Findings，把 OLS 结果作为方法执行证据展示，而不是只停留在 API response。

## 2026-05-13 P2-D Method Execution Evidence UI

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-method-execution-ui-bdd.md`，定义方法执行证据在 observability、Execution 页面和 Results/FindingCard 中必须可见。
- [x] TDD：扩展 `tests/test_observable_execution.py`、`tests/test_observable_execution_frontend.py`、`tests/test_results_draft_evidence_binding.py`；首次失败原因符合预期：后端缺少 `method_execution`，前端缺少 `observable-method-execution` 和 FindingCard 方法证据渲染。
- [x] 实现：扩展 `Product/backend/observability_service.py` 和 `Product/backend/results_draft_service.py`，从 run manifest / artifact 读取 `Results/json/method_execution_result.json`，并把方法、公式、样本量、处理变量系数和证据等级返回给页面。
- [x] 前端：扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，在“实证执行”新增“方法执行证据”，在“结果与草稿”的 FindingCard 内新增方法执行证据块。
- [x] 验证：目标测试 4 OK；Results Draft 回归 10 OK；相邻回归 38 OK；全量回归 161 OK，skipped=1；Python 编译、`node --check` 和 `git diff --check` 通过。
- [x] API 验收：`GET /api/v1/projects/proj_undergraduate_thesis/runs/run_4c62f1721afb/observability` 和 `/results-draft` 均返回 `method_execution.evidence_level=local_execution`、`engine=python_ols_adapter`、`formula=wage ~ trained + edu + experience`、`nobs=12`、`treatment_coefficient=1.8505076803`。
- [x] 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2d-method`，在“实证执行”和“结果与草稿”均可看到 OLS 方法执行证据、artifact 路径、公式、样本量和处理变量系数。
- [x] P2-E：扩展方法执行 evaluator，补齐标准误、t 统计量、p 值、95% 置信区间、残差诊断和命名 evaluator checks，并把结果绑定到 FindingCard 方法证据。

## 2026-05-13 P2-E OLS Evaluator Evidence

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-ols-evaluator-bdd.md`，定义 OLS 方法执行必须产出推断指标、诊断项、evaluator verdict，并在 Results & Draft 显示。
- [x] TDD：扩展 `tests/test_ols_execution_adapter.py` 和 `tests/test_results_draft_evidence_binding.py`；首次失败为 `KeyError: standard_errors/evaluator/evaluator_status`，符合“尚未实现 evaluator 证据”的预期。
- [x] 实现：扩展 `Product/backend/project_service.py`，本地 OLS adapter 计算标准误、t 统计量、normal approximation p 值、95% 置信区间、残差自由度、残差标准误和 evaluator checks。
- [x] 实现：扩展 `Product/backend/results_draft_service.py`，FindingCard 的 `method_evidence` 绑定 `standard_error`、`p_value`、`confidence_interval`、`evaluator_status` 和完整 evaluator。
- [x] 前端：扩展 `Product/web/assets/app.js` 和 `Product/web/assets/styles.css`，把 FindingCard 的方法证据改为紧凑中文审阅摘要，避免窄卡片网格拥挤；`Product/web/index.html` asset version 更新到 `20260513-p2e-eval2`。
- [x] 验证：目标测试 19 OK；全量回归 165 OK，skipped=1；Python 编译、`node --check Product/web/assets/app.js` 和 `git diff --check` 通过。
- [x] API 验收：真实 full run `run_a3674e9e78c6` succeeded；`p_value_trained=8.83354660202e-133`、`standard_error_trained=0.0754664205`、`evaluator_status=passed`，四项 evaluator checks 全部 passed。
- [x] 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2e-eval`，点击“结果与草稿”，结果论断卡显示 `ols · n=12 · β=1.8505 · 标准误=0.0755 · p=8.83e-133 · 95% 置信区间 1.7026 ~ 1.9984 · 评估器通过`。
- [x] P2-F：使用 `/Users/mahaoxuan/Desktop/实证数据库` 中的真实数据源做数据接入验收，先以只读候选池方式把真实数据 inventory/profile 接到 Data & Design。

## 2026-05-13 P2-F Real Data Candidate Pool

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-real-data-catalog-bdd.md`，定义真实数据仓库必须以只读候选池进入产品，而不是直接伪装成项目内数据。
- [x] TDD：新增 `tests/test_external_data_catalog.py`；首次失败覆盖 `external_catalog` 缺失、外部 CSV 画像缺失、DTA 可见性缺失和前端候选池面板缺失。
- [x] 实现：扩展 `Product/backend/overview_service.py`，`GET /datasets` 返回 `external_catalog`；默认读取 `/Users/mahaoxuan/Desktop/实证数据库`，也可用 `EMPIRICAL_DATA_LIBRARY_ROOT` 覆盖。
- [x] 实现：外部候选数据全部标记 `evidence_level=local_file`、`read_only=true`、`role=external_candidate_dataset`；CSV 做最多 200 行轻量预览画像，DTA/XLSX/Parquet 等暂标 `not_profiled` 但保留可见。
- [x] 前端：扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，在“数据与设计”页新增 `真实数据候选池`，与项目内 `analysis_sample.csv` 分开展示；首屏只渲染 6 张候选卡，避免重新拥挤。
- [x] 真实数据验收：本机 `/Users/mahaoxuan/Desktop/实证数据库` 扫描到 223 个候选数据文件；Safari 页面显示 CFPS DTA 文件、`本地文件`、`尚未画像`、`只读` 和真实根目录。
- [x] 验证：目标测试 5 OK；相邻数据画像测试 11 OK；全量回归 170 OK，skipped=1；Python 编译、`node --check`、`git diff --check` 通过。
- [x] 交接：更新 handoff、manifest、decision-log、review、current-stage、workflow，并同步 `Tasks/` 到 `tasks/`。
- [x] P2-G：设计“从真实候选池导入/绑定数据集”的显式预检。导入前记录来源、目标路径、文件大小、证据等级和用户动作；预检阶段不移动、不复制、不绑定外部原始数据。

## 2026-05-14 P2-G Real Dataset Bind Preflight

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-dataset-bind-preflight-bdd.md`，定义真实候选数据进入项目之前必须先生成导入/绑定预检，而不是直接复制或喂给变量角色、DesignSpec、RunPlan。
- [x] TDD：新增 `tests/test_external_dataset_bind_preflight.py`；首次运行失败原因符合预期：API 返回 404，前端缺少 `external-bind-preflight-panel` 和候选数据预检按钮。
- [x] 实现：扩展 `Product/backend/overview_service.py` 和 `Product/app.py`，新增 `POST /api/v1/projects/{project_id}/datasets/external-bind-preflight`，只接受 `/Users/mahaoxuan/Desktop/实证数据库` 候选池内的数据文件，写入 `state/product/dataset_import_preflights.json`。
- [x] 实现：预检结果包含 `status=ready_for_review`、`evidence_level=local_file`、源文件路径、目标建议路径 `Data/Raw/<filename>`、策略、文件大小、4 项检查和 `will_mutate_source=false` / `will_create_project_file=false`。
- [x] 前端：扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，在“真实数据候选池”候选卡上新增“生成导入/绑定预检”，并在“导入/绑定预检”面板显示待人工确认、来源、目标、策略、检查项和只读说明。
- [x] 验证：目标测试 5 OK；相邻数据测试 16 OK；全量回归 175 OK，skipped=1；Python 编译、`node --check` 和 `git diff --check` 通过。
- [x] API 验收：`GET /datasets` 返回外部候选池 223 个文件；`POST /datasets/external-bind-preflight` 对 CFPS DTA 候选文件返回 `ready_for_review`、目标 `Data/Raw/...dta` 和 4 项 passed checks。
- [x] 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260513-p2g-bind1`，点击“数据与设计”，点击候选文件“生成导入/绑定预检”，页面显示 `待人工确认`、源路径、目标路径、`尚未导入/绑定 · 源文件只读` 和 4 项通过检查。
- [x] 交接：更新 handoff、manifest、decision-log、review、current-stage、workflow，并同步 `Tasks/` 到 `tasks/`。
- [x] P2-H：实现显式 apply/import workflow。只有用户确认后才允许把预检记录变成项目内 `Data/Raw/...` 文件或绑定记录；同时必须记录人工动作、目标 artifact、哈希/大小和失败回滚语义。

## 2026-05-14 P2-H Real Dataset Import Apply

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-dataset-import-apply-bdd.md`，明确本地版可复制/绑定真实数据，线上版不能读取用户桌面路径，必须走上传或云对象。
- [x] TDD：新增 `tests/test_external_dataset_import_apply.py`；首次运行失败符合预期：apply API 返回 404，前端没有三类人工动作按钮。
- [x] 实现：扩展 `Product/backend/overview_service.py` 和 `Product/app.py`，新增 `POST /api/v1/projects/{project_id}/datasets/external-bind-preflight/{preflight_id}/apply`。
- [x] 实现：支持 `copy_to_project_raw`、`bind_external_reference`、`cancel` 三种动作；记录 `dataset_import`、SHA256、大小、目标路径、runtime mode、人工动作和状态。
- [x] 产品边界：`runtime_mode=cloud` 对本地路径返回 409 `cloud_upload_required`，避免线上应用假装能读取本机文件。
- [x] 前端：扩展“导入/绑定预检”面板，显示“确认导入到项目 / 只绑定引用 / 取消预检”及按钮解释；apply 后回显“已接入”、动作、local 模式和 SHA256。
- [x] 验证：目标测试 5 OK；相邻数据测试 21 OK；全量回归 180 OK，skipped=1；Python 编译、`node --check`、`git diff --check` 通过。
- [x] 可视化验收：Safari + Computer Use 打开 `http://127.0.0.1:8765/?v=20260514-p2h-import1`，点击“数据与设计”，对 CFPS 预检点击“只绑定引用”，页面显示 `已接入`、`已绑定外部引用`、`模式：local` 和 SHA256。
- [x] P2-I：对已复制或已绑定的真实数据做安全字段画像/变量字典预览，尤其是 DTA/XLSX/Parquet；完成前不得让新数据进入 VariableRoleSet、DesignSpec 或 RunPlan。

## 2026-05-14 P2-I Dataset Import Field Profile

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-dataset-import-profile-bdd.md`，定义真实数据接入后的字段画像/变量字典预览边界。
- [x] TDD：新增 `tests/test_external_dataset_import_profile.py`；首次运行 6 条失败，原因是缺少 profile API、前端画像入口和画像面板。
- [x] 实现：新增 dataset import profile 服务，读取已 apply 的 CSV 字段结构并持久化画像结果。
- [x] 实现：DTA/XLSX/Parquet 暂不伪造字段，返回 `blocked/not_profiled` 和阻塞原因。
- [x] 前端：导入/绑定预检结果区增加“生成字段画像”和画像预览面板，明确不会改写 VariableRoleSet、DesignSpec 或 RunPlan。
- [x] 验证：目标测试 6 OK；相邻回归 27 OK；全量回归 186 OK，skipped=1；Python/JS 静态检查、`git diff --check`、API 和页面静态资源验收通过。

## 2026-05-14 P2-J Stata DTA Field Profile

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-dta-field-profile-bdd.md`，定义 DTA metadata-only 字段画像、损坏文件阻塞、不改写研究状态。
- [x] TDD：扩展 `tests/test_external_dataset_import_profile.py`；首次运行 3 条失败，原因是有效 DTA 仍返回 blocked、损坏 DTA 阻塞原因不精确、前端缺少变量标签/Stata 类型。
- [x] 实现：扩展 `Product/backend/overview_service.py`，用 `pyreadstat.read_dta(..., metadataonly=True)` 读取 Stata 元数据，返回字段名、变量标签、Stata 类型、display format、样本数和字段数。
- [x] 实现：损坏 DTA 或缺少读取器时返回 `blocked/not_profiled`、空字段和 `DTA 读取失败...`，不抛 500、不伪造字段。
- [x] 前端：字段画像表从“样本值”改为“变量标签 / Stata 类型”，并修正字段表列宽和表头大小写。
- [x] 真实验收：`dataset_import_e9d864229be8` 绑定的 `cfps2011adult_202202(1).dta` 返回 `profiled/ready`、`row_count=1279`、`column_count=723`、`row_count_source=metadata_only`，前 6 个字段含 `pid=个人id`、`fid=家户号`、`provcd=省国标码`。
- [x] 验证：目标测试 7 OK；相邻回归 28 OK；全量回归 187 OK，skipped=1；Python/JS 静态检查和 `git diff --check` 通过；Playwright CLI 截图 `/tmp/empirical-workbench-p2j-dta-profile.png`。
- [x] P2-K：按用户最新要求，优先建立严谨实证执行契约；full run 必须声明当前真实执行后端、候选 StatsPAI/StataMCP 后端、数据预检和可复现入口。
- [x] P2-K：Execution 页面显示“严谨执行契约 / 数据预检 / 可复现入口”，明确 StatsPAI/StataMCP 目前是候选后端，不能冒充 `local_execution`。
- [x] P2-L：把字段画像推进为“字段审阅 / VariableRoleSet 候选生成”状态机，但仍必须人工确认，不允许自动改写研究状态。
- [x] P2-M：先完成 approved candidate 到正式 VariableRoleSet 的显式写回链路；候选必须载入正式编辑器并允许人工调整，保存后才写入正式研究状态。
- [ ] P2-N：接入真实 StatsPAI/StatsAPI 或 StataMCP 执行器，要求生成独立日志、结果文件、evaluator checks、交叉验证和 `local_execution` evidence。

## 2026-05-14 P2-K Rigorous Empirical Execution Contract

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-rigorous-empirical-execution-bdd.md`，定义“严谨实证执行契约”。
- [x] TDD：扩展 `tests/test_ols_execution_adapter.py` 和 `tests/test_observable_execution_frontend.py`；首次运行失败原因为缺少 `execution_contract`、`data_preflight` 和前端展示。
- [x] 实现：`Product/backend/project_service.py` 的 full run 现在写入 `execution_contract`，并把 active backend 固定为真实执行过的 `python_ols_adapter`。
- [x] 实现：StatsPAI/StatsAPI 与 StataMCP/Stata 只作为候选后端展示，除非未来实际调用并产生日志/产物，否则不标记为 `local_execution`。
- [x] 实现：OLS 任务写入 `data_preflight`，包含读取行数、可用数值行、丢弃行数、必需字段和自由度预检。
- [x] 实现：OLS 任务写入 `reproducibility`，包含 run_id、RunPlan/DesignSpec 版本、公式、结果文件路径和源码入口。
- [x] 前端：Execution 页面新增“严谨执行契约”“数据预检”“可复现入口”三块，用户能直接看到 Python/StatsPAI/StataMCP 的真实状态边界。
- [x] 验证：目标测试 24 OK；相邻回归 42 OK；全量回归 190 OK，skipped=1；Python/JS 静态检查和 `git diff --check` 通过；Playwright CLI 可视化检查无横向溢出。

## 2026-05-14 P2-L Variable Role Candidate Review

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-variable-role-candidate-review-bdd.md`，定义真实 DTA 字段画像只能生成可审阅候选，不能自动写入正式 VariableRoleSet。
- [x] TDD：新增 `tests/test_variable_role_candidates.py`；首次运行 5 条失败，原因是候选 API 404、前端缺少 `variable-role-candidate-panel` 和候选 review 操作。
- [x] 实现：扩展 `Product/backend/variable_role_service.py`，新增 `state/product/variable_role_candidates.json` 候选状态机，支持生成、确认候选、标记需调整和驳回。
- [x] 实现：扩展 `Product/app.py`，新增候选列表、生成和 review API，并对未画像 import 返回 409 `field_profile_required`，对非法动作返回 400 `invalid_variable_role_candidate_action`。
- [x] 前端：扩展“数据与设计”页，新增“字段审阅”面板；用户可以从真实字段画像生成变量角色候选，并看到 `不会写入正式变量角色集` 的边界说明。
- [x] 验证：目标测试 5 OK；相邻回归 17 OK；全量回归 195 OK，skipped=1；Python 编译和 JS 语法检查通过。
- [x] 可视化验收：Chrome + Computer Use 打开 `http://127.0.0.1:8765/?v=20260515-p2l-candidates1`，进入“数据与设计”，真实 CFPS `.dta` 显示 723 个字段；点击“生成变量角色候选”后显示 `待人工审阅`、候选角色、候选字段表和 `state/product/variable_role_candidates.json`；点击“候选已确认”后候选状态为 `approved_candidate`。
- [x] 安全边界验收：确认前后 `state/product/variable_roles.json` SHA256 均为 `bc8bedca4d1638d2556ad77957de146eda170cef521db24eeb7ffde5c2e94649`，mtime 未变化，证明候选 review 没有写回正式变量角色集。
- [ ] P2-M：把 approved candidate 之后的真实变量选择流程做成可编辑确认，不再依赖启发式猜测；随后接 StatsPAI/StataMCP/Python 严格执行器。

## 2026-05-14 P2-M Candidate Promotion to Formal VariableRoleSet

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-variable-role-candidate-promote-bdd.md`，定义候选进入正式变量角色集的边界：未确认候选不能写入，已确认候选也必须先载入正式编辑器，保存后才写入。
- [x] TDD：扩展 `tests/test_variable_role_candidates.py`；首次运行失败符合预期：后端仍按旧本地数据路径校验拒绝真实候选，前端缺少 `pendingVariableRoleCandidateId`。
- [x] 实现：扩展 `Product/backend/variable_role_service.py`，`save_project_variable_roles(..., candidate_id=...)` 支持从 approved candidate 写入正式 VariableRoleSet，并保留 `candidate_id`、`dataset_import_id`、`dataset_import_profile_id`、`source`、`binding` 和 provenance。
- [x] 实现：未确认、需调整或被驳回的候选返回 409 `variable_role_candidate_approval_required`，不能写入正式研究状态。
- [x] 实现：保存成功后候选状态更新为 `applied_to_variable_roles`，并记录 `applied_variable_role_set_version`，避免同一个候选被误认为仍待写回。
- [x] 前端：字段审阅卡片新增“载入正式编辑器”；点击后编辑器切换为 `draft_from_candidate · local_file`，带入 `candidate_id`、真实数据路径和候选角色，提示“保存后才写入正式变量角色集”。
- [x] 可视化验收：Chrome + Computer Use 打开 `http://127.0.0.1:8765/?v=20260514-p2m`，进入“数据与设计”，点击“载入正式编辑器”后确认编辑器显示 `candidate_id=variable_role_candidate_495092cb7af2`、`draft_from_candidate · local_file`、真实 CFPS DTA 路径和候选字段。
- [x] 保护性验收：本轮没有点击“保存变量角色集”，避免把当前演示项目已批准的 `analysis_sample.csv` 变量角色覆盖成 CFPS 启发式候选。
- [x] 验证：目标测试 8 OK；全量回归 198 OK，skipped=1；Python 编译和 JS 语法检查通过。
- [x] P2-N：接入 StatsPAI/StatsAPI 作为 OLS 独立验证后端，生成独立结果文件、交叉验证检查和 `local_execution` evidence。
- [x] P2-O：把本地 Codex Supervisor 作为智能中控层显式接入 workflow contract 和首页，展示 provider readiness、执行开关、阻塞原因和派工计划。
- [ ] P2-P：实现真实 Supervisor plan artifact。启用 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1` 后，由本地 Codex 生成/审阅阶段计划并写入可审计产物；未启用时必须继续显示 blocked，不允许伪装智能派工。

## 2026-05-14 P2-N StatsPAI Independent OLS Validation

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-statspai-execution-validation-bdd.md`，定义 StatsPAI 必须真实执行并写出独立验证产物。
- [x] TDD：扩展 `tests/test_ols_execution_adapter.py`；首次失败原因是 full run 只有 Python OLS adapter，没有 `backend_validations` 和 `Results/json/statspai_execution_result.json`。
- [x] 实现：扩展 `Product/backend/project_service.py`，新增 `execute_statspai_ols_validation()`；当 StatsPAI 可用且数据为 CSV 时调用 `statspai.regress()`，输出系数、标准误、p 值、t 统计、诊断和 cross-check。
- [x] 前端：扩展 `Product/web/assets/app.js` 和 `Product/web/assets/styles.css`，在实证执行页“方法执行证据”中新增“独立后端验证”，显示 StatsPAI adapter、状态、产物路径、证据等级和交叉检查。
- [x] 可视化/API 验收：Chrome + Computer Use 打开 `http://127.0.0.1:8765/?v=20260514-p2n-supervisor1`；最终 API 复核启动完整实证执行生成 `run_bb423547439c`，observability 返回 `独立后端验证`、`passed`、`statspai.regress` 和 `Results/json/statspai_execution_result.json`。
- [x] 验证：目标测试和全量回归均通过；最新全量为 `python3 -m unittest discover -s tests -v`，203 tests OK，skipped=1。

## 2026-05-14 P2-O LLM Supervisor Readiness Contract

- [x] BDD：扩展 `tests/test_product_workflow_contract.py`，定义 workflow contract 必须显式声明 LLM Supervisor 层，首页必须展示本地大模型中控状态。
- [x] TDD：首次失败原因是 `workflow_contract` 缺少 `intelligence_layer`，前端缺少 `llm-supervisor-panel` 和 `renderIntelligenceLayer()`。
- [x] 实现：扩展 `Product/backend/overview_service.py`，新增 `build_intelligence_layer_contract()`，读取 `local_codex_status()`，返回 `supervisor_agent_id=pipeline_supervisor`、provider、ready/blocked 状态、blockers 和派工计划。
- [x] 前端：扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，首页新增“智能中控”面板，显示本地 Codex Supervisor、Provider、可用性、执行开关、阻塞原因和阶段派工计划。
- [x] 可视化验收：页面显示 `本地 Codex Supervisor 未启用`、`provider=local_codex`、`可用=是`、`允许执行=否`、`local_codex_execution_not_enabled` 和四个派工方向。
- [ ] 未完成：当前只是 Supervisor readiness contract，不是实际 LLM 派工执行。真实派工必须等 P2-P 持久化 `supervisor_plan` 并在执行开关启用时调用本地 Codex。

## 2026-05-16 P2-P Local Codex SupervisorPlan Artifact

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-supervisor-plan-bdd.md`，定义本地 Codex Supervisor 只能生成可审阅计划，不能直接改写正式研究状态。
- [x] TDD：新增 `tests/test_supervisor_plan.py`；首次运行 5 条失败，原因是 `/supervisor-plan` API 返回 404，前端缺少 `supervisor-plan-panel`。
- [x] 实现：新增 `Product/backend/supervisor_plan_service.py`，在 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1` 时调用本地 Codex 生成计划，并持久化到 `state/product/supervisor_plan.json`。
- [x] 实现：扩展 `Product/backend/codex_provider.py`，新增通用 `run_local_codex_prompt()`，保留 provider readiness 与显式执行开关。
- [x] 实现：扩展 `Product/app.py`，新增 `GET/POST /api/v1/projects/{project_id}/supervisor-plan`。
- [x] 前端：首页新增 `SupervisorPlan 审阅台`，显示计划状态、风险、证据要求、子 Agent 分工、人工确认 gate 和生成按钮。
- [x] 边界：未启用 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC` 时返回 409 `local_codex_execution_not_enabled`，不会创建 `supervisor_plan.json`，也不会伪装智能派工。
- [x] 保护性验证：测试确认生成 SupervisorPlan 前后 `state/product/variable_roles.json`、`state/product/design_spec.json`、`state/product/run_plan.json` 不变。
- [x] 验证：目标测试 5 OK；相邻回归 20 OK；全量回归 208 OK，skipped=1；Python 编译、JS 语法和 `git diff --check` 通过。
- [x] 可视化/API 验收：当前工作树服务运行在 `http://127.0.0.1:8767/?v=20260516-p2p-supervisor-plan`；DOM 显示 `SupervisorPlan 审阅台`、`生成 SupervisorPlan`、`本地 Codex SupervisorPlan` 和默认阻断 `local_codex_execution_not_enabled`；截图保存到 `artifacts/ui-checks/p2p-supervisor-plan-overview.png`。
- [ ] 下一步 P2-Q：把 SupervisorPlan approval 做成显式人工确认状态，然后让 approved SupervisorPlan 驱动下一轮执行任务队列；仍不能自动改写 VariableRoleSet、DesignSpec 或 RunPlan。

## 2026-05-16 P2-P1 Home Progressive Disclosure

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-home-progressive-disclosure-bdd.md`，定义首页智能中控和 SupervisorPlan 的细节默认折叠。
- [x] TDD：扩展 `tests/test_supervisor_plan.py` 和 `tests/test_product_workflow_contract.py`；首次运行 2 条新增前端行为失败，原因是页面没有 `progressive-disclosure`、`查看中控详情`、`查看计划详情`。
- [x] 实现：首页“智能中控”首屏只显示启用状态、证据等级、阻塞数量和派工角色数量；Provider、执行开关、阻塞项和派工计划进入可展开详情。
- [x] 实现：首页 `SupervisorPlan 审阅台` 首屏只显示状态、主按钮、人工确认说明和下一步摘要；版本、写入边界、阶段计划、子 Agent 分工、证据要求和风险进入可展开详情。
- [x] 可访问性：使用原生 `details/summary`，默认不加 `open`，并补齐 focus-visible 样式。
- [x] 验证：目标测试 15 OK；全量回归 210 OK，skipped=1；Python 编译、JS 语法、`git diff --check` 通过。
- [x] 右侧内置浏览器验收：`http://127.0.0.1:8767/?v=20260516-p2p-disclosure1` 中两个详情块初始关闭；点击后 `Provider` 和 `SupervisorPlan` 明细可见；截图保存到 `artifacts/ui-checks/p2p-home-progressive-disclosure.png`。
- [ ] 下一步 P2-Q：实现 SupervisorPlan approve/reject/needs_revision 审批状态机，并把 approved plan 作为后续任务队列的输入。

## 2026-05-16 P2-Q Topic-first Home

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-topic-first-home-bdd.md`，定义首页必须先让用户输入或选择研究选题，再进入具体判断环节。
- [x] TDD：扩展 `tests/test_product_workflow_contract.py`；首次运行 3 条新增行为失败，原因是页面缺少 `research-topic-intake`、`research-workbench-after-topic` 和 `data-topic-start-action`。
- [x] 实现：首页新增“开始一项实证研究”入口，包含选题输入、从已有选题继续、从真实数据候选池开始。
- [x] 实现：原首页中的下一步研究决策、智能中控、SupervisorPlan、风险和执行概览默认进入 `research-workbench-after-topic`，确认选题后才展开。
- [x] 实现：选题只保存为前端本地状态，不写回 VariableRoleSet、DesignSpec、RunPlan 或 SupervisorPlan。
- [x] 视觉收敛：窄视口下隐藏右侧 inspector、压缩侧栏和间距，保证选题入口能在首屏可见。
- [x] 验证：目标前端契约测试 9 OK；相邻回归 18 OK；全量回归 213 OK，skipped=1；Python 编译、JS 语法、`git diff --check` 通过。
- [x] 右侧内置浏览器验收：`http://127.0.0.1:8767/?v=20260516-p2q-topic1` 初始只显示选题入口；输入选题并点击 `进入研究判断` 后，才显示 `下一步研究决策`、`智能中控` 和 `SupervisorPlan`。
- [ ] 下一步 P2-R：把确认后的研究选题升级为后端 `ResearchQuestion` / `TopicSession` 审计对象，再做 SupervisorPlan approve/reject/needs_revision 审批状态机。

## 2026-05-16 P2-S SupervisorPlan Topic Binding

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-supervisor-plan-topic-binding-bdd.md`，定义 SupervisorPlan 必须基于 confirmed ResearchQuestion / TopicSession。
- [x] TDD：扩展 `tests/test_supervisor_plan.py`；首次运行 5 条失败，原因是 Codex prompt 缺少 confirmed research question、无选题时没有提前返回 `research_question_required`、前端审阅台不显示绑定选题。
- [x] 实现：`Product/backend/supervisor_plan_service.py` 在生成 SupervisorPlan 前读取 `state/product/research_question.json`，只接受 `status=confirmed`。
- [x] 实现：SupervisorPlan 输出新增 `input_research_question`、`input_state_versions.research_question_version`、`input_evidence.research_question_path`。
- [x] 实现：传给本地 Codex 的 prompt 新增 `confirmed_research_question`，包含 question、version、topic_session_id、evidence_level 和 path。
- [x] 前端：`SupervisorPlan 审阅台` 摘要显示 `绑定选题`，详情显示 `TopicSession` 和 `ResearchQuestion 版本`。
- [x] 验证：目标测试 8 OK；相邻回归 23 OK；全量回归 221 OK，skipped=1；Python 编译、JS 语法和 `git diff --check` 通过。
- [x] 可视化验收：`http://127.0.0.1:8767/?v=20260516-p2s-supervisor-topic1` 显示已确认选题和 SupervisorPlan 审阅台绑定选题；console error=0；截图保存到 `artifacts/ui-checks/p2s-supervisor-topic-binding.png`。
- [x] 下一步 P2-T：已实现 SupervisorPlan approve/reject/needs_revision 审批 API 和前端操作；只有 approved plan 才能进入 Agent Task Queue。

## 2026-05-16 P2-T SupervisorPlan Review State Machine

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-supervisor-plan-review-bdd.md`，定义 SupervisorPlan 人工审批、阻断派工和不可篡改研究状态的行为。
- [x] TDD：扩展 `tests/test_supervisor_plan.py`；首次目标测试失败，原因是缺少 `/supervisor-plan/review` API、review 状态持久化和前端审批按钮。
- [x] 实现：`PUT /api/v1/projects/{project_id}/supervisor-plan/review` 支持 `approve`、`needs_revision`、`reject`，写入 `human_review`、`can_dispatch` 和下一步动作。
- [x] 实现：审批只更新 `state/product/supervisor_plan.json`，不会改写 `state/product/research_question.json`、`state/product/variable_roles.json`、`state/product/design_spec.json` 或 `state/product/run_plan.json`。
- [x] 前端：首页 `SupervisorPlan 审阅台` 在存在计划时显示 `批准计划`、`要求修改`、`驳回计划`，并用 `可进入任务队列` / `不可派工` 明确结果。
- [x] 保护性验证：目标测试 13 OK；相邻回归 28 OK；全量回归 226 OK，skipped=1；Python 编译、JS 语法、`git diff --check` 通过。
- [x] 可视化验收：本地服务运行在 `http://127.0.0.1:8767/?v=20260516-p2t-supervisor-review1`；当前真实项目尚未生成 `supervisor_plan.json`，页面正确显示 `尚未生成` 和 `生成 SupervisorPlan`；截图保存到 `artifacts/ui-checks/p2t-supervisor-review-page.png`。
- [ ] 下一步 P2-U：把 approved SupervisorPlan 拆成 Agent Task Queue，显示 owner agent、输入证据、输出要求、阻塞项和状态；未 approved 的计划必须继续阻断。

## 2026-05-17 P2-U Agent Task Queue

- [x] BDD：新增 `docs/architecture-v2/codex-phase-p2-agent-task-queue-bdd.md`，定义 approved SupervisorPlan 才能创建可审阅任务队列。
- [x] TDD：新增 `tests/test_agent_task_queue.py`；首次目标测试 8 条失败，失败原因是缺少 API、持久化服务和前端队列面板。
- [x] 实现：新增 `Product/backend/agent_task_queue_service.py`，从 `status=approved` 且 `can_dispatch=true` 的 SupervisorPlan 生成 `state/product/agent_task_queue.json`。
- [x] 实现：扩展 `Product/app.py`，新增 `GET/POST /api/v1/projects/{project_id}/agent-task-queue`；未生成计划、未批准计划和空 `subagent_dispatch` 都返回结构化 409。
- [x] 实现：扩展 `Product/web/index.html`、`Product/web/assets/app.js`、`Product/web/assets/styles.css`，首页新增 `Agent 任务队列`，默认展示摘要、阻塞、负责人和任务状态，任务详情用 `details/summary` 按需展开。
- [x] 保护性边界：创建队列只写 `state/product/agent_task_queue.json`，不执行子 Agent，不改写 ResearchQuestion、VariableRoleSet、DesignSpec、RunPlan 或 SupervisorPlan。
- [x] 自动验证：`python3 -m unittest tests.test_agent_task_queue -v` 8 tests OK；`python3 -m unittest discover -s tests -v` 234 tests OK，skipped=1；Python 编译、JS 语法和 `git diff --check` 通过。
- [x] 浏览器验收：真实项目在无 approved SupervisorPlan 时显示 `缺少 SupervisorPlan` 且创建按钮 disabled；受控 approved-plan 场景点击创建后显示 2 个任务、2 个详情默认折叠、无 console error；截图保存到 `/tmp/empirical-workbench-agent-task-queue-p2u-final.png` 和 `/tmp/empirical-workbench-agent-task-queue-p2u-approved.png`。
- [ ] 下一步 P2-V：把 approved Agent Task Queue 推进到“人工派工 / 执行前审计”状态；仍不能自动启动子 Agent 或绕过任务级人工检查。

## 2026-05-25 P2-AB Topic-first Auto Research CLI

- [x] BDD：锁定 `auto-research` 本地高效工作流主入口，默认追求 best-available execution，而不是 fallback-first dry-run。
- [x] 边界：CNKI / Web / Zotero / StatsPAI / LLM Supervisor / agentmemory 都是可用则启用；不可用时局部降级并写入 capability evidence，不能静默失败。
- [x] 边界：所有自动产物默认 `exploratory` / `draft` / `needs_human_review`，不能自动晋升正式变量、正式设计、正式 RunPlan 或正式引用。
- [x] TDD：新增 `tests/test_auto_research_cli.py`；首次 RED 失败原因为 `Product/cli.py` 尚无 `auto-research` 子命令。
- [x] 实现：新增 `Product.backend.auto_research_service.run_auto_research()`，复用 `create_run_workspace()` 和现有 evidence inventory。
- [x] CLI：新增 `python3 Product/cli.py auto-research --topic ... --mode auto --max-depth 2 --max-iterations 5`。
- [x] 兼容：治理层新增 transient runtime project 解析，允许 CLI 直接指向未注册本地项目，同时不污染 Product 全局 registry。
- [x] 验证：目标测试、相邻 CLI 回归、Python 编译检查通过。
- [ ] 全量风险：`python3 -m unittest discover -s tests -v` 当前 282 tests 中 17 个前端契约失败，集中在旧 Agent Drawer、首页产品工作区锚点、中文导航契约和 SupervisorPlan 前端面板；需另开前端契约修复轮。

## 2026-05-25 P3-C Intake To Analysis Workspace

- [x] BDD：修订 `docs/architecture-v2/codex-phase-p3-semantic-glow-cards-bdd.md`，锁定“入口页只做输入，提交后才进入分析工作台”的产品规则。
- [x] TDD：新增/修订 `tests/test_p3_semantic_glow_cards.py` 与 `tests/test_p3_react_input_tabs.py`；首次按新规则运行失败，原因是语义卡仍挂在入口页。
- [x] 实现：`App.tsx` 拆成 `task === null` 的 intake screen 与 `analysis-workspace` 两个状态；首屏只保留标题和研究输入器。
- [x] 实现：新增 `SemanticGlowCards.tsx`，提交后把题目拆成研究对象、数据线索、方法线索、证据缺口和下一步任务五张 draft-only 卡。
- [x] 实现：`ResearchCommandInput` 支持 `onDraftChange`，但输入器内部不渲染语义卡，避免入口页信息过载。
- [x] 视觉：GlowCard 改为黑白灰低对比 spotlight，卡片只在分析页出现；分析页标题收敛为工作台标题尺寸。
- [x] 类型：补齐 `@types/react`、`@types/react-dom`、`@types/three`，让 React 子项目可跑 `npx tsc --noEmit`。
- [x] 验证：目标 React 契约 12 tests OK；`npx tsc --noEmit` 通过；`npm run build` 通过；Playwright 入口页 `initialCards=0`、提交后 `analysisCards=5`。
- [ ] 下一步 P3-D：把分析页拆成真正的阶段页面容器；不同阶段再接不同 UI 组件和真实工作流，不再把所有分析塞在一个页面。

## 2026-05-25 P3-D Task Brief Demo

- [x] 写 BDD：任务书阶段页、右侧 Inspector、语义卡后置、draft-only 边界。
- [x] 写失败测试：`tests/test_p3_task_brief_demo.py`。
- [x] 实现 `TaskBriefDemo` 低保真阶段页。
- [x] App 增加 `activeStage`，默认进入任务书；切换到其他阶段后才显示语义卡。
- [x] 增加黑白灰 task brief / inspector 样式。
- [x] 运行目标测试、类型检查、build 和 Playwright 验收。
- [ ] 下一步：围绕“任务书页”进入 grill-me，确认主屏 5 个信号是否合适、右侧 Inspector 是否应该改成抽屉或固定栏。

## 2026-05-27 P5-B Formal Package Manifest

- [x] 节点时间盒：P5-B 只处理“审批后正式包 manifest + 目录骨架”，不生成 PDF、docx、正式正文或回归结果，避免超过 20 分钟节点边界。
- [x] Agent Team：启用只读 sidecar 映射现有 export/package/formal-state 代码；结论是 P5-B 安全写入面应限定在 `Results/json`、`Reviews`、`Submissions/formal_package`。
- [x] BDD：在 `docs/architecture-v2/codex-phase-p4-paper-package-quality-bdd.md` 新增 Behavior 24，定义 P5-A 审批通过后才能建立正式包清单。
- [x] TDD：新增 `tests/test_formal_paper_package_manifest.py`；首次 RED 失败原因是缺少 `Program/formal_paper_package_manifest.py`。
- [x] 实现：新增 `Program/workbench/formal_paper_package_manifest.py` 和 CLI wrapper，读取 `formal_writeback_approval.json` 与 `writeback_approvals.json` 后生成 manifest/review/skeleton。
- [x] 产物：生成 `Results/json/formal_paper_package_manifest.json`、`Reviews/formal_paper_package_manifest.md`、`Submissions/formal_package/README.md`。
- [x] 保护边界：manifest 明确 `this_command_wrote_formal_state=false`、`this_command_wrote_final_outputs=false`，并记录 formal state guard。
- [x] 验证：目标测试 3 OK；相邻 P5/P1 export 回归 17 OK；Python 编译通过；真实 CLI 运行输出 `formal_package_manifest_ready`。
- [ ] 下一步 P5-C：基于 manifest 组装正式稿源文件清单和章节占位，不直接跳到最终 PDF；P5-D 再做 PDF/export preflight。

## 2026-05-27 P5-C Formal Manuscript Source Assembly

- [x] 节点时间盒：P5-C 只处理“正式稿源装配清单 + 章节源占位”，不生成最终 PDF、docx 或正式正文；超过该边界的写作和导出进入 P5-D/P6。
- [x] Agent Team：尝试新建 verifier sidecar 时因线程上限被拒绝，已复用现有后台审查线程；主线不等待，避免阻塞 20 分钟节点。
- [x] BDD：在 `docs/architecture-v2/codex-phase-p4-paper-package-quality-bdd.md` 新增 Behavior 25，定义 ready manifest 才能装配章节源。
- [x] TDD：新增 `tests/test_formal_manuscript_source_assembly.py`；首次 RED 失败原因是缺少 `Program/formal_manuscript_source_assembly.py`。
- [x] 实现：新增 `Program/workbench/formal_manuscript_source_assembly.py` 和 CLI wrapper，复用 `REQUIRED_SECTIONS` / `SECTION_TARGETS` 生成 10 个章节源占位和 `section_sources.json`。
- [x] 产物：生成 `Results/json/formal_manuscript_source_map.json`、`Reviews/formal_manuscript_source_map.md`、`Submissions/formal_package/manuscript/section_sources.json` 和 10 个章节源占位文件。
- [x] 保护边界：source map 明确 `this_command_wrote_formal_state=false`、`this_command_wrote_final_outputs=false`，并记录 formal state guard。
- [x] 验证：目标测试 3 OK；真实 CLI 运行输出 `formal_manuscript_sources_ready` 和 `can_prepare_pdf_preflight=true`。
- [ ] 下一步 P5-D：对章节源、文献、方法、结果和复现说明做 PDF-first export preflight；只生成预检与补写任务，不直接输出正式 PDF。

## 2026-05-27 P5-D Formal PDF Export Preflight

- [x] 节点时间盒：P5-D 只处理“正式稿源和证据是否足以进入 PDF 候选渲染”，不生成 PDF、docx 或正式论文正文；超过该边界的渲染接入进入下一节点。
- [x] Agent Team：复用现有后台审查线程做只读 sidecar；结论是现有 `Program/export_pdf.py` 负责通用 QMD 渲染工具链，P5-D 负责正式论文包章节源和证据准入，两者暂不混合。
- [x] BDD：在 `docs/architecture-v2/codex-phase-p4-paper-package-quality-bdd.md` 新增 Behavior 26，定义 ready source map 才能运行 PDF-first 预检。
- [x] TDD：新增 `tests/test_formal_pdf_export_preflight.py`；首次 RED 失败原因是缺少 `Program/formal_pdf_export_preflight.py`。
- [x] 实现：新增 `Program/workbench/formal_pdf_export_preflight.py` 和 CLI wrapper，检查 `section_sources.json`、章节源占位、目标长度和 evidence registry。
- [x] 产物：生成 `Results/json/formal_pdf_export_preflight.json`、`Reviews/formal_pdf_export_preflight.md`、`Submissions/formal_package/reproducibility/pdf_export_preflight_tasks.json`。
- [x] 真实项目验收：当前真实包被正确阻断为 `blocked_by_source_gaps`，原因是 10 个章节源仍为占位，且缺少 approved findings、citation log、domain notes、figure manifest、limitations、regression tables、robustness matrix、sample profile、variable role set、verified context sources。
- [x] 保护边界：预检明确 `this_command_wrote_formal_state=false`、`this_command_wrote_final_outputs=false`，并记录 formal state guard。
- [x] 验证：目标测试 3 OK；相邻 P5/PDF 回归 14 OK；Python 编译通过；真实 CLI 运行输出 `can_export_pdf_candidate=false`。
- [ ] 下一步 P5-E：把 P5-D 的 20 个任务拆成每个 <=20 分钟的小节点，优先补证据索引映射和章节源写作入口，再把通过后的正式源接到 PDF 候选渲染。

## 2026-05-27 P5-E1 Formal Evidence Registry Resolver

- [x] 节点时间盒：P5-E1 只扫描 P5-D 缺失证据，生成 evidence registry patch proposal；不生成目标 evidence files，不改 canonical registry，不改正式层。后续每个 P5-E 子节点控制在 20 分钟内，超过就继续拆。
- [x] Agent Team：尝试新建 explorer 因线程上限失败，复用既有 Agent 做只读 sidecar；主线实现采用更深的 derivable artifact resolver，并用真实仓库产物交叉校验。
- [x] BDD：在 `docs/architecture-v2/codex-phase-p4-paper-package-quality-bdd.md` 新增 Behavior 27，定义补证据前必须先扫描已有正式状态、审稿账本、方法执行结果、文献包和质量报告。
- [x] TDD：新增 `tests/test_formal_evidence_registry_resolver.py`；首次 RED 失败原因是缺少 `Program/formal_evidence_registry_resolver.py`。
- [x] 实现：新增 `Program/workbench/formal_evidence_registry_resolver.py` 和 CLI wrapper，只生成 resolution report、review markdown 和 patch proposal。
- [x] 产物：生成 `Results/json/formal_evidence_registry_resolution.json`、`Reviews/formal_evidence_registry_resolution.md`、`Submissions/formal_package/reproducibility/evidence_registry_patch_proposal.json`。
- [x] 真实项目验收：P5-D 的 10 个缺失证据全部找到现有来源或可派生来源；`variable_role_set` 是 direct alias，另外 9 个是 derivable，`missing_after_scan=0`。
- [x] 保护边界：resolver 明确 `this_command_mutated_preflight=false`、`this_command_wrote_formal_state=false`、`can_apply_without_human_review=false`，不直接修改 PDF 预检报告、章节源、正式研究状态或 canonical evidence registry。
- [x] 验证：目标测试 3 OK；P5-D/P5-E1 回归 6 OK；全量回归 360 OK，skipped=1；Python 编译通过；真实 CLI 运行输出 `status=evidence_registry_patch_proposed`、`patch_items=10`。
- [x] P5-E2a 节点规则：本节点只材料化最高确定性的 3 个证据文件：`variable_role_set`、`sample_profile`、`regression_tables`；不写正式 `state/product/*`，不处理图、稳健性、局限和章节正文。后续所有 P5/P6 的 A/B/C/D 小节点最多 20 分钟，超时必须拆解或回退路线。
- [x] P5-E2a BDD/TDD：新增行为 28 和 `tests/test_formal_evidence_materializer.py`；RED 为缺少 `Program/formal_evidence_materializer.py`，GREEN 后覆盖目标证据材料化、缺 proposal 阻断和未请求证据不写出。
- [x] P5-E2a 实现：新增 `Program/formal_evidence_materializer.py` 和 `Program/workbench/formal_evidence_materializer.py`，从现有 artifact 生成 `Results/json/formal_evidence_materialization_report.json`、`Reviews/formal_evidence_materialization.md`、`Submissions/formal_package/evidence/variable_role_set.json`、`Results/json/sample_profile.json`、`Results/json/regression_tables.json`。
- [x] P5-E2a PDF 预检刷新：让 `formal_pdf_export_preflight` 优先读取 `Submissions/formal_package/evidence/variable_role_set.json`；重跑后 `variable_role_set`、`sample_profile`、`regression_tables` 三项 evidence check 已 passed。
- [x] P5-E2a 风险记录：当前正式变量角色仍绑定旧样例 `Data/Final/analysis_sample.csv`，真实方法执行使用 `Data/Final/cfps_robot_reallocation.csv`；材料化报告保留 `variable_role_dataset_mismatch`，等待后续人工确认或正式变量角色升级。
- [x] P5-E2a Agent Team：尝试派发 sidecar 复核时因当前环境 agent thread limit 被拒绝；主 Agent 按 20 分钟节点先完成可验证 CLI/TDD/预检刷新，并把下一次 Agent Team 调用点写入材料化报告。
- [x] P5-E2a 验证：目标测试 3 OK；P5-D/P5-E1/P5-E2a 回归 9 OK；Python 编译通过；真实 CLI 输出 `status=evidence_materialized`、`materialized=3`；全量回归 `363 tests OK, skipped=1`。
- [x] P5-E2b 节点规则：本节点只材料化 `figure_manifest`、`robustness_matrix`、`limitations_register` 三个审阅证据；不写正式 `state/product/*`，不渲染 PDF/docx，不处理章节源占位和文献/上下文来源。
- [x] P5-E2b BDD/TDD：新增行为 29 和 `tests/test_formal_evidence_materializer.py`；RED 为缺少 `Results/json/figure_manifest.json`，GREEN 后覆盖三个证据文件、预警状态和正式层不改写。
- [x] P5-E2b 实现：扩展 `Program/workbench/formal_evidence_materializer.py`，从真实方法诊断、方法门、审稿 scorecard 和可用图表目录材料化 `Results/json/figure_manifest.json`、`Results/json/robustness_matrix.json`、`Results/json/limitations_register.json`。
- [x] P5-E2b 真实运行：CLI 输出 `status=evidence_materialized`、`materialized=3`；重跑 PDF 预检后这三项 evidence check 已 passed，当前剩余缺口集中在 `approved_findings`、`citation_verification_log`、`domain_notes`、`verified_context_sources` 和章节源占位。
- [x] P5-E2b Agent Team：当前环境再次触发 agent thread limit，无法新开 sidecar；主 Agent 按 20 分钟节点完成 TDD、真实 CLI 和预检刷新，并把下一次 Agent Team 调用点收敛到 P5-E2c 的文献/上下文/章节源补证。
- [x] P5-E2b 验证：目标测试 1 OK；materializer 全文件 4 OK；P5-D/P5-E1/P5-E2 回归 10 OK；Python 编译通过；全量回归 `364 tests OK, skipped=1`。
- [x] P5-E2c 节点规则：本节点只材料化 `approved_findings`、`citation_verification_log`、`domain_notes`、`verified_context_sources` 四个 finding/文献/上下文证据；不写正式 `state/product/*`，不处理章节源占位，不渲染 PDF/docx。
- [x] P5-E2c Agent Team：按用户要求先尝试新建只读 explorer，但当前环境返回 `collab spawn failed: agent thread limit reached`；主 Agent 继续本地 TDD/CLI 闭环，并把该限制记录为当前运行约束。
- [x] P5-E2c BDD/TDD：新增行为 30 和 materializer 测试；RED 为四个目标证据文件未生成，GREEN 后覆盖 approved review、DOI 书目日志、领域笔记、来源 registry 聚合和正式层不改写。
- [x] P5-E2c 实现：扩展 `Program/workbench/formal_evidence_materializer.py`，兼容 list/dict 两种 finding review 账本，从 `finding_reviews.json`、`literature_package_report.json`、`verified_bibliography.csv`、`candidate_literature.csv`、`source_registry.json` 派生四个 JSON 证据文件。
- [x] P5-E2c 真实运行：CLI 输出 `status=evidence_materialized`、`materialized=4`；重跑 PDF 预检后 `required_evidence_missing` 已清零，当前唯一阻断原因是 `section_source_placeholders_remaining`。
- [x] P5-E2c 验证：新增目标测试 OK；materializer 全文件 5 OK；P5-D/P5-E1/P5-E2 回归 11 OK；Python 编译通过；全量回归 `365 tests OK, skipped=1`。
- [x] 长程执行约束更新：后续每个 P5/P6 小节点默认最多 20 分钟；超过 20 分钟必须拆成更小节点，或回退判断路线是否走错。Agent Team 优先用于并行调研/只读复核/实现审查；若当前会话线程上限阻断，必须记录原因并继续用本地可验证闭环推进。
- [x] P5-E2d 节点规则：本节点只把 `section_source_placeholders_remaining` 推进为证据绑定的章节源草案；不渲染 PDF/docx，不扩写完整论文，不写正式 `state/product/*`。
- [x] P5-E2d Agent Team：按用户要求先尝试新建只读 explorer 复核章节源/预检边界，但当前环境返回 `collab spawn failed: agent thread limit reached`；主 Agent 继续按 20 分钟节点完成本地 BDD/TDD/CLI 闭环。
- [x] P5-E2d BDD/TDD：新增行为 31 和 `tests/test_formal_section_source_drafter.py`；RED 为缺少 `Program/formal_section_source_drafter.py`，GREEN 后覆盖章节源草案生成、缺证据阻断、正式层不改写和 PDF 预检联动。
- [x] P5-E2d 实现：新增 `Program/formal_section_source_drafter.py` 和 `Program/workbench/formal_section_source_drafter.py`，把 10 个章节源从占位改为 `source_draft_ready`，并绑定每节所需证据路径。
- [x] P5-E2d 真实运行：CLI 输出 `status=section_source_drafts_ready`、`drafted_sections=10`；重跑 PDF 预检后输出 `status=ready_for_pdf_export_review`、`can_export_pdf_candidate=true`、`blocking_reasons=[]`。
- [x] P5-E2d 验证：目标测试 2 OK；相邻 PDF/source assembly 回归 8 OK；Python 编译通过；全量回归 `367 tests OK, skipped=1`。
- [x] P5-E3 节点规则：本节点只把 `source_draft_ready` 章节源和通过的 PDF 预检推进为 PDF 候选稿；不写正式 `state/product/*`，不批准最终 PDF/docx，不合并 canonical 方法库。
- [x] P5-E3 时间盒：拆成 4 个 20 分钟以内的小节点：导出链路定位、BDD/TDD、候选 PDF CLI 实现、验证提交。若后续节点超过 20 分钟，必须继续拆小或回退路线。
- [x] P5-E3 Agent Team：按用户要求尝试新建只读 explorer 复核导出链路，但当前环境返回 `collab spawn failed: agent thread limit reached`；主 Agent 继续本地 BDD/TDD/CLI 闭环，并把该限制写入候选 PDF 报告的 `agent_team_schedule`。
- [x] P5-E3 BDD/TDD：新增 Behavior 32 和 `tests/test_formal_pdf_candidate.py`；RED 为缺少 `Program/formal_pdf_candidate.py`，GREEN 后覆盖候选 QMD/审阅报告/复跑脚本、预检未通过阻断、正式层不改写。
- [x] P5-E3 实现：新增 `Program/formal_pdf_candidate.py` 和 `Program/workbench/formal_pdf_candidate.py`，从 `formal_pdf_export_preflight.json`、`formal_manuscript_source_map.json`、`section_sources.json` 组装 `paper_candidate.qmd`，并在本机 Quarto/XeLaTeX 工具链可用时渲染候选 PDF。
- [x] P5-E3 真实运行：CLI 输出 `status=pdf_candidate_ready`；生成 `Submissions/formal_package/manuscript/paper_candidate.qmd`、`Submissions/formal_package/paper_candidate.pdf`、`Results/json/formal_pdf_candidate_report.json`、`Reviews/formal_pdf_candidate.md` 和 `Submissions/formal_package/reproducibility/render_pdf_candidate.sh`；`pdfinfo` 显示候选 PDF 共 10 页。
- [x] P5-E3 验证：目标测试 2 OK；P5-D/P5-E2d/P5-E3 相邻回归 7 OK；Python 编译通过；`git diff --check` 通过。
- [x] P5-E4 节点规则：本节点只对 PDF 候选稿做机器审阅、人工审阅入口和最终写回预检；不把 `paper_candidate.pdf` 晋升为最终 PDF/docx，不写 `state/product/*`，不合并 canonical 方法库。
- [x] P5-E4 时间盒：拆成 4 个 20 分钟以内的小节点：行为契约、失败测试、CLI/报告实现、真实运行和提交。后续 P5/P6 的 A/B/C/D 小节点继续按 20 分钟封顶，超时必须拆解或回退路线。
- [x] P5-E4 Agent Team：按要求尝试新建只读 test-engineer 复核 Behavior 33、测试和实现边界，但当前环境返回 `collab spawn failed: agent thread limit reached`；主 Agent 继续本地 BDD/TDD/CLI 闭环，并把线程上限写入候选稿审阅报告的 `agent_team_schedule`。
- [x] P5-E4 BDD/TDD：新增 Behavior 33 和 `tests/test_formal_pdf_candidate_review.py`；RED 为缺少 `Program/formal_pdf_candidate_review.py`，GREEN 后覆盖候选 PDF 审阅、最终写回预检、候选报告未 ready 阻断、正式层不改写和候选 PDF 字节不变。
- [x] P5-E4 实现：新增 `Program/formal_pdf_candidate_review.py` 和 `Program/workbench/formal_pdf_candidate_review.py`，读取 `formal_pdf_candidate_report.json`，检查候选 PDF 可读性、章节清单和候选命令写入边界，生成审阅 JSON、审阅 Markdown 和最终写回预检 JSON。
- [x] P5-E4 真实运行：CLI 输出 `status=ready_for_final_approval_review`、`can_request_final_approval=true`；生成 `Results/json/formal_pdf_candidate_review.json`、`Reviews/formal_pdf_candidate_review.md`、`Results/json/formal_pdf_final_writeback_preflight.json`；报告确认 PDF 可读 10 页、`final_writeback_allowed=false`、formal state guard 未变化。
- [x] P5-E4 验证：目标测试 2 OK；P5-D/P5-E3/P5-E4 相邻回归 7 OK；Python 编译通过。
- [x] P5-E5 节点规则：本节点只写“人工最终批准账本”，授权 P6-A 可以写最终 PDF/docx；不复制、移动、重命名 `paper_candidate.pdf`，不生成 `paper.pdf`、`paper.docx`，不改写正式研究状态。
- [x] P5-E5 时间盒：拆成 4 个 20 分钟以内的小节点：Behavior 34、失败测试、CLI/ledger 实现、真实运行和提交。后续 P6-A/P6-B/P6-C 继续遵守每个小节点最多 20 分钟，超时必须拆解或回退路线。
- [x] P5-E5 Agent Team：使用 verifier sidecar Gibbs 复核批准账本边界；采纳其建议，把最终 PDF 批准写入独立 `final_pdf_approvals.formal_pdf_candidate`，不复用旧的 `formal_preflight_approvals`，避免混淆“包入口审批”和“最终产物写回授权”。
- [x] P5-E5 BDD/TDD：新增 Behavior 34 和 `tests/test_formal_pdf_final_approval.py`；RED 为缺少 `Program/formal_pdf_final_approval.py`，GREEN 后覆盖 approve、needs_revision、preflight blocked、旧 `approvals` 保留、正式层不改写和最终产物不生成。
- [x] P5-E5 实现：新增 `Program/formal_pdf_final_approval.py` 和 `Program/workbench/formal_pdf_final_approval.py`，读取 `formal_pdf_final_writeback_preflight.json`，写出 `Results/json/formal_pdf_final_approval.json`、`Reviews/formal_pdf_final_approval.md`，并更新 `state/product/writeback_approvals.json`。
- [x] P5-E5 真实运行：CLI 输出 `status=approved_for_final_writeback`、`can_enter_p6=true`、`final_writeback_authorized=true`；报告确认 `this_command_wrote_final_outputs=false`、`this_command_wrote_formal_state=false`，本仓库仍无 `Submissions/formal_package/paper.pdf` 或 `paper.docx`。
- [x] P5-E5 验证：目标测试 3 OK；P5-E4/P5-E5/正式写回审批相邻回归 8 OK；Python 编译通过；真实 CLI 运行通过。
- [x] P6-A 节点规则：本节点只把已批准的 `paper_candidate.pdf` 晋升为最终 `paper.pdf`；不生成 docx，不改写 P5 审批账本，不改写正式研究状态。docx 导出预检拆到 P6-B，避免单节点超过 20 分钟。
- [x] P6-A Agent Team：使用 verifier sidecar Lagrange 复核 P6-A 边界；采纳其“审批后才能写最终产物、不得改写 P5 账本和正式状态”的保护建议，同时把 docx 写回拆出到 P6-B。
- [x] P6-A BDD/TDD：新增 Behavior 35 和 `tests/test_formal_pdf_final_writeback.py`；RED 为缺少 `Program/formal_pdf_final_writeback.py`，GREEN 后覆盖批准后写最终 PDF、未批准阻断、候选路径与批准账本不一致阻断。
- [x] P6-A 实现：新增 `Program/formal_pdf_final_writeback.py` 和 `Program/workbench/formal_pdf_final_writeback.py`，读取 candidate report、final preflight、final approval report 和 writeback approval ledger 后复制候选 PDF 为最终 PDF，并记录 sha256、bytes、路径和 formal state guard。
- [x] P6-A 真实运行：CLI 输出 `status=final_pdf_written`、`final_pdf=Submissions/formal_package/paper.pdf`、`wrote_final_pdf=true`、`wrote_docx=false`；`paper.pdf` 与 `paper_candidate.pdf` sha256 一致，本仓库仍无 `Submissions/formal_package/paper.docx`。
- [x] P6-A 验证：目标测试 3 OK；P5-E3/P5-E4/P5-E5/P6-A 相邻回归 10 OK；Python 编译通过。
- [x] P6-B 节点规则：本节点只做 docx 导出预检与工具链报告；不生成 `Submissions/formal_package/paper.docx`，不改写 `paper.pdf`、`paper_candidate.qmd`、P5/P6 审批账本或正式研究状态。
- [x] P6-B Agent Team：使用 verifier sidecar Volta 复核边界；采纳其建议，不复用旧 `state/product/docx_export_preflight.json`，改为正式包专用 `Results/json/formal_docx_export_preflight.json` 和 `Reviews/formal_docx_export_preflight.md`。
- [x] P6-B BDD/TDD：新增 Behavior 36 和 `tests/test_formal_docx_export_preflight.py`；RED 为缺少 `Program/formal_docx_export_preflight.py`，GREEN 后覆盖 ready、最终 PDF 写回未完成阻断、pandoc 缺失阻断。
- [x] P6-B 实现：新增 `Program/formal_docx_export_preflight.py` 和 `Program/workbench/formal_docx_export_preflight.py`，读取最终 PDF 写回报告、最终批准报告、批准账本和候选 QMD，记录 pandoc 路径/版本与计划导出命令。
- [x] P6-B 真实运行：CLI 输出 `status=ready_for_docx_export`、`can_export_docx=true`、`wrote_docx=false`；本机 `pandoc 3.9` 可用，本命令未创建 `Submissions/formal_package/paper.docx`。
- [x] P6-B 验证：目标测试 3 OK；P5-E3/P5-E4/P5-E5/P6-A/P6-B 相邻回归 13 OK；Python 编译和 scoped diff check 通过。
- [x] P6-C 节点规则：本节点只读取 P6-B `ready_for_docx_export` 报告并生成最终 `paper.docx`；不重新跑 P6-B，不改写 `paper.pdf`、`paper_candidate.qmd`、P5/P6 审批账本或正式研究状态。
- [x] P6-C Agent Team：使用 verifier sidecar Beauvoir 复核边界；采纳其建议，复用 `Program/export_docx.py` 的 pandoc 导出能力，但由 formal 专属 wrapper 写 `Results/json/formal_docx_export.json` 和 `Reviews/formal_docx_export.md`，并记录通用 `Submissions/export_manifest.json` 副产物。
- [x] P6-C BDD/TDD：新增 Behavior 37 和 `tests/test_formal_docx_export.py`；RED 为缺少 `Program/formal_docx_export.py`，GREEN 后覆盖 ready 导出、预检未 ready 阻断、候选 QMD 缺失阻断、最终 PDF 不回滚和正式状态不改写。
- [x] P6-C 实现：新增 `Program/formal_docx_export.py` 和 `Program/workbench/formal_docx_export.py`，读取 `formal_docx_export_preflight.json` 后调用通用 exporter，生成正式 docx，并记录 docx sha256、bytes、日志、命令、formal state guard 和 blocker。
- [x] P6-C 真实运行：CLI 输出 `status=docx_exported`、`docx=Submissions/formal_package/paper.docx`、`wrote_docx=true`；生成 `Submissions/formal_package/paper.docx`、`Results/json/formal_docx_export.json`、`Reviews/formal_docx_export.md`、`Results/logs/formal_docx_export.log` 和通用 `Submissions/export_manifest.json`。
- [x] P6-C 验证：目标测试 3 OK；P6-A/P6-B/P6-C 相邻回归 9 OK；完整 `python3 -m unittest discover -s tests -v` 383 OK / 1 skipped；Python 编译通过；真实报告确认 `formal_state_guard.changed=false`。
- [x] P6-D 节点规则：本节点只汇总正式投稿包 manifest 和人工验收说明；只读取 `paper.pdf`、`paper.docx`、P6-A/P6-B/P6-C 报告，不重新渲染 PDF/docx，不改写正式研究状态。后续每个小节点继续最多 20 分钟，超时必须拆小或回退路线。
- [x] P6-D Agent Team：使用 verifier sidecar Anscombe 复核边界；采纳其建议，输出 `Results/json/formal_submission_package_manifest.json`、`Reviews/formal_submission_package_acceptance.md` 和包内 `Submissions/formal_package/manifest.json`，并强制记录 PDF/docx 指纹、一致性检查、人工验收清单和“不渲染/不改正式状态”边界。
- [x] P6-D BDD/TDD：新增 Behavior 38 和 `tests/test_formal_submission_package_manifest.py`；RED 为缺少 `Program/formal_submission_package_manifest.py`，GREEN 后覆盖成功 manifest、P6-C 未 exported 阻断、docx 缺失阻断、P6-A hash 不一致阻断和正式层不改写。
- [x] P6-D 实现：新增 `Program/formal_submission_package_manifest.py` 和 `Program/workbench/formal_submission_package_manifest.py`，读取 P6-A/P6-B/P6-C 报告与最终 PDF/docx，写出验收 manifest、review markdown 和包内自包含 manifest。
- [x] P6-D 真实运行：CLI 输出 `status=formal_submission_package_ready`、`package_manifest_written=true`；真实包内 PDF sha256=`1dc03960fb232e198d64a60807d510939986b2905f504dd8d379f2edfbdf7ff0`，docx sha256=`77964d6a73a3be4abf9d128c17d61dd50e18eb0982c963b838e4c049cf7129cc`，一致性检查全部通过。
- [x] P6-D 验证：目标测试 4 OK；P6-A/P6-B/P6-C/P6-D 相邻回归 13 OK；Python 编译通过；完整回归 `python3 -m unittest discover -s tests -v` 通过，387 tests OK，skipped=1。
- [x] P6-E1 节点规则：按用户新增约束，本节点封顶 20 分钟；只把 P6-D 正式投稿包 manifest 转成产品层可读 summary，不做 HTTP API、不打开文件、不重渲染 PDF/docx、不改写正式研究状态。API/浏览器挂载拆到 P6-F。
- [x] P6-E1 Agent Team：使用 verifier sidecar Hubble 做只读复核；采纳其建议，把 P6-E 拆成“CLI/product state bridge”和后续“HTTP API/UI wiring”两段，避免一个节点同时处理状态归一化和接口集成。
- [x] P6-E1 BDD/TDD：新增 Behavior 39 和 `tests/test_formal_submission_package_summary.py`；RED 为缺少 `Program/formal_submission_package_summary.py`，GREEN 后覆盖成功 summary、manifest 未 ready 阻断、PDF 缺失阻断、docx hash 不一致阻断和正式层不改写。
- [x] P6-E1 实现：新增 `Program/formal_submission_package_summary.py` 和 `Program/workbench/formal_submission_package_summary.py`，读取 `Results/json/formal_submission_package_manifest.json` 与包内 `manifest.json`，写出 `Results/json/formal_submission_package_summary.json`、`state/product/formal_submission_package_summary.json`、`Reviews/formal_submission_package_summary.md`。
- [x] P6-E1 真实运行：CLI 输出 `status=ready_for_manual_acceptance`、`ready_for_manual_acceptance=true`；产品层 summary 暴露 PDF/DOCX 打开入口，PDF sha256=`1dc03960fb232e198d64a60807d510939986b2905f504dd8d379f2edfbdf7ff0`，docx sha256=`77964d6a73a3be4abf9d128c17d61dd50e18eb0982c963b838e4c049cf7129cc`，blocking reasons 为空。
- [x] P6-E1 验证：目标测试 4 OK；P6-A/P6-B/P6-C/P6-D/P6-E1 相邻回归 17 OK；Python 编译通过；完整回归 `python3 -m unittest discover -s tests -v` 通过，391 tests OK，skipped=1。
- [x] P6-F1 节点规则：按用户新增约束，本节点封顶 20 分钟；只提供正式包 summary 的只读产品 API，不做前端 UI、不打开文件、不重渲染 PDF/docx、不改写正式研究状态。浏览器挂载拆到 P6-F2。
- [x] P6-F1 Agent Team：使用只读 explorer sidecar Zeno 复核现有 Product API 入口；采纳其建议，新增 `GET /api/v1/projects/{project_id}/formal-submission-package-summary`，并把状态读取封装到独立 backend service，避免前端直接解析 CLI artifact。
- [x] P6-F1 BDD/TDD：新增 Behavior 40 和 `tests/test_formal_submission_package_summary_api.py`；RED 为 endpoint 404，GREEN 后覆盖成功读取、缺 summary 结构化 409、`_meta.service=formal_submission_package_service`、`mode=read_only` 和 summary 文件字节不变。
- [x] P6-F1 实现：新增 `Product/backend/formal_submission_package_service.py`，在 `Product/app.py` 暴露只读接口，返回 `visible_summary`、`open_targets`、`manual_acceptance`、`source_manifest`、`consistency_checks`、`blocking_reasons` 和产品元信息。
- [x] P6-F1 验证：目标测试 2 OK；P6-E1/P6-F1/API 相邻回归 15 OK，skipped=1；Python 编译通过；scoped diff 已复核。
- [ ] 下一步 P6-F2：把正式包 summary API 挂到产品页面或内置浏览器验收台，显示“打开 PDF/DOCX、验收清单、阻断原因”，并用 Browser 做可视化验收。

## 2026-05-27 P6-G5 Manuscript Section Scaffold

- [x] 节点时间盒：按用户新增约束，本节点封顶 20 分钟；只把 P6-G4 的 ManuscriptAgent 章节工单落成 `Manuscripts/sections/*.md` 草案入口，不扩写正文、不生成 PDF/docx、不写正式 `state/product/*`。
- [x] Agent Team：使用只读 explorer sidecar Pascal 复核可复用链路；采纳其建议，不复用 P5 formal section source drafter，单独实现 `paper_revision_round -> draft section scaffold`。
- [x] BDD/TDD：新增 Behavior 16.2 和 `test_bdd_11_2_section_work_orders_create_draft_section_scaffolds`；RED 为缺少 `Program/manuscript_section_scaffold.py`，GREEN 后覆盖章节文件生成、report/review 写出和正式层不改写。
- [x] 实现：新增 `Program/manuscript_section_scaffold.py` 和 `Program/workbench/manuscript_section_scaffold.py`，读取 `paper_revision_round.json.manuscript_section_work_orders`，写出章节草案入口、scaffold report 和 review markdown。
- [x] 验证：目标测试 1 OK；paper package quality 回归 15 OK；Python 编译通过；真实 CLI 输出 `status=section_scaffolds_ready`、`section_scaffolds=9`、`formal_state_guard.changed=false`，并生成 `Manuscripts/sections/main-results.md` 等 9 个章节入口。

## 2026-05-27 P6-G6a Manuscript Section Evidence Bindings

- [x] 节点时间盒：按用户新增约束，本节点封顶 20 分钟；只把章节入口绑定到真实 artifact 或显式缺口，不扩写正文、不生成 PDF/docx、不写正式 `state/product/*`。
- [x] Agent Team：按要求尝试新建只读 explorer 复核证据映射，但当前环境返回 `collab spawn failed: agent thread limit reached`；主 Agent 继续本地 BDD/TDD/CLI 闭环，并把下一次 Agent Team 调用点写入 evidence binding report。
- [x] BDD/TDD：新增 Behavior 16.3 和 `test_bdd_11_3_section_scaffolds_bind_real_evidence_or_explicit_gaps`；RED 为缺少 `Program/manuscript_section_evidence_bindings.py`，GREEN 后覆盖真实证据绑定、显式 missing evidence、正式层不改写和 Agent Team 调用节奏。
- [x] 实现：新增 `Program/manuscript_section_evidence_bindings.py` 和 `Program/workbench/manuscript_section_evidence_bindings.py`，读取 `paper_revision_round.json.manuscript_section_work_orders` 与 `manuscript_section_scaffold_report.json`，为每个 required evidence 记录路径、bytes、sha256、evidence level 或缺口。
- [x] 真实运行：CLI 输出 `status=section_evidence_bindings_ready`、`bound=27`、`missing=0`、`formal_writeback_allowed=false`；生成 `Results/json/manuscript_section_evidence_bindings.json` 和 `Reviews/manuscript_section_evidence_bindings.md`，Main Results 已绑定 `regression_tables.json`、`approved_findings.json` 和 coefficient 解释来源。
- [x] 验证：目标测试 1 OK；paper package quality 回归 16 OK；Python 编译通过；scoped `git diff --check` 通过。

## 2026-05-27 P6-G6b Main Results Evidence-Bound Draft Expansion

- [x] 节点时间盒：按用户新增约束，本节点封顶 20 分钟；只扩写 `Main Results` 草案层正文，不扩写全稿、不生成 PDF/docx、不写正式 `state/product/*`。
- [x] Agent Team：按要求尝试新建只读 verifier/explorer sidecar 复核章节扩写边界，但当前环境返回 `collab spawn failed: agent thread limit reached`；主 Agent 继续本地 BDD/TDD/CLI 闭环，并把下一次 Agent Team 调用点写入扩写报告。
- [x] BDD/TDD：新增 Behavior 16.4 和 `test_bdd_11_4_main_results_expansion_consumes_bound_evidence_only`；RED 为缺少 `Program/manuscript_section_draft_expansion.py`，GREEN 后覆盖 Main Results 只消费已绑定证据、章节草案写出、正式层不改写和 Agent Team 调用节奏。
- [x] 实现：新增 `Program/manuscript_section_draft_expansion.py` 和 `Program/workbench/manuscript_section_draft_expansion.py`，读取 `manuscript_section_evidence_bindings.json`，把 Main Results 的主回归表、approved findings 和系数解释来源整理成可审阅章节草案。
- [x] 真实运行：CLI 输出 `status=section_drafts_expanded`、`expanded=1`、`blocked=0`、`formal_writeback_allowed=false`；生成 `Results/json/manuscript_section_draft_expansion_report.json`、`Reviews/manuscript_section_draft_expansion.md`，并更新 `Manuscripts/sections/main-results.md`。
- [x] 验证：目标测试 1 OK；paper package quality 回归 17 OK；Python 编译通过；真实 CLI 运行通过；scoped `git diff --check` 通过。

## 2026-05-27 P6-G6c Main Results Semantic Review

- [x] 节点时间盒：按用户新增约束，本节点封顶 20 分钟；只对 `Main Results` 扩写草案做 VerifierAgent 语义核验，不改章节正文、不扩写下一节、不生成 PDF/docx、不写正式 `state/product/*`。
- [x] Agent Team：新建 subagent 仍受线程上限阻断；改为复用既有 Franklin sidecar 做只读复核，不阻塞主线 BDD/TDD/CLI 闭环。
- [x] BDD/TDD：新增 Behavior 16.5 和 `test_bdd_11_5_main_results_semantic_review_verifies_bound_claims`；RED 为缺少 `Program/manuscript_section_semantic_review.py`，GREEN 后覆盖 evidence id 声明、草案层边界、正式写回关闭、核心 claim 反查和 Agent Team 调用节奏。
- [x] 实现：新增 `Program/manuscript_section_semantic_review.py` 和 `Program/workbench/manuscript_section_semantic_review.py`，读取 `manuscript_section_draft_expansion_report.json` 与章节草案，只读生成 semantic review JSON 和人工审阅 Markdown。
- [x] 真实运行：CLI 输出 `status=semantic_review_passed`、`passed=1`、`needs_revision=0`、`formal_writeback_allowed=false`；生成 `Results/json/manuscript_section_semantic_review.json` 和 `Reviews/manuscript_section_semantic_review.md`。
- [x] 验证：目标测试 1 OK；paper package quality 回归 18 OK；Python 编译通过；真实 CLI 运行通过。

## 2026-05-27 P6-G6d Main Results Claim Ledger

- [x] 节点时间盒：按用户新增约束，本节点封顶 20 分钟；只把通过语义核验的 `Main Results` 转成草案层 claim ledger，不扩写正文、不生成 PDF/docx、不写正式 `state/product/*`。
- [x] Agent Team：按要求尝试新建 Verifier sidecar 复核节点，但当前环境返回 `collab spawn failed: agent thread limit reached`；主 Agent 继续本地 BDD/TDD/CLI 闭环，并把下一次 Agent Team 调用点写入 claim ledger。
- [x] BDD/TDD：新增 Behavior 16.6 和 16.7，覆盖“通过语义核验的章节必须生成论断账本”和“缺少已审批论断文本时不得编造 claim”；RED 为缺少 `Program/manuscript_section_claim_ledger.py`，GREEN 后覆盖 ready ledger、needs_revision ledger、正式层不改写和 Agent Team 调用节奏。
- [x] 实现：新增 `Program/manuscript_section_claim_ledger.py` 和 `Program/workbench/manuscript_section_claim_ledger.py`，读取 `manuscript_section_semantic_review.json` 与 `approved_findings.json`，只把章节中真实出现且已有 approved claim text 的论断写入账本。
- [x] 真实运行：当前真实 `Results/json/approved_findings.json` 的 approved finding 仍缺 `claim` 文本，因此 CLI 输出 `status=claim_ledger_needs_revision`、`claims=0`、`needs_revision=1`、`formal_writeback_allowed=false`；生成 `Results/json/manuscript_section_claim_ledger.json` 和 `Reviews/manuscript_section_claim_ledger.md`，缺口为 `no_approved_finding_claim_detected_in_section`。
- [x] 验证：新增目标测试 OK；paper package quality 回归 20 OK；Python 编译通过；真实 CLI 运行通过；scoped `git diff --check` 通过。

## 2026-05-27 P6-G6e Main Results Claim Proposal

- [x] 节点时间盒：本节点封顶 20 分钟；只把缺失 approved claim 文本的 `Main Results` 转成草案层 claim proposal，不批准论断、不改正文、不生成 PDF/docx、不写正式 `state/product/*`。
- [x] Agent Team：按要求尝试新建 Verifier sidecar 复核节点，但当前环境返回 `collab spawn failed: agent thread limit reached`；主 Agent 继续本地 BDD/TDD/CLI 闭环，并把 proposal 标记为 `needs_human_review`。
- [x] BDD/TDD：新增 Behavior 16.8 和 `test_bdd_11_8_missing_claim_text_generates_reviewable_claim_proposal`；RED 为 summary 缺少 `claim_proposals`，GREEN 后覆盖 proposal 字段、正式层不改写和不进入 `claims`。
- [x] 实现：扩展 `Program/workbench/manuscript_section_claim_ledger.py`，在 approved finding 缺 `claim` 但主回归表存在时，从真实回归表抽取 coefficient、standard error、p value 和 N，生成可审阅草案论断提案。
- [x] 真实运行：CLI 输出 `status=claim_ledger_needs_revision`、`claims=0`、`claim_proposals=1`、`needs_revision=1`、`formal_writeback_allowed=false`；proposal 绑定 `regression_table_1` 和 `finding_trained_effect`。
- [x] 验证：新增目标测试 OK；相邻 16.6/16.7 OK；paper package quality 回归 21 OK；Python 编译通过；真实 CLI 运行通过；scoped `git diff --check` 通过；完整回归 `python3 -m unittest discover -s tests -v` 通过，406 tests OK，skipped=1。

## 2026-05-27 P6-G6f Claim Proposal Human Review

- [x] 节点时间盒：本节点封顶 20 分钟；只记录 `claim_proposal` 的显式人工审阅动作，不晋升正式 claim、不改章节、不生成 PDF/docx、不写正式 `state/product/*`。如果后续小节点超过 20 分钟，必须继续拆小或回退路线。
- [x] Agent Team：按要求尝试新建 Verifier sidecar 复核节点，但当前环境返回 `collab spawn failed: agent thread limit reached`；主 Agent 继续本地 BDD/TDD/CLI 闭环，并把 `approve` 结果限制为 `approved_for_promotion`。
- [x] BDD/TDD：新增 Behavior 16.9 和 `test_bdd_11_9_claim_proposal_review_records_human_decision_without_promotion`；RED 为缺少 `Program/manuscript_claim_proposal_review.py`，GREEN 后覆盖 approve 审阅账本、正式层不改写和 proposal 不进入 `claims`。
- [x] 实现：新增 `Program/manuscript_claim_proposal_review.py` 和 `Program/workbench/manuscript_claim_proposal_review.py`，消费 `manuscript_section_claim_ledger.json` 中的 proposal，写出 `Results/json/manuscript_claim_proposal_review.json` 与 `Reviews/manuscript_claim_proposal_review.md`。
- [x] 真实运行：CLI 输出 `status=claim_proposal_approved_for_promotion`、`promotion_allowed=true`、`promoted_to_claims=false`、`formal_writeback_allowed=false`；真实 proposal 为 `main-results::finding_trained_effect::claim_proposal`。
- [x] 验证：新增目标测试 OK；paper package quality 回归 22 OK；Python 编译通过；真实 CLI 运行通过；scoped `git diff --check` 通过；完整回归 `python3 -m unittest discover -s tests -v` 通过，407 tests OK，skipped=1。

## 2026-05-27 P6-G6g Claim Promotion Patch

- [x] 节点时间盒：本节点封顶 20 分钟；只把 `approved_for_promotion` 的 claim proposal 转成正式层写回补丁提案，不直接改 `approved_findings.json`、章节草案、PDF/docx 或 `state/product/*`。
- [x] Agent Team：按要求尝试新建 Verifier sidecar 复核节点，但当前环境返回 `collab spawn failed: agent thread limit reached`；主 Agent 继续本地 BDD/TDD/CLI 闭环，并把本节点限制为 patch proposal。
- [x] BDD/TDD：新增 Behavior 16.10 和 `test_bdd_11_10_approved_claim_proposal_creates_patch_without_formal_writeback`；RED 为缺少 `Program/manuscript_claim_promotion_patch.py`，GREEN 后覆盖 patch operation、人工审阅证据、正式层不改写。
- [x] 实现：新增 `Program/manuscript_claim_promotion_patch.py` 和 `Program/workbench/manuscript_claim_promotion_patch.py`，读取 `manuscript_claim_proposal_review.json`，写出 `Results/json/manuscript_claim_promotion_patch.json` 与 `Reviews/manuscript_claim_promotion_patch.md`。
- [x] 真实运行：CLI 输出 `status=claim_promotion_patch_ready`、`ready_for_apply=true`、`applied=false`、`formal_writeback_allowed=false`；patch operation 指向 `Results/json/approved_findings.json` 中的 `finding_trained_effect`。
- [x] 验证：新增目标测试 OK；paper package quality 回归 23 OK；Python 编译通过；真实 CLI 运行通过；scoped `git diff --check` 通过；全量 `python3 -m unittest discover -s tests -v` 为 408 tests OK，skipped=1，耗时 160.148s。

## 2026-05-27 P6-G6h Claim Promotion Apply

- [x] 节点时间盒：本节点封顶 20 分钟；只在显式 `--confirm-apply`、审阅人和备注都存在时，把 claim promotion patch 写入 `Results/json/approved_findings.json`，不写章节、PDF/docx 或 `state/product/*`。
- [x] BDD/TDD：新增 Behavior 16.11 和 `test_bdd_11_11_explicit_apply_writes_claim_to_approved_finding_only`；RED 为缺少 `Program/manuscript_claim_promotion_apply.py`，GREEN 后覆盖 before/after hash、审阅证据、正式 finding claim 写入和边界文件不变。
- [x] 实现：新增 `Program/manuscript_claim_promotion_apply.py` 和 `Program/workbench/manuscript_claim_promotion_apply.py`，消费 `manuscript_claim_promotion_patch.json`，写出 apply report 与 review markdown。
- [x] 真实运行：CLI 输出 `status=claim_promotion_patch_applied`、`applied=true`、`formal_writeback_allowed=true`；真实 `approved_findings.json` 的 `finding_trained_effect.claim` 已写入已审阅论断，并保留 proposal id、source table、reviewer 和 before/after hash。
- [x] 验证：新增目标测试 OK；paper package quality 回归 24 OK；全量测试 `409 tests OK / skipped=1`；Python 编译通过；真实 CLI 运行通过；scoped `git diff --check` 通过。

## 2026-05-27 P6-G6i Claim Ledger Consumption

- [x] 节点时间盒：本节点封顶 20 分钟；只重跑章节草案扩写、语义核验和章节论断账本，验证刚写回的正式 claim 是否被 `Main Results` 草案消费，不新增代码。
- [x] Agent Team：再次尝试派发 sidecar explorer 复核下一节点拆法，但运行环境返回 `agent thread limit reached`；本节点改为本地执行，不把时间耗在调度失败上。
- [x] 真实运行：先重跑 claim ledger 得到 `claim_ledger_needs_revision`，缺口为 `no_approved_finding_claim_detected_in_section`；随后重跑 `manuscript_section_draft_expansion -> manuscript_section_semantic_review -> manuscript_section_claim_ledger`，最终输出 `claim_ledger_ready`、`claims=1`、`needs_revision=0`。
- [x] 验证：`test_bdd_11_6_passed_section_review_creates_reviewable_claim_ledger` OK；三个报告的 `formal_state_guard.changed=false`；`Main Results` 已消费 `finding_trained_effect.claim`，但仍处于草案层。

## 2026-05-27 P6-G6j PDF Export Preflight Refresh

- [x] 节点时间盒：按用户新增约束，本节点封顶 20 分钟；只刷新 PDF 导出前置预检，不渲染 PDF、不生成 docx、不改写正式研究状态。若后续 PDF 渲染超过 20 分钟，必须拆成“定位渲染器 / 候选渲染 / 验收记录”更小节点。
- [x] 节点效率规则：P4/P5/P6 任意 A/B/C/D/G6x 小节点默认最多 20 分钟；超过即拆解或回退路线，不允许把多个目标塞进一个节点。
- [x] 真实运行：`formal_pdf_export_preflight` 输出 `status=ready_for_pdf_export_review`、`can_export_pdf_candidate=true`、`blocking_reasons=[]`、`formal_state_guard.changed=false`。
- [x] 验证：`python3 -m unittest tests.test_formal_pdf_export_preflight -v` 3 tests OK；预检 review 显示章节源与 19 项证据检查全部 passed；下一步为 `render_pdf_candidate`。

## 2026-05-27 P6-G6k PDF Candidate Render

- [x] 节点时间盒：本节点封顶 20 分钟；只渲染候选层 `paper_candidate.pdf` 和 `paper_candidate.qmd`，不批准最终 PDF、不生成 docx、不写 `state/product/*`。
- [x] Agent Team：按用户要求尝试派发只读 explorer 定位 PDF 渲染链路，但当前环境返回 `agent thread limit reached`；主 Agent 直接复用既有 `formal_pdf_candidate` 链路，不重复造轮子。
- [x] 真实运行：`Program/formal_pdf_candidate.py --render-mode auto` 输出 `status=pdf_candidate_ready`、`output_pdf_exists=true`；Quarto 调用 xelatex 完成 3 轮编译，生成 `Submissions/formal_package/paper_candidate.pdf`。
- [x] 验证：`python3 -m unittest tests.test_formal_pdf_candidate -v` 2 tests OK；候选 PDF bytes=107169，QMD bytes=10886，复跑脚本 bytes=633；报告声明 `formal_state_guard.changed=false`、`this_command_wrote_formal_state=false`、`this_command_wrote_final_outputs=false`。

## 2026-05-27 P6-G6l PDF Candidate Machine Review

- [x] 节点时间盒：本节点封顶 20 分钟；只做候选 PDF 机器审阅与最终写回预检，不批准最终 PDF、不复制为 `paper.pdf`、不生成 docx、不写 `state/product/*`。
- [x] Agent Team：按用户要求尝试派发 Verifier sidecar 复核候选 PDF 审阅入口，但当前环境返回 `agent thread limit reached`；主 Agent 用既有 `formal_pdf_candidate_review` CLI 完成本地可验证闭环。

## 2026-05-27 P6-G6m+ 节点执行校准

- [x] 用户新增硬约束：后续每一个小节点最多 20 分钟；超过即拆分或回退路线判断，不再把多个目标塞进单个节点。
- [x] 启动约束：每个节点开始前写清“只解决什么、产物是什么、验收命令是什么”。
- [x] 收尾约束：每个节点结束时写清“是否 20 分钟内闭环、是否需要拆下一节点、Agent Team 是否成功调用或为何受限”。
- [ ] 下一步 P6-G6m：仅记录候选 PDF 的人工最终批准；不复制为最终 `paper.pdf`，不生成 docx，不改写正式研究状态。
- [ ] 下一步 P6-G6n：在 P6-G6m 已批准后，把 `paper_candidate.pdf` 晋升为正式 `paper.pdf`；不重新渲染，不改审批账本。
- [x] 真实运行：`Program/formal_pdf_candidate_review.py` 输出 `status=ready_for_final_approval_review`、`can_request_final_approval=true`；`formal_pdf_final_writeback_preflight.json` 输出 `status=ready_for_human_final_approval`、`final_writeback_allowed=false`。
- [x] 验证：`python3 -m unittest tests.test_formal_pdf_candidate_review -v` 2 tests OK；PDF metadata 为 `readable`、pages=10、bytes=107169；机器审阅 10 项检查全部 passed，`formal_state_guard.changed=false`。

## 2026-05-27 P6-H0 Formal Package Audit And Timebox Enforcement

- [x] 节点时间盒：本节点封顶 20 分钟；只做正式包完成度审计和节奏校准，不渲染 PDF，不生成 docx，不改写正式研究状态，不扩展 UI。
- [x] 用户新增硬约束升级：P4/P5/P6 任意 A/B/C/D/G6x/Hx 小节点最多 20 分钟；超过 20 分钟必须拆成更小节点，或判断当前路线走错并回退。质量标准不降低，靠更小切片、真实验证和 Agent Team 提速。
- [x] Agent Team：尝试沿用 Verifier sidecar 做只读复核；新建线程受 `agent thread limit reached` 限制时，复用现有 Franklin 线程完成正式包审计。主 Agent 不等待空转，同时本地执行 hash 审计和全量测试。
- [x] 本地审计：`paper.pdf` hash=`1dc03960fb232e198d64a60807d510939986b2905f504dd8d379f2edfbdf7ff0`，`paper.docx` hash=`77964d6a73a3be4abf9d128c17d61dd50e18eb0982c963b838e4c049cf7129cc`；`formal_submission_package_summary.json` 当前为 `ready_for_manual_acceptance` 且 `blocking_reasons=[]`。
- [x] Agent Team 复核发现：最终 `paper.pdf` 与 `paper.docx` 包自身一致，但当前磁盘上的 `Submissions/formal_package/paper_candidate.pdf` hash=`07bcaebc586f445a01fc34b95bb63bec82e5ac57ff465ea4770149da2d38ca88`，与 `formal_pdf_final_writeback.json` 记录的 `source_candidate_sha256=1dc03960fb232e198d64a60807d510939986b2905f504dd8d379f2edfbdf7ff0` 不一致。
- [x] 全量验证：`python3 -m unittest discover -s tests -v` 通过，409 tests OK，skipped=1，用时 272.469s。
- [x] 下一步 P6-H1：做 `formal_package_provenance_lock_check` 小节点，只比较 final writeback 记录、当前 candidate PDF、最终 PDF、docx 和 submission manifest 的 provenance 一致性；不重渲染、不导出、不改正式层。若 candidate 漂移确认存在，输出锁定报告并决定是冻结批准时 candidate、重新跑短链审批，还是把 candidate 从最终验收视图中降级为历史候选。

## 2026-05-27 P6-H1 Formal Package Provenance Lock Check

- [x] 节点时间盒：本节点封顶 20 分钟；只做正式投稿包来源锁校验，不重渲染 PDF，不导出 DOCX，不改 `state/product/*`，不改写 final package 产物。
- [x] Agent Team：复用 Franklin sidecar 做只读复核，主线不等待空转；sidecar 要求只输出当前 provenance 状态、P6-H1 应检测的 warning/blocker 和 acceptance tests。
- [x] BDD/TDD：新增 Behavior 44 和 `tests/test_formal_package_provenance_lock_check.py`；RED 为缺少 `Program/formal_package_provenance_lock_check.py`，GREEN 后覆盖来源锁定、候选稿漂移 warning、最终 PDF hash 破坏 blocker、summary 未 ready blocker 和输入文件不变。
- [x] 实现：新增 `Program/formal_package_provenance_lock_check.py` 和 `Program/workbench/formal_package_provenance_lock_check.py`，读取 final writeback、docx export、submission manifest、summary 和包内 manifest，写出 `Results/json/formal_package_provenance_lock_check.json` 与 `Reviews/formal_package_provenance_lock_check.md`。
- [x] 真实运行：CLI 输出 `status=ready_for_manual_acceptance_with_provenance_warning`、`can_continue_manual_acceptance=true`；最终 `paper.pdf` 与 `paper.docx` 产物锁一致，当前 `paper_candidate.pdf` 相对最终写回记录发生漂移，且 bytes 同为 107169 但 sha256 不同，warning=`candidate_pdf_drifted_from_final_writeback_source`、`candidate_pdf_same_size_but_hash_changed`。
- [x] 验证：目标测试 4 OK；相邻正式包链路回归 18 OK；真实 CLI 运行通过；报告声明 `formal_state_guard.changed=false`、`this_command_wrote_final_outputs=false`、`this_command_wrote_formal_state=false`。
- [x] 下一步 P6-H2：用 20 分钟小节点处理 candidate 漂移决策。推荐先做 `freeze_approved_candidate_snapshot`：保存最终写回时的权威 candidate 指纹和来源说明，把当前 `paper_candidate.pdf` 标成“后续草案/历史候选”，避免用户验收时把候选层和正式层混在一起。

## 2026-05-27 P6-H2 Approved Candidate Snapshot Freeze

- [x] 节点时间盒：本节点封顶 20 分钟；只冻结已批准 candidate 的来源权威，不重渲染 PDF，不导出 DOCX，不改 `state/product/*`，不改 `paper.pdf`、`paper.docx`、`paper_candidate.pdf` 或 `manifest.json`。
- [x] Agent Team：复用 Franklin sidecar 做只读复核，确认应读取 P6-H1 provenance lock、final writeback、formal package 产物和 summary；建议写 package-local sidecar `Submissions/formal_package/provenance/approved_candidate_snapshot.json`，并保持正式产物不可变。
- [x] BDD/TDD：新增 Behavior 45 和 `tests/test_formal_package_candidate_snapshot_freeze.py`；RED 为缺少 `Program/formal_package_candidate_snapshot_freeze.py`，GREEN 后覆盖权威快照写入、broken provenance blocker、正式产物不变和正式状态不变。
- [x] 实现：新增 `Program/formal_package_candidate_snapshot_freeze.py` 和 `Program/workbench/formal_package_candidate_snapshot_freeze.py`，读取 `formal_package_provenance_lock_check.json` 与 `formal_pdf_final_writeback.json`，写出 `Results/json/formal_package_candidate_snapshot_freeze.json`、`Reviews/formal_package_candidate_snapshot_freeze.md` 和 `Submissions/formal_package/provenance/approved_candidate_snapshot.json`。
- [x] 真实运行：CLI 输出 `status=approved_candidate_snapshot_frozen`、`snapshot_written=true`；批准时 candidate 的权威 hash 为 `1dc03960fb232e198d64a60807d510939986b2905f504dd8d379f2edfbdf7ff0`，由 `Submissions/formal_package/paper.pdf` 恢复；当前 `paper_candidate.pdf` 被标记为 `historical_candidate_or_next_draft`。
- [x] 验证：目标测试 2 OK；相邻正式包来源链路回归 10 OK；真实 CLI 运行通过；Python 编译和 scoped `git diff --check` 通过；报告声明 `formal_state_guard.changed=false`、`this_command_wrote_final_outputs=false`、`this_command_wrote_formal_state=false`。
- [x] 下一步 P6-H3：把 `approved_candidate_snapshot.json` 接入正式包验收摘要或导出审计视图，让用户验收时只看到“正式包权威稿”和“当前候选草案”的清晰区分。

## 2026-05-27 P6-H3 Formal Acceptance Summary Candidate Authority

- [x] 节点时间盒：本节点封顶 20 分钟；只把 P6-H2 的 `approved_candidate_snapshot.json` 接入正式包 summary，不改 UI，不重写正式包，不改正式研究状态。
- [x] Agent Team：复用 Franklin sidecar 只读定位 summary CLI/module/test 和最小字段，回收结论为只改 `Program/formal_submission_package_summary.py`、`Program/workbench/formal_submission_package_summary.py`、`tests/test_formal_submission_package_summary.py` 及 summary 输出。
- [x] BDD/TDD：新增 Behavior 46，先确认 summary 缺少 `approved_candidate_snapshot` 的 RED，再实现 GREEN。
- [x] 实现：`formal_submission_package_summary` 新增 `approved_candidate_snapshot` 聚合字段，并在 `visible_summary` 中加入 `approved_candidate_authority`，明确 `paper.pdf` 是当前正式包权威稿，`paper_candidate.pdf` 是后续草案/历史候选。
- [x] 真实运行：重跑 `Program/formal_submission_package_summary.py --project-root .`，输出 `status=ready_for_manual_acceptance`、`approved_candidate_snapshot.status=available`、`authority=formal_pdf_final_writeback`、`current_candidate.treatment=historical_candidate_or_next_draft`。
- [x] 验证：目标测试 1 OK；summary 测试 5 OK；相邻 P6-H1/H2/H3 链路 11 OK；Python 编译通过；真实 summary review 已列出“权威稿”摘要。
- [x] 下一步 P6-H4：把正式包验收摘要接入一个 CLI 级人工验收记录节点，记录用户是否接受 PDF/DOCX，而不是继续生成新候选稿。

## 2026-05-27 P6-H4 Formal Package Manual Acceptance Record

- [x] 节点时间盒：本节点封顶 20 分钟；只建立正式包人工验收记录 CLI，不生成新候选稿，不重渲染 PDF，不导出 DOCX，不改 `paper.pdf`、`paper.docx`、`manifest.json` 或正式研究状态。
- [x] Agent Team：尝试新建只读 sidecar 失败，原因仍为 `agent thread limit reached`；改为复用 Franklin sidecar。sidecar 建议的最小节点名为 `formal_submission_package_manual_acceptance`，并确认应保护正式包产物和 `state/product/*` 正式研究状态。
- [x] BDD/TDD：新增 Behavior 47；RED 先确认为缺少 `Program/formal_submission_package_manual_acceptance.py`，随后补最小实现；补充 `defer` 决策，避免 Codex 在未获得用户确认时伪造“已接受”。
- [x] 实现：新增 `Program/formal_submission_package_manual_acceptance.py` 和 `Program/workbench/formal_submission_package_manual_acceptance.py`，消费 `state/product/formal_submission_package_summary.json`，写出 `Results/json/formal_submission_package_manual_acceptance.json`、`state/product/formal_submission_package_manual_acceptance.json` 与 `Reviews/formal_submission_package_manual_acceptance.md`。
- [x] 真实运行：当前真实项目以 `--decision defer` 记录为 `pending_human_manual_acceptance`，PDF/DOCX hash 已锁定，`accepted=false`，下一步为 `open_and_review_pdf_docx`。
- [x] 验证：目标测试 4 OK；相邻 summary 回归合计 9 OK；Python 编译通过；真实 CLI 运行通过；命令声明 `formal_state_guard.changed=false`、`this_command_wrote_final_outputs=false`。
- [ ] 下一步 P6-H5：在用户实际打开 PDF/DOCX 后，用同一 CLI 写入 `accept`、`needs_revision` 或 `reject` 的真实人工决定；不自动替用户接受。

## 2026-05-27 P6-H5a Formal Package Human Review Handoff

- [x] 节点时间盒：本节点封顶 20 分钟；只交接人工审阅文件位置和审阅清单，不重跑论文、不改稿、不生成新 PDF/DOCX、不替用户接受。
- [x] Agent Team：本节点不派新 Agent。原因是任务已收敛为人工审阅交接，继续派发会增加沟通成本；下一次 Agent Team 调用点为用户给出 `needs_revision` 或 `reject` 后，由 ReviewerAgent/ManuscriptAgent/MethodAgent 按问题类型拆分修订任务。
- [x] 审阅文件：正式 PDF 为 `Submissions/formal_package/paper.pdf`；正式 DOCX 为 `Submissions/formal_package/paper.docx`；包清单为 `Submissions/formal_package/manifest.json`。
- [x] 审阅重点：先看 PDF/DOCX 是否能打开、标题和章节结构是否像一篇论文、摘要/引言/文献/数据/方法/结果/结论是否完整、表格和证据说明是否可读、是否有明显空段/模板话/乱码/格式问题。
- [x] 当前验收状态：重新以 `--decision defer` 记录为 `pending_human_manual_acceptance`，说明系统等待用户审阅；这不是通过，也不是退修。
- [ ] 下一步 P6-H5b：用户审阅后，执行 `accept`、`needs_revision` 或 `reject`。若是 `needs_revision`，必须把用户意见拆成 <=20 分钟的小节点进入修订队列。

## 2026-05-27 P6-I1 CGSS Topic-To-Paper Capability Audit

- [x] 节点时间盒：本节点控制在 20 分钟内；只判断新题目“社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析”能不能复用当前正式论文包，不写正式变量角色、不改设计方案、不生成新论文。
- [x] 结论：当前正式包是机器人/CFPS 题目，不能直接拿来冒充 CGSS 幸福感题目；新题目必须重新走数据绑定、变量画像、方法设计和论文写作。
- [x] 实现：新增 `Program/topic_to_paper_capability_audit.py` 与 `Program/workbench/topic_to_paper_capability_audit.py`，写出 `Results/json/topic_to_paper_capability_audit.json` 和 `Reviews/topic_to_paper_capability_audit.md`。
- [x] 验证：`python3 -m unittest tests.test_topic_to_paper_capability_audit -v` 2 tests OK；真实 CLI 运行通过。

## 2026-05-27 P6-I2 CGSS Data Discovery And Variable Candidate Profile

- [x] 节点时间盒：本节点控制在 20 分钟内；只读取本机 CGSS 数据元信息并生成候选变量，不把候选变量写成正式角色。
- [x] Agent Team：把真实 CGSS 数据发现交给 sidecar 只读完成；回收结论为 CGSS2023、CGSS2021、CGSS2018 都存在，并包含幸福感、信任、社会交往、社会支持和常用人口学控制变量。
- [x] 实现：新增 `Program/cgss_topic_variable_discovery.py` 与 `Program/workbench/cgss_topic_variable_discovery.py`，读取 `.dta` metadata，写出 `Results/json/cgss_social_capital_happiness_variable_candidates.json` 和 `Reviews/cgss_social_capital_happiness_variable_candidates.md`。
- [x] 初步候选：因变量优先看 `a36/A36/D36/D1`；社会资本优先看信任 `a33/A33`、交往频率 `a31a/a31b/a311`、社会支持 `c11*/c12*`；控制变量优先看性别、年龄、教育、收入、健康、户籍和省份。
- [x] 验证：`python3 -m unittest tests.test_cgss_topic_variable_discovery -v` 2 tests OK；真实 CGSS 目录运行通过。

## 2026-05-27 P6-I3 CGSS Minimal Model

- [x] 节点时间盒：本节点控制在 20 分钟内；只跑 CGSS2023 最小基准模型，产物停留在探索性结果，不写正式论文包。
- [x] 实现：新增 `Program/cgss_minimal_model.py` 与 `Program/workbench/cgss_minimal_model.py`，读取 CGSS2023，清洗特殊缺失值，构造幸福感、信任、邻里交往、朋友交往、休闲社交和社会资本指数，并加入性别、年龄、教育、收入、健康、户籍、省份控制。
- [x] 真实结果：CGSS2023 样本量为 5310；社会资本指数系数约 `0.1658`，稳健标准误约 `0.0187`，p 值小于 `0.001`；信任和休闲社交也呈正向关系，邻里/朋友交往在当前模型中不稳定。
- [x] 调试记录：发现 `log_income` 被错误当作分类变量后已修复为连续变量，并新增测试防止回归表出现 `log_income[T.*]` 这类错误。
- [x] 产物：`Results/json/cgss_social_capital_happiness_minimal_model.json` 与 `Reviews/cgss_social_capital_happiness_minimal_model.md`。
- [x] 验证：`python3 -m unittest tests.test_cgss_minimal_model -v` 1 test OK；P6-I scoped 回归 5 tests OK；真实 CLI 运行通过。
- [x] 下一步 P6-I4：补有序因变量稳健性和方法门禁，优先跑 ordered logit / ordered probit 候选；如果超过 20 分钟，拆成“方法可用性检查”和“稳健性运行”两个节点。

## 2026-05-27 P6-I4 CGSS Ordered Outcome Robustness

- [x] 节点时间盒：本节点控制在 20 分钟内；只补幸福感有序因变量的 ordered logit 稳健性，不晋升正式变量角色，不写正式论文包。
- [x] BDD/TDD：新增 `tests/test_cgss_ordered_robustness.py`，先确认缺少 `Program.workbench.cgss_ordered_robustness` 的 RED，再实现 GREEN；覆盖“可跑有序模型”和“幸福感等级不足时被方法门禁拦住”两个行为。
- [x] 实现：新增 `Program/cgss_ordered_robustness.py` 与 `Program/workbench/cgss_ordered_robustness.py`，复用 CGSS2023 分析样本，按 `happiness` 1-5 等级估计 ordered logit，并写出 JSON 与 Markdown 审阅报告。
- [x] 真实结果：CGSS2023 样本量为 5310，幸福感覆盖 1-5 五个等级，方法门禁通过；`social_capital_index` ordered logit 系数约 `0.4050`，标准误约 `0.0424`，p 值小于 `0.001`，方向与 OLS 一致。
- [x] 产物：`Results/json/cgss_social_capital_happiness_ordered_robustness.json` 与 `Reviews/cgss_social_capital_happiness_ordered_robustness.md`。
- [x] 验证：`python3 -m unittest tests.test_cgss_ordered_robustness -v` 2 tests OK；P6-I scoped 回归 7 tests OK；真实 CLI 运行通过。
- [x] 下一步 P6-I5：把 OLS 与 Ordered Logit 合并成“结果证据包”，生成论文写作可消费的表格摘要和变量口径待确认清单；仍不写正式 paper package。

## 2026-05-27 P6-I5 CGSS Results Evidence Package

- [x] 节点时间盒：本节点控制在 20 分钟内；只合并 OLS 与 Ordered Logit 的结果证据，供后续论文草稿消费，不写正式 paper package，不晋升正式变量角色。
- [x] Agent Team：派发 verifier sidecar 做只读复核；回收建议后补齐 `source_artifacts`、输入 schema/status、变量口径、method gate 阻断测试，并保留正式层边界 flags。
- [x] BDD/TDD：新增 `tests/test_cgss_results_evidence_package.py`，先确认缺少 `Program.workbench.cgss_results_evidence_package` 的 RED，再实现 GREEN；覆盖 OLS/Ordered 合并、缺模型阻断、Ordered gate 未通过阻断、审阅文件写出。
- [x] 实现：新增 `Program/cgss_results_evidence_package.py` 与 `Program/workbench/cgss_results_evidence_package.py`，读取 `cgss_social_capital_happiness_minimal_model.json` 和 `cgss_social_capital_happiness_ordered_robustness.json`，写出结果证据包 JSON 与 Markdown。
- [x] 真实结果：证据包状态为 `ready_for_paper_draft_input`；OLS 与 Ordered Logit 的核心变量都是 `social_capital_index`，样本量都为 5310，方向一致为正；写作种子句已生成。
- [x] 产物：`Results/json/cgss_social_capital_happiness_results_evidence_package.json` 与 `Reviews/cgss_social_capital_happiness_results_evidence_package.md`。
- [x] 验证：`python3 -m unittest tests.test_cgss_results_evidence_package -v` 4 tests OK；P6-I scoped 回归 11 tests OK；Python 编译通过；真实 CLI 运行通过。
- [x] 下一步 P6-I6：从结果证据包生成“变量角色审阅草案”，要求把因变量、社会资本指数、控制变量的选择理由写清楚，但仍等待人工确认后才能进入正式变量角色。

## 2026-05-27 P6-I6 CGSS Variable Role Review Draft

- [x] 节点时间盒：本节点控制在 20 分钟内；只生成变量角色审阅草案，不写 `state/product/variable_roles.json`，不改 `DesignSpec`、`RunPlan` 或正式论文包。
- [x] Agent Team：复用 verifier sidecar 做只读复核；回收意见后补齐正式层边界、OLS/Ordered Logit 结果证据、原始变量候选映射和 pending 人工审阅决定。
- [x] BDD/TDD：新增 `tests/test_cgss_variable_role_review_draft.py`，先确认缺少 `Program.workbench.cgss_variable_role_review_draft` 的 RED，再实现 GREEN；覆盖可审阅草案、证据包未 ready 阻断、草案文件写出和正式层不改写。
- [x] 实现：新增 `Program/cgss_variable_role_review_draft.py` 与 `Program/workbench/cgss_variable_role_review_draft.py`，读取结果证据包和变量候选画像，写出 `Results/json/cgss_social_capital_happiness_variable_role_review_draft.json` 与 `Reviews/cgss_social_capital_happiness_variable_role_review_draft.md`。
- [x] 真实结果：草案状态为 `needs_human_role_review`；因变量为 `happiness <- a36`，核心解释变量为 `social_capital_index`，来源题项为 `a33/a31a/a31b/a311`，控制变量包括性别、年龄、教育、收入、健康、户籍和省份固定效应；模型证据显示 OLS 和 Ordered Logit 样本量均为 5310、方向一致为正。
- [x] 验证：目标测试 3 OK；P6-I scoped 回归 14 OK；Python 编译通过；真实 CLI 运行通过。
- [ ] 下一步 P6-I7：生成 CGSS 文献综述种子包。要求接入 Scholar/CNKI/Zotero 或本地文献来源，形成“社会资本—主观幸福感”的文献、机制和变量依据；仍不写正式论文正文。
