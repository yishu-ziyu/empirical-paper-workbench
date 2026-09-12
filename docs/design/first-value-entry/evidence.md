# 能力与案例证据

本稿对外描述以 [能力清单](../../product/capability-inventory.md) 的允许文案和限制为边界；[术语表](../../product/terminology.md) 控制中英用词。英文页面是对应语义翻译，适用范围不扩张。

| 页面能力陈述（中 / 英） | 清单条目 | 证据及范围 |
|---|---|---|
| 比较两条真实设定 / Compare two real specifications | 多方案比较、单次估计 | Card Evidence Lab 旅程与 test_card_spec_run.py；本页仅下述已归档 pair，不泛化方法覆盖 |
| 查看改变与保持的设定 / See what changed and what stayed fixed | 多方案比较 | 两 run 的 choices/formula/covariance；见 card-pair.json，协方差也变了 |
| 追到数据与计算来源 / Trace data and calculation sources | 证据关联、单次估计 | run provenance、analysis_dataset.hash、producer_run_id；只承诺本案例有证据 |
| 确认分析方案后运行 / Confirm plans before running | 分析方案、预期 | Card freeze API / test_card_research_lab.py；Card 方案范围 |
| 结论需要你确认 / You confirm the conclusion | 结论确认 | test_card_claim_ledger.py、r3 approve 旅程；不代表因果已证明 |
| 可上传 CSV / Stata / Excel，记录类型与清洗 / Upload CSV, Stata or Excel with type and cleaning records | 数据导入和清洗 | test_upload.py、test_clean.py；实现存在；页面自然文案为“尚未完整验证任意自带数据从清洗到成文的全过程” |
| 按章写并确认，可下载文档和分析代码 / Write and review by chapter; download documents and analysis code | 章节编辑/回滚、文档和代码导出 | test_chapter.py、test_doc_export.py、test_code_export.py；页面说明“完整成文质量尚未验证；下载脚本不保证不同语言算出一致数值”；完整自带数据旅程与跨语言数值复现未验证，不能将 r3 mock 结果章作为真实写作证据 |
| 桌面工作台入口 / Desktop workbench entry | 上手入口 + 界面语言 | 不阻拦已有会话；完整 GuidePage/DeskPage 已读；已有回调入口，设计稿未接线；不承诺手机工作台 |

## 本页数字唯一来源

原始：`/tmp/econpaper-r3/journey-log-final.json`，`/calls/10/response/specification_runs`。最小去敏快照 [card-pair.json](card-pair.json) 记录原始归档 SHA-256、完整来源引用、数据 hash、formula、covariance、设定和 run ID。删去本机数据绝对路径，未复制用户信息或原始 CSV。这里的会话/run ID 是教学测试记录定位符。

- session：`5b4c3539-abf6-423e-9186-8fc950bc2983`，producer run：`3d4c6546-cadb-4b3a-a7b6-0bb101492f58`。
- 两条 run 均 `status=ok`，创建时刻 `2026-09-07T16:16:38+00:00`；两者 n=3010。
- A `ols_region_dummies`：coef `0.07469325559311334`，SE `0.0034983456584787432`，estimator `statspai.feols`，covariance `HC1`。
- B `iv_region_dummies`：coef `0.13150383625543327`，SE `0.05496367260228859`，estimator `statspai.ivreg`，covariance `nonrobust`。
- 展示只四舍五入为 0.0747 / 0.1315；不混用同批中 `ols_full_controls` 0.0740 / `iv_nearc4_full` 0.1323。
- 改变：OLS→IV；不使用工具→`nearc4`；协方差 HC1→nonrobust（影响推断，不能把两者的标准误当作完全同口径）。保持：同一数据 hash、educ/lwage、经验二次项、black、smsa/south、1966 地区控制、n=3010。只是观察到系数不同，不能从此断言哪个更接近真值。
- 来源：`statspai:papers/data_card1995.csv`，extract `wooldridge_card_34`。源 checksum `eda514228a77327ab9aa20df72b89256cdec579482fa9dbbe4e3d757748c9bf2`；分析数据 hash `f1833bfc3ad60bac52577b6e0cdba08c40567e9515d303045be152ebc6d40d27`。两种 hash 指向不同层，不混为同一个文件。

## 必须带着的限制

能力清单将本地约 0.0747/0.1315 与 CI 约 0.0740/0.1323 的差异记为**复现待核**。本次 pair 核对说明这一归档同时有不同设定的数值，不据此提前宣布跨环境差异已解决，也不归因为平台浮点误差。

[最近 r3 validator](../../acceptance/localized-first-study-r3-validator.md) 指出旧契约 zh 会话 ID 记错、最终 JSON 实际只有 en 标签的一遍，不能宣称它含双语独立归档。正确 zh 会话据服务器日志为 e6df83df-2652-48e5-bb96-8b057f1cde1c；本稿只引用可直接核对的 en 会话。API 标签不证明界面语言；此前语言证据是组件测试与 Scene D。

同次 results chapter `generation_source=mock, generation_degraded=true`。不能作为真实 LLM 成文演示或论文质量证据；本稿不展示其正文。原有旧截图若含内部英文、旧结果或旧壳，不代表当前实现。此 HTML 的结果卡是以真实运行数据重排的**设计稿**，不是当前产品截图；实际运行已发生于历史验收，不在打开页面时重算。

本轮没有重新执行 Card、没有数值复现裁决、没有真人理解数据。主 agent/validator 的本地渲染记录只证明设计稿可查看。
