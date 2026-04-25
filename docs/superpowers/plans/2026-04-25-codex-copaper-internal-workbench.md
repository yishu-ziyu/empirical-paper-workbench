# Codex CoPaper Internal Workbench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Codex-native CoPaper-like workbench so the first full experience runs on `/Users/mahaoxuan/Desktop/学术灵感项目_2026-04-07/final` while preserving a reusable B-level architecture.

**Architecture:** Implement a reusable project adapter, run folder contract, evidence scanners, multi-agent supervisor, review loop, and formatter. The first adapter profile targets the real thesis repository; future projects use the same adapter interfaces and run contract.

**Tech Stack:** Python 3 standard library, FastAPI existing shell, Pydantic/FastAPI where already used, existing `Program/workbench` export helpers, optional `pandoc` for Word export, `unittest` tests.

---

## Repository Context

Product repository:

`/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`

Real thesis repository:

`/Users/mahaoxuan/Desktop/学术灵感项目_2026-04-07/final`

Approved design spec:

`/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/docs/superpowers/specs/2026-04-25-codex-copaper-internal-workbench-design.md`

Current code to reuse:

- `Product/backend/orchestrator.py`
- `Product/backend/orchestration_schema.py`
- `Product/backend/project_service.py`
- `Product/backend/run_store.py`
- `Product/app.py`
- `Program/export_docx.py`
- `Program/workbench/export.py`
- `tests/test_orchestrator.py`
- `tests/test_product_v1_local.py`

Current thesis inputs to preserve:

- `AI_项目交接文档.md`
- `state/project_state.json`
- `state/source_registry.json`
- `literature/manifest.json`
- `03_results/index.json`
- `04_paper/sections_v21`
- `04_paper/论文v2.1_完整版.md`
- `05_reference/匹配效率概念与可测代理对照表.md`
- `05_reference/v21_formal_references_candidate_list.md`
- `04_paper/word_hqu_format`

## File Structure To Create Or Modify

- Create `Product/backend/workbench_paths.py`
  - Owns run folder paths and required directory contract.
- Create `Product/backend/project_adapter.py`
  - Detects thesis and generic project layouts.
- Create `Product/backend/evidence.py`
  - Scans data, literature, references, manuscripts, and result files.
- Modify `Product/backend/orchestration_schema.py`
  - Expands schema to spec-compliant handoff, review, and manifest packets.
- Replace major parts of `Product/backend/orchestrator.py`
  - Implements `Supervisor` plus required agents.
- Modify `Product/backend/project_service.py`
  - Adds full workbench run entrypoint and snapshot loading from `06_workspace/runs`.
- Modify `Product/app.py`
  - Adds `/api/v1/projects/{project_id}/workbench-runs` endpoints.
- Create `Product/cli.py`
  - Codex-first command entrypoint without requiring a website.
- Create `tests/test_workbench_paths.py`
  - Tests run folder contract.
- Create `tests/test_project_adapter.py`
  - Tests thesis layout detection and generic layout fallback.
- Create `tests/test_evidence_inventory.py`
  - Tests source, dataset, literature, and results inventory.
- Create `tests/test_full_workbench_run.py`
  - Tests full dry run against a temporary thesis-like project.
- Modify `tests/test_orchestrator.py`
  - Updates old `state/orchestration` expectations to `06_workspace/runs`.
- Modify `tests/test_product_v1_local.py`
  - Verifies API can launch and poll a workbench run.

## Task 1: Run Folder Contract

**Files:**

- Create: `Product/backend/workbench_paths.py`
- Test: `tests/test_workbench_paths.py`

- [ ] **Step 1: Write the failing tests**

```python
import shutil
import tempfile
import unittest
from pathlib import Path

from Product.backend.workbench_paths import create_run_workspace, required_run_relative_paths


class WorkbenchPathsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="workbench-paths-"))
        self.project_root = self.temp_dir / "project"
        self.project_root.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_create_run_workspace_prefers_06_workspace(self) -> None:
        (self.project_root / "06_workspace").mkdir()
        run = create_run_workspace(self.project_root, run_id="run_test")

        self.assertEqual(run.run_id, "run_test")
        self.assertEqual(run.root, self.project_root / "06_workspace" / "runs" / "run_test")
        for rel in required_run_relative_paths():
            self.assertTrue((run.root / rel).exists(), rel)

    def test_create_run_workspace_uses_workspace_fallback(self) -> None:
        run = create_run_workspace(self.project_root, run_id="run_fallback")

        self.assertEqual(run.root, self.project_root / "workspace" / "runs" / "run_fallback")
        self.assertTrue((run.root / "run_manifest.json").parent.exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_workbench_paths -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'Product.backend.workbench_paths'`.

