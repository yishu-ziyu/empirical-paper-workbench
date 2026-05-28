import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_target_adapter_readiness import (
    build_auto_mode_formal_target_adapter_readiness,
    write_auto_mode_formal_target_adapter_readiness_outputs,
)


class AutoModeFormalTargetAdapterReadinessTests(unittest.TestCase):
    """BDD: P7-N maps apply-manifest target groups without executing adapters."""

    def test_bdd_p7n_ready_apply_manifest_maps_all_target_groups(self) -> None:
        """行为 1：ready apply manifest 映射 6 类 target group，但不执行 adapter。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            package_manifest = self._write_package(project_root)

            report = build_auto_mode_formal_target_adapter_readiness(
                project_root,
                self._ready_apply_manifest(),
                package_manifest,
                source_paths=self._source_paths(),
            )

            self.assertEqual(report["schema_version"], "p7.auto_mode_formal_target_adapter_readiness.v1")
            self.assertEqual(report["status"], "ready_for_formal_target_adapter_review")
            self.assertTrue(report["can_request_target_adapter_execution"])
            self.assertFalse(report["formal_target_adapters_executed"])
            self.assertFalse(report["formal_writeback_executed"])
            self.assertFalse(report["this_command_wrote_formal_state"])
            self.assertEqual(len(report["adapter_mappings"]), 6)
            groups = {mapping["writeback_target_group"] for mapping in report["adapter_mappings"]}
            self.assertEqual(
                groups,
                {
                    "formal_manuscript_sources",
                    "formal_bibliography_sources",
                    "method_review_records",
                    "statistical_result_records",
                    "reproducibility_records",
                    "formal_package_records",
                },
            )
            for mapping in report["adapter_mappings"]:
                self.assertEqual(mapping["mapping_status"], "ready_for_target_adapter")
                self.assertTrue(mapping["requires_target_adapter_execution"])
                self.assertFalse(mapping["executed_by_this_command"])
                self.assertTrue(mapping["candidate_targets"])
                self.assertTrue(all(target["path"].startswith("Submissions/auto_mode/") for target in mapping["candidate_targets"]))
                self.assertTrue(all(source["exists"] for source in mapping["source_artifacts"]))

    def test_bdd_p7n_blocks_when_apply_manifest_is_missing(self) -> None:
        """行为 2：当前没有 apply manifest 时不能生成 adapter mapping。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            package_manifest = self._write_package(project_root)

            report = build_auto_mode_formal_target_adapter_readiness(project_root, {}, package_manifest)

            self.assertEqual(report["status"], "blocked_by_apply_manifest")
            self.assertFalse(report["can_request_target_adapter_execution"])
            self.assertEqual(report["adapter_mappings"], [])
            self.assertIn("apply_manifest_missing_or_invalid_schema", report["blocking_reasons"])

    def test_bdd_p7n_unknown_target_group_blocks_mapping(self) -> None:
        """行为 3：未知 target group 必须阻断，不能猜测目标路径。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            package_manifest = self._write_package(project_root)
            apply_manifest = self._ready_apply_manifest()
            apply_manifest["operations"][0]["writeback_target_group"] = "unknown_target_group"

            report = build_auto_mode_formal_target_adapter_readiness(project_root, apply_manifest, package_manifest)

            self.assertEqual(report["status"], "blocked_by_target_adapter_mapping")
            self.assertFalse(report["can_request_target_adapter_execution"])
            self.assertIn("unknown_writeback_target_group:unknown_target_group", report["blocking_reasons"])

    def test_bdd_p7n_missing_package_artifact_blocks_readiness(self) -> None:
        """行为 4：映射需要真实 package source artifact。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            package_manifest = self._write_package(project_root, skip_targets={"paper.md"})

            report = build_auto_mode_formal_target_adapter_readiness(
                project_root,
                self._ready_apply_manifest(),
                package_manifest,
            )

            self.assertEqual(report["status"], "blocked_by_package_artifacts")
            self.assertFalse(report["can_request_target_adapter_execution"])
            self.assertIn("package_artifact_missing:paper.md", report["blocking_reasons"])

    def test_bdd_p7n_apply_manifest_boundary_violation_blocks_readiness(self) -> None:
        """行为 5：上游 manifest 有正式层越界标记时阻断。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            package_manifest = self._write_package(project_root)
            apply_manifest = self._ready_apply_manifest()
            apply_manifest["boundary_flags"]["modified_formal_manuscript"] = True

            report = build_auto_mode_formal_target_adapter_readiness(project_root, apply_manifest, package_manifest)

            self.assertEqual(report["status"], "blocked_by_apply_manifest_boundary")
            self.assertFalse(report["can_request_target_adapter_execution"])
            self.assertIn(
                "apply_manifest_boundary_violation:modified_formal_manuscript",
                report["blocking_reasons"],
            )

    def test_bdd_p7n_writes_review_outputs_without_creating_candidate_targets(self) -> None:
        """行为 1 补充：ready mapping 只写 report/review，不创建候选 target 文件。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            package_manifest = self._write_package(project_root)
            report = build_auto_mode_formal_target_adapter_readiness(
                project_root,
                self._ready_apply_manifest(),
                package_manifest,
            )

            report_path, review_path = write_auto_mode_formal_target_adapter_readiness_outputs(project_root, report)

            self.assertTrue(report_path.exists())
            self.assertTrue(review_path.exists())
            self.assertFalse((project_root / "Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md").exists())
            self.assertFalse((project_root / "state/product/auto_mode_formal_target_adapter_readiness.json").exists())

    def test_bdd_p7n_cli_defaults_to_current_missing_apply_manifest(self) -> None:
        """行为 6：CLI 默认 apply manifest 缺失时写 blocked readiness。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_package(project_root)

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_target_adapter_readiness.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=Path(__file__).resolve().parents[1],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_apply_manifest", result.stdout)
            self.assertIn("can_request_target_adapter_execution=false", result.stdout)
            self.assertIn("formal_target_adapters_executed=false", result.stdout)
            self.assertTrue((project_root / "Results/json/auto_mode_formal_target_adapter_readiness.json").exists())
            self.assertTrue((project_root / "Reviews/auto_mode_formal_target_adapter_readiness.md").exists())
            self.assertFalse((project_root / "Submissions/auto_mode/cgss_social_capital_happiness/manuscript/paper.md").exists())

    def _ready_apply_manifest(self) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_writeback_apply_manifest.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "source_execute_report": "Results/json/auto_mode_formal_writeback_execute.json",
            "manifest_path": "workspace/formal_writeback_apply/auto_mode/formal_writeback_apply_manifest.json",
            "reviewer": "unit_test_reviewer",
            "note": "Record apply manifest for target mapping tests.",
            "formal_writeback_executed": False,
            "formal_target_adapters_executed": False,
            "operations": [
                self._operation("01", "manuscript", "formal_manuscript_sources"),
                self._operation("02", "bibliography", "formal_bibliography_sources"),
                self._operation("03", "method_review", "method_review_records"),
                self._operation("04", "statistical_results", "statistical_result_records"),
                self._operation("05", "reproducibility", "reproducibility_records"),
                self._operation("06", "package_artifacts", "formal_package_records"),
            ],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _operation(self, index: str, category: str, target_group: str) -> dict:
        return {
            "operation_id": f"formal_writeback::{index}::{category}",
            "category": category,
            "label": category.replace("_", " ").title(),
            "writeback_target_group": target_group,
            "evidence_refs": [{"target": f"{category}.json", "kind": "unit_test"}],
            "operation_status": "planned_not_executed",
            "requires_target_adapter": True,
            "executed_by_this_command": False,
        }

    def _write_package(self, project_root: Path, skip_targets: set[str] | None = None) -> dict:
        skip_targets = skip_targets or set()
        package_dir = project_root / "workspace/paper_packages/cgss_social_capital_happiness"
        targets = [
            ("paper.md", "draft_layer"),
            ("literature_review_packet.json", "draft_layer"),
            ("method_gate.md", "human_review_required"),
            ("reviewer_report.md", "human_review_required"),
            ("revision_task_queue.md", "human_review_required"),
            ("results_evidence_package.json", "real_run"),
            ("reproducibility_readme.md", "generated_package_metadata"),
            ("manifest.json", "generated_package_metadata"),
            ("paper.pdf", "real_run"),
        ]
        files = []
        for target, kind in targets:
            files.append({"source": "", "target": target, "kind": kind})
            if target not in skip_targets:
                path = package_dir / target
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f"{target}\n", encoding="utf-8")
        manifest = {
            "schema_version": "p6.cgss_paper_package.v1",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "package_dir": "workspace/paper_packages/cgss_social_capital_happiness",
            "draft_layer_only": True,
            "formal_writeback_allowed": False,
            "files": files,
            "status": "needs_human_paper_package_review",
            "missing_targets": [],
        }
        manifest_path = package_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return manifest

    def _clean_boundary_flags(self) -> dict:
        return {
            "modified_formal_manuscript": False,
            "modified_formal_bibliography": False,
            "modified_project_bibliography": False,
            "modified_design_spec": False,
            "modified_run_plan": False,
            "modified_product_state": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "reran_models": False,
            "modified_statistical_execution_artifacts": False,
        }

    def _source_paths(self) -> dict:
        return {
            "apply_manifest": "workspace/formal_writeback_apply/auto_mode/formal_writeback_apply_manifest.json",
            "package_manifest": "workspace/paper_packages/cgss_social_capital_happiness/manifest.json",
        }


if __name__ == "__main__":
    unittest.main()
