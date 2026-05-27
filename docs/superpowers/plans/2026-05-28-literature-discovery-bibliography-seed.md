# Literature Discovery Bibliography Seed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first generic LiteratureAgent seed that turns a user topic and dataset-index context into query plans, source registry, bibliography states, and human-reviewable discovery tasks.

**Architecture:** Add a focused workbench module that does not perform live network calls in this slice. It expands topic concepts, uses Dataset Motherlode Index candidates as context, registers discovery/acquisition sources, creates candidate search records, and writes draft JSON plus Markdown review outputs.

**Tech Stack:** Python standard library, `unittest`, existing thin CLI pattern, generated JSON and Markdown review artifacts.

---

## BDD Behaviors

1. Given a custom topic, When LiteratureAgent builds a discovery seed, Then it outputs Chinese and English query plans with X/Y concepts, dataset hints, and method-context hints.
   Business rule: literature work starts from structured search intent, not one blank prompt.

2. Given a Dataset Motherlode Index report, When literature discovery seed runs, Then candidate data bindings such as IFR, robot, CLDS, CFPS, CGSS, CMDS, and labor-market datasets are folded into the query plan.
   Business rule: data discovery and literature discovery must inform each other.

3. Given the source registry, When the seed is inspected, Then it lists local PDF/Zotero import, OpenAlex-style metadata, Crossref metadata, Semantic Scholar metadata, open fulltext discovery, Chinese database/manual review queues, Google Scholar/manual queues, and user-uploaded fulltext.
   Business rule: the product has a clear answer to where references come from.

4. Given candidate search records, When bibliography state is inspected, Then every record starts as `candidate`, cannot support strong claims, and must pass through fulltext/source-span/human-review states before project bibliography approval.
   Business rule: discovery can be aggressive, but paper claims remain evidence-bound.

5. Given the CLI runs, When outputs are written, Then it creates `Results/json/literature_discovery_seed.json` and `Reviews/literature_discovery_seed.md` with status `needs_human_literature_discovery_review`.
   Business rule: P7-B remains a reviewable draft layer.

6. Given Auto Mode is active, When boundary flags are inspected, Then no formal bibliography, formal manuscript, or product state is written.
   Business rule: candidate references do not silently become canonical sources.

## Files

- Create: `Program/workbench/literature_discovery_seed.py`
  - Topic expansion, dataset-context integration, source registry, bibliography state model, review renderer.
- Create: `Program/literature_discovery_seed.py`
  - Thin CLI wrapper.
- Create: `tests/test_literature_discovery_seed.py`
  - BDD/TDD tests with temporary dataset-index fixtures.
- Create: `docs/superpowers/plans/2026-05-28-literature-discovery-bibliography-seed.md`
  - This plan and execution record.

## Tasks

- [x] Write failing tests for topic query expansion, dataset-index integration, source registry, bibliography states, output writing, and boundary flags.
- [x] Confirm RED caused by missing `Program.workbench.literature_discovery_seed`.
- [x] Implement the minimal workbench module and CLI.
- [x] Run target tests and py_compile.
- [x] Run the real CLI using `Results/json/dataset_motherlode_index.json`.
- [x] Record output paths and verification in `Tasks/todo.md`.
- [x] Commit scoped P7-B files only.

## Execution Record

- Planned output JSON: `Results/json/literature_discovery_seed.json`.
- Planned output review: `Reviews/literature_discovery_seed.md`.
- Formal writeback: disabled for bibliography, manuscript, and product state.
- Deliberate gap: live API search, deduplication, PDF download, source-span extraction, and Zotero import are later LiteratureAgent execution nodes.
- Real CLI run: `python3 Program/literature_discovery_seed.py --project-root . --topic "工业机器人对劳动力市场匹配效率的影响" --dataset-index Results/json/dataset_motherlode_index.json`.
- Real status: `needs_human_literature_discovery_review`.
- Real query count: 13.
- Registered source count: 8.
- Candidate search record count: 13.
