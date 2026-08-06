"""Topic literature pack: Crossref DOI verification + artifacts for writing.

Manuscript rule: verified author-year citations may enter prose.
Repo paths / claim IDs never enter the paper body.
"""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CROSSREF = "https://api.crossref.org/works"
UA = "empirical-paper-workbench/1.0 (literature-verify; mailto:dev@local)"

# Parent-education → child wage / intergenerational education seed set.
# Only entries whose DOI resolves via Crossref become "verified".
SEED_DOIS: list[dict[str, str]] = [
    {
        "doi": "10.1086/298118",
        "citation_key": "becker_tomes_1986",
        "role": "theory_anchor",
        "topic_note": "代际人力资本与家庭投资理论框架",
    },
    {
        "doi": "10.1016/s1573-4463(99)03010-2",
        "citation_key": "solon_1999",
        "role": "review_mobility",
        "topic_note": "劳动市场代际流动综述",
    },
    {
        "doi": "10.1016/s1573-4463(99)03011-4",
        "citation_key": "card_1999",
        "role": "returns_review",
        "topic_note": "教育对收入因果效应综述与识别讨论",
    },
    {
        "doi": "10.1257/0002828053828635",
        "citation_key": "black_devereux_salvanes_2005",
        "role": "closest_causal_parent_edu",
        "topic_note": "义务教育改革作工具，父母教育对子女教育",
    },
    {
        "doi": "10.1257/000282802760015757",
        "citation_key": "behrman_rosenzweig_2002",
        "role": "causal_mother_schooling",
        "topic_note": "母亲教育与下一代教育",
    },
    {
        "doi": "10.1086/506484",
        "citation_key": "oreopoulos_page_stevens_2006",
        "role": "compulsory_schooling_iv",
        "topic_note": "义务教育法代际效应",
    },
    {
        "doi": "10.1257/jel.49.3.615",
        "citation_key": "holmlund_lindahl_plug_2011",
        "role": "method_survey",
        "topic_note": "父母教育对子女教育因果证据比较综述",
    },
    {
        "doi": "10.1016/j.jdeveco.2011.05.009",
        "citation_key": "li_liu_zhang_2012",
        "role": "china_returns_twins",
        "topic_note": "中国城镇双胞胎教育回报",
    },
    {
        "doi": "10.1016/j.jce.2019.09.004",
        "citation_key": "chen_jiang_zhou_2020",
        "role": "china_cfps_returns",
        "topic_note": "学制改革与中国城镇教育回报（含 CFPS）",
    },
    {
        "doi": "10.1111/rode.12538",
        "citation_key": "gong_2019",
        "role": "china_parent_in_mincer",
        "topic_note": "中国 Mincer 方程中父母教育的作用",
    },
    {
        "doi": "10.1007/s11459-011-0148-y",
        "citation_key": "chen_feng_2011",
        "role": "china_parent_wage_closest",
        "topic_note": "中国父母教育与子女工资关联",
    },
    {
        "doi": "10.1016/j.chieco.2021.101710",
        "citation_key": "huo_golley_2022",
        "role": "china_intergen_gender",
        "topic_note": "中国教育代际传递的性别维度",
    },
    {
        "doi": "10.1016/j.chieco.2019.101327",
        "citation_key": "liu_wan_2019",
        "role": "china_expansion",
        "topic_note": "教育扩张与教育代际传递",
    },
]


@dataclass
class VerifiedWork:
    citation_key: str
    doi: str
    title: str
    authors: str
    year: int | str
    venue: str
    volume: str = ""
    issue: str = ""
    pages: str = ""
    url: str = ""
    role: str = ""
    topic_note: str = ""
    verification_status: str = "doi_verified"
    verification_notes: str = "Resolved via Crossref works API"


def _http_get_json(url: str, timeout: float = 30.0) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _authors_str(authors: list[dict[str, Any]] | None) -> str:
    if not authors:
        return ""
    parts = []
    for a in authors[:8]:
        family = (a.get("family") or "").strip()
        given = (a.get("given") or "").strip()
        if family and given:
            parts.append(f"{family}, {given}")
        elif family:
            parts.append(family)
        elif given:
            parts.append(given)
    return "; ".join(parts)


