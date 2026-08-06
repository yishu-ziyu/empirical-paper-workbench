"""Continuous Empirical Loop — SSOT outer loop (propose→run→evaluate→learn↻→package).

Book-grade structure:
  Agent delivery path = this loop (not linear full_pipeline alone).
  L8: quality/citation red → machine next_action + target_steps re-entry + max_rounds fuse.
  Never report completed_green while blocking quality reds remain.

Pi Agent: optional revise assist each learn round via run_pi_task.
"""

from __future__ import annotations

import json
import shutil
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime.full_pipeline import FullPaperPipeline, ROOT, _now, _write_json, _write_text

# Verdicts that block completed_green (must learn or honest-halt).
BLOCKING_VERDICTS = frozenset(
    {
        "too_thin",
        "missing_sections",
        "section_length_gate_required",
        "evidence_integrity_blocked",
        "format_gate_required",
    }
)
# Soft reds: degrade claims / package with limits, not automatic infinite expand.
SOFT_VERDICTS = frozenset(
    {
        "needs_literature_review",
        "method_gate_required",
        "needs_review_loop",
        "evidence_integrity_needs_review",
    }
)
REWRITE_TAIL = [
    "06_writing",
    "07_revision",
    "08_format_citation",
    "09_replication",
    "10_defense",
]


@dataclass
class LearnPlan:
    codes: list[str]
    next_action: str  # rewrite_expand | degrade_and_rewrite | halt_honest | package_green
    target_steps: list[str] = field(default_factory=list)
    expand_mode: bool = False
    degrade_mode: bool = False
    notes: str = ""
    severity: str = "info"  # info | warn | hard


@dataclass
class LoopRound:
    round: int
    pipeline_run_id: str
    pipeline_status: str
    verdict: list[str] = field(default_factory=list)
    learn: dict[str, Any] = field(default_factory=dict)
    pi_assist: dict[str, Any] | None = None
    elapsed_sec: float = 0.0


@dataclass
class LoopResult:
    loop_id: str
    status: str  # completed_green | halted_honest | failed | max_rounds
    rounds: list[LoopRound] = field(default_factory=list)
    final_verdict: list[str] = field(default_factory=list)
    package: dict[str, str] = field(default_factory=dict)
    started_at: str = ""
    finished_at: str = ""
    reason: str = ""

    def save(self, path: Path) -> None:
        _write_json(
            path,
            {
                "loop_id": self.loop_id,
                "status": self.status,
                "started_at": self.started_at,
                "finished_at": self.finished_at,
                "reason": self.reason,
                "final_verdict": self.final_verdict,
                "package": self.package,
                "rounds": [asdict(r) for r in self.rounds],
            },
        )


def _normalize_verdict(verdict: Any) -> list[str]:
    if verdict is None:
        return []
    if isinstance(verdict, str):
        return [verdict] if verdict else []
    if isinstance(verdict, (list, tuple, set)):
        return [str(v) for v in verdict if v]
    return [str(verdict)]


def has_blocking_quality(verdict: Any = None, *, evaluation: dict[str, Any] | None = None) -> bool:
    """True if any BLOCKING_VERDICTS red is present — forbids completed_green."""
    if evaluation is not None:
        blocking = evaluation.get("blocking") or []
        if blocking:
            return True
        verdict = evaluation.get("verdict") if verdict is None else verdict
    codes = set(_normalize_verdict(verdict))
    return bool(codes & BLOCKING_VERDICTS)


