import json
import tempfile
import unittest
from pathlib import Path

from Program.workbench.statistical_adapter_contract import (
    build_statistical_adapter_contract,
    write_outputs,
)


class StatisticalAdapterContractTests(unittest.TestCase):
    """BDD: statistical execution artifacts must share an Auto Mode contract."""

    def test_bdd_p7g_normalizes_local_ols_and_iv_method_execution_results(self) -> None:
        """行为 1：本地 OLS/IV 执行结果被规范成同一统计结果结构。"""
        contract = build_statistical_adapter_contract(
            method_execution=self._method_execution_result(),
            cgss_results_evidence={},
            source_paths={"method_execution": "Results/json/method_execution_result.json"},
        )

        self.assertEqual(contract["schema_version"], "p7.statistical_adapter_contract.v1")
        self.assertEqual(contract["status"], "needs_human_statistical_adapter_review")
        results = {item["result_id"]: item for item in contract["normalized_results"]}
        ols = results["method_execution:baseline_ols"]
        self.assertEqual(ols["method_id"], "ols")
        self.assertEqual(ols["engine"], "statspai")
        self.assertEqual(ols["evidence_level"], "local_execution")
        self.assertEqual(ols["dataset_path"], "Data/Final/sample.csv")
        self.assertEqual(ols["formula"], "y ~ x + z")
        self.assertEqual(ols["nobs"], 100)
        self.assertEqual(ols["focal_estimate"]["term"], "x")
        self.assertEqual(ols["focal_estimate"]["coefficient"], 0.2)
        self.assertEqual(ols["focal_estimate"]["standard_error"], 0.05)
        self.assertEqual(ols["focal_estimate"]["p_value"], 0.01)
        self.assertEqual(ols["contract_status"], "contract_ready")

        iv = results["method_execution:iv_2sls"]
        self.assertEqual(iv["method_id"], "iv")
        self.assertEqual(iv["outcome"], "lwage")
        self.assertEqual(iv["focal_estimate"]["term"], "educ")
        self.assertIn("First-stage F", iv["diagnostics"])
        self.assertEqual(iv["reproducibility"]["adapter"], "statspai_iv")

    def test_bdd_p7g_normalizes_cgss_ols_and_ordered_logit_evidence(self) -> None:
        """行为 2：CGSS OLS 与 Ordered Logit 证据进入同一 contract。"""
        contract = build_statistical_adapter_contract(
            method_execution={},
            cgss_results_evidence=self._cgss_results_evidence(),
            source_paths={"cgss_results_evidence": "workspace/paper_packages/cgss/results_evidence_package.json"},
        )

        results = {item["result_id"]: item for item in contract["normalized_results"]}
        self.assertEqual(results["cgss_results_evidence:ols"]["method_id"], "ols")
        self.assertEqual(results["cgss_results_evidence:ordered_logit"]["method_id"], "ordered_logit")
        self.assertEqual(results["cgss_results_evidence:ordered_logit"]["ordered_outcome_levels"], [1, 2, 3, 4, 5])
        self.assertEqual(results["cgss_results_evidence:ordered_logit"]["focal_estimate"]["coefficient"], 0.405)
        self.assertTrue(contract["source_consistency"]["sample_nobs_match"])
        self.assertEqual(contract["source_consistency"]["ordered_method_gate"], "passed")

    def test_bdd_p7g_reports_capability_matrix_and_incomplete_methods(self) -> None:
        """行为 3：capability matrix 标明可消费方法和缺字段方法。"""
        method_execution = self._method_execution_result()
        method_execution["methods"].append(
            {
                "task_id": "did_incomplete",
                "method_id": "did",
                "estimator": "did",
                "evidence_level": "local_execution",
            }
        )

        contract = build_statistical_adapter_contract(
            method_execution=method_execution,
            cgss_results_evidence={},
            source_paths={"method_execution": "Results/json/method_execution_result.json"},
        )

        matrix = contract["capability_matrix"]
        self.assertEqual(matrix["ols"]["contract_ready_count"], 1)
        self.assertEqual(matrix["iv"]["contract_ready_count"], 1)
        self.assertEqual(matrix["did"]["incomplete_count"], 1)
        incomplete = next(item for item in contract["normalized_results"] if item["result_id"] == "method_execution:did_incomplete")
        self.assertEqual(incomplete["contract_status"], "needs_mapping_review")
        self.assertIn("formula", incomplete["missing_required_fields"])
        self.assertIn("nobs", incomplete["missing_required_fields"])
        self.assertIn("focal_estimate", incomplete["missing_required_fields"])

    def test_bdd_p7g_writes_json_and_review_without_formal_writeback(self) -> None:
        """行为 4：输出 contract JSON 和审阅 Markdown，不重跑模型或写正式层。"""
        contract = build_statistical_adapter_contract(
            method_execution=self._method_execution_result(),
            cgss_results_evidence=self._cgss_results_evidence(),
            source_paths=self._source_paths(),
        )

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp) / "project"
            report_path, review_path = write_outputs(
                project_root,
                contract,
                Path("Results/json/statistical_adapter_contract.json"),
                Path("Reviews/statistical_adapter_contract.md"),
            )

            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["status"], "needs_human_statistical_adapter_review")
            review = review_path.read_text(encoding="utf-8")
            self.assertIn("Statistical Adapter Contract", review)
            self.assertIn("正式层写回：否", review)
            self.assertIn("模型重跑：否", review)
            self.assertFalse((project_root / "state/product/statistical_adapter_contract.json").exists())
            self.assertFalse((project_root / "Results/json/method_execution_result.json").exists())
            self.assertFalse(contract["boundary_flags"]["modified_product_state"])
            self.assertFalse(contract["boundary_flags"]["reran_models"])

    def test_bdd_p7g_blocks_when_statistical_sources_are_missing(self) -> None:
        """行为 5：缺少统计来源时阻断，不伪造 normalized results。"""
        contract = build_statistical_adapter_contract(
            method_execution={},
            cgss_results_evidence={},
            source_paths={},
        )

        self.assertEqual(contract["status"], "blocked_missing_statistical_sources")
        self.assertEqual(contract["normalized_results"], [])
        self.assertIn("method_execution", contract["missing_sources"])
        self.assertIn("cgss_results_evidence", contract["missing_sources"])

    def _method_execution_result(self) -> dict:
        return {
            "id": "method_execution_result",
            "engine": "statspai",
            "evidence_level": "local_execution",
            "execution_contract": {"active_backend": "statspai"},
            "methods": [
                {
                    "task_id": "baseline_ols",
                    "method_id": "ols",
                    "estimator": "ols",
                    "formula": "y ~ x + z",
                    "dataset_path": "Data/Final/sample.csv",
                    "nobs": 100,
                    "dependent_var": "y",
                    "treatment": "x",
                    "coefficients": {"x": 0.2, "z": 1.5},
                    "standard_errors": {"x": 0.05, "z": 0.2},
                    "p_values": {"x": 0.01, "z": 0.03},
                    "confidence_intervals": {"x": {"level": 0.95, "low": 0.1, "high": 0.3}},
                    "diagnostics": {"R-squared": 0.5},
                    "reproducibility": {
                        "adapter": "python_ols_adapter",
                        "result_artifact_path": "Results/json/method_execution_result.json",
                    },
                    "evidence_level": "local_execution",
                },
                {
                    "task_id": "iv_2sls",
                    "method_id": "iv",
                    "estimator": "iv",
                    "formula": "lwage ~ (educ ~ nearc4) + exper",
                    "dataset_path": "Data/Final/card.csv",
                    "nobs": 50,
                    "dependent_var": "lwage",
                    "treatment": "educ",
                    "coefficients": {"educ": 0.08, "exper": 0.02},
                    "standard_errors": {"educ": 0.03, "exper": 0.01},
                    "p_values": {"educ": 0.02, "exper": 0.04},
                    "diagnostics": {"First-stage F": 14.2},
                    "reproducibility": {"adapter": "statspai_iv"},
                    "evidence_level": "local_execution",
                },
            ],
        }

    def _cgss_results_evidence(self) -> dict:
        return {
            "schema_version": "p6.cgss_results_evidence_package.v1",
            "status": "ready_for_paper_draft_input",
            "dataset": {"path": "CGSS2023.dta", "year": "2023"},
            "variables": {
                "outcome": "happiness <- a36",
                "social_capital": {"index": "social_capital_index"},
                "controls": ["female", "age", "education_level"],
                "ordered_outcome_levels": [1, 2, 3, 4, 5],
            },
            "primary_result": {
                "ols": {
                    "model": "baseline_index",
                    "variable": "social_capital_index",
                    "coef": 0.1658,
                    "std_error": 0.0187,
                    "p_value": 0.0,
                    "nobs": 5310,
                },
                "ordered_logit": {
                    "model": "ordered_logit_index",
                    "variable": "social_capital_index",
                    "coef": 0.405,
                    "std_error": 0.0424,
                    "p_value": 0.0,
                    "nobs": 5310,
                    "outcome_levels": [1, 2, 3, 4, 5],
                },
            },
            "evidence_consistency": {
                "sample_nobs_match": True,
                "ordered_method_gate": "passed",
                "social_capital_direction": "consistent_positive",
            },
        }

    def _source_paths(self) -> dict:
        return {
            "method_execution": "Results/json/method_execution_result.json",
            "cgss_results_evidence": "workspace/paper_packages/cgss/results_evidence_package.json",
        }


if __name__ == "__main__":
    unittest.main()