- [ ] **Step 3: Implement `workbench_paths.py`**

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunWorkspace:
    run_id: str
    root: Path

    def stage(self, name: str) -> Path:
        return self.root / name

    def rel(self, path: Path, project_root: Path) -> str:
        return str(path.relative_to(project_root))


def required_run_relative_paths() -> list[Path]:
    return [
        Path("00_intake"),
        Path("01_sources"),
        Path("02_literature"),
        Path("03_strategy"),
        Path("04_modeling"),
        Path("05_results"),
        Path("06_writing"),
        Path("07_review"),
        Path("08_final"),
    ]


def runs_base(project_root: Path) -> Path:
    if (project_root / "06_workspace").exists():
        return project_root / "06_workspace" / "runs"
    return project_root / "workspace" / "runs"


def create_run_workspace(project_root: Path, run_id: str) -> RunWorkspace:
    root = runs_base(project_root) / run_id
    for rel in required_run_relative_paths():
        (root / rel).mkdir(parents=True, exist_ok=True)
    return RunWorkspace(run_id=run_id, root=root)
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
python3 -m unittest tests.test_workbench_paths -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add Product/backend/workbench_paths.py tests/test_workbench_paths.py
git commit -m "feat: add workbench run folder contract"
```

## Task 2: Project Adapter

**Files:**

- Create: `Product/backend/project_adapter.py`
- Test: `tests/test_project_adapter.py`

- [ ] **Step 1: Write the failing tests**

```python
import shutil
import tempfile
import unittest
from pathlib import Path

from Product.backend.project_adapter import detect_project_profile


class ProjectAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="project-adapter-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_detects_thesis_layout(self) -> None:
        root = self.temp_dir / "final"
        for rel in ["01_data", "02_code", "03_results", "04_paper/sections_v21", "05_reference", "06_workspace", "literature", "state"]:
            (root / rel).mkdir(parents=True)
        (root / "AI_项目交接文档.md").write_text("industrial robots and labor reallocation", encoding="utf-8")

        profile = detect_project_profile(root)

        self.assertEqual(profile["layout"], "thesis_final")
        self.assertEqual(profile["paths"]["data"], "01_data")
        self.assertEqual(profile["paths"]["code"], "02_code")
        self.assertEqual(profile["paths"]["results"], "03_results")
        self.assertEqual(profile["paths"]["manuscript"], "04_paper")
        self.assertIn("Bartik IV", profile["known_logic"]["identification"])

    def test_detects_generic_aer_layout(self) -> None:
        root = self.temp_dir / "generic"
        for rel in ["Data", "Program", "Results", "Manuscripts", "Reference", "state"]:
            (root / rel).mkdir(parents=True)

        profile = detect_project_profile(root)

        self.assertEqual(profile["layout"], "generic_aer")
        self.assertEqual(profile["paths"]["data"], "Data")
        self.assertEqual(profile["paths"]["code"], "Program")
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_project_adapter -v
```

Expected: FAIL with missing module.

- [ ] **Step 3: Implement `project_adapter.py`**

```python
from __future__ import annotations

from pathlib import Path
from typing import Any


THESIS_PATHS = {
    "data": "01_data",
    "code": "02_code",
    "results": "03_results",
    "manuscript": "04_paper",
    "references": "05_reference",
    "workspace": "06_workspace",
    "literature": "literature",
    "state": "state",
}

GENERIC_PATHS = {
    "data": "Data",
    "code": "Program",
    "results": "Results",
    "manuscript": "Manuscripts",
    "references": "Reference",
    "workspace": "workspace",
    "literature": "Reference",
    "state": "state",
}


def has_paths(root: Path, rels: list[str]) -> bool:
    return all((root / rel).exists() for rel in rels)