def evaluate_after_pipeline(pipe: FullPaperPipeline) -> dict[str, Any]:
    """Model-out evaluate: structured quality + citation + REPRO markers."""
    quality = pipe.record.quality or {}
    verdict = _normalize_verdict(quality.get("verdict") or [])
    citation_path = ROOT / "Results" / "json" / f"{pipe.SLUG}_full_pipeline_citation_gate.json"
    citation = {}
    if citation_path.exists():
        citation = json.loads(citation_path.read_text(encoding="utf-8"))
    repro_ok = any(
        s.step_id == "09_replication" and s.status == "passed" for s in pipe.record.steps
    )
    if pipe.record.status == "failed":
        failed_steps = [s.step_id for s in pipe.record.steps if s.status == "failed"]
        return {
            "pipeline_status": "failed",
            "verdict": verdict,
            "blocking": sorted(BLOCKING_VERDICTS.intersection(verdict)),
            "soft": sorted(SOFT_VERDICTS.intersection(verdict)),
            "citation_status": citation.get("status"),
            "repro_ok": False,
            "failed_steps": failed_steps,
            "is_green": False,
        }
    blocking = sorted(BLOCKING_VERDICTS.intersection(verdict))
    soft = sorted(SOFT_VERDICTS.intersection(verdict))
    # Strict course-green: only ready_for_review (no soft reds, no blocking)
    # Hard invariant: any blocking → is_green=False (never completed_green)
    strict_green = (
        pipe.record.status == "completed"
        and repro_ok
        and not blocking
        and (verdict == ["ready_for_review"] or verdict == [])
    )
    return {
        "pipeline_status": pipe.record.status,
        "verdict": verdict,
        "blocking": blocking,
        "soft": soft,
        "citation_status": citation.get("status"),
        "repro_ok": repro_ok,
        "failed_steps": [],
        "is_green": strict_green,
        "is_soft_only": bool(soft) and not blocking and repro_ok and pipe.record.status == "completed",
        "recommended_next_tasks": quality.get("recommended_next_tasks") or [],
        "quality_path": quality.get("path"),
    }


def build_learn_plan(evaluation: dict[str, Any], *, round_i: int, max_rounds: int) -> LearnPlan:
    """Map evaluate → next_action + target_steps (L8 spine)."""
    if evaluation.get("pipeline_status") == "failed":
        failed = evaluation.get("failed_steps") or []
        # Hard fail on data/estimate/repro → halt unless only writing failed
        if any(s in failed for s in ("04_data_gate", "05_causal_analysis", "09_replication")):
            return LearnPlan(
                codes=failed,
                next_action="halt_honest",
                severity="hard",
                notes=f"hard step failed: {failed}",
            )
        return LearnPlan(
            codes=failed,
            next_action="rewrite_expand",
            target_steps=REWRITE_TAIL,
            expand_mode=True,
            degrade_mode=True,
            severity="hard",
            notes=f"retry tail after step fail: {failed}",
        )

    if evaluation.get("is_green"):
        return LearnPlan(codes=["ready_for_review"], next_action="package_green", severity="info")

    blocking = evaluation.get("blocking") or []
    soft = evaluation.get("soft") or []
    codes = list(blocking) + list(soft)

    if round_i >= max_rounds:
        return LearnPlan(
            codes=codes,
            next_action="halt_honest",
            severity="hard",
            notes="max_rounds reached with residual reds",
        )

    expand = any(c in blocking for c in ("too_thin", "section_length_gate_required", "missing_sections", "format_gate_required"))
    degrade = any(
        c in codes
        for c in (
            "evidence_integrity_blocked",
            "needs_literature_review",
            "method_gate_required",
            "evidence_integrity_needs_review",
        )
    )
    if blocking:
        return LearnPlan(
            codes=codes,
            next_action="degrade_and_rewrite" if degrade else "rewrite_expand",
            target_steps=list(REWRITE_TAIL),
            expand_mode=expand or True,
            degrade_mode=degrade or True,
            severity="hard",
            notes=(
                f"blocking={blocking}; soft={soft}; "
                f"tasks={evaluation.get('recommended_next_tasks')}"
            ),
        )

    # Soft only: one degrade rewrite then allow halted_honest package if still soft
    if soft:
        return LearnPlan(
            codes=codes,
            next_action="degrade_and_rewrite",
            target_steps=list(REWRITE_TAIL),
            expand_mode=True,
            degrade_mode=True,
            severity="warn",
            notes=f"soft reds only: {soft}",
        )

    return LearnPlan(
        codes=codes or ["unknown_red"],
        next_action="halt_honest",
        severity="warn",
        notes="unclassified evaluation",
    )


