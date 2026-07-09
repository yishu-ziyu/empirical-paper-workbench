# CGSS read-only Gate Dashboard 设计说明

## 首屏 layout

1. 顶部：产品名、项目名、read-only 状态。
2. Overview：一句自然语言状态判断 + strongest allowed claim。
3. Entry Routing：显示 `mixed existing workspace`，并列出论文草稿 / PDF、变量字典、表、图、脚本、review report、复现文件。
4. Artifact Inventory：九个 artifact card 置顶为主视觉；`MethodGate` 默认展开，演示 evidence panel 展开态。
5. 右侧 rail：First Failing Gate、Blocked Claims、Replication Readiness、一个主 CTA。

## 组件层级

- `WorkspaceShell`
- `Topbar`
- `WorkspaceOverview`
- `EntryRouting`
- `StrongestAllowedClaim`
- `ArtifactInventory`
- `ArtifactCard`
- `EvidencePanel`
- `GateClaimRail`
- `FirstFailingGate`
- `BlockedClaimList`
- `ReplicationReadiness`
- `RecommendedNextAction`

## 状态视觉差异

- `claim-ready`：绿色 mono 标签，白色纸面卡片，表示可支撑 descriptive claim。
- `mismatch`：琥珀 mono 标签，说明材料存在但字段或结构不完全对齐，必须带 caveat。
- `blocked` / `clean_rerun_required`：红色 mono 标签，展开时有更明显 outline，表示当前不能支撑更强 claim。

## Evidence panel 展开态

Artifact card 使用原生 `details / summary`：点击整张卡展开内联 evidence panel。展开面板显示证据文件路径、关键字段、以及该 artifact 对 claim 的支持边界。默认展开 `MethodGate`，因为它是 first failing gate。

## 30 秒验收答案

- 数据：CGSS 2012、2013、2015、2017、2018、2021、2023 七期重复横截面。
- 样本：原始 79,014，完整主样本 64,808；样本量清楚，但逐变量 drop reason 未结构化。
- 变量：变量字典存在，幸福感和互联网使用跨年映射清楚；跨年测量等价性仍需 gate。
- 卡住的 gate：MethodGate。
- 最大 claim strength：`descriptive`。
- 下一步 artifact：补 MethodGate，先确认标准误聚类层级。
