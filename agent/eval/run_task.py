"""headless 跑分器：在无 LLM、无前端、无 Postgres 的条件下跑一个 eval 任务并打分。

用法（在仓库根目录或 backend/ 下）：
    backend/.venv/bin/python agent/eval/run_task.py undergrad_did_01

流程：
1. 从 agent/eval/tasks/<task_id>/task.json + dataset.csv 构造初始 state。
   绕过真实 upload_data 节点：直接把 dataset.csv 读成 DataFrame，
   按 upload_data 实际写入的字段形状（name/path/format/columns/rows/
   dtypes/missing_count）手工构造 uploaded_datasets，等价于
   upload_data 之后的形态。csv_path 在真实流程里由 backend 于上传时
   写入，这里同样等价补齐（identification_verify / estimate 都读它）。
2. 强制 LLM mock：ECONPAPER_LLM=mock（llm/router.py 优先级 1），
   在任何 agent 模块 import 之前设置——router 是 import 时实例化的。
   本任务涉及的 4 个节点本身不调 LLM（纯 pandas / StatsPAI），
   设 mock 是为了兜住未来链路扩展，并让基线可复现。
3. 逐节点推进到 estimate 完成（等价于 agent/graph.py 预写图的前半段，
   但不走 build_graph()——它会连 Postgres checkpointer，headless 环境无 DB）：
       clean_data → (route_after_clean: 有方向) → set_direction
       → identification_verify → (route_after_identification: 星级>0)
       → estimate
   与图一致的差异：0 星时真图会进 hitl_pause 等用户调整，headless
   直接截断打分；estimate 之后的 robustness_check / search_literature
   并行臂不在本基线范围。
4. 逐条跑 rubric.json 的 check（CHECK_FUNCS 函数字典），输出 JSON
   分数卡到 stdout（进度信息走 stderr），全过退出码 0，否则 1。

基线意义：mock 下 estimate 走固定 StatsPAI 分派（非 LLM），先证明
"无 LLM 的固定管线"在该任务上能拿几分；Phase A 的 agent 模式跑同一
任务即可对比增量。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

# ---------------------------------------------------------------------------
# 0. 环境强制（必须在任何 agent 模块 import 之前）
# ---------------------------------------------------------------------------
# llm/router.py 的配置优先级：ECONPAPER_LLM=mock 是第 1 优先级，
# 覆盖 SSOT 文件里的 MiniMax key。headless 基线绝不真调 LLM API。
os.environ["ECONPAPER_LLM"] = "mock"

# agent/ 用扁平 import（from nodes.xxx import ...），需要 agent/ 在 sys.path
_AGENT_DIR = Path(__file__).resolve().parents[1]
if str(_AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENT_DIR))

TASKS_ROOT = Path(__file__).resolve().parent / "tasks"

# ---------------------------------------------------------------------------


def log(msg: str) -> None:
    """进度信息只走 stderr，保证 stdout 是纯 JSON 分数卡。"""
    print(f"[run_task] {msg}", file=sys.stderr)


def load_task(task_id: str) -> Tuple[Path, Dict[str, Any], List[Dict[str, Any]]]:
    """读 task.json + rubric.json，校验数据文件存在。"""
    task_dir = TASKS_ROOT / task_id
    if not task_dir.is_dir():
        available = sorted(p.name for p in TASKS_ROOT.iterdir() if p.is_dir())
        raise SystemExit(
            f"任务不存在: {task_id}（TASKS_ROOT={TASKS_ROOT}，可用: {available}）"
        )
    task = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    rubric = json.loads((task_dir / "rubric.json").read_text(encoding="utf-8"))
    data_file = task_dir / str(task.get("data_file") or "dataset.csv")
    if not data_file.is_file():
        raise SystemExit(f"数据文件缺失: {data_file}（先跑同目录 gen_dataset.py）")
    return task_dir, task, rubric


def build_initial_state(task_id: str, task: Dict[str, Any], csv_path: Path, workspace: str) -> Dict[str, Any]:
    """构造初始 state：等价于 upload_data 之后的形态 + 用户已确认方向。

    upload_data 节点（agent/nodes/upload_data.py）对带 path 的数据集
    实际写入：name/path/format/columns/rows/dtypes/missing_count。
    这里按 pandas 现算同样的字段，绕过文件上传入口。
    """
    import pandas as pd

    df = pd.read_csv(csv_path)
    meta = {
        "name": csv_path.name,
        "path": str(csv_path),
        "format": "csv",
        "columns": list(df.columns),
        "rows": int(len(df)),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_count": int(df.isna().sum().sum()),
    }

    # research_direction：与 backend POST /sessions/{id}/direction 写入的
    # 字段对齐（set_direction.py 顶部注释）；id_col/time_col 显式给出，
    # 避免 project_method_columns 靠列名猜测注入降级记录。
    rd: Dict[str, Any] = {
        "question": task["research_question"],
        "dv": task["dv"],
        "iv": task["treatment"],
        "controls": list(task.get("controls") or []),
        "method": task["method"],
        "id_col": task.get("id_col") or "",
        "time_col": task.get("time_col") or "",
        "template": "cn_journal",
        "claim": "causal",
    }
    if task.get("cluster"):
        rd["cluster"] = task["cluster"]

    return {
        "session_id": f"eval_{task_id}",
        "csv_path": str(csv_path),
        "uploaded_datasets": [meta],
        "workspace": workspace,
        "research_direction": rd,
    }


def run_pipeline(state: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str], List[str]]:
    """逐节点推进到 estimate 完成，镜像 agent/graph.py 预写图前半段的边。

    不 import agent/graph.py：它在模块级 build_graph() → _get_checkpointer()
    → psycopg.connect(Postgres)，headless 环境没有 DB。逐节点调用与图中
    该段路径逐字段等价（每个节点返回部分 dict，按 key 合并，LangGraph
    的合并语义就是按 key 整体替换）。
    """
    from nodes.clean_data import clean_data
    from nodes.estimate import estimate
    from nodes.identification_verify import identification_verify
    from nodes.set_direction import set_direction

    nodes_run: List[str] = []
    stop_reasons: List[str] = []

    # clean_data（upload 已被初始 state 等价替代）
    state.update(clean_data(state))
    nodes_run.append("clean_data")

    # route_after_clean：有 research_direction（question/dv）才进 set_direction
    rd = state.get("research_direction") or {}
    if not (isinstance(rd, dict) and (rd.get("question") or rd.get("dv"))):
        stop_reasons.append("route_after_clean: 无研究方向，图在此 END")
        return state, nodes_run, stop_reasons

    state.update(set_direction(state))
    nodes_run.append("set_direction")

    state.update(identification_verify(state))
    nodes_run.append("identification_verify")

    # route_after_identification：0 星 → hitl_pause（真图等用户调整）；
    # headless 无用户输入，直接截断打分，让 pipeline_completed 判 fail。
    if state.get("star_rating") == 0:
        stop_reasons.append("route_after_identification: 0 星截断（真图进 hitl_pause）")
        return state, nodes_run, stop_reasons

    state.update(estimate(state))
    nodes_run.append("estimate")
    # 真图 estimate 之后还有 robustness_check / search_literature 并行臂
    # 与标题/大纲生成，均超出本基线（推进到 estimate 完成）的范围。
    return state, nodes_run, stop_reasons


# ---------------------------------------------------------------------------
# rubric check 函数字典：fn(state, params) -> (pass, detail)
# ---------------------------------------------------------------------------
def check_pipeline_completed(state: Dict[str, Any], params: Dict[str, Any]) -> Tuple[bool, str]:
    del params
    parts: List[str] = []
    ok = True

    steps = (state.get("cleaning_report") or {}).get("steps") or []
    failed = [s.get("name") for s in steps if s.get("status") != "success"]
    if not steps:
        ok = False
        parts.append("cleaning_report 缺失")
    elif failed:
        ok = False
        parts.append(f"cleaning 失败步骤: {failed}")
    else:
        parts.append(f"cleaning {len(steps)} 步全 success")

    if state.get("identification_diag"):
        parts.append("identification_diag 已写出")
    else:
        ok = False
        parts.append("identification_diag 缺失")

    est = state.get("estimate") or {}
    if est.get("status") == "ok":
        parts.append("estimate status=ok")
    else:
        ok = False
        detail = f"estimate status={est.get('status') or '缺失'}"
        if est.get("error"):
            detail += f"（error: {str(est['error'])[:160]}）"
        parts.append(detail)
    return ok, "；".join(parts)


def check_identification_passed(state: Dict[str, Any], params: Dict[str, Any]) -> Tuple[bool, str]:
    del params
    diag = state.get("identification_diag") or {}
    passed = diag.get("passed") is True
    strategy = diag.get("strategy")
    detail = f"strategy={strategy} passed={diag.get('passed')}"
    if not passed and diag.get("report"):
        detail += f"（report: {str(diag['report'])[:160]}）"
    return passed, detail


def check_estimate_stars_gte_2(state: Dict[str, Any], params: Dict[str, Any]) -> Tuple[bool, str]:
    del params
    star = state.get("star_rating")
    if star is None:
        star = (state.get("identification_diag") or {}).get("star_rating")
    ok = star is not None and int(star) >= 2
    return ok, f"star_rating={star}（None 表示诊断没跑成）"


def check_coef_within_tolerance(state: Dict[str, Any], params: Dict[str, Any]) -> Tuple[bool, str]:
    target = float(params.get("target", 2.5))
    tolerance = float(params.get("tolerance", 0.6))
    est = state.get("estimate") or {}
    coef = est.get("coef")
    if coef is None:
        return False, f"estimate.coef 缺失（status={est.get('status')}）"
    diff = abs(float(coef) - target)
    return (
        diff <= tolerance,
        f"coef={float(coef):.4f} target={target} |diff|={diff:.4f} <= {tolerance}",
    )


def check_claim_mentions_treatment(state: Dict[str, Any], params: Dict[str, Any]) -> Tuple[bool, str]:
    """主结果表点名处理变量。

    必须出现在真正的结果表上下文里：estimate.treatment_row 非空且含
    处理变量名，且 state.results（结果章可引用的主结果 markdown）含表头
    和该变量。报错文本里恰好包含变量名（如公式回显）不算数。
    """
    est = state.get("estimate") or {}
    treatment = str(params.get("treatment") or est.get("treatment") or "")
    row = str(est.get("treatment_row") or "")
    results = str(state.get("results") or "")
    if not treatment:
        return False, "未指定处理变量"
    ok = bool(row) and treatment in row and treatment in results
    if ok:
        return True, f"结果表 treatment_row 含 '{treatment}'，state.results 为主结果表"
    if est.get("status") != "ok":
        return False, f"estimate status={est.get('status')}，无结果表（'{treatment}' 即便出现在报错文本里也不算）"
    return False, f"结果表 treatment_row={row!r} 未正确点名 '{treatment}'"


def check_no_fabricated_coef_on_failure(state: Dict[str, Any], params: Dict[str, Any]) -> Tuple[bool, str]:
    del params
    est = state.get("estimate")
    if not est:
        return False, "estimate 未写出（节点没跑到或抛异常）"
    status = est.get("status")
    if status == "ok":
        ok = est.get("coef") is not None
        return ok, f"status=ok，coef={'有' if ok else '缺失（异常）'}"
    row = str(est.get("treatment_row") or "")
    ok = row == ""
    return ok, f"status={status}，treatment_row={'空（未编造）' if ok else '非空（编造了系数！）'}"


CHECK_FUNCS: Dict[str, Callable[[Dict[str, Any], Dict[str, Any]], Tuple[bool, str]]] = {
    "pipeline_completed": check_pipeline_completed,
    "identification_passed": check_identification_passed,
    "estimate_stars_gte_2": check_estimate_stars_gte_2,
    "coef_within_tolerance": check_coef_within_tolerance,
    "claim_mentions_treatment": check_claim_mentions_treatment,
    "no_fabricated_coef_on_failure": check_no_fabricated_coef_on_failure,
}


def score(state: Dict[str, Any], rubric: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """逐条跑 rubric check；未知 check 名记 fail，不让坏量规静默通过。"""
    results = []
    for item in rubric:
        cid = item.get("id")
        fn = CHECK_FUNCS.get(item.get("check"))
        if fn is None:
            results.append({
                "id": cid,
                "description": item.get("description"),
                "pass": False,
                "detail": f"未知 check: {item.get('check')}",
            })
            continue
        try:
            ok, detail = fn(state, item.get("params") or {})
        except Exception as exc:  # 单条 check 失败不阻塞其余条目
            ok, detail = False, f"check 执行异常: {type(exc).__name__}: {exc}"
        results.append({
            "id": cid,
            "description": item.get("description"),
            "pass": bool(ok),
            "detail": detail,
        })
    return results


def state_evidence(state: Dict[str, Any]) -> Dict[str, Any]:
    """从 state 抽取关键证据，方便分数卡之外人工复核。"""
    est = state.get("estimate") or {}
    diag = state.get("identification_diag") or {}
    steps = (state.get("cleaning_report") or {}).get("steps") or []
    return {
        "n_cleaning_steps": len(steps),
        "n_cleaning_steps_success": sum(1 for s in steps if s.get("status") == "success"),
        "identification_strategy": diag.get("strategy"),
        "star_rating": state.get("star_rating"),
        "identification_report": diag.get("report"),
        "estimate_status": est.get("status"),
        "estimator": est.get("estimator"),
        "method": est.get("method"),
        "formula": est.get("formula"),
        "coef": est.get("coef"),
        "se": est.get("se"),
        "p": est.get("p"),
        "n": est.get("n"),
        "estimate_error": est.get("error"),
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="headless 跑分器：跑一个 eval 任务并输出 JSON 分数卡")
    parser.add_argument("task_id", nargs="?", default="undergrad_did_01", help="agent/eval/tasks/ 下的任务目录名")
    args = parser.parse_args(argv)

    task_dir, task, rubric = load_task(args.task_id)
    csv_path = task_dir / str(task.get("data_file") or "dataset.csv")
    log(f"task={args.task_id} dir={task_dir}")

    # LLM provider 复核（ECONPAPER_LLM=mock 已在模块顶部、import 前设置）
    try:
        from llm.router import router

        provider = router.get_config("generate").provider
    except Exception as exc:
        provider = f"unknown（router 导入失败: {exc}）"
    log(f"llm_provider={provider}")

    with tempfile.TemporaryDirectory(prefix="econpaper_eval_") as workspace:
        state = build_initial_state(args.task_id, task, csv_path, workspace)
        run_error = None
        nodes_run: List[str] = []
        stop_reasons: List[str] = []
        try:
            state, nodes_run, stop_reasons = run_pipeline(state)
        except Exception as exc:
            run_error = f"{type(exc).__name__}: {exc}"
            log(f"管线异常中断: {run_error}")
        checks = score(state, rubric)

    passed = sum(1 for c in checks if c["pass"])
    total = len(checks)
    card = {
        "task": args.task_id,
        "task_dir": str(task_dir),
        "llm_provider": provider,
        "nodes_run": nodes_run,
        "stop_reasons": stop_reasons,
        "run_error": run_error,
        "checks": checks,
        "summary": {
            "passed": passed,
            "total": total,
            "score": round(passed / total, 4) if total else 0.0,
            "all_pass": passed == total,
        },
        "state_evidence": state_evidence(state),
    }
    print(json.dumps(card, ensure_ascii=False, indent=2))
    return 0 if passed == total and run_error is None else 1


if __name__ == "__main__":
    raise SystemExit(main())
