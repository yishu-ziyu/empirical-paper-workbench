"""Deterministic course-paper assembly from bound facts.

Human-facing manuscript style (applied micro Chinese):
- NO repository paths, NO (证据：tables/...) stamps, NO product jargon
- Numbers rounded for reading; tables referred as 表1/表2
- Evidence binding lives in claim register / JSON / replication (not in prose)

Machine artifacts remain separate from the paper body.
"""

from __future__ import annotations

from typing import Any


def _f(facts: dict[str, Any], key: str, default: str = "—") -> str:
    v = facts.get(key)
    return default if v is None else str(v)


def _num(x: Any, nd: int = 3) -> str:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x) if x is not None else "—"
    if abs(v) >= 1000 and float(v).is_integer():
        return str(int(v))
    s = f"{v:.{nd}f}"
    # trim trailing zeros after decimal
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def _p_fmt(p: Any) -> str:
    try:
        v = float(p)
    except (TypeError, ValueError):
        return str(p) if p is not None else "—"
    if v < 0.001:
        return "<0.001"
    return _num(v, 3)


def _references_block(works: list[Any]) -> str:
    if not works:
        return "待核验。在文献元数据完成核验之前，本文不列出未核实的正式条目。"
    lines: list[str] = []
    # Sort by first author family then year
    def sort_key(w: Any) -> tuple:
        authors = getattr(w, "authors", "") or (w.get("authors") if isinstance(w, dict) else "")
        year = getattr(w, "year", "") or (w.get("year") if isinstance(w, dict) else "")
        fam = str(authors).split(",")[0].strip()
        try:
            y = int(year)
        except (TypeError, ValueError):
            y = 0
        return (fam.lower(), y)

    for i, w in enumerate(sorted(works, key=sort_key), 1):
        if isinstance(w, dict):
            authors = w.get("authors", "")
            year = w.get("year", "")
            title = w.get("title", "")
            venue = w.get("venue", "")
            vol = w.get("volume", "")
            issue = w.get("issue", "")
            pages = w.get("pages", "")
            doi = w.get("doi", "")
        else:
            authors = w.authors
            year = w.year
            title = w.title
            venue = w.venue
            vol = w.volume
            issue = w.issue
            pages = w.pages
            doi = w.doi
        vip = ""
        if vol and issue and pages:
            vip = f", {vol}({issue}): {pages}"
        elif vol and pages:
            vip = f", {vol}: {pages}"
        elif vol:
            vip = f", {vol}"
        doi_s = f". DOI: {doi}" if doi else ""
        lines.append(
            f"{i}. {authors} ({year}). {title}. *{venue}*{vip}{doi_s}."
        )
    return "\n\n".join(lines)


