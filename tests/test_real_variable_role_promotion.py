from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

import Product.app as product_app
from Product.backend.registry import ensure_registry


class RealVariableRolePromotionTests(unittest.TestCase):
    """BDD: 真实字段候选必须先进入可编辑草稿，再由用户保存为正式变量角色。"""

    def setUp(self) -> None:
        self.original_product_root = product_app.PRODUCT_ROOT
        self.original_repo_root = product_app.REPO_ROOT
        self.temp_dir = Path(tempfile.mkdtemp(prefix="real-variable-role-promotion-"))
        self.repo_root = self.temp_dir / "repo"
        self.product_root = self.repo_root / "Product"
        self.project_root = self.temp_dir / "empirical-project"
        self.product_root.mkdir(parents=True)
        self._create_minimal_project(self.project_root)
        ensure_registry(self.product_root, self.repo_root)
        product_app.PRODUCT_ROOT = self.product_root
        product_app.REPO_ROOT = self.repo_root
        self.client = TestClient(product_app.app)
        response = self.client.post(
            "/api/v1/projects",
            json={
                "slug": "real-variable-role-promotion",
                "title": "Real Variable Role Promotion Project",
                "project_root": str(self.project_root),
                "language": "zh",
            },
        )
        self.assertEqual(response.status_code, 201, msg=response.text)
        self.project_id = response.json()["id"]
        self.candidate_id = "variable_role_candidate_real_fields"
        self._write_approved_candidate(self.candidate_id)

    def tearDown(self) -> None:
        product_app.PRODUCT_ROOT = self.original_product_root
        product_app.REPO_ROOT = self.original_repo_root
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_approved_candidate_creates_editable_draft(self) -> None:
        """行为 1：已审批候选可以创建可编辑 VariableRoleSet 草稿。"""
        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/variable-role-candidates/{self.candidate_id}/promote",
            json={"note": "基于真实字段候选创建变量角色草稿。"},
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        draft = response.json()["variable_role_set_draft"]
        self.assertEqual(draft["status"], "draft")
        self.assertEqual(draft["source_candidate_id"], self.candidate_id)
        self.assertEqual(draft["evidence_level"], "local_file")
        self.assertEqual(draft["write_boundary"], "draft_only_until_user_approval")
        self.assertEqual(draft["roles"]["outcome"], ["wage"])
        self.assertEqual(draft["source_dataset"]["name"], "cfps2011adult_202202.dta")

        draft_path = self.project_root / "state" / "product" / "variable_roles_drafts.json"
        self.assertTrue(draft_path.exists())
        saved = json.loads(draft_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["pending_variable_roles_draft"]["id"], draft["id"])

    def test_bdd_2_promotion_does_not_overwrite_approved_variable_roles(self) -> None:
        """行为 2：创建草稿不能覆盖已经 approved 的正式 VariableRoleSet。"""
        formal_path = self.project_root / "state" / "product" / "variable_roles.json"
        original_formal = {
            "id": "variable_role_set",
            "version": 7,
            "status": "approved",
            "evidence_level": "local_file",
            "dataset_path": "Data/Final/analysis_sample.csv",
            "roles": {"outcome": ["income"], "treatment": ["robot"], "controls": [], "instruments": [], "fixed_effects": [], "cluster_by": []},
        }
        formal_path.parent.mkdir(parents=True, exist_ok=True)
        formal_path.write_text(json.dumps(original_formal, ensure_ascii=False, indent=2), encoding="utf-8")
        before_hash = self._sha256(formal_path)

        response = self.client.post(
            f"/api/v1/projects/{self.project_id}/variable-role-candidates/{self.candidate_id}/promote",
            json={"note": "创建草稿，不覆盖正式变量角色。"},
        )

        self.assertEqual(response.status_code, 201, msg=response.text)
        self.assertEqual(self._sha256(formal_path), before_hash)
        saved = json.loads(formal_path.read_text(encoding="utf-8"))
        self.assertEqual(saved["roles"]["outcome"], ["income"])
        self.assertTrue((self.project_root / "state" / "product" / "variable_roles_drafts.json").exists())

    def test_bdd_3_user_approves_promoted_draft_into_formal_state(self) -> None:
        """行为 3：用户编辑 promoted draft 并保存后，正式状态保留候选和草稿 provenance。"""
        promoted = self.client.post(
            f"/api/v1/projects/{self.project_id}/variable-role-candidates/{self.candidate_id}/promote",
            json={"note": "先创建可编辑草稿。"},
        )
        self.assertEqual(promoted.status_code, 201, msg=promoted.text)
        draft_id = promoted.json()["variable_role_set_draft"]["id"]

        edited_roles = {
            "outcome": ["wage"],
            "treatment": ["trained"],
            "controls": ["edu"],
            "instruments": [],
            "fixed_effects": ["pid"],
            "cluster_by": ["pid"],
        }
        response = self.client.put(
            f"/api/v1/projects/{self.project_id}/variable-roles",
            json={
                "dataset_path": "external/A001CFPS/cfps2011adult_202202.dta",
                "candidate_id": self.candidate_id,
                "roles": edited_roles,
                "note": "人工确认 promoted draft，删除 experience，设置 pid 固定效应和聚类。",
            },
        )

        self.assertEqual(response.status_code, 200, msg=response.text)
        role_set = response.json()["variable_role_set"]
        self.assertEqual(role_set["status"], "approved")
        self.assertEqual(role_set["candidate_id"], self.candidate_id)
        self.assertEqual(role_set["provenance"]["variable_roles_draft_path"], "state/product/variable_roles_drafts.json")
        self.assertEqual(role_set["provenance"]["source_variable_roles_draft_id"], draft_id)
        self.assertEqual(role_set["roles"]["controls"], ["edu"])
        self.assertEqual(role_set["roles"]["fixed_effects"], ["pid"])
        self.assertEqual(role_set["roles"]["cluster_by"], ["pid"])

    def test_bdd_4_frontend_separates_candidate_from_formal_state(self) -> None:
        """行为 4：前端必须把候选建议和正式变量角色保存区分开。"""
        root = Path(__file__).resolve().parents[1]
        app_js = (root / "Product" / "web" / "assets" / "app.js").read_text(encoding="utf-8")
        styles = (root / "Product" / "web" / "assets" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("候选建议", app_js)
        self.assertIn("正式变量角色", app_js)
        self.assertIn("promoteVariableRoleCandidate", app_js)
        self.assertIn("data-promote-variable-candidate-action", app_js)
        self.assertIn("handleSaveVariableRoles", app_js)
        self.assertIn("variable-role-draft", styles)

    def _write_approved_candidate(self, candidate_id: str) -> None:
        state_path = self.project_root / "state" / "product" / "variable_role_candidates.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        candidate = {
            "id": candidate_id,
            "dataset_import_id": "dataset_import_cfps",
            "dataset_import_profile_id": "dataset_import_profile_cfps",
            "status": "approved_candidate",
            "evidence_level": "local_file",
            "source": {
                "name": "cfps2011adult_202202.dta",
                "path": "external/A001CFPS/cfps2011adult_202202.dta",
                "sha256": "abc123",
            },
            "binding": {"mode": "external_reference", "read_only": True},
            "candidate_roles": {
                "outcome": ["wage"],
                "treatment": ["trained"],
                "controls": ["edu", "experience"],
                "instruments": [],
                "fixed_effects": [],
                "cluster_by": [],
            },
            "can_apply_to_variable_roles": True,
            "does_not_mutate_variable_role_set": True,
            "review_events": [{"actor": "user", "action": "approve_candidate", "timestamp": "2026-05-17T00:00:00+00:00"}],
        }
        state_path.write_text(
            json.dumps({"candidates": {candidate_id: candidate}, "latest_candidate_id": candidate_id}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def _create_minimal_project(project_root: Path) -> None:
        (project_root / "Data" / "Final").mkdir(parents=True)
        (project_root / "Program").mkdir(parents=True)
        (project_root / "paper.yaml").write_text(
            "project:\n  slug: real-variable-role-promotion\n  title: Real Variable Role Promotion Project\n"
            "data:\n  final_dataset: Data/Final/analysis_sample.csv\n",
            encoding="utf-8",
        )
        (project_root / "Program" / "run_paper.py").write_text("print('ok')\n", encoding="utf-8")
        (project_root / "Data" / "Final" / "analysis_sample.csv").write_text(
            "wage,trained,edu\n10,1,16\n12,0,14\n",
            encoding="utf-8",
        )

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


if __name__ == "__main__":
    unittest.main()