def _year_from_message(msg: dict[str, Any]) -> int | str:
    for key in ("published-print", "published-online", "issued", "created"):
        parts = (msg.get(key) or {}).get("date-parts") or []
        if parts and parts[0]:
            return int(parts[0][0])
    return ""


def resolve_doi(doi: str) -> dict[str, Any]:
    url = f"{CROSSREF}/{urllib.parse.quote(doi.strip())}"
    data = _http_get_json(url)
    return data["message"]


def verify_seed(
    seeds: list[dict[str, str]] | None = None,
    *,
    sleep_s: float = 0.25,
    retries: int = 2,
) -> list[VerifiedWork]:
    seeds = seeds or SEED_DOIS
    out: list[VerifiedWork] = []
    for seed in seeds:
        doi = seed["doi"]
        last_err = ""
        for attempt in range(1, retries + 2):
            try:
                msg = resolve_doi(doi)
                vol = str(msg.get("volume") or "")
                issue = str(msg.get("issue") or "")
                pages = str(msg.get("page") or "")
                vip = ""
                if vol and issue and pages:
                    vip = f"{vol}({issue}):{pages}"
                elif vol and pages:
                    vip = f"{vol}:{pages}"
                elif vol:
                    vip = vol
                work = VerifiedWork(
                    citation_key=seed.get("citation_key") or _key_from_meta(msg),
                    doi=str(msg.get("DOI") or doi),
                    title=(msg.get("title") or [""])[0],
                    authors=_authors_str(msg.get("author")),
                    year=_year_from_message(msg),
                    venue=(msg.get("container-title") or [""])[0],
                    volume=vol,
                    issue=issue,
                    pages=pages,
                    url=str(msg.get("URL") or f"https://doi.org/{doi}"),
                    role=seed.get("role", ""),
                    topic_note=seed.get("topic_note", ""),
                    verification_notes=f"Crossref resolve OK; vip={vip}",
                )
                out.append(work)
                last_err = ""
                break
            except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, KeyError, json.JSONDecodeError) as exc:
                last_err = f"{type(exc).__name__}: {exc}"
                time.sleep(0.6 * attempt)
        if last_err:
            print(f"  ⚠ literature DOI fail {doi}: {last_err}")
        time.sleep(sleep_s)
    return out


def _key_from_meta(msg: dict[str, Any]) -> str:
    authors = msg.get("author") or []
    fam = (authors[0].get("family") if authors else "anon") or "anon"
    year = _year_from_message(msg) or "nd"
    slug = re.sub(r"[^a-z0-9]+", "_", fam.lower()).strip("_")
    return f"{slug}_{year}"


def cite_short(work: VerifiedWork) -> str:
    """Chinese-academic author-year short cite, e.g. Black et al.（2005）."""
    authors = [a.strip() for a in work.authors.split(";") if a.strip()]
    families = []
    for a in authors:
        fam = a.split(",")[0].strip()
        if fam:
            families.append(fam)
    year = work.year
    if not families:
        return f"（{year}）"
    if len(families) == 1:
        return f"{families[0]}（{year}）"
    if len(families) == 2:
        return f"{families[0]} 与 {families[1]}（{year}）"
    return f"{families[0]} 等（{year}）"


def volume_issue_pages(work: VerifiedWork) -> str:
    if work.volume and work.issue and work.pages:
        return f"{work.volume}({work.issue}):{work.pages}"
    if work.volume and work.pages:
        return f"{work.volume}:{work.pages}"
    if work.volume:
        return work.volume
    return work.pages


def to_bibtex(works: list[VerifiedWork]) -> str:
    chunks: list[str] = []
    for w in works:
        authors_bib = " and ".join(
            part.strip() for part in w.authors.split(";") if part.strip()
        )
        fields = [
            f"  title = {{{w.title}}}",
            f"  author = {{{authors_bib}}}",
            f"  year = {{{w.year}}}",
        ]
        if w.venue:
            fields.append(f"  journal = {{{w.venue}}}")
        if w.volume:
            fields.append(f"  volume = {{{w.volume}}}")
        if w.issue:
            fields.append(f"  number = {{{w.issue}}}")
        if w.pages:
            fields.append(f"  pages = {{{w.pages.replace('-', '--')}}}")
        if w.doi:
            fields.append(f"  doi = {{{w.doi}}}")
        if w.url:
            fields.append(f"  url = {{{w.url}}}")
        body = ",\n".join(fields)
        chunks.append(f"@article{{{w.citation_key},\n{body}\n}}\n")
    return "\n".join(chunks)


