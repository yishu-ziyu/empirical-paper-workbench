# 展示术语表（Localized first study · C2）

这些是**界面展示语言**。后端对象名（`canonical_spec_id`、`PromoteRequest`、`claim`、`stale`、`grounded`、`provenance` 等）不要求重命名。

文稿语言（论文用中文还是英文写）**未实现**，不要做假开关。`expectation.locale` 只随预期文本存储，不是文稿语言。

## B4 对照

| 内部对象 / 工程名 | 中文主界面 | 英文主界面 | 一句话帮助 |
|---|---|---|---|
| Canonical / canonical spec | 当前主分析 | Primary analysis | 报告和导出默认引用的那条估计。 |
| Promote | 设为主分析 | Set as primary analysis | 把选中的设定改成报告里的主结果；预览在你确认前不会顶替它。 |
| Claim Ledger | 研究结论 | Research claims | 要写入论文前，需要你确认的结论及其三种措辞。 |
| Stale | 证据已更新，请重新核对 | Evidence updated — review needed | 估计或主分析变了，旧结论不能继续当作已核对。 |
| Provenance | 数据与计算来源 | Data & calculation sources | 这条数字从哪份数据、哪次运行、哪条设定来。 |
| Grounded | 已关联当前证据 | Linked to current evidence | 正文里的数字和结论仍指向现在的证据，而不是过期稿。 |
| Research Question | 研究问题 | Research question | 这篇研究要回答什么。 |
| Expectation | 预期 | Expectation | 在看到结果之前，你认为估计会怎样。 |
| ExpectationCriterion | 意外判定 | Surprise condition | 用来判断结果是否意外的一条可检验条件。揭晓后不能改。 |
| Admissible Space / specification space | 分析方案 | Analysis plans | 揭晓前拟纳入比较的估计设定。 |
| Freeze admissible space | 确认分析方案 | Confirm analysis plans | 先确认设定，再看比较，避免先看数字再改方案。 |
| Run specifications | 运行分析方案 | Run analysis plans | 按已确认的设定真实估计。 |
| Evidence Lab | 结果与证据 | Results & evidence | 看估计、比较、意外和建议的下一步检验。 |
| Surprise | 意外 | Surprise | 真实结果相对你写下的判定是符合、不符合，还是尚未判定。 |
| Unevaluated + `no_criteria` | 尚未判定：尚未设置可检验的预期。 | Not yet evaluated: no testable expectation is set. | 没有判据就不是「符合预期」。 |
| Unevaluated + unresolved metrics | 尚未判定：所需证据还没有产生 | Not yet evaluated: the required evidence has not been produced | 有判据，但要用的指标还没出现。 |
| Inconclusive | 部分判定：有的所需证据还没有产生 | Partial: some required evidence has not been produced | 部分可判定且没有违反，其余指标缺失。 |
| Expected / Unexpected | 与预期相符 / 与预期不符 | Expected / Unexpected | 已解析的判定全部满足，或任意一条被违反。 |
| Compare | 比较 | Compare | 看两条真实设定之间移动了什么。 |
| Next-best Challenge | 建议的下一步检验 | Suggested next check | 下一步最值得做的检验；接受后会真的跑。 |
| Supported | 当前证据支持 | Supported by current evidence | 在现有估计下可以使用的措辞。 |
| Conditionally supported | 有条件支持 | Conditionally supported | 只有在列出的假设下才能用的更强措辞。 |
| Unsupported | 当前证据不支持 | Not supported by current evidence | 现有证据不够支撑的过强说法。 |
| Teaching case / Card 1995 | 教学案例 Card 1995 | Teaching case Card 1995 | 公开的教育与工资复现案例。Card 1995 是专名。 |
| OLS | OLS | OLS | 本案例中：控制列出变量后，教育与对数工资的相关。 |
| IV | IV | IV | 本案例中：用大学邻近作工具变量的局部估计。强度诊断不能单独证明工具有效。 |
| Preview | 预览设定 | Preview specification | 试跑一条设定，当前主分析保持不变，直到你设为主分析。 |
| New study | 新研究 | New study | 离开当前会话，回到空桌开始另一项研究。不删除服务器上已有会话文件，只清本地会话句柄。 |

## 使用规则

- 同一条系统文案只出现一种界面语言。不要写 `Claim Ledger（结论账本）` 或 `New study · 回工作台`。
- 用户原文、变量名、公式、代码、来源标题、专名可以保持原语言。
- OLS / IV 保留缩写，旁边提供就地帮助，不是测验。