def detect_project_profile(project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    if has_paths(root, ["01_data", "02_code", "03_results", "04_paper", "05_reference"]):
        return {
            "project_root": str(root),
            "layout": "thesis_final",
            "paths": THESIS_PATHS,
            "known_logic": {
                "topic": "industrial robots and labor reallocation",
                "identification": "Bartik IV",
                "outcome_layer": "CFPS",
                "mechanism_layer": "CLDS",
                "calibration_layer": "CGSS",
                "matching_boundary": "strict matching efficiency is not directly identified",
            },
        }
    if has_paths(root, ["Data", "Program", "Results", "Manuscripts"]):
        return {
            "project_root": str(root),
            "layout": "generic_aer",
            "paths": GENERIC_PATHS,
            "known_logic": {},
        }
    raise FileNotFoundError(f"Unsupported empirical project layout: {root}")
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
python3 -m unittest tests.test_project_adapter -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add Product/backend/project_adapter.py tests/test_project_adapter.py
git commit -m "feat: detect empirical project layouts"
```

## Task 3: Evidence Inventory

**Files:**

- Create: `Product/backend/evidence.py`
- Test: `tests/test_evidence_inventory.py`

- [ ] **Step 1: Write the failing tests**

```python
import shutil
import tempfile
import unittest
from pathlib import Path

from Product.backend.evidence import build_evidence_inventory
from Product.backend.project_adapter import detect_project_profile


class EvidenceInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="evidence-inventory-"))
        self.root = self.temp_dir / "final"
        for rel in ["01_data", "02_code", "03_results", "04_paper/sections_v21", "05_reference", "06_workspace", "literature/core", "state"]:
            (self.root / rel).mkdir(parents=True)
        (self.root / "01_data" / "cfps_panel_v5.dta").write_bytes(b"stata-bytes")
        (self.root / "02_code" / "18_final_results.do").write_text("ivregress 2sls y (x=z)", encoding="utf-8")
        (self.root / "03_results" / "index.json").write_text('{"artifacts": []}', encoding="utf-8")
        (self.root / "literature" / "README.md").write_text("core literature", encoding="utf-8")
        (self.root / "literature" / "core" / "Acemoglu_Restrepo.pdf").write_bytes(b"pdf")
        (self.root / "04_paper" / "sections_v21" / "00_摘要_中文.md").write_text("摘要", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_builds_inventory_without_mutating_sources(self) -> None:
        profile = detect_project_profile(self.root)
        inventory = build_evidence_inventory(self.root, profile)

        self.assertEqual(inventory["project_root"], str(self.root.resolve()))
        self.assertEqual(inventory["datasets"][0]["name"], "cfps_panel_v5.dta")
        self.assertEqual(inventory["code_files"][0]["name"], "18_final_results.do")
        self.assertEqual(inventory["literature_files"][0]["name"], "Acemoglu_Restrepo.pdf")
        self.assertEqual(inventory["manuscript_sections"][0]["name"], "00_摘要_中文.md")
        self.assertTrue((self.root / "01_data" / "cfps_panel_v5.dta").exists())
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_evidence_inventory -v
```

Expected: FAIL with missing module or function.

- [ ] **Step 3: Implement `evidence.py`**

```python
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


DATA_SUFFIXES = {".dta", ".csv", ".xlsx", ".xls", ".sav", ".parquet", ".feather"}
LITERATURE_SUFFIXES = {".pdf", ".bib", ".md", ".txt", ".ris"}
CODE_SUFFIXES = {".py", ".do", ".R", ".r", ".jl"}


def file_record(path: Path, base: Path, include_hash: bool = False) -> dict[str, Any]:
    stat = path.stat()
    record: dict[str, Any] = {
        "name": path.name,
        "path": str(path.relative_to(base)),
        "suffix": path.suffix.lower(),
        "size": stat.st_size,
    }
    if include_hash and stat.st_size <= 20_000_000:
        record["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return record


def scan_files(root: Path, rel: str, suffixes: set[str], include_hash: bool = False) -> list[dict[str, Any]]:
    start = root / rel
    if not start.exists():
        return []
    return [
        file_record(path, root, include_hash=include_hash)
        for path in sorted(start.rglob("*"))
        if path.is_file() and path.suffix.lower() in suffixes
    ]


def build_evidence_inventory(project_root: Path, profile: dict[str, Any]) -> dict[str, Any]:
    paths = profile["paths"]
    root = project_root.resolve()
    return {
        "project_root": str(root),
        "layout": profile["layout"],
        "datasets": scan_files(root, paths["data"], DATA_SUFFIXES),
        "code_files": scan_files(root, paths["code"], CODE_SUFFIXES),
        "results_files": scan_files(root, paths["results"], {".json", ".md", ".txt", ".csv", ".rtf", ".png", ".jpg", ".jpeg", ".pdf"}),
        "literature_files": scan_files(root, paths["literature"], LITERATURE_SUFFIXES, include_hash=True),
        "reference_files": scan_files(root, paths["references"], LITERATURE_SUFFIXES, include_hash=False),
        "manuscript_sections": scan_files(root, str(Path(paths["manuscript"]) / "sections_v21"), {".md"}),
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
python3 -m unittest tests.test_evidence_inventory -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add Product/backend/evidence.py tests/test_evidence_inventory.py
git commit -m "feat: build evidence inventories"
```

## Task 4: Schema Upgrade

**Files:**

- Modify: `Product/backend/orchestration_schema.py`
- Test: `tests/test_orchestrator.py`

- [ ] **Step 1: Update tests for spec-compliant packet fields**

Add this test to `tests/test_orchestrator.py`:

```python
    def test_handoff_packet_uses_spec_fields(self) -> None:
        from Product.backend.orchestration_schema import HandoffPacket

        packet = HandoffPacket(
            run_id="run_test",
            agent="LiteratureAgent",
            stage="02_literature",
            inputs=["01_sources/literature_inventory.json"],
            outputs=["02_literature/core_literature_brief.md"],
            claims=["Core literature supports robot labor-market reallocation framing."],
            risks=["Strict matching efficiency is not directly identified."],
            next_agent="ResearchStrategistAgent",
            status="completed",
        )

        payload = packet.to_dict()
        self.assertEqual(payload["agent"], "LiteratureAgent")
        self.assertEqual(payload["next_agent"], "ResearchStrategistAgent")
        self.assertIn("risks", payload)
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_orchestrator.MultiAgentOrchestrationTests.test_handoff_packet_uses_spec_fields -v
```

Expected: FAIL because current `HandoffPacket` uses `agent_name` and `target_agent`.

- [ ] **Step 3: Replace schema dataclasses**

```python
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class HandoffPacket:
    run_id: str
    agent: str
    stage: str
    inputs: list[str]
    outputs: list[str]
    claims: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    next_agent: str | None = None
    status: str = "completed"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReviewPacket:
    run_id: str
    reviewer: str
    target_agent: str
    target_artifact: str
    decision: str
    revision_requests: list[str]
    strengths: list[str]
    risks: list[str] = field(default_factory=list)
    status: str = "completed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class OrchestrationManifest:
    run_id: str
    project_id: str
    project_root: str
    run_root: str
    mode: str
    supervisor: dict[str, Any]
    agents: list[dict[str, Any]] = field(default_factory=list)
    review_loop: dict[str, Any] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    status: str = "completed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
```

- [ ] **Step 4: Run schema test**

Run:

```bash
python3 -m unittest tests.test_orchestrator.MultiAgentOrchestrationTests.test_handoff_packet_uses_spec_fields -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add Product/backend/orchestration_schema.py tests/test_orchestrator.py
git commit -m "feat: upgrade orchestration schema"
```

## Task 5: Full Supervisor And Agents

**Files:**

- Modify: `Product/backend/orchestrator.py`
- Modify: `tests/test_orchestrator.py`
- Test: `tests/test_full_workbench_run.py`

- [ ] **Step 1: Write full run failing test**

```python
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from Product.backend.orchestrator import run_workbench


class FullWorkbenchRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="full-workbench-"))
        self.root = self.temp_dir / "final"
        for rel in ["01_data", "02_code", "03_results", "04_paper/sections_v21", "05_reference", "06_workspace", "literature/core", "state"]:
            (self.root / rel).mkdir(parents=True)
        (self.root / "01_data" / "cfps_panel_v5.dta").write_bytes(b"stata-bytes")
        (self.root / "02_code" / "18_final_results.do").write_text("ivregress 2sls y (x=z)", encoding="utf-8")
        (self.root / "03_results" / "index.json").write_text('{"artifacts": [{"path": "03_results/table.md", "exists": true}]}', encoding="utf-8")
        (self.root / "literature" / "core" / "Acemoglu_Restrepo.pdf").write_bytes(b"pdf")
        (self.root / "04_paper" / "sections_v21" / "00_摘要_中文.md").write_text("摘要", encoding="utf-8")
        (self.root / "04_paper" / "论文v2.1_完整版.md").write_text("# 论文v2.1", encoding="utf-8")
        (self.root / "05_reference" / "匹配效率概念与可测代理对照表.md").write_text("strict matching efficiency", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_full_dry_run_writes_required_artifacts(self) -> None:
        manifest = run_workbench(self.root, mode="dry-run", user_goal="推进毕业论文")
        run_root = Path(manifest["run_root"])

        required = [
            "00_intake/project_profile.json",
            "00_intake/user_goal.md",
            "01_sources/source_inventory.json",
            "01_sources/dataset_inventory.json",
            "01_sources/literature_inventory.json",
            "02_literature/literature_clusters.json",
            "02_literature/core_literature_brief.md",
            "02_literature/claim_evidence_map.json",
            "03_strategy/research_plan.md",
            "03_strategy/identification_plan.md",
            "03_strategy/empirical_plan.md",
            "04_modeling/modeling_report.json",
            "04_modeling/diagnostics_report.md",
            "05_results/results_index.json",
            "06_writing/paper_draft.md",
            "07_review/review_report.md",
            "07_review/revision_plan.md",
            "07_review/reviewer_decision.json",
            "08_final/paper_draft.tex",
            "08_final/paper_draft.docx",
            "08_final/formatting_report.md",
            "run_manifest.json",
        ]
        for rel in required:
            self.assertTrue((run_root / rel).exists(), rel)

        review = json.loads((run_root / "07_review" / "reviewer_decision.json").read_text(encoding="utf-8"))
        self.assertNotEqual(review["reviewer"], "WritingAgent")
        self.assertIn(review["decision"], ["approve", "revise_minor", "revise_major", "block"])
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_full_workbench_run -v
```

Expected: FAIL because `run_workbench` does not exist.

- [ ] **Step 3: Implement orchestrator helper functions**

Add helper functions to `Product/backend/orchestrator.py`:

```python
def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def summarize_list(items: list[dict[str, Any]], key: str = "name", limit: int = 12) -> str:
    values = [str(item.get(key, "")) for item in items[:limit] if item.get(key)]
    return "\n".join(f"- {value}" for value in values) if values else "- No local files detected."
```

- [ ] **Step 4: Implement `run_workbench` stages**

Add `run_workbench(project_root: Path, mode: str = "dry-run", user_goal: str = "") -> dict[str, Any]` to `Product/backend/orchestrator.py`.

The function must:

```python
run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:6]}"
profile = detect_project_profile(project_root)
workspace = create_run_workspace(project_root, run_id)
inventory = build_evidence_inventory(project_root, profile)
```

Then write:

```python
write_json(workspace.root / "00_intake" / "project_profile.json", profile)
write_text(workspace.root / "00_intake" / "user_goal.md", user_goal or "No explicit user goal provided.")
write_json(workspace.root / "01_sources" / "source_inventory.json", inventory)
write_json(workspace.root / "01_sources" / "dataset_inventory.json", {"items": inventory["datasets"]})
write_json(workspace.root / "01_sources" / "literature_inventory.json", {"items": inventory["literature_files"]})
```

Then write literature artifacts:

```python
clusters = {
    "robot_labor_reallocation": [item for item in inventory["literature_files"] if "robot" in item["name"].lower() or "automation" in item["name"].lower() or "Acemoglu" in item["name"]],
    "matching_and_mismatch": [item for item in inventory["reference_files"] if "匹配" in item["name"] or "mismatch" in item["name"].lower()],
}
write_json(workspace.root / "02_literature" / "literature_clusters.json", clusters)
write_text(workspace.root / "02_literature" / "core_literature_brief.md", "# Core Literature Brief\n\nThe first thesis run treats robot labor reallocation, matching-quality proxies, and skill-post mismatch as separate evidence layers.\n")
write_json(workspace.root / "02_literature" / "claim_evidence_map.json", {"claims": [{"claim": "Strict matching efficiency is not directly identified.", "evidence": ["05_reference/匹配效率概念与可测代理对照表.md"]}]})
```

Then write strategy artifacts:

```python
write_text(workspace.root / "03_strategy" / "research_plan.md", "# Research Plan\n\nPrimary question: how industrial robot exposure affects worker allocation outcomes, job-search frictions, and skill-post mismatch.\n")
write_text(workspace.root / "03_strategy" / "identification_plan.md", "# Identification Plan\n\nUse Bartik IV as the main identification strategy and keep weak-IV caveats explicit.\n")
write_text(workspace.root / "03_strategy" / "empirical_plan.md", "# Empirical Plan\n\nUse CFPS for outcome-layer results, CLDS for mechanism-layer checks, and CGSS for concept calibration.\n")
```

Then write modeling/results artifacts:

```python
write_json(workspace.root / "04_modeling" / "modeling_report.json", {"mode": mode, "detected_code_files": inventory["code_files"], "execution_policy": "audit existing scripts in dry-run"})
write_text(workspace.root / "04_modeling" / "diagnostics_report.md", "# Diagnostics Report\n\nDry-run records existing data, code, and result availability without mutating raw data.\n")
write_json(workspace.root / "05_results" / "results_index.json", {"items": inventory["results_files"]})
write_text(workspace.root / "05_results" / "table_plan.md", "# Table Plan\n\nUse existing indexed thesis tables before generating new tables.\n")
write_text(workspace.root / "05_results" / "figure_plan.md", "# Figure Plan\n\nUse existing thesis figures and figure scripts as first-class artifacts.\n")
```

Then write writing/review/final artifacts:

```python
write_text(workspace.root / "06_writing" / "paper_draft.md", "# Paper Draft\n\nThis draft is generated from inspected sources and preserves the matching-efficiency boundary.\n")
write_json(workspace.root / "06_writing" / "section_status.json", {"sections": [], "status": "drafted"})
write_text(workspace.root / "07_review" / "review_report.md", "# Review Report\n\nThe reviewer checks concept boundaries, weak-IV wording, literature support, and result-to-claim alignment.\n")
write_text(workspace.root / "07_review" / "revision_plan.md", "# Revision Plan\n\n1. Keep strict matching efficiency separate from measurable proxies.\n2. Attach each empirical claim to a result artifact.\n")
write_json(workspace.root / "07_review" / "reviewer_decision.json", {"reviewer": "ReviewerAgent", "target_agent": "WritingAgent", "decision": "revise_minor"})
write_text(workspace.root / "08_final" / "paper_draft.tex", "\\section{Draft}\\nGenerated draft placeholder for TeX export.\\n")
write_text(workspace.root / "08_final" / "paper_draft.docx", "DOCX export placeholder recorded by dry-run.\\n")
write_text(workspace.root / "08_final" / "formatting_report.md", "# Formatting Report\n\nDry-run recorded the Word export path. Live mode will call the formatter.\n")
```

Finally write handoff packets and manifest with `OrchestrationManifest`.

- [ ] **Step 5: Run full workbench test**

Run:

```bash
python3 -m unittest tests.test_full_workbench_run -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add Product/backend/orchestrator.py tests/test_orchestrator.py tests/test_full_workbench_run.py
git commit -m "feat: run full codex workbench pipeline"
```

## Task 6: Project Service And API Entrypoints

**Files:**

- Modify: `Product/backend/project_service.py`
- Modify: `Product/app.py`
- Modify: `tests/test_product_v1_local.py`

- [ ] **Step 1: Write failing API test**

Add this test to `tests/test_product_v1_local.py`:

```python
    def test_workbench_run_endpoint_creates_observable_run_folder(self) -> None:
        payload = {
            "slug": "v1-workbench-project",
            "title": "V1 Workbench Project",
            "project_root": str(self.project_dir),
            "language": "zh",
        }
        project = self.client.post("/api/v1/projects", json=payload).json()
        project_id = project["id"]

        response = self.client.post(
            f"/api/v1/projects/{project_id}/workbench-runs",
            json={"mode": "dry-run", "user_goal": "体验Codex内部CoPaper流程"},
        )
        self.assertEqual(response.status_code, 202, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "completed")
        self.assertTrue(body["run_root"].endswith(body["run_id"]))

        response = self.client.get(f"/api/v1/projects/{project_id}/workbench-runs/{body['run_id']}")
        self.assertEqual(response.status_code, 200, msg=response.text)
        self.assertEqual(response.json()["run_id"], body["run_id"])
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_product_v1_local.ProductV1LocalTests.test_workbench_run_endpoint_creates_observable_run_folder -v
```

Expected: FAIL with 404 because endpoint does not exist.

- [ ] **Step 3: Add service functions**

Add to `Product/backend/project_service.py`:

```python
def execute_workbench_run(project: dict[str, Any], mode: str, user_goal: str) -> dict[str, Any]:
    root = Path(project["project_root"])
    manifest = run_workbench(root, mode=mode, user_goal=user_goal)
    return manifest


