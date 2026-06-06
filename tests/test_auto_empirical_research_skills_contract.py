import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class AutoEmpiricalResearchSkillsContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="aers-contract-"))
        self.source_root = self.temp_dir / "Auto-Empirical-Research-Skills"
        (self.source_root / "catalog").mkdir(parents=True)
        (self.source_root / "skills" / "00.1-Full-empirical-analysis-skill_Python").mkdir(parents=True)
        (self.source_root / "skills" / "50-brycewang-aer-skills").mkdir(parents=True)
        (self.source_root / "catalog" / "skills.json").write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "summary": {
                        "skill_files": 2,
                        "top_level_collections": 2,
                    },
                    "collections": [
                        {
                            "id": "00.1-Full-empirical-analysis-skill_Python",
                            "path": "skills/00.1-Full-empirical-analysis-skill_Python",
                            "license": "CC-BY-SA-4.0 (repository default)",
                            "commercial_use": "share-alike",
                            "source_confidence": "high",
                            "source_url": "https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills",
                            "skill_count": 1,
                            "primary_skill": {
                                "name": "Full-empirical-analysis-skill",
                                "path": "skills/00.1-Full-empirical-analysis-skill_Python/SKILL.md",
                                "description": "Full empirical analysis workflow with Table 1, baseline models, robustness and paper-ready outputs.",
                            },
                        },
                        {
                            "id": "50-brycewang-aer-skills",
                            "path": "skills/50-brycewang-aer-skills",
                            "license": "CC-BY-SA-4.0 (repository default)",
                            "commercial_use": "share-alike",
                            "source_confidence": "high",
                            "source_url": "https://github.com/brycewang-stanford/AER-skills",
                            "skill_count": 9,
                            "primary_skill": {
                                "name": "aer-workflow",
                                "path": "skills/50-brycewang-aer-skills/skills/aer-workflow/SKILL.md",
                                "description": "Routes manuscript work through AER topic selection, identification, robustness, writing and replication checks.",
                            },
                        },
                    ],
                    "skills": [
                        {
                            "collection": "00.1-Full-empirical-analysis-skill_Python",
                            "name": "Full-empirical-analysis-skill",
                            "path": "skills/00.1-Full-empirical-analysis-skill_Python/SKILL.md",
                            "description": "Full empirical analysis workflow with Table 1, baseline models, robustness and paper-ready outputs.",
                            "has_frontmatter": True,
                        },
                        {
                            "collection": "50-brycewang-aer-skills",
                            "name": "aer-workflow",
                            "path": "skills/50-brycewang-aer-skills/skills/aer-workflow/SKILL.md",
                            "description": "AER manuscript workflow router.",
                            "has_frontmatter": True,
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_source_metadata_keeps_license_and_human_review_boundary(self) -> None:
        """Given AERS is configured, When indexed, Then source metadata preserves attribution and canonical write limits."""
        from Product.backend.auto_empirical_research_skills import get_aers_source_info

        source = get_aers_source_info(self.source_root)

        self.assertTrue(source["available"])
        self.assertEqual(source["source_url"], "https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills")
        self.assertEqual(source["license"], "CC-BY-SA-4.0")
        self.assertIn("Attribution", source["license_obligations"])
        self.assertFalse(source["canonical_policy"]["auto_write_canonical"])
        self.assertEqual(source["canonical_policy"]["mode"], "proposal_only_until_human_review")
        self.assertEqual(source["summary"]["skill_files"], 2)

    def test_bdd_2_catalog_entries_become_non_executable_product_capabilities(self) -> None:
        """Given AERS catalog entries, When mapped into product capabilities, Then skills are discoverable but not executable actions."""
        from Product.backend.auto_empirical_research_skills import index_aers_capabilities

        capabilities = index_aers_capabilities(self.source_root)
        by_id = {cap["id"]: cap for cap in capabilities}

        self.assertIn("cap_aers_00_1_full_empirical_analysis_skill_python", by_id)
        self.assertIn("cap_aers_50_brycewang_aer_skills", by_id)
        self.assertEqual(by_id["cap_aers_00_1_full_empirical_analysis_skill_python"]["status"], "template")
        self.assertEqual(
            by_id["cap_aers_00_1_full_empirical_analysis_skill_python"]["category"],
            "full_empirical_pipeline",
        )
        self.assertEqual(by_id["cap_aers_50_brycewang_aer_skills"]["status"], "checklist")
        self.assertEqual(by_id["cap_aers_50_brycewang_aer_skills"]["category"], "journal_standard")
        self.assertTrue(all(cap["status"] != "executable" for cap in capabilities))
        self.assertTrue(all(cap["namespace"] == "external_skill" for cap in capabilities))

    def test_bdd_3_patch_policy_routes_automode_to_proposals_not_formal_rules(self) -> None:
        """Given Auto Mode uses AERS, When it drafts method changes, Then output targets proposal storage only."""
        from Product.backend.auto_empirical_research_skills import build_aers_methodology_policy

        policy = build_aers_methodology_policy()

        self.assertFalse(policy["auto_mode"]["can_write_canonical"])
        self.assertEqual(policy["auto_mode"]["proposal_status"], "needs_human_review")
        self.assertEqual(
            policy["proposal_path"],
            "Program/methodology/proposals/auto-empirical-research-skills/",
        )
        self.assertIn("canonical_rules_require_manual_review", policy["hard_constraints"])

    def test_bdd_4_registry_includes_aers_source_and_classifies_external_skills(self) -> None:
        """Given capability registry reindexes, When AERS is available, Then Supervisor sees the source and classification buckets."""
        from Product.backend.capability_registry import reindex_capabilities

        project_root = self.temp_dir / "project"
        product_root = self.temp_dir / "product"
        repo_root = self.temp_dir / "repo"
        project_root.mkdir()

        project = {
            "id": "p1",
            "slug": "p1",
            "title": "Project",
            "root": str(project_root),
            "project_root": str(project_root),
        }
        with (
            patch("Product.backend.capability_registry.get_project_by_id_or_transient", return_value=project),
            patch("Product.backend.capability_registry.get_statspai_info", return_value={"available": False, "path": ""}),
            patch("Product.backend.capability_registry.index_statspai_capabilities", return_value=[]),
            patch("Product.backend.capability_registry.get_aers_source_info") as source_info,
            patch("Product.backend.capability_registry.index_aers_capabilities") as index_caps,
        ):
            source_info.return_value = {
                "available": True,
                "path": str(self.source_root),
                "source_url": "https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills",
                "license": "CC-BY-SA-4.0",
                "summary": {"skill_files": 2, "top_level_collections": 2},
            }
            index_caps.return_value = [
                {
                    "id": "cap_aers_50_brycewang_aer_skills",
                    "namespace": "external_skill",
                    "name": "aer-workflow",
                    "category": "journal_standard",
                    "description": "AER workflow checklist",
                    "risk_level": "medium",
                    "cost_model": "llm_tokens",
                    "allowed_roles": ["supervisor", "reviewer_agent"],
                    "adapter_path": "external://skills/50-brycewang-aer-skills/skills/aer-workflow/SKILL.md",
                    "input_schema": {"type": "object", "properties": {}},
                    "output_schema": {"type": "object", "properties": {}},
                    "status": "checklist",
                }
            ]

            result = reindex_capabilities(product_root, repo_root, "p1")

        registry = result["capability"]
        self.assertIn("auto_empirical_research_skills", registry["sources"])
        self.assertIn("cap_aers_50_brycewang_aer_skills", registry["classification"]["checklist"])

    def test_bdd_5_missing_source_is_safe_and_non_blocking(self) -> None:
        """Given AERS is not installed locally, When indexed, Then registry reports unavailable instead of crashing."""
        from Product.backend.auto_empirical_research_skills import get_aers_source_info, index_aers_capabilities

        missing = self.temp_dir / "missing"

        source = get_aers_source_info(missing)
        capabilities = index_aers_capabilities(missing)

        self.assertFalse(source["available"])
        self.assertEqual(source["reason"], "catalog_not_found")
        self.assertEqual(capabilities, [])


if __name__ == "__main__":
    unittest.main()
