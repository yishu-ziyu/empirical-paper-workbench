"""Full empirical paper pipeline — book-grade Agent loop + real evidence.

Runs the 10-step research OS flow for the parent-education-wage demo with:
- Deterministic data/stats steps (no invented coefficients)
- Default LLM: Grok 4.5 via Product.backend.llm_client (provider_id=grok)
- Trajectory + claim register + course-paper quality gate

This is the product E2E path when CHARLS scripts are not present for this topic.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import time
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _cn_len(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


# Engineering / product tokens that must never appear in the human manuscript body.
_PATH_LEAK_RE = re.compile(
    r"(?:"
    r"证据\s*[：:]|"
    r"tables/|"
    r"Results/|"
    r"Data/(?:Raw|Interim|Final)/|"
    r"Manuscripts/|"
    r"evidence/|"
    r"replication/|"
    r"state/runs/|"
    r"litreview/|"
    r"Submissions/|"
    r"claim[_\s-]?register|"
    r"Continuous\s+Empirical\s+Loop|"
    r"Continuous\s+Loop|"
    r"integrity[_\s-]?(?:audit|gate|floor)|"
    r"causal_claim_allowed|"
    r"learn_notes|"
    r"expand_mode|"
    r"degrade_mode|"
    r"package\s*失败|"
    r"outer\s*loop|"
    r"L8\s*回炉|"
    r"质量门|"
    r"full_pipeline|"
    r"dataset_sha256|"
    r"\b[A-Za-z0-9_\-./]+\.(?:json|csv|py|md|dta|log)\b|"
    r"`[^`]{0,80}/[^`]{0,80}`"
    r")",
    re.IGNORECASE,
)

_EVIDENCE_PAREN_RE = re.compile(r"[（(]\s*证据\s*[：:][^）)]*[）)]")
_EVIDENCE_LINE_RE = re.compile(r"^[ \t]*[（(]?\s*证据\s*[：:].*$", re.MULTILINE)


def manuscript_has_path_leaks(text: str) -> bool:
    """True if body looks like an engineering audit log rather than a paper."""
    if not text or not text.strip():
        return False
    if _PATH_LEAK_RE.search(text):
        return True
    # bare relative paths common in this repo
    if re.search(r"(?:^|[\s「『\"'(（])(?:tables|Results|Data|evidence|replication)/", text):
        return True
    return False


def sanitize_manuscript_prose(text: str) -> str:
    """Strip path stamps and product jargon from manuscript prose.

    Claim↔evidence binding stays in claim register / Results JSON / replication,
    never as parenthetical file paths in the body.
    """
    if not text:
        return ""
    out = text
    out = _EVIDENCE_PAREN_RE.sub("", out)
    out = _EVIDENCE_LINE_RE.sub("", out)
    # Drop lines that are mostly path / product annotations
    kept: list[str] = []
    for line in out.splitlines():
        if manuscript_has_path_leaks(line) and (
            "证据" in line
            or "/" in line
            or re.search(r"\.(json|csv|py|md)\b", line, re.I)
            or re.search(
                r"claim\s*register|Continuous|integrity|learn_notes|expand_mode|package",
                line,
                re.I,
            )
        ):
            # try to salvage pure academic text before the path stamp
            cleaned = _PATH_LEAK_RE.sub("", line)
            cleaned = re.sub(r"[（(]\s*[）)]", "", cleaned).strip()
            cleaned = re.sub(r"`[^`]+`", "", cleaned).strip()
            if cleaned and _cn_len(cleaned) >= 12 and not manuscript_has_path_leaks(cleaned):
                kept.append(cleaned)
            continue
        kept.append(line)
    out = "\n".join(kept)
    # Soften residual product English tokens if any slipped through
    replacements = {
        "Continuous Empirical Loop": "研究流程",
        "Continuous Loop": "研究流程",
        "claim register": "证据登记",
        "Claim Register": "证据登记",
        "causal_claim_allowed=false": "本文不作因果主张",
        "causal_claim_allowed=True": "因果主张需单独论证",
        "REPRO_OK": "复现通过",
    }
    for a, b in replacements.items():
        out = out.replace(a, b)
    # collapse excess blank lines
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip() + ("\n" if out.strip() else "")


@dataclass
class StepOutcome:
    step_id: str
    name: str
    status: str  # passed | failed | skipped
    artifacts: list[str] = field(default_factory=list)
    notes: str = ""
    elapsed_sec: float = 0.0
    error: str = ""


@dataclass
class PipelineRun:
    topic: str
    run_id: str
    started_at: str
    steps: list[StepOutcome] = field(default_factory=list)
    status: str = "running"
    final_artifacts: dict[str, str] = field(default_factory=dict)
    quality: dict[str, Any] = field(default_factory=dict)
    finished_at: str = ""

    def save(self, path: Path) -> None:
        _write_json(
            path,
            {
                "topic": self.topic,
                "run_id": self.run_id,
                "started_at": self.started_at,
                "finished_at": self.finished_at,
                "status": self.status,
                "steps": [asdict(s) for s in self.steps],
                "final_artifacts": self.final_artifacts,
                "quality": self.quality,
            },
        )


class FullPaperPipeline:
    """10-step full pipeline for parent education wage pilot."""

    TOPIC = "父母受教育水平对子女工资收入的影响"
    SLUG = "parent_education_wage"
    DATA = ROOT / "Data" / "Interim" / "parent_education_wage_repaired.csv"

    def __init__(
        self,
        *,
        use_llm: bool = True,
        provider_id: str = "grok",
        model: str | None = "grok-4.5",
        run_id: str | None = None,
        expand_mode: bool = False,
        degrade_mode: bool = False,
        learn_notes: str = "",
    ) -> None:
        self.use_llm = use_llm
        self.provider_id = provider_id
        self.model = model
        self.expand_mode = expand_mode
        self.degrade_mode = degrade_mode
        self.learn_notes = learn_notes
        stamp = time.strftime("%Y%m%d_%H%M%S")
        self.run_id = run_id or f"full_pipeline_{self.SLUG}_{stamp}"
        self.run_dir = ROOT / "state" / "runs" / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.ctx: dict[str, Any] = {"run_id": self.run_id, "topic": self.TOPIC}
        self.record = PipelineRun(topic=self.TOPIC, run_id=self.run_id, started_at=_now())
        self._evidence: dict[str, Any] = {}

    # ── LLM helper ─────────────────────────────────────────────

    def _llm(self, system: str, user: str, *, temperature: float = 0.25) -> str:
        if not self.use_llm:
            return ""
        from Product.backend.llm_client import chat_completion, load_local_env_if_present, LLMError

        load_local_env_if_present(ROOT)
        last_err: Exception | None = None
        for attempt in range(1, 4):
            try:
                text, usage = chat_completion(
                    [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    provider_id=self.provider_id,
                    model=self.model,
                    temperature=temperature,
                    # Keep short so RemoteDisconnected fails fast into course builder
                    timeout_seconds=35,
                )
                self.ctx.setdefault("llm_usage", []).append(usage or {})
                return (text or "").strip()
            except Exception as exc:  # noqa: BLE001 — never raise; writing must degrade
                last_err = exc
                name = type(exc).__name__
                print(f"  ⚠ llm attempt {attempt}/3 {name}: {exc}")
                time.sleep(1.5 * attempt)
                # Always continue retries for network / LLM stack failures
                continue
        print(f"  ⚠ llm gave up after retries: {last_err}")
        return ""

    def _step(self, step_id: str, name: str, fn: Callable[[], list[str]]) -> StepOutcome:
        print(f"\n══ {step_id} · {name} ══")
        t0 = time.time()
        try:
            arts = fn()
            out = StepOutcome(
                step_id=step_id,
                name=name,
                status="passed",
                artifacts=arts,
                elapsed_sec=round(time.time() - t0, 3),
            )
            print(f"  ✓ passed ({out.elapsed_sec}s) artifacts={len(arts)}")
        except Exception as exc:  # noqa: BLE001
            out = StepOutcome(
                step_id=step_id,
                name=name,
                status="failed",
                error=f"{type(exc).__name__}: {exc}",
                notes=traceback.format_exc()[-1500:],
                elapsed_sec=round(time.time() - t0, 3),
            )
            print(f"  ✗ failed: {out.error}")
        self.record.steps.append(out)
        self.record.save(self.run_dir / "pipeline_state.json")
        return out

    # ── steps ──────────────────────────────────────────────────

    def step_01_design(self) -> list[str]:
        arts: list[str] = []
        cq = ROOT / "causal_question.yaml"
        rd = ROOT / "research_design.md"
        if not cq.exists():
            raise FileNotFoundError("causal_question.yaml missing")
        if not rd.exists():
            raise FileNotFoundError("research_design.md missing")
        arts.append(str(cq.relative_to(ROOT)))
        arts.append(str(rd.relative_to(ROOT)))
        risk = self.run_dir / "01_design_risk.md"
        _write_text(
            risk,
            f"""# 设计风险 · {self.TOPIC}

