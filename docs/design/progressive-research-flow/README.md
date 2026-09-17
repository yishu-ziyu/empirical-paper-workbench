# 渐进研究流审阅稿

入口：`docs/design/progressive-research-flow/index.html`

用途：验证 2026-09-17 当前接受的交互方向——**保留旧 first-value 设计的纸张/墨色/绿色视觉底色，但用更稀疏的一屏一焦点布局，把研究过程逐步披露出来。**

本文件夹不是正式业务页面，不调用 API，不创建会话，也不声称重新运行 Card 数据。

## 数据事实

审阅稿里出现的 Card 结果全部来自仓库现有：

`docs/design/first-value-entry/card-pair.json`

- OLS `ols_region_dummies`: coef `0.07469325559311334`, SE `0.0034983456584787432`, HC1, n=3010
- IV `iv_region_dummies`: coef `0.13150383625543327`, SE `0.05496367260228859`, nonrobust, n=3010
- effective F `14.138670079757798`
- first-stage F `13.255785330576094`
- reproduction status: `复现待核 / Reproduction pending verification`

因此页面只写“历史运行数据”，不把它包装成这次新算出的结果。

## 怎么审阅

直接浏览器打开 `index.html`。顶部审阅条可以前后切换 8 个状态；也可以在页面内顺着动作走。

建议重点检查：

1. 首屏是否足够克制。
2. Agent 追问是否一次只有一个真正的决定。
3. 分析状态是否“可理解但不假装有精确进度”。
4. 是否先显示一条结果，再主动披露第二条比较。
5. 来源/公式是否保持按需下钻。
6. 纸张背景、墨色、绿色、分隔线是否与 `../first-value-entry/` 同源。

当前设计基线与 Agent 交接协议见：

`docs/specs/frontend-interaction-current.md`

## 与真实产品核对 + 本轮接线

`WIRING.md`：审阅稿与真实运行中的产品逐项核对（token、字体、布局密度、哪些按钮无逻辑、
哪些步骤是定时器而不是事件），以及本轮把「分析中」的路径披露接到**真实 `run.progress` 事件**
上的最小接线与真实运行证据。

运行实拍（`shots/`）：
- `live-desk-entry.png` 真实产品空桌（纸张/米白 + Instrument Serif）
- `live-run-progress-open.png` 真实 run 进行中，披露区展开显示后端真实事件
- `draft-01-idea.png` 审阅稿第 01 状态
- `old-first-value-hero.png` 旧稿 first-value-entry 首屏（对照密度）

## 外部评审

给云端模型的独立评审问题与本次改动汇总：`docs/reviews/20260917-progressive-flow-review-brief.md`。
它带上 `cd45d65..60feb83` 的交接块、我实测过的验证命令与结果、以及 9 个待答复的问题。
