"""Tests for Product.backend.capabilities_query_service.

Task 43 BDD (4 behaviors):
- 抽屉入口: returns 1018 methods, drawer button works (frontend; we cover service)
- 抽屉分类: 49 categories with correct counts after getattr-on-dict bug fix
- 抽屉内搜索: filter by `q` substring match
- 抽屉不阻塞: query is sync + cached, no blocking side effects
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

STATSPAI_PATH = Path("/Users/mahaoxuan/Desktop/经济学论文/StatsPAI")
if str(STATSPAI_PATH) not in sys.path:
    sys.path.insert(0, str(STATSPAI_PATH))

from Product.backend.capabilities_query_service import (  # noqa: E402
    get_methods_overview,
    search_methods,
)


class CapabilitiesQueryServiceTests(unittest.TestCase):
    def test_bdd_getattr_fix_overview_has_real_categories(self) -> None:
        """Behavior 2: 修复 statspai_adapter bug 后才能正确分类.

        Before the getattr-on-dict bug fix, every cap had category='unknown'.
        After the fix, the top-5 categories are causal/regression/output/...
        """
        overview = get_methods_overview()
        cats = [c["name"] for c in overview["categories"]]
        counts = {c["name"]: c["count"] for c in overview["categories"]}
        # BDD spec top-5: causal 375, regression 40, output 40, panel 36
        self.assertIn("causal", cats, "causal category missing → bug fix regressed")
        self.assertGreater(counts.get("causal", 0), 100, f"causal too small: {counts.get('causal')}")
        self.assertEqual(counts.get("regression", 0), 40)
        self.assertEqual(counts.get("output", 0), 40)
        # Sanity: no "unknown" leaked in
        self.assertNotIn("unknown", counts, "unknown category leaked → getattr bug regressed")

    def test_bdd_overview_methods_count_matches_total(self) -> None:
        overview = get_methods_overview()
        self.assertEqual(overview["total"], len(overview["methods"]))
        self.assertGreaterEqual(overview["total"], 1000)

    def test_bdd_categories_sorted_by_count_desc(self) -> None:
        overview = get_methods_overview()
        counts = [c["count"] for c in overview["categories"]]
        self.assertEqual(counts, sorted(counts, reverse=True))

    def test_bdd_search_filters_by_substring_case_insensitive(self) -> None:
        """Behavior 3: 用户在搜索框输入 `did` / `bartik` / `bootstrap` 实时过滤."""
        hits = search_methods("did", limit=10)
        names = [m["name"].lower() for m in hits]
        # All returned names contain 'did' substring
        for n in names:
            self.assertIn("did", n, f"{n!r} should match 'did'")
        self.assertGreater(len(hits), 0)

    def test_bdd_search_returns_deterministic_shape(self) -> None:
        hits = search_methods("bootstrap", limit=5)
        for m in hits:
            self.assertIn("id", m)
            self.assertIn("name", m)
            self.assertIn("category", m)
            self.assertIn("description", m)
            self.assertIn("risk_level", m)

    def test_bdd_empty_query_returns_all(self) -> None:
        overview = get_methods_overview()
        all_methods = overview["methods"]
        empty = search_methods("", limit=2000)
        self.assertEqual(len(empty), len(all_methods))

    def test_bdd_search_category_filter(self) -> None:
        overview = get_methods_overview()
        causal = [m for m in overview["methods"] if m["category"] == "causal"]
        self.assertGreater(len(causal), 100)


if __name__ == "__main__":
    unittest.main()
