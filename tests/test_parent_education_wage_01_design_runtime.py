from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DESIGN_FILES = [
    "research_design.md",
    "causal_question.yaml",
    "design_risk.md",
]

FORBIDDEN_STALE_TERMS = [
    "robot",
    "机器人",
    "bartik_iv",
    "ln_robot",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_01_design_entry_files_exist_for_parent_education_wage() -> None:
    """BDD 行为 1：父母教育题目必须落成三份 01_design 入口文件。"""
    missing = [path for path in DESIGN_FILES if not (ROOT / path).exists()]
    assert missing == []


def test_causal_question_declares_machine_readable_design_contract() -> None:
    """BDD 行为 2：后续 agent 能直接读取处理、结果、样本、方法和数据源。"""
    text = read("causal_question.yaml")
    required_terms = [
        "treatment:",
        "outcome:",
        "population:",
        "primary_design:",
        "data_source:",
        "parental_education_years",
        "ln_wage",
        "CFPS",
    ]
    missing = [term for term in required_terms if term not in text]
    assert missing == []


def test_design_outputs_do_not_reuse_robot_topic_contamination() -> None:
    """BDD 行为 3：新题目入口不能沿用旧的工业机器人变量。"""
    combined = "\n".join(read(path) for path in DESIGN_FILES)
    leaked = [term for term in FORBIDDEN_STALE_TERMS if term in combined]
    assert leaked == []


def test_artifact_registry_marks_01_design_outputs_present() -> None:
    """BDD 行为 4：运行时 registry 必须登记 01_design 已完成。"""
    registry = read("Tasks/artifact-registry.md")
    expected_rows = [
        "| 01 | research_design.md | research_design.md | present |",
        "| 01 | causal_question.yaml | causal_question.yaml | present |",
        "| 01 | design_risk.md | design_risk.md | present |",
    ]
    missing = [row for row in expected_rows if row not in registry]
    assert missing == []


def test_router_reports_git_canonical_artifact_registry_path() -> None:
    """BDD 行为 4 扩展：报告路径必须使用 Git 中真实存在的 Tasks/ 目录。"""
    subprocess.run(
        ["python3", "scripts/21_route_next_workflow.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    report = read("artifacts/workflow_router_report.md")
    assert "Artifact registry: `Tasks/artifact-registry.md`" in report
    assert "Artifact registry: `tasks/artifact-registry.md`" not in report


def test_router_advances_from_design_to_literature() -> None:
    """BDD 行为 5：完成 01_design 后，下一步必须进入 02_literature。"""
    completed = subprocess.run(
        ["python3", "scripts/21_route_next_workflow.py"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "NEXT 02_literature" in completed.stdout
