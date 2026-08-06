"""Evaluator-driven score for Continuous Empirical Loop packages.

Karpathy/OpenEvolve spirit: cannot bluff past numeric gates.
Mutable object: writing expand flags / paper md / latex pipeline params.
Not full OpenEvolve yet — score + archive + keep/rollback hooks.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class PackageScore:
    score: float
    components: dict[str, float] = field(default_factory=dict)
    flags: dict[str, bool] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
    better_than_best: bool = False
    built_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _cn_chars(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def score_package(
    *,
    project_root: Path | None = None,
    slug: str = "parent_education_wage",
    loop_state: dict[str, Any] | None = None,
) -> PackageScore:
    root = project_root or ROOT
    comps: dict[str, float] = {}
    notes: list[str] = []
    flags: dict[str, bool] = {}

    # 1) REPRO
    main = root / "Results" / "json" / f"{slug}_full_pipeline_main_results.json"
    repro_script = root / "replication" / f"reproduce_{slug}_full_pipeline.py"
    repro_report = root / "replication" / f"{slug}_repro_report.md"
    repro = 0.0
    if main.exists() and repro_script.exists():
        repro = 0.5
        if repro_report.exists() and "REPRO_OK" in repro_report.read_text(encoding="utf-8", errors="replace"):
            repro = 1.0
        elif repro_report.exists() and "passed" in repro_report.read_text(encoding="utf-8", errors="replace"):
            repro = 0.85
    comps["repro"] = repro
    flags["repro_ok"] = repro >= 0.85

    # 2) Quality gate (inverse of blocking severity)
    qpath = root / "Results" / "json" / f"{slug}_full_pipeline_quality.json"
    q_score = 0.0
    blocking: list[str] = []
    soft: list[str] = []
    verdict: list[str] = []
    if qpath.exists():
        try:
            q = json.loads(qpath.read_text(encoding="utf-8"))
            verdict = q.get("verdict") or []
            if isinstance(verdict, str):
                verdict = [verdict]
            if not isinstance(verdict, list):
                verdict = list(verdict) if verdict else []
            hard = {
                "too_thin",
                "missing_sections",
                "section_length_gate_required",
                "evidence_integrity_blocked",
                "format_gate_required",
            }
            if verdict == ["ready_for_review"] or verdict == []:
                q_score = 1.0
            else:
                blocking = [v for v in verdict if v in hard]
                soft = [v for v in verdict if v not in hard]
                # start from 0.75 and subtract
                q_score = max(0.0, 0.75 - 0.12 * len(blocking) - 0.04 * len(soft))
                notes.append(f"verdict={verdict}")
        except json.JSONDecodeError:
            notes.append("quality_json_invalid")
    # Integrity floor: hard evidence block caps quality component to 0
    if "evidence_integrity_blocked" in verdict or "evidence_integrity_blocked" in blocking:
        q_score = 0.0
        flags["integrity_floor"] = True
        notes.append("integrity_floor: evidence_integrity_blocked → quality=0")
    comps["quality"] = q_score
    flags["quality_green"] = q_score >= 0.99

    # 3) Paper substance (Chinese length + sections)
    paper = root / "Manuscripts" / "generated" / f"{slug}_full_pipeline_paper.md"
    sub = 0.0
    if paper.exists():
        text = paper.read_text(encoding="utf-8", errors="replace")
        n = _cn_chars(text)
        # 10k+ green band for course paper
        sub = min(1.0, n / 10000.0)
        for h in ("摘要", "引言", "数据", "方法", "结果", "结论"):
            if h not in text:
                sub *= 0.92
                notes.append(f"missing_heading_hint:{h}")
        notes.append(f"cn_chars={n}")
    comps["substance"] = sub

    # 3b) Craft markers from good-paper standard (Black/Bellemare)
    # Paths / (证据：tables/...) in the body are HARD anti-craft — academic prose only.
    craft = 0.0
    if paper.exists():
        text = paper.read_text(encoding="utf-8", errors="replace")
        path_leak = bool(
            re.search(
                r"证据\s*[：:].*(?:tables/|Results/)|tables/|Results/json|\.csv`|\.json`",
                text,
            )
            or ("tables/" in text and "证据" in text)
        )
        if path_leak:
            craft = 0.0
            notes.append("craft_fail:path_leaks_in_manuscript")
        else:
            marks = 0
            if re.search(r"关联|偏相关", text):
                marks += 1
            if re.search(r"不是因果|非因果|不是.*LATE|不允许.*因果|不作因果", text):
                marks += 1
            if re.search(r"表\s*[123]|见表", text):
                marks += 1
            if re.search(r"能力偏误|选择|未观测", text):
                marks += 1
            if re.search(r"HC1|稳健标准误|OLS", text):
                marks += 1
            craft = marks / 5.0
            notes.append(f"craft_markers={marks}/5")
    comps["craft"] = craft

    # 4) LaTeX PDF
    pdf = root / "Submissions" / f"{slug}_loop_paper.pdf"
    tex = list((root / "Submissions" / "latex_build" / slug).glob("*.tex"))
    latex = 0.0
    if pdf.exists() and pdf.stat().st_size > 5000:
        latex = 1.0
    elif tex:
        latex = 0.4
        notes.append("tex_without_pdf")
    comps["latex_pdf"] = latex
    flags["pdf_ok"] = latex >= 1.0

    # 5) Honesty / causal claim discipline
    honesty = 0.7
    if main.exists():
        try:
            m = json.loads(main.read_text(encoding="utf-8"))
            if m.get("causal_claim_allowed") is False:
                honesty = 1.0
            if paper.exists():
                t = paper.read_text(encoding="utf-8", errors="replace")
                if re.search(r"因果效应|政策效应|LATE", t) and "不是" not in t[:2000]:
                    # weak heuristic
                    if "不是因果" not in t and "非因果" not in t and "不是" not in t:
                        honesty = min(honesty, 0.4)
                        notes.append("possible_overclaim")
        except json.JSONDecodeError:
            pass
    comps["honesty"] = honesty

    # 6) Loop status bonus
    loop_bonus = 0.0
    if loop_state:
        st = loop_state.get("status")
        if st == "completed_green":
            loop_bonus = 1.0
        elif st == "halted_honest":
            loop_bonus = 0.55
        elif st == "max_rounds":
            loop_bonus = 0.35
        elif st == "failed":
            loop_bonus = 0.0
        else:
            loop_bonus = 0.2
    comps["loop_status"] = loop_bonus

    # Weighted total 0-100
    weights = {
        "repro": 25,
        "quality": 25,
        "substance": 10,
        "craft": 5,
        "latex_pdf": 20,
        "honesty": 10,
        "loop_status": 5,
    }
    total = sum(comps.get(k, 0.0) * w for k, w in weights.items())

    # Integrity floor: evidence_integrity_blocked hard → total score forced 0
    # (anti-Goodhart: cannot trade "looks like paper" for dirty evidence)
    if flags.get("integrity_floor") or "evidence_integrity_blocked" in verdict:
        total = 0.0
        flags["integrity_floor"] = True
        if "integrity_floor: total=0" not in notes:
            notes.append("integrity_floor: total=0")

    return PackageScore(
        score=round(total, 2),
        components={k: round(v, 4) for k, v in comps.items()},
        flags=flags,
        notes=notes,
        built_at=_now(),
    )


def load_best(archive_path: Path) -> dict[str, Any] | None:
    if not archive_path.exists():
        return None
    try:
        return json.loads(archive_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def maybe_update_best(
    score: PackageScore,
    archive_dir: Path,
    *,
    project_root: Path | None = None,
    slug: str = "parent_education_wage",
) -> PackageScore:
    """Append every attempt to history.jsonl; promote best.json only on strict score ↑.

    When promoted, also copy live paper bytes to archive_dir/best_paper.md so
    Continuous Loop can restore a previous best after a regressing rewrite
    (Penguin Selection/Rollback: rejected candidates never stay as Reference).
    """
    archive_dir.mkdir(parents=True, exist_ok=True)
    root = project_root or ROOT
    best_path = archive_dir / "best.json"
    history = archive_dir / "history.jsonl"
    best = load_best(best_path)
    better = best is None or float(score.score) > float(best.get("score", -1))
    score.better_than_best = better
    payload = score.to_dict()
    # history.jsonl = all attempts (accepted + rejected)
    with history.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
    if better:
        best_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        paper_rel = f"Manuscripts/generated/{slug}_full_pipeline_paper.md"
        pdf_rel = f"Submissions/{slug}_loop_paper.pdf"
        snap = {
            "score": score.score,
            "paper": paper_rel,
            "pdf": pdf_rel,
            "best_paper_copy": "best_paper.md",
            "saved_at": _now(),
        }
        (archive_dir / "best_pointers.json").write_text(
            json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        # Content snapshot for cross-loop rollback (pointer alone is live path)
        paper_path = root / paper_rel
        if paper_path.exists():
            (archive_dir / "best_paper.md").write_text(
                paper_path.read_text(encoding="utf-8", errors="replace"),
                encoding="utf-8",
            )
    return score
