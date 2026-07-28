"""ADR-0004 Stage 3: mock 文献库。

含 30 条经济学顶刊条目，覆盖劳动 / 发展 / 公共 / 计量 / 宏观 5 个子领域
（每个子领域 6 条），中英文混合（标题英文，摘要中文）。
用于 search_literature 节点的 mock 检索源。

设计要点：
- 每条含 title/authors/year/abstract/doi/source/relevance_score
- 默认 relevance_score=0.5；filter_by_query 按匹配度调整
- DOI 格式合理（如 10.1016/j.jceco.2023.001）
- abstract 用中文描述（20-50 字），含子领域关键词便于相关性匹配
"""
from typing import List

from protocols import LiteratureEntry


def mock_literature_corpus() -> List[LiteratureEntry]:
    """返回完整 mock 文献库（30 条）。

    覆盖 5 个子领域：劳动 / 发展 / 公共 / 计量 / 宏观，每个 6 条。
    """
    return [
        # ------------------------------------------------------------------
        # 劳动经济学（6 条）
        # ------------------------------------------------------------------
        LiteratureEntry(
            title="Returns to Education in Urban China",
            authors=["Zhang, Junsen", "Zhao, Yaohui"],
            year=2023,
            abstract="利用 CHNS 数据估计城镇教育回报率，劳动经济学实证研究。",
            doi="10.1016/j.jceco.2023.001",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Minimum Wage Effects on Employment",
            authors=["Card, David", "Krueger, Alan"],
            year=2022,
            abstract="自然实验估计最低工资对就业的影响，劳动经济学经典议题。",
            doi="10.1016/j.labeco.2022.002",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Gender Wage Gap in China's Labor Market",
            authors=["Li, Shi", "Song, Jin"],
            year=2021,
            abstract="分析中国劳动市场性别工资差异，IV 工具变量识别因果。",
            doi="10.1016/j.labeco.2021.003",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Informal Employment and Social Insurance",
            authors=["Heckman, James", "Pages, Carmen"],
            year=2020,
            abstract="研究非正规就业与社保覆盖关系，劳动经济学政策评估。",
            doi="10.1016/j.jde.2020.004",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Migration and Urban Wage Premium",
            authors=["Zhou, Liqun", "Xie, Yu"],
            year=2022,
            abstract="DID 双重差分估计劳动力迁移的城市工资溢价，劳动经济学。",
            doi="10.1016/j.jceco.2022.005",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Automation and Job Displacement",
            authors=["Acemoglu, Daron", "Restrepo, Pascual"],
            year=2023,
            abstract="自动化技术对劳动就业的替代效应，劳动经济学前沿研究。",
            doi="10.1016/j.labeco.2023.006",
            source="mock",
            relevance_score=0.5,
        ),

        # ------------------------------------------------------------------
        # 发展经济学（6 条）
        # ------------------------------------------------------------------
        LiteratureEntry(
            title="Microfinance and Poverty Alleviation",
            authors=["Banerjee, Abhijit", "Duflo, Esther"],
            year=2022,
            abstract="随机对照试验评估小额信贷扶贫效果，发展经济学经典。",
            doi="10.1016/j.jdeveco.2022.007",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Education Subsidies in Rural China",
            authors=["Chen, Yuyu", "Li, Hongbin"],
            year=2021,
            abstract="RDD 断点回归评估农村教育补贴政策，发展经济学实证。",
            doi="10.1016/j.jdeveco.2021.008",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Health Insurance and Rural Welfare",
            authors=["Wang, Hui", "Yu, Yiran"],
            year=2023,
            abstract="DID 估计新农合对农村居民健康福利的影响，发展经济学。",
            doi="10.1016/j.jdeveco.2023.009",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Land Reform and Agricultural Productivity",
            authors=["Besley, Timothy", "Burgess, Robin"],
            year=2020,
            abstract="土地改革对农业生产率的影响，发展经济学制度分析。",
            doi="10.1016/j.jdeveco.2020.010",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Conditional Cash Transfers and Schooling",
            authors=["Schultz, T. Paul"],
            year=2022,
            abstract="条件现金转移对教育入学的影响，发展经济学政策评估。",
            doi="10.1016/j.jdeveco.2022.011",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Infrastructure Investment and Regional Growth",
            authors=["Banerjee, Abhijit", "Duflo, Esther"],
            year=2023,
            abstract="IV 工具变量识别基础设施投资的区域增长效应，发展经济学。",
            doi="10.1016/j.jdeveco.2023.012",
            source="mock",
            relevance_score=0.5,
        ),

        # ------------------------------------------------------------------
        # 公共经济学（6 条）
        # ------------------------------------------------------------------
        LiteratureEntry(
            title="Tax Incentives and Firm Investment",
            authors=["Zwick, Eric", "Mahon, James"],
            year=2022,
            abstract="DID 估计税收激励对企业投资的刺激作用，公共经济学实证。",
            doi="10.1016/j.jpubeco.2022.013",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="VAT Reform and Enterprise Productivity",
            authors=["Liu, Yongzheng", "Mao, Jie"],
            year=2021,
            abstract="增值税改革对企业生产率的影响，IV 工具变量识别，公共经济学。",
            doi="10.1016/j.jpubeco.2021.014",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Environmental Tax and Emissions",
            authors=["Goulder, Lawrence", "Schein, Robert"],
            year=2023,
            abstract="环境税对污染排放的减排效果，DID 识别，公共经济学政策评估。",
            doi="10.1016/j.jpubeco.2023.015",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Intergovernmental Transfers and Local Spending",
            authors=["Gordon, Roger", "Li, Wei"],
            year=2020,
            abstract="政府间转移支付对地方公共支出的影响，公共经济学实证。",
            doi="10.1016/j.jpubeco.2020.016",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Property Tax and Housing Market",
            authors=["Mieszkowski, Peter", "Toder, Eric"],
            year=2022,
            abstract="房产税对住房市场的影响，IV 工具变量识别，公共经济学。",
            doi="10.1016/j.jpubeco.2022.017",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Social Security and Retirement Savings",
            authors=["Feldstein, Martin"],
            year=2021,
            abstract="社保制度对家庭储蓄的挤出效应，DID 识别，公共经济学。",
            doi="10.1016/j.jpubeco.2021.018",
            source="mock",
            relevance_score=0.5,
        ),

        # ------------------------------------------------------------------
        # 计量经济学（6 条）
        # ------------------------------------------------------------------
        LiteratureEntry(
            title="Difference-in-Differences with Staggered Treatment",
            authors=["Callaway, Brantly", "Sant'Anna, Pedro"],
            year=2022,
            abstract="交错处理下的 DID 双重差分估计量，计量经济学方法贡献。",
            doi="10.1016/j.jeconom.2022.019",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Instrumental Variables and Weak Instruments",
            authors=["Stock, James", "Yogo, Motohiro"],
            year=2021,
            abstract="弱工具变量检验与 IV 估计的稳健性，计量经济学方法研究。",
            doi="10.1016/j.jeconom.2021.020",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Regression Discontinuity Designs",
            authors=["Lee, David", "Lemieux, Thomas"],
            year=2020,
            abstract="RDD 断点回归设计的识别假设与稳健性，计量经济学方法论。",
            doi="10.1016/j.jeconom.2020.021",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Synthetic Control Methods",
            authors=["Abadie, Alberto", "Gardeazabal, Javier"],
            year=2023,
            abstract="合成控制法作为 DID 的稳健性补充，计量经济学识别策略。",
            doi="10.1016/j.jeconom.2023.022",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Panel Data Fixed Effects",
            authors=["Wooldridge, Jeffrey", "Imbens, Guido"],
            year=2022,
            abstract="面板数据固定效应模型的内生性处理，计量经济学方法。",
            doi="10.1016/j.jeconom.2022.023",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="High-Dimensional Covariates in Regression",
            authors=["Belloni, Alexandre", "Chernozhukov, Victor"],
            year=2021,
            abstract="高维协变量下的 IV 与双重机器学习，计量经济学前沿方法。",
            doi="10.1016/j.jeconom.2021.024",
            source="mock",
            relevance_score=0.5,
        ),

        # ------------------------------------------------------------------
        # 宏观经济学（6 条）
        # ------------------------------------------------------------------
        LiteratureEntry(
            title="Monetary Policy and Inflation Dynamics",
            authors=["Gali, Jordi", "Gertler, Mark"],
            year=2022,
            abstract="货币政策传导与通胀动态，宏观经济学 DSGE 实证研究。",
            doi="10.1016/j.jmoneco.2022.025",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Fiscal Multipliers in Recession",
            authors=["Blanchard, Olivier", "Leigh, Daniel"],
            year=2021,
            abstract="衰退期财政乘数估计，IV 工具变量识别，宏观经济学实证。",
            doi="10.1016/j.jmoneco.2021.026",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Housing Prices and Business Cycles",
            authors=["Iacoviello, Matteo", "Pavan, Stefano"],
            year=2023,
            abstract="房价波动与经济周期关联，DID 识别，宏观经济学研究。",
            doi="10.1016/j.jmoneco.2023.027",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Technology Shocks and Productivity",
            authors=["Comin, Diego", "Gertler, Mark"],
            year=2020,
            abstract="技术冲击与生产率波动的内生性，宏观经济学实证分析。",
            doi="10.1016/j.jmoneco.2020.028",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Unemployment and Job Creation Flow",
            authors=["Mortensen, Dale", "Pissarides, Christopher"],
            year=2022,
            abstract="失业与岗位创造搜寻匹配模型，宏观经济学劳动市场分析。",
            doi="10.1016/j.jmoneco.2022.029",
            source="mock",
            relevance_score=0.5,
        ),
        LiteratureEntry(
            title="Exchange Rate Pass-through",
            authors=["Burstein, Ariel", "Gopinath, Gita"],
            year=2023,
            abstract="汇率传导机制与通胀内生性，IV 工具变量识别，宏观经济学。",
            doi="10.1016/j.jmoneco.2023.030",
            source="mock",
            relevance_score=0.5,
        ),
    ]


def filter_by_query(
    entries: List[LiteratureEntry], query: str
) -> List[LiteratureEntry]:
    """按查询关键词过滤文献（mock 相关性匹配）。

    匹配规则：title 或 abstract 包含 query 中任一关键词 → 命中
    命中条目数越多，relevance_score 越高：
        relevance_score = min(1.0, 0.3 + 0.2 * match_count)
    未命中的条目不返回。

    Args:
        entries: 完整文献库
        query: 空格分隔的检索查询（如 "劳动 教育"）

    Returns:
        命中的文献条目列表（relevance_score 已按命中数调整）
    """
    if not query:
        return entries

    keywords = [k.strip().lower() for k in query.split() if len(k.strip()) > 1]
    if not keywords:
        return entries

    filtered: List[LiteratureEntry] = []
    for e in entries:
        title = (e.get("title", "") or "").lower()
        abstract = (e.get("abstract", "") or "").lower()
        match_count = sum(
            1 for kw in keywords if kw in title or kw in abstract
        )
        if match_count > 0:
            adjusted = dict(e)
            adjusted["relevance_score"] = min(1.0, 0.3 + 0.2 * match_count)
            filtered.append(adjusted)

    return filtered
