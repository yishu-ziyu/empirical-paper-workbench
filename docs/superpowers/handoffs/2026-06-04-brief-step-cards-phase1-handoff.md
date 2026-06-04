# Brief Step-Cards Phase 1 + Skill 集成 - Handoff

**Date**: 2026-06-05 早
**Author**: 主控
**Status**: Phase 1 后端 ✅ / 前端修复中 / Skill 盘点中 / 解耦审计中
**Branch**: `brief-step-cards` (worktree: `.claude/worktrees/brief-step-cards/`)

---

## 1. 任务背景

用户 2026-06-04 18:00 给的两个并行任务：
- (A) brief tab 改 SSE 流式 4-step step-cards，**范文质量**输出，不要 LLM-default 罗列
- (B) 集成 `brycewang-stanford/Awesome-Agent-Skills-for-Empirical-Research` 49 个 skill，**后端高度解耦**
- 验收：2026-06-05 早上

---

## 2. 已完成 (Phase 1 后端)

### 2.1 后端 SSE 流式 ✅
| 文件 | 状态 | 说明 |
|------|------|------|
| `Program/prompts/brief/v4.md` | ✅ commit 194c677 | 4-step SSE-friendly prompt + 学术散文硬约束 |
| `Program/prompts/brief/v4.py` | ✅ | loader |
| `Product/backend/wrapper/brief_stream_service.py` | ✅ 9.1K | run_brief_stream + resume_brief_stream + heartbeat |
| `Product/backend/llm_client.py` | ✅ | chat_completion_stream 单一 LLM 入口 (Anthropic + OpenAI) |
| `Product/types/research.py` | ✅ | BriefEvent + BriefResumeRequest Pydantic 模型 |
| `Product/api/brief.py` | ✅ | GET /api/brief (SSE) + POST /api/brief/resume |
| `tests/wrapper/test_brief_stream_service.py` | ✅ | 3 BDD tests |
| `tests/wrapper/test_brief_prompt_v4.py` | ✅ | 1 unit test |
| `tests/wrapper/test_llm_client_stream.py` | ✅ | 1 unit test |

**事件序列**:
1. `step_start` (i=1..4, title=步骤 N) → 累积 step 1..3 文本
2. `step_delta` (text chunk) → 实时打字效果
3. `step_done` (summary) → step status 转为 done
4. `await_user` (仅 step 3 后) → 前端展示 3 按钮
5. 用户点击 → POST /api/brief/resume
6. `final_brief` (markdown) → 落盘 + state.briefResult
7. `heartbeat` (15s) → 防止 proxy timeout
8. `done` / `error`

### 2.2 前端组件 ✅
| 文件 | 状态 | 说明 |
|------|------|------|
| `Product/web-react/src/components/BriefPanel.tsx` | ✅ 357 行 | SSE 消费 + 状态机 |
| `Product/web-react/src/components/StepCard.tsx` | ✅ 172 行 | 单步卡片 |
| `Product/web-react/src/App.tsx` | ✅ | briefResult state 跨 tab 保留 |
| `Product/web-react/e2e/brief-step-cards.spec.ts` | ✅ 80 行 | Playwright e2e (未跑) |

**SSE 消费**: native `fetch` + `ReadableStream` + `AbortController`
**状态机**:
- 整体 phase: `idle` / `running` / `awaiting` / `completed` / `error`
- 单步 status: `pending` / `running` / `done` / `awaiting` / `error`

### 2.3 真实 LLM 验证 ✅
- 杀掉硬编码 mock demo_server.py
- 用 `.env.local` 加载 MINIMAX_API_KEY (`set -a; source .env.local; set +a`)
- uvicorn 跑 Product/app.py 端口 8765
- 浏览器跑通 "父母教育水平影响儿女收入水平吗" 真实生成
- LLM 输出包含真实引用: Becker & Tomes (1979/1986), Solon (1999), Hertz (2007) 等

### 2.4 4 段简报落盘 ✅
- 路径: `Tasks/untitled/brief.md`
- 4 段: 研究问题 / 边际贡献 / 研究边界 / 成功标准
- 完成自动跳到 search tab

### 2.5 v4 prompt 范文级质量 ✅
- 强约束: "避免 bullet 罗列、短句堆叠、口语化连接"
- 引用规范: "作者1和作者2(年份)"
- 句首数字: 汉字
- 散文段 (3 段) 替代 bullet 列表
- 3 个贡献点用"第一/第二/第三"散文嵌入
- 研究边界用"本文不考察...而是聚焦..."结构
- 成功标准带 Partial R²≥0.05 / AR p<0.05 阈值

---

## 3. 待完成 (Phase 1 前端收尾)

