from __future__ import annotations

import json
import re
import shutil
import subprocess
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from .evidence import build_evidence_inventory
from .orchestration_schema import HandoffPacket, OrchestrationManifest, ReviewPacket
from .project_adapter import detect_project_profile
from .run_event_bus import drop_queue, emit_event
from .workbench_paths import create_run_workspace


# ── Checkpoint data models ───────────────────────────────────────────────────

class CheckpointStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


@dataclass
class Checkpoint:
    id: str
    stage: str
    agent_name: str
    title: str
    description: str
    payload: dict = field(default_factory=dict)
    status: CheckpointStatus = CheckpointStatus.PENDING
    user_feedback: str = ""
    created_at: str = ""
    resolved_at: str = ""


# ── HITL stage configuration ─────────────────────────────────────────────────

HITL_STAGES: dict[str, dict[str, str]] = {
    "02_literature": {
        "title": "文献综述确认",
        "description": "请确认文献综述框架是否合理，是否覆盖了核心文献。",
    },
    "03_strategy": {
        "title": "识别策略确认",
        "description": "请确认识别策略（工具变量、固定效应、聚类方式）设定是否合理。",
    },
    "04_modeling": {
        "title": "建模结果确认",
        "description": "请确认回归结果、显著性和系数方向是否符合预期。",
    },
    "06_writing": {
        "title": "写作内容确认",
        "description": "请确认生成的正文段落和结果表格是否准确。",
    },
}


# ── Checkpoint persistence helpers ───────────────────────────────────────────

def _checkpoint_state_path(project_root: Path) -> Path:
    return project_root / "state" / "product" / "checkpoints.json"


