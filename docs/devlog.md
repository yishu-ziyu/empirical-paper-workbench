# 开发日志（DEVLOG）

> 记录产品每一步真实进展。规则：一条一个日期，写了什么、为什么、验收数字、
> 还欠什么。决策性内容不在这里展开，指向 docs/adr/ 对应条目。

## 2026-08-27 —— 北极星落地日：从"陪聊半成品"到"替你干完 + 每一步可查"

今日基调：确立产品北极星——**替你干完 + 每一步可查**（功能取舍判据：
不同时推进这两条的，砍）。参照系：Apodex（Self-Evolving Heavy-Duty Solver）
的产品架构与开源件。全天五刀 + 一条真接口实弹验证，全部先红测试后实现。

### 1. `b2c6579` 修地基 + 审批硬证据门

- **backend 14 个失败清零**（此前挂的全是用户面）：
  - 根因一：passlib(2020 停维护) × bcrypt 5.x 不兼容，连合法密码都炸。
    弃用 passlib，auth.py 直连 bcrypt，72 字节截断与旧 $2b$ 哈希互通。
  - 根因二：WS 流式测试停留在三个月前的流程假设（upload 跑全图），
    现按真实路径走：上传 → 设方向（HITL 暂停）→ 预写 → 开流。
- **废除"必放行"**：approve-chapter 端点对未过审章节返回
  409 `{review_gate, score, threshold, needs_force}`；唯一旁路是显式
  `force:true` 且章节永久带 `approved_forced` 标记。

### 2. `e66429f` run 目录工件化

"可查"从 state 字段升格为磁盘事实。每个会话：

```
runs/<session_id>/manifest.json    trace.jsonl   checkpoints/(+latest.json)
                    workspace/     outputs/export/
```

- facade 全节点追踪（上传管线/预写/生成/再生成/评审/回滚/导出），
  事件含毫秒耗时与关键 detail（评审分数、接地失败、降级原因、blockers）
- 清洗 sidecar、clean.py/do、tex/pdf/docx 全部落 workspace，不再散落 /tmp
- 人工动作也是事件：审批 ok|forced、评审决策 accept|reject|force_pass，
  绕过必留 `reviewer_bypassed_review: true`
- fail-open：工件写入失败永不阻断主流程；删会话连目录一起删
- 只读端点：GET /sessions/{id}/artifacts、/trace

### 3. `ac6d2df` 把门亮到界面上（首次执行前端质量协议）

- 先取 shadcn/ui AlertDialog 与 Badge 参考实现的交互契约
  （role=alertdialog、aria、遮罩、安全 vs 破坏性动作分离、pill 变体），
  用项目 Editorial Academic Refined 令牌定制，零新增依赖
- ReviewGateDialog：409 不再是裸报错——显示分数/阈值/评审意见，
  两出口：打回重写（走 regenerate）、强行放行（两步确认）
- ApprovalBadge：绕过核对的章节挂危险徽标，全程可见
- RunTracePanel：右栏接入最近 20 条运行事件
- 顺手清 3 笔历史 TS 债，`tsc -b` 归零；修复批准按钮空回调问题

### 4. `7444511` 综述引用回溯硬规则（ADR-0011 上半）

结构层新增两条拦截（分数上限 0.65）：

- `citation_year_mismatch`：[N] 邻近的作者-年份必须与编号指向条目一致，
  张冠李戴视为编造——此前完全放行
- 编号表非空时，含作者-年份叙述的句子必须带合法 [N]，无从核对的主张
  按 invented_citation 处理

### 5. `8d23d03` Apodex 深搜旁路实弹接通（ADR-0011 下半）

用户申请到两周免费 API key 后实弹联调，暴露三种形态，逐一红转绿：

| 形态 | 解法 |
|---|---|
| 默认 SSE 流（text/event-stream） | 显式 stream:false + 强推时拼装 delta.content |
| 深研模型无视 JSON-only 指令（实测返回 15 万字符中文综述，自调 web_search×4） | 递归收集所有 content 字符串逐段扫描 |
| 连排 JSON + 空 choices:[] 噪声 | Extra-data 安全的对象遍历 + 空数组不算命中 + 文献形状识别 |

**实弹验收**：查询"最低工资 就业 中国 双重差分"，从真实响应解析出
20 条真实中国 DID 文献。启用方式：`LITERATURE_SOURCE=apodex` +
`APODEX_API_KEY`（默认 base=https://api.apodex.ai/v1、模型
apodex-1-0-deep-research）。免费窗口过期按 ADR-0011 整体拆除。
已拒绝方案：MiniMax 兼管文献事实层（生成/证据须分权），详见 ADR。

### 验收数字（当日收盘）

| 层 | 结果 |
|---|---|
| agent | 543 passed |
| backend | 188 passed, 7 skipped(环境性) |
| frontend | vitest 204 passed / tsc -b 0 errors / oxlint 0 errors |

### 已知欠账（下次优先级）

1. apodex 条目缺 year/doi 元数据 → 接 Crossref DOI 反查补齐，让
  citation_year_mismatch 门对其生效
2. 20 条条目的 relevance_score 当前恒为 1.0，未利用模型排序信号
3. 免费窗口结束：ADR-0011 到期拆除动作（模块+测试+本日志标注）

---

*维护约定：新条目插在最新日期条目之上，倒序排列；只写事实与数字，判断走 ADR。*
