from __future__ import annotations

import csv
import importlib.util
import json
import os
import shutil
import socket
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import urlopen

from .evidence import build_evidence_inventory
from .orchestrator import artifact_rel, write_json, write_text
from .project_adapter import detect_project_profile
from .workbench_paths import create_run_workspace


CAPABILITY_IDS = [
    "local_data",
    "statspai",
    "cnki",
    "web_search",
    "agentmemory",
    "llm_supervisor",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_auto_research(
    project_root: Path,
    topic: str,
    mode: str = "auto",
    max_depth: int = 2,
    max_iterations: int = 5,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    if not topic.strip():
        raise ValueError("topic is required")

    run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:6]}"
    workspace = create_run_workspace(project_root, run_id)
    run_root = workspace.root
    profile = detect_project_profile(project_root)
    inventory = build_evidence_inventory(project_root, profile)
    capability_status = detect_capabilities(project_root, inventory, mode=mode)
    literature_clues = build_literature_clues(project_root, inventory, topic)
    variable_candidates = build_variable_candidates(project_root, inventory, topic)
    method_candidates = build_method_candidates(topic, variable_candidates)
    evidence_gaps = build_evidence_gaps(capability_status, method_candidates)
    artifacts: list[str] = []

    def record(path: Path) -> Path:
        artifacts.append(artifact_rel(path, project_root))
        return path

    research_intent = {
        "topic": topic,
        "status": "exploratory",
        "mode": mode,
        "execution_policy": "best_available" if mode == "auto" else "dry_run",
        "max_depth": max_depth,
        "max_iterations": max_iterations,
        "evidence_level": "local_file",
        "can_promote": False,
        "created_at": utc_now(),
    }
    recursive_search_plan = {
        "topic": topic,
        "status": "needs_human_review",
        "max_depth": max_depth,
        "max_iterations": max_iterations,
        "strategy": [
            "从题目抽取核心概念和中文检索词",
            "用本地文献、CNKI、Web、Zotero 生成 LiteratureClue 候选",
            "从候选文献中提取变量、数据源、方法和识别风险",
            "让缺失证据触发下一轮数据、文献或方法搜索",
        ],
        "enabled_sources": [
            cap["id"] for cap in capability_status if cap["status"] in {"available", "requires_manual_assist"}
        ],
        "blocked_sources": [cap for cap in capability_status if cap["status"] not in {"available", "requires_manual_assist"}],
        "evidence_level": "local_file",
        "can_promote": False,
    }
    artifact_policy = {
        "status": "needs_human_review",
        "labels": ["exploratory", "draft", "needs_human_review"],
        "can_promote": False,
        "formal_state_write_policy": "do_not_overwrite_variable_roles_design_spec_or_run_plan",
    }

    write_json(record(run_root / "00_intake" / "research_intent.json"), research_intent)
    write_json(record(run_root / "01_sources" / "source_inventory.json"), inventory)
    write_json(record(run_root / "01_sources" / "dataset_inventory.json"), {"items": inventory["datasets"]})
    write_json(record(run_root / "01_sources" / "literature_inventory.json"), {"items": literature_clues})
    write_json(record(run_root / "01_sources" / "recursive_search_plan.json"), recursive_search_plan)
    write_json(record(run_root / "03_strategy" / "variable_candidates.json"), variable_candidates)
    write_json(record(run_root / "03_strategy" / "method_candidates.json"), {"items": method_candidates})
    write_json(record(run_root / "03_strategy" / "evidence_gaps.json"), {"items": evidence_gaps})
    write_jsonl(record(run_root / "02_literature" / "literature_clues.jsonl"), literature_clues)
    write_jsonl(project_root / "state" / "orchestration" / "literature_clues.jsonl", literature_clues, append=True)
    write_text(record(run_root / "06_writing" / "research_report.md"), render_research_report(topic, capability_status, variable_candidates, method_candidates, evidence_gaps))
    write_text(record(run_root / "06_writing" / "paper_draft_exploratory.md"), render_exploratory_draft(topic, variable_candidates, method_candidates))

    manifest = {
        "run_id": run_id,
        "run_root": str(run_root),
        "status": "completed",
        "mode": mode,
        "execution_policy": research_intent["execution_policy"],
        "research_intent": research_intent,
        "capability_status": capability_status,
        "artifact_policy": artifact_policy,
        "artifacts": artifacts,
        "created_at": research_intent["created_at"],
        "evidence_level": "local_file",
        "can_promote": False,
    }
    write_json(record(run_root / "run_manifest.json"), manifest)
    return manifest


