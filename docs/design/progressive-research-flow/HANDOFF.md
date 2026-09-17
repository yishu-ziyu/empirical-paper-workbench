# 给本地 Coding Agent 的交接提示词

把下面整段交给本地 Agent。它必须自己读取仓库事实，不要把这段话当作代码事实的替代品。

```text
你现在接手 econpaper 的“渐进研究流”设计融合工作。

仓库：yishu-ziyu/empirical-paper-workbench
分支：feat/progressive-research-flow
当前设计基线：docs/specs/frontend-interaction-current.md
当前审阅稿：docs/design/progressive-research-flow/index.html
旧视觉参考：docs/design/first-value-entry/index.html
真实历史结果来源：docs/design/first-value-entry/card-pair.json

第一原则：总是以事实为准，不要附和我。若我的口述、上一个 Agent 的总结、截图，与代码、git diff、运行结果或测试冲突，以可验证事实为准，并明确指出冲突。

先做这些，不要先改代码：
1. git fetch，并切到/更新 feat/progressive-research-flow。
2. 读 docs/specs/frontend-interaction-current.md。
3. 看该分支相对 main 的完整 diff。
4. 浏览器实际打开 docs/design/progressive-research-flow/index.html，从 01 到 08 走一遍。
5. 对照 docs/design/first-value-entry/index.html，确认哪些背景、颜色、字体、边界和气质是从旧稿继承的。
6. 核对 card-pair.json，确认页面里所有统计数字都来自现有历史记录；不要把历史结果说成本轮新运行。

当前已确认方向：
- 保留旧 first-value 设计的纸张/暖灰底色、墨色、低饱和绿色、Serif + Sans + Mono 的编辑型气质。
- 不保留旧稿的密集布局。
- 页面采用渐进披露：一个屏幕/状态只处理一个焦点。
- 顺序大致是：想法 → 一个追问 → 确认研究问题 → 数据进入 → 分析中 → 候选设计 → 第一条真实证据 → 必要的方法风险/来源下钻。
- 分析中默认只给一句真实状态 + 安静呼吸点；路径是次级信息，用户展开才看。没有真实事件就不要造百分比、倒计时或假步骤。
- 结果不要一次把所有卡片铺满。优先先给一条，再让用户主动展开第二条比较。
- 数字不要 count-up；来源/公式/trace/code 按需下钻。
- Agent 光标只在真的指向某个正在检查的对象时出现，不做常驻装饰。
- 账本是审计历史，不是第二套状态编辑器。

注意：当前分支的新增内容首先是“设计审阅稿 + 设计基线”，不是正式业务接线。不要把审阅稿直接当成生产实现，也不要为了让它看起来完整而伪造后端能力。

你的任务：
A. 先评价当前审阅稿与本地实际运行的视觉是否一致，尤其是用户喜欢的背景/纸张感。如果不一致，先定位真实 CSS/组件来源，用事实说明差异。
B. 在不破坏真实业务状态机的前提下，提出并实施下一步最小接线方案；优先复用现有 DeskPage / AgentSpikePage / AgentCursorLayer / motion primitives，而不是新造第二套系统。
C. 实际运行后再判断布局、动画和状态披露是否成立。不要只看静态代码。

做完后 commit + push 到同一分支，然后严格按下面格式回复给用户，让用户把整段转交给 ChatGPT：

HANDOFF TO CHATGPT
repo: yishu-ziyu/empirical-paper-workbench
branch: feat/progressive-research-flow
base_sha: <sha>
head_sha: <sha>

changed_files:
- ...

what_changed:
- ...

runtime_evidence:
- 实际打开/运行了什么：
- 实际观察到什么：
- 若有截图，给路径：

verification:
- command: ...
  result: PASS/FAIL + 关键原始结果

known_gaps_or_disagreements:
- ...

facts_vs_requests:
- 用户口述与代码/运行事实冲突处；没有写 none

commits_pushed:
- <sha> <message>
```
