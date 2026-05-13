import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class ApiContractV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="api-contract-v2-"))
        self.repo_root = self.temp_dir / "repo"
        self.project_root = self.temp_dir / "empirical-project"
        self.product_root = self.repo_root / "Product"
        self.product_root.mkdir(parents=True)
        self._create_minimal_project(self.project_root)
        ensure_registry(self.product_root, self.repo_root)
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)
        response = self.client.post(
            "/api/v1/projects",
            json={
                "slug": "contract-v2",
                "title": "API Contract V2 Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_overview_returns_six_stage_summaries(self) -> None:
        """行为 1：overview 必须聚合返回 6 个阶段摘要卡片。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/overview")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertIn("_meta", body)
        self.assertIn(body["_meta"]["evidence_level"], {"mock", "local_file"})
        self.assertEqual(len(body["stage_summaries"]), 6)
        for summary in body["stage_summaries"]:
            self.assert_required_keys(summary, {"stage_id", "title", "status", "progress", "summary"})

    def test_bdd_2_journey_returns_nine_required_stages(self) -> None:
        """行为 2：journey 必须返回 9 个研究旅程阶段。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/journey")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["_meta"]["evidence_level"], "mock")
        self.assertEqual(len(body["stages"]), 9)
        allowed_status = {"completed", "in_progress", "blocked", "not_started"}
        for stage in body["stages"]:
            self.assert_required_keys(stage, {"id", "name", "status", "progress", "href"})
            self.assertIn(stage["status"], allowed_status)
            self.assertGreaterEqual(stage["progress"], 0)
            self.assertLessEqual(stage["progress"], 1)

    def test_bdd_3_datasets_list_local_files_as_local_file_evidence(self) -> None:
        """行为 3：datasets API 必须列出项目内真实数据文件，而不是 mock 空状态。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/datasets")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["_meta"]["evidence_level"], "local_file")
        self.assertGreaterEqual(len(body["items"]), 1)
        dataset = body["items"][0]
        self.assert_required_keys(dataset, {"name", "path", "file_type", "size", "evidence_level", "role"})
        self.assertEqual(dataset["path"], "Data/Final/analysis_sample.csv")
        self.assertEqual(dataset["evidence_level"], "local_file")
        self.assertEqual(dataset["role"], "configured_final_dataset")
        self.assertEqual(dataset["row_count"], 1)
        self.assertEqual(dataset["column_count"], 4)

    def test_bdd_4_design_returns_minimum_renderable_state(self) -> None:
        """行为 4：research design API 必须给前端可渲染的设计状态。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/design")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["_meta"]["evidence_level"], "mock")
        self.assertIn("research_question", body)
        self.assertIn("variables", body)
        self.assertIn("strategies", body)
        self.assertIn("pending_confirmations", body)

    def test_bdd_5_drafts_read_real_manuscripts_as_local_file(self) -> None:
        """行为 5：drafts API 必须读取真实 Manuscripts/generated 文件。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/drafts")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["_meta"]["evidence_level"], "local_file")
        self.assertEqual(len(body["items"]), 2)
        paths = {item["path"] for item in body["items"]}
        self.assertIn("Manuscripts/generated/paper_draft.md", paths)
        self.assertIn("Manuscripts/generated/appendix.tex", paths)
        for draft in body["items"]:
            self.assert_required_keys(draft, {"chapter_id", "title", "path", "status"})

    def test_bdd_6_agents_list_separates_pipeline_and_dimension_roles(self) -> None:
        """行为 6：Agent 列表必须同时保留 pipeline roles 与 dimension roles。"""
        response = self.client.get("/api/v1/agents")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["_meta"]["evidence_level"], "mock")
        role_types = {agent["role_type"] for agent in body["items"]}
        self.assertEqual(role_types, {"pipeline", "dimension"})
        pipeline_ids = {agent["id"] for agent in body["items"] if agent["role_type"] == "pipeline"}
        self.assertEqual(
            pipeline_ids,
            {
                "pipeline_overview",
                "pipeline_data",
                "pipeline_design",
                "pipeline_execution",
                "pipeline_manuscript",
                "pipeline_artifacts",
                "pipeline_supervisor",
            },
        )
        self.assertEqual(len([agent for agent in body["items"] if agent["role_type"] == "dimension"]), 10)
        for agent in body["items"]:
            self.assert_required_keys(agent, {"id", "name", "role", "role_type", "status"})

    def test_bdd_7_agent_details_include_governance_fields(self) -> None:
        """行为 7：Agent 详情必须包含身份、权限、能力、成本、产物和审计日志。"""
        response = self.client.get("/api/v1/agents/pipeline_supervisor/details")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["_meta"]["evidence_level"], "mock")
        for key in ["identity", "permissions", "capabilities", "cost", "artifacts", "audit_log"]:
            self.assertIn(key, body)

    def test_bdd_8_artifact_provenance_returns_lineage(self) -> None:
        """行为 8：provenance 必须返回每个产物的可追溯 lineage。"""
        response = self.client.get("/api/v1/artifacts/mock_artifact_baseline/provenance")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["_meta"]["evidence_level"], "mock")
        self.assertEqual(body["artifact_id"], "mock_artifact_baseline")
        self.assertGreaterEqual(len(body["lineage"]), 1)
        for step in body["lineage"]:
            self.assert_required_keys(step, {"step", "type", "description", "actor"})

    def test_unknown_project_returns_structured_error_for_v2_get_endpoints(self) -> None:
        response = self.client.get("/api/v1/projects/proj_missing/overview")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "project_not_found")

    def test_unknown_agent_returns_structured_error(self) -> None:
        response = self.client.get("/api/v1/agents/not_real/details")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "agent_not_found")

    def test_unknown_provenance_artifact_returns_structured_error(self) -> None:
        response = self.client.get("/api/v1/artifacts/not_real/provenance")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "artifact_not_found")

    def assert_required_keys(self, payload: dict, keys: set[str]) -> None:
        missing = keys - payload.keys()
        self.assertFalse(missing, msg=f"Missing keys {missing} from {payload}")

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Program").mkdir(parents=True)
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Manuscripts" / "generated").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: contract-v2\n  title: API Contract V2 Project\n"
            "research:\n  question: 工业机器人如何影响劳动力市场匹配效率？\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu,experience\n10,1,16,3\n",
            encoding="utf-8",
        )
        (project_root / "Manuscripts" / "generated" / "paper_draft.md").write_text(
            "# 论文草稿\n\n本文件用于测试真实草稿读取。\n",
            encoding="utf-8",
        )
        (project_root / "Manuscripts" / "generated" / "appendix.tex").write_text(
            "\\section{Appendix}\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