class ContinuousEmpiricalLoop:
    """Outer loop SSOT: full_pipeline rounds + evaluate + learn re-entry + optional Pi assist."""

    def __init__(
        self,
        *,
        max_rounds: int = 3,
        use_llm: bool = True,
        provider_id: str = "grok",
        model: str | None = "grok-4.5",
        use_pi_assist: bool = False,
        pi_provider: str = "minimax-cn",
        pi_model: str = "MiniMax-M3",
        pi_timeout_sec: float = 300.0,
    ) -> None:
        self.max_rounds = max(1, max_rounds)
        self.use_llm = use_llm
        self.provider_id = provider_id
        self.model = model
        self.use_pi_assist = use_pi_assist
        self.pi_provider = pi_provider
        self.pi_model = pi_model
        self.pi_timeout_sec = pi_timeout_sec
        stamp = time.strftime("%Y%m%d_%H%M%S")
        self.loop_id = f"continuous_loop_{FullPaperPipeline.SLUG}_{stamp}"
        self.loop_dir = ROOT / "state" / "runs" / self.loop_id
        self.loop_dir.mkdir(parents=True, exist_ok=True)
        self.result = LoopResult(loop_id=self.loop_id, status="running", started_at=_now())
        # Penguin-style mutable snapshot / rollback state (paper.md only)
        self._last_pre_edit_snapshot: Path | None = None
        self._accepted_snapshot: Path | None = None
        self._accepted_score: float | None = None
        self._last_rollback: dict[str, Any] | None = None

    def _paper_path(self) -> Path:
        return ROOT / "Manuscripts" / "generated" / f"{FullPaperPipeline.SLUG}_full_pipeline_paper.md"

    def _snapshot_dir(self) -> Path:
        d = self.loop_dir / "mutable_snapshot"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _snapshot_paper_before_rewrite(self, round_i: int) -> Path | None:
        """Before expand/degrade rewrite: copy live paper → mutable_snapshot/round_N_paper.md.

        Penguin in-round fast path: retain exact original-file record before Candidate edit.
        """
        paper = self._paper_path()
        if not paper.exists():
            return None
        dest = self._snapshot_dir() / f"round_{round_i}_paper.md"
        shutil.copy2(paper, dest)
        self._last_pre_edit_snapshot = dest
        meta = {
            "round": round_i,
            "source": str(paper.relative_to(ROOT)),
            "snapshot": str(dest.relative_to(ROOT)),
            "bytes": dest.stat().st_size,
            "saved_at": _now(),
            "purpose": "pre_expand_degrade_reference",
        }
        _write_json(self._snapshot_dir() / f"round_{round_i}_meta.json", meta)
        print(f"   📸 snapshot pre-rewrite → {dest.relative_to(ROOT)}")
        return dest

    def _save_accepted_paper(self, score: float, *, round_i: int | None = None) -> Path | None:
        """Persist accepted Reference paper bytes under loop mutable_snapshot/."""
        paper = self._paper_path()
        if not paper.exists():
            return None
        dest = self._snapshot_dir() / "accepted_paper.md"
        shutil.copy2(paper, dest)
        self._accepted_snapshot = dest
        self._accepted_score = float(score)
        meta = {
            "score": float(score),
            "round": round_i,
            "snapshot": str(dest.relative_to(ROOT)),
            "source": str(paper.relative_to(ROOT)),
            "saved_at": _now(),
        }
        _write_json(self._snapshot_dir() / "accepted_meta.json", meta)
        return dest

    def _resolve_restore_source(self) -> tuple[Path | None, str]:
        """Pick restore file: last accepted loop snapshot → pre-edit → archive best_paper.md."""
        if self._accepted_snapshot is not None and self._accepted_snapshot.exists():
            return self._accepted_snapshot, "loop_accepted_snapshot"
        accepted = self._snapshot_dir() / "accepted_paper.md"
        if accepted.exists():
            return accepted, "loop_accepted_snapshot"
        if self._last_pre_edit_snapshot is not None and self._last_pre_edit_snapshot.exists():
            return self._last_pre_edit_snapshot, "last_pre_edit_snapshot"
        # Fall back to cross-loop archive content copy (not the live pointer path)
        archive_best = ROOT / "state" / "evolve_archive" / "best_paper.md"
        if archive_best.exists():
            return archive_best, "evolve_archive_best_paper"
        # Last resort: best_pointers live path only if it still exists (may be overwritten)
        pointers = ROOT / "state" / "evolve_archive" / "best_pointers.json"
        if pointers.exists():
            try:
                p = json.loads(pointers.read_text(encoding="utf-8"))
                rel = p.get("paper") or ""
                if rel:
                    cand = ROOT / rel
                    if cand.exists() and cand.resolve() != self._paper_path().resolve():
                        return cand, "best_pointers_paper"
            except (json.JSONDecodeError, OSError):
                pass
        return None, "none"

    def _maybe_rollback_paper(
        self,
        score_payload: dict[str, Any],
        *,
        round_i: int | None = None,
    ) -> dict[str, Any] | None:
        """If not better_than_best and score dropped vs accepted/best → restore paper.

        Does not touch quality gates / integrity_floor / red-not-green status decisions.
        history.jsonl already recorded the attempt; best.json is not updated on reject.
        """
        if score_payload.get("error") and score_payload.get("score") is None:
            return None
        better = bool(score_payload.get("better_than_best"))
        try:
            cand_score = float(score_payload["score"]) if score_payload.get("score") is not None else None
        except (TypeError, ValueError):
            cand_score = None
        if cand_score is None:
            return None

        # Accept path: promote Reference paper snapshot
        if better:
            self._save_accepted_paper(cand_score, round_i=round_i)
            return None

        # Reference score: loop-accepted, else archive best.json
        ref_score = self._accepted_score
        if ref_score is None:
            best_path = ROOT / "state" / "evolve_archive" / "best.json"
            if best_path.exists():
                try:
                    ref_score = float(json.loads(best_path.read_text(encoding="utf-8")).get("score", -1))
                except (json.JSONDecodeError, TypeError, ValueError):
                    ref_score = None

        # Only restore when score actually dropped (ties keep candidate; strict Penguin is
        # "not strictly higher" for scoreboard, but file restore is reserved for regressions)
        if ref_score is None or cand_score >= float(ref_score):
            return None

        src, src_kind = self._resolve_restore_source()
        paper = self._paper_path()
        if src is None or not src.exists():
            record = {
                "rolled_back": False,
                "reason": "score_dropped_but_no_restore_source",
                "candidate_score": cand_score,
                "reference_score": ref_score,
                "better_than_best": better,
                "round": round_i,
                "at": _now(),
            }
            _write_json(self.loop_dir / "rollback.json", record)
            self._last_rollback = record
            return record

        # Capture rejected candidate before overwrite (audit)
        rejected_path = self._snapshot_dir() / (
            f"rejected_round_{round_i}_paper.md" if round_i is not None else "rejected_paper.md"
        )
        if paper.exists():
            shutil.copy2(paper, rejected_path)

        shutil.copy2(src, paper)
        try:
            restored_from = str(src.resolve().relative_to(ROOT.resolve()))
        except Exception:
            restored_from = str(src)
        try:
            rejected_rel = str(rejected_path.resolve().relative_to(ROOT.resolve()))
        except Exception:
            rejected_rel = str(rejected_path)
        try:
            paper_rel = str(paper.resolve().relative_to(ROOT.resolve()))
        except Exception:
            paper_rel = str(paper)
        record = {
            "rolled_back": True,
            "reason": "score_not_better_than_best_and_dropped",
            "candidate_score": cand_score,
            "reference_score": float(ref_score),
            "better_than_best": better,
            "restored_from": restored_from,
            "restore_kind": src_kind,
            "rejected_copy": rejected_rel,
            "paper_path": paper_rel,
            "round": round_i,
            "at": _now(),
        }
        _write_json(self.loop_dir / "rollback.json", record)
        self._last_rollback = record
        print(
            f"   ⏪ rollback paper score {cand_score} < ref {ref_score} "
            f"← {src_kind}"
        )
        return record

    def _pi_assist(self, plan: LearnPlan, evaluation: dict[str, Any]) -> dict[str, Any] | None:
        if not self.use_pi_assist:
            return None
        try:
            from Product.backend.pi_runtime.rpc_client import run_pi_task
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": f"pi_import_failed: {exc}"}
        paper = ROOT / "Manuscripts" / "generated" / f"{FullPaperPipeline.SLUG}_full_pipeline_paper.md"
        msg = f"""你是 Continuous Empirical Loop 的 revise 助手（Pi harness）。

任务：根据质量红灯扩写/降级改写论文草稿，禁止编造系数与假文献。

learn_plan:
{json.dumps(asdict(plan), ensure_ascii=False, indent=2)}

evaluation:
{json.dumps(evaluation, ensure_ascii=False, indent=2)}

请：
1. 读取 `{paper.relative_to(ROOT) if paper.exists() else 'Manuscripts/generated/..._paper.md'}`
2. 按 expand/degrade 要求改写，主文中文尽量加厚且每条数字保留证据路径
3. 写回同一 paper 路径
4. 简短说明改了什么
"""
        try:
            r = run_pi_task(
                ROOT,
                msg,
                provider=self.pi_provider,
                model=self.pi_model,
                no_session=False,
                verbose=True,
                timeout_sec=self.pi_timeout_sec,
            )
            return {
                "ok": r.success,
                "answer_preview": (r.answer or "")[:1500],
                "error": r.error,
                "trajectory": r.trajectory_path,
                "elapsed_sec": r.elapsed_sec,
            }
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc)}

    def _score_and_archive(
        self,
        status: str,
        evaluation: dict[str, Any],
        *,
        round_i: int | None = None,
    ) -> dict[str, Any]:
        """Programmatic package score after package; write into evolve archive.

        history.jsonl always appends the attempt. best.json only improves.
        If score is not better_than_best and dropped vs Reference → restore paper
        and write loop_dir/rollback.json (Penguin Selection/Rollback).
        """
        try:
            from runtime.evolve_evaluator import maybe_update_best, score_package

            loop_state = {
                "status": status,
                "loop_id": self.loop_id,
                "final_verdict": evaluation.get("verdict") or self.result.final_verdict,
                "blocking": evaluation.get("blocking") or [],
            }
            sc = score_package(
                project_root=ROOT,
                slug=FullPaperPipeline.SLUG,
                loop_state=loop_state,
            )
            archive = ROOT / "state" / "evolve_archive"
            sc = maybe_update_best(
                sc,
                archive,
                project_root=ROOT,
                slug=FullPaperPipeline.SLUG,
            )
            payload = sc.to_dict()
            # Penguin rollback: reject candidate file state when fitness regressed
            rb = self._maybe_rollback_paper(payload, round_i=round_i)
            if rb is not None:
                payload["rollback"] = rb
            _write_json(self.loop_dir / "package_score.json", payload)
            return payload
        except Exception as exc:  # noqa: BLE001
            err = {"score": None, "error": str(exc), "built_at": _now()}
            _write_json(self.loop_dir / "package_score.json", err)
            return err

    def _package(self, pipe: FullPaperPipeline, evaluation: dict[str, Any], status: str) -> dict[str, str]:
        # Harden: never emit completed_green when blocking quality remains
        if status == "completed_green" and has_blocking_quality(evaluation=evaluation):
            status = "halted_honest"
            self.result.status = "halted_honest"
            if "blocked:" not in (self.result.reason or ""):
                self.result.reason = (
                    f"blocked: refused completed_green with blocking="
                    f"{evaluation.get('blocking')}"
                )

        paper = pipe.ctx.get("paper_path") or str(
            ROOT / "Manuscripts" / "generated" / f"{pipe.SLUG}_full_pipeline_paper.md"
        )
        paper_path = Path(paper) if Path(paper).is_absolute() else ROOT / paper
        # Fallback: canonical generated paper if ctx path is stale/missing
        if not paper_path.exists():
            alt = ROOT / "Manuscripts" / "generated" / f"{pipe.SLUG}_full_pipeline_paper.md"
            if alt.exists():
                paper_path = alt
        try:
            paper_rel = str(paper_path.resolve().relative_to(ROOT.resolve()))
        except Exception:
            paper_rel = str(paper_path) if not Path(paper).is_absolute() else paper

        # LaTeX → beautiful PDF (xelatex/ctexart). Always attempt from paper path.
        # Isolate build dir under loop_dir so concurrent outer-loop runs cannot race
        # on Submissions/latex_build/{slug}/.
        latex_meta: dict[str, Any] = {}
        try:
            from runtime.latex_pdf import render_markdown_paper_to_pdf

            lr = render_markdown_paper_to_pdf(
                paper_path,
                out_dir=self.loop_dir / "latex_build",
                slug=pipe.SLUG,
                title=pipe.TOPIC,
                project_root=ROOT,
            )
            latex_meta = lr.to_dict()
        except Exception as exc:  # noqa: BLE001
            latex_meta = {
                "ok": False,
                "errors": [f"package_latex_exception:{exc}"],
                "pdf_path": "",
                "tex_path": "",
                "used_last_good": False,
            }
            # Keep last good deliver PDF if present
            deliver = ROOT / "Submissions" / f"{pipe.SLUG}_loop_paper.pdf"
            if deliver.exists() and deliver.stat().st_size > 1000:
                try:
                    latex_meta["pdf_path"] = str(deliver.resolve().relative_to(ROOT.resolve()))
                except Exception:
                    latex_meta["pdf_path"] = str(deliver.relative_to(ROOT))
                latex_meta["used_last_good"] = True
                latex_meta["errors"].append("using_last_good_pdf")

        # Persist latex result + error log; never kill package on log IO failure
        try:
            _write_json(self.loop_dir / "latex_pdf_result.json", latex_meta)
            if not latex_meta.get("ok"):
                err_lines = [str(x) for x in (latex_meta.get("errors") or [])]
                body = "\n".join(err_lines) if err_lines else "latex_failed_no_details"
                if latex_meta.get("log_path"):
                    body += f"\n\nsee_also_log: {latex_meta.get('log_path')}"
                if latex_meta.get("used_last_good") or "using_last_good_pdf" in err_lines:
                    body += f"\nusing_last_good_pdf: {latex_meta.get('pdf_path') or ''}"
                _write_text(self.loop_dir / "latex_pdf_errors.log", body + "\n")
        except Exception as log_exc:  # noqa: BLE001
            try:
                _write_text(
                    self.loop_dir / "latex_pdf_errors.log",
                    f"latex_meta_write_failed: {log_exc}\nmeta={latex_meta!r}\n",
                )
            except Exception:
                pass

        # Normalize package pdf to project-relative path when present
        pdf_rel = str(latex_meta.get("pdf_path") or "")
        if pdf_rel:
            p = Path(pdf_rel)
            if p.is_absolute():
                try:
                    pdf_rel = str(p.resolve().relative_to(ROOT.resolve()))
                except Exception:
                    pass
        if not pdf_rel:
            deliver = ROOT / "Submissions" / f"{pipe.SLUG}_loop_paper.pdf"
            if deliver.exists() and deliver.stat().st_size > 1000:
                try:
                    pdf_rel = str(deliver.resolve().relative_to(ROOT.resolve()))
                except Exception:
                    pdf_rel = f"Submissions/{pipe.SLUG}_loop_paper.pdf"
                latex_meta["used_last_good"] = True

        latex_note = ""
        if latex_meta.get("used_last_good") or "using_last_good_pdf" in (
            latex_meta.get("errors") or []
        ):
            latex_note = "using_last_good_pdf"

        # Evolve score after package artifacts are in place (pdf path may exist)
        last_round = self.result.rounds[-1].round if self.result.rounds else None
        score_payload = self._score_and_archive(status, evaluation, round_i=last_round)
        score_val = score_payload.get("score")
        score_str = "" if score_val is None else str(score_val)
        # If rollback restored paper, refresh package paper path (same path, new bytes)
        if score_payload.get("rollback", {}).get("rolled_back") and paper_path.exists():
            try:
                paper_rel = str(paper_path.resolve().relative_to(ROOT.resolve()))
            except Exception:
                paper_rel = str(paper_path)

        package = {
            "paper": paper_rel,
            "quality": evaluation.get("quality_path") or f"Results/json/{pipe.SLUG}_full_pipeline_quality.json",
            "main_results": f"Results/json/{pipe.SLUG}_full_pipeline_main_results.json",
            "replication": f"replication/reproduce_{pipe.SLUG}_full_pipeline.py",
            "loop_state": str((self.loop_dir / "loop_state.json").relative_to(ROOT)),
            "status": status,
            "pdf": pdf_rel,
            "tex": latex_meta.get("tex_path") or "",
            "latex_ok": str(bool(latex_meta.get("ok"))),
            "latex_note": latex_note,
            "score": score_str,
            "score_path": str((self.loop_dir / "package_score.json").relative_to(ROOT)),
            "rollback": str((self.loop_dir / "rollback.json").relative_to(ROOT))
            if (self.loop_dir / "rollback.json").exists()
            else "",
        }
        # Latest pointer + package_manifest with score
        latest = {
            "loop_id": self.loop_id,
            "status": status,
            "final_verdict": evaluation.get("verdict"),
            "blocking": evaluation.get("blocking") or [],
            "package": package,
            "score": score_payload,
            "updated_at": _now(),
        }
        _write_json(ROOT / "Results" / "json" / f"{pipe.SLUG}_continuous_loop_latest.json", latest)
        manifest = self.loop_dir / "package_manifest.json"
        _write_json(manifest, latest)
        package["manifest"] = str(manifest.relative_to(ROOT))
        summary = self.loop_dir / "LOOP_SUMMARY.md"
        _write_text(
            summary,
            f"""# Continuous Empirical Loop · {self.loop_id}

- status: **{status}**
- rounds: {len(self.result.rounds)}
- final_verdict: `{evaluation.get('verdict')}`
- score: `{score_val}`
- reason: {self.result.reason}

## Package

- paper: `{package['paper']}`
- pdf: `{package.get('pdf')}` latex_ok=`{package.get('latex_ok')}` note=`{package.get('latex_note')}`
- tex: `{package.get('tex')}`
- quality: `{package['quality']}`
- main_results: `{package['main_results']}`
- replication: `{package['replication']}`
- score: `{score_val}` components: `{score_payload.get('components')}`

## Rounds

"""
            + "\n".join(
                f"- r{r.round}: pipeline={r.pipeline_run_id} status={r.pipeline_status} "
                f"verdict={r.verdict} action={r.learn.get('next_action')}"
                for r in self.result.rounds
            ),
        )
        package["summary"] = str(summary.relative_to(ROOT))
        return package

    def run(self) -> LoopResult:
        print(f"\n🔁 Continuous Empirical Loop  loop_id={self.loop_id}")
        print(f"   max_rounds={self.max_rounds} llm={self.use_llm} pi_assist={self.use_pi_assist}")

        only_steps: list[str] | None = None
        expand = False
        degrade = False
        learn_notes = ""
        last_eval: dict[str, Any] = {}
        last_pipe: FullPaperPipeline | None = None

        for round_i in range(1, self.max_rounds + 1):
            t0 = time.time()
            run_id = f"{self.loop_id}_r{round_i}"
            # Penguin: snapshot mutable paper BEFORE expand/degrade Candidate rewrite
            if expand or degrade:
                self._snapshot_paper_before_rewrite(round_i)
            pipe = FullPaperPipeline(
                use_llm=self.use_llm,
                provider_id=self.provider_id,
                model=self.model,
                run_id=run_id,
                expand_mode=expand,
                degrade_mode=degrade,
                learn_notes=learn_notes,
            )
            print(f"\n—— Loop round {round_i}/{self.max_rounds} ——")
            record = pipe.run(only_steps=only_steps)
            evaluation = evaluate_after_pipeline(pipe)
            last_eval = evaluation
            last_pipe = pipe
            plan = build_learn_plan(evaluation, round_i=round_i, max_rounds=self.max_rounds)

            # Persist evaluate + learn for this round
            _write_json(
                self.loop_dir / f"round_{round_i}_evaluate.json",
                evaluation,
            )
            _write_json(
                self.loop_dir / f"round_{round_i}_learn.json",
                asdict(plan),
            )

            pi_info = None
            if plan.next_action in ("rewrite_expand", "degrade_and_rewrite") and round_i < self.max_rounds:
                pi_info = self._pi_assist(plan, evaluation)

            self.result.rounds.append(
                LoopRound(
                    round=round_i,
                    pipeline_run_id=record.run_id,
                    pipeline_status=record.status,
                    verdict=list(evaluation.get("verdict") or []),
                    learn=asdict(plan),
                    pi_assist=pi_info,
                    elapsed_sec=round(time.time() - t0, 3),
                )
            )
            self.result.final_verdict = list(evaluation.get("verdict") or [])
            self.result.save(self.loop_dir / "loop_state.json")

            if plan.next_action == "package_green":
                # Harden at decision point: blocking quality can never complete green
                if has_blocking_quality(evaluation=evaluation) or not evaluation.get("is_green"):
                    self.result.status = "halted_honest"
                    self.result.reason = (
                        f"blocked: package_green refused "
                        f"(blocking={evaluation.get('blocking')}, "
                        f"verdict={evaluation.get('verdict')})"
                    )
                    self.result.package = self._package(pipe, evaluation, self.result.status)
                    break
                self.result.status = "completed_green"
                self.result.reason = "quality ready_for_review + REPRO_OK"
                self.result.package = self._package(pipe, evaluation, self.result.status)
                break

            if plan.next_action == "halt_honest":
                # Soft-only residual after at least one degrade pass → still honest halt
                self.result.status = "halted_honest"
                self.result.reason = plan.notes or "honest halt"
                self.result.package = self._package(pipe, evaluation, self.result.status)
                break

            # L8 re-entry: set flags for next round
            only_steps = plan.target_steps or list(REWRITE_TAIL)
            expand = plan.expand_mode
            degrade = plan.degrade_mode
            learn_notes = plan.notes
            print(f"   L8 → {plan.next_action} target={only_steps} expand={expand} degrade={degrade}")
        else:
            # for-else: exhausted rounds without break
            self.result.status = "max_rounds"
            self.result.reason = f"exhausted max_rounds={self.max_rounds}"
            if last_pipe is not None:
                self.result.package = self._package(last_pipe, last_eval, self.result.status)

        # Safety net: never alias red completed as green (re-package if demoted)
        if self.result.status == "completed_green":
            blocked = has_blocking_quality(
                self.result.final_verdict,
                evaluation=last_eval or None,
            )
            if blocked or (last_eval and not last_eval.get("is_green", True) and last_eval.get("blocking")):
                self.result.status = "halted_honest"
                self.result.reason = (
                    f"blocked: green claimed with blocking verdicts "
                    f"{last_eval.get('blocking') if last_eval else self.result.final_verdict}"
                )
                if last_pipe is not None:
                    self.result.package = self._package(
                        last_pipe, last_eval or {}, self.result.status
                    )
                elif self.result.package:
                    self.result.package["status"] = "halted_honest"

        self.result.finished_at = _now()
        self.result.save(self.loop_dir / "loop_state.json")
        # Append trajectory line
        jsonl = ROOT / "artifacts" / "agent_trace_log.jsonl"
        jsonl.parent.mkdir(parents=True, exist_ok=True)
        with jsonl.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "ts": time.time(),
                        "runtime": "continuous_loop",
                        "loop_id": self.loop_id,
                        "status": self.result.status,
                        "rounds": len(self.result.rounds),
                        "final_verdict": self.result.final_verdict,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
        print(f"\n======== CONTINUOUS LOOP RESULT ========")
        print(f"status: {self.result.status}")
        print(f"loop_id: {self.loop_id}")
        print(f"rounds: {len(self.result.rounds)}")
        print(f"final_verdict: {self.result.final_verdict}")
        print(f"package: {self.result.package}")
        return self.result


def run_continuous_loop(**kwargs: Any) -> LoopResult:
    return ContinuousEmpiricalLoop(**kwargs).run()
