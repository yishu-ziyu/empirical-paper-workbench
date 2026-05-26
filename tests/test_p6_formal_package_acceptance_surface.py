from __future__ import annotations

from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_REACT_ROOT = REPO_ROOT / "Product" / "web-react"
BDD_DOC = REPO_ROOT / "docs" / "architecture-v2" / "codex-phase-p4-paper-package-quality-bdd.md"


class ReactFormalPackageAcceptanceSurfaceContractTest(unittest.TestCase):
    """P6-F2：正式投稿包验收台前端契约。"""

    def test_behavior_41_is_documented(self) -> None:
        source = BDD_DOC.read_text(encoding="utf-8")

        required_markers = [
            "Behavior 41",
            "formal-submission-package-summary",
            "formal package acceptance bench",
            "read-only",
            "formal_submission_package_summary_required",
        ]
        for marker in required_markers:
            self.assertIn(marker, source, f"Missing P6-F2 BDD marker: {marker}")

    def test_formal_package_acceptance_component_reads_summary_api(self) -> None:
        component_path = WEB_REACT_ROOT / "src" / "components" / "FormalPackageAcceptancePanel.tsx"
        self.assertTrue(component_path.exists(), "FormalPackageAcceptancePanel component is missing.")

        source = component_path.read_text(encoding="utf-8")
        expected_markers = [
            "FormalPackageAcceptancePanel",
            "/api/v1/projects/",
            "formal-submission-package-summary",
            "ready_for_manual_acceptance",
            "formal_submission_package_summary_required",
            "visible_summary",
            "open_targets",
            "manual_acceptance",
            "consistency_checks",
            "blocking_reasons",
            "打开 PDF",
            "打开 DOCX",
            "人工验收清单",
            "一致性检查",
            "阻断原因",
            "只读验收摘要",
        ]
        for marker in expected_markers:
            self.assertIn(marker, source, f"Missing acceptance surface marker: {marker}")

        forbidden_markers = [
            "approveFormalPackage",
            "regenerate",
            "renderPdf",
            "renderDocx",
            "window.open(",
        ]
        for marker in forbidden_markers:
            self.assertNotIn(marker, source, f"Acceptance surface must stay read-only: {marker}")

    def test_agent_activity_panel_mounts_acceptance_surface_after_execution_authorization(self) -> None:
        source = (WEB_REACT_ROOT / "src" / "components" / "AgentActivityPanel.tsx").read_text(encoding="utf-8")

        required_markers = [
            "FormalPackageAcceptancePanel",
            'projectId="proj_undergraduate_thesis"',
            "executionStarted &&",
            "formal-package-acceptance-slot",
        ]
        for marker in required_markers:
            self.assertIn(marker, source, f"Missing mounted acceptance surface marker: {marker}")

    def test_styles_include_acceptance_surface_rules(self) -> None:
        css = (WEB_REACT_ROOT / "src" / "styles.css").read_text(encoding="utf-8")

        required_markers = [
            "formal-package-acceptance",
            "formal-package-acceptance__targets",
            "formal-package-acceptance__checklist",
            "formal-package-acceptance__blockers",
        ]
        for marker in required_markers:
            self.assertIn(marker, css, f"Missing acceptance surface CSS marker: {marker}")


if __name__ == "__main__":
    unittest.main()