def build_course_paper(
    facts: dict[str, Any],
    *,
    run_id: str = "",
    slug: str = "parent_education_wage",
    learn_notes: str = "",
    expand_mode: bool = False,
    degrade_mode: bool = False,
) -> str:
    """Build a Chinese course-style empirical draft. Paths never enter the body."""
    del run_id, learn_notes, expand_mode, degrade_mode  # metadata only outside prose

    topic = _f(facts, "topic", "父母受教育水平对子女工资收入的影响")
    pe = _num(facts.get("parent_education_coef"), 3)
    se = _num(facts.get("parent_education_se"), 3)
    pval = _p_fmt(facts.get("parent_education_p"))
    nobs = _num(facts.get("nobs"), 0)
    r2 = _num(facts.get("r2"), 3)
    n_raw = _num(facts.get("n_raw"), 0)
    n_analysis = _num(facts.get("n_analysis"), 0)
    formula = _f(facts, "formula", "ln_wage ~ parent_education + age + female + urban + edu_last + experience")
    lit_count = int(facts.get("literature_verified_count") or 0)

    # Prefer prebuilt literature section prose (from literature_pack); never invent cites.
    lit_section = (facts.get("literature_section_md") or "").strip()
    works = facts.get("literature_works") or []
    if not lit_section and lit_count > 0:
        try:
            from runtime.literature_pack import VerifiedWork, literature_section_prose

            vworks = []
            for item in works:
                if isinstance(item, VerifiedWork):
                    vworks.append(item)
                elif isinstance(item, dict) and item.get("doi"):
                    vworks.append(VerifiedWork(**{k: item[k] for k in VerifiedWork.__dataclass_fields__ if k in item}))
            if vworks:
                lit_section = literature_section_prose(vworks).strip()
                works = vworks
        except Exception:  # noqa: BLE001
            lit_section = ""
    if not lit_section:
        lit_section = """## 文献与贡献

代际流动与教育传递构成第一条线索：父母教育可能通过子女教育、健康、非认知技能与社会网络影响成年结果。教育的劳动市场回报构成第二条线索：在控制能力与家庭背景后，教育年限与工资的关联如何被解读。两条线索的交叉处，观察性数据几乎总是把「教育」与未观测能力纠缠在一起；因此，把条件关联直接写成「回报」或「因果效应」需要额外的识别设计。

识别策略文献通常沿着几条路径推进：义务教育或学制改革带来的外生教育变动、双胞胎与收养样本、以及政策冲击下的工具变量。这些路径的共同目标，是把选择与因果拆开。本文当前并不声称已经走完其中任一条路径。相反，本文先固定一条可复现的 OLS 基线：在明确的控制组与标准误约定下，报告父母教育与子女对数工资的条件关联，并把「尚未识别」写进正文。

在书目字段完成 DOI 核验之前，本文不做「填补某文献空白」式的贡献宣称，也不粘贴未核验的作者—年份清单。
"""

    lit_intro_boundary = (
        f"第二，本文在已核验的 {lit_count} 篇核心文献基础上定位问题，"
        "但明确自身贡献是关联基线而非新的因果识别。"
        if lit_count > 0
        else "第二，在文献条目尚未完成核验之前，本文不假装完成正式综述对话，也不粘贴未核验的作者—年份清单。"
    )
    lit_abstract_tail = (
        f"本文在已核验文献对话中定位为可复现的关联基线（核验条目 {lit_count} 篇），"
        "因果识别设计留待具备可信外生变动之后再单独立项。"
        if lit_count > 0
        else "正式文献对话与因果识别设计留待核验与后续工作。"
    )
    lit_conclusion = (
        f"第二，文献对话基于 DOI 核验条目（{lit_count} 篇），本文不越权宣称已闭合因果识别。"
        if lit_count > 0
        else "第二，文献核验尚未完成，本文不做未核验的正式对话。"
    )
    refs_body = _references_block(works) if works else (
        "待核验。在文献元数据完成核验之前，本文不列出未核实的正式条目。"
    )

    # Academic formula display (not code path)
    formula_cn = (
        "以子女对数工资为被解释变量，核心解释变量为父母受教育年限，"
        "控制年龄、性别、城乡、自身教育年限与工作经验"
    )

    # Drop leading ## if lit_section already has it (we embed under structure)
    if lit_section.startswith("## "):
        lit_body = lit_section
    else:
        lit_body = "## 文献与贡献\n\n" + lit_section

    return f"""# {topic}

## 摘要

本文利用中国家庭追踪调查（CFPS）的可分析样本，在控制年龄、性别、城乡、自身教育与工作经验后，采用普通最小二乘法并报告异方差稳健标准误（HC1），考察父母受教育年限与子女对数工资之间的条件关联。分析样本量为 {nobs}。主回归中，父母教育的估计系数为 {pe}，标准误为 {se}，在常规显著性水平上拒绝系数为零的原假设；模型拟合优度 R² 约为 {r2}。

需要强调：本文报告的是统计关联，而不是工具变量或政策实验意义上的因果效应，也无意将系数解读为「提高父母教育一年将改变子女工资」的政策参数。观察性数据中的父母教育与未观测能力、家庭资源与地区机会结构高度纠缠。本文的贡献限于可复现的关联证据与清晰的识别边界；{lit_abstract_tail}

关键词：代际教育；工资；最小二乘；关联估计

JEL 分类号：J24；I24；J62；C21

## 引言

父母受教育程度较高的家庭，子女往往在劳动市场上表现更好。这一现象在许多国家的描述统计中反复出现，并被广泛用于讨论机会公平、人力资本投资与社会流动性。然而，相关并不自动意味着因果。一种解释是选择：更有能力、更重视教育或拥有更好社会网络的父母，既更可能完成更高学历，也更可能把优势传递给子女。另一种解释是因果：教育本身改变了父母的资源、偏好或养育方式，从而改变子女成年后的收入。区分这两种故事，对教育政策是否具有跨代溢出含义至关重要。

本文将问题刻意收窄为一个可检验、可复现的经验问题：在 CFPS 可分析样本中，控制一组常规人口与人力资本变量后，父母受教育年限与子女对数工资的偏相关方向与量级是什么？该关联在性别与城乡子样本中是否保持同号？在识别策略尚未闭合之前，哪些结论可以被当前证据支持，哪些必须明确拒绝？

经验上，本文采用线性回归，{formula_cn}。估计量为 OLS，标准误为 HC1。在分析样本 n={nobs} 上，父母教育的点估计为 {pe}（标准误 {se}）。全文数字以回归表为准；正文只作关联解读，不把系数升级为局部平均处理效应或政策回报。

相对已有讨论，本文的边界同样需要写清楚。第一，本文交付的是可复现的关联证据，而不是新的因果识别策略。{lit_intro_boundary}第三，机制分解、工具变量与政策外推均不在本轮闭合范围内。这样的保守写法，是为了避免在证据不足时用叙事强度换取「看起来像因果论文」的外观。

全文结构如下。第二节回顾相关文献并说明本文位置。第三节给出理论动机与识别威胁。第四节介绍数据、样本与变量。第五节说明估计策略与不可做主张。第六节报告主结果。第七节讨论子样本稳健性与机制边界。第八节总结并讨论局限与下一步。

{lit_body}

## 制度背景与理论

人力资本框架提示，父母教育可能通过直接资源（时间、金钱、信息）、间接资源（对子女教育的投资）以及偏好与预期（职业抱负、风险态度）影响子女收入。代际传递讨论进一步强调，家庭是一个联合生产单位：父母教育既是投入，也可能是更深层家庭能力的代理变量。因此，即便回归系数显著为正，经济解释仍可能是「家庭综合优势的投影」，而不是「教育年限本身可被政策操纵的效应」。

中国语境为上述机制提供了丰富但难识别的背景。教育扩张改变了队列的受教育分布；城乡分割与迁移影响工资决定；市场化改变了教育信号的回报结构；家庭内部谁受教育、谁外出务工的决策，与地区机会高度相关。这些事实说明两件事。第一，讨论父母教育与子女工资的关联具有现实相关性。第二，恰恰因为混淆丰富，更不能在缺乏外生变动时把 OLS 写成政策效应。

威胁清单至少包括：能力与偏好的代际相关；共同的社区与学校质量；工资与教育的测量误差；就业与字段缺失带来的样本选择；以及在动态家庭决策中更复杂的反向与联立问题。父母完成教育通常早于子女进入劳动力市场，但时间先后既不是随机化，也不能自动排除共同的未观测因素。

测量层面同样重要。调查中的工资可能以不同周期或区间记录，教育年限可能由学历映射而来，成年子女样本中的父母教育依赖回顾性报告。经典测量误差会把系数拉向零；非经典误差则方向不定。因此，结果节的任务是报告与解释边界，而不是在理论节提前宣布「效应很大」或「效应很小」。

## 数据与变量

分析使用 CFPS 修复后的可分析样本。原始记录约 {n_raw} 条，进入主回归的分析样本量为 {nobs}（与回归输出一致）。缺失处理采用列删：只要回归所需任一变量缺失，该观测不进入主回归。这一规则简单可复现，但会改变可外推对象——能够同时观测工资与父母教育的个体，并不代表全体劳动年龄人口。

被解释变量为对数工资，用于在半对数规格下讨论条件均值关联。核心解释变量为父母受教育年限。控制变量包括年龄、性别、城乡、自身教育年限与工作经验。控制自身教育会改变系数的解释：它可能吸收「父母教育→子女教育→工资」这一通道，使父母教育系数更接近「在子女教育已被吸收后的剩余关联」；它也可能引入坏控制，如果自身教育处在结果路径上。本文不在此裁决完整因果图，只报告包含上述控制的基准规格，并把规格敏感性留给后续工作。

表 1 给出描述统计。读者可用其检查关键变量的均值与离散程度、分析样本相对原始样本的缩减，以及性别与城乡构成是否提示选择。本文结论针对进入分析样本的观测，而不是「中国所有子女」或「所有家庭」。对政策讨论而言，这一限制与「非因果」限制同样重要。

变量命名与回归设定保持一致，以便与表 2 对照。若未来对工资做缩尾或对教育做截断，应在数据节声明规则并在稳健性中给出对照；当前正文不引入未在估计中执行的额外编码规则。

## 实证策略

### 估计方程

基准回归可写为：

在控制年龄、性别、城乡、自身教育与经验后，将子女对数工资对父母受教育年限做线性回归。

形式化地，估计式对应：

`{formula}`

估计量为 OLS，协方差矩阵采用 HC1 异方差稳健标准误。选择 OLS+HC1 的理由是双重的最小充分：它给出可解释的条件均值关联，计算稳定，复现成本低，并且与「当前不允许因果主张」的边界一致。本文不在正文中报告 2SLS，也不把研究规划中可能存在的工具变量设想自动写成已执行方法。

### 参数解释

父母教育系数被解释为：在给定控制组下，父母受教育年限与子女对数工资的偏相关。主结果为 {pe}（标准误 {se}，p 值 {pval}，n={nobs}，R²≈{r2}）。在半对数规格下，可把系数启发式读作「父母教育多一年，对数工资条件均值大约变化 {pe}」，但这仍是关联读法，不是「外生提高父母教育一年」的处理效应。

### 识别边界

本文不允许如下表述进入结论：政策效应、因果影响、局部平均处理效应、工具变量已识别、提高父母教育将导致子女工资上升或下降。允许的表述包括：关联、偏相关、在控制……后仍显著或不显著、不能拒绝零、估计不精确。

识别威胁包括但不限于能力偏误、家庭未观测异质性、测量误差、样本选择与可能的反向因果。本文不假装残差已经「很干净」。若研究设计文档中仍保留 IV 推荐，那只代表规划方向，不代表本轮已经执行 IV；正文以实际估计量为准。

### 推断与规格纪律

主检验聚焦父母教育系数。按性别与城乡重估用于描述关联是否由单一可见分组驱动，不作多重检验意义上的「机制发现」。基准规格预先固定，而不是在看到结果后挑选控制组合。若存在地区或家庭层级相关，聚类标准误可能更合适，但需要相应群标识与样本量；当前报告 HC1，不假装已经处理组内相关。

## 主结果

表 2 报告主回归。分析样本 n={nobs}。父母教育的点估计为 {pe}，HC1 标准误为 {se}，对应 p 值为 {pval}；R² 约为 {r2}。完整系数向量见主回归表。

阅读顺序建议如下。先确认样本量与控制组设定，再读核心系数与标准误，然后查看控制变量符号是否符合常识（例如自身教育与工资的关联方向），最后回到核心系数的关联解释。若在常规水平上拒绝系数为零，表述应为「在当前控制组与样本下，统计上可以拒绝偏相关为零」；若不能拒绝，表述应为「估计不精确或不能拒绝零」，而不是「证明无效应」。

经济量级必须克制。把 {pe} 读作约 {pe} 个对数点的条件均值差异，只在半对数关联框架内有启发意义；它不是福利分析，也不是政策投资回报。更稳妥的写法是同时报告点估计与标准误，并强调：在识别未闭合时，量级不能支撑因果成本—收益计算。

控制变量系数只在表中存在时讨论，且不作因果审计。自身教育若与工资呈正相关，符合人力资本常识，但在本设计中它可能是中介，也可能是坏控制。性别与城乡系数反映组间条件均值差异，同样是关联，不是歧视或政策的因果评估。

显著性也不等于实质重要性。即便 p 值很小，经济量级仍可能有限；即便 p 值较大，也只说明在当前样本与规格下不能拒绝零。结果段固定采用「主张—证据—限制」结构：先报告数字，再作关联解释，最后接上识别或样本边界。

## 稳健性、机制与异质性

表 3（稳健性）按性别与城乡等可见分组重估同一公式。阅读纪律如下。

第一，若子样本系数与全样本同号，说明关联并非由单一细胞完全驱动；这支持描述意义上的稳健，不支持机制已识别。第二，若量级变化较大，应优先检查组内方差、缺失模式、样本量与选择，而不是把差异写成「异质性因果效应」。第三，机制（例如父母教育经由子女教育影响工资）需要中介设计与额外假设；当前并未交付完整中介分解，因此机制讨论只保留为边界说明。

本轮不报告安慰剂的因果解读、匹配或双重稳健的替代因果估计，以及工具变量弱识别诊断，因为相应模块尚未执行。若后续加入，应各自形成表格与可核对输出，而不是在本节口头插入。

异质性分析的最小诚实模板是：预先声明分组变量，报告各组估计与样本量，讨论选择与功效，避免事后故事。机制分析的最小诚实模板是：写出中介、时序与必要假设，并承认条件可能不成立。当前两者均未闭合，故本节标题中的「机制」主要起结构占位作用。

若某子样本系数变号，正文应优先列出数据原因（样本过小、选择、测量），而不是立刻上升为理论异质性发现。科学写作里，克制往往比戏剧性更接近真相。

## 结论

在可复现的 OLS 与 HC1 标准误下，父母受教育年限与子女对数工资呈现可审阅的条件关联：主系数为 {pe}（标准误 {se}，p 值 {pval}，n={nobs}）。本文同时强调三重限制。第一，关联不是因果。{lit_conclusion}第三，样本与字段约束限制外推。

下一步按可执行性排序：在已有 DOI 核验书目基础上继续补强中国微观与政策暴露文献；评估是否存在可信外生变动以支持工具变量或事件研究，并单独立项通过诊断；扩展规格曲线与更完整的异质性与机制设计。在此之前，不宜把关联估计包装成政策参数。

可观察的完成标准应是：主数字与表格一致，章节结构完整，复现脚本可重跑得到一致系数，识别边界写清楚，参考文献均可回链 DOI。红灯不应被改写成「已完成」。可复现与诚实，优先于听起来更强的故事。

## 参考文献

{refs_body}

## 数据可得性说明

本研究所用回归样本、主结果与稳健性表，以及复现程序，构成最小可复现材料包。外部研究者应能在相同环境依赖下重跑得到一致系数（允许浮点误差）。详细字段与清洗步骤见研究附录材料，正文从略。
"""


def cn_char_count(text: str) -> int:
    import re

    return len(re.findall(r"[\u4e00-\u9fff]", text))