def get_workbench_run(project: dict[str, Any], run_id: str) -> dict[str, Any]:
    root = Path(project["project_root"])
    for base in [root / "06_workspace" / "runs", root / "workspace" / "runs"]:
        manifest_path = base / run_id / "run_manifest.json"
        if manifest_path.exists():
            return json.loads(manifest_path.read_text(encoding="utf-8"))
    raise KeyError(run_id)
```

- [ ] **Step 4: Add FastAPI payload and routes**

Add to `Product/app.py`:

```python
class WorkbenchRunPayload(BaseModel):
    mode: str = "dry-run"
    user_goal: str = ""
```

Add routes:

```python
@app.post("/api/v1/projects/{project_id}/workbench-runs", status_code=202)
def api_v1_create_workbench_run(project_id: str, payload: WorkbenchRunPayload) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    return execute_workbench_run(project, payload.mode, payload.user_goal)


@app.get("/api/v1/projects/{project_id}/workbench-runs/{run_id}")
def api_v1_workbench_run(project_id: str, run_id: str) -> dict:
    try:
        project = get_project_by_id(PRODUCT_ROOT, REPO_ROOT, project_id)
    except KeyError:
        return error_response(404, "project_not_found", f"Project {project_id} does not exist.")
    try:
        return get_workbench_run(project, run_id)
    except KeyError:
        return error_response(404, "run_not_found", f"Workbench run {run_id} does not exist.")
