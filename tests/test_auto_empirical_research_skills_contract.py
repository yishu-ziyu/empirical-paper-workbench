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
        (self.source_root / "eval-harness" / "scenarios").mkdir(parents=True)
        (self.source_root / "benchmark" / "tasks").mkdir(parents=True)
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
        (self.source_root / "eval-harness" / "scenarios" / "statspai-weak-iv.toml").write_text(
            """
id = "statspai-weak-iv"
skill = "skills/00-Full-empirical-analysis-skill_StatsPAI"
title = "Weak-instrument case must report first-stage F and use weak-IV-robust inference"
category = "causal-identification"
severity = "critical"
prompt = "My first-stage F-statistic is about 8. Run the 2SLS carefully."

[[rubric]]
id = "reports-first-stage-f"
check = "regex_any"
required = true
weight = 3
description = "Reports first-stage F."

[[rubric]]
id = "weak-iv-robust-inference"
check = "regex_any"
required = true
weight = 4
description = "Recommends weak-IV-robust inference."

[[rubric]]
id = "exclusion-restriction"
check = "manual"
required = false
weight = 2
description = "Discusses exclusion restriction."
""".strip(),
            encoding="utf-8",
        )
        (self.source_root / "benchmark" / "tasks" / "card-iv-recovery.toml").write_text(
            """
id = "card-iv-recovery"
title = "Card IV recovery: does the pipeline get the IV>OLS schooling result and report instrument strength?"
data = "demo-StatsPAI-skill/data/card.csv"
reference_candidate = "reference-iv"
description = "Recover OLS, IV and first-stage strength for a Card-style IV task."

[[gold]]
id = "ols-return-positive"
required = true
weight = 2
description = "Reports a positive OLS return."
check = "value_near"
field = "ols_return"
expected = 0.075
tol = 0.03

[[gold]]
id = "first-stage-reported-and-adequate"
required = true
weight = 3
description = "Reports first-stage F."
check = "first_stage_min"
min_f = 10.0
""".strip(),
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
            patch("Product.backend.capability_registry.index_aers_quality_gates") as index_gates,
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
            index_gates.return_value = [
                {
                    "id": "cap_aers_eval_statspai_weak_iv",
                    "namespace": "external_skill",
                    "name": "Weak-instrument case must report first-stage F",
                    "category": "evaluation_gate",
                    "description": "Weak IV quality gate",
                    "risk_level": "high",
                    "cost_model": "llm_review",
                    "allowed_roles": ["supervisor", "reviewer_agent"],
                    "adapter_path": "external://eval-harness/scenarios/statspai-weak-iv.toml",
                    "input_schema": {"type": "object", "properties": {}},
                    "output_schema": {"type": "object", "properties": {}},
                    "status": "checklist",
                    "quality_gate": {"gate_type": "eval_scenario"},
                }
            ]

            result = reindex_capabilities(product_root, repo_root, "p1")

        registry = result["capability"]
        self.assertIn("auto_empirical_research_skills", registry["sources"])
        self.assertIn("cap_aers_50_brycewang_aer_skills", registry["classification"]["checklist"])
        self.assertIn("cap_aers_eval_statspai_weak_iv", registry["classification"]["checklist"])
        self.assertEqual(registry["sources"]["auto_empirical_research_skills"]["quality_gate_count"], 1)

    def test_bdd_5_missing_source_is_safe_and_non_blocking(self) -> None:
        """Given AERS is not installed locally, When indexed, Then registry reports unavailable instead of crashing."""
        from Product.backend.auto_empirical_research_skills import get_aers_source_info, index_aers_capabilities

        missing = self.temp_dir / "missing"

        source = get_aers_source_info(missing)
        capabilities = index_aers_capabilities(missing)

        self.assertFalse(source["available"])
        self.assertEqual(source["reason"], "catalog_not_found")
        self.assertEqual(capabilities, [])

    def test_bdd_6_eval_scenarios_become_method_quality_gate_capabilities(self) -> None:
        """Given AERS eval scenarios, When indexed, Then method risks become product-visible quality gates."""
        from Product.backend.auto_empirical_research_skills import index_aers_quality_gates

        gates = index_aers_quality_gates(self.source_root)
        by_id = {cap["id"]: cap for cap in gates}

        gate = by_id["cap_aers_eval_statspai_weak_iv"]
        self.assertEqual(gate["status"], "checklist")
        self.assertEqual(gate["category"], "evaluation_gate")
        self.assertEqual(gate["risk_level"], "high")
        self.assertIn("reviewer_agent", gate["allowed_roles"])
        self.assertEqual(gate["quality_gate"]["gate_type"], "eval_scenario")
        self.assertEqual(gate["quality_gate"]["scenario_id"], "statspai-weak-iv")
        self.assertEqual(gate["quality_gate"]["severity"], "critical")
        self.assertEqual(gate["quality_gate"]["rubric_count"], 3)
        self.assertEqual(gate["quality_gate"]["machine_checkable_count"], 2)
        self.assertEqual(gate["quality_gate"]["manual_count"], 1)
        self.assertFalse(gate["canonical_policy"]["auto_mode"]["can_write_canonical"])

    def test_bdd_7_numeric_benchmarks_become_reproducible_quality_gates(self) -> None:
        """Given AERS numeric benchmarks, When indexed, Then gold checks become reproducibility gates."""
        from Product.backend.auto_empirical_research_skills import index_aers_quality_gates

        gates = index_aers_quality_gates(self.source_root)
        by_id = {cap["id"]: cap for cap in gates}

        gate = by_id["cap_aers_benchmark_card_iv_recovery"]
        self.assertEqual(gate["status"], "checklist")
        self.assertEqual(gate["category"], "empirical_benchmark")
        self.assertEqual(gate["risk_level"], "medium")
        self.assertIn("execution_agent", gate["allowed_roles"])
        self.assertEqual(gate["quality_gate"]["gate_type"], "benchmark_task")
        self.assertEqual(gate["quality_gate"]["task_id"], "card-iv-recovery")
        self.assertEqual(gate["quality_gate"]["required_gold_count"], 2)
        self.assertEqual(gate["quality_gate"]["gold_count"], 2)
        self.assertEqual(gate["quality_gate"]["data"], "demo-StatsPAI-skill/data/card.csv")
        self.assertEqual(gate["quality_gate"]["reference_candidate"], "reference-iv")


if __name__ == "__main__":
    unittest.main()
