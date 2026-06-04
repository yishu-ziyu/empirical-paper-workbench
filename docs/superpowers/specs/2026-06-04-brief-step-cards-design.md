# Brief Tab Step-Cards Design

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the brief tab's batch-mode "click → wait → dump" UX with a step-by-step research journal that streams the LLM's reasoning, with a light user checkpoint at the contribution-planning step.

**Architecture:** Convert `/api/brief` from POST-batch-JSON to POST-SSE. Single LLM call emits a structured prompt with `### STEP_N_DONE ###` markers. Backend parser walks the token stream, emits `step_start` / `step_delta` / `step_done` / `await_user` SSE events. At step 3 (contribution planning), backend holds. Frontend BriefPanel renders a vertical list of StepCards; at the key node, three buttons (continue / modify / reselect) drive the next SSE call.

**Tech Stack:** Python 3.12 + FastAPI (uvicorn) + sse-starlette; React 19 + TypeScript + Vite. SSE parsed in-browser with `fetch` + ReadableStream (same pattern ExecutionPanel uses).

---

## Scope

**In scope (Phase 1):**
- New SSE endpoint `/api/brief` (replaces the batch one, but old JSON shape is preserved for the brief downstream pipeline that writes to disk)
- New `Program/prompts/brief/v4.md` (4-step structured prompt)
- New `BriefPanel` rewrite in TypeScript with StepCard components
- 3 BDD unit tests + 1 e2e Playwright test
- DoD 8/9 → 9/9 once `Program/dod_pm_accepted.txt` is touched (out of scope for this spec)

**Out of scope (Phase 2+):**
- Other 4 tabs (search, variables, design, execution)
- Multi-round dialog inside a step
- Per-step regenerate without affecting later steps
- 6th tab identification-audit integration

---

## Design

### 1. SSE event protocol

Backend → Frontend, 6 event types (each is a `data: {...}\n\n` SSE line):

```ts
type BriefEvent =
  | { event: "step_start"; step_index: 1|2|3|4; title: string }
  | { event: "step_delta"; step_index: 1|2|3|4; text: string }  // incremental token chunk
  | { event: "step_done"; step_index: 1|2|3|4; summary: string } // summary = first sentence of live text, computed backend-side
  | { event: "await_user"; step_index: 3 }                       // pause
  | { event: "final_brief"; markdown: string; brief_path: string; verdict_passed: boolean }
  | { event: "heartbeat" }                                       // 15s keepalive, no data
  | { event: "done" }
  | { event: "error"; message: string };
```

Frontend → Backend, 2 actions sent as second POST after `await_user`:

```ts
// POST /api/brief/resume
type BriefResumeRequest = {
  topic: string;
  topic_slug?: string;
  action: "continue" | "modify" | "reselect";
  user_input?: string;  // required when action="modify"
};
```

### 2. Backend flow

```
POST /api/brief (initial)
  → load prompt v4, append topic
  → start LLM call (stream=True)
  → token-by-token:
      detect "### STEP_N_DONE ###" markers
      push step_start / step_delta / step_done events
  → on step 3 done:
      emit await_user
      STOP reading from LLM (close stream)
      return control to client

POST /api/brief/resume (when user acts)
  → action="continue": resume LLM with same context, no user_input
  → action="modify":  prepend user_input as high-priority constraint, re-prompt step 3
                      then continue to step 4
  → action="reselect": rerun the whole pipeline (start over)
  → push remaining events → final_brief → done
```

### 3. Step template (4 steps, fixed order)

| # | Title (LLM-fills) | Auto / Await | What LLM produces |
|---|---|---|---|
| 1 | 分析: {LLM} | auto | 1 sentence: 这是 X 类问题，用 Y 方法 |
| 2 | 文献: {LLM} | auto | 2-3 papers + 1 specific gap |
| 3 | 贡献: {LLM} | **await_user** | 3 bullets, each "数据 + 方法 + 看到什么" |
| 4 | 成文: {LLM} | auto | Full 4-paragraph brief markdown |

The "key node" is step 3 (contributions). This is where the user's domain knowledge adds the most value: they can correct misaligned contribution points before the LLM writes the final brief.

### 4. Prompt design (Program/prompts/brief/v4.md)

```markdown
你是实证经济学论文简报作者。把题目拆成 4 步来想，每步走完用 ### STEP_N_DONE ### 标记切分。

题目：{topic}

请按顺序思考：

### 步骤 1: 分析研究问题 ###
1-2 句话点出这是什么类型的研究问题（因果推断/描述性/政策评估），预期用什么方法。
### STEP_1_DONE ###

### 步骤 2: 映射文献缺口 ###
列出 2-3 个最相关的已有研究方向 + 1 个具体的文献缺口。
### STEP_2_DONE ###

### 步骤 3: 拟定贡献点 (关键) ###
列出 3 个贡献点 bullet，每个 bullet 一句话：用什么数据 + 什么方法 + 看到什么结果。
### STEP_3_DONE ###

### 步骤 4: 写出 4 段研究简报 ###
(若用户提供了修改约束，请融合进以下内容)

## 研究简报
**研究问题**: ...
**边际贡献**:
- 数据: ...
- 方法: ...
- 发现: ...

**研究边界**: ...
**成功标准**: ...
```