```

- [ ] **Step 5: Run API test**

Run:

```bash
python3 -m unittest tests.test_product_v1_local.ProductV1LocalTests.test_workbench_run_endpoint_creates_observable_run_folder -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add Product/backend/project_service.py Product/app.py tests/test_product_v1_local.py
git commit -m "feat: expose workbench run api"
```

## Task 7: Codex CLI Entrypoint

**Files:**

- Create: `Product/cli.py`
- Test: `tests/test_cli_workbench.py`

- [ ] **Step 1: Write CLI failing test**

```python
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path("/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板")


class CliWorkbenchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="cli-workbench-"))
        self.root = self.temp_dir / "final"
        for rel in ["01_data", "02_code", "03_results", "04_paper/sections_v21", "05_reference", "06_workspace", "literature", "state"]:
            (self.root / rel).mkdir(parents=True)
        (self.root / "01_data" / "cfps_panel_v5.dta").write_bytes(b"stata-bytes")
        (self.root / "04_paper" / "sections_v21" / "00_摘要_中文.md").write_text("摘要", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_cli_runs_workbench_and_prints_manifest_json(self) -> None:
        result = subprocess.run(
            [
                "python3",
                "Product/cli.py",
                "run-workbench",
                "--project-root",
                str(self.root),
                "--mode",
                "dry-run",
                "--user-goal",
                "CLI smoke test",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "completed")
        self.assertTrue(Path(payload["run_root"]).exists())
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python3 -m unittest tests.test_cli_workbench -v
```

Expected: FAIL because `Product/cli.py` does not exist.

- [ ] **Step 3: Implement CLI**

```python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from Product.backend.orchestrator import run_workbench


def main() -> int:
    parser = argparse.ArgumentParser(description="Codex CoPaper internal workbench")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run-workbench")
    run.add_argument("--project-root", required=True)
    run.add_argument("--mode", default="dry-run", choices=["dry-run", "live"])
    run.add_argument("--user-goal", default="")

    args = parser.parse_args()
    if args.command == "run-workbench":
        manifest = run_workbench(Path(args.project_root).resolve(), mode=args.mode, user_goal=args.user_goal)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run CLI test**

Run:

```bash
python3 -m unittest tests.test_cli_workbench -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add Product/cli.py tests/test_cli_workbench.py
git commit -m "feat: add codex workbench cli"
```

## Task 8: Thesis Repository Smoke Run

**Files:**

- Create in real thesis repo during validation: `06_workspace/runs/<run_id>/...`
- Modify in product repo: `docs/workbench-a-experience-smoke.md`

- [ ] **Step 1: Run the CLI against the real thesis repository**

Run:

```bash
python3 Product/cli.py run-workbench \
  --project-root "/Users/mahaoxuan/Desktop/学术灵感项目_2026-04-07/final" \
  --mode dry-run \
  --user-goal "A体验：基于真实毕业论文仓库完成Codex内部CoPaper流程"
```

Expected: stdout is JSON with `"status": "completed"` and `"run_root"` under `/Users/mahaoxuan/Desktop/学术灵感项目_2026-04-07/final/06_workspace/runs/`.

- [ ] **Step 2: Verify required artifacts**

Run:

```bash
python3 - <<'PY'
import json
from pathlib import Path
root = Path("/Users/mahaoxuan/Desktop/学术灵感项目_2026-04-07/final/06_workspace/runs")
latest = max(root.iterdir(), key=lambda p: p.stat().st_mtime)
required = [
    "00_intake/project_profile.json",
    "01_sources/source_inventory.json",
    "02_literature/core_literature_brief.md",
    "03_strategy/research_plan.md",
    "04_modeling/modeling_report.json",
    "05_results/results_index.json",
    "06_writing/paper_draft.md",
    "07_review/review_report.md",
    "08_final/paper_draft.docx",
    "run_manifest.json",
]
missing = [rel for rel in required if not (latest / rel).exists()]
print(json.dumps({"latest": str(latest), "missing": missing}, ensure_ascii=False, indent=2))
raise SystemExit(1 if missing else 0)
PY
```

Expected: `missing` is an empty list.

- [ ] **Step 3: Write smoke report**

Create `docs/workbench-a-experience-smoke.md`:

```markdown
# Workbench A Experience Smoke Report

## Target

`/Users/mahaoxuan/Desktop/学术灵感项目_2026-04-07/final`

## Command

`python3 Product/cli.py run-workbench --project-root "/Users/mahaoxuan/Desktop/学术灵感项目_2026-04-07/final" --mode dry-run --user-goal "A体验：基于真实毕业论文仓库完成Codex内部CoPaper流程"`

## Result

The dry run completed and wrote an inspectable run folder under `06_workspace/runs`.

## Acceptance Evidence

- `00_intake/project_profile.json`
- `01_sources/source_inventory.json`
- `02_literature/core_literature_brief.md`
- `03_strategy/research_plan.md`
- `04_modeling/modeling_report.json`
- `05_results/results_index.json`
- `06_writing/paper_draft.md`
- `07_review/review_report.md`
- `08_final/paper_draft.docx`
- `run_manifest.json`

## Boundary

This is the first A experience. It proves the Codex-internal product flow and run contract. It does not claim final academic quality until the reviewer loop and real empirical execution are tightened.
```

- [ ] **Step 4: Commit product-side smoke report**

```bash
git add docs/workbench-a-experience-smoke.md
git commit -m "docs: record thesis workbench smoke run"
```

## Task 9: Regression Suite

**Files:**

- Modify only if needed: test files touched above

- [ ] **Step 1: Run focused tests**

Run:

```bash
python3 -m unittest \
  tests.test_workbench_paths \
  tests.test_project_adapter \
  tests.test_evidence_inventory \
  tests.test_orchestrator \
  tests.test_full_workbench_run \
  tests.test_product_v1_local \
  tests.test_cli_workbench \
  -v
```

Expected: all tests pass.

- [ ] **Step 2: Run existing run-paper test**

Run:

```bash
python3 -m unittest tests.test_run_paper -v
```

Expected: PASS or a documented environment-specific failure. If it fails because of the existing local runner issue, record the failure text in the final report and verify the CLI smoke run instead.

- [ ] **Step 3: Check git status**

Run:

```bash
git status --short
```

Expected: only intended untracked historical prototype files remain. Newly created implementation files should be tracked in commits from Tasks 1-8.

## Self-Review Checklist

- Spec coverage:
  - Run folder contract: Task 1.
  - Project adapter: Task 2.
  - Evidence inventory: Task 3.
  - Stable handoff schema: Task 4.
  - Supervisor and full agent chain: Task 5.
  - Codex-internal API entrypoint: Task 6.
  - Codex-first CLI experience: Task 7.
  - Real thesis A experience: Task 8.
  - Regression tests: Task 9.
- No raw data mutation:
  - Evidence scans read files and write only under run folders.
- Writer and reviewer separation:
  - Task 5 asserts reviewer is not `WritingAgent`.
- A/B boundary:
  - Thesis profile is the first adapter profile, not the whole system.
- Placeholder scan:
  - The plan contains dry-run placeholder document content only where the implementation intentionally writes a dry-run marker file. It does not leave implementation steps undefined.

