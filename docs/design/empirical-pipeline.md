# 实证是怎么做出来的：现状梳理（2026-09-24）

只读梳理，未改代码。目的：弄清一项实证研究在产品里从题目走到论文数字的全过程，找出哪里是通用的、哪里是按方法或按案例写死的，再决定怎么改，避免一个方法一个方法地打补丁。

## 结论

1. **方法知识散在各个阶段，没有集中的地方。** 识别核查、主估计、稳健性检验、代码导出、设定运行各自按方法分支、各自读设计字段、各自解析结果。支持一种方法要改 6 处左右；同一件事的几份实现会慢慢不一致。
2. **有几处写的是具体案例，不是通用逻辑。** 设计提议靠正则认出 Card-Krueger、“教育与工资”、Barro 这几个题目；研究台账把 `lwage`、`educ`、`nearc4` 写成常量；设定运行的第一阶段检验也写死了 `educ` / `nearc4`。
3. **最近发现的两个 bug 都是第 1 条的症状，不是孤立问题。** RD / SCM / CS 的主估计报告成功却没有系数：三套读结果的代码之一过时了。DiD 的 TWFE 分支算出了聚类变量却没传给估计：同一个设计字段，在不同阶段读法不同。

## 两条做实证的路径

```mermaid
flowchart TD
  subgraph A[正式流程：用户自己的研究]
    A1[题目 / 研究问题] --> A2[propose_design<br/>正则认题目 → 方法和变量]
    A2 --> A3[用户确认 session.design<br/>挂接数据]
    A3 --> A4[set_direction → DirectionSpec<br/>→ main_specification]
    A4 --> A5[identification_verify<br/>按方法分派诊断]
    A5 --> A6[estimate<br/>按方法分派；可选估计 Agent]
    A6 --> A7[robustness_check<br/>按方法分派一组检验]
    A7 --> A8[标题 / 大纲 / 逐章写作<br/>bind 把结果投进提示词]
    A8 --> A9[导出：translate_code 按方法翻译<br/>复现包按记录还原]
  end
  subgraph B[研究台账：Card 教学案例]
    B1[/demos/card] --> B2[设定空间<br/>OUTCOME=lwage、TREATMENT=educ、INSTRUMENT=nearc4]
    B2 --> B3[冻结 → 设定运行<br/>复用 _estimate_ols / _estimate_iv]
    B3 --> B4[比较、意外、主张批准 → 准备写论文]
  end
```

| 阶段 | 代码位置 | 在做什么 |
|---|---|---|
| 设计提议 | `agent/design/propose.py::propose_design` | 用正则匹配题目文字，决定方法与变量槽位；认不出就默认 OLS |
| 设计结构 | `agent/design/spec.py::DirectionSpec` | 事实上的“研究设计”：所有方法可能用到的字段平铺在一个对象里，再按方法拼成主设定 |
| 识别核查 | `agent/nodes/identification_verify.py::_DISPATCH` | DiD / IV / RD / SCM 各一个诊断函数 |
| 主估计 | `agent/nodes/estimate.py::_estimate_fixed` | 按方法分派到 StatsPAI；开关打开时先走估计 Agent |
| 稳健性 | `agent/nodes/robustness_check.py` | 每种方法一组检验（聚类、异质性、安慰剂、CS 等） |
| 写作投影 | `agent/engine/bind.py`、`readiness.py` | 把估计结果、估计器名称投进章节提示词 |
| 代码导出 | `agent/nodes/translate_code.py` | 按方法把分析翻译成 py / do / R / m |
| 复现包 | `backend/services/replication.py` | 按估计器在调用处写下的 `call` 还原（本次新增） |
| 研究台账 | `backend/services/research_lab.py`、`spec_run.py` | Card 专用的设定空间与运行 |

## 方法知识散落在哪里

横着看是一种方法，竖着看是一个阶段。每一格都是一段单独维护的代码。

| 阶段 \ 方法 | OLS | IV | DiD | RD | SCM |
|---|---|---|---|---|---|
| 读设计字段 | `to_main_specification` | 同左 + `_iv_formula` 两处 | 同左 + `did_spec`、`allow_did` | 同左 | 同左 |
| 识别核查 | — | `_diag_iv` | `_diag_did` | `_diag_rd` | `_diag_scm` |
| 主估计 | `_estimate_ols` + OLS 锁 | `_estimate_iv` | `_estimate_did`（3 个分支） | `_estimate_rd` | `_estimate_scm` |
| 稳健性 | 聚类 / 异质性 / 拒绝 | `_run_iv_battery` | 聚类 / CS 组 | `_run_rd_battery` | 安慰剂 |
| 读结果 | `effect_from_fit` | 同左 | 同左 | 同左 | 同左 |
| 稳健性里读结果 | `_coef_of` / `_se_of` / `_p_of`（另一套） | 同左 | 同左 | 同左 | 同左 |
| 代码导出 | `translate_code` 分支 | 同左 | 同左 | 同左 | 同左 |

