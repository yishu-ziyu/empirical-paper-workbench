# L9 Cross-Lane Review — 2026-06-04

> **Scope:** Review work from L1–L8 (the 5-tab product, prompt tuning, spec runner, DoD).
> **Reviewer:** Claude (auto mode) for the user.

## Verdict

All 5 lanes (brief / search / variables / design / execution) plus the L7 prompt tuning
and L8 spec_runner / DoD work **integrate correctly**. 120/120 wrapper/api/types/program
tests pass, DoD report is **8 PASS / 0 FAIL / 1 MANUAL** (PM browser-acceptance remains a
manual gate by design).

Live M3 smoke test: HTTP 200, ~75 input / 130 output tokens, substantive Chinese reply.

## What was verified

| Lane | What | Status |
|---|---|---|
| M3 model path | All 5 wrappers route to `provider_id="minimax"` (AST check) | ✅ |
| Live M3 end-to-end | `chat_completion(...)` → real M3 reply, 200 OK | ✅ |
| DoD #2 e2e spec | `Product/web-react/e2e/end-to-end.spec.ts` exists | ✅ |
| DoD #3 failure modes | 5 endpoints have try/except + HTTPException | ✅ |
| DoD #6 prompt versions | brief=2, search=2, variables=3, design=3, **execution=4** | ✅ |
| DoD #9 M3 path | 5/5 wrappers use `provider_id="minimax"` | ✅ |
| v4 loader chain | execute_service picks v4 for intro/results/robust/strategy, falls back per-section | ✅ |
| 6th tab identification-audit hooks | v4 prompts contain "identification" + "evidence_id" refs | ✅ |
| 9 BDD cases for spec_runner | 9/9 cases pass (mocked HTTP) | ✅ |
| 9 BDD cases for DoD | 9/9 cases pass | ✅ |

## Cross-lane findings

### ✅ Strengths

1. **M3 wiring is end-to-end real**, not just paper. Live curl to `/api/brief` with
   `MINIMAX_API_KEY` set returns a substantive 4-paragraph research brief.
2. **Prompt iteration evidence is preserved** in `Program/prompts/CHANGELOG.md` with
   per-version rationale (Phase 7 P3 pain → "回归系数凭空写" → v3 evidence binding).
3. **AST-based M3 check is more honest than literal grep** — it follows module-level
   constants (`_PROVIDER = "minimax"`) and parameter defaults (`provider_id=DEFAULT_PROVIDER`),
   catching what text grep would miss.
4. **Loader chain in execute_service is graceful**: v4→v3→v2→v1 fallback means adding
   v5 to a future section won't break the un-upgraded sections.

### ⚠️ Open gaps (NOT DoD blockers, but worth tracking)

1. **6th tab (IdentificationAuditPanel) is not in SlideTabs navigation.**
   `IdentificationAuditPanel.tsx` exists, is rendered conditionally in App.tsx on
   `activeStage === "identification-audit"`, but `SlideTabs.tsx DEFAULT_TABS` only has
   5 entries. A user can't navigate to the 6th tab via the tab bar — they'd have to
   set state directly. The D3 6th-tab stub was partial. **Recommended fix:** add
   `{ id: "identification-audit", label: "识别审计", hint: "..." }` to `DEFAULT_TABS`
   in `SlideTabs.tsx`. Out of scope for the DoD fix because SlideTabs.tsx is in the
   dirty L1-L6 working tree and wasn't covered by DoD.

2. **e2e spec is a stub.** The 60-min end-to-end walkthrough is documented in
   `end-to-end.spec.ts` but only opens the page. Full implementation belongs in Phase 9.

3. **v3/v4 prompts only cover 4 of 9 execution sections.** `section_lit`,
   `section_data`, `section_institution`, `section_conclusion`, `section_refs` stay at
   v2/v1. The DoD min for execution (4 versions) is met by section-level v1/v2 plus
   cross-section v3/v4 entries. Bumping the remaining 5 sections to v3 is a logical
   Phase 9 task.

4. **`Product/web-dist/index.html` is tracked despite being build output.** This causes
   recurring dirty-tree issues when L1–L6 workers run `npm run build`. Should be added
   to `.gitignore` in a follow-up cleanup commit. Not DoD-related.

5. **Smoke-test artifacts (Tasks/smoke-*, Results/sse-smoke-*, etc.) are untracked
   in l8-dod worktree.** Already moved to `.l8-stash/` during the rebase. Recommend
   the worker either commit the smoke tests as `Program/tests/smoke/...` or add a
   `.gitignore` line.

## Recommended next steps (post L9)

- [ ] **Phase 9 (priority: high):** Add 6th tab to SlideTabs.DEFAULT_TABS so users
  can navigate to IdentificationAuditPanel. ~10 LoC.
- [ ] **Phase 9 (medium):** Implement full 5-tab walkthrough in `end-to-end.spec.ts`.
- [ ] **Phase 9 (low):** Bump remaining 5 execution sections to v3 (evidence binding).
- [ ] **Cleanup (low):** Add `Product/web-dist/` to `.gitignore` to stop tracking build
  output. Stops L1-L6 dirty-tree issues.
- [ ] **Cleanup (low):** Decide on smoke-test artifact retention (commit vs gitignore).

## Conclusion

L1–L8 work is **internally consistent, testable, and end-to-end functional** with the
real M3 Token Plan key. The DoD gates that are automatable all pass. The one MANUAL
gate (PM browser-acceptance) and the open gaps above are explicitly tagged for follow-up
and not DoD-blocking.

Phase 8 (5-tab product) is ready for PM-driven manual acceptance.
