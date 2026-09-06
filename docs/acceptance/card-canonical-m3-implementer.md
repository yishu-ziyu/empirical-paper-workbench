# M3 implementer summary — Card Canonical Research Experience

Date: 2026-09-06  
Branch: `review/workbench-v2`  
Hard bar: C17–C20 programmatic parts in `docs/acceptance/card-canonical-research-experience.md`

## Change

After Surprise Unexpected, the Agent rail offers `这个变化值得检查` + `Show me`. A labeled Agent cursor (not a system pointer) travels via `motion` transforms to semantic targets `evidence.spec.ols` → `evidence.spec.iv`, opens the existing Evidence Lab compare (Δ / identification intent), then points `evidence.choice.estimator` and fades unchanged choices. It stops; it does not auto-continue.

Experience form: `Show preview` points `evidence.choice.experience`, shows a Preview proposal only, waits for `Run Preview`, then calls the existing workspace `handleRunSpec(..., 'preview')` backend `spec_run`. Compare; small Δ shows `Little changed`. Canonical estimate is unchanged until the user promotes.

Agent scripts are data. No LLM. No x/y, CSS selector, or XPath as the control plane.

## Files changed

Frontend

- `frontend/src/lib/agentCursor/` — `SemanticTargetRegistry`, control-plane id parser, Card scripts, player primitives, context
- `frontend/src/components/AgentCursorLayer.tsx` — overlay on Workbench Shell (`motion` x/y, `pointer-events: none`)
- `frontend/src/components/EvidenceLab.tsx` — register semantic ids (incl. Method / Experience headers); consume compare/fade/preview from the cursor
- `frontend/src/components/AgentRail.tsx` — Show me / Run Preview / Cancel / Replay
- `frontend/src/App.tsx` — mount `AgentCursorRoot` on the shell; Run Preview → existing preview spec_run
- tests: `agentCursor.test.ts`, `AgentCursorLayer.test.tsx`

Not changed: backend spec_run math, Claim Ledger, Paper.

## Commands run

| Command | Result |
|---|---|
| `cd frontend && npm test` | pass — 340 passed (was 328; +12; no new skip) |
| `cd frontend && npx tsc --noEmit` | pass |
| `cd frontend && npm run lint` | pass (warnings only; no errors) |

C17: registry exists; `scripts.ts` only names semantic ids; helpers throw on `{x,y}` / `querySelector` / XPath. Overlay resolves rects after lookup; scripts never pass coordinates.

C18: `point` / Show-me script never call `runPreview` or `promote`.

C19: `runPreview` is a no-op until `agent-cursor-run-preview`; then `handleRunSpec(specId, 'preview')` — same preview path as M2 (does not write `state.estimate`).

C20 (program): `motion` travel; reduced-motion duration 0; missing target aborts without throw; resize/scroll re-resolve; pointer/keyboard yield; Cancel / Replay; overlay `pointer-events: none` with Agent label. Browser 1280/1440 still for the main agent.

## Scripts (data)

Show me (`card.show-me`): `evidence.spec.ols` → `evidence.spec.iv` → compare → `evidence.choice.estimator` → fade unchanged → stop.

Challenge experience (`card.challenge-experience`): `evidence.choice.experience` → preview `experience.linear-quadratic` → await confirm → `runPreview` → compare quadratic vs linear.

Preview spec id is resolved from admissible OLS linear definition (`ols_linear_exper` fallback). No new API.

## Visual

wb tokens, 2.5px diamond + “Agent” label + short intent. No glow, no GSAP, no OS cursor clone.
