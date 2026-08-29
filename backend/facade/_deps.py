"""Agent 依赖加载器（facade 收敛 Task 2）。

agent 已是正式安装包（pip install -e），因此这里采用**直接 import + 启动时快速
失败**，彻底移除 facade 顶部那段逐节点的 try/except 吞噬式防御导入。

失败语义：
- 任何 `from agent...` 在导入时报错，都会在本模块被导入时立刻抛出不吞掉，
  由上层（熔断 / 运维日志）一次性记录并给出清晰原因：
  - ``ModuleNotFoundError`` / ``ImportError`` → agent 未正确安装（或未在可导入路径）
  - 其余异常 → agent 内部错误（说明 agent 装上了但自身坏了）
- 那 20 段 `except Exception: X = None` 的"吞错置 None、运行时才 503"的写法
  不再需要：agent 已装，节点必然存在。

注意：这里暴露的每个名字都会被 ``facade/__init__.py`` 原样 re-export 到
facade 包命名空间，以便测试用 ``monkeypatch.setattr("facade.<name>", ...)``
在调用时替换节点函数（保持 ADR-0003 的 monkeypatch 契约不变）。
"""
from __future__ import annotations

# 注意：不要在此急切 ``import agent.graph``。`agent.graph` 在模块顶层引用了
# ``engine.prewrite``，而 prewrite 又在模块顶层把各节点函数绑定进
# ``PRWRITE_SEQUENCE``。若在 facade 加载期就导入它，prewrite 会在测试
# ``monkeypatch.setattr("agent.nodes.X.X", ...)`` 之前把**真实**节点函数绑定好，
# 导致 run_prewrite 绕过被替换的假节点。因此 graph 用下面这个惰性代理暴露：
# facade 初次调用才真正 ``import agent.graph``（那之后测试已 patch，prewrite 会
# 绑定被替换后的假节点）。节点/清洗函数本身不依赖 prewrite，保持急切导入即可。

class _LazyGraph:
    """对 agent.graph 的惰性代理：首次属性访问 / 调用才加载真实 graph。

    ``facade._graph`` 指向本代理（对象非 None），因此
    ``monkeypatch.setattr("facade._graph", FakeGraph()/None)`` 的既有测试语义
    不受影响；未替换时按需加载真实 graph。
    """

    def __init__(self) -> None:
        self._graph: object | None = None

    def _get(self):
        if self._graph is None:
            from agent.graph import graph as _real
            self._graph = _real
        return self._graph

    def __getattr__(self, name: str):
        return getattr(self._get(), name)


graph = _LazyGraph()

from agent.nodes.set_direction import set_direction as set_direction_node
from agent.nodes.generate_outline import generate_outline as generate_outline_node
from agent.nodes.identification_verify import (
    identification_verify as identification_verify_node,
)
from agent.nodes.estimate import estimate as estimate_node
from agent.nodes.robustness_check import robustness_check as robustness_check_node
from agent.nodes.generate_chapter import generate_chapter as generate_chapter_node
from agent.nodes.review_chapter import review_chapter as review_chapter_node
from agent.nodes.search_literature import search_literature as search_literature_node
from agent.nodes.citation_graph import build_citation_graph as build_citation_graph_node
from agent.nodes.rollback import rollback_chapter as rollback_chapter_node
from agent.nodes.export_docx import export_docx as export_docx_node
from agent.nodes.translate_code import translate_code as translate_code_node

from agent.cleaning.transform import TransformStep as TransformStepCls
from agent.cleaning.filter import FilterStep as FilterStepCls
from agent.cleaning.balance import BalanceStep as BalanceStepCls
from agent.cleaning.profiling import (
    _detect_dataset_type as detect_dataset_type_fn,
    _load_charls_config as load_charls_config_fn,
)