# Localized first study — implementer report

Date: 2026-09-07  
Branch: `review/localized-first-study`  
HEAD (uncommitted work on): `87c5e5b726911130d4490efd10194ed4241817a5`  
Contract: `docs/acceptance/localized-first-study.md` (Status left **open**)

## Change

中文界面和英文界面各自用一种系统语言走完 Card 研究路径。空桌主入口是「体验一项真实研究」/ “Explore a real study”。语言切换只改展示。任务旁有可关闭的帮助。能力盘点诚实，不宣称全部能力可上线。

## Not this

不 merge、不 push、不改 `main`、不碰 issue #30、不实现 DiD/新 Agent、不改 Card 系数、不做阶段 C 宣发重设计、不造文稿语言开关。

## Files

| File | Why |
|---|---|
| `docs/product/capability-inventory.md` | C1 |
| `docs/product/terminology.md` | C2 |
| `frontend/src/lib/i18n.tsx` / `i18nWorkbench.ts` | 词条、html lang、插值 |
| `frontend/index.html` | 默认 `lang="zh-CN"` |
| `frontend/src/components/TaskHelp.tsx` | 任务旁帮助 |
| Desk / App / ResearchLabPanels / EvidenceLab / AgentRail / 导出对话框等 | 核心路径单一语言 |
| `frontend/src/__tests__/cardCanonicalLiterals.test.ts` | 双语资源存在且默认不堆叠 |
| `frontend/src/__tests__/languageSwitchDisplayOnly.test.tsx` | C4 |
| `docs/acceptance/assets/localized-first-study/` | C6 截图 |
| `frontend/vite.config.ts` | 隔离后端 URL |

## Commands run (copied output)

### make test

```text
[check-api-drift] ✅ openapi.json 与后端代码同步
[check-api-drift] ✅ docs/api/openapi.json 与后端代码同步
[check-api-drift] ✅ types/api.ts 与 openapi.json 同步
819 passed, 1 skipped, 4 warnings in 60.63s
451 passed, 8 skipped, 32 warnings in 151.88s
 Test Files  56 passed (56)
      Tests  403 passed (403)
[test] agent + backend + frontend 全部通过
```

无新增 skip（agent 1 skipped、backend 8 skipped 为既有）。

### frontend tsc / lint / build

```text
npx tsc --noEmit   # 0
npm run lint       # 0 errors；既有 only-export-components warnings
npm run build
✓ built in 1.70s
```

### make check-api-drift

```text
[check-api-drift] ✅ openapi.json 与后端代码同步
[check-api-drift] ✅ docs/api/openapi.json 与后端代码同步
[check-api-drift] ✅ types/api.ts 与 openapi.json 同步
```

### Browser (isolated)

Ports **5174 / 8001**（用户 5173/8000 占用，未连接、未杀日常进程）。  
ego-browser `useOrCreateTaskSpace('localized-first-study')` id **91**.

Card Surprise（浏览器）：

```text
Unexpected
IV estimate 0.1315 > OLS estimate 0.0747
```

空判据：

```text
Unevaluated
尚未判定：尚未设置可检验的预期。
```

缺指标：

```text
Unevaluated
尚未判定：所需证据还没有产生
```

## Proofs

- 空桌 zh/en：`zh-empty-desk-1280.png` / `en-empty-desk-1280.png` 等。
- 路径：question / plans / run / evidence / claims / paper / jump-evidence，zh 与 en。
- 语言切换测试：无 PUT `/research/expectation`；揭晓后判据标签仍为 `IV estimate < OLS estimate`。
- 帮助：`TaskHelp.test.tsx`；`zh-help-confirm-plans-1280.png`。

失败/重试：vitest M2 失败卡 + `spec.retry` / `workbench.retryCard` 中英词条。隔离 runner 停掉后 boot 保持 pending，未形成 boot-failure 截图。

## Git status (at report)

Uncommitted on `review/localized-first-study`. Not pushed. Not merged. HEAD still based on `87c5e5b`.