(For the modify branch, prepend `用户的额外约束: {user_input}\n请用这个约束重做步骤 3。\n### STEP_3_DONE ###\n` then continue with step 4.)

### 5. Frontend StepCard

```tsx
interface StepCardProps {
  stepIndex: 1|2|3|4;
  title: string;          // from step_start
  status: "pending" | "running" | "done" | "awaiting" | "error";
  liveText?: string;       // from step_delta (concatenated)
  summary?: string;        // from step_done
  // Only for step 3 when status="awaiting":
  onContinue?: () => void;
  onModify?: (userInput: string) => void;
  onReselect?: () => void;
}
```

Layout: vertical list, each card collapsed when status=pending (just title + spinner), expanded when running/done. Step 3 always shows the 3 buttons when status=awaiting.

### 6. State machine in BriefPanel

```
idle → (user clicks "生成") → loading
loading → step_start(1) → step1 running
step1 running → step_done(1) → step2 running
step2 running → step_done(2) → step3 running
step3 running → step_done(3) → step3 awaiting
step3 awaiting → (user clicks ✓) → step_start(4) → step4 running
step3 awaiting → (user clicks ✎) → modify mode → resume
step3 awaiting → (user clicks ✗) → reselect → loading
step4 running → final_brief → done
done → (onComplete callback fires)
```

### 7. Error handling

- LLM stream error: emit `error` event, BriefPanel shows error card with "重试" button (calls /api/brief again from step 1)
- Marker parse error: regex fallback — if a step is "stuck running" for >60s, mark it error and let user reselect
- User disconnects mid-await: state held server-side for 5 min, then GC'd

### 8. Testing

**Unit tests** (Python, `tests/api/test_brief_sse.py`):
1. 4-step happy path: brief topic → 4 step_done events → final_brief → done
2. Key node pause: step 3 done → await_user emitted → no further events
3. Continue action: resume with action="continue" → step 4 → final_brief
4. Modify action: resume with action="modify" + user_input → step 3 redone with constraint → step 4
5. Reselect action: resume with action="reselect" → pipeline restarts from step 1
6. Error handling: LLM returns malformed stream → error event emitted

**E2E test** (Playwright, `Product/web-react/e2e/brief-step-cards.spec.ts`):
- Open page → type topic → click generate
- Wait for step 1 + step 2 to mark done
- Verify step 3 card shows 3 buttons
- Click ✓ → wait for final_brief
- Verify brief markdown is displayed

**Manual smoke**:
- `curl -N -X POST http://127.0.0.1:8765/api/brief -H 'Content-Type: application/json' -d '{"topic": "工业机器人对工资的影响"}'`
- Stream visible in terminal
- Resume with action="continue" and verify final event

### 9. Migration / compat

- `/api/brief` keeps same POST shape but response is now SSE
- BriefService.run_brief() is still called internally and still writes to disk (Tasks/{slug}/brief.md)
- Final `brief_path` and `verdict_passed` arrive in the `final_brief` event
- Downstream code (variable panel, design panel) reads from disk path, unchanged
- **Deprecation:** old JSON batch response goes away in Phase 2 when other tabs also migrate

### 10. Out of scope / future

- Step-level "re-do this step only" (currently reselect restarts everything)
- Multi-round dialog inside a card
- Persisting step state across page refreshes
- Apply same pattern to other 4 tabs

---

## Risk + Mitigation

| Risk | Mitigation |
|---|---|
| LLM emits markers in unexpected places (e.g. inside a citation) | Use strict regex `### STEP_\d_DONE ###\s*`; treat only end-of-line matches as boundaries |
| Step 3 modify branch: LLM ignores user_input | v4 prompt puts user_input in a high-priority "system" position; test 4 verifies constraint appears in step 3 redo |
| SSE timeouts on slow networks | Heartbeat event every 15s with `event: "heartbeat"` |
| User clicks button 2x rapidly | Disable buttons on click; only re-enable on next SSE event |

---

## Estimated effort

- Backend: 1 new endpoint + 1 prompt + 1 SSE parser ≈ 4 hours
- Frontend: BriefPanel rewrite + StepCard component ≈ 3 hours
- Tests: 3 unit + 1 e2e ≈ 2 hours
- **Total: ~1.5 working days**

Phase 1 done = brief tab feels like "watching a researcher think". Phase 2 = same pattern to other 4 tabs.
