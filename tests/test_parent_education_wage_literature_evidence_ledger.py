from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry
from Program.workbench.parent_education_wage_literature_evidence_ledger import (
    build_parent_education_wage_literature_evidence_ledger,
    write_parent_education_wage_literature_evidence_ledger,
)


class ParentEducationWageLiteratureEvidenceLedgerTests(unittest.TestCase):
    """BDD: P1-A literature evidence must be auditable before citation use."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="pew-literature-ledger-"))
        self.project_root = self.tmp / "project"
        self._seed_project(self.project_root)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_bdd_p1a_builds_current_topic_seed_ledger_without_verified_claims(self) -> None:
        """行为 1：从当前题目 literature.md 生成 seed/candidate/verified 分层账本。"""
        ledger = build_parent_education_wage_literature_evidence_ledger(self.project_root)

        self.assertEqual(ledger["schema_version"], "p1a.parent_education_wage_literature_evidence_ledger.v1")
        self.assertEqual(ledger["topic_slug"], "parent-education-wage")
        self.assertEqual(ledger["status"], "needs_external_literature_verification")
        self.assertEqual(ledger["verified_count"], 0)
        self.assertGreaterEqual(len(ledger["candidate_topics"]), 4)
        self.assertGreaterEqual(len(ledger["citation_records"]), 4)
        query_text = "\n".join(topic["query_seed"] for topic in ledger["candidate_topics"])
        self.assertIn("父母教育、家庭背景与子女工资收入", query_text)
        self.assertNotIn("brief.md", query_text)
        self.assertNotIn("variables.yaml", query_text)
        self.assertNotIn("当前状态", query_text)
        self.assertTrue(all(record["citation_status"] == "seed" for record in ledger["citation_records"]))
        self.assertTrue(all(record["can_support_claims"] is False for record in ledger["citation_records"]))
        self.assertIn("external_or_manual_literature_search_required", ledger["blocking_reasons"])

    def test_bdd_p1a_protects_formal_bibliography_and_manuscript(self) -> None:
        """行为 2：未核验文献不能写入正式 bibliography 或正式论文层。"""
        formal_bib = self.project_root / "Manuscripts/references.bib"
        formal_manuscript = self.project_root / "Manuscripts/paper.md"
        before = {
            "bib": formal_bib.read_text(encoding="utf-8"),
            "manuscript": formal_manuscript.read_text(encoding="utf-8"),
        }

        ledger = build_parent_education_wage_literature_evidence_ledger(self.project_root)
        write_parent_education_wage_literature_evidence_ledger(self.project_root, ledger)

        self.assertFalse(ledger["promotion"]["allowed"])
        self.assertFalse(ledger["boundary_flags"]["modified_formal_bibliography"])
        self.assertFalse(ledger["boundary_flags"]["modified_formal_manuscript"])
        self.assertEqual(before["bib"], formal_bib.read_text(encoding="utf-8"))
        self.assertEqual(before["manuscript"], formal_manuscript.read_text(encoding="utf-8"))

    def test_bdd_p1a_writes_reviewable_json_and_markdown_outputs(self) -> None:
        """行为 3：P1-A 产物必须同时有机器可读 JSON 和人工审阅 Markdown。"""
        ledger = build_parent_education_wage_literature_evidence_ledger(self.project_root)
        json_path, review_path = write_parent_education_wage_literature_evidence_ledger(self.project_root, ledger)

        self.assertTrue(json_path.exists())
        self.assertTrue(review_path.exists())
        self.assertEqual(json.loads(json_path.read_text(encoding="utf-8"))["status"], "needs_external_literature_verification")
        review = review_path.read_text(encoding="utf-8")
        self.assertIn("P1-A 文献证据账本", review)
        self.assertIn("写入正式 bibliography：否", review)
        self.assertIn("父母受教育水平对子女工资收入的影响", review)

    def _seed_project(self, root: Path) -> None:
        self._write_text(root, "Manuscripts/references.bib", "% existing references\n")
        self._write_text(root, "Manuscripts/paper.md", "# Draft\n\nNo citations yet.\n")
        self._write_text(
            root,
            "Tasks/parent-education-wage/literature.md",
            """---