def detect_capabilities(project_root: Path, inventory: dict[str, Any], mode: str) -> list[dict[str, Any]]:
    return [
        capability("local_data", "available" if inventory["datasets"] else "unavailable", "local datasets detected" if inventory["datasets"] else "no local dataset files detected"),
        capability("statspai", "available" if importlib.util.find_spec("statspai") else "unavailable", "statspai module importable" if importlib.util.find_spec("statspai") else "statspai module not found"),
        detect_cnki_capability(mode),
        detect_web_capability(mode),
        capability("agentmemory", "available" if shutil.which("agentmemory") else "unavailable", "agentmemory executable found" if shutil.which("agentmemory") else "agentmemory executable not found"),
        detect_llm_supervisor(project_root),
    ]


def capability(capability_id: str, status: str, reason: str) -> dict[str, Any]:
    return {
        "id": capability_id,
        "status": status,
        "reason": reason,
        "evidence_level": "local_file",
        "can_promote": False,
    }


def detect_cnki_capability(mode: str) -> dict[str, Any]:
    if mode == "dry-run":
        return capability("cnki", "skipped_by_policy", "dry-run mode does not open browser automation")
    try:
        with urlopen("http://127.0.0.1:9222/json/version", timeout=0.3) as response:
            if response.status == 200:
                return capability("cnki", "requires_manual_assist", "Chrome DevTools endpoint detected; CNKI login/captcha still require manual handling")
    except Exception:
        pass
    return capability("cnki", "blocked_by_browser_session", "Chrome DevTools endpoint not detected; CNKI remains manual-assisted")


def detect_web_capability(mode: str) -> dict[str, Any]:
    if mode == "dry-run":
        return capability("web_search", "skipped_by_policy", "dry-run mode does not perform network search")
    try:
        with socket.create_connection(("www.google.com", 443), timeout=0.6):
            return capability("web_search", "available", "network connectivity check succeeded")
    except Exception:
        return capability("web_search", "unavailable", "network connectivity check failed")


def detect_llm_supervisor(project_root: Path) -> dict[str, Any]:
    enabled = os.environ.get("EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC") == "1"
    if enabled and shutil.which("codex"):
        return capability("llm_supervisor", "available", "local Codex execution enabled and codex executable found")
    if enabled:
        return capability("llm_supervisor", "provider_error", "local Codex execution enabled but codex executable not found")
    return capability("llm_supervisor", "unavailable", "EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC is not enabled")


def build_literature_clues(project_root: Path, inventory: dict[str, Any], topic: str) -> list[dict[str, Any]]:
    clues: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for item in inventory["literature_files"] + inventory["reference_files"]:
        path = item.get("path", "")
        if not path or path in seen_paths:
            continue
        seen_paths.add(path)
        clues.append(
            {
                "id": f"lit_{uuid.uuid4().hex[:10]}",
                "source": "local_file",
                "source_type": "literature_clue",
                "topic": topic,
                "title": Path(path).stem,
                "path": path,
                "suffix": item.get("suffix", ""),
                "evidence_level": "local_file",
                "status": "candidate",
                "can_promote": False,
                "access_status": "metadata_only",
                "relevance_rationale": "本地文献或参考材料文件，第一版仅登记为候选线索。",
            }
        )
    if clues:
        return clues
    return [
        {
            "id": f"lit_{uuid.uuid4().hex[:10]}",
            "source": "topic_seed",
            "source_type": "literature_clue",
            "topic": topic,
            "title": topic,
            "evidence_level": "mock",
            "status": "candidate",
            "can_promote": False,
            "access_status": "search_required",
            "relevance_rationale": "暂无本地文献文件；该线索只是题目种子，不能作为论文证据。",
        }
    ]


def build_variable_candidates(project_root: Path, inventory: dict[str, Any], topic: str) -> dict[str, Any]:
    dataset = inventory["datasets"][0] if inventory["datasets"] else {}
    columns = read_csv_columns(project_root / dataset.get("path", "")) if dataset else []
    candidates = {
        "status": "needs_human_review",
        "evidence_level": "local_file" if dataset else "mock",
        "can_promote": False,
        "dataset": dataset,
        "columns": columns,
        "roles": {
            "outcome_candidates": infer_columns(columns, ["wage", "income", "earn", "收入", "工资"]),
            "treatment_candidates": infer_columns(columns, ["ai", "robot", "treat", "policy", "人工智能", "机器人"]),
            "control_candidates": infer_columns(columns, ["age", "edu", "gender", "experience", "年龄", "教育"]),
            "instrument_candidates": [],
        },
        "rationale": "变量角色为自动候选，必须人工确认后才可进入正式 VariableRoleSet。",
    }
    return candidates


