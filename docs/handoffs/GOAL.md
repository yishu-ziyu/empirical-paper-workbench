# Paper engine loop

Operational target for this product. Design authority: `docs/specs/paper-engine.md`.
Parent accepts. Workers implement non-overlapping files. Do not wait for the human to say 开.

```text
Goal:     After the user sets a direction on a CSV with the named columns,
          the engine has identification, a citable main table, a robustness
          stamp, and a literature list before any chapter prose exists.
          Six chapters then write from those artifacts. OLS cannot be written
          as causal. Numbers in the results chapter must be the tool table.

Hard bar: Spec hard bars 1-6 stay green on the command below.
          Named leftovers in this file are 0.

Improve:  leftover named defects (start: 5 → now: 0)

Loop:     accept or change → run the hard-bar command → read → hunt the
          next in-scope defect → dispatch or implement → repeat
Stop:     hard bars hold, leftover list is empty, and the next change
          would be frontend, git, or a new product surface
```

## Hard-bar command

From `/Users/mahaoxuan/Desktop/经济学论文/econpaper`:

```bash
./agent/.venv/bin/python -m pytest \
  agent/tests/test_readiness.py \
  agent/tests/test_association_methods.py \
  agent/tests/test_estimate.py \
  agent/tests/test_grounding.py \
  agent/tests/test_generate_chapter.py \
  agent/tests/test_generate_chapter_versions.py \
  agent/tests/test_review_chapter.py \
  agent/tests/test_rollback.py \
  agent/tests/test_results_table_grounding.py \
  agent/tests/test_search_literature.py \
  agent/tests/test_crossref_source.py \
  agent/tests/test_structure_checks.py \
  agent/tests/test_robustness_check.py \
  agent/tests/test_graph_six_chapters.py \
  agent/tests/test_graph_fanin.py \
  -q --tb=short

./backend/.venv/bin/python -m pytest \
  backend/tests/test_review.py \
  backend/tests/test_graph.py \
  backend/tests/test_journey.py \
  backend/tests/test_facade.py \
  -q --tb=short
```

`test_graph_fanin.py` may be absent until batch 6 lands. If the fan-in test is red, `graph.py` stays linear. That is success for batch 6, not a leftover.

## Leftovers (count these)

Empty as of 2026-08-17. Accepted this loop:

1. Graph fan-in: literature ∥ estimate; `generate_title` once (`add_edge([robustness, cite], title)`). Facade `run_prewrite` stays serial.
2. DiD Bacon + no `first_treat_col` → `status=error`, empty `treatment_row`.
3. CS robustness uses `control_group` / `notyet_cutoff`.
4. Empty citation table + `Smith (2020)` → `invented_citation`.
5. Backend door: `statspai` / `statsmodels==0.14.6` / `psycopg` / `jinja2` / postgres checkpointer in `backend/.venv`. Smoke: `income ~ age` writes `| age | 0.1000 | ... |`.

Out of scope (do not start): frontend, journey copy, desktop shell, git/PR, ReAct planner, multi-agent swarm, MCP-as-product.

Residual risks, not leftovers:

- Live MiniMax may emit a second `| 变量 | 系数 | SE | p |` header; review is supposed to fail (`invented_table`).
- Chinese treatment labels such as 年龄 are outside the invented_number label set.

## How this loop runs

1. STATUS files are a map. Parent reruns the hard-bar command.
2. Failures that belong to an open worker file: send back, do not rewrite their file in the parent unless they are blocked and the human already authorized the parent to finish.
3. Independent startable leftovers may go to 执行1–4 with non-overlapping files, or the parent does them if a split would collide.
4. After a wave is accepted, immediately take the next leftover. Do not wait for 开.
5. Write leftover count into `COORDINATOR.md` when it changes.

## Why stop

Hard bars 1-6 green, leftover list empty, no further in-scope defect a test would catch.