topic: parent_education_wage
topic_slug: parent-education-wage
evidence_status: needs_real_literature_discovery
downstream_consumers:
- variables.yaml
- design.json
- manuscript_paper.pdf
---

# parent_education_wage - 文献综述工作面

## 当前题目

父母受教育水平对子女工资收入的影响。

## 待检索方向

1. 父母教育、家庭背景与子女工资收入。
2. 代际人力资本传递与教育回报。
3. 中国家庭追踪调查或类似微观数据中的工资与教育测量。
4. 义务教育、教育扩张或家庭教育背景的识别策略。

## 证据边界

- 不得把未核验候选写入正式论文参考文献。
""",
        )

    def _write_text(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


class ProductControlP1LiteratureApiAndReactTests(unittest.TestCase):
    """BDD: Product Control must expose P1-A literature ledger status."""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.tmp = Path(tempfile.mkdtemp(prefix="p1-literature-api-"))
        self.repo_root = self.tmp / "repo"
        self.product_root = self.repo_root / "Product"
        self.project_root = self.tmp / "project"
        self.product_root.mkdir(parents=True)
        self._seed_project(self.project_root)
        ensure_registry(self.product_root, self.repo_root)
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)
        response = self.client.post(
            "/api/v1/projects",
            json={
                "slug": "parent-education-wage",
                "title": "Parent Education Wage",
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

    def test_bdd_p1a_api_get_reports_missing_and_post_generates_ledger(self) -> None:
        """行为 4：GET 不隐式生成；POST 才生成 P1-A 文献账本。"""
        missing = self.client.get(f"/api/v1/projects/{self.project_id}/product-control/p1-literature-ledger")
        self.assertEqual(missing.status_code, 200, msg=missing.text)
        self.assertEqual(missing.json()["status"], "p1a_literature_ledger_missing")

        created = self.client.post(f"/api/v1/projects/{self.project_id}/product-control/p1-literature-ledger")

        self.assertEqual(created.status_code, 201, msg=created.text)
        body = created.json()
        self.assertEqual(body["status"], "needs_external_literature_verification")
        self.assertEqual(body["project"]["id"], self.project_id)
        self.assertTrue((self.project_root / "Results/json/parent_education_wage_literature_evidence_ledger.json").exists())

    def test_bdd_p1a_react_product_control_panel_exposes_p1a_literature_status(self) -> None:
        """行为 5：React 产品控制面必须能展示 P1-A 文献证据链状态。"""
        root = Path(__file__).resolve().parents[1]
        component = (root / "Product/web-react/src/components/ProductControlP0Panel.tsx").read_text(encoding="utf-8")

        self.assertIn("/product-control/p1-literature-ledger", component)
        self.assertIn("P1-A 文献证据", component)
        self.assertIn("needs_external_literature_verification", component)
        self.assertIn("真实文献候选", component)

    def _seed_project(self, root: Path) -> None:
        self._write_text(root, "paper.yaml", "research:\n  question: 父母受教育水平对子女工资收入的影响\n")
        self._write_text(root, "Program/run_paper.py", "print('ok')\n")
        self._write_json(
            root,
            "state/product/topic_binding.json",
            {
                "expected_topic": "父母受教育水平对子女工资收入的影响",
                "expected_slug": "parent-education-wage",
                "binding_type": "demo_acceptance_line",
            },
        )
        self._write_json(
            root,
            "state/product/research_question.json",
            {
                "status": "confirmed",
                "question": "父母受教育水平对子女工资收入的影响",
            },
        )
        self._write_text(root, "Manuscripts/references.bib", "% existing references\n")
        self._write_text(root, "Manuscripts/paper.md", "# Draft\n\nNo citations yet.\n")
        self._write_text(
            root,
            "Tasks/parent-education-wage/literature.md",
            "# Literature\n\n1. 父母教育、家庭背景与子女工资收入。\n2. 代际人力资本传递与教育回报。\n3. 中国家庭追踪调查或类似微观数据中的工资与教育测量。\n4. 义务教育、教育扩张或家庭教育背景的识别策略。\n",
        )

    def _write_text(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _write_json(self, root: Path, relative_path: str, payload: dict) -> None:
        self._write_text(root, relative_path, json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