def read_csv_columns(path: Path) -> list[str]:
    if not path.exists() or path.suffix.lower() != ".csv":
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return next(csv.reader(handle), [])
    except Exception:
        return []


def infer_columns(columns: list[str], tokens: list[str]) -> list[str]:
    lowered = [(column, column.lower()) for column in columns]
    return [column for column, lower in lowered if any(token.lower() in lower or token in column for token in tokens)]


def build_method_candidates(topic: str, variable_candidates: dict[str, Any]) -> list[dict[str, Any]]:
    roles = variable_candidates.get("roles", {})
    has_outcome = bool(roles.get("outcome_candidates"))
    has_treatment = bool(roles.get("treatment_candidates"))
    return [
        {
            "id": "ols_baseline",
            "method": "OLS",
            "status": "candidate" if has_outcome and has_treatment else "blocked",
            "purpose": "建立探索性基准相关关系，不宣称因果识别。",
            "evidence_level": variable_candidates.get("evidence_level", "mock"),
            "can_promote": False,
            "requirements": ["确认因变量", "确认处理变量", "确认控制变量", "检查缺失值和样本定义"],
        },
        {
            "id": "identification_upgrade",
            "method": "DID/IV/RDD/PSM/DML",
            "status": "needs_evidence",
            "purpose": "根据题目语义和数据结构选择更强识别策略。",
            "evidence_level": "local_file",
            "can_promote": False,
            "requirements": ["政策冲击或处理时点", "工具变量或断点", "可比对照组", "平行趋势或重叠假设证据"],
        },
    ]


def build_evidence_gaps(capability_status: list[dict[str, Any]], method_candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gaps = [
        {
            "id": f"capability_{cap['id']}",
            "label": f"{cap['id']} capability is not fully available",
            "status": cap["status"],
            "reason": cap["reason"],
            "evidence_level": cap["evidence_level"],
            "can_promote": False,
        }
        for cap in capability_status
        if cap["status"] not in {"available", "requires_manual_assist"}
    ]
    for method in method_candidates:
        if method["status"] != "candidate":
            gaps.append(
                {
                    "id": f"method_{method['id']}",
                    "label": f"{method['method']} requires additional evidence",
                    "status": method["status"],
                    "requirements": method["requirements"],
                    "evidence_level": method["evidence_level"],
                    "can_promote": False,
                }
            )
    return gaps


def render_research_report(
    topic: str,
    capability_status: list[dict[str, Any]],
    variable_candidates: dict[str, Any],
    method_candidates: list[dict[str, Any]],
    evidence_gaps: list[dict[str, Any]],
) -> str:
    capabilities = "\n".join(f"- {cap['id']}: {cap['status']} ({cap['reason']})" for cap in capability_status)
    methods = "\n".join(f"- {item['method']}: {item['status']} - {item['purpose']}" for item in method_candidates)
    gaps = "\n".join(f"- {gap['id']}: {gap.get('status')} {gap.get('reason', '')}" for gap in evidence_gaps) or "- 暂无阻塞，但仍需人工审阅。"
    return (
        f"# Auto Research Report\n\n"
        f"## 研究题目\n\n{topic}\n\n"
        f"## 能力状态\n\n{capabilities}\n\n"
        f"## 变量候选\n\n```json\n{json.dumps(variable_candidates, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## 方法候选\n\n{methods}\n\n"
        f"## 缺失证据\n\n{gaps}\n\n"
        f"## 证据边界\n\n本报告为 exploratory / needs_human_review，不能直接作为正式论文证据。\n"
    )


def render_exploratory_draft(
    topic: str,
    variable_candidates: dict[str, Any],
    method_candidates: list[dict[str, Any]],
) -> str:
    method_names = "、".join(item["method"] for item in method_candidates)
    return (
        f"# Exploratory Paper Draft\n\n"
        f"## 暂定题目\n\n{topic}\n\n"
        f"## 研究状态\n\n本文档由 Auto Mode 生成，状态为 draft / exploratory / needs_human_review。\n\n"
        f"## 数据与变量\n\n当前变量角色仍是候选：`{json.dumps(variable_candidates.get('roles', {}), ensure_ascii=False)}`。\n\n"
        f"## 方法路线\n\n候选方法包括：{method_names}。所有因果解释必须等待人工确认和真实执行证据。\n"
    )


def write_jsonl(path: Path, rows: list[dict[str, Any]], append: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with path.open(mode, encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