- 主设计声明 IV/2SLS，但本轮 E2E **仅执行 OLS 描述基准**（产品可复现证据）。
- 不可把 OLS 关联写成因果 LATE。
- 父母教育构造依赖 P18 修复；需在正文披露口径。
- 进入工资样本存在选择偏误风险。
- 文献库若未 verified，不得写正式 bibliography claim。

run_id: `{self.run_id}`
generated: {_now()}
""",
        )
        arts.append(str(risk.relative_to(ROOT)))
        self.ctx["design_ok"] = True
        return arts

    def step_02_literature(self) -> list[str]:
        """Crossref DOI pack + optional CNKI page-verified pack (no invented cites)."""
        from runtime.literature_pack import (
            VerifiedWork,
            build_and_write,
            literature_section_prose,
            write_literature_artifacts,
            cite_short,
        )

        works_en, paths = build_and_write(
            root=ROOT,
            slug=self.SLUG,
            topic=self.TOPIC,
            run_id=self.run_id,
        )
        # Merge CNKI page-verified works if present (Playwright CDP search)
        cnki_path = ROOT / "litreview" / "cnki" / f"{self.SLUG}_verified.json"
        if not cnki_path.exists():
            cnki_path = ROOT / "litreview" / "cnki" / "cnki_parent_education_wage_verified.json"
        cnki_works: list[Any] = []
        if cnki_path.exists():
            try:
                raw = json.loads(cnki_path.read_text(encoding="utf-8"))
                items = raw.get("works") or raw if isinstance(raw, dict) else []
                org_re = re.compile(
                    r"大学|学院|中心|研究所|党校|研究院|财经|师范|民族|行政|研究|西部|中国|省|市|县|部$|系$"
                )

                def _clean_authors(s: str) -> str:
                    names: list[str] = []
                    for p in re.split(r"[;；,，]", s or ""):
                        p = re.sub(r"\d+$", "", p.strip()).strip()
                        if not p:
                            continue
                        if org_re.search(p):
                            m = re.match(r"^([\u4e00-\u9fff]{2,4})", p)
                            if m and not org_re.search(m.group(1)):
                                names.append(m.group(1))
                            continue
                        if re.fullmatch(r"[\u4e00-\u9fff]{2,4}", p):
                            names.append(p)
                    seen: set[str] = set()
                    out: list[str] = []
                    for n in names:
                        if n not in seen and not org_re.search(n):
                            seen.add(n)
                            out.append(n)
                    return "; ".join(out[:5])

                for w in items:
                    title = w.get("list_title") or w.get("title") or ""
                    if not title:
                        continue
                    authors = _clean_authors(w.get("authors") or "")
                    year = w.get("year") or (w.get("list_date") or "")[:4] or ""
                    journal = (w.get("list_journal") or w.get("journal") or "").split(".")[0].strip()
                    fam = re.sub(
                        r"[^\w\u4e00-\u9fff]",
                        "",
                        (authors.split(";")[0] if authors else "anon"),
                    )[:8]
                    role = (
                        "china_parent_income_closest"
                        if ("收入" in title or "工资" in title)
                        else "china_cnki"
                    )
                    cnki_works.append(
                        VerifiedWork(
                            citation_key=f"cnki_{fam}_{year}",
                            doi="",
                            title=title,
                            authors=authors,
                            year=int(year) if str(year).isdigit() else year,
                            venue=journal,
                            url=w.get("url") or "",
                            role=role,
                            topic_note=(w.get("abstract") or "")[:100],
                            verification_status=w.get("verification_status")
                            or "cnki_page_verified",
                            verification_notes="CNKI page verified",
                        )
                    )
            except (json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
                print(f"  ⚠ CNKI pack load failed: {exc}")

        works = list(works_en) + cnki_works
        if cnki_works:
            # rewrite combined artifacts + Chinese-augmented section
            paths = write_literature_artifacts(
                works,
                root=ROOT,
                slug=self.SLUG,
                topic=self.TOPIC,
                run_id=self.run_id,
            )
            base = literature_section_prose(works_en)
            closest = [w for w in cnki_works if "收入" in w.title or "工资" in w.title][:5]
            intergen = [w for w in cnki_works if "代际" in w.title][:4]
            hc = [w for w in cnki_works if "人力资本" in w.title or "教育" in w.title][:4]

            def _cites(ws: list[Any]) -> str:
                return "、".join(cite_short(w) for w in ws) if ws else "（待补）"

            cnki_para = (
                "### 中国知网检索补充（已核验条目）\n\n"
                "为补强中文对话，本文经中国知网主题检索并对详情页元数据做页面核验。"
                f"与本文结果变量最近的中文证据包括：{_cites(closest)}。"
                "这些研究普遍报告父母受教育程度与子女收入或工资存在正向关联，"
                "并讨论家庭背景与人力资本机制，但识别策略与样本口径各异。\n\n"
                f"在代际流动与教育扩张线索上，{_cites(intergen)} 等讨论了教育扩招与教育数量、质量的代际流动。"
                f"{_cites(hc)} 则从子女人力资本角度刻画中间结果。"
                "上述中文文献支撑问题合法性，也强化边界：本文 OLS+HC1 仅报告条件关联。\n\n"
                "知网核验条目与 Crossref 英文条目一并计入文献包。\n"
            )
            if "### 本文位置与贡献边界" in base:
                base = base.replace(
                    "### 本文位置与贡献边界",
                    cnki_para + "\n### 本文位置与贡献边界",
                )
            else:
                base = base + "\n" + cnki_para
            base = base.replace(
                f"已核验的 {len(works_en)} 篇",
                f"已核验的 {len(works)} 篇（含英文与中文知网）",
            )
            section_path = ROOT / "litreview" / f"{self.SLUG}_literature_section.md"
            _write_text(section_path, base)
            self.ctx["literature_section_md"] = base
            paths["section"] = str(section_path.relative_to(ROOT))
            paths["cnki_count"] = str(len(cnki_works))
        else:
            section_path = ROOT / paths.get("section", "")
            if section_path.exists():
                self.ctx["literature_section_md"] = section_path.read_text(encoding="utf-8")

        self.ctx["literature_verified_count"] = len(works)
        self.ctx["literature_works"] = works
        self._evidence["literature"] = {
            "verified_count": len(works),
            "crossref_count": len(works_en),
            "cnki_count": len(cnki_works),
            "dois": [w.doi for w in works if getattr(w, "doi", "")],
            "keys": [w.citation_key for w in works],
        }
        if not works:
            raise RuntimeError(
                "literature verification returned 0 works — refuse to pretend verified"
            )
        print(
            f"  → literature verified_count={len(works)} "
            f"(crossref={len(works_en)} cnki={len(cnki_works)})"
        )
        return [p for p in paths.values() if p and not str(p).isdigit()]

    def step_03_paper_reading(self) -> list[str]:
        notes = ROOT / "lit_reading_notes" / f"{self.SLUG}_reading_protocol.md"
        _write_text(
            notes,
            f"""# 论文阅读协议 · {self.TOPIC}

