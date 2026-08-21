"""对照用的四份稿件。每份已经写好，不跑整条写作流水线。"""
from __future__ import annotations

from typing import Any, Dict, List


def _base(
    *,
    packet_id: str,
    chapter_type: str,
    content: str,
    auto_decision: str,
    method: str = "DID",
    extra: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    idx = {"intro": 0, "lit_review": 1, "data_desc": 2, "methods": 3, "results": 4, "conclusion": 5}[
        chapter_type
    ]
    state: Dict[str, Any] = {
        "session_id": f"ab-{packet_id}",
        "packet_id": packet_id,
        "research_direction": {
            "question": "城乡医保整合是否降低农村中老年人住院自付支出？",
            "method": method,
            "dv": "ln_oophos",
            "iv": "nrcms_enroll",
        },
        "claim": "整合是否减负高度依赖固定效应，首选规格不支持显著下降。",
        "star_rating": 2,
        "identification_failed": False,
        "current_chapter_index": idx + 1,
        "review_chapter_index": idx,
        "review_iteration": 1,
        "max_review_iterations": 2,
        "review_scores": [0.82 if auto_decision == "pass" else 0.41],
        "review_feedback": [
            "机器意见：关键词覆盖充分，建议通过。"
            if auto_decision == "pass"
            else "机器意见：识别交代不足，建议重写。"
        ],
        "revision_suggestions": ["补充稳健性。"],
        "review_rubrics": [
            {
                "endogeneity": 0.8,
                "identification": 0.8,
                "robustness": 0.7,
                "contribution": 0.8,
                "readability": 0.8,
            }
            if auto_decision == "pass"
            else {
                "endogeneity": 0.3,
                "identification": 0.2,
                "robustness": 0.4,
                "contribution": 0.4,
                "readability": 0.5,
            }
        ],
        "citation_indices": {"10.1093/restud/rdaa084": 1, "10.1016/j.jhealeco.2015.01.004": 2},
        "literature_entries": [
            {
                "title": "Difference-in-Differences with Multiple Time Periods",
                "authors": ["Callaway", "Sant'Anna"],
                "year": 2021,
                "doi": "10.1093/restud/rdaa084",
            }
        ],
        "body_chapters": [
            {
                "type": chapter_type,
                "title": chapter_type,
                "content": content,
                "status": "generated",
                "chapter_index": idx,
            }
        ],
    }
    if extra:
        state.update(extra)
    # review_* 列表按当前章对齐：collect 用 review_chapter_index
    # 上面 scores 只有 1 项，把 index 改成 0 以免越界
    state["review_chapter_index"] = 0
    state["current_chapter_index"] = 1
    state["body_chapters"][0]["chapter_index"] = 0
    return state


def packet_good_methods() -> Dict[str, Any]:
    content = (
        "本文用 CHARLS 2011–2020 面板，处理组为新农合参保人，对照为城镇职工/居民医保。"
        "因各省整合时点交错，主规格采用 Callaway–Sant'Anna [1] 处理交错 DID，"
        "并报告平行趋势事件研究。CHARLS 流失与回忆偏差写入威胁卡："
        "死亡/失访与住院利用相关，故稳健性排除 2020 年疫情波。"
        "不能把简单双向固定效应的负向结果写成政策减负。"
    )
    return _base(
        packet_id="good_methods",
        chapter_type="methods",
        content=content,
        auto_decision="pass",
    )


def packet_keyword_intro() -> Dict[str, Any]:
    content = (
        "本文使用 DID IV RDD 三重差分合成控制断点回归因果识别。"
        "内生性稳健性异质性安慰剂平行趋势弱工具变量均已考虑。"
        "城乡医保整合显著降低农村中老年住院自付支出，贡献巨大。"
        "没写谁被处理、什么时候开始、跟谁比，也没写 CHARLS 流失。"
    )
    return _base(
        packet_id="keyword_intro",
        chapter_type="intro",
        content=content,
        auto_decision="pass",
    )


def packet_invented_cite() -> Dict[str, Any]:
    content = (
        "文献表明医保整合显著减负 [99]。Callaway 的交错 DID 见 [1]。"
        "另有研究指出弱工具在此设定中不存在 [17]。"
    )
    return _base(
        packet_id="invented_cite",
        chapter_type="lit_review",
        content=content,
        auto_decision="pass",
    )


def packet_overclaim_results() -> Dict[str, Any]:
    content = (
        "表 3 首选规格 M5 系数为 +0.081，标准误 0.053，不显著。"
        "2015 安慰剂未通过。据此我们得出：城乡医保整合显著降低了"
        "农村中老年人住院自付支出，政策效果稳健。"
    )
    return _base(
        packet_id="overclaim_results",
        chapter_type="results",
        content=content,
        auto_decision="pass",
    )


def packet_weak_iv() -> Dict[str, Any]:
    content = (
        "本文用省级医保办公室距离作为工具变量估计整合对自付支出的影响。"
        "没有报告一阶段统计量，没有弱工具表。CHARLS 个体聚类。"
    )
    return _base(
        packet_id="weak_iv",
        chapter_type="methods",
        content=content,
        auto_decision="fail",
        method="IV",
    )


def all_packets() -> List[Dict[str, Any]]:
    return [
        packet_good_methods(),
        packet_keyword_intro(),
        packet_invented_cite(),
        packet_overclaim_results(),
        packet_weak_iv(),
    ]
