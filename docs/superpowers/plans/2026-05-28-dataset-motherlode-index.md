# Dataset Motherlode Index Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a read-only CLI indexer for the local empirical dataset motherlode so Auto Mode can find candidate data sources for a topic before literature, method, and execution agents run.

**Architecture:** Add a focused workbench module that scans only file metadata, groups files by dataset family, extracts year and format hints, and ranks candidate families for a topic. Add a thin CLI wrapper that writes a draft JSON manifest and Markdown review report under generated/review paths without touching formal state.

**Tech Stack:** Python standard library, `unittest`, JSON and Markdown outputs, existing `Program/workbench` plus thin `Program/*.py` CLI pattern.

---

## BDD Behaviors

1. Given a local empirical dataset motherlode, When the indexer scans it, Then the report records the data source as `read_only`, `local_only`, and `user_provided_public_dataset_pool` without mutating source files.
   Business rule: user-provided datasets are source material, not product state.

2. Given nested data, archive, document, and code files, When the indexer builds dataset families, Then each family includes file counts, bytes, extensions, year hints, sample paths, and field profile status without reading full raw data.
   Business rule: the first pass must be fast and safe enough for large local stores.

3. Given the custom topic `工业机器人对劳动力市场匹配效率的影响`, When topic matching runs, Then candidate families prioritize robot, IFR, labor market, CLDS, CFPS, CMDS, and labor segmentation sources by transparent match reasons.
   Business rule: Auto Mode must turn a topic into data leads instead of asking the user to browse folders manually.

4. Given a completed scan, When the CLI writes outputs, Then it creates `Results/json/dataset_motherlode_index.json` and `Reviews/dataset_motherlode_index.md` with status `needs_human_dataset_index_review`.
   Business rule: the output enters a draft/review layer and remains human-reviewable.

5. Given the indexer runs in Auto Mode, When boundary flags are inspected, Then they show no formal manuscript, bibliography, run plan, or raw dataset writeback.
   Business rule: discovery can propose bindings but cannot silently promote anything to canonical project state.

## Files

- Create: `Program/workbench/dataset_motherlode_index.py`
  - Owns dataset source metadata, family scan, topic matching, JSON report construction, and Markdown rendering.
- Create: `Program/dataset_motherlode_index.py`
  - Thin CLI wrapper matching the existing workbench CLI pattern.
- Create: `tests/test_dataset_motherlode_index.py`
  - BDD/TDD tests using temporary dummy files, not the real data motherlode.
- Create: `docs/superpowers/plans/2026-05-28-dataset-motherlode-index.md`
  - This execution plan and acceptance record.

## Task 1: Tracer Test For Read-Only Manifest

**Files:**
- Create: `tests/test_dataset_motherlode_index.py`
- Create: `Program/workbench/dataset_motherlode_index.py`

- [x] **Step 1: Write the failing test**

```python
def test_bdd_p7a_indexes_local_motherlode_as_read_only_source(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        data_root = Path(tmp) / "motherlode"
        family = data_root / "IFR industrial robots 1993-2023"
        family.mkdir(parents=True)
        (family / "ifr_robot_2020.csv").write_text("year,value\n2020,1\n", encoding="utf-8")

        report = build_dataset_motherlode_index(data_root, topic="工业机器人对劳动力市场匹配效率的影响")

        self.assertEqual(report["schema_version"], "p7.dataset_motherlode_index.v1")
        self.assertEqual(report["status"], "needs_human_dataset_index_review")
        self.assertEqual(report["data_source"]["status"], "read_only")
        self.assertFalse(report["boundary_flags"]["modified_raw_dataset"])
```

- [x] **Step 2: Run the test to verify it fails**

Run: `python3 -m unittest tests.test_dataset_motherlode_index -v`

Expected: FAIL with `ModuleNotFoundError` or missing `build_dataset_motherlode_index`.

- [x] **Step 3: Write minimal implementation**

Implement `build_dataset_motherlode_index(data_root: Path, topic: str | None = None) -> dict[str, Any]` with schema, status, data source metadata, one scanned family, and boundary flags.

- [x] **Step 4: Run the test to verify it passes**

Run: `python3 -m unittest tests.test_dataset_motherlode_index -v`

Expected: PASS for the tracer behavior.

## Task 2: Dataset Family Metadata