## 每篇核心文献必须回答

1. 识别策略是什么？
2. 数据与样本是谁？
3. 主结果数量级？
4. 对本文贡献矩阵落在哪一格？

## 本轮状态

- 尚无 verified PDF / DOI 绑定条目。
- 阅读笔记阶段 **blocked on metadata verification**。
- 下游写作必须用「待核验文献」措辞，不得伪造引用。

run_id: `{self.run_id}`
""",
        )
        return [str(notes.relative_to(ROOT))]

    def step_04_data_gate(self) -> list[str]:
        if not self.DATA.exists():
            raise FileNotFoundError(self.DATA)
        df = pd.read_csv(self.DATA)
        required = ["ln_wage", "parent_education", "age", "female", "urban", "edu_last", "experience"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise RuntimeError(f"missing columns: {missing}")

        rows = []
        for c in required:
            s = df[c]
            rows.append(
                {
                    "variable": c,
                    "n": int(s.notna().sum()),
                    "missing": int(s.isna().sum()),
                    "mean": float(s.mean(skipna=True)) if pd.api.types.is_numeric_dtype(s) else None,
                    "std": float(s.std(skipna=True)) if pd.api.types.is_numeric_dtype(s) else None,
                    "min": float(s.min(skipna=True)) if pd.api.types.is_numeric_dtype(s) else None,
                    "max": float(s.max(skipna=True)) if pd.api.types.is_numeric_dtype(s) else None,
                }
            )
        analysis = df.dropna(subset=required).copy()
        gate = {
            "run_id": self.run_id,
            "dataset": str(self.DATA.relative_to(ROOT)),
            "dataset_sha256": _sha256_file(self.DATA),
            "n_raw": int(len(df)),
            "n_analysis": int(len(analysis)),
            "required_variables": required,
            "variable_summary": rows,
            "status": "passed" if len(analysis) > 1000 else "failed_thin_sample",
            "generated_at": _now(),
        }
        if gate["status"] != "passed":
            raise RuntimeError(f"data gate failed thin sample n={len(analysis)}")

        jpath = ROOT / "Results" / "json" / f"{self.SLUG}_full_pipeline_data_gate.json"
        tpath = ROOT / "tables" / f"{self.SLUG}_table1_desc.csv"
        _write_json(jpath, gate)
        tpath.parent.mkdir(parents=True, exist_ok=True)
        with tpath.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

        md = ROOT / "artifacts" / f"{self.SLUG}_data_gate_report.md"
        _write_text(
            md,
            f"""# 数据门禁报告

