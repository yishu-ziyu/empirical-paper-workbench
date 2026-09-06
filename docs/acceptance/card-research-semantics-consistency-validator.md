# Validator report: Card research semantics consistency (S1–S8)

Date: 2026-09-06
Branch: `review/workbench-v2` @ HEAD `732d55a` (dirty working tree; 3 fixes uncommitted)
Contract: `docs/acceptance/card-research-semantics-consistency.md` (Status left **open**; this report does not close it)
Parent: `docs/acceptance/card-research-integrity.md` (I3 definition-corrected via C-rev)
Evaluator: independent validator. Did not implement. Did not treat implementer conversation or summaries as proof. Re-ran programmatic checks from this shell.

## Verdict: ACCEPT

The working-tree diff is the three contracted fixes plus tests, parent I3 C-rev wording, and task-state notes. No redesign, no feature expansion, no merge, no push.

S1–S4 hard bars passed on this validator’s pytest/vitest output. S5–S7 live browser walks were **NOT RUN** (orchestrator). Tests that encode those scenarios were re-run and passed. Local S8 gates passed; CI on PR #28 was **NOT RUN**.

---

## Diff vs HEAD (scope)

`git diff --name-status HEAD`:

```
M	agent/engine/claim_wording.py
M	agent/engine/readiness.py
M	agent/tests/test_claim_wording.py
M	agent/tests/test_readiness.py
M	backend/services/research_lab.py
M	backend/tests/test_card_claim_ledger.py
M	docs/acceptance/card-research-integrity.md
M	frontend/src/components/AgentRail.tsx
M	frontend/src/components/__tests__/AgentRail.test.tsx
M	runtime/STATE.md
```

Untracked (contract/task only):

```
docs/acceptance/card-research-semantics-consistency.md
runtime/tasks/20260906-card-research-semantics-consistency.md
```

Product code mapping:

| File | Fix |
|---|---|
| `backend/services/research_lab.py` | S1: `promote_run` / `revert_canonical` return lab without `bump_evidence_revision`; still write `canonical_history` + `decision_events`. S4: `require_claim_ready_for_paper` / `approve_card_claim` call shared `claim_revision_is_stale`. |
| `agent/engine/claim_wording.py` | S2 sentence split without requiring whitespace after `。！？!?`; S3 population-wide tokens fail closed even with IV caveat. |
| `agent/engine/readiness.py` | S4 shared `claim_revision_is_stale`; missing `based_on_evidence_revision` is stale when lab has `evidence_revision` (including 0). |
| `frontend/src/components/AgentRail.tsx` | S4 Paper badge: lab `evidence_revision` present + missing `based_on` → not grounded. Not a UI redesign. |

`bump_evidence_revision` remains on completed spec-run merge (`spec_run.py:218`, `research_lab.merge` when runs added). Promote/revert bodies no longer call it.

Parent I3 C-rev in `card-research-integrity.md` matches the in-force definition: Promote/Revert are decision history, not `evidence_revision +1`. That is a named definition correction, not a silent relaxation of stale-on-new-evidence.

---

## Checks

### S1 evidence_revision 定义 — PASS

Command:

```
PYTHONPATH=$(pwd):$(pwd)/backend backend/.venv/bin/python -m pytest -v --tb=short -p no:cacheprovider \
  --basetemp=$(mktemp -d /tmp/ep-be-XXXXXX) \
  backend/tests/test_card_claim_ledger.py::test_promote_and_revert_do_not_bump_evidence_revision_or_stale_claim \
  backend/tests/test_card_claim_ledger.py::test_prepare_paper_does_not_implicitly_promote_canonical \
  backend/tests/test_card_claim_ledger.py::test_new_spec_run_stales_approved_claim \
  backend/tests/test_card_claim_ledger.py::test_promote_marks_results_stale
```

Evidence excerpt (this run):

```
backend/tests/test_card_claim_ledger.py::test_promote_and_revert_do_not_bump_evidence_revision_or_stale_claim PASSED
backend/tests/test_card_claim_ledger.py::test_prepare_paper_does_not_implicitly_promote_canonical PASSED
backend/tests/test_card_claim_ledger.py::test_new_spec_run_stales_approved_claim PASSED
backend/tests/test_card_claim_ledger.py::test_promote_marks_results_stale PASSED
5 passed in 14.33s
```

