"""识别诊断的三轴状态与唯一许可判定。

背景（issue #40 参谋意见 §2.2、§4）：原来诊断结果被压成一个 0–3 星评分，星级同时
承担三件不同的事，于是三种语义被混在一起：

1. **执行有没有完成** —— ``execution``：completed / partial / failed / not_run；
2. **发现了什么** —— ``assessment``：risk_found / risk_not_found /
   insufficient_evidence / not_applicable；
3. **接下来允许做什么** —— ``permissions``：显式字典。

修掉的三处旧语义：

- 全 ``warn``（没有任何 ``pass``）会掉进 ``return 0``，被当成「完全不可信」硬阻断。
  警告只说明有风险，不等于该设计不可用。
- 一条都评不了（全 ``error`` / 全 ``skipped``）时 ``passed`` 写成 ``True``。尚未评估
  不等于通过；现在是 ``None``（未知）。
- Callaway–Sant'Anna 分支用效应的 ``p < 0.05`` 生成 ``pass``，把「效应显著」当成
  「设计有效」，缺 p 值还会被 ``or 0.0`` 折成 0。效应显著性改记为
  ``role="effect_estimate"``，不参与设计有效性判定。

``star_rating`` 保留为展示值，但它不再单独决定流程是否继续、也不决定论文能否写成因果。
本模块是唯一判定入口：图、Facade 串行路径、章节写入闸门、章节绑定层、HTTP Facade 都调
``identification_decision``，同一份 state 从任何入口问都得到同一个答案。

纯函数，无 I/O、无 LLM、无 pandas。
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

# --- 轴一：执行有没有完成 -------------------------------------------------
EXECUTION_COMPLETED = "completed"
EXECUTION_PARTIAL = "partial"
EXECUTION_FAILED = "failed"
EXECUTION_NOT_RUN = "not_run"

# --- 轴二：发现了什么 -----------------------------------------------------
ASSESSMENT_RISK_FOUND = "risk_found"
ASSESSMENT_RISK_NOT_FOUND = "risk_not_found"
ASSESSMENT_INSUFFICIENT_EVIDENCE = "insufficient_evidence"
ASSESSMENT_NOT_APPLICABLE = "not_applicable"

# --- 诊断条目的角色 -------------------------------------------------------
# design_validity：判定识别设计是否站得住，进入星级与许可。
# effect_estimate：只是把估计结果记下来（例如 Callaway–Sant'Anna 的点估计与 p 值），
#   不参与设计有效性判定 —— 显著与否不是设计有效性的证据。
ROLE_DESIGN_VALIDITY = "design_validity"
ROLE_EFFECT_ESTIMATE = "effect_estimate"
_ROLES = frozenset({ROLE_DESIGN_VALIDITY, ROLE_EFFECT_ESTIMATE})

_EVALUABLE_STATUSES = frozenset({"pass", "warn", "fail"})
_ERROR_STATUSES = frozenset({"error"})
_SKIPPED_STATUSES = frozenset({"skipped"})

# 诊断条目出错后不能再算「没发现问题」。这些状态只影响执行完整度。
_INCOMPLETE_STATUSES = _ERROR_STATUSES | _SKIPPED_STATUSES

# 旧写法可能把失败状态写在 diag 根部（原 bind._FAILED_IDENTIFICATION_STATUSES，
# 已收进这里，避免两处各留一份）。
_FAILED_DIAG_STATUSES = frozenset(
    {"degraded", "error", "failed", "failure", "blocked"}
)


def status_of(item: Any) -> str:
    """诊断条目状态的小写规范化。"""
    if not isinstance(item, Mapping):
        return ""
    return str(item.get("status") or "").strip().lower()


def role_of(item: Any) -> str:
    """诊断条目的角色；缺省按 design_validity 处理（保守：默认参与判定）。"""
    if not isinstance(item, Mapping):
        return ROLE_DESIGN_VALIDITY
    role = str(item.get("role") or "").strip().lower()
    return role if role in _ROLES else ROLE_DESIGN_VALIDITY


def design_validity_diagnostics(diagnostics: Any) -> list[Mapping]:
    """只留判定设计有效性用的条目；效应估计记录被排除。"""
    if not isinstance(diagnostics, Iterable) or isinstance(diagnostics, (str, bytes)):
        return []
    return [
        item
        for item in diagnostics
        if isinstance(item, Mapping) and role_of(item) == ROLE_DESIGN_VALIDITY
    ]


def assess_diagnostics(diagnostics: Any) -> dict[str, Any]:
    """从一个 diagnostics 列表算出执行状态、发现与展示星级。

    星级只在**可评估**的条目上算（``pass`` / ``warn`` / ``fail``）：

    - 有 ``fail``：有 ``pass`` → 1 星；没有 ``pass`` → 0 星（无任何正面证据）
    - 无 ``fail`` 有 ``warn`` → 2 星（有风险，可继续，须披露）
    - 全部 ``pass`` 且没有没跑成的检查 → 3 星
    - 没有可评估条目 → ``None``（未知，不是 0 星）

    ``error`` / ``skipped`` 两档都算「没跑成」：不参与星级，但会把 ``execution`` 降为
    ``partial``，并把 ``passed`` 置为 ``None`` —— 少跑了一项就不能声称「未发现问题」。
    """
    design = design_validity_diagnostics(diagnostics)
    statuses = [status_of(item) for item in design]

    passes = [s for s in statuses if s == "pass"]
    warns = [s for s in statuses if s == "warn"]
    fails = [s for s in statuses if s == "fail"]
    errored = [s for s in statuses if s in _ERROR_STATUSES]
    skipped = [s for s in statuses if s in _SKIPPED_STATUSES]
    evaluable = len(passes) + len(warns) + len(fails)

    counts = {
        "pass": len(passes),
        "warn": len(warns),
        "fail": len(fails),
        "error": len(errored),
        "skipped": len(skipped),
    }

    if not evaluable:
        star: int | None = None
        passed: bool | None = None
        if design or errored or skipped:
            assessment = ASSESSMENT_INSUFFICIENT_EVIDENCE
        else:
            assessment = ASSESSMENT_NOT_APPLICABLE
        execution = EXECUTION_FAILED if errored else EXECUTION_NOT_RUN
        return {
            "execution": execution,
            "assessment": assessment,
            "passed": passed,
            "star_rating": star,
            "counts": counts,
        }

    # 少跑一项（error 或 skipped）都不能声称「没发现问题」，所以也把 passed 置未知。
    incomplete = bool(errored or skipped)

    if fails:
        star = 1 if passes else 0
        passed = False
        assessment = ASSESSMENT_RISK_FOUND
    elif warns:
        star = 2
        passed = None if incomplete else True
        assessment = ASSESSMENT_RISK_FOUND
    elif incomplete:
        star = 2
        passed = None
        assessment = ASSESSMENT_INSUFFICIENT_EVIDENCE
    else:
        star = 3
        passed = True
        assessment = ASSESSMENT_RISK_NOT_FOUND

    execution = EXECUTION_PARTIAL if incomplete else EXECUTION_COMPLETED
    return {
        "execution": execution,
        "assessment": assessment,
        "passed": passed,
        "star_rating": star,
        "counts": counts,
    }


# 许可三档。布尔值不够用：「未知」与「禁止」是两件事，前者不构成拒绝的依据。
PERMISSION_ALLOW = "allow"
PERMISSION_CONFIRM = "confirm"
PERMISSION_FORBID = "forbid"

_PERMISSION_VALUES = frozenset(
    {PERMISSION_ALLOW, PERMISSION_CONFIRM, PERMISSION_FORBID}
)


def permission_is(value: Any, level: str) -> bool:
    """许可是否正好是某一档。未知的取值一律按最保守的 forbid 处理。"""
    normalized = str(value or "").strip().lower()
    if normalized not in _PERMISSION_VALUES:
        return level == PERMISSION_FORBID
    return normalized == level


def permissions_for(
    *,
    assessment: str,
    star_rating: int | None,
    has_failures: bool,
    hard_block: bool,
) -> dict[str, Any]:
    """把状态翻成「接下来允许做什么」。

    每个动作报三档而不是布尔：``allow``（直接可用）／``confirm``（要用户显式越过、
    留痕）／``forbid``（禁止）。布尔值分不出「未知」和「禁止」，而这两者完全不同：
    未知不能当作拒绝的依据。

    对应产品已定的三个桶（`docs/specs/frontend-interaction-principles.md` §5）：

    - **必须拦住**（``hard_block``）：继续、因果表述、主结果晋升全部 ``forbid``。
    - **要劝、用户可越（越过留痕）**：不停流程，因果表述退回 ``confirm``，主结果
      晋升 ``forbid`` —— 有硬失败项时不给主结果。
    - **用户自主**：``allow``。

    未知（``insufficient_evidence`` / ``not_applicable``）既不是通过也不是否定：
    不授予因果表述（``forbid``），主结果晋升要用户越过（``confirm``），但**不阻断继续**
    （``allow``），同时要求披露。

    ``causal_language`` 不是「星级即因果可信度」：1–2 星给的是 ``confirm`` ——
    「可写因果、必须带披露与留痕」，不是干净的许可。
    """
    # 干净许可要求「评估到位且没发现问题」——只看星级是不够的：一个有 3 星、明细却
    # 全是 skipped 的 state（旧快照或手写 state）不该拿到干净因果许可。
    clean = (
        star_rating == 3
        and not has_failures
        and assessment == ASSESSMENT_RISK_NOT_FOUND
    )
    unknown = assessment in {
        ASSESSMENT_INSUFFICIENT_EVIDENCE,
        ASSESSMENT_NOT_APPLICABLE,
    }
    risk_found = assessment == ASSESSMENT_RISK_FOUND

    if hard_block:
        continue_level = PERMISSION_FORBID
        causal_level = PERMISSION_FORBID
        promote_level = PERMISSION_FORBID
    elif has_failures:
        continue_level = PERMISSION_CONFIRM
        causal_level = PERMISSION_CONFIRM
        promote_level = PERMISSION_FORBID
    elif clean:
        continue_level = PERMISSION_ALLOW
        causal_level = PERMISSION_ALLOW
        promote_level = PERMISSION_ALLOW
    elif risk_found:
        continue_level = PERMISSION_ALLOW
        causal_level = PERMISSION_CONFIRM
        promote_level = PERMISSION_CONFIRM
    else:
        # 未知：不阻断、不授予因果、主结果要越过。
        continue_level = PERMISSION_ALLOW
        causal_level = PERMISSION_FORBID
        promote_level = PERMISSION_CONFIRM

    return {
        # 诊断结果从不阻止用户看数据、改设计、写数据描述。
        "view_and_describe_data": PERMISSION_ALLOW,
        "edit_design": PERMISSION_ALLOW,
        "continue_to_estimate": continue_level,
        "causal_language": causal_level,
        "promote_main_result": promote_level,
        "requires_disclosure": bool(risk_found or unknown),
    }


def _as_star(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _diag_star(diag: Mapping | None) -> int | None:
    if not isinstance(diag, Mapping):
        return None
    star = _as_star(diag.get("star_rating"))
    if star is not None:
        return star
    # 旧结构的 diag 没写 star_rating：从 diagnostics 现算，不猜。
    return assess_diagnostics(diag.get("diagnostics"))["star_rating"]


def _from_star(star: int) -> tuple[str, str, bool]:
    """只有星级、没有明细的旧快照：按星级当时的含义回填三轴。

    这类 state 出现在早期会话快照与既有测试夹具里。星级本身是跑过诊断才写下的，
    所以回填不是猜：0–1 星 = 有硬失败项，2 星 = 有风险但不阻断，3 星 = 干净通过。
    一旦明细存在，明细优先 —— 这正是「同一份 state 一个判定」的前提。
    """
    if star <= 0:
        return EXECUTION_FAILED, ASSESSMENT_RISK_FOUND, False
    if star == 1:
        return EXECUTION_PARTIAL, ASSESSMENT_RISK_FOUND, False
    if star == 2:
        return EXECUTION_COMPLETED, ASSESSMENT_RISK_FOUND, True
    return EXECUTION_COMPLETED, ASSESSMENT_RISK_NOT_FOUND, True


def _diag_status_failed(diag: Mapping | None) -> bool:
    if not isinstance(diag, Mapping):
        return False
    if diag.get("degraded") is True:
        return True
    return str(diag.get("status") or "").strip().lower() in _FAILED_DIAG_STATUSES


def identification_decision(state: Mapping[str, Any] | None) -> dict[str, Any]:
    """同一份 state → 同一个判定。所有入口都调它。

    返回 ``present`` / ``execution`` / ``assessment`` / ``star_rating`` / ``passed``
    / ``counts`` / ``has_failures`` / ``hard_block`` / ``untrustworthy``
    / ``permissions``。

    - ``present``：是否已经跑过识别诊断（没有 = 还没评估，不是失败）。
    - ``passed``：``True`` 只表示「跑到的检查都没有硬失败」；``None`` 表示未知。
    - ``counts``：``diagnostics`` 列表里各状态的条数。只有星级、没有明细的旧快照
      没有可数的条目，所以那里是 0，不代表「没有发现问题」。
    - ``hard_block``：**流程**是否停在这里。含显式 ``identification_failed`` 标记，
      所以只认 ``star_rating == 0`` 的入口不会再漏掉它。图、串行预写路径、章节写入
      闸门、HTTP Facade 问的都是这一个。
    - ``untrustworthy``：**章节绑定**用的保守档 —— 比 ``hard_block`` 严一档，
      额外把「跑了但有硬失败项」「diag 根部写着失败状态」也算不可信。两个问题不同，
      所以在同一处各给一个明确答案，而不是让两处各写一套内联判断。
    """
    state = state if isinstance(state, Mapping) else {}
    diag = state.get("identification_diag")
    diag = diag if isinstance(diag, Mapping) else None
    present = bool(diag)

    legacy_failed = state.get("identification_failed") is True

    star = _as_star(state.get("star_rating"))
    if star is None:
        star = _diag_star(diag)

    if present:
        assessed = assess_diagnostics(diag.get("diagnostics"))
        # 新结构把三轴写在 diag 上；写了就以它为准，没写就用现算的。
        execution = str(diag.get("execution") or assessed["execution"])
        assessment = str(diag.get("assessment") or assessed["assessment"])
        passed = diag.get("passed", assessed["passed"])
        if not isinstance(passed, bool):
            passed = None
        counts = assessed["counts"]
        if diag.get("assessment") and star is None:
            star = _as_star(diag.get("star_rating"))
        # 只有星级、**完全没有明细**才是旧快照，按星级回填三轴。
        # 有明细却一条都评不了（全 error / 全 skipped）不是旧快照，是「没跑成」——
        # 那种情况必须留在 insufficient_evidence，不能被星级抬成已评估。
        if (
            not diag.get("diagnostics")
            and star is not None
            and not diag.get("assessment")
        ):
            execution, assessment, passed = _from_star(star)
    elif star is not None:
        execution, assessment, passed = _from_star(star)
        counts = {"pass": 0, "warn": 0, "fail": 0, "error": 0, "skipped": 0}
    else:
        execution = EXECUTION_NOT_RUN
        assessment = ASSESSMENT_INSUFFICIENT_EVIDENCE
        passed = None
        counts = {"pass": 0, "warn": 0, "fail": 0, "error": 0, "skipped": 0}

    has_failures = bool(counts.get("fail")) or passed is False
    hard_block = legacy_failed or star == 0
    untrustworthy = (
        hard_block or has_failures or passed is False or _diag_status_failed(diag)
    )

    return {
        "present": present,
        "execution": execution,
        "assessment": assessment,
        "star_rating": star,
        "passed": passed,
        "has_failures": has_failures,
        "counts": counts,
        "hard_block": hard_block,
        "untrustworthy": untrustworthy,
        "permissions": permissions_for(
            assessment=assessment,
            star_rating=star,
            has_failures=has_failures,
            hard_block=hard_block,
        ),
    }


def identification_hard_block(state: Mapping[str, Any] | None) -> bool:
    """流程是否停在这里。图 / 串行路径 / 写入闸门 / HTTP Facade 共用这一个答案。"""
    return bool(identification_decision(state)["hard_block"])


def identification_untrustworthy(state: Mapping[str, Any] | None) -> bool:
    """识别结论是否不可信到不能支撑因果主张（章节绑定用的保守档）。

    比 ``hard_block`` 严：额外把「跑了但有硬失败项」与 diag 根部的失败状态算进来。
    未验证与未提供都不算可信。
    """
    return bool(identification_decision(state)["untrustworthy"])


def identification_trusted(state: Mapping[str, Any] | None) -> bool:
    """识别结论是否可信到可以据此做干净的因果表述。

    最严一档：没有硬失败、跑到位、每一条设计有效性检查都通过。未验证与未提供都不算。
    """
    decision = identification_decision(state)
    if decision["untrustworthy"]:
        return False
    if decision["passed"] is not True:
        return False
    if decision["assessment"] != ASSESSMENT_RISK_NOT_FOUND:
        return False
    return decision["star_rating"] == 3


__all__ = [
    "ASSESSMENT_INSUFFICIENT_EVIDENCE",
    "ASSESSMENT_NOT_APPLICABLE",
    "ASSESSMENT_RISK_FOUND",
    "ASSESSMENT_RISK_NOT_FOUND",
    "EXECUTION_COMPLETED",
    "EXECUTION_FAILED",
    "EXECUTION_NOT_RUN",
    "EXECUTION_PARTIAL",
    "PERMISSION_ALLOW",
    "PERMISSION_CONFIRM",
    "PERMISSION_FORBID",
    "ROLE_DESIGN_VALIDITY",
    "ROLE_EFFECT_ESTIMATE",
    "assess_diagnostics",
    "design_validity_diagnostics",
    "identification_decision",
    "identification_hard_block",
    "identification_trusted",
    "identification_untrustworthy",
    "permission_is",
    "permissions_for",
    "role_of",
    "status_of",
]