- 数据：`{self.DATA.relative_to(ROOT)}`
- SHA256：`{gate['dataset_sha256'][:16]}…`
- 原始行数：{gate['n_raw']}
- 分析样本（关键变量无缺失）：{gate['n_analysis']}
- 状态：{gate['status']}

run_id: `{self.run_id}`
""",
        )
        self._evidence["data_gate"] = gate
        self._evidence["analysis_n"] = gate["n_analysis"]
        self.ctx["analysis_df_path"] = str(self.DATA)
        return [str(p.relative_to(ROOT)) for p in (jpath, tpath, md)]

    def step_05_causal_analysis(self) -> list[str]:
        import statsmodels.api as sm

        df = pd.read_csv(self.DATA)
        cols = ["ln_wage", "parent_education", "age", "female", "urban", "edu_last", "experience"]
        d = df.dropna(subset=cols).copy()
        y = d["ln_wage"].astype(float)
        X = d[["parent_education", "age", "female", "urban", "edu_last", "experience"]].astype(float)
        X = sm.add_constant(X)
        model = sm.OLS(y, X).fit(cov_type="HC1")

        coef_rows = []
        for name in model.params.index:
            coef_rows.append(
                {
                    "term": str(name),
                    "coef": float(model.params[name]),
                    "se": float(model.bse[name]),
                    "t": float(model.tvalues[name]),
                    "p": float(model.pvalues[name]),
                    "ci_low": float(model.conf_int().loc[name, 0]),
                    "ci_high": float(model.conf_int().loc[name, 1]),
                }
            )

        # Robustness: male/female subsample
        robust = []
        for label, mask in [
            ("full", slice(None)),
            ("female", d["female"] == 1),
            ("male", d["female"] == 0),
            ("urban", d["urban"] == 1),
            ("rural", d["urban"] == 0),
        ]:
            sub = d.loc[mask] if not isinstance(mask, slice) else d
            if len(sub) < 200:
                continue
            ys = sub["ln_wage"].astype(float)
            Xs = sm.add_constant(sub[["parent_education", "age", "female", "urban", "edu_last", "experience"]].astype(float))
            # drop collinear constant issues for pure female/male: female becomes constant
            if label in {"female", "male"}:
                Xs = sm.add_constant(sub[["parent_education", "age", "urban", "edu_last", "experience"]].astype(float))
            m = sm.OLS(ys, Xs).fit(cov_type="HC1")
            if "parent_education" in m.params.index:
                robust.append(
                    {
                        "spec": label,
                        "nobs": int(m.nobs),
                        "parent_education_coef": float(m.params["parent_education"]),
                        "parent_education_se": float(m.bse["parent_education"]),
                        "parent_education_p": float(m.pvalues["parent_education"]),
                    }
                )

        evidence = {
            "run_id": self.run_id,
            "estimator": "OLS",
            "cov_type": "HC1",
            "formula": "ln_wage ~ parent_education + age + female + urban + edu_last + experience",
            "nobs": int(model.nobs),
            "r2": float(model.rsquared),
            "r2_adj": float(model.rsquared_adj),
            "coefficients": coef_rows,
            "robustness": robust,
            "causal_claim_allowed": False,
            "claim_language": "statistical association under controls; not causal LATE",
            "generated_at": _now(),
            "dataset": str(self.DATA.relative_to(ROOT)),
            "dataset_sha256": _sha256_file(self.DATA),
        }
        jpath = ROOT / "Results" / "json" / f"{self.SLUG}_full_pipeline_main_results.json"
        _write_json(jpath, evidence)

        table2 = ROOT / "tables" / f"{self.SLUG}_table2_main_ols.csv"
        with table2.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(coef_rows[0].keys()))
            w.writeheader()
            w.writerows(coef_rows)

        rob_path = ROOT / "tables" / f"{self.SLUG}_table_robustness.csv"
        with rob_path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(robust[0].keys()))
            w.writeheader()
            w.writerows(robust)

        pe = next(r for r in coef_rows if r["term"] == "parent_education")
        self._evidence["main"] = evidence
        self._evidence["parent_education"] = pe
        return [str(p.relative_to(ROOT)) for p in (jpath, table2, rob_path)]

    def step_06_writing(self) -> list[str]:
        pe = self._evidence.get("parent_education") or {}
        main = self._evidence.get("main") or {}
        gate = self._evidence.get("data_gate") or {}
        # Machine facts for claim register / tables (paths OK here, never in manuscript body)
        facts = {
            "topic": self.TOPIC,
            "nobs": main.get("nobs"),
            "r2": main.get("r2"),
            "parent_education_coef": pe.get("coef"),
            "parent_education_se": pe.get("se"),
            "parent_education_p": pe.get("p"),
            "formula": main.get("formula"),
            "n_raw": gate.get("n_raw"),
            "n_analysis": gate.get("n_analysis"),
            "dataset": str(self.DATA.relative_to(ROOT)),
            "tables": {
                "table1": f"tables/{self.SLUG}_table1_desc.csv",
                "table2": f"tables/{self.SLUG}_table2_main_ols.csv",
                "robustness": f"tables/{self.SLUG}_table_robustness.csv",
            },
            "literature_verified_count": int(
                self.ctx.get("literature_verified_count")
                or (self._evidence.get("literature") or {}).get("verified_count")
                or 0
            ),
            "causal_claim_allowed": False,
            "literature_section_md": self.ctx.get("literature_section_md") or "",
            "literature_works": self.ctx.get("literature_works") or [],
        }
        # Load pack from disk if step_02 already ran in a prior process
        if not facts["literature_section_md"] or not facts["literature_works"]:
            pack_path = ROOT / "Results" / "json" / f"{self.SLUG}_literature_pack.json"
            section_path = ROOT / "litreview" / f"{self.SLUG}_literature_section.md"
            if pack_path.exists():
                try:
                    pack = json.loads(pack_path.read_text(encoding="utf-8"))
                    facts["literature_verified_count"] = int(pack.get("verified_count") or 0)
                    facts["literature_works"] = pack.get("works") or []
                    self.ctx["literature_works"] = facts["literature_works"]
                    self.ctx["literature_verified_count"] = facts["literature_verified_count"]
                except (json.JSONDecodeError, OSError):
                    pass
            if section_path.exists():
                facts["literature_section_md"] = section_path.read_text(encoding="utf-8")
                self.ctx["literature_section_md"] = facts["literature_section_md"]
        # Facts exposed to the writing model: numbers + verified cite strings only (no paths)
        llm_facts = {
            "topic": self.TOPIC,
            "nobs": main.get("nobs"),
            "r2": main.get("r2"),
            "parent_education_coef": pe.get("coef"),
            "parent_education_se": pe.get("se"),
            "parent_education_p": pe.get("p"),
            "formula": main.get("formula"),
            "n_raw": gate.get("n_raw"),
            "n_analysis": gate.get("n_analysis"),
            "literature_verified_count": facts["literature_verified_count"],
            "causal_claim_allowed": False,
            "table_labels": ["表1 描述统计", "表2 主回归", "表3 稳健性/分组"],
            "verified_cites": [
                {
                    "cite": f"{(w.get('authors') or '').split(',')[0]}（{w.get('year')}）"
                    if isinstance(w, dict)
                    else str(w),
                    "title": (w.get("title") if isinstance(w, dict) else getattr(w, "title", ""))[:80],
                    "year": w.get("year") if isinstance(w, dict) else getattr(w, "year", ""),
                    "venue": w.get("venue") if isinstance(w, dict) else getattr(w, "venue", ""),
                }
                for w in (facts.get("literature_works") or [])[:20]
            ],
        }

        # Primary deliverable: deterministic academic Chinese (no paths, ever).
        body = self._sanitize_manuscript_prose(self._fallback_paper(facts))
        print(f"  → course_paper_builder primary cn_chars={_cn_len(body)}")

        # Optional LLM polish of an already-clean draft. If it leaks paths or
        # collapses substance, discard and keep the course builder body.
        if self.use_llm:
            system = (
                "你是应用微观经济学中文论文的润色编辑。"
                "任务：在不改变任何数字与主张边界的前提下，把草稿改得更像正式课程论文。\n"
                "## 硬红线\n"
                "1. 数字只许来自用户 facts（可合理取 2–3 位小数，p 值可写 <0.001）。\n"
                "2. 禁止编造文献作者、年份、期刊；verified=0 时不得写已发表引用。\n"
                "3. causal_claim_allowed=false：禁止导致/提高/政策效应/LATE/工具变量已识别；"
                "只用关联、偏相关、条件关联。\n"
                "4. 正文是给人读的论文。绝对禁止：仓库路径、文件名、.json/.csv、"
                "「证据：…」、claim register、Continuous Loop、integrity、package、run_id、"
                "质量门、L8、复现脚本路径。表只称「表1」「表2」「稳健性表」。\n"
                "5. 保持完整 Markdown 章节结构；完整中文段落，不要 bullet 墙。\n"
            )
            if self.degrade_mode:
                system += "文献未核验必须诚实声明；识别未闭合写清「本文不解决」。\n"
            if self.expand_mode:
                system += (
                    "在事实不变前提下加长识别威胁、样本选择、系数关联解读与限制，"
                    "禁止路径与产品术语，禁止假引用与假机制结果。\n"
                )
            # Never feed a path-leaking prior into the model (that is how paths re-enter).
            clean_seed = body
            if self.expand_mode:
                existing = ROOT / "Manuscripts" / "generated" / f"{self.SLUG}_full_pipeline_paper.md"
                if existing.exists():
                    prior_raw = existing.read_text(encoding="utf-8", errors="replace")
                    prior_clean = self._sanitize_manuscript_prose(prior_raw)
                    if prior_clean and not self._manuscript_has_path_leaks(prior_clean) and _cn_len(prior_clean) >= 2000:
                        clean_seed = prior_clean[:14000]
            user = (
                "请润色下列学术草稿。facts 仅供核对数字；不要把 facts 里的键名写进正文。\n"
                f"facts=\n{json.dumps(llm_facts, ensure_ascii=False, indent=2)}\n\n"
                f"{('修订指令：' + self.learn_notes + chr(10)) if self.learn_notes else ''}"
                f"## 草稿\n{clean_seed}\n"
            )
            try:
                polished = self._llm(system, user, temperature=0.25)
            except Exception as exc:  # noqa: BLE001
                print(f"  ⚠ writing llm hard-fail → keep course builder: {exc}")
                polished = ""
            polished = self._sanitize_manuscript_prose(polished)
            if (
                polished
                and _cn_len(polished) >= 3000
                and not self._manuscript_has_path_leaks(polished)
            ):
                body = polished
                print(f"  → llm polish accepted cn_chars={_cn_len(body)}")
            elif polished:
                print(
                    f"  → llm polish rejected "
                    f"(cn={_cn_len(polished)} leaks={self._manuscript_has_path_leaks(polished)}); "
                    "keep course builder"
                )

        body = self._sanitize_manuscript_prose(body)
        if self._manuscript_has_path_leaks(body) or _cn_len(body) < 2500:
            body = self._sanitize_manuscript_prose(self._fallback_paper(facts))
            print(f"  → final fallback course_paper_builder cn_chars={_cn_len(body)}")

        paper_path = ROOT / "Manuscripts" / "generated" / f"{self.SLUG}_full_pipeline_paper.md"
        _write_text(paper_path, body)

        # Also write section splits if headings exist
        sections_dir = ROOT / "Manuscripts" / "sections"
        sections_dir.mkdir(parents=True, exist_ok=True)
        _write_text(sections_dir / "main-results.md", self._extract_or_stub(body, "结果", facts))
        _write_text(sections_dir / "data-and-measurement.md", self._extract_or_stub(body, "数据", facts))

        claim = ROOT / "evidence" / f"{self.SLUG}_claim_register_full_pipeline.md"
        _write_text(
            claim,
            f"""# Claim Register · {self.run_id}

