"""Product.backend.wrapper.search_service BDD 测试。

命名约定: test_bdd_<feature>_<scenario>
中文 docstring 描述业务含义（项目现有风格）。
Phase 2 — 递归搜索（Search）tab 的 service 层单元测试。
"""
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable
from unittest.mock import patch

from Product.backend.wrapper.search_service import (
    build_queries,
    run_queries,
    rerank,
    write_literature,
    verify_search,
    run_search,
)
from Product.types.research import Paper, SearchRequest
from Program.prompts.search.v1 import load_prompt_v1


def _fake_arxiv_results(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """模拟 arxiv-mcp 返回固定 3 篇结果。"""
    return [
        {
            "title": f"Test paper for {query} - A",
            "authors": ["Author X"],
            "year": 2020,
            "abstract": "Abstract A",
            "arxiv_id": f"arxiv-{query}-001",
        },
        {
            "title": f"Test paper for {query} - B",
            "authors": ["Author Y"],
            "year": 2021,
            "abstract": "Abstract B",
            "arxiv_id": f"arxiv-{query}-002",
        },
        {
            "title": f"Test paper for {query} - C",
            "authors": ["Author Z"],
            "year": 2022,
            "abstract": "Abstract C",
            "arxiv_id": f"arxiv-{query}-003",
        },
    ][:max_results]


class SearchServiceBuildQueriesTests(unittest.TestCase):
    """build_queries: LLM 把研究简报 → 3-5 个 arxiv 检索词 JSON。"""

    def test_bdd_build_queries_returns_3_to_5_queries(self) -> None:
        """行为 1: build_queries 返回 3-5 个 dict，每个含 query + rationale。"""
        def fake_chat(messages, **kwargs):
            payload = json.dumps([
                {"query": "industrial robots employment", "rationale": "matches core topic"},
                {"query": "robotics labor market", "rationale": "captures economic angle"},
                {"query": "automation displacement", "rationale": "covers substitution effect"},
            ], ensure_ascii=False)
            return payload, {"input_tokens": 0, "output_tokens": 0}

        results = build_queries(
            brief_text="工业机器人对就业结构的影响",
            chat_completion_fn=fake_chat,
        )
        self.assertIsInstance(results, list)
        self.assertGreaterEqual(len(results), 3)
        self.assertLessEqual(len(results), 5)
        for q in results:
            self.assertIn("query", q)
            self.assertIn("rationale", q)
            self.assertIsInstance(q["query"], str)
            self.assertTrue(q["query"].strip())


class SearchServiceRunQueriesTests(unittest.TestCase):
    """run_queries: 调 arxiv → dedupe → 返回 8-12 篇 Paper。"""

    def test_bdd_run_queries_uses_arxiv_and_returns_deduped_papers(self) -> None:
        """行为 2: run_queries 调 arxiv_fn，对结果按 arxiv_id dedupe 并映射为 Paper。"""
        queries = [
            {"query": "robots employment", "rationale": "x"},
            {"query": "automation labor", "rationale": "y"},
        ]
        papers = run_queries(queries, arxiv_fn=_fake_arxiv_results, per_query=3)
        self.assertIsInstance(papers, list)
        # 两个 query 各 3 篇，去重后应有 6 篇（不同 query 的 arxiv_id 不同）
        self.assertGreaterEqual(len(papers), 5)
        self.assertLessEqual(len(papers), 12)
        ids = [p.arxiv_id for p in papers]
        self.assertEqual(len(ids), len(set(ids)), "arxiv_id should be unique after dedup")
        for p in papers:
            self.assertIsInstance(p, Paper)
            self.assertTrue(p.title)
            self.assertTrue(p.authors)
            self.assertIsInstance(p.year, int)
            self.assertTrue(p.abstract)
            self.assertTrue(p.arxiv_id)

    def test_bdd_run_queries_dedupes_same_arxiv_id_across_queries(self) -> None:
        """行为 3: 同一 arxiv_id 在不同 query 出现时只保留 1 篇。"""
        def overlapping_arxiv(query, max_results=5):
            return [
                {
                    "title": "Shared Paper",
                    "authors": ["A"],
                    "year": 2020,
                    "abstract": "x",
                    "arxiv_id": "shared-001",
                },
            ]

        queries = [
            {"query": "q1", "rationale": "r1"},
            {"query": "q2", "rationale": "r2"},
        ]
        papers = run_queries(queries, arxiv_fn=overlapping_arxiv, per_query=2)
        self.assertEqual(len(papers), 1)
        self.assertEqual(papers[0].arxiv_id, "shared-001")


class SearchServiceRerankTests(unittest.TestCase):
    """rerank: LLM 给每篇 paper 打 relevance_score 0-1。"""

    def test_bdd_rerank_uses_llm_to_score_papers(self) -> None:
        """行为 4: rerank 调用 LLM 给每篇 paper 打分，并按分数倒序排序。"""
        papers = [
            Paper(title="A", authors=["a"], year=2020, abstract="x", arxiv_id="1", relevance_score=0.0),
            Paper(title="B", authors=["b"], year=2021, abstract="y", arxiv_id="2", relevance_score=0.0),
        ]

        def fake_chat(messages, **kwargs):
            payload = json.dumps([
                {"arxiv_id": "1", "relevance_score": 0.6},
                {"arxiv_id": "2", "relevance_score": 0.9},
            ], ensure_ascii=False)
            return payload, {"input_tokens": 0, "output_tokens": 0}

        ranked = rerank(papers, brief_text="brief", chat_completion_fn=fake_chat)
        # LLM 缺失时 rerank 仍能回退（默认 0.5）以保证不崩，但若 LLM 给了分数则必须被使用
        self.assertEqual(len(ranked), 2)
        # 排在第一的应该是分数高的 B
        self.assertEqual(ranked[0].arxiv_id, "2")
        self.assertGreater(ranked[0].relevance_score, ranked[1].relevance_score)
        for p in ranked:
            self.assertGreaterEqual(p.relevance_score, 0.0)
            self.assertLessEqual(p.relevance_score, 1.0)


class SearchServiceVerifyTests(unittest.TestCase):
    """verify_search: verdict gate — 8-12 篇且每篇有 relevance_score。"""

    def test_bdd_verify_passes_when_paper_count_in_range(self) -> None:
        """行为 5: 8-12 篇 paper 时 verify_search 返回 True。"""
        papers = [
            Paper(title=f"p{i}", authors=["a"], year=2020, abstract="x", arxiv_id=f"id{i}", relevance_score=0.5)
            for i in range(10)
        ]
        self.assertTrue(verify_search(papers, min_count=8, max_count=12))

    def test_bdd_verify_fails_when_too_few_papers(self) -> None:
        """行为 6: 少于 min_count 时 verify_search 返回 False。"""
        papers = [
            Paper(title="p1", authors=["a"], year=2020, abstract="x", arxiv_id="1", relevance_score=0.5)
        ]
        self.assertFalse(verify_search(papers, min_count=8, max_count=12))

    def test_bdd_verify_fails_when_score_missing(self) -> None:
        """行为 7: 任一 paper 缺 relevance_score 时 verify_search 返回 False。"""
        papers = [
            Paper(title="p1", authors=["a"], year=2020, abstract="x", arxiv_id="1", relevance_score=0.5)
            for _ in range(10)
        ]
        papers[0].relevance_score = -1.0  # 越界即视为未打分
        self.assertFalse(verify_search(papers, min_count=8, max_count=12))


class SearchServiceWriteLiteratureTests(unittest.TestCase):
    """write_literature: 落盘 Tasks/{slug}/literature.md。"""

    def test_bdd_write_literature_creates_file_with_provenance(self) -> None:
        """行为 8: write_literature 落盘到 Tasks/{topic_slug}/literature.md，附 provenance frontmatter。"""
        papers = [
            Paper(
                title="Industrial Robots",
                authors=["Acemoglu", "Restrepo"],
                year=2020,
                abstract="We study robots...",
                arxiv_id="2003.12345",
                relevance_score=0.92,
                accepted=True,
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = write_literature(
                papers=papers,
                topic="工业机器人对就业结构的影响",
                topic_slug="industrial-robots-employment",
                tasks_root=Path(tmp),
            )
            self.assertTrue(path.exists())
            self.assertEqual(path.name, "literature.md")
            content = path.read_text(encoding="utf-8")
            self.assertIn("---", content, "YAML frontmatter missing")
            self.assertIn("topic_slug: industrial-robots-employment", content)
            self.assertIn("Industrial Robots", content)
            self.assertIn("2003.12345", content)


class SearchServiceEndToEndTests(unittest.TestCase):
    """run_search: 端到端编排（build_queries + run_queries + rerank + write + verify）。"""

    def test_bdd_run_search_end_to_end_with_mocks(self) -> None:
        """行为 9: run_search 调 build→run→rerank→write→verify，返 SearchResponse。"""
        import re as _re

        def fake_chat(messages, **kwargs):
            user_content = messages[-1]["content"] if messages else ""
            if "检索词" in user_content or "arxiv 检索词" in user_content:
                payload = json.dumps([
                    {"query": "robots employment", "rationale": "x"},
                    {"query": "automation labor", "rationale": "y"},
                    {"query": "robotics wage", "rationale": "z"},
                ], ensure_ascii=False)
                return payload, {"input_tokens": 0, "output_tokens": 0}
            # rerank 阶段：从 prompt 里解析所有 arxiv_id，全部打 0.5-0.9 区间分
            ids = _re.findall(r'"arxiv_id":\s*"([^"]+)"', user_content)
            ids = [i for i in ids if i and not i.startswith("stub-")]
            # 按出现顺序打分 0.9, 0.85, 0.8, ...，最低 0.5
            scored = []
            for idx, aid in enumerate(ids):
                score = max(0.5, 0.95 - idx * 0.05)
                scored.append({"arxiv_id": aid, "relevance_score": score})
            return json.dumps(scored, ensure_ascii=False), {"input_tokens": 0, "output_tokens": 0}

        with tempfile.TemporaryDirectory() as tmp:
            brief_path = Path(tmp) / "brief.md"
            brief_path.write_text(
                "# 研究问题\n工业机器人对就业的影响\n## 边际贡献\nx\n## 研究边界\ny\n## 成功标准\nz\n",
                encoding="utf-8",
            )
            req = SearchRequest(
                topic_slug="industrial-robots-employment",
                brief_path=str(brief_path),
            )
            resp = run_search(
                req,
                tasks_root=Path(tmp),
                chat_completion_fn=fake_chat,
                arxiv_fn=_fake_arxiv_results,
                per_query=3,
            )
            self.assertIsNotNone(resp.literature_path)
            self.assertTrue(Path(resp.literature_path).exists())
            self.assertGreaterEqual(len(resp.papers), 5)
            self.assertTrue(resp.verdict_passed)
            for p in resp.papers:
                self.assertGreaterEqual(p.relevance_score, 0.0)
                self.assertLessEqual(p.relevance_score, 1.0)


if __name__ == "__main__":
    unittest.main()
