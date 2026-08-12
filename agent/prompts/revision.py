"""评审回炉字段：弱维 + 修改约束。

所有章节 USER_TEMPLATE 都带 ``{low_dims}`` / ``{revision_suggestions}``。
首轮这两个键为空串；``fill_revision`` 给缺省，避免 ``str.format`` KeyError。
"""
from __future__ import annotations

from typing import Any, Dict

REVISION_BLOCK = (
    "\n\n上一轮弱维：{low_dims}。修改约束：{revision_suggestions}。\n"
    "不得只增加关键词，必须补假设或检验。"
)

REVISION_KEYS = ("low_dims", "revision_suggestions")


def fill_revision(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """复制 kwargs，缺省弱维 / 修改约束为空串，杜绝格式化残留 None。"""
    out = dict(kwargs)
    for key in REVISION_KEYS:
        value = out.get(key, "")
        if value is None:
            value = ""
        out[key] = value
    return out
