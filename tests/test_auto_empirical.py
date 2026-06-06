import json
import shutil
import tempfile
import unittest
from pathlib import Path

from Program.workbench.auto_empirical import (
    JsonlLedger,
    SourceRegistry,
    build_raw_data_manifest,
    load_capability_sources,
    load_research_search_space,
    score_candidate,
    verify_raw_data_manifest,
)
from Program.workbench.auto_empirical.capabilities import missing_required_capabilities
from Program.workbench.auto_empirical.guards import validate_no_readonly_writes, validate_registered_inputs


REPO_ROOT = Path("/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板")


class AutoEmpiricalWorkbenchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="auto-empirical-"))
        self.raw_root = self.temp_dir / "raw_sources"
        self.raw_root.mkdir()
        self.raw_file = self.raw_root / "survey.csv"
        self.raw_file.write_text("id,y\n1,2\n", encoding="utf-8")
        self.registry_path = self.temp_dir / "source_registry.json"
        self.registry_path.write_text(
            json.dumps(
                {
                    "sources": {
                        "raw": {
                            "path": str(self.raw_root),
                            "type": "raw_dataset_motherlode",
                            "status": "registered",
                            "mutable": False,
                            "notes": ["read-only"],
                        }
                    }
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_capability_sources_register_stats_engine_and_skill_library(self) -> None:
        sources = load_capability_sources(REPO_ROOT / "Program/config/capabilities.yml")
        by_name = {source.name: source for source in sources}

        self.assertIn("empirical_skills", by_name)
        self.assertIn("auto_empirical_research_skills", by_name)
        self.assertIn("statspai", by_name)
        self.assertTrue(by_name["empirical_skills"].exists)
        self.assertTrue(by_name["statspai"].exists)
        self.assertFalse(by_name["auto_empirical_research_skills"].required)
        self.assertEqual(missing_required_capabilities(sources), [])

    def test_source_registry_accepts_registered_paths_only(self) -> None:
        registry = SourceRegistry.from_file(self.registry_path)

        self.assertTrue(registry.is_registered_path(self.raw_file))
        self.assertFalse(registry.is_registered_path(self.temp_dir / "unregistered.csv"))
        self.assertEqual(validate_registered_inputs([self.raw_file], registry), [])
        self.assertEqual(
            validate_registered_inputs([self.temp_dir / "unregistered.csv"], registry)[0]["violation"],
            "unregistered_source",
        )

    def test_raw_data_manifest_detects_mutation(self) -> None:
        manifest = build_raw_data_manifest([self.raw_file])

        self.assertEqual(verify_raw_data_manifest(manifest), [])
        self.raw_file.write_text("id,y\n1,999\n", encoding="utf-8")
        violations = verify_raw_data_manifest(manifest)

        self.assertEqual(violations[0]["violation"], "hash_changed")

    def test_readonly_source_write_guard_flags_raw_changes(self) -> None:
        registry = SourceRegistry.from_file(self.registry_path)

        violations = validate_no_readonly_writes([self.raw_file], registry)

        self.assertEqual(violations[0]["violation"], "readonly_source_modified")
        self.assertEqual(violations[0]["source"], "raw")

    def test_search_space_loads_local_empirical_design_space(self) -> None:
        search_space = load_research_search_space(REPO_ROOT / "Program/config/research_search_space.yml")

        self.assertIn("clds", search_space.dataset_keys())
        self.assertIn("matching_efficiency", search_space.outcome_keys())
        self.assertIn("bartik_shift_share", search_space.design_keys())
        self.assertIn("raw data is read-only", search_space.hard_constraints)

    def test_candidate_score_accepts_stable_paths_and_rejects_violations(self) -> None:
        accepted = score_candidate(
            {
                "data_feasibility": 1.0,
                "identification_credibility": 0.8,
                "literature_novelty": 0.8,
                "result_stability": 0.7,
                "mechanism_clarity": 0.8,
                "writing_fit": 0.9,
            }
        )
        rejected = score_candidate(
            {
                "data_feasibility": 1.0,
                "identification_credibility": 1.0,
                "literature_novelty": 1.0,
                "result_stability": 1.0,
                "mechanism_clarity": 1.0,
                "writing_fit": 1.0,
            },
            violations=["raw_data_modified"],
        )

        self.assertTrue(accepted.accepted)
        self.assertGreaterEqual(accepted.score, 70.0)
        self.assertFalse(rejected.accepted)
        self.assertEqual(rejected.score, 0.0)

    def test_jsonl_ledger_appends_without_overwriting_previous_records(self) -> None:
        ledger = JsonlLedger(self.temp_dir / "exploration_ledger.jsonl")

        first = ledger.append({"spec_id": "s1", "status": "failed"})
        second = ledger.append({"spec_id": "s2", "status": "kept"})
        records = ledger.read_all()

        self.assertEqual([record["spec_id"] for record in records], ["s1", "s2"])
        self.assertIn("created_at", first)
        self.assertIn("created_at", second)


if __name__ == "__main__":
    unittest.main()