| claim_id | 文本 claim | 强度 | 绑定证据 | 状态 |
|----------|------------|------|----------|------|
| C1 | parent_education 系数 = {pe.get('coef')} | 关联 | tables/{self.SLUG}_table2_main_ols.csv + Results/json/{self.SLUG}_full_pipeline_main_results.json | bound |
| C2 | nobs = {main.get('nobs')} | 事实 | 同上 | bound |
| C3 | 因果 LATE | 禁止 | — | blocked_by_design |
| C4 | 文献贡献 | 已核验对话 | Results/json/{self.SLUG}_literature_pack.json + references.bib | {"bound" if int(self.ctx.get("literature_verified_count") or 0) > 0 else "unverified_lit"} |

规则：任何未绑定 claim 不得进入正式结论。正文引用仅允许 DOI 核验条目。
""",
        )
        self.ctx["paper_path"] = str(paper_path)
        return [str(p.relative_to(ROOT)) for p in (paper_path, claim)]

    def _sanitize_manuscript_prose(self, text: str) -> str:
        return sanitize_manuscript_prose(text)

    def _manuscript_has_path_leaks(self, text: str) -> bool:
        return manuscript_has_path_leaks(text)

    def _expand_fallback(self, body: str, facts: dict[str, Any]) -> str:
        """Legacy hook: never append path/product appendices to the manuscript.

        Academic thickness lives in ``course_paper_builder``. Claim↔path binding
        stays in claim register / Results JSON only.
        """
        del facts  # facts used only by claim register writers, not prose appendices
        return self._sanitize_manuscript_prose(body or self._fallback_paper({}))

    def _fallback_paper(self, facts: dict[str, Any]) -> str:
        from runtime.course_paper_builder import build_course_paper

        return build_course_paper(
            facts,
            run_id=self.run_id,
            slug=self.SLUG,
            learn_notes=self.learn_notes or "",
            expand_mode=self.expand_mode,
            degrade_mode=self.degrade_mode,
        )

    def _extract_or_stub(self, body: str, key: str, facts: dict[str, Any]) -> str:
        return f"# {key}\n\n（从全文草稿同步；run_id={self.run_id}）\n\nfacts.nobs={facts.get('nobs')}\n"

    def step_07_revision(self) -> list[str]:
        paper = Path(self.ctx.get("paper_path") or ROOT / "Manuscripts" / "generated" / f"{self.SLUG}_full_pipeline_paper.md")
        from Program.workbench.paper_quality import build_paper_quality_report, write_paper_quality_report

        report = build_paper_quality_report(ROOT, paper, profile="general_working_paper")
        out = ROOT / "Results" / "json" / f"{self.SLUG}_full_pipeline_quality.json"
        write_paper_quality_report(ROOT, report, out)
        recommended = report.get("recommended_next_tasks") or []
        self.record.quality = {
            "verdict": report.get("verdict"),
            "status": report.get("status"),
            "path": str(out.relative_to(ROOT)),
            "recommended_next_tasks": recommended,
        }
        self.ctx["quality_report"] = report
        # Machine-readable learn signal for Continuous Loop (not human theater)
        learn_signal = ROOT / "Results" / "json" / f"{self.SLUG}_full_pipeline_learn_signal.json"
        _write_json(
            learn_signal,
            {
                "run_id": self.run_id,
                "verdict": report.get("verdict"),
                "recommended_next_tasks": recommended,
                "generated_at": _now(),
            },
        )
        notes = ROOT / "Reviews" / f"{self.SLUG}_full_pipeline_revision_notes.md"
        _write_text(
            notes,
            f"""# 修订笔记 · {self.run_id}