def contribution_matrix_md(works: list[VerifiedWork], *, topic: str, run_id: str = "") -> str:
    lines = [
        f"# 贡献矩阵 · {topic}",
        "",
        f"核验状态：`verified_count={len(works)}`（Crossref DOI）。",
        "",
        "| 角色 | 文献 | 年份 | 期刊 | 与本文关系 | DOI |",
        "|------|------|------|------|------------|-----|",
    ]
    for w in works:
        lines.append(
            f"| {w.role or '—'} | {cite_short(w)} · {w.title[:48]}… | {w.year} | "
            f"{w.venue[:36]} | {w.topic_note} | `{w.doi}` |"
        )
    lines.extend(
        [
            "",
            "## 本文相对位置（诚实）",
            "",
            "- 最近因果文献（义务教育/双胞胎/收养）识别父母教育对子女**教育**或工资的处理效应；本文当前仅交付 **OLS+HC1 关联**。",
            "- 中国回报与代际文献提供情境与对照；本文不声称填补其因果空白。",
            "- 正式写作仅允许上表 verified 条目进入作者—年份引用。",
            "",
            f"run_id: `{run_id}`" if run_id else "",
            "",
        ]
    )
    return "\n".join(lines)


def literature_section_prose(works: list[VerifiedWork]) -> str:
    """Academic Chinese literature section body (no paths)."""
    by_role = {w.role: w for w in works}
    c_bt = by_role.get("theory_anchor")
    c_solon = by_role.get("review_mobility")
    c_card = by_role.get("returns_review")
    c_black = by_role.get("closest_causal_parent_edu")
    c_behr = by_role.get("causal_mother_schooling")
    c_oreo = by_role.get("compulsory_schooling_iv")
    c_holm = by_role.get("method_survey")
    c_li = by_role.get("china_returns_twins")
    c_chen = by_role.get("china_cfps_returns")
    c_gong = by_role.get("china_parent_in_mincer")
    c_cf = by_role.get("china_parent_wage_closest")
    c_huo = by_role.get("china_intergen_gender")
    c_liu = by_role.get("china_expansion")

    def C(w: VerifiedWork | None) -> str:
        return cite_short(w) if w else "（待补）"

    n = len(works)
    return f"""## 文献与贡献

本文的问题位于两条长期线索的交叉处。第一条线索是代际人力资本与社会流动：家庭如何把资源、偏好与机会传递给下一代。{C(c_bt)} 把父母对子女的人力资本投资放进跨期家庭决策框架；{C(c_solon)} 系统梳理劳动市场上的代际收入流动测度与解释。第二条线索是教育的劳动市场回报：在能力与家庭背景纠缠的情况下，教育年限与工资关联应如何被解读。{C(c_card)} 总结了教育对收入因果效应的主要识别路径与估计量级讨论。两条线索在「父母教育 → 子女结果」处相遇：父母教育既可能通过子女教育、健康与非认知技能影响成年收入，也可能只是更深层家庭优势的代理变量。

### 识别策略文献

要把选择与因果拆开，现有研究主要依赖外生教育变动。{C(c_black)} 利用挪威义务教育年限延长，以改革前后队列差异识别父母教育对子女教育的影响，并强调 OLS 关联显著并不等于因果成立。{C(c_behr)} 讨论提高女性受教育水平是否提高下一代教育，提示母亲教育与子女结果之间的关联需要仔细处理能力与家庭背景。{C(c_oreo)} 考察义务教育法的代际效应，把制度冲击当作识别父母人力资本传递的来源。{C(c_holm)} 对双胞胎、收养与义务教育改革等策略下的父母教育因果效应做了比较综述，结论是：不同设计给出的因果估计往往弱于朴素关联，且因样本与制度而异。这些文献共同给出本文必须遵守的纪律——在缺乏可信外生变动时，不得把条件关联写成政策处理效应。

### 中国情境与回报证据

中国研究为上述讨论提供了重要的制度与数据对照。{C(c_li)} 使用城镇双胞胎数据估计教育回报，以控制家庭与部分基因层面的混淆。{C(c_chen)} 利用学制改革等自然实验，在含 CFPS 等微观数据的框架下估计城镇教育回报，说明中国教育扩张与制度改革会改变教育—工资映射。{C(c_gong)} 重新审视 Mincer 工资方程中父母教育的作用，提醒：若把父母教育仅当作「背景控制」而不讨论其生成过程，解释容易漂移。{C(c_cf)} 直接讨论中国父母教育与子女工资的关联，与本文结果变量更为接近。{C(c_huo)} 与 {C(c_liu)} 则从性别维度与教育扩张角度描述教育代际传递的变化，提示中国情境下的异质性与政策背景不可忽视。

### 本文位置与贡献边界

在已核验的 {n} 篇文献所构成的对话中，本文的位置是克制的。第一，本文交付的是 CFPS 可分析样本上、控制常规人口与人力资本变量后的 **OLS+HC1 条件关联**，而不是义务教育工具变量、双胞胎差分或收养设计下的因果估计。第二，本文与 {C(c_cf)}、{C(c_gong)} 同属「父母背景—子女工资」描述与关联讨论一侧，但明确拒绝把系数升级为局部平均处理效应。第三，相对于 {C(c_black)}、{C(c_oreo)} 与 {C(c_holm)} 所代表的识别前沿，本文的贡献不在于新的外生变动，而在于把可复现的关联基线、标准误约定与识别边界写清楚，为后续若引入政策暴露或制度工具时提供对照锚点。

相应的非贡献同样必须列清：不解决能力偏误；不提供第一阶段与弱工具诊断；不完成中介分解；不把中国局部样本关联外推为一般政策参数。若下一步引入可信的外生教育变动，应单独立项完成设计与诊断，并与上列因果文献直接对话，而不是在本 OLS 结果上口头升级。

本节引用均来自已通过 DOI 元数据核验的条目（Crossref）；未核验文献不进入正文作者—年份引用。
"""


