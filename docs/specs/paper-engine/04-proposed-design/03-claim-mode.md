# 主张模式（只降不升）

> 上级：[Proposed Design](../04-proposed-design.md)


```python
def machine_claim(state) -> str:
    rd = state.get("research_direction") or {}
    method = str(rd.get("method") or "").strip().lower()
    star = state.get("star_rating")
    if star == 0:
        return "blocked"
    if method in {"did", "iv", "rd", "rdd", "scm"} and isinstance(star, int) and star >= 1:
        return "causal_with_caveat"
    return "association"  # OLS、未知、star is None、诊断没跑成


def claim_mode(state) -> str:
    """机器只降级。用户写 association，2 星 DiD 也保持 association。"""
    machine = machine_claim(state)
    user = str((state.get("research_direction") or {}).get("claim") or "").strip().lower()
    if machine == "blocked":
        return "blocked"
    if user in {"association", "assoc", "correlation"}:
        return "association"
    return machine
```

OLS / `_norm_method` 返回 None：`star_rating is None`，`claim_mode == "association"`。这是成功路径。
