from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.product_control_phase_service import run_product_control_p0_phase
from Product.backend.registry import ensure_registry


class ProductControlP0StagePanelApiTests(unittest.TestCase):
    """BDD: P0 control panel needs a read-only report API distinct from refresh."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="p0-panel-"))
        self.repo_root = self.tmp / "repo"
        self.product_root = self.repo_root / "Product"
        self.project_root = self.tmp / "project"
        self.product_root.mkdir(parents=True)
        self._create_project()
        ensure_registry(self.product_root, self.repo_root)
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)
        response = self.client.post(
            "/api/v1/projects",
            json={
                "slug": "p0-panel",
                "title": "P0 Panel Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.tmp)

    def test_bdd_1_get_p0_phase_returns_existing_report_without_refreshing(self) -> None:
        """行为 1：GET 只读返回已有阶段报告，不重新生成覆盖。"""
        run_product_control_p0_phase(self.project_root)
        report_path = self.project_root / "Results/json/product_control_p0_phase.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["read_marker"] = "should_survive_get"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p0-phase")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "p0_phase_ready_for_review")
        self.assertEqual(body["read_marker"], "should_survive_get")
        self.assertEqual(body["project"]["id"], self.project_id)
        self.assertEqual(
            json.loads(report_path.read_text(encoding="utf-8"))["read_marker"],
            "should_survive_get",
        )

    def test_bdd_2_get_p0_phase_reports_missing_state(self) -> None:
        """行为 2：没有 P0 report 时，GET 必须显式提示可刷新。"""
        response = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p0-phase")

        self.assertEqual(response.status_code, 200, msg=response.text)
        body = response.json()
        self.assertEqual(body["status"], "p0_phase_report_missing")
        self.assertTrue(body["can_refresh"])
        self.assertEqual(body["refresh_endpoint"], f"/api/v1/projects/{self.project_id}/product-control/p0-phase")

    def test_bdd_2b_legacy_entry_redirects_to_react_main_entry(self) -> None:
        """行为 2b：旧工作台不能继续作为产品验收入口。"""
        response = self.client.get("/legacy", follow_redirects=False)

        self.assertEqual(response.status_code, 307, msg=response.text)
        self.assertEqual(response.headers["location"], "/")

    def _create_project(self) -> None:
        topic = "数字普惠金融对家庭创业的影响"
        slug = "digital-finance-entrepreneurship"
        self._write_text("paper.yaml", f"research:\n  question: {topic}\n")
        self._write_text("Program/run_paper.py", "print('ok')\n")
        self._write_json(
            "state/product/topic_binding.json",
            {
                "expected_topic": topic,
                "expected_slug": slug,
                "binding_type": "project_topic_binding",
            },
        )
        self._write_json("state/product/research_question.json", {"status": "confirmed", "question": topic})
        self._write_text(f"Tasks/{slug}/brief.md", f"# {topic}\n")
        self._write_text(f"Tasks/{slug}/literature.md", "# Literature\n\n等待真实文献检索。\n")
        self._write_text(f"Tasks/{slug}/variables.yaml", f"topic_slug: {slug}\nvariables:\n  - treatment\n")
        self._write_json(f"Tasks/{slug}/design.json", {"topic": topic})

    def _write_text(self, relative_path: str, content: str) -> None:
        path = self.project_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _write_json(self, relative_path: str, payload: dict) -> None:
        self._write_text(relative_path, json.dumps(payload, ensure_ascii=False, indent=2))


class ProductControlP0StagePanelReactTests(unittest.TestCase):
    """BDD: P0 phase panel remains historical source but is no longer a main workbench surface."""

    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.react_root = root / "Product" / "web-react" / "src"
        cls.app_tsx = (cls.react_root / "App.tsx").read_text(encoding="utf-8")
        cls.component_path = cls.react_root / "components" / "ProductControlP0Panel.tsx"
        cls.component = cls.component_path.read_text(encoding="utf-8") if cls.component_path.exists() else ""
        cls.styles = (cls.react_root / "styles.css").read_text(encoding="utf-8")

    def test_bdd_3_react_main_entry_does_not_mount_p0_stage_panel(self) -> None:
        """行为 3：当前 React 主入口不能再挂载 P0 控制面板。"""
        self.assertTrue(self.component_path.exists(), "React ProductControlP0Panel component is missing.")
        self.assertNotIn("ProductControlP0Panel", self.app_tsx)
        self.assertNotIn("<ProductControlP0Panel", self.app_tsx)
        self.assertIn("PaperProductionStatusPanel", self.app_tsx)
        self.assertIn("product-control-p0-panel", self.component)
        self.assertIn("产品控制 P0", self.component)

    def test_bdd_4_frontend_exposes_evidence_gaps_and_formal_boundary(self) -> None:
        """行为 4：P0 面板必须暴露 needs_evidence 和正式层边界。"""
        self.assertIn("needs_evidence", self.component)
        self.assertIn("不能进入正式论文", self.component)
        self.assertIn("真实文献", self.component)
        self.assertIn("数据与变量", self.component)
        self.assertIn("方法执行", self.component)

    def test_bdd_5_frontend_refreshes_p0_phase_with_explicit_post(self) -> None:
        """行为 5：刷新按钮必须调用 POST 并更新面板状态。"""
        self.assertIn("/product-control/p0-phase", self.component)
        self.assertIn("loadProductControlP0", self.component)
        self.assertIn("handleRefreshProductControlP0", self.component)
        self.assertIn('method: "POST"', self.component)

    def test_bdd_6_frontend_does_not_offer_auto_execution_from_p0_panel(self) -> None:
        """行为 6：P0 面板只能显示待派工审阅，不能提供自动执行入口。"""
        self.assertIn("待派工审阅", self.component)
        self.assertIn("dispatch_review_required", self.component)
        self.assertIn("product-control-p0-panel", self.styles)
        self.assertNotIn("data-p0-auto-execute", self.component)


if __name__ == "__main__":
    unittest.main(verbosity=2)
