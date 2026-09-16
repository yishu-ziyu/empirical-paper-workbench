# 本地设计稿浏览器检查

2026-09-08，主 agent 实际操作 ego lite 独立 task 97。入口为本机 `docs/design/first-value-entry/index.html` 的 file URL，无 HTTP 服务、无公开部署、无业务 API 调用。这里只验设计审阅稿，不代表 GuidePage 已实施，不是实际研究引擎验收或真人理解验证。

## 通过

- `render-matrix.json`：zh-CN/en × 1440×900/390×844 × 01/02/03，共 12 个实际渲染状态；visibleSections 与选项一致，scrollWidth 均不超过 viewport width。
- 同名 `zh|en-01|02|03-desktop|mobile.png` 为分节首屏。`02-pair-mobile` 补两结果及设定；`02-sources-mobile` 补原生来源展开；`02-boundary-desktop|mobile` 与 `03-end-desktop|mobile` 补下半页结论边界和末尾入口。没有把整页压成一张长图。
- 主 agent 实际查看截图：首屏中英文、结果比较与设定、来源 hash/运行与两公式、两语言的结论边界、桌面与手机末尾入口；未见文字截断或内容横向溢出。屏幕下沿的后续内容可通过正常滚动到达。
- 真实操作主入口「看真实案例」→ 02；来源展开 → 显示同 pair 的数据标识、公式和 run；「当前范围」→ 03；末尾入口 → 只打开设计交接说明，明确拟回现有空桌、由用户主动选择 Card，不创建或替换研究会话。
- `interaction-checks.json`：中英来源 open=true，展开后无横向溢出；完整模式显示 1/2/3；桌面中选择 390 审阅画幅，实际 canvasWidth=390、canvasScrollWidth=390，桌面入口标签隐藏、手机交接标签显示；语言切换保留全部模式，实际 document.lang 更新；资源请求列表为空。
- 弹窗关闭按钮通过；原生 Escape 键通过。首次 ego `pressKey('ESC')` 调用未关闭弹窗（原输出保留）；使用原生 CDP Escape keyDown/keyUp 后 open=false，按钮关闭也 open=false，未修改应用来迎合测试。
- 最后 source/code 审阅：脚本仅在设计 DOM 内切显示状态；无 fetch/XHR/WebSocket/业务写入。相对链接目标在本目录，文件方式可查看。

## 本轮未执行

未重新运行 Card 或 PR #33 测试；未制作演示成片；未接通正式工作台；未测真人理解、移动端工作台、生产服务。最终视觉选择与真人理解仍由用户及未来获准的真人试用决定。

说明：全部 12 张首屏及边界/末尾截图在最终第 3 节文案和 label 修订后重采。来源/结果对的补充截图在该文案修订前采集，这些来源/数字/公式内容未在修订中改变。未将其作为旧版第 3 节证据。