Hard-bar encoding in `test_prepare_paper_does_not_implicitly_promote_canonical`: approve Claim `based_on == N` → promote OLS → prepare-paper 409 `canonical_mismatch` → claim `stale is not True` and revision still N → promote IV → revision still N, same claim version, `claim_drafted` events unchanged, exactly one `claim_approved` → prepare-paper 200. `test_promote_and_revert_do_not_bump_evidence_revision_or_stale_claim` asserts `preview_promote` / `preview_revert` events and `canonical_history` without revision bump. `test_new_spec_run_stales_approved_claim` still `evidence_revision == revision + 1` and `claim.stale is True`. `test_promote_marks_results_stale` keeps R4: Results chapter `stale` / `needs_regeneration` after promote, Claim not stale, revision unchanged.

Source: `promote_run` ends `return lab`; `revert_canonical` no longer assigns `bump_evidence_revision`.

### S2 wording 标点切分 — PASS

Command:

```
PYTHONPATH=$(pwd):$(pwd)/backend agent/.venv/bin/python -m pytest -v --tb=short -p no:cacheprovider \
  --basetemp=$(mktemp -d /tmp/ep-ag-XXXXXX) \
  agent/tests/test_claim_wording.py::test_chinese_period_splits_without_whitespace
```

Evidence excerpt:

```
agent/tests/test_claim_wording.py::test_chinese_period_splits_without_whitespace PASSED
```

Must-reject string in test: `在工具变量假设成立时，IV 估计表明存在局部因果回报。多读一年书导致所有人工资提高13%。` Implementation: `_SENTENCE_SPLIT = re.compile(r"(?<=[。！？!?])\s*|(?<=\.)(?=\s+|[A-Z])")`. `check_grounding` / `results_is_grounded` import `wording_exceeds_evidence` (`test_grounding_and_results_gate_share_policy` in the targeted agent suite).

### S3 wording 人口范围 — PASS

Command:

```
PYTHONPATH=$(pwd):$(pwd)/backend agent/.venv/bin/python -m pytest -v --tb=short -p no:cacheprovider \
  --basetemp=$(mktemp -d /tmp/ep-ag-XXXXXX) \
  agent/tests/test_claim_wording.py::test_caveat_does_not_greenlight_population_wide_ate \
  agent/tests/test_claim_wording.py::test_population_wide_wording_exceeds_even_with_iv_caveat \
  agent/tests/test_claim_wording.py::test_caveated_iv_wording_is_allowed
```

Evidence excerpt:

```
agent/tests/test_claim_wording.py::test_caveat_does_not_greenlight_population_wide_ate PASSED
agent/tests/test_claim_wording.py::test_population_wide_wording_exceeds_even_with_iv_caveat PASSED
agent/tests/test_claim_wording.py::test_caveated_iv_wording_is_allowed PASSED
```

Must-reject: `Under the college-proximity IV assumptions, IV estimates suggest a local return, but education raises everyone's wage by 13%.` Cases also cover `everyone` / `everyone's` / `all workers` / `all people` / `所有人` / `每个人` / `普遍提高`. Allowed: `Under the college-proximity IV assumptions, IV estimates suggest a positive local causal return to schooling.` Tokens: `_POPULATION_EN` / `_POPULATION_ZH`; `_sentence_exceeds` returns True on population-wide even when caveat is present. No LLM/NLP added.

### S4 stale fail closed 且统一 — PASS

Commands:

```
PYTHONPATH=$(pwd):$(pwd)/backend agent/.venv/bin/python -m pytest -v --tb=short -p no:cacheprovider \
  --basetemp=$(mktemp -d /tmp/ep-ag-XXXXXX) \
  agent/tests/test_readiness.py::test_missing_based_on_revision_blocks_results_when_lab_has_revision \
  agent/tests/test_readiness.py::test_missing_based_on_is_stale_when_evidence_revision_is_zero

PYTHONPATH=$(pwd):$(pwd)/backend backend/.venv/bin/python -m pytest -v --tb=short -p no:cacheprovider \
  --basetemp=$(mktemp -d /tmp/ep-be-XXXXXX) \
  backend/tests/test_card_claim_ledger.py::test_missing_based_on_revision_is_stale_when_lab_has_revision

cd frontend && npx vitest run src/components/__tests__/AgentRail.test.tsx
```

Evidence excerpt:

```
agent/tests/test_readiness.py::test_missing_based_on_revision_blocks_results_when_lab_has_revision PASSED
agent/tests/test_readiness.py::test_missing_based_on_is_stale_when_evidence_revision_is_zero PASSED
backend/tests/test_card_claim_ledger.py::test_missing_based_on_revision_is_stale_when_lab_has_revision PASSED
 ✓ src/components/__tests__/AgentRail.test.tsx (4 tests) 42ms
   missing based_on_evidence_revision is not grounded when lab has revision
```

Shared helper: `agent.engine.readiness.claim_revision_is_stale`; backend `require_claim_ready_for_paper` imports it. Lab `evidence_revision=3`, approved claim missing `based_on_evidence_revision` → `paper_ready_to_write` Results blocked `claim_stale` → `results_is_grounded` false → snapshot `write_blockers` contains `claim_stale`, Results `grounded is False` → prepare-paper 409 `code == claim_stale` → AgentRail badge `data-grounded=false`.

### S5 浏览器 Scenario A — NOT RUN

Live Card teaching-case browser walk not executed (orchestrator). Encodings verified:

- Programmatic Scenario A: `test_prepare_paper_does_not_implicitly_promote_canonical` PASSED (S1).
- UI mismatch + Promote supporting + Write Results, claim `stale: false` so Review-new-evidence branch is not taken: `EvidenceLab.test.tsx` `mismatch after approve offers explicit promote and still allows write results` PASSED.

```
cd frontend && npx vitest run src/components/__tests__/EvidenceLab.test.tsx
 ✓ src/components/__tests__/EvidenceLab.test.tsx (3 tests) 58ms
```

UI source: `stale ? Review new evidence : Approved` (`EvidenceLab.tsx`). Not a live 409-toast / post-Promote unlock walk.

### S6 浏览器 Scenario B — NOT RUN

Live Preview/Challenge browser walk not executed. Encoding verified: `test_new_spec_run_stales_approved_claim` PASSED — preview run `evidence_revision == revision + 1`, `claim.stale is True`, `claim_stale` write blocker. UI still shows `Review new evidence` when `claim.stale`. No dedicated frontend test asserting the Review button after preview.

### S7 浏览器 Scenario C — NOT RUN

Live wording-bypass browser walk not executed. Encoding verified by S2/S3 pytest (`test_chinese_period_splits_without_whitespace`, `test_caveat_does_not_greenlight_population_wide_ate`, `test_caveated_iv_wording_is_allowed` all PASSED). Shared policy: `test_grounding_and_results_gate_share_policy` in targeted agent suite (32 passed including that file).

### S8 回归与门禁 — PASS (CI NOT RUN)

Targeted (this validator):

```
backend/tests/test_card_claim_ledger.py backend/tests/test_card_spec_run.py
.........................                                                [100%]
25 passed in 22.52s

agent/tests/test_claim_wording.py agent/tests/test_readiness.py agent/tests/test_grounding.py
................................                                         [100%]
32 passed in 0.04s

npx vitest run AgentRail.test.tsx EvidenceLab.test.tsx
 Test Files  2 passed (2)
      Tests  7 passed (7)
```

Full suites:

```
make test-agent     → 819 passed, 1 skipped, 4 warnings in 42.83s
make test-backend   → 421 passed, 8 skipped, 32 warnings in 115.79s
make test-frontend  → Test Files 53 passed (53); Tests 348 passed (348)
```

Skip counts match R3: agent 1 skip, backend 8 skip, frontend 0 skip. No new skip in this diff.

```
make check-api-drift
[check-api-drift] ✅ openapi.json 与后端代码同步
[check-api-drift] ✅ docs/api/openapi.json 与后端代码同步
[check-api-drift] ✅ types/api.ts 与 openapi.json 同步

cd frontend && npx oxlint .
Found 5 warnings and 0 errors.

cd frontend && npx tsc -b --pretty false
exit 0

cd frontend && npm run build
tsc -b && vite build
✓ 499 modules transformed.
✓ built in 1.60s
```

CI on PR #28: **NOT RUN** (uncommitted working tree; validator did not push).

---

## Named relaxations applied

- R1: Card-only deterministic wording; no NLP.
- R2: browser Scenarios not executed here.
- R3: existing 1 agent / 8 backend skips unchanged.
- R4: Promote may stale Results chapter; Claim must not stale (`test_promote_marks_results_stale`).
- C-rev on parent I3: definition correction, not a Named relaxation of new-evidence stale.

## Not done by this validator

- Did not close contract Status.
- Did not commit, merge, or push.
- Did not drive browser Scenario A–C.
- Did not observe GitHub CI on PR #28.
