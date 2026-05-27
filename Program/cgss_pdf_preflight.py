from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_pdf_preflight import (  # noqa: E402
    DEFAULT_HTML_PATH,
    DEFAULT_PAPER_PATH,
    DEFAULT_PDF_PATH,
    DEFAULT_RESULT_PATH,
    DEFAULT_REVIEW_PATH,
    build_cgss_pdf_preflight,
    write_cgss_pdf_preflight_outputs,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a local PDF/HTML preflight artifact for the CGSS exploratory paper.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--paper", default=str(DEFAULT_PAPER_PATH))
    parser.add_argument("--output-pdf", default=str(DEFAULT_PDF_PATH))
    parser.add_argument("--output-html", default=str(DEFAULT_HTML_PATH))
    parser.add_argument("--output-result", default=str(DEFAULT_RESULT_PATH))
    parser.add_argument("--output-review", default=str(DEFAULT_REVIEW_PATH))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    package = build_cgss_pdf_preflight(
        project_root,
        Path(args.paper),
        Path(args.output_pdf),
        html_path=Path(args.output_html),
    )
    result_path, review_path = write_cgss_pdf_preflight_outputs(
        project_root,
        package,
        Path(args.output_result),
        Path(args.output_review),
    )

    print(f"[econ-workbench] cgss_pdf_preflight={result_path.relative_to(project_root)}")
    print(f"[econ-workbench] cgss_pdf_preflight_review={review_path.relative_to(project_root)}")
    print(f"[econ-workbench] status={package['status']}")
    print(f"[econ-workbench] pdf={package['pdf']['path']} exists={package['pdf']['exists']} bytes={package['pdf']['bytes']}")
    print(f"[econ-workbench] html={package['html']['path']} exists={package['html']['exists']} bytes={package['html']['bytes']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
