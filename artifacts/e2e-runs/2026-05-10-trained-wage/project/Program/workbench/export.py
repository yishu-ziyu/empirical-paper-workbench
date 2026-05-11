from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def build_export_manifest(
    project_root: Path,
    markdown_path: Path,
    docx_path: Path,
    reference_doc: Path | None,
    command: list[str],
) -> dict[str, Any]:
    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source_markdown": str(markdown_path.relative_to(project_root)),
        "output_docx": str(docx_path.relative_to(project_root)),
        "reference_doc": str(reference_doc.relative_to(project_root)) if reference_doc else None,
        "command": command,
        "docx_exists": docx_path.exists(),
    }


def write_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run_pandoc(command: list[str], log_path: Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, text=True, capture_output=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        "\n".join(
            [
                "COMMAND:",
                " ".join(command),
                "",
                "STDOUT:",
                result.stdout,
                "",
                "STDERR:",
                result.stderr,
            ]
        ),
        encoding="utf-8",
    )
    return result

