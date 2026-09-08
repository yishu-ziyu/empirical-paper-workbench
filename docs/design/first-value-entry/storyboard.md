# 80 秒演示分镜

这是编辑预算，不是运行耗时承诺。演示成片尚未制作。本轮 HTML 支持按节审阅，未伪造视频播放器或现场运行进度。

| 时段 | 画面与操作 | 中文讲稿 | English narration | 依据 |
|---|---|---|---|---|
| 0–16 秒 | 从案例段开始，A/B 同屏；角标全程「历史运行回放」；停在 0.0747 / 0.1315 | 同一份 Card 教学数据，教育年限的两条估计分别为 0.0747 和 0.1315，结果变量是对数工资。先看它们的设定。 | On the same Card teaching dataset, two estimates for education are 0.0747 and 0.1315. The outcome is log wage. Let’s inspect their specifications. | card-pair.json 两 region_dummies run；不混用 full_controls |
| 16–34 秒 | 下移到改变 / 保持两列；依次强调 OLS→IV、nearc4、HC1→nonrobust；共同控制与 n 在旁 | IV 加入大学邻近作为工具；协方差口径也变了。数据和列出的控制保持相同，两条估计各有 3010 个观测。数字更大不代表更正确。 | IV uses college proximity as an instrument. Covariance changes too. The dataset and listed controls stay fixed, with 3,010 observations in each estimate. Larger does not mean more correct. | 两 run choices、formula、covariance、n；不虚构抽样一致性额外检验 |
| 34–51 秒 | 打开「数据与计算来源」，从 A/B 公式到 hash、run ID，再点去敏记录。长字段不要求观众读完 | 每条结果连着数据来源、计算公式和运行记录。这里能核对同一分析数据和对应设定。当前跨环境数值复现仍待核。 | Each result links to the data source, formula and run record. You can check the analysis dataset and specification here. Cross-environment numerical reproduction remains unverified. | 最小快照源指针 /calls/10/response；evidence.md |
| 51–67 秒 | 来源收起，边界框完整呈现；不播 mock 结果章 | 不能由此说教育对每个人都有相同因果影响。IV 解释依赖假设，强度诊断也不能单独证明工具有效。 | This does not establish the same causal effect for everyone. IV interpretation depends on assumptions. Instrument strength alone does not establish validity. | 能力清单「诊断与稳健性」「结论确认」及术语 OLS/IV |
| 67–80 秒 | 展示末尾能力边界和桌面入口；设计审阅时弹出交接说明，正式成片待实现后录现有空桌→「体验一项真实研究」 | 如果这适合你的研究，在桌面工作台选择体验一项真实研究。刚才看到的是历史回放；工作台中的运行会现场计算，时间与成功与否以实际状态为准。 | If this fits your study, choose “Try a real study” in the desktop workbench. This was a historical replay. Workbench runs execute live, with timing and success determined by their actual state. | DeskPage.onTryCard；当前设计稿没有接线，不伪造已进入 |

合计 16+18+17+16+13 = **80 秒**。中英文各录一版，不能同时堆字幕；允许按真实语速微调至 60–90 秒，但不省略复现状态、协方差差异、结论边界和历史标识。

预计算回放：已归档真实估计作为只读展示，所有切换只换视图，不触发研究。现场执行：只有进入工作台后用户主动「运行分析方案」才称现场，真实显示等待、失败、终态；失败时保留失败画面，不能剪接历史结果冒充成功。此次任务不新跑引擎、不承诺 80 秒跑完。正式视频制作与工作台接线须等设计确认。