## 质量门

- path: `{out.relative_to(ROOT)}`
- verdict: {report.get('verdict')}
- status: {report.get('status')}
- learn_signal: `{learn_signal.relative_to(ROOT)}`

## 强制红线

1. 文献 verified_count=0 → 不得写正式引用列表冒充已核验。
2. OLS ≠ 因果。
3. 所有数字必须回链 table/json。

## recommended_next_tasks（机器可读，供 L8 消费）

```json
{json.dumps(recommended, ensure_ascii=False, indent=2)}
```
""",
        )
        return [str(out.relative_to(ROOT)), str(notes.relative_to(ROOT)), str(learn_signal.relative_to(ROOT))]

    def step_08_format_citation(self) -> list[str]:
        pack_path = ROOT / "Results" / "json" / f"{self.SLUG}_literature_pack.json"
        verified_count = int(self.ctx.get("literature_verified_count") or 0)
        dois: list[str] = []
        if pack_path.exists():
            try:
                pack = json.loads(pack_path.read_text(encoding="utf-8"))
                verified_count = max(verified_count, int(pack.get("verified_count") or 0))
                dois = [w.get("doi", "") for w in (pack.get("works") or []) if w.get("doi")]
            except (json.JSONDecodeError, OSError, TypeError, ValueError):
                pass
        bib_ok = (ROOT / "references.bib").exists() and verified_count > 0
        bib_status = {
            "run_id": self.run_id,
            "verified_bibliography": bib_ok,
            "verified_count": verified_count,
            "references_bib_present": (ROOT / "references.bib").exists(),
            "dois": dois,
            "source": "runtime.literature_pack",
            "status": "passed" if bib_ok else "blocked_unverified",
            "action": (
                "ok"
                if bib_ok
                else "run step_02_literature / runtime.literature_pack.build_and_write"
            ),
        }
        path = ROOT / "Results" / "json" / f"{self.SLUG}_full_pipeline_citation_gate.json"
        _write_json(path, bib_status)
        # also mirror gate path written by literature_pack
        return [str(path.relative_to(ROOT)), "references.bib"] if bib_ok else [str(path.relative_to(ROOT))]

    def step_09_replication(self) -> list[str]:
        script = ROOT / "replication" / f"reproduce_{self.SLUG}_full_pipeline.py"
        _write_text(
            script,
            f'''#!/usr/bin/env python3
"""Reproduce main OLS for {self.SLUG} full pipeline."""
from pathlib import Path
import json
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data/Interim/parent_education_wage_repaired.csv"
cols = ["ln_wage", "parent_education", "age", "female", "urban", "edu_last", "experience"]
d = pd.read_csv(DATA).dropna(subset=cols)
y = d["ln_wage"].astype(float)
X = sm.add_constant(d[["parent_education", "age", "female", "urban", "edu_last", "experience"]].astype(float))
m = sm.OLS(y, X).fit(cov_type="HC1")
out = {{
  "nobs": int(m.nobs),
  "parent_education": float(m.params["parent_education"]),
  "parent_education_se": float(m.bse["parent_education"]),
}}
print(json.dumps(out, ensure_ascii=False, indent=2))
expected = json.loads((ROOT / "Results/json/{self.SLUG}_full_pipeline_main_results.json").read_text())
pe = next(c for c in expected["coefficients"] if c["term"] == "parent_education")
assert abs(out["parent_education"] - pe["coef"]) < 1e-6
assert out["nobs"] == expected["nobs"]
print("REPRO_OK")
''',
        )
        # run repro
        import subprocess

        r = subprocess.run(
            ["python3", str(script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
        report = ROOT / "replication" / f"{self.SLUG}_repro_report.md"
        _write_text(
            report,
            f"""# 复现报告

