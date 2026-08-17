"""ADR-0003 Stage A: schema 一致性测试。

验证：
1. 每个 *Output TypedDict 的字段集 ⊆ EconPaperState.__annotations__.keys()
2. 节点函数返回类型注解是对应的 *Output，而非裸 dict
"""
import inspect
from typing import get_type_hints

from protocols import (
    UploadDataOutput, CleanDataOutput, GenerateTitleOutput, SetDirectionOutput,
    EstimateOutput, GenerateOutlineOutput, GenerateChapterOutput, TranslateCodeOutput,
    ExportDocxOutput, ApproveChapterOutput, RollbackOutput, ReviewOutput,
    CitationGraphOutput, ReferencesOutput, LiteratureOutput,
)
from state import EconPaperState
from nodes.upload_data import upload_data
from nodes.clean_data import clean_data
from nodes.generate_title import generate_title
from nodes.set_direction import set_direction
from nodes.estimate import estimate
from nodes.generate_outline import generate_outline
from nodes.generate_chapter import generate_chapter
from nodes.review_chapter import review_chapter
from nodes.translate_code import translate_code
from nodes.export_docx import export_docx
from nodes.approve_chapter import approve_chapter
from nodes.rollback import rollback_chapter
from nodes.citation_graph import build_citation_graph
from nodes.generate_references import generate_references
from nodes.search_literature import search_literature


STATE_KEYS = set(EconPaperState.__annotations__.keys())

# (节点函数, 期望的 Output TypedDict)
NODES = [
    (upload_data, UploadDataOutput),
    (clean_data, CleanDataOutput),
    (generate_title, GenerateTitleOutput),
    (set_direction, SetDirectionOutput),
    (estimate, EstimateOutput),
    (generate_outline, GenerateOutlineOutput),
    (generate_chapter, GenerateChapterOutput),
    (review_chapter, ReviewOutput),
    (translate_code, TranslateCodeOutput),
    (export_docx, ExportDocxOutput),
    (approve_chapter, ApproveChapterOutput),
    (rollback_chapter, RollbackOutput),
    (build_citation_graph, CitationGraphOutput),
    (generate_references, ReferencesOutput),
    (search_literature, LiteratureOutput),
]


def test_output_fields_subset_of_state():
    """每个 Output TypedDict 的字段必须 ⊆ EconPaperState 字段集。"""
    for func, output_type in NODES:
        output_keys = set(output_type.__annotations__.keys())
        extra = output_keys - STATE_KEYS
        assert not extra, f"{func.__name__} 的 Output 含 state 外字段: {extra}"


def test_node_return_type_is_output():
    """节点函数的返回类型注解必须是对应的 *Output，而非裸 dict。"""
    for func, expected_output in NODES:
        hints = get_type_hints(func)
        return_hint = hints.get("return")
        assert return_hint is expected_output, (
            f"{func.__name__} 返回类型应为 {expected_output.__name__}, 实际 {return_hint}"
        )
