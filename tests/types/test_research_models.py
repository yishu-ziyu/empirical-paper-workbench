"""Product.types.research Pydantic 模型 BDD 测试。

命名约定: test_bdd_<feature>_<scenario>
中文 docstring 描述业务含义（项目现有风格）。
"""
import unittest

from Product.types.research import (
    BriefRequest, BriefResponse,
    Paper, SearchRequest, SearchResponse,
    Variable, VariablesRequest, VariablesResponse,
    DesignCandidate, DesignRequest, DesignResponse,
    ExecuteRequest, ExecuteEvent,
)


class ResearchModelsTests(unittest.TestCase):

    def test_bdd_brief_request_accepts_topic_only(self) -> None:
        """行为 1: BriefRequest 必填 topic，topic_slug 可选。"""
        req = BriefRequest(topic="工业机器人对就业的影响", topic_slug=None)
        self.assertEqual(req.topic, "工业机器人对就业的影响")
        self.assertIsNone(req.topic_slug)

    def test_bdd_brief_request_accepts_explicit_slug(self) -> None:
        """行为 2: 显式传 topic_slug 时保留原值。"""
        req = BriefRequest(topic="CFPS 工业机器人", topic_slug="cfps-robots-2020")
        self.assertEqual(req.topic_slug, "cfps-robots-2020")

    def test_bdd_paper_has_all_required_fields(self) -> None:
        """行为 3: Paper 含题名/作者/年/摘要/arxiv_id/相关性评分/采纳标志。"""
        p = Paper(
            title="Industrial Robots and Employment",
            authors=["Acemoglu", "Restrepo"],
            year=2020,
            abstract="We study...",
            arxiv_id="2003.12345",
            relevance_score=0.92,
            accepted=True,
        )
        self.assertEqual(p.year, 2020)
        self.assertTrue(p.accepted)
        self.assertAlmostEqual(p.relevance_score, 0.92)

    def test_bdd_paper_relevance_score_must_be_in_unit_interval(self) -> None:
        """行为 4: relevance_score 必须在 [0, 1] 区间，越界则校验失败。"""
        with self.assertRaises(Exception):
            Paper(
                title="x", authors=["a"], year=2020, abstract="",
                arxiv_id="x", relevance_score=1.5,
            )

    def test_bdd_variable_role_must_be_one_of_five(self) -> None:
        """行为 5: Variable.role 必须是 5 个枚举值之一。"""
        v = Variable(
            role="X", dataset_column="irobot_density",
            semantic_label="工业机器人渗透率", description="每万名工人拥有机器人数",
        )
        self.assertEqual(v.role, "X")
        with self.assertRaises(Exception):
            Variable(
                role="invalid_role",
                dataset_column="x", semantic_label="x", description="x",
            )

    def test_bdd_design_candidate_method_must_be_did_iv_rdd_psm_dml(self) -> None:
        """行为 6: DesignCandidate.method 必须是 DID/IV/RDD/PSM/DML 之一。"""
        c = DesignCandidate(method="IV", rationale="适合工具变量", fits_data=True)
        self.assertEqual(c.method, "IV")
        with self.assertRaises(Exception):
            DesignCandidate(method="OLS", rationale="x", fits_data=False)

    def test_bdd_execute_event_supports_all_event_types(self) -> None:
        """行为 7: ExecuteEvent 6 种 event 类型都能构造（start/progress/section_done/paper_ready/done/error）。"""
        for ev in ["start", "progress", "section_done", "paper_ready", "done", "error"]:
            e = ExecuteEvent(event=ev, stage="writing", message="x")
            self.assertEqual(e.event, ev)
        with self.assertRaises(Exception):
            ExecuteEvent(event="unknown_event", stage="x", message="x")

    def test_bdd_execute_event_paper_ready_carries_paths(self) -> None:
        """行为 8: paper_ready 事件带 paper_pdf_path + results_json_path。"""
        e = ExecuteEvent(
            event="paper_ready",
            stage="done",
            message="paper rendered",
            paper_pdf_path="Manuscripts/cfps/paper.pdf",
            results_json_path="Results/cfps/results.json",
        )
        self.assertEqual(e.paper_pdf_path, "Manuscripts/cfps/paper.pdf")
        self.assertEqual(e.results_json_path, "Results/cfps/results.json")

    def test_bdd_variables_request_dataset_name_enum(self) -> None:
        """行为 9: VariablesRequest.dataset_name 必须是 4 个枚举值之一。"""
        req = VariablesRequest(
            topic_slug="cfps-robots", brief_path="x",
            dataset_name="CFPS", custom_dataset_path=None,
        )
        self.assertEqual(req.dataset_name, "CFPS")
        with self.assertRaises(Exception):
            VariablesRequest(
                topic_slug="x", brief_path="x", dataset_name="BOGUS",
            )

    def test_bdd_search_response_papers_default_to_accepted(self) -> None:
        """行为 10: Paper.accepted 默认 True（用户未排除则采纳）。"""
        p = Paper(
            title="x", authors=["a"], year=2020, abstract="",
            arxiv_id="x", relevance_score=0.5,
        )
        self.assertTrue(p.accepted)
