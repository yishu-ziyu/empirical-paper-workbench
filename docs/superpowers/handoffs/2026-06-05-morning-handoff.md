# 2026-06-05 早 验收 Handoff

> 撰写时间: 2026-06-05 05:50 (用户起床前)
> 撰写人: 主控 (MiniMax-M3)
> Worktree: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/.claude/worktrees/brief-step-cards/`
> Branch: `brief-step-cards` (HEAD: `77ba2a8`, 16 commits ahead of main, **未 merge**)

---

## 一句话状态

**brief-step-cards Phase 1 实现完毕 + e2e 3/3 GREEN (mock LLM 模式)**. 16 commits, 29 文件, +2837/-4565 行. 真实 MiniMax streaming key 缺失, 真 LLM 模式被阻塞, **等你起床决策** streaming key 申请 or 降级到轮询.

---

## 验收 3 步走 (起床后约 5 分钟)

```bash
# 1. 进 worktree
cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/.claude/worktrees/brief-step-cards

# 2. 看 16 个 commits
git log --oneline -16

# 3. 跑 mock 模式 e2e (1.5s 跑完, 不用真 LLM)
PYTHONPATH=. python /tmp/uvicorn_with_mock.py &
cd Product/web-react && npm run dev -- --port 5173 &
sleep 8
cd Product/web-react
E2E_BASE_URL=http://127.0.0.1:5173/react/ npx playwright test e2e/brief-step-cards.spec.ts
# 预期: 1 passed (1.4s)

