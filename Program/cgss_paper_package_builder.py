from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Program.workbench.cgss_paper_package_builder import (  # noqa: E402
    DEFAULT_PACKAGE_DIR,
    build_cgss_paper_package,
    write_cgss_paper_package,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the CGSS reviewable paper package.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--package-dir", default=str(DEFAULT_PACKAGE_DIR))
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    package = build_cgss_paper_package(project_root, Path(args.package_dir))
    package_dir = write_cgss_paper_package(project_root, package)

    print(f"[econ-workbench] cgss_paper_package={package_dir.relative_to(project_root)}")
    print(f"[econ-workbench] status={package['status']}")
    print(f"[econ-workbench] rendered_artifact={package.get('rendered_artifact', '')}")
    print(f"[econ-workbench] files={len(package.get('files', []))}")
    if package.get("missing_targets"):
        print(f"[econ-workbench] missing={','.join(package['missing_targets'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