**Files:**
- Modify: `tests/test_dataset_motherlode_index.py`
- Modify: `Program/workbench/dataset_motherlode_index.py`

- [x] **Step 1: Add failing test for family metadata**

```python
def test_bdd_p7a_groups_nested_files_into_dataset_families(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        data_root = Path(tmp) / "motherlode"
        family = data_root / "CLDS 2018 labor survey"
        nested = family / "stata"
        nested.mkdir(parents=True)
        (nested / "clds2018.dta").write_bytes(b"demo")
        (family / "dictionary_2018.xlsx").write_bytes(b"demo")

        report = build_dataset_motherlode_index(data_root, topic="劳动力市场匹配效率")
        clds = report["dataset_families"][0]

        self.assertEqual(clds["family_name"], "CLDS 2018 labor survey")
        self.assertEqual(clds["file_count"], 2)
        self.assertEqual(clds["extensions"], [".dta", ".xlsx"])
        self.assertEqual(clds["year_hints"], ["2018"])
        self.assertEqual(clds["field_profile_status"], "not_profiled_metadata_index_only")
```

- [x] **Step 2: Run and confirm failure**

Run: `python3 -m unittest tests.test_dataset_motherlode_index -v`

Expected: FAIL on missing or incomplete family metadata.

- [x] **Step 3: Implement metadata scan**

Scan supported files with `Path.rglob`, group by top-level family, calculate byte size with `stat().st_size`, collect extensions, infer `20xx` year hints, cap sample paths, and mark `not_profiled_metadata_index_only`.

- [x] **Step 4: Run and confirm pass**

Run: `python3 -m unittest tests.test_dataset_motherlode_index -v`

Expected: PASS.

## Task 3: Topic Matching

**Files:**
- Modify: `tests/test_dataset_motherlode_index.py`
- Modify: `Program/workbench/dataset_motherlode_index.py`

- [x] **Step 1: Add failing test for topic-to-data matching**

```python
def test_bdd_p7a_ranks_robot_labor_topic_candidates(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        data_root = Path(tmp) / "motherlode"
        for family_name in [
            "IFR industrial robots 1993-2023",
            "CLDS 中国劳动力动态调查 2018",
            "CGSS 中国综合社会调查 2021",
            "provincial labor market segmentation 2000-2024",
            "unrelated_weather_data",
        ]:
            family = data_root / family_name
            family.mkdir(parents=True)
            (family / "data_2020.csv").write_text("x\n1\n", encoding="utf-8")

        report = build_dataset_motherlode_index(data_root, topic="工业机器人对劳动力市场匹配效率的影响")
        top_names = [item["family_name"] for item in report["candidate_data_bindings"][:4]]

        self.assertIn("IFR industrial robots 1993-2023", top_names)
        self.assertIn("CLDS 中国劳动力动态调查 2018", top_names)
        self.assertIn("provincial labor market segmentation 2000-2024", top_names)
        self.assertNotEqual(report["candidate_data_bindings"][0]["family_name"], "unrelated_weather_data")
```

- [x] **Step 2: Run and confirm failure**

Run: `python3 -m unittest tests.test_dataset_motherlode_index -v`

Expected: FAIL because topic ranking is absent or weak.

- [x] **Step 3: Implement transparent scoring**

Add a small dictionary for robot, labor, survey, market matching terms. Score family name and path text, return positive-score candidates sorted by score, and include `match_reasons`.

- [x] **Step 4: Run and confirm pass**

Run: `python3 -m unittest tests.test_dataset_motherlode_index -v`

Expected: PASS.

## Task 4: CLI Output And Review Report

**Files:**
- Create: `Program/dataset_motherlode_index.py`
- Modify: `tests/test_dataset_motherlode_index.py`
- Modify: `Program/workbench/dataset_motherlode_index.py`

- [x] **Step 1: Add failing test for draft outputs**