def load_checkpoints(project_root: Path) -> list[dict]:
    path = _checkpoint_state_path(project_root)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def save_checkpoint(project_root: Path, checkpoint: dict) -> None:
    checkpoints = load_checkpoints(project_root)
    existing = [c for c in checkpoints if c["id"] != checkpoint["id"]]
    existing.append(checkpoint)
    _checkpoint_state_path(project_root).parent.mkdir(parents=True, exist_ok=True)
    _checkpoint_state_path(project_root).write_text(
        json.dumps(existing, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def resolve_checkpoint(
    project_root: Path,
    checkpoint_id: str,
    status: str,
    user_feedback: str = "",
) -> dict:
    checkpoints = load_checkpoints(project_root)
    for cp in checkpoints:
        if cp["id"] == checkpoint_id:
            cp["status"] = status
            cp["user_feedback"] = user_feedback
            cp["resolved_at"] = utc_now()
            _checkpoint_state_path(project_root).write_text(
                json.dumps(checkpoints, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            run_id = cp.get("payload", {}).get("run_id")
            if run_id:
                emit_event(
                    run_id,
                    "checkpoint.resolved",
                    stage=cp.get("stage", ""),
                    agent_name=cp.get("agent_name", ""),
                    payload={
                        "checkpoint_id": checkpoint_id,
                        "status": status,
                        "user_feedback": user_feedback,
                    },
                )
            return {"resolved": True, "checkpoint": cp}
    return {"resolved": False, "reason": "checkpoint_not_found"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Governance helpers ───────────────────────────────────────────────────────

def _resolve_product_root() -> Path:
    """Return the Product package root (where state/product/ lives)."""
    return Path(__file__).resolve().parent.parent


def _resolve_project_id(profile: dict[str, Any]) -> str:
    """Derive project_id from profile or fall back to registry default."""
    existing_id = profile.get("id")
    if existing_id:
        return existing_id
    slug = profile.get("slug", "")
    if slug:
        return f"proj_{slug.replace('-', '_')}"
    title = profile.get("title", "")
    if title:
        safe_title = re.sub(r"[^\w\s-]", "", title).strip().lower()[:30]
        safe_title = re.sub(r"[-\s]+", "_", safe_title)
        if safe_title:
            return f"proj_{safe_title}"
    return "proj_undergraduate_thesis"


def _resolve_agent_id(agent_role: str) -> str:
    """Build the canonical agent_id used in identity/permission registries."""
    return f"agent_{agent_role}_01"


def _estimate_llm_cost(provider_id: str, model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate LLM cost in USD based on provider and token counts."""
    pricing = {
        "openrouter": {
            "anthropic/claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
            "anthropic/claude-opus-4-6": {"input": 15.0, "output": 75.0},
            "anthropic/claude-haiku-4-5-20251001": {"input": 0.25, "output": 1.25},
            "openai/gpt-4o": {"input": 2.5, "output": 10.0},
            "openai/gpt-4o-mini": {"input": 0.15, "output": 0.6},
            "default": {"input": 3.0, "output": 15.0},
        },
        "kimi-code": {"default": {"input": 0.5, "output": 2.0}},
        "kimi-code-anthropic-token": {"default": {"input": 0.5, "output": 2.0}},
        "moonshot-kimi": {"default": {"input": 0.5, "output": 2.0}},
    }
    provider_pricing = pricing.get(provider_id, pricing["openrouter"])
    model_pricing = provider_pricing.get(
        model,
        provider_pricing.get("default", {"input": 3.0, "output": 15.0}),
    )
    input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
    output_cost = (output_tokens / 1_000_000) * model_pricing["output"]
    return round(input_cost + output_cost, 6)


def _agent_role_from_display_name(display_name: str) -> str:
    """Map display names like 'LiteratureAgent' to roles like 'literature_agent'."""
    mapping = {
        "PreparationAgent": "supervisor",
        "LiteratureAgent": "literature_agent",
        "ResearchStrategistAgent": "identification_agent",
        "ModelingAgent": "modeling_agent",
        "VisualizationAgent": "data_agent",
        "WritingAgent": "writing_agent",
        "ReviewerAgent": "reviewer_agent",
        "FormatterAgent": "export_agent",
    }
    return mapping.get(display_name, display_name.replace("Agent", "").lower())


def _action_for_stage(stage: str) -> str:
    """Map stage to the permission action catalog entry."""
    mapping = {
        "00_intake": "project.read",
        "01_sources": "project.read",
        "02_literature": "source.inspect",
        "03_strategy": "project.read",
        "04_modeling": "method.execute",
        "05_results": "artifact.read",
        "06_writing": "artifact.write",
        "07_review": "artifact.read",
        "08_final": "export.docx",
    }
    return mapping.get(stage, "project.read")


def _capability_id_for_stage(stage: str) -> str:
    """Map stage to a capability ID for cost tracking."""
    mapping = {
        "00_intake": "cap_build_evidence",
        "01_sources": "cap_build_evidence",
        "02_literature": "cap_build_evidence",
        "03_strategy": "cap_build_evidence",
        "04_modeling": "cap_statspai_ols",
        "05_results": "cap_build_evidence",
        "06_writing": "cap_export_docx",
        "07_review": "cap_build_evidence",
        "08_final": "cap_export_docx",
    }
    return mapping.get(stage, "cap_build_evidence")


def _run_stage(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    run_id: str,
    stage: str,
    agent_display_name: str,
    stage_func: Callable[[], Any],
) -> Any:
    """Execute a single stage with governance hooks (identity, permission, capability, cost).

    BEFORE execution:
      1. Verify agent identity is registered.
      2. Check permission for the action.
      3. Resolve capability.
    DURING execution:
      4. Start cost event.
    AFTER execution:
      5. Finish cost event with wall time.
    """
    # Lazy imports to avoid circular dependency with project_service
    from . import identity_service
    from . import permission_service
    from . import capability_registry
    from . import cost_service

    agent_role = _agent_role_from_display_name(agent_display_name)
    agent_id = _resolve_agent_id(agent_role)
    action = _action_for_stage(stage)
    cap_id = _capability_id_for_stage(stage)

    # 1. Identity check
    identity_result = identity_service.get_project_identity(product_root, repo_root, project_id)
    identities = identity_result.get("identity", {}).get("identities", [])
    agent_registered = any(agent.get("id") == agent_id for agent in identities)
    if not agent_registered:
        # Auto-initialize identities if empty
        if identity_result.get("identity", {}).get("version", 0) == 0:
            identity_service.init_project_identities(product_root, repo_root, project_id)
            identity_result = identity_service.get_project_identity(product_root, repo_root, project_id)
            identities = identity_result.get("identity", {}).get("identities", [])
            agent_registered = any(agent.get("id") == agent_id for agent in identities)

    # 2. Permission check
    perm_result = permission_service.check_permission(product_root, repo_root, project_id, agent_id, action)
    if not perm_result.get("allowed", False):
        # Auto-initialize permissions if empty
        if perm_result.get("reason") == "permission_registry_not_initialized":
            permission_service.init_project_permissions(product_root, repo_root, project_id)
            perm_result = permission_service.check_permission(product_root, repo_root, project_id, agent_id, action)

    # 3. Capability resolution
    caps_result = capability_registry.get_project_capabilities(product_root, repo_root, project_id)
    capabilities = caps_result.get("capability", {}).get("capabilities", [])
    resolved_cap = capability_registry.find_capability_by_id(capabilities, cap_id)
    if resolved_cap is None:
        # Fall back to builtin capability if statspai not indexed
        resolved_cap = capability_registry.find_capability_by_id(capabilities, "cap_build_evidence")
    effective_cap_id = resolved_cap.get("id", cap_id) if resolved_cap else cap_id

    emit_event(
        run_id,
        "stage.start",
        stage=stage,
        agent_name=agent_display_name,
        payload={"stage": stage, "agent_name": agent_display_name, "action": action, "capability_id": effective_cap_id},
    )

    # 4. Start cost event
    event_id = cost_service.start_cost_event(
        project_root=repo_root,
        project_id=project_id,
        workflow_id=run_id,
        task_id=f"{run_id}_{stage}",
        actor_id=agent_id,
        capability_id=effective_cap_id,
        event_type="agent_task_run",
    )

    # Execute stage with wall-clock timing
    start_ts = time.perf_counter()
    status = "succeeded"
    try:
        result = stage_func()
    except Exception as exc:
        status = "failed"
        emit_event(
            run_id,
            "stage.output",
            stage=stage,
            agent_name=agent_display_name,
            payload={"source": "log", "chunk": f"Error: {exc}"},
        )
        raise
    finally:
        wall_seconds = time.perf_counter() - start_ts
        # 5. Finish cost event
        cost_service.finish_cost_event(
            project_root=repo_root,
            event_id=event_id,
            status=status,
            wall_seconds=round(wall_seconds, 3),
        )
        # 6. Git experiment log
        try:
            from . import git_experiment_logger
            git_experiment_logger.commit_stage(
                project_root=repo_root,
                stage=stage,
                agent_name=agent_display_name,
                status=status,
            )
        except Exception:
            # Git logging is best-effort; don't fail the stage if git fails
            pass
        emit_event(
            run_id,
            "stage.complete",
            stage=stage,
            agent_name=agent_display_name,
            payload={"stage": stage, "status": status, "wall_seconds": round(wall_seconds, 3)},
        )

    # ── HITL checkpoint creation ───────────────────────────────────────────
    hitl_config = HITL_STAGES.get(stage)
    if hitl_config:
        checkpoint_id = f"checkpoint_{uuid.uuid4().hex[:12]}"
        checkpoint = Checkpoint(
            id=checkpoint_id,
            stage=stage,
            agent_name=agent_display_name,
            title=hitl_config["title"],
            description=hitl_config["description"],
            payload={"status": status, "run_id": run_id},
            status=CheckpointStatus.PENDING,
            created_at=utc_now(),
        )
        save_checkpoint(repo_root, checkpoint.__dict__)
        emit_event(
            run_id,
            "checkpoint.pending",
            stage=stage,
            agent_name=agent_display_name,
            payload={
                "checkpoint_id": checkpoint_id,
                "stage": stage,
                "title": hitl_config["title"],
                "description": hitl_config["description"],
            },
        )

    return result


def _load_state_json(project_root: Path, filename: str) -> dict[str, Any] | None:
    path = project_root / "state" / "product" / filename
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def _build_modeling_prompt(
    design_spec: dict[str, Any] | None,
    research_plan_text: str,
    identification_plan_text: str,
    empirical_plan_text: str,
    inventory: dict[str, Any],
) -> str:
    """Build LLM prompt for the modeling stage."""
    rq = (design_spec or {}).get("research_question", "未指定")
    variables = (design_spec or {}).get("variables", {})
    model = (design_spec or {}).get("model", {})
    id_strategy = (design_spec or {}).get("identification_strategy", {})
    dataset_path = (design_spec or {}).get("dataset_path", "未指定")

    outcome = ", ".join(variables.get("outcome", [])) or "未指定"
    treatment = ", ".join(variables.get("treatment", [])) or "未指定"
    controls = ", ".join(variables.get("controls", [])) or "未指定"
    instruments = ", ".join(variables.get("instruments", [])) or "无"
    fe = ", ".join(variables.get("fixed_effects", [])) or "无"
    cluster = ", ".join(variables.get("cluster_by", [])) or "无"
    formula = model.get("formula", "未指定")
    estimator = id_strategy.get("name", "ols")

    datasets = inventory.get("datasets", [])
    data_info = f"检测到 {len(datasets)} 个数据文件: " + ", ".join([d.get("name", "") for d in datasets[:5]]) if datasets else "未检测到数据文件"

    prompt = f"""你是一位实证经济学建模专家。请根据以下研究设计，生成建模策略报告（Markdown格式）。

## 研究问题
{rq}

## 变量设计
- 结果变量 (outcome): {outcome}
- 处理变量 (treatment): {treatment}
- 控制变量 (controls): {controls}
- 工具变量 (instruments): {instruments}
- 固定效应 (fixed_effects): {fe}
- 聚类层级 (cluster_by): {cluster}

## 识别策略
- 方法: {estimator}
- 公式: `{formula}`
- 说明: {id_strategy.get("summary", "未说明")}

## 数据信息
- 数据集路径: {dataset_path}
- {data_info}

## 研究计划摘要
{research_plan_text[:800] if len(research_plan_text) > 800 else research_plan_text}

## 识别计划摘要
{identification_plan_text[:800] if len(identification_plan_text) > 800 else identification_plan_text}

## 任务要求
请按以下结构输出建模报告：

### 1. 研究设计评估
评估当前变量选择和识别策略的合理性。

### 2. 潜在内生性问题
列出主要的内生性威胁（遗漏变量、样本选择、反向因果等）。

### 3. 模型建议
给出具体的回归执行建议，包括：
- 是否需要稳健标准误
- 是否需要固定效应
- 是否需要工具变量
- 是否需要异质性分析

### 4. 稳健性检验建议
列出应进行的稳健性检验。

### 5. 执行摘要
用1-2段话总结核心建模策略。
"""
    return prompt


def _call_llm_for_modeling(prompt: str) -> tuple[str, dict[str, Any]]:
    """Call LLM for modeling report. Returns (text, metadata)."""
    # Lazy import to avoid circular dependency
    from .llm_client import chat_completion_with_fallback

    messages = [
        {"role": "system", "content": "你是一位实证经济学研究方法论专家，擅长因果推断和计量经济学建模。"},
        {"role": "user", "content": prompt},
    ]

    try:
        text, metadata = chat_completion_with_fallback(
            messages,
            attempts=(
                {"provider_id": "kimi-code-anthropic-token", "model": "kimi-for-coding", "env": "ANTHROPIC_AUTH_TOKEN"},
                {"provider_id": "kimi-code", "model": "kimi-for-coding", "env": "KIMI_CODE_API_KEY"},
                {"provider_id": "openrouter", "model": "anthropic/claude-sonnet-4-6", "env": "OPENROUTER_API_KEY"},
            ),
            temperature=0.3,
        )
        return text, metadata
    except Exception as exc:
        # Return a graceful fallback with error info
        error_text = f"""# 建模报告（LLM调用失败）

## 错误信息
LLM调用失败: {exc}

## 手动检查清单
- [ ] 确认研究问题与变量设计一致
- [ ] 检查识别策略是否满足排他性约束
- [ ] 验证数据覆盖范围与样本量
- [ ] 确认控制变量不包含 collider
"""
        return error_text, {"error": str(exc), "provider_id": "none"}


def _execute_modeling_with_backend(
    project_root: Path,
    run_id: str,
    design_spec: dict[str, Any] | None,
    run_plan: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Execute StatsPAI modeling if design_spec and run_plan are available."""
    if not design_spec or not run_plan:
        return None

    # Lazy import to avoid circular dependency
    from .execution_backend_service import execute_agent_task_with_backend

    dataset_path = design_spec.get("dataset_path") or run_plan.get("dataset_path")
    if not dataset_path:
        return None

    # Build a task dict compatible with execute_agent_task_with_backend
    task = {
        "id": f"modeling_{run_id}",
        "title": "Modeling Execution",
        "role": "modeling_agent",
        "status": "reviewed_for_dispatch",
        "selected_backend": {
            "id": "statspai",
            "label": "StatsPAI",
            "evidence_level": "local_execution",
        },
        "method_id": (run_plan.get("tasks", [{}])[0].get("estimator") or "ols"),
    }

    try:
        result = execute_agent_task_with_backend(task, project_root)
        return result
    except Exception as exc:
        return {"status": "failed", "error": str(exc), "engine": "statspai"}


def read_json(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def read_text(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def schedule_drop_run_queue(run_id: str) -> None:
    timer = threading.Timer(60.0, drop_queue, args=(run_id,))
    timer.daemon = True
    timer.start()


def summarize_list(items: list[dict[str, Any]], key: str = "name", limit: int = 12) -> str:
    values = [str(item.get(key, "")) for item in items[:limit] if item.get(key)]
    return "\n".join(f"- {value}" for value in values) if values else "- No local files detected."


def artifact_rel(path: Path, project_root: Path) -> str:
    return str(path.relative_to(project_root))


def write_handoff(
    run_id: str,
    run_root: Path,
    project_root: Path,
    agent: str,
    stage: str,
    inputs: list[Path],
    outputs: list[Path],
    claims: list[str],
    risks: list[str],
    next_agent: str | None,
    metadata: dict[str, Any] | None = None,
) -> HandoffPacket:
    packet = HandoffPacket(
        run_id=run_id,
        agent=agent,
        stage=stage,
        inputs=[artifact_rel(path, project_root) for path in inputs],
        outputs=[artifact_rel(path, project_root) for path in outputs],
        claims=claims,
        risks=risks,
        next_agent=next_agent,
        metadata=metadata or {},
    )
    safe_name = agent.replace("Agent", "").lower()
    write_json(run_root / stage / f"{safe_name}_handoff.json", packet.to_dict())
    return packet


def build_literature_clusters(inventory: dict[str, Any]) -> dict[str, Any]:
    literature = inventory["literature_files"] + inventory["reference_files"]
    return {
        "robot_labor_reallocation": [
            item
            for item in literature
            if any(term in item["name"].lower() for term in ["robot", "automation", "acemoglu", "autor"])
            or any(term in item["name"] for term in ["机器人", "自动化"])
        ],
        "matching_and_mismatch": [
            item
            for item in literature
            if any(term in item["name"].lower() for term in ["matching", "mismatch", "search"])
            or any(term in item["name"] for term in ["匹配", "错配", "求职"])
        ],
        "identification_and_bartik": [
            item
            for item in literature
            if any(term in item["name"].lower() for term in ["bartik", "iv", "instrument"])
            or any(term in item["name"] for term in ["识别", "工具变量"])
        ],
    }


def select_markdown_source(project_root: Path) -> Path | None:
    candidates = [
        project_root / "04_paper" / "论文v2.1_完整版.md",
        project_root / "04_paper" / "word_hqu_format" / "论文初稿_工业机器人冲击下的劳动者重新配置.md",
    ]
    candidates.extend(sorted((project_root / "04_paper").glob("*.md")))
    return next((path for path in candidates if path.exists()), None)


def read_manuscript_source(project_root: Path, inventory: dict[str, Any]) -> tuple[str, str | None]:
    source_path = select_markdown_source(project_root)
    if source_path is not None:
        return read_text(source_path), str(source_path.relative_to(project_root))
    section_texts = [
        read_text(project_root / item["path"])
        for item in inventory["manuscript_sections"]
        if read_text(project_root / item["path"])
    ]
    return "\n\n".join(section_texts), None


def normalize_markdown_for_run(text: str, project_root: Path) -> str:
    figures_root = project_root / "04_paper" / "figures"

    def replace_image(match: re.Match[str]) -> str:
        alt = match.group("alt")
        path = match.group("path")
        suffix = match.group("suffix") or ""
        if path.startswith(("/", "http://", "https://")):
            return match.group(0)
        if path.startswith("figures/"):
            return f"![{alt}]({figures_root / path.removeprefix('figures/')}){suffix}"
        return match.group(0)

    return re.sub(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)(?P<suffix>\{[^}]*\})?", replace_image, text)


def build_review_payload(draft_text: str, mode: str, source_markdown: str | None) -> dict[str, Any]:
    checks = [
        {
            "priority": "P0",
            "name": "source_of_truth",
            "passed": source_markdown == "04_paper/论文v2.1_完整版.md" or (source_markdown or "").startswith("04_paper/sections_v21"),
            "risk": "写作源必须以 sections_v21 或 论文v2.1_完整版.md 为准，word_hqu_format 只作为旧 Word 导出链参考。",
        },
        {
            "priority": "P1",
            "name": "concept_boundary",
            "passed": "严格" in draft_text and ("错配" in draft_text or "配置" in draft_text),
            "risk": "匹配效率、匹配质量代理、技能岗位错配三层边界需要在摘要、文献述评和结论中保持一致。",
        },
        {
            "priority": "P1",
            "name": "weak_iv_caution",
            "passed": "弱工具变量" in draft_text or "Stock-Yogo" in draft_text or "第一阶段" in draft_text,
            "risk": "Bartik IV 需要保留第一阶段和弱 IV 口径，不能写成已经彻底解决。",
        },
        {
            "priority": "P1",
            "name": "clds_causal_rank",
            "passed": "机制扩展" in draft_text and ("补充" in draft_text or "辅助" in draft_text),
            "risk": "CLDS 机制结果不是 Bartik IV 主识别，必须写成补充机制证据，不能和 CFPS+Bartik IV 同等因果等级。",
        },
        {
            "priority": "P1",
            "name": "bartik_exclusion_boundary",
            "passed": "排他" in draft_text or "识别边界" in draft_text or "外生" in draft_text,
            "risk": "Bartik 排他性需要说明产业结构可能反映制造业基础、开放程度和发展路径，不能写成天然外生。",
        },
        {
            "priority": "P1",
            "name": "result_claim_alignment",
            "passed": any(term in draft_text for term in ["表 4", "表4", "Table", "图 5", "图5"]),
            "risk": "每个核心结论需要挂到表格、图形或结果索引。",
        },
        {
            "priority": "P2",
            "name": "part_time_zero_result",
            "passed": "兼职" not in draft_text or "不显著" in draft_text or "证据不足" in draft_text,
            "risk": "兼职变量如果不显著，不能反向解释为支持正规就业导向。",
        },
        {
            "priority": "P2",
            "name": "reference_completeness",
            "passed": "暂无中文核心文献" not in draft_text and "待补充" not in draft_text,
            "risk": "参考文献不能保留“暂无中文核心文献，待补充”等未完成标记。",
        },
    ]
    failed = [item for item in checks if not item["passed"]]
    return {
        "decision": "revise_major" if len(failed) >= 2 else "revise_minor",
        "checks": checks,
        "source_markdown": source_markdown,
        "revision_requests": [item["risk"] for item in failed]
        or [
            "保留概念边界、弱 IV 谨慎口径、结果到论断的引用链，并在最终 Word 前再次检查摘要与结论。",
        ],
        "strengths": [
            "审阅对象来自真实论文 Markdown 源稿。" if mode == "live" else "审阅对象来自 dry-run 草稿。",
            "审阅者与写作者在 handoff 中保持逻辑分离。",
        ],
        "risks": [item["risk"] for item in checks if not item["passed"]],
    }


def write_real_review_files(review_report_path: Path, revision_plan_path: Path, review_payload: dict[str, Any]) -> None:
    check_lines = [
        f"- {item['priority']} {item['name']}: {'PASS' if item['passed'] else 'FAIL'} - {item['risk']}"
        for item in review_payload["checks"]
    ]
    failed_lines = [
        f"- {item['priority']} {item['name']}: {item['risk']}"
        for item in review_payload["checks"]
        if not item["passed"]
    ]
    write_text(
        review_report_path,
        "\n".join(
            [
                "# Review Report",
                "",
                "## Review Object",
                "",
                f"- mode: {review_payload.get('mode', 'unknown')}",
                f"- source_markdown: {review_payload.get('source_markdown') or 'section-assembled'}",
                "- source_policy: sections_v21 and 论文v2.1_完整版.md are the current writing sources; word_hqu_format is an export-chain source.",
                "",
                "## Decision",
                "",
                review_payload["decision"],
                "",
                "## Findings",
                "",
                *(failed_lines or ["- No blocking findings. Keep reviewer checks active before final submission."]),
                "",
                "## Checks",
                "",
                *check_lines,
                "",
                "## Revision Requests",
                "",
                *[f"- {item}" for item in review_payload["revision_requests"]],
            ]
        )
        + "\n",
    )
    write_text(
        revision_plan_path,
        "\n".join(
            [
                "# Revision Plan",
                "",
                "## Principles",
                "",
                "- Do not rewrite locked empirical results without explicit approval.",
                "- Fix source-of-truth, reference, and evidence-boundary issues before language polishing.",
                "- Keep CFPS+Bartik IV as main identification and CLDS as mechanism extension.",
                "",
                "## Action Items",
                "",
                *[f"{idx}. {item}" for idx, item in enumerate(review_payload["revision_requests"], start=1)],
                "",
                "## Recheck Gate",
                "",
                "- Recheck references, table/figure numbers, abstract numbers, weak-IV wording, CLDS causal rank, and HQU Word formatting.",
                "",
                "## Required Before Final Submission",
                "",
                "1. 更新 Word/WPS 目录域。",
                "2. 复核摘要、结论、弱 IV 表述是否一致。",
                "3. 确认每个实证结论均能追溯到结果表、图或日志。",
            ]
        )
        + "\n",
    )


def build_hqu_docx(project_root: Path, markdown: Path, output: Path, report: Path) -> dict[str, Any]:
    template = project_root / "05_reference" / "毕业论文格式规范" / "经济与金融学院本科毕业论文格式模板.docx"
    script = Path("/Users/mahaoxuan/.codex/skills/hqu-thesis-formatting/scripts/build_hqu_docx.py")
    archive_dir = output.parent / "archive_word_versions"
    if not template.exists():
        message = f"HQU template not found: {template}"
        write_text(output, message + "\n")
        write_text(report, f"# Formatting Report\n\nFAILED: {message}\n")
        return {"status": "failed", "returncode": 1, "error": message, "template": str(template)}
    if shutil.which("pandoc") is None:
        message = "pandoc is required for live HQU docx export but was not found in PATH"
        write_text(output, message + "\n")
        write_text(report, f"# Formatting Report\n\nFAILED: {message}\n")
        return {"status": "failed", "returncode": 1, "error": message, "template": str(template)}
    command = [
        "python3",
        str(script),
        "--markdown",
        str(markdown),
        "--template",
        str(template),
        "--output",
        str(output),
        "--archive-dir",
        str(archive_dir),
    ]
    process = subprocess.run(command, cwd=project_root, text=True, capture_output=True)
    status = "completed" if process.returncode == 0 and output.exists() else "failed"
    fallback: dict[str, Any] | None = None
    if status == "failed":
        fallback_output = output
        fallback_command = [
            "pandoc",
            str(markdown),
            "--from",
            "markdown+tex_math_dollars+raw_tex",
            "--reference-doc",
            str(template),
            "-o",
            str(fallback_output),
        ]
        fallback_process = subprocess.run(fallback_command, cwd=project_root, text=True, capture_output=True)
        fallback = {
            "command": fallback_command,
            "returncode": fallback_process.returncode,
            "stdout": fallback_process.stdout,
            "stderr": fallback_process.stderr,
        }
        if fallback_process.returncode == 0 and fallback_output.exists():
            status = "completed_with_reference_doc_fallback"
    write_text(
        report,
        "\n".join(
            [
                "# Formatting Report",
                "",
                f"- status: {status}",
                f"- template: {template}",
                f"- markdown: {markdown}",
                f"- output: {output}",
                f"- archive_dir: {archive_dir}",
                f"- returncode: {process.returncode}",
                "",
                "## stdout",
                "",
                process.stdout or "(empty)",
                "",
                "## stderr",
                "",
                process.stderr or "(empty)",
                "",
                "## fallback",
                "",
                json.dumps(fallback, ensure_ascii=False, indent=2) if fallback else "(not used)",
            ]
        )
        + "\n",
    )
    return {
        "status": status,
        "returncode": process.returncode,
        "command": command,
        "stdout": process.stdout,
        "stderr": process.stderr,
        "fallback": fallback,
        "template": str(template),
    }


def run_workbench(project_root: Path, mode: str = "dry-run", user_goal: str = "") -> dict[str, Any]:
    project_root = project_root.resolve()
    run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:6]}"
    workspace = create_run_workspace(project_root, run_id)
    run_root = workspace.root
    profile = detect_project_profile(project_root)
    inventory = build_evidence_inventory(project_root, profile)
    artifacts: list[str] = []
    handoffs: list[HandoffPacket] = []

    # Governance roots
    product_root = _resolve_product_root()
    project_id = _resolve_project_id(profile)
    current_stage = ""
    emit_event(run_id, "run.started", payload={"mode": mode, "user_goal": user_goal})

    def record(path: Path) -> Path:
        artifacts.append(artifact_rel(path, project_root))
        return path

    def run_stage(stage: str, agent_display_name: str, stage_func: Callable[[], Any]) -> Any:
        nonlocal current_stage
        current_stage = stage
        try:
            return _run_stage(product_root, project_root, project_id, run_id, stage, agent_display_name, stage_func)
        except Exception as exc:
            emit_event(run_id, "run.failed", payload={"stage": current_stage, "error": str(exc)})
            schedule_drop_run_queue(run_id)
            raise

    # ── 00_intake ──────────────────────────────────────────────────────────
    def _stage_00_intake() -> None:
        nonlocal project_profile_path, user_goal_path
        project_profile_path = record(run_root / "00_intake" / "project_profile.json")
        user_goal_path = record(run_root / "00_intake" / "user_goal.md")
        write_json(project_profile_path, profile)
        write_text(user_goal_path, user_goal or "No explicit user goal provided.")
        handoffs.append(
            write_handoff(
                run_id,
                run_root,
                project_root,
                "PreparationAgent",
                "00_intake",
                [],
                [project_profile_path, user_goal_path],
                ["Project profile normalized for workbench execution."],
                [],
                "LiteratureAgent",
                {"layout": profile["layout"]},
            )
        )

    project_profile_path: Path = Path()
    user_goal_path: Path = Path()
    run_stage("00_intake", "PreparationAgent", _stage_00_intake)

    # ── 01_sources ─────────────────────────────────────────────────────────
    def _stage_01_sources() -> None:
        nonlocal source_inventory_path, dataset_inventory_path, literature_inventory_path
        source_inventory_path = record(run_root / "01_sources" / "source_inventory.json")
        dataset_inventory_path = record(run_root / "01_sources" / "dataset_inventory.json")
        literature_inventory_path = record(run_root / "01_sources" / "literature_inventory.json")
        write_json(source_inventory_path, inventory)
        write_json(dataset_inventory_path, {"items": inventory["datasets"]})
        write_json(literature_inventory_path, {"items": inventory["literature_files"]})

    source_inventory_path: Path = Path()
    dataset_inventory_path: Path = Path()
    literature_inventory_path: Path = Path()
    run_stage("01_sources", "PreparationAgent", _stage_01_sources)

    # ── 02_literature ──────────────────────────────────────────────────────
    def _stage_02_literature() -> None:
        nonlocal clusters, literature_clusters_path, literature_brief_path, claim_map_path
        clusters = build_literature_clusters(inventory)
        literature_clusters_path = record(run_root / "02_literature" / "literature_clusters.json")
        literature_brief_path = record(run_root / "02_literature" / "core_literature_brief.md")
        claim_map_path = record(run_root / "02_literature" / "claim_evidence_map.json")
        write_json(literature_clusters_path, clusters)
        write_text(
            literature_brief_path,
            "\n".join(
                [
                    "# Core Literature Brief",
                    "",
                    "The first thesis run treats robot labor reallocation, matching-quality proxies, and skill-post mismatch as separate evidence layers.",
                    "",
                    "## Detected Literature Clusters",
                    "",
                    f"- Robot and automation files: {len(clusters['robot_labor_reallocation'])}",
                    f"- Matching and mismatch files: {len(clusters['matching_and_mismatch'])}",
                    f"- Identification files: {len(clusters['identification_and_bartik'])}",
                ]
            ),
        )
        write_json(
            claim_map_path,
            {
                "claims": [
                    {
                        "claim": "Strict matching efficiency is not directly identified.",
                        "evidence": ["05_reference/匹配效率概念与可测代理对照表.md"],
                    },
                    {
                        "claim": "The thesis should frame measurable outcomes as allocation quality, search-friction proxies, and mismatch.",
                        "evidence": ["04_paper/sections_v21", "05_reference"],
                    },
                ]
            },
        )
        handoffs.append(
            write_handoff(
                run_id,
                run_root,
                project_root,
                "LiteratureAgent",
                "02_literature",
                [literature_inventory_path],
                [literature_clusters_path, literature_brief_path, claim_map_path],
                ["Literature evidence is separated into robot, matching, and identification clusters."],
                ["File-level inventory is not a substitute for full-text causal claim verification."],
                "ResearchStrategistAgent",
            )
        )

    clusters: dict[str, Any] = {}
    literature_clusters_path: Path = Path()
    literature_brief_path: Path = Path()
    claim_map_path: Path = Path()
    run_stage("02_literature", "LiteratureAgent", _stage_02_literature)

    # ── 03_strategy ────────────────────────────────────────────────────────
    def _stage_03_strategy() -> None:
        nonlocal research_plan_path, identification_plan_path, empirical_plan_path
        research_plan_path = record(run_root / "03_strategy" / "research_plan.md")
        identification_plan_path = record(run_root / "03_strategy" / "identification_plan.md")
        empirical_plan_path = record(run_root / "03_strategy" / "empirical_plan.md")
        write_text(
            research_plan_path,
            "# Research Plan\n\nPrimary question: how industrial robot exposure affects worker allocation outcomes, job-search frictions, and skill-post mismatch.\n",
        )
        write_text(
            identification_plan_path,
            "# Identification Plan\n\nUse Bartik IV as the main identification strategy and keep weak-IV caveats explicit.\n",
        )
        write_text(
            empirical_plan_path,
            "# Empirical Plan\n\nUse CFPS for outcome-layer results, CLDS for mechanism-layer checks, and CGSS for concept calibration.\n",
        )
        handoffs.append(
            write_handoff(
                run_id,
                run_root,
                project_root,
                "ResearchStrategistAgent",
                "03_strategy",
                [project_profile_path, literature_brief_path, claim_map_path],
                [research_plan_path, identification_plan_path, empirical_plan_path],
                ["Bartik IV remains the main identification path for the first thesis run."],
                ["Weak-IV language must stay cautious in draft and handoff files."],
                "ModelingAgent",
            )
        )

    research_plan_path: Path = Path()
    identification_plan_path: Path = Path()
    empirical_plan_path: Path = Path()
    run_stage("03_strategy", "ResearchStrategistAgent", _stage_03_strategy)

    # ── 04_modeling: REAL LLM + StatsPAI integration ───────────────────────
    def _stage_04_modeling() -> None:
        from . import cost_service

        nonlocal modeling_report_path, diagnostics_report_path
        nonlocal design_spec, run_plan, llm_report, llm_metadata, backend_result
        modeling_report_path = record(run_root / "04_modeling" / "modeling_report.json")
        diagnostics_report_path = record(run_root / "04_modeling" / "diagnostics_report.md")

        # Load design spec and run plan from state
        design_spec = _load_state_json(project_root, "design_spec.json")
        run_plan = _load_state_json(project_root, "run_plan.json")

        # Build research plan text for prompt
        research_plan_text = read_text(research_plan_path)
        identification_plan_text = read_text(identification_plan_path)
        empirical_plan_text = read_text(empirical_plan_path)

        # ── LLM call with separate cost event ──────────────────────────────
        llm_prompt = _build_modeling_prompt(
            design_spec, research_plan_text, identification_plan_text,
            empirical_plan_text, inventory,
        )
        llm_event_id = cost_service.start_cost_event(
            project_root=project_root,
            project_id=project_id,
            workflow_id=run_id,
            task_id=f"{run_id}_04_modeling_llm",
            actor_id=_resolve_agent_id("modeling_agent"),
            capability_id="cap_llm_modeling",
            event_type="llm_call",
        )
        llm_start_ts = time.perf_counter()
        llm_status = "succeeded"
        try:
            llm_report, llm_metadata = _call_llm_for_modeling(llm_prompt)
            emit_event(
                run_id,
                "stage.output",
                stage="04_modeling",
                agent_name="ModelingAgent",
                payload={
                    "source": "llm",
                    "chunk": llm_report[:500] + "..." if len(llm_report) > 500 else llm_report,
                },
            )
        except Exception:
            llm_status = "failed"
            raise
        finally:
            input_tokens = llm_metadata.get("input_tokens", 0)
            output_tokens = llm_metadata.get("output_tokens", 0)
            estimated_usd = _estimate_llm_cost(
                llm_metadata.get("provider_id", ""),
                llm_metadata.get("model", ""),
                input_tokens,
                output_tokens,
            )
            cost_service.finish_cost_event(
                project_root=project_root,
                event_id=llm_event_id,
                status=llm_status,
                wall_seconds=round(time.perf_counter() - llm_start_ts, 3),
                provider=llm_metadata.get("provider_id", "unknown"),
                model=llm_metadata.get("model", "unknown"),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_usd=estimated_usd,
            )

        # ── StatsPAI execution with separate cost event ────────────────────
        backend_result = None
        if mode == "live" and design_spec and run_plan:
            statspai_event_id = cost_service.start_cost_event(
                project_root=project_root,
                project_id=project_id,
                workflow_id=run_id,
                task_id=f"{run_id}_04_modeling_statspai",
                actor_id=_resolve_agent_id("modeling_agent"),
                capability_id="cap_statspai_ols",
                event_type="statistical_execution",
            )
            statspai_start_ts = time.perf_counter()
            statspai_status = "succeeded"
            try:
                backend_result = _execute_modeling_with_backend(project_root, run_id, design_spec, run_plan)
                if backend_result:
                    emit_event(
                        run_id,
                        "stage.output",
                        stage="04_modeling",
                        agent_name="ModelingAgent",
                        payload={
                            "source": "statspai",
                            "chunk": f"StatsPAI backend: {backend_result.get('status', 'unknown')}",
                        },
                    )
            except Exception:
                statspai_status = "failed"
                raise
            finally:
                cost_service.finish_cost_event(
                    project_root=project_root,
                    event_id=statspai_event_id,
                    status=statspai_status,
                    wall_seconds=round(time.perf_counter() - statspai_start_ts, 3),
                )

        modeling_report_payload: dict[str, Any] = {
            "mode": mode,
            "detected_code_files": inventory["code_files"],
            "execution_policy": "audit existing scripts in dry-run" if mode == "dry-run" else "live execution with StatsPAI backend",
            "llm_enabled": True,
            "llm_provider": llm_metadata.get("provider_id", "unknown"),
            "llm_model": llm_metadata.get("model", "unknown"),
            "llm_error": llm_metadata.get("error"),
            "design_spec_loaded": design_spec is not None,
            "run_plan_loaded": run_plan is not None,
            "backend_result": backend_result,
        }

        if backend_result:
            modeling_report_payload["backend_status"] = backend_result.get("status")
            modeling_report_payload["backend_engine"] = backend_result.get("engine")
            modeling_report_payload["backend_artifact"] = backend_result.get("artifact_path")

        write_json(modeling_report_path, modeling_report_payload)

        diagnostics_content = f"""# Diagnostics Report

{"## LLM Modeling Report" if not llm_metadata.get("error") else "## LLM Modeling Report (with errors)"}

{llm_report}

## Execution Status
- Mode: {mode}
- LLM Provider: {llm_metadata.get("provider_name", llm_metadata.get("provider_id", "unknown"))}
- LLM Model: {llm_metadata.get("model", "unknown")}
- Design Spec Loaded: {"yes" if design_spec else "no"}
- Run Plan Loaded: {"yes" if run_plan else "no"}
- Backend Execution: {backend_result.get("status", "not_run") if backend_result else "not_run"}

{"## StatsPAI Results\n\n" + json.dumps(backend_result, ensure_ascii=False, indent=2)[:3000] if backend_result else ""}
"""
        write_text(diagnostics_report_path, diagnostics_content)

        handoffs.append(
            write_handoff(
                run_id,
                run_root,
                project_root,
                "ModelingAgent",
                "04_modeling",
                [empirical_plan_path],
                [modeling_report_path, diagnostics_report_path],
                [
                    "LLM-generated modeling strategy report is included in diagnostics." if not llm_metadata.get("error") else "LLM call failed; manual review required.",
                    f"StatsPAI backend status: {backend_result.get('status', 'not_run')}." if backend_result else "StatsPAI backend was not executed (dry-run or missing design_spec).",
                ],
                [
                    "LLM output should be reviewed for methodology soundness." if not llm_metadata.get("error") else "LLM failure requires manual modeling strategy input.",
                    "Backend execution results must be cross-checked against theoretical predictions." if backend_result else "No live execution was performed.",
                ],
                "VisualizationAgent",
            )
        )

    modeling_report_path: Path = Path()
    diagnostics_report_path: Path = Path()
    design_spec: dict[str, Any] | None = None
    run_plan: dict[str, Any] | None = None
    llm_report: str = ""
    llm_metadata: dict[str, Any] = {}
    backend_result: dict[str, Any] | None = None
    run_stage("04_modeling", "ModelingAgent", _stage_04_modeling)

    # ── 05_results ─────────────────────────────────────────────────────────
    def _stage_05_results() -> None:
        nonlocal results_index_path, table_plan_path, figure_plan_path
        results_index_path = record(run_root / "05_results" / "results_index.json")
        table_plan_path = record(run_root / "05_results" / "table_plan.md")
        figure_plan_path = record(run_root / "05_results" / "figure_plan.md")
        write_json(results_index_path, {"items": inventory["results_files"]})
        write_text(table_plan_path, "# Table Plan\n\nUse existing indexed thesis tables before generating new tables.\n")
        write_text(figure_plan_path, "# Figure Plan\n\nUse existing thesis figures and figure scripts as first-class artifacts.\n")
        handoffs.append(
            write_handoff(
                run_id,
                run_root,
                project_root,
                "VisualizationAgent",
                "05_results",
                [modeling_report_path],
                [results_index_path, table_plan_path, figure_plan_path],
                ["Results are indexed before manuscript claims are rewritten."],
                ["Some visual artifacts may still be generated by another IDE and need later sync."],
                "WritingAgent",
            )
        )

    results_index_path: Path = Path()
    table_plan_path: Path = Path()
    figure_plan_path: Path = Path()
    run_stage("05_results", "VisualizationAgent", _stage_05_results)

    # ── 06_writing ─────────────────────────────────────────────────────────
    def _stage_06_writing() -> None:
        nonlocal manuscript_source, manuscript_source_rel, paper_draft_path, section_status_path
        manuscript_source, manuscript_source_rel = read_manuscript_source(project_root, inventory)
        paper_draft_path = record(run_root / "06_writing" / "paper_draft.md")
        section_status_path = record(run_root / "06_writing" / "section_status.json")
        if mode == "live" and manuscript_source:
            write_text(paper_draft_path, normalize_markdown_for_run(manuscript_source, project_root))
        else:
            write_text(
                paper_draft_path,
                "\n".join(
                    [
                        "# Paper Draft",
                        "",
                        "This draft is generated from inspected sources and preserves the matching-efficiency boundary.",
                        "",
                        "## Source Snapshot",
                        manuscript_source[:6000] if manuscript_source else "No manuscript source detected.",
                    ]
                ),
            )
        write_json(
            section_status_path,
            {
                "sections_detected": [item["path"] for item in inventory["manuscript_sections"]],
                "source_markdown": manuscript_source_rel,
                "status": "drafted",
            },
        )
        handoffs.append(
            write_handoff(
                run_id,
                run_root,
                project_root,
                "WritingAgent",
                "06_writing",
                [research_plan_path, identification_plan_path, results_index_path, claim_map_path],
                [paper_draft_path, section_status_path],
                ["Draft generation must preserve concept boundaries and evidence references."],
                ["Generated draft requires independent review before final formatting."],
                "ReviewerAgent",
            )
        )

    manuscript_source: str = ""
    manuscript_source_rel: str | None = None
    paper_draft_path: Path = Path()
    section_status_path: Path = Path()
    run_stage("06_writing", "WritingAgent", _stage_06_writing)

    # ── 07_review ──────────────────────────────────────────────────────────
    def _stage_07_review() -> None:
        nonlocal review_report_path, revision_plan_path, reviewer_decision_path, review_payload, review
        review_report_path = record(run_root / "07_review" / "review_report.md")
        revision_plan_path = record(run_root / "07_review" / "revision_plan.md")
        reviewer_decision_path = record(run_root / "07_review" / "reviewer_decision.json")
        review_payload = build_review_payload(read_text(paper_draft_path), mode, manuscript_source_rel)
        review_payload["mode"] = mode
        review = ReviewPacket(
            run_id=run_id,
            reviewer="ReviewerAgent",
            target_agent="WritingAgent",
            target_artifact=artifact_rel(paper_draft_path, project_root),
            decision=review_payload["decision"],
            revision_requests=review_payload["revision_requests"],
            strengths=review_payload["strengths"],
            risks=review_payload["risks"],
        )
        write_real_review_files(review_report_path, revision_plan_path, review_payload)
        write_json(reviewer_decision_path, review.to_dict())
        handoffs.append(
            write_handoff(
                run_id,
                run_root,
                project_root,
                "ReviewerAgent",
                "07_review",
                [paper_draft_path],
                [review_report_path, revision_plan_path, reviewer_decision_path],
                ["Reviewer is independent from WritingAgent."],
                review.risks,
                "FormatterAgent",
            )
        )

    review_report_path: Path = Path()
    revision_plan_path: Path = Path()
    reviewer_decision_path: Path = Path()
    review_payload: dict[str, Any] = {}
    review: ReviewPacket = ReviewPacket(
        run_id=run_id, reviewer="ReviewerAgent", target_agent="WritingAgent",
        target_artifact="", decision="revise_minor", revision_requests=[],
        strengths=[], risks=[],
    )
    run_stage("07_review", "ReviewerAgent", _stage_07_review)

    # ── 08_final ───────────────────────────────────────────────────────────
    def _stage_08_final() -> None:
        nonlocal tex_path, docx_path, formatting_report_path, formatting_result
        tex_path = record(run_root / "08_final" / "paper_draft.tex")
        docx_path = record(run_root / "08_final" / "paper_draft.docx")
        formatting_report_path = record(run_root / "08_final" / "formatting_report.md")
        write_text(tex_path, "\\section{Draft}\nGenerated draft placeholder for TeX export.\n")
        if mode == "live":
            formatting_result = build_hqu_docx(project_root, paper_draft_path, docx_path, formatting_report_path)
        else:
            write_text(docx_path, "DOCX export placeholder recorded by dry-run.\n")
            write_text(formatting_report_path, "# Formatting Report\n\nDry-run recorded the Word export path. Live mode will call the formatter.\n")
            formatting_result = {"status": "dry-run", "returncode": 0}
        handoffs.append(
            write_handoff(
                run_id,
                run_root,
                project_root,
                "FormatterAgent",
                "08_final",
                [paper_draft_path, reviewer_decision_path],
                [tex_path, docx_path, formatting_report_path],
                ["Word output path is recorded for the A experience."],
                [] if formatting_result["status"] == "completed" else [f"Formatter status: {formatting_result['status']}"],
                None,
                {"formatting_result": formatting_result},
            )
        )

    tex_path: Path = Path()
    docx_path: Path = Path()
    formatting_report_path: Path = Path()
    formatting_result: dict[str, Any] = {"status": "dry-run", "returncode": 0}
    run_stage("08_final", "FormatterAgent", _stage_08_final)

    # ── Manifest ───────────────────────────────────────────────────────────
    manifest_path = run_root / "run_manifest.json"
    artifacts.append(artifact_rel(manifest_path, project_root))
    manifest = OrchestrationManifest(
        run_id=run_id,
        project_id=_resolve_project_id(profile),
        project_root=str(project_root),
        run_root=str(run_root),
        mode=mode,
        supervisor={
            "name": "Supervisor",
            "status": "completed",
            "created_at": utc_now(),
            "user_goal": user_goal,
        },
        agents=[
            {"name": packet.agent, "stage": packet.stage, "status": packet.status}
            for packet in handoffs
        ],
        review_loop={
            "writer": "WritingAgent",
            "reviewer": "ReviewerAgent",
            "decision": review.decision,
            "iterations": 1,
            "status": "completed",
        },
        artifacts=artifacts,
        status="completed",
    )
    write_json(manifest_path, manifest.to_dict())
    emit_event(
        run_id,
        "run.completed",
        payload={"status": "completed", "artifacts_count": len(artifacts)},
    )
    schedule_drop_run_queue(run_id)
    return manifest.to_dict()


def orchestrate_project(project_root: Path, run_live: bool = False) -> dict[str, Any]:
    mode = "live" if run_live else "dry-run"
    return run_workbench(project_root, mode=mode, user_goal="Legacy orchestration endpoint")