def write_literature_artifacts(
    works: list[VerifiedWork],
    *,
    root: Path | None = None,
    slug: str = "parent_education_wage",
    topic: str = "父母受教育水平对子女工资收入的影响",
    run_id: str = "",
) -> dict[str, str]:
    """Write verified CSV/bib/matrix/JSON; return relative paths."""
    root = root or ROOT
    lit_dir = root / "litreview"
    lit_dir.mkdir(parents=True, exist_ok=True)
    data_lit = root / "Data" / "literature" / "processed"
    data_lit.mkdir(parents=True, exist_ok=True)
    results_json = root / "Results" / "json"
    results_json.mkdir(parents=True, exist_ok=True)

    # candidates + verified CSV (project litreview)
    cand_path = lit_dir / f"{slug}_literature_candidates.csv"
    with cand_path.open("w", encoding="utf-8", newline="") as fh:
        fields = [
            "key",
            "title",
            "authors",
            "year",
            "venue",
            "doi",
            "status",
            "role",
            "note",
        ]
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for x in works:
            w.writerow(
                {
                    "key": x.citation_key,
                    "title": x.title,
                    "authors": x.authors,
                    "year": x.year,
                    "venue": x.venue,
                    "doi": x.doi,
                    "status": x.verification_status,
                    "role": x.role,
                    "note": x.topic_note,
                }
            )

    verified_csv = data_lit / "verified_bibliography.csv"
    # Keep robot-topic rows if present? Safer: write topic-specific + shared verified for this slug
    topic_verified = data_lit / f"{slug}_verified_bibliography.csv"
    fieldnames = [
        "source_id",
        "citation_key",
        "title",
        "authors",
        "year",
        "venue",
        "volume_issue_pages",
        "doi",
        "publisher_url",
        "working_paper_url",
        "cnki_url",
        "google_scholar_url",
        "openalex_id",
        "semantic_scholar_id",
        "zotero_key",
        "pdf_hash",
        "acquisition_source",
        "verification_status",
        "verification_notes",
        "topic_relevance",
        "method_relevance",
        "data_relevance",
        "contribution_role",
        "used_in_section",
    ]
    rows = []
    for x in works:
        rows.append(
            {
                "source_id": x.citation_key,
                "citation_key": x.citation_key,
                "title": x.title,
                "authors": x.authors,
                "year": str(x.year),
                "venue": x.venue,
                "volume_issue_pages": volume_issue_pages(x),
                "doi": x.doi,
                "publisher_url": x.url,
                "working_paper_url": "",
                "cnki_url": "",
                "google_scholar_url": "",
                "openalex_id": "",
                "semantic_scholar_id": "",
                "zotero_key": "",
                "pdf_hash": "",
                "acquisition_source": "crossref_doi_resolve",
                "verification_status": x.verification_status,
                "verification_notes": x.verification_notes,
                "topic_relevance": x.topic_note,
                "method_relevance": x.role,
                "data_relevance": "",
                "contribution_role": x.role,
                "used_in_section": "Literature and Contribution",
            }
        )
    for path in (topic_verified, verified_csv):
        with path.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)

    matrix = lit_dir / f"{slug}_contribution_matrix.md"
    matrix.write_text(contribution_matrix_md(works, topic=topic, run_id=run_id), encoding="utf-8")
    (data_lit / "contribution_matrix.md").write_text(
        contribution_matrix_md(works, topic=topic, run_id=run_id), encoding="utf-8"
    )

    query = lit_dir / f"{slug}_query_plan.json"
    query.write_text(
        json.dumps(
            {
                "topic": topic,
                "queries": [
                    "parental education child wage intergenerational",
                    "compulsory schooling intergenerational Oreopoulos",
                    "returns to education China CFPS twins",
                    "Black Devereux Salvanes apple doesn't fall far",
                ],
                "status": "doi_verified",
                "verified_count": len(works),
                "dois": [w.doi for w in works],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    bib_body = to_bibtex(works)
    bib_path = root / "references.bib"
    # Replace placeholder test bib with real verified set (keep backup if huge custom?)
    backup = root / "references.bib.bak_before_litpack"
    if bib_path.exists() and not backup.exists():
        backup.write_text(bib_path.read_text(encoding="utf-8"), encoding="utf-8")
    bib_path.write_text(bib_body, encoding="utf-8")
    (lit_dir / f"{slug}_verified.bib").write_text(bib_body, encoding="utf-8")

    pack_json = results_json / f"{slug}_literature_pack.json"
    pack_json.write_text(
        json.dumps(
            {
                "topic": topic,
                "run_id": run_id,
                "verified_count": len(works),
                "verification": "crossref_doi",
                "works": [asdict(w) for w in works],
                "cites": {w.citation_key: cite_short(w) for w in works},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    section_md = lit_dir / f"{slug}_literature_section.md"
    section_md.write_text(literature_section_prose(works), encoding="utf-8")

    gate = results_json / f"{slug}_full_pipeline_citation_gate.json"
    gate.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "verified_bibliography": True,
                "verified_count": len(works),
                "status": "passed" if works else "blocked_unverified",
                "source": "runtime.literature_pack.crossref",
                "dois": [w.doi for w in works],
                "bib_path": "references.bib",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    rel = lambda p: str(p.relative_to(root))  # noqa: E731
    return {
        "candidates": rel(cand_path),
        "verified_csv": rel(topic_verified),
        "verified_csv_shared": rel(verified_csv),
        "matrix": rel(matrix),
        "query": rel(query),
        "bib": rel(bib_path),
        "pack_json": rel(pack_json),
        "section": rel(section_md),
        "citation_gate": rel(gate),
        "verified_count": str(len(works)),
    }


def build_and_write(
    *,
    root: Path | None = None,
    slug: str = "parent_education_wage",
    topic: str = "父母受教育水平对子女工资收入的影响",
    run_id: str = "",
    offline_works: list[VerifiedWork] | None = None,
) -> tuple[list[VerifiedWork], dict[str, str]]:
    """Verify seeds (or use offline) and write all literature artifacts."""
    if offline_works is not None:
        works = offline_works
    else:
        print("  → Crossref verifying literature DOIs…")
        works = verify_seed()
        print(f"  → verified_count={len(works)}")
    paths = write_literature_artifacts(
        works, root=root, slug=slug, topic=topic, run_id=run_id
    )
    return works, paths


if __name__ == "__main__":
    works, paths = build_and_write(run_id="cli_literature_pack")
    print(json.dumps({"verified_count": len(works), "paths": paths}, ensure_ascii=False, indent=2))