```python
def test_bdd_p7a_writes_json_and_markdown_review_outputs(self) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        project_root = Path(tmp) / "project"
        data_root = Path(tmp) / "motherlode"
        (data_root / "CFPS 2022").mkdir(parents=True)
        (data_root / "CFPS 2022" / "cfps2022.csv").write_text("x\n1\n", encoding="utf-8")

        report = build_dataset_motherlode_index(data_root, topic="居民幸福感")
        report_path, review_path = write_report(
            project_root,
            report,
            Path("Results/json/dataset_motherlode_index.json"),
            Path("Reviews/dataset_motherlode_index.md"),
        )

        self.assertTrue(report_path.exists())
        self.assertTrue(review_path.exists())
        self.assertIn("needs_human_dataset_index_review", review_path.read_text(encoding="utf-8"))
        self.assertIn("正式层写回：否", review_path.read_text(encoding="utf-8"))
```

- [x] **Step 2: Run and confirm failure**

Run: `python3 -m unittest tests.test_dataset_motherlode_index -v`

Expected: FAIL because `write_report` or CLI wiring is missing.

- [x] **Step 3: Implement writer and CLI**

Write JSON and Markdown outputs under project root. CLI arguments: `--project-root`, `--data-root`, `--topic`, `--output-report`, `--output-review`.

- [x] **Step 4: Run tests and compile**

Run:

```bash
python3 -m unittest tests.test_dataset_motherlode_index -v
python3 -m py_compile Program/dataset_motherlode_index.py Program/workbench/dataset_motherlode_index.py tests/test_dataset_motherlode_index.py
```

Expected: PASS and no compile output.

## Task 5: Real Motherlode Smoke Run

**Files:**
- Generated: `Results/json/dataset_motherlode_index.json`
- Generated: `Reviews/dataset_motherlode_index.md`

- [x] **Step 1: Run the CLI on the local motherlode**

Run:

```bash
python3 Program/dataset_motherlode_index.py --project-root . --data-root "/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库" --topic "工业机器人对劳动力市场匹配效率的影响"
```

Expected: prints draft JSON path, review path, and `status=needs_human_dataset_index_review`.

- [x] **Step 2: Verify outputs**

Run:

```bash
python3 -m unittest tests.test_dataset_motherlode_index -v
git diff --check -- Program/dataset_motherlode_index.py Program/workbench/dataset_motherlode_index.py tests/test_dataset_motherlode_index.py docs/superpowers/plans/2026-05-28-dataset-motherlode-index.md Results/json/dataset_motherlode_index.json Reviews/dataset_motherlode_index.md
```

Expected: tests pass and whitespace check passes.

- [x] **Step 3: Commit scoped files only**

Run:

```bash
git add Program/dataset_motherlode_index.py Program/workbench/dataset_motherlode_index.py tests/test_dataset_motherlode_index.py docs/superpowers/plans/2026-05-28-dataset-motherlode-index.md Results/json/dataset_motherlode_index.json Reviews/dataset_motherlode_index.md
git commit -m "Index empirical dataset motherlode for topic intake"
```

Expected: commit contains only P7-A files and excludes UI, formal state, templates, and old run directories.

## Self-Review

- Spec coverage: covers first implementation slice `Dataset Motherlode Index`, the Data Source Model, read-only source handling, topic-to-data candidate discovery, and draft/review output boundary.
- Deliberate gap: variable-level profiling is deferred to a later DataAgent profiling slice because it requires dataset-specific parsers and can be expensive on large files.
- Placeholder scan: no placeholder terms are used as work instructions.
- Type consistency: public interface remains `build_dataset_motherlode_index(data_root: Path, topic: str | None = None)`, plus `write_report(project_root, report, report_path, review_path)`.

## Execution Record

- Real CLI run: `python3 Program/dataset_motherlode_index.py --project-root . --data-root "/Users/mahaoxuan/Desktop/论文核心素材库/01_原始数据/实证数据库" --topic "工业机器人对劳动力市场匹配效率的影响"`.
- Output JSON: `Results/json/dataset_motherlode_index.json`.
- Output review: `Reviews/dataset_motherlode_index.md`.
- Real status: `needs_human_dataset_index_review`.
- Real top candidate: `外部源数据`, with match reasons including `ifr`, `robot`, `工业机器人`, and `机器人`.
- TDD expansion after real run: added tests for nested path keyword hints beyond sample paths and hidden/system-file filtering.
- Verified: `python3 -m unittest tests.test_dataset_motherlode_index -v`, `python3 -m py_compile Program/dataset_motherlode_index.py Program/workbench/dataset_motherlode_index.py tests/test_dataset_motherlode_index.py`, and scoped `git diff --check`.