# 4. 浏览器手验 (前端 + 真 LLM 都看)
open http://127.0.0.1:5173/react/
# 走 brief tab → 输入"工业机器人对工资的影响" → 点"开始研究"
# 预期: 4 段 step card 流式播放 → 步骤 3 抵达时 3 按钮 → 选"继续" → 步骤 4 → final_brief
```

---

## 16 个 Commits (按时间顺序)

```
77ba2a8 chore(cleanup): remove demo_server.py, web-dist build artifacts, Tasks/ test runs  ← Subagent 4
c1da56a docs(handoff): append Subagent 3 e2e verification report  ← 主控
5052997 test(e2e): fix brief-step-cards spec for new vite /react/ base + tab-onComplete flow  ← Subagent 3
3da9237 fix(sse-proxy): backend CORS + frontend absolute URL (vite proxy can't pipe SSE)  ← 主控
701a36e refactor(api+wrapper): Phase A decoupling cleanup per audit 2026-06-05  ← Subagent 5
e9596fe fix(web): BriefPanel SSE endpoint path alignment (/api/brief → /api/brief/stream)  ← 主控
e3a5cd6 fix(prompts): restore v4.md academic-prose style  ← 主控
d16df12 feat(api): add /api/brief/stream + /api/brief/stream/resume SSE endpoints  ← Subagent 6
088e83b docs(handoff): append Subagent 2 final report  ← 主控
72e5484 feat(wrapper): restore brief_stream_service.py from pyc disassembly  ← Subagent 6
29540fe feat(llm_client): add chat_completion_stream as single LLM streaming entry point  ← Subagent 6
be873c6 fix(web): persist brief step snapshot across tab navigation  ← Subagent 2
2be69c2 fix(web): step_done always wins over awaiting (kill stale closure)  ← Subagent 2
8344134 fix(web): render step body via react-markdown + strip LLM template markers  ← Subagent 2
11c783e docs(handoff): update with skill inventory findings  ← 主控
eb1852b docs(handoff): brief-step-cards phase 1 + skill integration handoff  ← 主控
```

更早 (brief-step-cards branch 上已有):
- `00ac88b chore(web): add @playwright/test + @types/node`
- `1119a80 test(e2e): brief-step-cards happy path with await step 3 + continue`
- `ed8e7c1 fix(web): SSE parser flush, abort cleanup, double-click guard, type guards`
- `5370598 feat(web): BriefPanel rewrite — SSE consumption + step-cards`

---

## Subagent 7 个, 跑了什么

| # | Subagent | 任务 | 状态 |
|---|----------|------|------|
| 1 | prompt 重写 | 让 v4.md 范文质量 (作者+年份 引用, 不写 bullet, 散文风) | ✅ 完成 (e3a5cd6) |
| 2 | UX bug 修复 × 3 | (a) ReactMarkdown 渲染 (b) step_done 压 awaiting (c) snapshot 持久化 | ✅ 完成 (8344134/2be69c2/be873c6) |
| 3 | e2e 验证 | CORS + 绝对 URL fix 后跑 Playwright | ✅ 3/3 GREEN mock 模式 (5052997) |
| 4 | cleanup | 删 demo_server.py / web-dist / Tasks 临时, .gitignore | ✅ 完成 (77ba2a8) |
| 5 | 解耦审计 | Phase A 4 fixes + 路线图 + skill 集成目录建议 | ✅ 完成 (701a36e + handoff) |
| 6 | 恢复 Phase 1 后端 | brief_stream_service.py 从 .pyc 反编译 + chat_completion_stream + /api/brief/stream | ✅ 完成 (72e5484/29540fe/d16df12) |
| (主控) | SSE proxy 修复 | vite proxy 不能 pipe SSE → 改用 CORSMiddleware + VITE_API_BASE_URL | ✅ 完成 (3da9237) |

---

## Skill 集成计划 (下一阶段)

从 `2026-06-05-skill-inventory-report.md` 筛出 49 个 skills, Top 3 Phase 1 候选:

1. **chinese-de-aigc** (0.5d) — 范文级中文润色, v4 prompt 加 few-shot 后可用
2. **AI-research-feedback** (1d) — 把 brief 草稿喂进 academic reviewer, 找出"不够范文"的具体位置
3. **pyfixest** (2d) — design/execute tab 接 StatsPAI → pyfixest 落 IV-2SLS / DID 真实代码

**总工时 3.5d**. 不在本次合并 scope, 后续可独立派 3 个 subagent.

---

## ⚠️ 起床后必须决策的 3 件事

### 1. 真 LLM streaming key (硬阻塞)

**Subagent 3 验证**: 真实 MiniMax `sk-cp-08_...` key, `stream=False` 200 OK, `stream=True` 401.

**二选一**:
- (A) 申请新的 streaming 兼容 key (e.g. OpenAI / Anthropic 直连 / 其他 provider)
- (B) 降级前端到轮询 (后端 SSE → JSON 一次性, 前端 setInterval fetch)

**推荐 (A)**: 改 .env.local 一个变量即可, 不动业务代码.

### 2. 是否 merge brief-step-cards → main

- 16 commits 全部自洽
- 解耦审计 Phase A 4 fix 落地 (C1/C2/C3 关键 + 1 high)
- 3 个 UX bug 全修
- mock e2e 3/3 GREEN
- 1 个已知 bug (BriefPanel state restoration) 留 Phase 1 后续

**推荐: merge**. 早合早解锁后续 Phase 2 (skill 集成) + Phase 1 后续 (state restoration fix).

### 3. vite.config.ts 4 行 server config 要不要保留

Subagent 4 auto mode 下做了合理决定 (留). 这 4 行是:

```ts
server: {
  host: '127.0.0.1',
  port: 5173,
  strictPort: true,
},
```

**如果你不喜欢**: `git checkout HEAD~1 -- Product/web-react/vite.config.ts` 一行 revert.

---

## 文件交付清单 (供你快速找)

| 文件 | 用途 |
|------|------|
| `Product/web-react/src/components/BriefPanel.tsx` | 任务书 LLM 扩写面板 (主交互) |
| `Product/web-react/src/components/StepCard.tsx` | 4 步 step card 渲染 |
| `Product/api/brief_stream.py` | /api/brief/stream + /api/brief/stream/resume SSE 端点 |
| `Product/backend/wrapper/brief_stream_service.py` | 4 步流式服务 (从 .pyc 反编译恢复) |
| `Product/backend/llm_client.py` | chat_completion_stream 单一入口 |
| `Program/prompts/brief/v4.md` | 范文级 prompt (作者+年份引用, 散文风) |
| `Product/web-react/e2e/brief-step-cards.spec.ts` | Playwright e2e spec (3/3 GREEN) |
| `Product/web-react/.env.development` | VITE_API_BASE_URL=http://127.0.0.1:8765 |
| `Product/app.py` | CORSMiddleware 放行 5173 |
| `Product/api/_paths.py` | 共享 path 常量 (Phase A M2 fix) |
| `docs/superpowers/handoffs/2026-06-04-brief-step-cards-phase1-handoff.md` | 详细 handoff (15 节) |
| `docs/superpowers/handoffs/2026-06-05-decoupling-audit.md` | 解耦审计 + 修复路线图 |
| `docs/superpowers/handoffs/2026-06-05-skill-inventory-report.md` | 49 skills 清单 + Top 3 候选 |
| `docs/superpowers/handoffs/2026-06-05-morning-handoff.md` | **本文档** |

---

## 风险与未覆盖

1. **真 LLM 模式未 e2e 验证** (key 不支持 streaming). 决策前先用 mock 模式.
2. **BriefPanel state restoration bug**: 切到 search → view-saved-brief → 切回 brief, step 3 仍显示"等你决策". 原因: BriefPanel 重新挂载, `finalBrief` 没从 snapshot 还原. Subagent 3 注释里标了 out of scope, Phase 1 后续修.
3. **Phase A 之外的解耦问题** (Phase B/C): app.py 顶部 import 整理, _code_stubs/_stubs 提取, prompts 版本统一. 详见 `2026-06-05-decoupling-audit.md` §4. Phase C 必做 (chat_completion_stream 已经是 single entry point, 但 5 个 service 还没全统一调用).
4. **未跑后端 pytest** (e2e 跑通后没回头跑 unit). 风险: 5 个 service 改 chat_completion_stream 调用前要先确认测试不破.

---

**主控工作结束, 等你 3 个决策.**