### 3.1 UX 3 bug 修复 (Subagent 2 运行中)
- [ ] **Bug 1**: Steps 1-3 body 显示原始 markdown (### 步骤 N, ---, 截断)
  - 修法: ReactMarkdown 渲染 + strip 模板标记
  - 依赖: `react-markdown` + `remark-gfm` (新加 package.json)
- [ ] **Bug 2**: Step 3 status 卡在 "awaiting"，点 继续 后 step_done 没正确转 "done"
  - 修法: applyEvent step_done 分支无条件覆盖 status
- [ ] **Bug 3**: 切回 brief tab 看到 reset 状态
  - 修法: App.tsx 新加 `briefSteps` state + BriefPanel mount 时 hydrate
  - 新 UI: "查看已保存的简报" 按钮

### 3.2 e2e 测试 (Subagent 3 待派)
- [ ] 跑 `Product/web-react/e2e/brief-step-cards.spec.ts` against real backend
- [ ] 修复任何 flaky
- [ ] 至少 1 green run

### 3.3 合并 + 清理 (Subagent 4 待派)
- [ ] 删 `demo_server.py` (main + worktree)
- [ ] `web-dist/` 加 .gitignore
- [ ] merge `brief-step-cards` → main (用户验收通过后)

---

## 4. Skill 集成 (Task B, 进行中)

### 4.1 盘点 (Skill inventory subagent 运行中)
- 源: `https://github.com/brycewang-stanford/Awesome-Agent-Skills-for-Empirical-Research`
- 本地: `/Users/mahaoxuan/Desktop/经济学论文/Awesome-Agent-Skills-for-Empirical-Research/skills/`
- 数量: 49 skills
- 报告输出: `docs/superpowers/handoffs/2026-06-05-skill-inventory-report.md` (待生成)

### 4.2 暂定 5-tab OS 映射 (待 inventory 验证)
| 5-tab stage | 候选 skill | 来源 |
|------------|-----------|------|
| brief | chinese-de-aigc (48) | 降 AIGC skill |
| brief | claude-scholar (33) | 学术写作 |
| search | paper-search-mcp, arxiv-mcp | 学术搜索 |
| variables | (待盘点) | 数据集 schema mapping |
| design | StatsPAI (00), pyfixest (40), marginaleffects (39) | 因果推断工具 |
| execution | Stata skill (32) | Stata 执行 |
| identification-audit | causal-inference-mixtape (10), MixtapeTools (13) | 识别策略审计 |

### 4.3 Phase 1 集成 (本周可做 3 个)
- 候选优先级: 0.5×相关性 + 0.3×质量 - 0.2×难度
- 解耦集成架构: `Program/integrations/{skill_name}/`
  - `wrapper.py`: 暴露 Pydantic interface
  - `prompts/v1.md`: 适配本项目 prompt 格式
  - `tests/`: 单测 + 集成测试
- 严禁: 跨 integration 互相 import；绕过 chat_completion_stream

---

## 5. 后端解耦原则 (用户要求)

### 5.1 解耦审计 (Subagent 5 运行中)
- 报告输出: `docs/superpowers/handoffs/2026-06-05-decoupling-audit.md` (待生成)
- 重点审查: `Product/backend/wrapper/` 6 个 service 之间是否有跨 tab import
- 重点审查: `Product/types/research.py` 是否被多个 service 共享修改

### 5.2 铁律 (Phase 1 skill 集成前必做)
1. **每个 tab = 1 个 wrapper service + 1 个 api router**
2. **跨 tab 严禁 import**: brief_service 只能用 Pydantic 数据交换，不直接 import search_service
3. **SSE 端点纯文本**: 前端不依赖后端内部 state
4. **LLM 单一入口**: 所有调用走 `chat_completion_stream(messages, provider_id, model)`
5. **Pydantic 边界**: 跨 tab 数据流必须经过 `Product/types/research.py` 序列化/反序列化

### 5.3 Phase 1 skill 集成的目录结构
```
Program/
├── integrations/                  # 新增 (Phase 1 skill 落地)
│   ├── stats_pai/                 # 假设集成 StatsPAI
│   │   ├── wrapper.py             # Pydantic interface
│   │   ├── prompts/
│   │   │   └── v1.md
│   │   └── tests/
│   ├── py_econometrics/           # pyfixest + marginaleffects
│   └── ...
├── prompts/                       # 现有
│   ├── brief/
│   ├── search/
│   ├── variables/
│   ├── design/
│   └── execution/
└── ...

Product/
├── api/                           # 现有
│   ├── brief.py
│   ├── search.py
│   ├── variables.py
│   ├── design.py
│   └── execute.py
├── backend/
│   ├── wrapper/                   # 现有 5 个 service
│   │   ├── brief_service.py
│   │   ├── brief_stream_service.py
│   │   ├── search_service.py
│   │   ├── variables_service.py
│   │   ├── design_service.py
│   │   └── execute_service.py
│   ├── integrations/              # 新增 (skill 集成 wrapper)
│   │   ├── stats_pai_service.py
│   │   └── ...
│   └── llm_client.py              # 唯一 LLM 入口
└── types/
    └── research.py                # 共享 Pydantic models
```

---

## 6. 任务清单 (用户可见)

| ID | Subject | Status | Owner |
|----|---------|--------|-------|
| #30 | Subagent 1: v4 prompt 范文级 | ✅ completed | Subagent 1 |
| #32 | Subagent 2: UX 3 bug 修复 | 🔄 in_progress | Subagent 2 (后台) |
| #31 | Subagent 3: e2e 测试跑通 | ⏸ pending | Subagent 3 (待派) |
| #33 | Subagent 4: 合并 + 清理 | ⏸ pending | Subagent 4 (待派) |
| #36 | Subagent 5: 后端解耦审计 | 🔄 in_progress | Subagent 5 (后台) |
| (新) | Skill inventory | 🔄 in_progress | Skill subagent (后台) |
| #34 | 写 handoff 文档 | 🔄 in_progress | 主控 (本文档) |
| #35 | Phase 1 集成 Top 3 skills | ⏸ pending | 待 inventory 完成后派 |

---

## 7. 验收清单 (用户早上做)

### 7.1 Brief tab 端到端
1. 打开 http://localhost:8765 (后端 uvicorn 必须先起)
2. 默认进入 brief tab
3. 输入研究问题, e.g. "高铁开通对县域产业结构升级的影响"
4. 点 "开始研究"
5. 4 张 step card 应**流式**显示 LLM 生成 (不是一次性渲染)
6. 步骤 1 完成 → 步骤 2 开始 → 步骤 3 显示 3 按钮 (继续 / 修改 / 重选)
7. 点 "继续" → 步骤 4 生成 → 4 段简报落盘 → 跳 search tab
8. 切回 brief tab → **应**显示已保存的简报，不是 reset

### 7.2 范文质量检查
- 4 段每段都是连贯**散文** (不是 bullet)
- 引用格式: "Becker和Tomes(1979)" / "Solon等(1999)"
- 数字用法: 句首汉字 (一、二、三), 统计量保留 2 位小数
- 边际贡献 3 段递进: 数据 → 方法 → 发现
- 研究边界: "本文不考察...而是聚焦..." 结构

### 7.3 后端解耦抽查
```bash
# 应该零结果 (除 brief_stream import brief 类型外)
grep -r "from Product.backend.wrapper.search_service" Product/backend/wrapper/brief_stream_service.py
grep -r "from Product.backend.wrapper.design_service" Product/backend/wrapper/search_service.py
# 等等
```

### 7.4 LLM 单一入口
```bash
# 应该只有 llm_client.py 调用 anthropic/openai URL
grep -r "api.minimaxi.com\|api.openai.com" Product/ Program/
```

---

## 8. 已知风险

1. **真实 LLM 速度**: 4 段每段可能 30s-60s，需要耐心等
2. **MINIMAX_API_KEY**: 必须从 .env.local 加载 (用户已在 .env.local 配过, 不要硬编码)
3. **web-dist/**: 是 build 产物，应加 .gitignore (Subagent 4 处理)
4. **demo_server.py**: 是 mock 测试服务器，应删 (Subagent 4 处理)
5. **Tasks/test-topic/ 和 Tasks/untitled/**: 临时跑出来的 artifacts，Subagent 4 决定是否保留 .gitkeep

---

## 9. 中断信号 (用户验收不通过时的应急)

如果用户对结果不满意：
1. **不要急着改代码**，先看 v4.md 是不是真的范文级
2. 让用户指出具体哪段不像范文
3. 把范文 (`/Users/mahaoxuan/Desktop/论文核心素材库/_tmp_text_extract/范文-数字经济赋能城市经济韧性.txt`) 喂回 v4 prompt 作 few-shot example
4. 重跑一遍验证

如果用户对解耦不满意：
1. 看 Subagent 5 报告，列出违规
2. 按 critical → high → medium 顺序修
3. 每个修复单独 commit

---

## 10. 后续展望 (Phase 2+)

- **Phase 2 skill 集成**: 4 个 skill 落地 (06-13 ~ 07-12)
- **identification-audit tab**: Bartik IV / 平行趋势检验 / 弱 IV 诊断的 GUI
- **多任务并发**: 5-tab 流水 (brief → search → variables → design → execution)
- **可复现 artifact bundle**: PDF + 代码 + 数据 + .env 模板

---

**下一步 (主控继续)**:
1. 等 Subagent 2 / 5 / Skill inventory 三个后台任务完成
2. 收到后验收 + 派 Subagent 3 (e2e)
3. e2e green 后派 Subagent 4 (merge + cleanup)
4. 所有 commit 合并后通知用户验收
