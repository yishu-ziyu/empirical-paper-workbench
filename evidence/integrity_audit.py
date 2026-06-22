#!/usr/bin/env python3
"""integrity_audit.py — 反捏造审计（PaperSpine integrity_audit 模式）

运行：
    python3 evidence/integrity_audit.py --section main-results --write
    # 或对所有 section：
    python3 evidence/integrity_audit.py --all --write

退出码：
    0 = CLEAN（可进入翻译 / 投递）
    1 = BLOCKED（必须修，未登记声明 = 捏造）
    2 = 工具错误（路径 / JSON 损坏等）

每个发现 (AuditFinding) 输出 6 字段（PaperSpine 教学风格）：
    severity | what_was_found | root_cause | fix_action |
    downstream_impact | teaching_note
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# data types
# ---------------------------------------------------------------------------

@dataclass
class AuditFinding:
    id: str
    severity: str                   # BLOCKER | WARNING | INFO
    dimension: str
    what_was_found: str
    root_cause: str
    fix_action: str
    downstream_impact: str
    teaching_note: str


@dataclass
class AuditDimension:
    name: str
    findings: list[AuditFinding] = field(default_factory=list)

    @property
    def status(self) -> str:
        if any(f.severity == "BLOCKER" for f in self.findings):
            return "BLOCKED"
        if any(f.severity == "WARNING" for f in self.findings):
            return "WARNINGS"
        return "CLEAN"


@dataclass
class AuditReport:
    section: str
    section_path: str
    dimensions: list[AuditDimension] = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return any(d.status == "BLOCKED" for d in self.dimensions)

    @property
    def total_findings(self) -> int:
        return sum(len(d.findings) for d in self.dimensions)


# ---------------------------------------------------------------------------
# Constants — 反捏造禁词 / 必报模式
# ---------------------------------------------------------------------------

# 在 main-results.md 中**禁止**出现 / 必报为 BLOCKER 的模式
# 每一项映射"主标题 + 教学说明"
FORBIDDEN_NUMERIC_PATTERNS: dict[str, dict[str, str]] = {
    # 2026-06-02 模型捏造的具体数字
    "E-value=1.18": {
        "severity": "BLOCKER",
        "teach": "E-value 在本研究数据上计算失败 (AttributeError)；可写'失败 / failed'，禁止写 1.18 这类编造数字。",
    },
    "Acemoglu 0.5%": {
        "severity": "BLOCKER",
        "teach": "Acemoglu & Restrepo (2020) 的具体弹性数字需要去原论文查；本 evidence_bank 没有登记，禁止凭印象写。",
    },
    "Dauth 0.4%": {
        "severity": "BLOCKER",
        "teach": "Dauth et al. (2021) 的具体弹性数字需要去原论文查；本 evidence_bank 没有登记。",
    },
    "Sobel 30/70%": {
        "severity": "BLOCKER",
        "teach": "Sobel test 在本研究从未运行；中介比例 (30%/70%) 是捏造。",
    },
    "Baron-Kenny 1986": {
        "severity": "BLOCKER",
        "teach": "Baron & Kenny (1986) 在本研究并未被使用；如要引用先在 evidence_bank.md 登记。",
    },
    "2005-2007 基期": {
        "severity": "BLOCKER",
        "teach": "Bartik 工具变量基期未在 approved_findings 中确认；写论文前先查 design_spec.json。",
    },
    "剔除 2014 年": {
        "severity": "BLOCKER",
        "teach": "剔除某年的稳健性检验必须真的跑过；本 evidence_bank 没有对应 record。",
    },
    "OLS 系数被高估": {
        "severity": "BLOCKER",
        "teach": "本研究中 IV (0.1994) > OLS (0.1039)，IV > OLS 提示 OLS 被向下偏 (attenuation bias)，不是被高估。方向性错误是 LLM 幻觉典型表现。",
    },
}

# 弱断言 / 逻辑跳跃词 — 累积出现时触发 WARNING
WEAK_WORDS = {"clearly", "obviously", "undoubtedly", "without a doubt", "it is clear that"}
LEAP_WORDS = {"therefore", "thus", "hence", "consequently", "it follows that"}

# p-value 模式但缺统计量上下文
P_VALUE_RE = re.compile(r"p\s*[<>=]\s*0\.0[15](?!\d)")

# 4 位及以上小数 / 百分比 / 系数 — 审计锚点
NUMBER_PATTERNS = [
    re.compile(r"\b\d+\.\d{3,}\b"),                # 0.1039
    re.compile(r"\b\d+\.\d+\s*%"),                 # 0.2%
    re.compile(r"\bF\s*=\s*\d+"),                  # F=284
    re.compile(r"\bp\s*[<>=]\s*\d"),               # p<0.01
    re.compile(r"\bp\s*=\s*0\.\d+"),               # p=0.012
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_claim_register_ids(claim_register_md: str) -> set[str]:
    """从 claim_register.md 抽出所有已登记的 value 数字串。

    返回形如 {"0.1039", "0.1994", "0.0798", "14685.77", ...}。
    """
    found: set[str] = set()
    # 从表格 value 列抓数字
    for m in re.finditer(r"\b\d+\.\d+\b", claim_register_md):
        found.add(m.group(0))
    # 整数（如 N=15697, F=284, 14685.77）
    for m in re.finditer(r"\b\d{2,}\b", claim_register_md):
        found.add(m.group(0))
    return found


def _extract_evidence_bank_ids(evidence_bank_md: str) -> set[str]:
    """从 evidence_bank.md 抽出所有登记的数字锚点。"""
    return _extract_claim_register_ids(evidence_bank_md)  # 同种扫描


def _extract_numbers_in_section(section_md: str) -> set[str]:
    """从 main-results.md 抽出所有出现的数字（4 位以上小数 / 整数 / 百分比）。

    排除：
    - 章节引用 (如 §5.2 / §6.3)
    - LaTeX tabular 表格行（通过 tabular/booktabs 启发式识别）
    - 列表编号 / 表头 (如 (1) (2))
    """
    # 先把 LaTeX tabular 块挖掉
    cleaned = re.sub(r"\\begin\{tabular\}.*?\\end\{tabular\}", "", section_md, flags=re.DOTALL)
    # 章节引用
    cleaned = re.sub(r"§\s*\d+\.\d+", "", cleaned)
    # 整段代码行（以多空格 + | 开头的当 LaTeX 表格行删掉）
    cleaned = re.sub(r"^\s*\|.*$", "", cleaned, flags=re.MULTILINE)
    # 数字抽取
    found: set[str] = set()
    for m in re.finditer(r"\b\d+\.\d{3,}\b", cleaned):
        found.add(m.group(0).strip())
    for m in re.finditer(r"\b\d+\.\d+\s*%?", cleaned):
        found.add(m.group(0).rstrip("%").strip())
    for m in re.finditer(r"\b\d{2,}\b", cleaned):
        found.add(m.group(0).strip())
    return found


# ---------------------------------------------------------------------------
# Dimension 1 — 必需文件存在
# ---------------------------------------------------------------------------

REQUIRED_FILES = [
    "evidence/evidence_bank.md",
    "evidence/claim_register.md",
    "evidence/pipeline.md",
    "Manuscripts/sections/main-results.md",
]


def audit_required_files(project_root: Path) -> AuditDimension:
    dim = AuditDimension("Required Files")
    counter = 0
    for rel in REQUIRED_FILES:
        path = project_root / rel
        if not path.exists():
            counter += 1
            dim.findings.append(AuditFinding(
                id=f"REQ-{counter:03d}",
                severity="BLOCKER",
                dimension=dim.name,
                what_was_found=f"Required file `{rel}` is missing",
                root_cause="evidence/ 4 机制流水线必备文件；任何一个缺失 → 审计无法继续。",
                fix_action=f"按 evidence/README.md 的设计补齐 `{rel}`。",
                downstream_impact="integrity_audit 无证据池可参照；下游翻译 / 投递 gate 全部失效。",
                teaching_note="Pipeline 缺哪一环，audit 就抓哪一环。把'建文件'从'自由发挥'变成'硬门禁'。",
            ))
    if not dim.findings:
        dim.findings.append(AuditFinding(
            id="REQ-000", severity="INFO", dimension=dim.name,
            what_was_found=f"All {len(REQUIRED_FILES)} required files present",
            root_cause="", fix_action="", downstream_impact="", teaching_note="",
        ))
    return dim


# ---------------------------------------------------------------------------
# Dimension 2 — 数字锚点：每个数字必须出现在 claim_register / evidence_bank
# ---------------------------------------------------------------------------

def audit_number_anchoring(project_root: Path, section_name: str) -> AuditDimension:
    dim = AuditDimension("Number Anchoring")
    section_path = project_root / f"Manuscripts/sections/{section_name}.md"
    if not section_path.exists():
        dim.findings.append(AuditFinding(
            id="ANC-000", severity="BLOCKER", dimension=dim.name,
            what_was_found=f"Section file `{section_path.relative_to(project_root)}` not found",
            root_cause="audit 调用方提供了不存在的 section 名。",
            fix_action=f"确认 section 名；当前可用: main-results, abstract, conclusion, ...（来自 Manuscripts/sections/）。",
            downstream_impact="无内容可审计；流程中断。",
            teaching_note="",
        ))
        return dim

    section_md = section_path.read_text(encoding="utf-8")
    claim_register_path = project_root / "evidence/claim_register.md"
    evidence_bank_path = project_root / "evidence/evidence_bank.md"
    if not claim_register_path.exists() or not evidence_bank_path.exists():
        return dim  # REQ-* 已经报过了

    claim_ids = _extract_claim_register_ids(claim_register_path.read_text(encoding="utf-8"))
    bank_ids = _extract_evidence_bank_ids(evidence_bank_path.read_text(encoding="utf-8"))
    registered = claim_ids | bank_ids

    section_numbers = _extract_numbers_in_section(section_md)
    # 过滤掉"被 evidence_bank 显式声明是 gap" 的数字
    # 当前 (TODO)：evidence_bank §6 列出 GAP-001 ~ GAP-008，但没有具体数字。
    # 所以所有未登记数字都报 WARNING / BLOCKER。

    # 分级：4 位小数以上 → BLOCKER；2-3 位小数 / 整数 → WARNING
    block_counter = 0
    warn_counter = 0

    for num in sorted(section_numbers):
        # 跳过常见非数据（章节号、长度阈值等）
        if num in {"16", "90", "3000", "6000", "2010", "2014", "2016", "2018", "2020", "2005", "2007", "1991", "2013", "1997", "2017", "2019", "2020"}:
            continue
        # 章节号
        if re.match(r"^\d\.[1-9]$", num):
            continue
        # 年份 (1900-2099)
        if re.match(r"^(19|20)\d{2}$", num):
            continue
        if num in registered:
            continue
        # 浮点：4 位以上小数 → BLOCKER
        if re.match(r"^\d+\.\d{4,}$", num):
            block_counter += 1
            dim.findings.append(AuditFinding(
                id=f"ANC-{block_counter:03d}",
                severity="BLOCKER",
                dimension=dim.name,
                what_was_found=f"Number `{num}` appears in main-results.md but is NOT registered in claim_register.md or evidence_bank.md",
                root_cause="未走 4 大机制流水线 (写作前 → 写作中 → 写作后)：写完数字没登记。",
                fix_action=(
                    f"在 evidence/claim_register.md 新增一行：\n"
                    f"  | C-NEW | §X.Y | <原文片段> | {num} | <source_path> | <JSONPath> | approved/derived | verbatim | <note> |\n"
                    f"或确认 `{num}` 真的是 gap → 在 evidence/evidence_bank.md §6 加 gap_id，在 main-results.md 显式写'待 §6 补充'。"
                ),
                downstream_impact="**未登记 = 捏造**。这一数字若实际不在 approved_findings / regression_tables / analysis_result 中，整篇论文的可信度归零。",
                teaching_note=(
                    "4 位小数（0.1039、0.1994、23.47 这类）的可信度只来自 evidence 里的精确字段。"
                    "LLM 凭印象写出来的'近似值'几乎一定对不上 evidence；让 audit 自动捕获是唯一可靠路径。"
                ),
            ))
        else:
            warn_counter += 1
            dim.findings.append(AuditFinding(
                id=f"ANC-W{warn_counter:03d}",
                severity="WARNING",
                dimension=dim.name,
                what_was_found=f"Number `{num}` is not registered (lower precision: 2-3 decimal or integer)",
                root_cause="可能为派生数字（如比例、CI 下界）、整数（如样本量、阈值）。",
                fix_action=f"在 claim_register.md 的 `confidence=derived` 行登记；若是 gap 标 gap。",
                downstream_impact="派生 / 整数类数字登记不全，audit 无法完整追溯。",
                teaching_note="整数和 2-3 位小数也要登记，因为它们也常被捏造（如 95% CI 的 0.0439 是派生但很精确）。",
            ))

    if not dim.findings:
        dim.findings.append(AuditFinding(
            id="ANC-000", severity="INFO", dimension=dim.name,
            what_was_found="All numbers in section are anchored to claim_register or evidence_bank",
            root_cause="", fix_action="", downstream_impact="", teaching_note="",
        ))
    return dim


# ---------------------------------------------------------------------------
# Dimension 3 — 禁词 / 必报模式（E-value 1.18 这类历史捏造指纹）
# ---------------------------------------------------------------------------

def audit_forbidden_patterns(project_root: Path, section_name: str) -> AuditDimension:
    dim = AuditDimension("Forbidden Patterns")
    section_path = project_root / f"Manuscripts/sections/{section_name}.md"
    if not section_path.exists():
        return dim

    text = section_path.read_text(encoding="utf-8")
    counter = 0

    # 3.1 历史捏造指纹
    for pattern, info in FORBIDDEN_NUMERIC_PATTERNS.items():
        if pattern.lower() in text.lower():
            counter += 1
            dim.findings.append(AuditFinding(
                id=f"FORB-{counter:03d}",
                severity=info["severity"],
                dimension=dim.name,
                what_was_found=f"Forbidden pattern `{pattern}` found in section",
                root_cause="LLM 在类似 prompt 下倾向于补足'可信数字'，但这些数字本 evidence_bank 没有登记。",
                fix_action=(
                    f"删除 `{pattern}` 这类内容；"
                    f"如要写 E-value / Acemoglu 弹性，先把数字加进 evidence/claim_register.md 的 `gap` 行，"
                    f"再去 BibTeX / 原论文核实；最后走 approved_findings 流程。"
                ),
                downstream_impact="**这是 2026-06-02 触怒用户的 18 条捏造的核心模式**。再次出现 = 论文作废。",
                teaching_note=info["teach"],
            ))

    # 3.2 p-value 但缺统计量上下文（粗筛：仅在同段无 F/t/χ² 时报）
    p_matches = list(P_VALUE_RE.finditer(text))
    if p_matches:
        # 按段落切分，每个 p-value 检查所在段落是否有 F= / t= / χ²= / chi-square / First-stage
        paragraphs = re.split(r"\n\s*\n", text)
        # 把 p_match 映射回所在段落
        pos = 0
        p_orphans: list[str] = []
        for para in paragraphs:
            end = pos + len(para)
            for m in p_matches:
                if pos <= m.start() < end:
                    para_lower = para.lower()
                    has_stat = any(
                        tok in para_lower
                        for tok in ("f=", "t=", "t_stat", "chi", "first-stage", "kp ", "hausman", "r²", "r-squared")
                    )
                    if not has_stat:
                        p_orphans.append(m.group(0))
                    break
            pos = end
        if p_orphans:
            counter += 1
            dim.findings.append(AuditFinding(
                id=f"FORB-{counter:03d}",
                severity="WARNING",
                dimension=dim.name,
                what_was_found=f"Found {len(p_orphans)} orphan p-value(s) (no F/t/χ² in same paragraph): {p_orphans[:4]}",
                root_cause="AI 生成的结果部分常出现『整齐 p-value』但缺统计量上下文。",
                fix_action="对每个孤儿 p-value 补 t-stat / F-stat / chi-square 等统计量。",
                downstream_impact="统计审稿人会立刻质疑完整性。",
                teaching_note="P-value 永远不该孤立出现；'p<0.01' 加 't=17.6' 是最低标准。",
            ))

    # 3.3 弱断言 / 逻辑跳跃
    found_weak = [w for w in WEAK_WORDS if w in text.lower()]
    if found_weak:
        counter += 1
        dim.findings.append(AuditFinding(
            id=f"FORB-{counter:03d}",
            severity="WARNING",
            dimension=dim.name,
            what_was_found=f"Weak assertion words: {', '.join(found_weak)}",
            root_cause="修辞捷径，背后常常是证据不足。",
            fix_action="替换为具体证据或删除。",
            downstream_impact="专家读者会立刻降低信任。",
            teaching_note="如果真的清晰，不需要说'clearly'；'clearly' 通常在掩盖薄弱的推理。",
        ))

    leap_count = sum(text.lower().count(w) for w in LEAP_WORDS)
    para_count = max(1, text.count("\n\n") + 1)
    if leap_count / para_count > 1.5:
        counter += 1
        dim.findings.append(AuditFinding(
            id=f"FORB-{counter:03d}",
            severity="WARNING",
            dimension=dim.name,
            what_was_found=f"High logical-leap density: {leap_count} deductive connectors in ~{para_count} paragraphs ({leap_count/para_count:.1f}/para)",
            root_cause="结论性连接词被当推理步骤用。",
            fix_action="每个 'therefore / thus' 之前补一个观察 → 解读 → 含义 的中间步骤。",
            downstream_impact="读者感到跳跃式结论。",
            teaching_note="一篇文章里因此/所以超过 1.5 次/段，通常意味着推理链断。",
        ))

    if not dim.findings:
        dim.findings.append(AuditFinding(
            id="FORB-000", severity="INFO", dimension=dim.name,
            what_was_found="No forbidden patterns detected",
            root_cause="", fix_action="", downstream_impact="", teaching_note="",
        ))
    return dim


# ---------------------------------------------------------------------------
# Dimension 4 — 数字与回归表真值源一致性
# ---------------------------------------------------------------------------

def audit_source_of_truth_drift(project_root: Path, section_name: str) -> AuditDimension:
    dim = AuditDimension("Source-of-Truth Drift")
    # Source-of-truth drift 只在 main-results 跑（其它 section 本来就不引数字）
    if section_name != "main-results":
        dim.findings.append(AuditFinding(
            id="DRIFT-000", severity="INFO", dimension=dim.name,
            what_was_found="Source-of-truth drift check is main-results-specific (skipped for this section)",
            root_cause="", fix_action="", downstream_impact="", teaching_note="",
        ))
        return dim
    section_path = project_root / f"Manuscripts/sections/{section_name}.md"
    reg_path = project_root / "Results/json/regression_tables.json"
    if not section_path.exists() or not reg_path.exists():
        return dim
    section_md = section_path.read_text(encoding="utf-8")
    reg = _load_json(reg_path)

    counter = 0
    for table in reg.get("tables", []):
        for row in table.get("coefficient_rows", []):
            term = row["term"]
            coef = round(row["coefficient"], 4)
            coef_str = f"{coef:.4f}"
            if term not in {"ln_robot", "female", "age", "edu_last", "urban", "intercept"}:
                continue
            # 数字是否出现在 main-results.md
            if coef_str in section_md:
                continue
            # 容忍 3 位小数 (e.g. 0.104)
            short = f"{coef:.3f}"
            if short in section_md:
                continue
            # 容忍 -0.0002 / 0.0001 这种 4 位但绝对值小
            if coef != 0 and abs(coef) < 0.01 and short in section_md:
                continue
            # 在文中是否提到了 term 但没数字
            if term in section_md:
                counter += 1
                dim.findings.append(AuditFinding(
                    id=f"DRIFT-{counter:03d}",
                    severity="INFO",
                    dimension=dim.name,
                    what_was_found=f"`{term}` is mentioned in main-results.md but its exact coefficient `{coef_str}` from `{table['table_id']}` is not present",
                    root_cause="可能用文字描述代替了具体数字 → 仍要登记到 claim_register.md。",
                    fix_action="确认是文字描述后，在 claim_register.md 把对应行 confidence 标为 narrative。",
                    downstream_impact="读者无法独立验证；论文审计仍可走通但需要 narrative 来源。",
                    teaching_note="INFO 级别：审计建议，不阻断流程。",
                ))

    if not dim.findings:
        dim.findings.append(AuditFinding(
            id="DRIFT-000", severity="INFO", dimension=dim.name,
            what_was_found="All registered coefficients either appear in section or are narrative references",
            root_cause="", fix_action="", downstream_impact="", teaching_note="",
        ))
    return dim


# ---------------------------------------------------------------------------
# Dimension 5 — gap 诚实性：8 个缺口必须显式声明
# ---------------------------------------------------------------------------

GAP_DECLARATION_PATTERNS = {
    "GAP-001": r"分样本",
    "GAP-002": r"替换工具变量",
    "GAP-003": r"替换结果变量",
    "GAP-004": r"替换控制变量集",
    "GAP-005": r"(E-?value.*失败|失败.*E-?value|未报告.*E-?value)",
    "GAP-006": r"中介(效应)?.*分解|mediation",
    "GAP-007": r"IV.*(Oster|Sensemakr)|Oster.*IV",
}

# 每个 gap 只在指定 section 集合中查（其它 section 不该重复声明）
GAP_SCOPE: dict[str, set[str]] = {
    "GAP-001": {"robustness-mechanisms-heterogeneity", "main-results"},
    "GAP-002": {"robustness-mechanisms-heterogeneity", "main-results"},
    "GAP-003": {"robustness-mechanisms-heterogeneity", "main-results"},
    "GAP-004": {"robustness-mechanisms-heterogeneity", "main-results"},
    "GAP-005": {"main-results", "robustness-mechanisms-heterogeneity"},
    "GAP-006": {"main-results", "robustness-mechanisms-heterogeneity"},
    "GAP-007": {"main-results", "robustness-mechanisms-heterogeneity"},
}


def audit_gap_honesty(project_root: Path, section_name: str) -> AuditDimension:
    dim = AuditDimension("Gap Honesty")
    section_path = project_root / f"Manuscripts/sections/{section_name}.md"
    if not section_path.exists():
        return dim
    text = section_path.read_text(encoding="utf-8")

    counter = 0
    in_scope = [gid for gid, scope in GAP_SCOPE.items() if section_name in scope]
    for gap_id in in_scope:
        pat = GAP_DECLARATION_PATTERNS[gap_id]
        if not re.search(pat, text, flags=re.IGNORECASE):
            counter += 1
            dim.findings.append(AuditFinding(
                id=f"GAP-{counter:03d}",
                severity="BLOCKER",
                dimension=dim.name,
                what_was_found=f"Gap `{gap_id}` (pattern `{pat}`) is declared in evidence_bank.md §6 AND is in-scope for `{section_name}.md` ({len(in_scope)} gaps apply to this section), but the section does NOT explicitly mention it",
                root_cause="evidence_bank 登记了缺口 + 本 section 是该 gap 的声明位置，但论文没有诚实声明。",
                fix_action=(
                    f"在 `{section_name}.md` 显式写'{gap_id}: 待 §X 补充'或'未在本文档实证'。"
                ),
                downstream_impact="读者无法区分'做过了未呈现'和'没做'；审稿人若发现默认是后者。",
                teaching_note=f"诚实声明 gap 是学术写作的护城河；不写 = 默认在掩盖。仅在 '{section_name}' 触发该 gap 表明本节承担'缺口披露'责任。",
            ))

    if not dim.findings:
        scope_info = f"({len(in_scope)} gaps in-scope for this section)" if in_scope else "(no gaps in-scope for this section)"
        dim.findings.append(AuditFinding(
            id="GAP-000", severity="INFO", dimension=dim.name,
            what_was_found=f"All in-scope gaps are explicitly mentioned in the section {scope_info}",
            root_cause="", fix_action="", downstream_impact="", teaching_note="",
        ))
    return dim


# ---------------------------------------------------------------------------
# Dimension 6 — section 完整性：stub 必须达到最低长度 + 引用至少 1 个 evidence
# ---------------------------------------------------------------------------

# 各 section 的最低中文字符数（working paper 长度的硬下限）
SECTION_MIN_CHARS: dict[str, int] = {
    "abstract": 400,
    "introduction": 2000,
    "literature-and-contribution": 2000,
    "institutional-background-theory-context": 1800,
    "data-and-measurement": 2000,
    "empirical-strategy": 2000,
    "main-results": 2500,
    "robustness-mechanisms-heterogeneity": 2000,
    "conclusion": 1500,
}

# 各 section 至少要引用多少个 evidence_id（来自 section→evidence 绑定表）
SECTION_MIN_EVIDENCE_REFS: dict[str, int] = {
    "abstract": 1,
    "introduction": 1,
    "literature-and-contribution": 1,
    "institutional-background-theory-context": 1,
    "data-and-measurement": 1,
    "empirical-strategy": 1,
    "main-results": 2,
    "robustness-mechanisms-heterogeneity": 1,
    "conclusion": 1,
}


def _count_chinese_chars(text: str) -> int:
    return sum(1 for c in text if "\u4e00" <= c <= "\u9fff")


def _load_section_evidence_bindings(project_root: Path) -> dict[str, list[str]]:
    """从 manuscript_section_evidence_bindings.json 读每个 section 的 evidence_id 列表。"""
    path = project_root / "Results/json/manuscript_section_evidence_bindings.json"
    if not path.exists():
        return {}
    try:
        data = _load_json(path)
    except Exception:
        return {}
    out: dict[str, list[str]] = {}
    slug_map = {
        "Abstract": "abstract",
        "Introduction": "introduction",
        "Literature and Contribution": "literature-and-contribution",
        "Institutional Background / Theory / Context": "institutional-background-theory-context",
        "Data and Measurement": "data-and-measurement",
        "Empirical Strategy": "empirical-strategy",
        "Main Results": "main-results",
        "Robustness / Mechanisms / Heterogeneity": "robustness-mechanisms-heterogeneity",
        "Conclusion": "conclusion",
    }
    for s in data.get("sections", []):
        slug = slug_map.get(s.get("section", ""), s.get("section", "").lower().replace(" ", "-"))
        ids = [b.get("evidence_id", "") for b in s.get("bindings", []) if b.get("evidence_id")]
        out[slug] = ids
    return out


def audit_section_completeness(project_root: Path, section_name: str) -> AuditDimension:
    """检查 section 是否是 stub（行数/引用数都不够）。"""
    dim = AuditDimension("Section Completeness")
    section_path = project_root / f"Manuscripts/sections/{section_name}.md"
    if not section_path.exists():
        dim.findings.append(AuditFinding(
            id="COMP-000", severity="BLOCKER", dimension=dim.name,
            what_was_found=f"Section file `{section_path.relative_to(project_root)}` not found",
            root_cause="audit 调用方提供了不存在的 section 名。",
            fix_action=f"在 Manuscripts/sections/ 下创建 `{section_name}.md`",
            downstream_impact="无内容可审计；流程中断。",
            teaching_note="",
        ))
        return dim
    text = section_path.read_text(encoding="utf-8")
    counter = 0

    # 1. 中文字符数
    min_chars = SECTION_MIN_CHARS.get(section_name, 1500)
    cn_chars = _count_chinese_chars(text)
    if cn_chars < min_chars:
        counter += 1
        dim.findings.append(AuditFinding(
            id=f"COMP-{counter:03d}",
            severity="BLOCKER",
            dimension=dim.name,
            what_was_found=f"`{section_name}.md` 只有 {cn_chars} 个中文字符，远低于 working paper 下限 {min_chars}",
            root_cause="这是一个 stub placeholder，不是 working paper 章节。",
            fix_action=(
                f"扩写 `{section_name}.md` 至至少 {min_chars} 个中文字符。"
                f"扩写时遵循 evidence/pipeline.md 阶段 3：每写一条数字 → 在 evidence/claim_register.md 登记一行。"
            ),
            downstream_impact=f"BLOCKED。当前不扩写 = 投递一篇含 8 个 stub 的论文 = 学术不端。",
            teaching_note="Stub 长度检查是反'空文件 / 占位符'的硬门禁；audit 给的硬下限是诚实写作的最低线。",
        ))

    # 2. 引用 evidence_id 数（基于已绑定的 evidence_id 列表）
    bindings_map = _load_section_evidence_bindings(project_root)
    section_bindings = bindings_map.get(section_name, [])
    if section_bindings:
        min_refs = SECTION_MIN_EVIDENCE_REFS.get(section_name, 1)
        # 在文中查 evidence_id 的出现（粗筛：evidence_id 是简单 snake_case 字符串）
        text_lower = text.lower()
        refs_found = [eid for eid in section_bindings if eid.lower() in text_lower]
        # 兜底：路径 / 文件名出现也算（e.g. "regression_tables" 在文中 → 隐含引用 main_regression_table）
        path_anchor = {
            "regression_tables.json": "main_regression_table",
            "approved_findings.json": "approved_findings",
            "method_gate_report.json": "method_gate_report",
            "verified_bibliography.csv": "verified_bibliography.csv",
            "research_question.json": "research_question",
            "design_spec.json": "design_spec",
            "sample_profile.json": "dataset_profile",
            "robustness_matrix.json": "robustness_matrix",
            "limitations_register.json": "limitations_register",
            "domain_notes.json": "domain_notes",
            "literature_package_report.json": "literature_context",
        }
        # 中文别名 → evidence_id (支持中文学术写作的常见引用方式)
        cn_anchor: dict[str, str] = {
            "表 1": "main_regression_table",
            "表 2": "main_regression_table",
            "表 3": "main_regression_table",
            "表 4": "main_regression_table",
            "主回归表": "main_regression_table",
            "回归表": "main_regression_table",
            "approved": "approved_findings",
            "Bartik": "coefficient_interpretation",
            "移位-份额": "coefficient_interpretation",
        }
        for fname, eid_alias in path_anchor.items():
            if fname in text and eid_alias in section_bindings and eid_alias not in refs_found:
                refs_found.append(eid_alias)
        for cn_word, eid_alias in cn_anchor.items():
            if cn_word in text and eid_alias in section_bindings and eid_alias not in refs_found:
                refs_found.append(eid_alias)
        if len(refs_found) < min_refs:
            counter += 1
            dim.findings.append(AuditFinding(
                id=f"COMP-{counter:03d}",
                severity="BLOCKER",
                dimension=dim.name,
                what_was_found=f"`{section_name}.md` 只引用了 {len(refs_found)}/{len(section_bindings)} 个 bound evidence_id (minimum: {min_refs})",
                root_cause=f"该 section 已绑定 {len(section_bindings)} 个 evidence_id (见 manuscript_section_evidence_bindings.json)，但文中没有具体引用任何一个。",
                fix_action=(
                    f"在文中至少 {min_refs} 处显式引用绑定的 evidence_id 或其来源路径，例如：\n"
                    + "\n".join(f"  - `{eid}` → 引用 `{eid}.json` 路径或结果" for eid in section_bindings[:min_refs])
                ),
                downstream_impact="读者无法把该 section 与 evidence 关联；相当于凭空写作。",
                teaching_note="Bound evidence_id 是 contract：'该 section 必须用到这些 evidence'。不引用 = 违反合同。",
            ))

    if not dim.findings:
        dim.findings.append(AuditFinding(
            id="COMP-000", severity="INFO", dimension=dim.name,
            what_was_found=f"Section has {cn_chars} chinese chars (>= {min_chars}) and references {len(refs_found) if section_bindings else 'n/a'} bound evidence",
            root_cause="", fix_action="", downstream_impact="", teaching_note="",
        ))
    return dim


# ---------------------------------------------------------------------------
# Markdown 输出
# ---------------------------------------------------------------------------

def to_markdown(report: AuditReport) -> str:
    lines = [
        f"# Integrity Audit — `{report.section}`",
        "",
        f"- Section path: `{report.section_path}`",
        f"- Total findings: {report.total_findings}",
        f"- Gate verdict: {'**BLOCKED**' if report.blocked else '**READY**'}",
        "",
        "> 本审计教学式输出。每个 finding 含 6 字段：",
        "> severity | what_was_found | root_cause | fix_action | downstream_impact | teaching_note",
        "",
        "## Summary",
        "",
        "| Dimension | Status | Findings |",
        "|---|---|---|",
    ]
    for dim in report.dimensions:
        lines.append(f"| {dim.name} | {dim.status} | {len(dim.findings)} |")
    lines.append("")

    for dim in report.dimensions:
        if not dim.findings:
            continue
        lines.append(f"## {dim.name}")
        lines.append("")
        for f in dim.findings:
            if f.severity == "INFO":
                lines.append(f"**{f.id}** ✅ {f.what_was_found}")
                lines.append("")
                continue
            icon = "[BLOCKER]" if f.severity == "BLOCKER" else "[WARN]"
            lines.append(f"### {icon} {f.id} — {f.severity}")
            lines.append("")
            lines.append(f"**What was found:** {f.what_was_found}")
            lines.append("")
            lines.append(f"**Root cause:** {f.root_cause}")
            lines.append("")
            lines.append(f"**Fix:** {f.fix_action}")
            lines.append("")
            lines.append(f"**Downstream impact:** {f.downstream_impact}")
            lines.append("")
            if f.teaching_note:
                lines.append(f"**Why this matters:** {f.teaching_note}")
            lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def audit_section(project_root: Path, section_name: str) -> AuditReport:
    section_path = project_root / f"Manuscripts/sections/{section_name}.md"
    report = AuditReport(
        section=section_name,
        section_path=str(section_path.relative_to(project_root)) if section_path.exists() else "(missing)",
    )
    report.dimensions = [
        audit_required_files(project_root),
        audit_section_completeness(project_root, section_name),
        audit_number_anchoring(project_root, section_name),
        audit_forbidden_patterns(project_root, section_name),
        audit_source_of_truth_drift(project_root, section_name),
        audit_gap_honesty(project_root, section_name),
    ]
    return report


def main() -> int:
    p = argparse.ArgumentParser(description="Run evidence/integrity_audit.py (PaperSpine-style)")
    p.add_argument("--project-root", default=".", help="Project root (default: cwd)")
    p.add_argument("--section", default="main-results", help="Section name (default: main-results)")
    p.add_argument("--all", action="store_true", help="Audit every section under Manuscripts/sections/")
    p.add_argument("--markdown", action="store_true", help="Print markdown report to stdout")
    p.add_argument("--json", action="store_true", help="Print JSON report to stdout")
    p.add_argument("--write", action="store_true", help="Write integrity_audit.md next to the section")
    args = p.parse_args()

    project_root = Path(args.project_root).resolve()
    if not project_root.exists():
        print(f"Project root not found: {project_root}", file=sys.stderr)
        return 2

    sections_dir = project_root / "Manuscripts/sections"
    if not sections_dir.exists():
        print(f"Manuscripts/sections not found under {project_root}", file=sys.stderr)
        return 2

    if args.all:
        section_names = sorted(p.stem for p in sections_dir.glob("*.md"))
    else:
        section_names = [args.section]

    all_reports: list[AuditReport] = []
    for sn in section_names:
        all_reports.append(audit_section(project_root, sn))

    # 打印
    if args.json:
        out = []
        for r in all_reports:
            out.append({
                "section": r.section,
                "blocked": r.blocked,
                "total_findings": r.total_findings,
                "dimensions": [
                    {
                        "name": d.name,
                        "status": d.status,
                        "findings": [
                            {"id": f.id, "severity": f.severity, "what": f.what_was_found,
                             "root_cause": f.root_cause, "fix": f.fix_action,
                             "downstream": f.downstream_impact, "teaching": f.teaching_note}
                            for f in d.findings
                        ],
                    } for d in r.dimensions
                ],
            })
        print(json.dumps(out, ensure_ascii=False, indent=2))
    if args.markdown or not args.json:
        for r in all_reports:
            print(to_markdown(r))
            print()

    # 写文件
    if args.write:
        for r in all_reports:
            out_path = project_root / "evidence" / f"integrity_audit_{r.section}.md"
            out_path.write_text(to_markdown(r), encoding="utf-8")
            print(f"Wrote {out_path.relative_to(project_root)}", file=sys.stderr)

    # 退出码
    if any(r.blocked for r in all_reports):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
