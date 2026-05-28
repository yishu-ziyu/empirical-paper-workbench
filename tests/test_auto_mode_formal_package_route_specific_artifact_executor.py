import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_mode_formal_package_route_specific_artifact_executor import (
    run_auto_mode_formal_package_route_specific_artifact_executor,
    write_auto_mode_formal_package_route_specific_artifact_executor_outputs,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutoModeFormalPackageRouteSpecificArtifactExecutorTests(unittest.TestCase):
    """BDD: P7-AB dispatches one selected formal package route to its artifact command."""

    def test_bdd_p7ab_ready_execute_manifest_dry_run_plans_route_without_artifacts(self) -> None:
        """行为 1：ready manifest 可 dry-run 看到 delegated command，但不写产物。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report, exit_code = run_auto_mode_formal_package_route_specific_artifact_executor(
                project_root,
                self._ready_selected_route_execute("pdf_export"),
                self._execute_manifest("pdf_export"),
                mode="dry-run",
                source_paths=self._source_paths(),
            )

            self.assertEqual(exit_code, 0)
            self.assertEqual(report["schema_version"], "p7.auto_mode_formal_package_route_specific_artifact_executor.v1")
            self.assertEqual(report["status"], "route_specific_artifact_executor_dry_run_ready")
            self.assertTrue(report["can_execute_route_specific_artifact_with_confirmation"])
            self.assertFalse(report["route_specific_artifact_executed"])
            self.assertEqual(report["route_type"], "pdf_export")
            self.assertIn("Program/formal_pdf_final_writeback.py", report["route_specific_command"])
            self.assertFalse((project_root / "Submissions/formal_package/paper.pdf").exists())

    def test_bdd_p7ab_current_blocked_selected_route_execute_blocks_executor(self) -> None:
        """行为 2：当前 P7-AA blocked 时不能调任何产物命令。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            report, exit_code = run_auto_mode_formal_package_route_specific_artifact_executor(
                project_root,
                self._blocked_selected_route_execute(),
                {},
                mode="dry-run",
            )

            self.assertEqual(exit_code, 2)
            self.assertEqual(report["status"], "blocked_by_selected_route_execute")
            self.assertFalse(report["can_execute_route_specific_artifact_with_confirmation"])
            self.assertFalse(report["route_specific_command_executed"])
            self.assertEqual(report["route_specific_command"], [])
            self.assertIn("selected_route_execute_not_manifest_recorded", report["blocking_reasons"])

    def test_bdd_p7ab_missing_invalid_report_or_manifest_blocks_execution(self) -> None:
        """行为 3：execute report 或 manifest 缺失/错误时阻断。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            missing_report, _ = run_auto_mode_formal_package_route_specific_artifact_executor(
                project_root,
                {},
                {},
                mode="dry-run",
            )
            invalid_manifest, _ = run_auto_mode_formal_package_route_specific_artifact_executor(
                project_root,
                self._ready_selected_route_execute("pdf_export"),
                {"schema_version": "wrong.schema"},
                mode="dry-run",
            )

            self.assertEqual(missing_report["status"], "blocked_by_selected_route_execute")
            self.assertIn("selected_route_execute_missing_or_invalid_schema", missing_report["blocking_reasons"])
            self.assertEqual(invalid_manifest["status"], "blocked_by_selected_route_execute_manifest")
            self.assertIn("selected_route_execute_manifest_missing_or_invalid_schema", invalid_manifest["blocking_reasons"])

    def test_bdd_p7ab_bad_route_operation_contract_blocks_execution(self) -> None:
        """行为 4：manifest 内路线不干净时阻断。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            unknown = self._execute_manifest("pdf_export")
            unknown["selected_route_execute_operations"][0]["route_type"] = "unknown_route"
            duplicated = self._execute_manifest("pdf_export")
            duplicated["selected_route_execute_operations"].append(dict(duplicated["selected_route_execute_operations"][0]))
            already_marked = self._execute_manifest("pdf_export")
            already_marked["selected_route_execute_operations"][0]["will_execute_selected_route"] = True
            no_outputs = self._execute_manifest("pdf_export")
            no_outputs["selected_route_execute_operations"][0]["planned_outputs"] = []

            reports = [
                run_auto_mode_formal_package_route_specific_artifact_executor(
                    project_root,
                    self._ready_selected_route_execute("pdf_export"),
                    manifest,
                    mode="dry-run",
                )[0]
                for manifest in [unknown, duplicated, already_marked, no_outputs]
            ]

            self.assertTrue(all(report["status"] == "blocked_by_route_specific_artifact_contract" for report in reports))
            self.assertIn("route_type_unknown:unknown_route", reports[0]["blocking_reasons"])
            self.assertIn("selected_route_execute_operations_not_single", reports[1]["blocking_reasons"])
            self.assertIn("route_operation_marked_execute_by_this_command:pdf_export", reports[2]["blocking_reasons"])
            self.assertIn("route_operation_planned_outputs_missing:pdf_export", reports[3]["blocking_reasons"])

    def test_bdd_p7ab_execute_requires_confirmation_and_metadata(self) -> None:
        """行为 5：execute 必须有 confirm、reviewer 和 note。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            no_confirm, _ = run_auto_mode_formal_package_route_specific_artifact_executor(
                project_root,
                self._ready_selected_route_execute("pdf_export"),
                self._execute_manifest("pdf_export"),
                mode="execute",
                confirm_artifact_execution=False,
                reviewer="unit-test",
                note="execute route",
            )
            no_metadata, _ = run_auto_mode_formal_package_route_specific_artifact_executor(
                project_root,
                self._ready_selected_route_execute("pdf_export"),
                self._execute_manifest("pdf_export"),
                mode="execute",
                confirm_artifact_execution=True,
                reviewer="",
                note="",
            )

            self.assertEqual(no_confirm["status"], "blocked_by_missing_artifact_execution_confirmation")
            self.assertIn("confirm_artifact_execution_required", no_confirm["blocking_reasons"])
            self.assertEqual(no_metadata["status"], "blocked_by_artifact_execution_metadata")
            self.assertIn("reviewer_required", no_metadata["blocking_reasons"])
            self.assertIn("artifact_execution_note_required", no_metadata["blocking_reasons"])

    def test_bdd_p7ab_confirmed_pdf_and_docx_routes_delegate_to_artifact_commands(self) -> None:
        """行为 6：确认 PDF/DOCX 路线会调用真实产物命令。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "pdf-project"
            self._seed_pdf_route_project(project_root)

            pdf_report, pdf_exit = run_auto_mode_formal_package_route_specific_artifact_executor(
                project_root,
                self._ready_selected_route_execute("pdf_export"),
                self._execute_manifest("pdf_export"),
                mode="execute",
                confirm_artifact_execution=True,
                reviewer="unit-test",
                note="Execute PDF route.",
            )

            self.assertEqual(pdf_exit, 0, pdf_report["route_specific_result"])
            self.assertEqual(pdf_report["status"], "route_specific_artifact_executed")
            self.assertEqual(pdf_report["delegated_status"], "final_pdf_written")
            self.assertTrue(pdf_report["rendered_pdf"])
            self.assertTrue((project_root / "Submissions/formal_package/paper.pdf").exists())
            self.assertFalse((project_root / "Submissions/formal_package/paper.docx").exists())

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "docx-project"
            self._seed_docx_route_project(project_root)
            old_path = os.environ.get("PATH", "")
            fake_bin = self._install_fake_pandoc(project_root)
            os.environ["PATH"] = f"{fake_bin}{os.pathsep}{old_path}"
            try:
                docx_report, docx_exit = run_auto_mode_formal_package_route_specific_artifact_executor(
                    project_root,
                    self._ready_selected_route_execute("docx_export"),
                    self._execute_manifest("docx_export"),
                    mode="execute",
                    confirm_artifact_execution=True,
                    reviewer="unit-test",
                    note="Execute DOCX route.",
                )
            finally:
                os.environ["PATH"] = old_path

            self.assertEqual(docx_exit, 0, docx_report["route_specific_result"])
            self.assertEqual(docx_report["status"], "route_specific_artifact_executed")
            self.assertEqual(docx_report["delegated_status"], "docx_exported")
            self.assertTrue(docx_report["rendered_docx"])
            self.assertTrue((project_root / "Submissions/formal_package/paper.docx").exists())

    def test_bdd_p7ab_confirmed_package_and_manual_routes_delegate_to_artifact_commands(self) -> None:
        """行为 7：确认 package manifest/manual acceptance 路线会调用真实产物命令。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "package-project"
            self._seed_package_manifest_route_project(project_root)

            package_report, package_exit = run_auto_mode_formal_package_route_specific_artifact_executor(
                project_root,
                self._ready_selected_route_execute("package_manifest"),
                self._execute_manifest("package_manifest"),
                mode="execute",
                confirm_artifact_execution=True,
                reviewer="unit-test",
                note="Execute package manifest route.",
            )

            self.assertEqual(package_exit, 0, package_report["route_specific_result"])
            self.assertEqual(package_report["status"], "route_specific_artifact_executed")
            self.assertEqual(package_report["delegated_status"], "formal_submission_package_ready")
            self.assertTrue(package_report["package_manifest_generated"])
            self.assertTrue((project_root / "Submissions/formal_package/manifest.json").exists())

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "manual-project"
            self._seed_manual_acceptance_route_project(project_root)

            manual_report, manual_exit = run_auto_mode_formal_package_route_specific_artifact_executor(
                project_root,
                self._ready_selected_route_execute("manual_acceptance"),
                self._execute_manifest("manual_acceptance"),
                mode="execute",
                confirm_artifact_execution=True,
                reviewer="mahaoxuan",
                note="PDF and DOCX manually accepted.",
                manual_decision="accept",
            )

            self.assertEqual(manual_exit, 0, manual_report["route_specific_result"])
            self.assertEqual(manual_report["status"], "route_specific_artifact_executed")
            self.assertEqual(manual_report["delegated_status"], "formal_submission_package_accepted")
            self.assertTrue(manual_report["manual_acceptance_performed"])
            self.assertTrue(manual_report["can_write_product_state"])
            state_path = project_root / "state/product/formal_submission_package_manual_acceptance.json"
            self.assertTrue(state_path.exists())
            self.assertTrue(json.loads(state_path.read_text(encoding="utf-8"))["accepted"])

    def test_bdd_p7ab_cli_defaults_to_current_blocked_execute_report(self) -> None:
        """行为 8：CLI 默认读取当前 blocked P7-AA，写 blocked executor report。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self._write_json(
                project_root / "Results/json/auto_mode_formal_package_selected_route_execute.json",
                self._blocked_selected_route_execute(),
            )

            import subprocess

            result = subprocess.run(
                [
                    "python3",
                    "Program/auto_mode_formal_package_route_specific_artifact_executor.py",
                    "--project-root",
                    str(project_root),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("status=blocked_by_selected_route_execute", result.stdout)
            self.assertIn("route_specific_command_executed=false", result.stdout)
            self.assertTrue(
                (project_root / "Results/json/auto_mode_formal_package_route_specific_artifact_executor.json").exists()
            )
            self.assertTrue((project_root / "Reviews/auto_mode_formal_package_route_specific_artifact_executor.md").exists())
            self.assertFalse((project_root / "Results/json/formal_pdf_final_writeback.json").exists())

    def _ready_selected_route_execute(self, route_type: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_selected_route_execute.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "status": "selected_route_execute_manifest_recorded",
            "mode": "execute",
            "confirm_execute": True,
            "can_execute_selected_route_with_confirmation": True,
            "selected_route_execute_manifest_recorded": True,
            "selected_route_execute_manifest_path": (
                "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
            ),
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "package_manifest_generated": False,
            "manual_acceptance_performed": False,
            "formal_writeback_executed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "blocking_reasons": [],
            "selected_route_execute_operations": [self._route_operation(route_type)],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _blocked_selected_route_execute(self) -> dict:
        report = self._ready_selected_route_execute("pdf_export")
        report["status"] = "blocked_by_selected_route_execution_preflight"
        report["mode"] = "dry-run"
        report["confirm_execute"] = False
        report["can_execute_selected_route_with_confirmation"] = False
        report["selected_route_execute_manifest_recorded"] = False
        report["selected_route_execute_manifest_path"] = ""
        report["blocking_reasons"] = ["selected_route_execution_preflight_not_ready"]
        report["selected_route_execute_operations"] = []
        return report

    def _execute_manifest(self, route_type: str) -> dict:
        return {
            "schema_version": "p7.auto_mode_formal_package_selected_route_execute_manifest.v1",
            "generated_at": "2026-05-28T00:00:00+00:00",
            "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
            "selected_route_executed": False,
            "export_or_acceptance_executed": False,
            "rendered_pdf": False,
            "rendered_docx": False,
            "package_manifest_generated": False,
            "manual_acceptance_performed": False,
            "this_command_wrote_formal_state": False,
            "can_write_product_state": False,
            "selected_route_execute_operations": [self._route_operation(route_type)],
            "boundary_flags": self._clean_boundary_flags(),
        }

    def _route_operation(self, route_type: str) -> dict:
        planned_outputs = {
            "pdf_export": ["Submissions/formal_package/paper.pdf"],
            "docx_export": ["Submissions/formal_package/paper.docx"],
            "package_manifest": ["Submissions/formal_package/manifest.json"],
            "manual_acceptance": ["Reviews/formal_package_manual_acceptance.md"],
        }[route_type]
        routed_action = {
            "pdf_export": "formal_pdf_export_preflight",
            "docx_export": "formal_docx_export_preflight",
            "package_manifest": "formal_submission_package_manifest_preflight",
            "manual_acceptance": "manual_acceptance_packet_preflight",
        }[route_type]
        return {
            "operation_id": f"selected_route_execute::{route_type}",
            "route_execution_id": f"selected_formal_package_route_execution::{routed_action}",
            "routed_action": routed_action,
            "route_type": route_type,
            "next_command": f"formal_{route_type}_execute",
            "planned_outputs": planned_outputs,
            "operation_status": "planned_not_executed",
            "will_execute_selected_route": False,
            "will_render_pdf": False,
            "will_render_docx": False,
            "will_generate_package_manifest": False,
            "will_perform_manual_acceptance": False,
            "will_write_product_state": False,
        }

    def _seed_pdf_route_project(self, root: Path) -> None:
        results = root / "Results/json"
        state = root / "state/product"
        package = root / "Submissions/formal_package"
        manuscript = package / "manuscript"
        for directory in [results, state, manuscript]:
            directory.mkdir(parents=True, exist_ok=True)
        self._seed_protected_state(state)
        (manuscript / "paper_candidate.qmd").write_text("# Candidate\n", encoding="utf-8")
        candidate_pdf = package / "paper_candidate.pdf"
        candidate_pdf.write_bytes(b"%PDF-1.4\n% candidate pdf\n")
        self._write_json(
            results / "formal_pdf_candidate_report.json",
            {
                "schema_version": "p5.formal_pdf_candidate.v1",
                "status": "pdf_candidate_ready",
                "candidate_layer_only": True,
                "output_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                "output_pdf": "Submissions/formal_package/paper_candidate.pdf",
                "output_pdf_exists": True,
                "this_command_wrote_formal_state": False,
                "this_command_wrote_final_outputs": False,
                "formal_state_guard": {"changed": False, "changed_paths": []},
            },
        )
        self._write_json(
            results / "formal_pdf_final_writeback_preflight.json",
            {
                "schema_version": "p5.formal_pdf_final_writeback_preflight.v1",
                "status": "ready_for_human_final_approval",
                "can_request_final_approval": True,
                "candidate_pdf": "Submissions/formal_package/paper_candidate.pdf",
                "candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                "formal_state_guard": {"changed": False, "changed_paths": []},
            },
        )
        self._write_json(
            results / "formal_pdf_final_approval.json",
            {
                "schema_version": "p5.formal_pdf_final_approval.v1",
                "status": "approved_for_final_writeback",
                "can_enter_p6": True,
                "final_writeback_authorized": True,
                "candidate_pdf": "Submissions/formal_package/paper_candidate.pdf",
                "candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
            },
        )
        self._write_json(
            state / "writeback_approvals.json",
            {
                "schema_version": "product.writeback_approvals.v1",
                "final_pdf_approvals": {
                    "formal_pdf_candidate": {
                        "status": "approved",
                        "can_enter_p6": True,
                        "final_writeback_authorized": True,
                        "candidate_pdf": "Submissions/formal_package/paper_candidate.pdf",
                        "candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                    }
                },
            },
        )

    def _seed_docx_route_project(self, root: Path) -> None:
        results = root / "Results/json"
        state = root / "state/product"
        package = root / "Submissions/formal_package"
        manuscript = package / "manuscript"
        manuscripts = root / "Manuscripts"
        for directory in [results, state, manuscript, manuscripts]:
            directory.mkdir(parents=True, exist_ok=True)
        self._seed_protected_state(state)
        (manuscripts / "references.bib").write_text("", encoding="utf-8")
        (package / "paper.pdf").write_bytes(b"%PDF-1.4\n% final pdf\n")
        (manuscript / "paper_candidate.qmd").write_text("# Candidate\n\nDocx source.\n", encoding="utf-8")
        self._write_json(
            results / "formal_docx_export_preflight.json",
            {
                "schema_version": "p6.formal_docx_export_preflight.v1",
                "status": "ready_for_docx_export",
                "source_candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                "final_pdf": "Submissions/formal_package/paper.pdf",
                "expected_docx": "Submissions/formal_package/paper.docx",
                "can_export_docx": True,
                "blocking_reasons": [],
                "this_command_wrote_docx": False,
                "this_command_wrote_formal_state": False,
                "formal_state_guard": {"changed": False, "changed_paths": []},
            },
        )

    def _seed_package_manifest_route_project(self, root: Path) -> None:
        results = root / "Results/json"
        logs = root / "Results/logs"
        state = root / "state/product"
        package = root / "Submissions/formal_package"
        manuscript = package / "manuscript"
        for directory in [results, logs, state, manuscript, root / "Submissions"]:
            directory.mkdir(parents=True, exist_ok=True)
        self._seed_protected_state(state)
        pdf = package / "paper.pdf"
        docx = package / "paper.docx"
        candidate_qmd = manuscript / "paper_candidate.qmd"
        pdf.write_bytes(b"%PDF-1.4\n% final pdf\n")
        docx.write_bytes(b"PK\x03\x04 final docx\n")
        candidate_qmd.write_text("# Candidate\n", encoding="utf-8")
        (logs / "formal_docx_export.log").write_text("ok\n", encoding="utf-8")
        (root / "Submissions/export_manifest.json").write_text(json.dumps({"status": "exported"}), encoding="utf-8")
        self._write_json(
            results / "formal_pdf_final_writeback.json",
            {
                "schema_version": "p6.formal_pdf_final_writeback.v1",
                "status": "final_pdf_written",
                "source_candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                "final_pdf": "Submissions/formal_package/paper.pdf",
                "final_pdf_sha256": self._sha256(pdf),
                "final_pdf_bytes": pdf.stat().st_size,
                "this_command_wrote_final_pdf": True,
                "this_command_wrote_docx": False,
                "this_command_wrote_formal_state": False,
                "formal_state_guard": {"changed": False, "changed_paths": []},
            },
        )
        self._write_json(
            results / "formal_docx_export_preflight.json",
            {
                "schema_version": "p6.formal_docx_export_preflight.v1",
                "status": "ready_for_docx_export",
                "can_export_docx": True,
                "expected_docx": "Submissions/formal_package/paper.docx",
                "source_candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                "final_pdf": "Submissions/formal_package/paper.pdf",
                "blocking_reasons": [],
                "formal_state_guard": {"changed": False, "changed_paths": []},
            },
        )
        self._write_json(
            results / "formal_docx_export.json",
            {
                "schema_version": "p6.formal_docx_export.v1",
                "status": "docx_exported",
                "source_candidate_qmd": "Submissions/formal_package/manuscript/paper_candidate.qmd",
                "final_pdf": "Submissions/formal_package/paper.pdf",
                "docx": "Submissions/formal_package/paper.docx",
                "docx_sha256": self._sha256(docx),
                "docx_bytes": docx.stat().st_size,
                "blocking_reasons": [],
                "this_command_wrote_docx": True,
                "this_command_wrote_pdf": False,
                "this_command_wrote_formal_state": False,
                "formal_state_guard": {"changed": False, "changed_paths": []},
            },
        )

    def _seed_manual_acceptance_route_project(self, root: Path) -> None:
        self._seed_package_manifest_route_project(root)
        state = root / "state/product"
        package = root / "Submissions/formal_package"
        self._write_json(package / "manifest.json", {"status": "formal_submission_package_ready"})
        pdf = package / "paper.pdf"
        docx = package / "paper.docx"
        self._write_json(
            state / "formal_submission_package_summary.json",
            {
                "schema_version": "p6.formal_submission_package_summary.v1",
                "status": "ready_for_manual_acceptance",
                "ready_for_manual_acceptance": True,
                "artifacts": {
                    "paper_pdf": {
                        "path": "Submissions/formal_package/paper.pdf",
                        "exists": True,
                        "bytes": pdf.stat().st_size,
                        "sha256": self._sha256(pdf),
                    },
                    "paper_docx": {
                        "path": "Submissions/formal_package/paper.docx",
                        "exists": True,
                        "bytes": docx.stat().st_size,
                        "sha256": self._sha256(docx),
                    },
                },
                "blocking_reasons": [],
                "formal_state_guard": {"changed": False, "changed_paths": []},
            },
        )

    def _install_fake_pandoc(self, project_root: Path) -> Path:
        fake_bin = project_root / "fake-bin"
        fake_bin.mkdir(parents=True, exist_ok=True)
        script = fake_bin / "pandoc"
        script.write_text(
            "#!/usr/bin/env python3\n"
            "import sys, zipfile\n"
            "out = sys.argv[sys.argv.index('-o') + 1]\n"
            "with zipfile.ZipFile(out, 'w') as archive:\n"
            "    archive.writestr('[Content_Types].xml', '<Types/>')\n",
            encoding="utf-8",
        )
        script.chmod(0o755)
        return fake_bin

    def _seed_protected_state(self, state: Path) -> None:
        for name in [
            "research_question.json",
            "variable_roles.json",
            "variable_role_set.json",
            "design_spec.json",
            "run_plan.json",
            "supervisor_plan.json",
            "agent_task_queue.json",
        ]:
            self._write_json(state / name, {"name": name, "formal": True})

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
            "executed_target_adapters": False,
            "wrote_formal_state": False,
            "created_or_repaired_candidate_targets": False,
            "promoted_candidate_targets": False,
            "exported_or_accepted_formal_package": False,
            "generated_package_manifest": False,
            "performed_manual_acceptance": False,
        }

    def _source_paths(self) -> dict:
        return {
            "selected_route_execute": "Results/json/auto_mode_formal_package_selected_route_execute.json",
            "selected_route_execute_manifest": (
                "workspace/formal_package_selected_route_execute/auto_mode/selected_route_execute_manifest.json"
            ),
        }

    def _write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _sha256(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()
