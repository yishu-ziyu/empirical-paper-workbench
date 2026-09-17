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
