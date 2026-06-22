from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "parent_education_wage_delivery_package.v1"
TOPIC = "父母受教育水平对子女工资收入的影响"

P16_PATH = Path("Results/json/parent_education_wage_p16_user_acceptance_packet.json")
MANIFEST_PATH = Path("Submissions/parent_education_wage_delivery_manifest.json")
README_PATH = Path("Submissions/parent_education_wage_delivery_README.md")
ZIP_PATH = Path("Submissions/parent_education_wage_delivery_package.zip")

REQUIRED_DELIVERY_FILES = [
    Path("Submissions/parent_education_wage_paper_draft.docx"),
    Path("Manuscripts/generated/parent_education_wage_complete_paper_draft.md"),
    Path("Data/Interim/parent_education_wage_repaired.csv"),
    Path("Results/json/parent_education_wage_p13_run_plan_approval.json"),
    Path("Results/json/parent_education_wage_p14_execution_evidence_ledger.json"),
    Path("Results/json/parent_education_wage_p15_draft_export_package.json"),
    Path("Results/json/parent_education_wage_p16_user_acceptance_packet.json"),
    Path("Results/json/parent_education_wage_p17_data_repair_preflight.json"),
    Path("Results/json/parent_education_wage_p18_data_repair_apply.json"),
    Path("Reviews/parent_education_wage_p13_run_plan_approval.md"),
    Path("Reviews/parent_education_wage_p14_execution_evidence_ledger.md"),
    Path("Reviews/parent_education_wage_p15_draft_export_package.md"),
    Path("Reviews/parent_education_wage_p16_user_acceptance_packet.md"),
    Path("Reviews/parent_education_wage_p17_data_repair_preflight.md"),
    Path("Reviews/parent_education_wage_p18_data_repair_apply.md"),
]


def run_parent_education_wage_delivery_package(project_root: Path) -> tuple[dict[str, Any], Path | None]:
    project_root = project_root.resolve()
    manifest = build_parent_education_wage_delivery_package(project_root, write_package=True)
    if manifest.get("status") != "delivery_package_ready_for_human_review":
        return manifest, None
    write_json(project_root / MANIFEST_PATH, manifest)
    write_text(project_root / README_PATH, render_readme(manifest))
    write_zip(project_root, manifest)
    manifest = {
        **manifest,
        "delivery_readme": README_PATH.as_posix(),
        "delivery_zip": ZIP_PATH.as_posix(),
        "delivery_zip_sha256": sha256(project_root / ZIP_PATH),
        "delivery_zip_size": (project_root / ZIP_PATH).stat().st_size,
    }
    write_json(project_root / MANIFEST_PATH, manifest)
    return manifest, project_root / ZIP_PATH


def get_parent_education_wage_delivery_package(project_root: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    manifest_path = project_root / MANIFEST_PATH
    if manifest_path.exists():
        payload = load_json(manifest_path)
        payload["artifact_exists"] = True
        return payload
    return build_parent_education_wage_delivery_package(project_root, write_package=False)


def build_parent_education_wage_delivery_package(project_root: Path, write_package: bool) -> dict[str, Any]:
    p16_path = project_root / P16_PATH
    if not p16_path.exists():
        return blocked_packet("blocked_missing_p16_acceptance_packet", ["missing_p16_acceptance_packet"])
    p16 = load_json(p16_path)
    if p16.get("can_claim_complete_paper") is not True:
        return blocked_packet("blocked_complete_draft_not_ready", ["p16_can_claim_complete_paper_false"])

    missing_files = [path.as_posix() for path in REQUIRED_DELIVERY_FILES if not (project_root / path).exists()]
    if missing_files:
        return blocked_packet("blocked_missing_delivery_files", missing_files)

    files = [file_record(project_root, path) for path in REQUIRED_DELIVERY_FILES]
    status = "delivery_package_ready_for_human_review" if write_package else "delivery_package_ready_to_generate"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "topic": TOPIC,
        "stage": "DeliveryPackage",
        "status": status,
        "artifact_exists": write_package,
        "current_user_outcome": "完整论文初稿 + 数据修复 + 模型证据 + 验收材料",
        "can_deliver_reviewable_package": True,
        "can_claim_submission_ready": False,
        "delivery_manifest": MANIFEST_PATH.as_posix(),
        "delivery_readme": README_PATH.as_posix(),
        "delivery_zip": ZIP_PATH.as_posix(),
        "files": files,
        "blocking_reasons": [],
        "next_action": "human_review_delivery_package",
        "guardrails": [
            "这是可审阅交付包，不是投稿终稿。",
            "交付包不重新运行模型，不改变论文结论。",
            "投稿前仍需人工审阅、参考文献和格式终检。",
        ],
    }


def blocked_packet(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "topic": TOPIC,
        "stage": "DeliveryPackage",
        "status": status,
        "artifact_exists": False,
        "can_deliver_reviewable_package": False,
        "can_claim_submission_ready": False,
        "delivery_manifest": MANIFEST_PATH.as_posix(),
        "delivery_readme": README_PATH.as_posix(),
        "delivery_zip": ZIP_PATH.as_posix(),
        "files": [],
        "blocking_reasons": blocking_reasons,
        "next_action": "complete_p13_p16_before_delivery_package",
    }


def file_record(project_root: Path, relative_path: Path) -> dict[str, Any]:
    path = project_root / relative_path
    return {
        "path": relative_path.as_posix(),
        "size": path.stat().st_size,
        "sha256": sha256(path),
    }


def write_zip(project_root: Path, manifest: dict[str, Any]) -> None:
    zip_path = project_root / ZIP_PATH
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(project_root / MANIFEST_PATH, MANIFEST_PATH.as_posix())
        archive.write(project_root / README_PATH, README_PATH.as_posix())
        for item in manifest.get("files", []):
            relative_path = Path(str(item["path"]))
            archive.write(project_root / relative_path, relative_path.as_posix())


def render_readme(manifest: dict[str, Any]) -> str:
    lines = [
        "# Parent Education Wage Delivery Package",
        "",
        f"- Status: `{manifest.get('status')}`",
        f"- Outcome: {manifest.get('current_user_outcome')}",
        f"- Submission ready: `{manifest.get('can_claim_submission_ready')}`",
        "",
        "## Files",
        "",
    ]
    for item in manifest.get("files", []):
        lines.append(f"- `{item['path']}` size={item['size']} sha256={item['sha256']}")
    lines.extend(
        [
            "",
            "## Guardrails",
            "",
            *[f"- {item}" for item in manifest.get("guardrails", [])],
            "",
        ]
    )
    return "\n".join(lines)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()

