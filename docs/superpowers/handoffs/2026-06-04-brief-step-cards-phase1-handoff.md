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

### 3.1 UX 3 bug 修复 (Subagent 2 完成 ✅)

**3 个 commit** (提交顺序 = Bug 1 → Bug 2 → Bug 3):
- `8344134` fix(web): render step body via react-markdown + strip LLM template markers
- `2be69c2` fix(web): step_done always wins over awaiting (kill stale closure)
- `be873c6` fix(web): persist brief step snapshot across tab navigation

**实际修复方案**:
- Bug 1: `stripTemplateMarkers()` 用 `replace(/^###\s*步骤\s*\d+[^\n]*$/gm, "")` + `/^---$/gm` 清理, 然后喂给 `<ReactMarkdown remarkPlugins={[remarkGfm]}>`
- Bug 2: 根因是 `consumeSse = useCallback(..., [])` 冻结了 `applyEvent` 闭包。修复: `step_done` 改在 `setSteps((prev) => ...)` reducer 内捕获 `liveText`, status 强制 `"done"` 覆盖 awaiting
- Bug 3: App 新增 `briefSnapshot` state (与 `briefResult` 同级保留), BriefPanel 接 `initialSnapshot` prop → mount 时 hydrate

**新加 testid** (Subagent 3 可用):
- `view-saved-brief` — "查看已保存的简报" 按钮

**Bundle 体积警告**: `react-markdown@9` + `remark-gfm@4` + `micromark` 带来 ~50KB gzip, vite build warning chunk > 500KB。后续可 manualChunks 拆 `markdown-vendor`。

**Subagent 2 已知遗留** (Subagent 3/4 关注):
- e2e test 未加 "step 3 awaiting → done" 的 2s 断言 (Subagent 3 补)
- step 3 "修改" 后 summary 覆盖用户输入版本 (产品取舍, 暂不改)
- 刷新页面 `briefSnapshot` 丢 (无 localStorage 持久化, 后续可加)
- 严格模式 `priorStepsRef` 写两次同值, 无害

**Subagent 2 用的 worktree 操作**: `git reset --hard main` (从 194c677 拉回 00ac88b 取 BriefPanel/StepCard 实现) — worktree 内安全, 不影响 main。

### 3.2 e2e 测试 (Subagent 3 待派)
- [ ] 跑 `Product/web-react/e2e/brief-step-cards.spec.ts` against real backend
- [ ] 修复任何 flaky
- [ ] 至少 1 green run

### 3.3 合并 + 清理 (Subagent 4 待派)
- [ ] 删 `demo_server.py` (main + worktree)
- [ ] `web-dist/` 加 .gitignore
- [ ] merge `brief-step-cards` → main (用户验收通过后)

---

## 4. Skill 集成 (Task B, 已盘点)

### 4.1 盘点结果 ✅
- 源: `https://github.com/brycewang-stanford/Awesome-Agent-Skills-for-Empirical-Research`
- 本地: `/Users/mahaoxuan/Desktop/经济学论文/Awesome-Agent-Skills-for-Empirical-Research/skills/`
- 数量: **49 skills**
- 完整报告: `docs/superpowers/handoffs/2026-06-05-skill-inventory-report.md` (主路径, 307 行)

**仓库最有价值的 3 个 skill**:
1. **StatsPAI** (P=3.4) — execution/design 核心工具
2. **MixtapeTools Referee 2** (P=3.4) — identification-audit 协议
3. **chinese-de-aigc** (P=3.9) — 写作后处理 (中文学术降 AIGC)

**关键发现**:
- 大集合型 skill (07/17/24/26/33) 评分偏低 — 文档好但解耦差, **不推荐直接照搬**
- pyfixest 与 StatsPAI 功能重叠 — StatsPAI 优先, pyfixest 作 fallback / 交叉验证
- MixtapeTools "不修改作者代码" 原则与项目"重写优先"工作流冲突 — 需 wrapper 显式约束

### 4.2 Phase 1 集成 (锁定 3 个, 3.5 人天)

| 优先级 | Skill | 工作量 | 落地方式 | 路径 |
|:---:|---|:-:|---|---|
| P0 | **chinese-de-aigc** | 0.5d | 纯 prompt 模板 | `Program/prompts/writing_de_aigc/v1.md` |
| P1 | **AI-research-feedback** | 1d | 6-agent prompt | `Program/prompts/audit_claesbackman/v1.md` |
| P2 | **pyfixest** | 2d | 新 wrapper service | `Program/api/execution_pyfixest.py` |

### 4.3 Phase 2 (06-13 ~ 07-12, 6.5 人天)
- StatsPAI (3d) + causal-inference-mixtape (1.5d) + stata-accounting-research (1d) + claude-skills Song (1d)

### 4.4 Phase 3 (07-13+, 9 人天)
- MixtapeTools Referee 2 + stata-skill + marginaleffects + research-companion + awesome-econ-ai-stuff

### 4.5 解耦集成架构 (锁死)
```
Program/
├── integrations/                  # 新增根目录
│   ├── stats_pai/                 # Phase 2
│   ├── pyfixest/                  # Phase 1
│   ├── referee2/                  # Phase 3
│   └── ...
├── prompts/                       # 现有 + 新增
│   ├── writing_de_aigc/v1.md      # Phase 1 (chinese-de-aigc)
│   ├── audit_claesbackman/v1.md   # Phase 1 (AI-research-feedback)
│   ├── ...
├── knowledge/                     # 新增 (静态知识)
│   ├── mixtape/
│   ├── jar_patterns/
│   └── ...
└── llm/chat_completion_stream.py  # 单一 LLM 入口
```

**8 铁律** (来自 inventory 报告第 4.2 节):
1. 每个 skill 一个独立目录
2. wrapper 暴露纯 Pydantic model, 不向上层泄露 prompt 字符串
3. LLM 调用统一过 `Program/llm/chat_completion_stream.py`
4. 严禁跨 integration 互相 import
5. 集成层不写业务逻辑
6. 每个 integration 必须有 `tests/test_smoke.py`
7. 所有 prompt 模板按版本号管理 (v{N}.md)
8. LLM 字符串禁止外泄到上层 (Pydantic model 输出是结构化数据)

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
