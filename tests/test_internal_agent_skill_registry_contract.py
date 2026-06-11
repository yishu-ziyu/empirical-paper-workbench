import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class InternalAgentSkillRegistryContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="internal-agent-skills-"))
        self.registry_path = self.temp_dir / "agent_skill_registry.json"
        self.registry_path.write_text(
            json.dumps(
                {
                    "schema_version": "internal_agent_skill_registry.v1",
                    "status": "active",
                    "skills": [
                        {
                            "id": "recursive_research_search",
                            "lifecycle": "internal_draft",
                            "metadata": {
                                "name": "递归研究搜索",
                                "domain": "literature",
                                "owner_agent": "LiteratureAgent",
                                "allowed_agents": ["Supervisor", "LiteratureAgent", "ReviewerAgent"],
                                "risk_level": "medium",
                                "evidence_level": "web_and_local_source",
                                "source_policy": "external_reference_normalized",
                            },
                            "applies_when": {
                                "stage": "recursive_search",
                                "required_state": ["TaskBrief.approved"],
                                "blockers": ["missing_research_question"],
                            },
                            "inputs": {
                                "required": ["research_question", "boundary_terms"],
                                "optional": ["seed_literature", "dataset_hints"],
                            },
                            "outputs": {
                                "artifacts": ["LiteratureSeedPackage", "verification_queue"],
                                "state_patch_proposal": ["LiteratureSearchPlan"],
                                "formal_write_targets": [],
                            },
                            "tools": {
                                "allowed_adapters": ["web_search", "cnki_manual_assist", "zotero_optional"],
                                "forbidden_actions": ["write_formal_literature_review_without_verified_citations"],
                            },
                            "quality_gates": {
                                "machine_checkable": ["aers:eval:citation-hygiene-no-fake-refs"],
                                "manual_review": ["source_relevance_review"],
                            },
                            "human_confirmation": {
                                "required_before": ["formal_literature_review_writeback"],
                                "approver_role": "human_researcher",
                            },
                            "failure_conditions": {
                                "hard_fail": ["citation_not_verifiable"],
                                "soft_warn": ["english_only_search_results"],
                            },
                            "provenance": {
                                "external_sources": [
                                    {
                                        "name": "Auto-Empirical-Research-Skills",
                                        "url": "https://github.com/brycewang-stanford/Auto-Empirical-Research-Skills",
                                        "license": "CC-BY-SA-4.0",
                                    },
                                    {
                                        "name": "Maigret",
                                        "url": "https://github.com/soxoj/maigret",
                                        "license": "MIT",
                                    },
                                ],
                                "attribution": "Adapted into product lifecycle contract.",
                                "transformation_log": ["Converted recursive search idea into academic evidence graph workflow."],
                            },
                            "benchmark": {
                                "eval_scenarios": ["citation-hygiene-no-fake-refs"],
                                "numeric_tasks": [],
                                "pass_policy": "manual_open_items_block_formal_writeback",
                            },
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_bdd_1_source_metadata_keeps_audit_trail(self) -> None:
        """Given internal skills are adapted from external practices, When indexed, Then provenance stays visible."""
        from Product.backend.internal_agent_skill_registry import get_internal_agent_skill_source_info

        source = get_internal_agent_skill_source_info(self.registry_path)

        self.assertTrue(source["available"])
        self.assertEqual(source["schema_version"], "internal_agent_skill_registry.v1")
        self.assertEqual(source["skill_count"], 1)
        self.assertEqual(source["lifecycle_counts"]["internal_draft"], 1)
        self.assertFalse(source["canonical_policy"]["auto_write_canonical"])

    def test_bdd_2_internal_skills_are_non_executable_and_proposal_only(self) -> None:
        """Given Auto Mode uses an internal draft skill, When mapped to capabilities, Then it cannot write formal state."""
        from Product.backend.internal_agent_skill_registry import index_internal_agent_skill_capabilities

        capabilities = index_internal_agent_skill_capabilities(self.registry_path)
        skill = capabilities[0]

        self.assertEqual(skill["id"], "cap_internal_skill_recursive_research_search")
        self.assertEqual(skill["namespace"], "internal_agent_skill")
        self.assertEqual(skill["status"], "checklist")
        self.assertNotEqual(skill["status"], "executable")
        self.assertEqual(skill["internal_skill"]["lifecycle"], "internal_draft")
        self.assertEqual(skill["internal_skill"]["formal_write_targets"], [])
        self.assertFalse(skill["canonical_policy"]["auto_mode"]["can_write_canonical"])
        self.assertEqual(skill["canonical_policy"]["auto_mode"]["proposal_status"], "needs_human_review")

    def test_bdd_3_skill_binds_stage_agents_inputs_and_quality_gates(self) -> None:
        """Given Supervisor browses internal skills, When it selects one, Then stage, agents and gates are explicit."""
        from Product.backend.internal_agent_skill_registry import index_internal_agent_skill_capabilities

        skill = index_internal_agent_skill_capabilities(self.registry_path)[0]

        self.assertEqual(skill["internal_skill"]["stage"], "recursive_search")
        self.assertEqual(skill["internal_skill"]["owner_agent"], "LiteratureAgent")
        self.assertIn("Supervisor", skill["allowed_roles"])
        self.assertIn("research_question", skill["input_schema"]["required"])
        self.assertIn("LiteratureSeedPackage", skill["output_schema"]["properties"]["artifacts"]["items"])
        self.assertIn("aers:eval:citation-hygiene-no-fake-refs", skill["internal_skill"]["quality_gates"]["machine_checkable"])
        self.assertIn("formal_literature_review_writeback", skill["internal_skill"]["human_confirmation"]["required_before"])

    def test_bdd_4_missing_registry_is_safe_and_non_blocking(self) -> None:
        """Given the internal registry is missing, When indexed, Then capability indexing returns unavailable safely."""
        from Product.backend.internal_agent_skill_registry import (
            get_internal_agent_skill_source_info,
            index_internal_agent_skill_capabilities,
        )

        missing = self.temp_dir / "missing.json"

        source = get_internal_agent_skill_source_info(missing)
        capabilities = index_internal_agent_skill_capabilities(missing)

        self.assertFalse(source["available"])
        self.assertEqual(source["reason"], "registry_not_found")
        self.assertEqual(capabilities, [])

    def test_bdd_5_capability_registry_includes_internal_skill_source(self) -> None:
        """Given capability registry reindexes, When internal skills exist, Then product capabilities expose them."""
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
            patch("Product.backend.capability_registry.get_aers_source_info") as aers_info,
            patch("Product.backend.capability_registry.index_aers_capabilities", return_value=[]),
            patch("Product.backend.capability_registry.index_aers_quality_gates", return_value=[]),
            patch("Product.backend.capability_registry.get_internal_agent_skill_source_info") as internal_info,
            patch("Product.backend.capability_registry.index_internal_agent_skill_capabilities") as internal_caps,
        ):
            aers_info.return_value = {
                "available": False,
                "path": "",
                "source_url": "",
                "license": "unknown",
                "summary": {},
                "canonical_policy": {},
            }
            internal_info.return_value = {
                "available": True,
                "path": str(self.registry_path),
                "schema_version": "internal_agent_skill_registry.v1",
                "skill_count": 1,
                "lifecycle_counts": {"internal_draft": 1},
                "canonical_policy": {"auto_write_canonical": False},
            }
            internal_caps.return_value = [
                {
                    "id": "cap_internal_skill_recursive_research_search",
                    "namespace": "internal_agent_skill",
                    "name": "递归研究搜索",
                    "category": "literature_skill",
                    "description": "从题目出发做递归证据搜索。",
                    "risk_level": "medium",
                    "cost_model": "llm_tokens_and_external_sources",
                    "allowed_roles": ["Supervisor", "LiteratureAgent"],
                    "adapter_path": "internal://recursive_research_search",
                    "input_schema": {"type": "object", "required": ["research_question"]},
                    "output_schema": {"type": "object", "properties": {}},
                    "status": "checklist",
                }
            ]

            result = reindex_capabilities(product_root, repo_root, "p1")

        registry = result["capability"]
        self.assertIn("internal_agent_skill_registry", registry["sources"])
        self.assertEqual(registry["sources"]["internal_agent_skill_registry"]["function_count"], 1)
        self.assertIn("cap_internal_skill_recursive_research_search", registry["classification"]["checklist"])

    def test_bdd_6_product_default_registry_contains_first_five_internal_skills(self) -> None:
        """Given the shipped product registry, When indexed, Then the first five adapted skills are discoverable."""
        from Product.backend.internal_agent_skill_registry import (
            get_internal_agent_skill_source_info,
            index_internal_agent_skill_capabilities,
        )

        source = get_internal_agent_skill_source_info()
        capabilities = index_internal_agent_skill_capabilities()
        by_id = {cap["id"]: cap for cap in capabilities}

        self.assertTrue(source["available"])
        self.assertEqual(source["skill_count"], 5)
        self.assertEqual(source["lifecycle_counts"]["internal_draft"], 5)
        self.assertIn("cap_internal_skill_recursive_research_search", by_id)
        self.assertIn("cap_internal_skill_did_staggered_identification_gate", by_id)
        self.assertIn("cap_internal_skill_weak_iv_diagnostic_gate", by_id)
        self.assertIn("cap_internal_skill_aer_abstract_submission_preflight", by_id)
        self.assertIn("cap_internal_skill_replication_package_gate", by_id)
        self.assertTrue(all(cap["namespace"] == "internal_agent_skill" for cap in capabilities))
        self.assertTrue(all(cap["status"] != "executable" for cap in capabilities))

    def test_bdd_7_prompt_registry_exposes_aers_evidence_and_license_context(self) -> None:
        """Given LLM Supervisor selects skills, When prompt registry is compacted, Then AERS context is still auditable."""
        from Product.backend.internal_agent_skill_registry import compact_internal_agent_skills_for_prompt

        prompt_registry = compact_internal_agent_skills_for_prompt()
        by_skill_id = {skill["skill_id"]: skill for skill in prompt_registry["skills"]}

        recursive = by_skill_id["recursive_research_search"]
        self.assertIn("Auto-Empirical-Research-Skills", recursive["external_source_names"])
        self.assertIn("CC-BY-SA-4.0", recursive["source_licenses"])
        self.assertIn("research_question", recursive["required_inputs"])
        self.assertIn("LiteratureSeedPackage", recursive["expected_artifacts"])
        self.assertIn("aers:eval:citation-hygiene-no-fake-refs", recursive["quality_gates"]["machine_checkable"])
        self.assertIn("formal_literature_review_writeback", recursive["human_confirmation"]["required_before"])
        self.assertIn("web_search", recursive["allowed_adapters"])
        self.assertIn(
            "write_formal_literature_review_without_verified_citations",
            recursive["forbidden_actions"],
        )


if __name__ == "__main__":
    unittest.main()
