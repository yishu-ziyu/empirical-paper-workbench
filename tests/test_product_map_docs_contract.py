import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ProductMapDocsContractTest(unittest.TestCase):
    def _read_required_doc(self, relative_path: str) -> str:
        path = PROJECT_ROOT / relative_path
        self.assertTrue(path.exists(), f"Missing required product map doc: {relative_path}")
        content = path.read_text(encoding="utf-8")
        self.assertGreater(len(content.strip()), 800, f"{relative_path} is too thin to guide implementation")
        return content

    def test_current_product_map_names_pages_next_actions_and_evidence(self):
        content = self._read_required_doc("docs/current-product-map.md")

        required_terms = [
            "Product/web-react/src/App.tsx",
            "Product/web/index.html",
            "Product/app.py",
            "demo_server.py",
            "SystemStatusBar",
            "工作台首页",
            "数据与设计",
            "实证执行",
            "结果与草稿",
            "审阅与导出",
            "Next Action",
            "Agent Task Queue",
            "Verifier",
            "mock",
            "local_file",
            "local_execution",
        ]
        for term in required_terms:
            self.assertIn(term, content)

    def test_api_map_names_endpoints_handlers_and_state_touchpoints(self):
        content = self._read_required_doc("docs/api-map.md")

        required_terms = [
            "Product/app.py",
            "Product/api/brief.py",
            "Product/api/supervisor.py",
            "Product/api/variables.py",
            "Product/api/design.py",
            "Product/api/execute.py",
            "Product/api/capabilities.py",
            "Product/api/system.py",
            "/api/v1",
            "state/product",
            "state/runs",
            "Results/json",
        ]
        for term in required_terms:
            self.assertIn(term, content)

        exact_endpoints = [
            "POST /api/brief",
            "POST /api/supervisor/plan",
            "POST /api/variables",
            "POST /api/design",
            "POST /api/execute",
            "GET /api/capabilities/methods",
            "POST /api/system/status",
            "POST /api/v1/topic-intake/supervisor-plan",
            "GET /api/v1/projects/{project_id}/overview",
            "GET /api/v1/projects/{project_id}/journey",
            "GET|PUT /api/v1/projects/{project_id}/variable-roles",
            "GET|PUT /api/v1/projects/{project_id}/design-spec",
            "GET|PUT /api/v1/projects/{project_id}/run-plan",
            "GET|POST /api/v1/projects/{project_id}/agent-task-queue",
            "POST /api/v1/projects/{project_id}/runs/full",
        ]
        for endpoint in exact_endpoints:
            with self.subTest(endpoint=endpoint):
                self.assertIn(endpoint, content)

    def test_state_schema_maps_canonical_objects_to_files_and_gates(self):
        content = self._read_required_doc("docs/state-schema.md")

        required_terms = [
            "ResearchQuestion",
            "VariableRoleSet",
            "DesignSpec",
            "RunPlan",
            "MethodExecutionResult",
            "Finding",
            "ExportPackage",
            "AgentTask",
            "Capability",
            "Data Gate",
            "Design Gate",
            "Execution Gate",
            "Result Gate",
            "Export Gate",
        ]
        for term in required_terms:
            self.assertIn(term, content)

        canonical_paths = [
            "ResearchQuestion -> state/product/research_question.json",
            "VariableRoleSet -> state/product/variable_roles.json",
            "DesignSpec -> state/product/design_spec.json",
            "RunPlan -> state/product/run_plan.json",
            "AgentTask -> state/product/agent_task_queue.json",
            "Capability -> state/product/capabilities.json",
            "ExportPackage -> state/product/export_package_manifest.json",
            "Product/state",
            "state/product",
            "state/runs",
            "Results/json",
            "Manuscripts",
            "Submissions",
        ]
        for path in canonical_paths:
            with self.subTest(path=path):
                self.assertIn(path, content)


if __name__ == "__main__":
    unittest.main()