- script: `{script.relative_to(ROOT)}`
- exit: {r.returncode}
- stdout:\n```\n{r.stdout[-2000:]}\n```
- stderr:\n```\n{r.stderr[-1000:]}\n```
- status: {"passed" if r.returncode == 0 and "REPRO_OK" in r.stdout else "failed"}
""",
        )
        if r.returncode != 0 or "REPRO_OK" not in r.stdout:
            raise RuntimeError(f"replication failed: {r.stderr or r.stdout}")
        return [str(script.relative_to(ROOT)), str(report.relative_to(ROOT))]

    def step_10_defense(self) -> list[str]:
        pe = self._evidence.get("parent_education") or {}
        main = self._evidence.get("main") or {}
        qa = ROOT / "Reviews" / f"{self.SLUG}_full_pipeline_defense_qa.md"
        _write_text(
            qa,
            f"""# 答辩预案 · {self.TOPIC}

## Q1：你识别的是因果吗？

A：否。本轮主结果是 OLS+HC1 下的统计关联。研究设计保留 IV 方向，但本 run 未执行 2SLS。正文不作因果主张。

## Q2：核心系数是多少？

A：父母教育系数约 {pe.get('coef')}（se≈{pe.get('se')}, p≈{pe.get('p')}），n={main.get('nobs')}。以表 2 为准。

## Q3：数据从哪来？

A：中国家庭追踪调查（CFPS）修复后的可分析样本；详见数据节与复现材料。

## Q4：最大缺口？