读结果至少有三套实现：主估计的 `effect_from_fit`、稳健性检验的 `_coef_of` 一族、识别核查里各函数自己的读取。StatsPAI 的结果对象一变，它们会各自出问题。

同一个设计字段在不同地方的读法也不一致，例如时间列在一处读 `time`，另一处读 `time_col`，还有的两个都试；聚类在 DiD 的 TWFE 分支里被算出来，又没有传下去。

## 字段靠“补全所有拼写”维持一致

识别核查读原始研究方向 `research_direction`，主估计读整理后的 `main_specification`，两者不是同一个对象。正式流程先在 `formal_binding.align_direction` 里把方向规范化（结局与处理只留 `dv` / `iv`，工具变量只留复数 `instruments`），再由 `set_direction` 调用 `DirectionSpec.enrich_direction`，把每个字段的所有拼写（`outcome` / `outcome_col`、`instrument` / `instrument_col` 等）重新写回方向里，识别核查才读得到。

2026-09-24 按真实顺序（`align_direction` → `set_direction` → 识别核查）实测：IV、DiD、SCM、RD 的诊断都正常运行，均为 3 星。能用，但一致性靠“把所有别名都写一遍”维持：新增阶段只要用了没被覆盖的拼写，就会悄悄读不到字段。

更正：本节此前写过“正式流程里识别诊断基本没有运行”。那次实测跳过了 `set_direction`，结论错误，已撤回。

## 写死的案例知识

| 位置 | 写死了什么 | 影响 |
|---|---|---|
| `agent/design/propose.py` | Card-Krueger（最低工资、新泽西）→ DiD；“教育 + 工资”→ `schooling` / `wages`；Barro → 增长 | 只能认出这几个题目；其他研究一律退回 OLS、变量留空 |
| `backend/services/research_lab.py` | `OUTCOME="lwage"`、`TREATMENT="educ"`、`INSTRUMENT="nearc4"`、地区虚拟变量 | 设定空间、比较、意外判断只对 Card 成立，不能用于用户自己的数据 |
| `backend/services/spec_run.py` | 第一阶段检验 `endog="educ"`、`instruments=["nearc4"]` | 同上；这次已抽成常量并如实写进复现脚本，但仍是 Card 专用 |
| `agent/find_data/*`、`backend/services/allow_did.py` | `ck1994`、`barro`、`min_wage` 的特判 | 找数据与 DiD 放行规则里有案例分支 |

## 建议的方向（待你确认，尚未动手）

核心是把“一种方法需要知道的所有事”收拢到一处，各阶段只负责流程，不再各自懂方法。

**方法适配器**：每种方法一份，集中声明：

1. 需要哪些设计字段，以及它们的唯一读法（取代各处的别名猜测）；
2. 怎么生成估计调用，返回的就是 `call` 记录（估计、稳健性变体、复现包共用）；
3. 怎么从结果对象读出系数、标准误、p 值、样本量（全产品只此一处）；
4. 有哪些识别诊断，以及稳健性检验怎么由主调用变换得到；
5. 导出与写作时的名称和说明。

各阶段变成对适配器的通用循环：识别核查“跑这个方法声明的诊断”，稳健性“按声明变换主调用”，复现包“渲染记录”。

**案例知识退回数据**：研究台账的设定空间由已确认的设计生成（结局、处理、工具变量来自 `session.design`），Card 只是其中一份设计；设计提议改为根据研究问题与实际数据列推断，正则只作为可选的已知案例提示。

**落地顺序**（每步单独可验收，先不改变行为）：

1. 统一读结果与读设计字段：一个结果读取器、一个设计字段访问器，所有阶段改用它们；用现有测试加 RD / SCM / CS 的实跑测试守住行为不变。
2. 以 OLS、IV 为第一批做成适配器，主估计与设定运行改走适配器。
3. 识别核查、稳健性检验迁到适配器；此时 DiD 的聚类问题会作为“字段只读一次”的自然结果被修掉，而不是单独打补丁。
4. 研究台账按已确认的设计参数化，去掉 Card 常量。
5. 设计提议改为基于问题与数据列的推断。

## 进展

- 2026-09-24 第 1 步完成，未改变产品行为：
  - 读结果只剩一处：`agent/engine/results.py::read_effect`。主估计、稳健性检验、识别核查都改用它；`agent/tests/test_results_reader.py` 把四套旧读法原样复制为参照，在 feols、ivreg、statsmodels、rdrobust、synth、Callaway–Sant'Anna、密度检验的真实结果上逐值比对一致。
  - 读设计字段改用 `agent/design/fields.py::field`（规范名优先，只收纯拼写别名）。主估计、识别核查、稳健性检验、估计 Agent 已切换；`agent/tests/test_design_fields.py` 守住“生成方写出的各拼写取值相同”这一前提。
  - 尚未处理：研究方向的 `dv` / `iv` 词汇与主设定词汇并存（第 3 步识别核查改读主设定时解决）；`set_direction`、`DirectionSpec.from_direction`、研究台账里的读法。

