"""Shared pre-write path for the graph and the Facade.

单一真相：``PRWRITE_SEQUENCE`` 同时是
- ``run_prewrite``（Facade 的 set_direction_and_outline，串行命令式）的执行顺序；
- ``graph.build_graph`` / ``wire_prewrite_edges``（LangGraph 声明式图，并行）的边拓扑。

``PRWRITE_SEQUENCE`` 每一项为 ``(node_id, (module_path, attr), dependencies)``：
- ``node_id``：在图里注册的节点名（``estimate`` 与 state 键重名，故用
  ``run_estimate``；``run_prewrite`` 只用解析出的函数，不关心 id）。
- ``(module_path, attr)``：节点函数的导入来源。函数在**调用期**经
  ``_node_callable`` 解析，而不是 import 时捕获引用——这样测试可以通过
  monkeypatch 节点源模块（如 ``agent.nodes.estimate.estimate``）注入 fake，
  图与命令式路径共用同一接缝。
- ``dependencies``：该节点执行前必须已完成的节点 id。图据此建边，
  ``run_prewrite`` 按列表顺序调用（该顺序是一个满足依赖的合法拓扑序）。

Estimate runs before literature so a slow search cannot hide the table.
"""
from __future__ import annotations

import importlib

from .readiness import claim_mode

# 预写流程单一真相：预写步骤的有序元数据（节点名 + 调用来源 + 前驱依赖）。
# 顺序规则只在这一处表达，图与命令式路径都从它派生，防止两套实现漂移。
# graph 的并行结构由 dependencies 自然导出（identification_verify 并行扇出
# estimate∥literature；robustness_check∥build_citation_graph 扇入 generate_title）。
# run_prewrite 严格执行本列表顺序（保持 Facade HITL 路径的行为不变）。
PRWRITE_SEQUENCE: tuple[tuple[str, tuple[str, str], tuple[str, ...]], ...] = (
    ("set_direction", ("agent.nodes.set_direction", "set_direction"), ()),
    (
        "identification_verify",
        ("agent.nodes.identification_verify", "identification_verify"),
        ("set_direction",),
    ),
    ("run_estimate", ("agent.nodes.estimate", "estimate"), ("identification_verify",)),
    (
        "robustness_check",
        ("agent.nodes.robustness_check", "robustness_check"),
        ("run_estimate",),
    ),
    (
        "search_literature",
        ("agent.nodes.search_literature", "search_literature"),
        ("identification_verify",),
    ),
    (
        "build_citation_graph",
        ("agent.nodes.citation_graph", "build_citation_graph"),
        ("search_literature",),
    ),
    (
        "generate_title",
        ("agent.nodes.generate_title", "generate_title"),
        ("robustness_check", "build_citation_graph"),
    ),
    (
        "generate_outline",
        ("agent.nodes.generate_outline", "generate_outline"),
        ("generate_title",),
    ),
)

# 预写节点 id → (module_path, attr)。供图/命令式路径在构建时解析调用函数。
PRWRITE_SOURCES: dict[str, tuple[str, str]] = {
    node_id: src for node_id, src, _deps in PRWRITE_SEQUENCE
}

# 预写节点 id → 调用函数（import 时捕获的快照，供需要静态引用的场景使用；
# 运行时解析请用 ``_node_callable``，以保持 monkeypatch 接缝生效）。
PRWRITE_NODES: dict[str, object] = {}


def _node_callable(node_id: str):
    """解析预写节点的当前调用函数（运行时读取，patch 源模块可生效）。"""
    module_path, attr = PRWRITE_SOURCES[node_id]
    return getattr(importlib.import_module(module_path), attr)


def run_prewrite(state: dict) -> dict:
    """按 ``PRWRITE_SEQUENCE`` 顺序串行执行预写段（Facade HITL 路径）。

    识别节点后有中断判定：0 星或识别失败则直接返回，不跑估计／文献／大纲。
    """
    for node_id, _src, _deps in PRWRITE_SEQUENCE:
        state = {**state, **(_node_callable(node_id)(state))}
        if node_id == "identification_verify":
            state["claim"] = claim_mode(state)
            if state.get("star_rating") == 0 or state.get("identification_failed"):
                return state
    return state


# 惰性填充 PRWRITE_NODES 快照（延迟到函数体内，避免 import 期副作用）。仅作静态别名。
def _fill_snapshot() -> dict[str, object]:
    return {node_id: _node_callable(node_id) for node_id in PRWRITE_SOURCES}


PRWRITE_NODES.update(_fill_snapshot())