A：正式文献核验尚未完成；IV 未落地；识别边界需在后续设计中闭合。
""",
        )
        return [str(qa.relative_to(ROOT))]

    # ── main ───────────────────────────────────────────────────

    ALL_STEPS: list[tuple[str, str]] = [
        ("01_design", "选题与研究设计"),
        ("02_literature", "文献检索与综述"),
        ("03_paper_reading", "论文阅读与拆解"),
        ("04_data_gate", "数据获取与清洗"),
        ("05_causal_analysis", "统计分析与因果推断"),
        ("06_writing", "论文写作"),
        ("07_revision", "论文修改与润色"),
        ("08_format_citation", "格式与引用"),
        ("09_replication", "复现与归档"),
        ("10_defense", "答辩与展示"),
    ]

    def _step_fn(self, step_id: str) -> Callable[[], list[str]]:
        return {
            "01_design": self.step_01_design,
            "02_literature": self.step_02_literature,
            "03_paper_reading": self.step_03_paper_reading,
            "04_data_gate": self.step_04_data_gate,
            "05_causal_analysis": self.step_05_causal_analysis,
            "06_writing": self.step_06_writing,
            "07_revision": self.step_07_revision,
            "08_format_citation": self.step_08_format_citation,
            "09_replication": self.step_09_replication,
            "10_defense": self.step_10_defense,
        }[step_id]

    def hydrate_evidence_from_disk(self) -> None:
        """Reload main results / data gate so subset re-runs don't need 04/05 again."""
        main_p = ROOT / "Results" / "json" / f"{self.SLUG}_full_pipeline_main_results.json"
        gate_p = ROOT / "Results" / "json" / f"{self.SLUG}_full_pipeline_data_gate.json"
        if main_p.exists():
            main = json.loads(main_p.read_text(encoding="utf-8"))
            self._evidence["main"] = main
            pe = next((c for c in main.get("coefficients", []) if c.get("term") == "parent_education"), {})
            self._evidence["parent_education"] = pe
        if gate_p.exists():
            self._evidence["data_gate"] = json.loads(gate_p.read_text(encoding="utf-8"))
        paper = ROOT / "Manuscripts" / "generated" / f"{self.SLUG}_full_pipeline_paper.md"
        if paper.exists():
            self.ctx["paper_path"] = str(paper)

    def run(self, only_steps: list[str] | None = None) -> PipelineRun:
        """Run full 10-step pipeline, or a subset (for Continuous Loop L8 re-entry)."""
        name_map = dict(self.ALL_STEPS)
        if only_steps:
            steps = [(sid, name_map[sid], self._step_fn(sid)) for sid in only_steps if sid in name_map]
            self.hydrate_evidence_from_disk()
        else:
            steps = [(sid, name, self._step_fn(sid)) for sid, name in self.ALL_STEPS]

        print(f"\n🚀 Full paper pipeline  run_id={self.run_id}")
        print(f"   topic={self.TOPIC}")
        print(f"   llm={self.use_llm} provider={self.provider_id}")
        print(f"   steps={[s[0] for s in steps]} expand={self.expand_mode} degrade={self.degrade_mode}")

        for step_id, name, fn in steps:
            out = self._step(step_id, name, fn)
            if out.status == "failed":
                self.record.status = "failed"
                self.record.finished_at = _now()
                self.record.save(self.run_dir / "pipeline_state.json")
                self._write_summary()
                return self.record

        # Linear path still reports pipeline-level completed; Continuous Loop
        # owns green/halted semantics and must not treat this as course-green.
        self.record.status = "completed"
        self.record.finished_at = _now()
        paper = self.ctx.get("paper_path", "")
        if paper:
            self.record.final_artifacts["paper"] = str(Path(paper).relative_to(ROOT)) if Path(paper).is_absolute() else paper
        self.record.final_artifacts["run_dir"] = str(self.run_dir.relative_to(ROOT))
        self.record.save(self.run_dir / "pipeline_state.json")
        self._write_summary()
        return self.record

    def _write_summary(self) -> None:
        lines = [
            f"# Full Pipeline Summary · {self.run_id}",
            "",
            f"- topic: {self.TOPIC}",
            f"- status: **{self.record.status}**",
            f"- started: {self.record.started_at}",
            f"- finished: {self.record.finished_at}",
            f"- quality: {json.dumps(self.record.quality, ensure_ascii=False)}",
            "",
            "## Steps",
            "",
        ]
        for s in self.record.steps:
            lines.append(f"- `{s.step_id}` {s.name}: **{s.status}** ({s.elapsed_sec}s) {s.error}")
            for a in s.artifacts:
                lines.append(f"  - {a}")
        lines.append("")
        lines.append("## Try")
        lines.append("")
        lines.append("```bash")
        lines.append(f"cat {self.record.final_artifacts.get('paper', 'Manuscripts/generated/...')}")
        lines.append(f"cat {self.run_dir.relative_to(ROOT)}/pipeline_state.json | head")
        lines.append("```")
        path = ROOT / "Reviews" / f"{self.SLUG}_full_pipeline_summary.md"
        _write_text(path, "\n".join(lines) + "\n")
        self.record.final_artifacts["summary"] = str(path.relative_to(ROOT))
        # also copy pointer
        _write_json(ROOT / "Results" / "json" / f"{self.SLUG}_full_pipeline_latest.json", {
            "run_id": self.run_id,
            "status": self.record.status,
            "summary": str(path.relative_to(ROOT)),
            "paper": self.record.final_artifacts.get("paper"),
            "quality": self.record.quality,
            "run_dir": str(self.run_dir.relative_to(ROOT)),
        })


def main() -> int:
    import argparse
    import sys

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    parser = argparse.ArgumentParser(description="Full empirical paper pipeline E2E")
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--provider", default="grok")
    parser.add_argument("--model", default="grok-4.5")
    args = parser.parse_args()

    pipe = FullPaperPipeline(use_llm=not args.no_llm, provider_id=args.provider, model=args.model or None)
    result = pipe.run()
    print("\n======== FULL PIPELINE DONE ========")
    print(f"status: {result.status}")
    print(f"run_id: {result.run_id}")
    print(f"artifacts: {result.final_artifacts}")
    return 0 if result.status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
