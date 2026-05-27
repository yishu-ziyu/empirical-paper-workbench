import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.reference_marker_patch_proposal import (
    build_reference_marker_patch,
    write_outputs,
)


class ReferenceMarkerPatchProposalTests(unittest.TestCase):
    """BDD: LiteratureAgent repairs citation markers only as a draft-layer proposal."""

    def test_bdd_p7e_unmarked_candidate_references_are_marked_in_candidate_paper(self) -> None:
        patch = build_reference_marker_patch(
            paper_text=self._paper_with_references("- `bourdieu_1986`\n- `putnam_2000`\n"),
            source_path="workspace/paper_packages/cgss_social_capital_happiness/paper.md",
        )

        self.assertEqual(patch["schema_version"], "p7.reference_marker_patch_proposal.v1")
        self.assertEqual(patch["status"], "needs_human_reference_marker_review")
        self.assertEqual(len(patch["changed_references"]), 2)
        self.assertIn("- `bourdieu_1986`（候选，待人工核验）", patch["candidate_paper_text"])
        self.assertIn("- `putnam_2000`（候选，待人工核验）", patch["candidate_paper_text"])
        self.assertFalse(patch["boundary_flags"]["source_paper_overwritten"])

    def test_bdd_p7e_already_marked_references_are_idempotent(self) -> None:
        original = self._paper_with_references("- `bourdieu_1986`（候选，待人工核验）\n")

        patch = build_reference_marker_patch(paper_text=original, source_path="paper.md")

        self.assertEqual(patch["status"], "no_reference_marker_patch_needed")
        self.assertEqual(patch["changed_references"], [])
        self.assertEqual(patch["candidate_paper_text"], original)

    def test_bdd_p7e_writes_json_review_and_candidate_paper(self) -> None:
        patch = build_reference_marker_patch(
            paper_text=self._paper_with_references("- `bourdieu_1986`\n"),
            source_path="paper.md",
        )

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            report_path, review_path, candidate_path = write_outputs(
                project_root=project_root,
                patch=patch,
                report_path=Path("Results/json/reference_marker_patch_proposal.json"),
                review_path=Path("Reviews/reference_marker_patch_proposal.md"),
                candidate_paper_path=Path("Manuscripts/generated/candidate.md"),
            )

            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["status"], "needs_human_reference_marker_review")
            self.assertIn("Reference Marker Patch Proposal", review_path.read_text(encoding="utf-8"))
            self.assertIn("正式论文写回：否", review_path.read_text(encoding="utf-8"))
            self.assertIn("（候选，待人工核验）", candidate_path.read_text(encoding="utf-8"))

    def test_bdd_p7e_boundary_flags_block_formal_writeback(self) -> None:
        patch = build_reference_marker_patch(
            paper_text=self._paper_with_references("- `bourdieu_1986`\n"),
            source_path="paper.md",
        )

        self.assertFalse(patch["boundary_flags"]["modified_formal_manuscript"])
        self.assertFalse(patch["boundary_flags"]["modified_formal_bibliography"])
        self.assertFalse(patch["boundary_flags"]["modified_project_bibliography"])
        self.assertFalse(patch["boundary_flags"]["modified_product_state"])
        self.assertFalse(patch["boundary_flags"]["source_paper_overwritten"])

    def test_bdd_p7e_missing_candidate_references_section_blocks_patch(self) -> None:
        patch = build_reference_marker_patch(
            paper_text="# 论文\n\n## 结论\n\n没有候选引用节。",
            source_path="paper.md",
        )

        self.assertEqual(patch["status"], "blocked_missing_candidate_references_section")
        self.assertEqual(patch["changed_references"], [])
        self.assertNotIn("（候选，待人工核验）", patch["candidate_paper_text"])

    def _paper_with_references(self, references: str) -> str:
        return (
            "# 社会资本对居民主观幸福感的影响研究\n\n"
            "## 摘要\n\n"
            "这是草稿层论文。\n\n"
            "## 参考文献候选\n\n"
            f"{references}\n"
            "## 人工审阅清单\n\n"
            "- 检查候选引用。\n"
        )


if __name__ == "__main__":
    unittest.main()
