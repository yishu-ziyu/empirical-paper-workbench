# 论文项目绘图方案 - 进度追踪

> 生成日期：2026-04-25
> 更新日期：2026-04-25
> 项目：工业机器人冲击下的劳动者重新配置
> 用途：为论文定稿制定完整绘图规范

---

## 一、项目整体进度

### 1.1 v2.1草稿完成度

| 模块 | 状态 | 说明 |
|------|------|------|
| 33个叶子小节 | ✅ 完成 | sections_v21/ |
| 摘要节（中英文） | ✅ 完成 | 00_摘要_中文.md |
| 三层框架整合 | ✅ 完成 | 2.2节各节已区分 |
| AI交接文档 | ✅ 完成 | AI_项目交接文档.md |
| 格式规范 | ✅ 完成 | 华侨大学经金学院本科论文格式规范.md |

### 1.2 待完成任务

| 任务 | 优先级 | 状态 |
|------|--------|------|
| 图片生成与优化 | ⭐⭐⭐ | 🔄 进行中 |
| v2.1 Word整合 | ⭐⭐⭐ | ⏳ 待开始 |
| 参考文献完善(GB7714-87) | ⭐⭐ | ⏳ 待开始 |
| 诚信承诺书 | ⭐⭐ | ⏳ 待开始 |
| 目录生成 | ⭐⭐ | ⏳ 待开始 |
| 文献补充(10篇) | ⭐⭐ | ⏳ 待开始 |

### 1.3 Git待推送

```
未追踪文件（需提交）:
- 04_paper/figures/FIGURE_PLAN.md
- 04_paper/figures/Fig2_Coefplot_Merged.png
- 04_paper/figures/Fig5_1_Coefplot_AllOutcomes.png
- 04_paper/figures/Fig5_5_Mechanism_Results.png
- 04_paper/figures/generate_figures.py

建议commit: "feat: 生成v2.1核心图片(Batch 1)"
```

---

## 二、图片放置位置（论文结构映射）

### 2.1 论文章节结构

```
第1章 绪论 (1.1-1.3)
第2章 文献综述 (2.1-2.3)
  └─ 2.2 三层框架（理论核心）
第3章 研究设计 (3.1-3.3)
第4章 数据与识别策略 (4.1-4.3)
  └─ 4.3.2 Bartik工具变量构造
第5章 实证结果 (5.1-5.3)
  └─ 5.1.1 工资回报、行业配置与职业层级 ← 核心结果图
  └─ 5.2.1 常规稳健性检验
  └─ 5.3.1 CLDS机制扩展结果 ← 机制图
第6章 结论与政策建议 (6.1-6.3)
```

### 2.2 图片-章节对照表

| 图片编号 | 文件名 | 放置章节 | 内容说明 | 状态 |
|---------|--------|---------|---------|------|
| 图2 | `Fig2_Coefplot_Merged.pdf` | 5.1.1 | OLS/RF/IV工资+制造业对比 | ✅ 已生成 |
| 图5-1 | `Fig5_1_Coefplot_AllOutcomes.pdf` | 5.1.1 | 四outcome系数对比(表5-1可视化) | ✅ 已生成 |
| 图5-5 | `Fig5_5_Mechanism_Results.pdf` | 5.3.1 | 六机制变量系数(表5-5可视化) | ✅ 已生成 |
| 图6 | `Fig6_Robustness_SpecCurve.pdf` | 5.2.1 | 稳健性规格曲线 | ⏳ 待生成 |
| 图9 | `Fig9_Bartik_Flowchart.pdf` | 4.3.2 | Bartik工具变量构造流程 | ⏳ 待生成 |
| 图框架 | `Fig_ThreeLayer_Framework.pdf` | 2.2节首 | 三层概念框架图 | ⏳ 待生成 |
| 图5 | `Fig5_IV_Distribution.pdf` | 4.3.3 | Bartik IV省级分布 | ⏳ 待优化 |

### 2.3 已废弃/待删除图片

| 文件名 | 原因 | 操作 |
|--------|------|------|
| `Fig1_Robot_Wage.png` | 描述性散点，非核心 | 🗑️ 删除 |
| `Fig3_Heterogeneity.png` | 重复，可并入其他图 | 🗑️ 删除 |
| `Fig4_SkillComplementarity.png` | 重复，可并入其他图 | 🗑️ 删除 |
| `Fig10_Polarization.png` | 可能重复 | 🗑️ 删除 |
| `Fig7_Correlation.png` | 热力图评估后决定 | ❓ 待评估 |
| `Fig8_Mechanism_Pathway.png` | 机制路径图可简化 | 🔄 简化 |
| `Fig_Pretrend_*.png` (6张) | 平行趋势检验 | 📦 整合 |

---

## 三、Batch执行进度

### 3.1 Batch 1 - 核心图（已完成 ✅）

| 序号 | 图片 | 输出文件 | 验证 |
|------|------|---------|------|
| 1 | 四outcome系数对比 | `Fig5_1_Coefplot_AllOutcomes.pdf/png` | ✅ |
| 2 | 机制系数对比 | `Fig5_5_Mechanism_Results.pdf/png` | ✅ |
| 3 | OLS/RF/IV合并图 | `Fig2_Coefplot_Merged.pdf/png` | ✅ |

### 3.2 Batch 2 - 定稿前（待执行）

| 序号 | 图片 | 说明 | 依赖 |
|------|------|------|------|
| 4 | 三层框架概念图 | 2.2节开头 | 无 |
| 5 | Fig6稳健性曲线 | 规格曲线风格 | 需Stata输出 |
| 6 | Fig9四步流程图 | Bartik构造简化 | 无 |

### 3.3 Batch 3 - 可选（待评估）

| 序号 | 图片 | 说明 |
|------|------|------|
| 7 | Fig7热力图 | 评估是否保留 |
| 8 | 预检验图整合 | 6张→1张 |

---

## 四、图片规格标准（学术规范）

### 4.1 技术规格

```
格式：PDF（向量）+ PNG（300DPI）
宽度：单栏6英寸（适合Word/LaTeX）
字体：Times New Roman（英文）+ Songti SC（中文）
配色：Ocean Dusk (#264653, #2A9D8F, #E76F51, #F4A261, #B0BEC5)
```

### 4.2 图表类型决策

| 数据特征 | 图表类型 | 适用图片 |
|---------|---------|---------|
| 3-5个估计量对比 | **水平柱状图+误差棒** | Fig5-1, Fig5-5 |
| 多outcome并列 | **分组柱状图** | Fig2 |
| 多规格稳健性 | **Specification Curve** | Fig6 |
| 地区分布 | **柱状图/箱线图** | Fig5 |
| 相关性结构 | **热力图** | Fig7 |
| 概念关系 | **文字箭头图** | Fig框架 |

---

## 五、生成脚本说明

### 5.1 脚本位置

```
04_paper/figures/generate_figures.py
```

### 5.2 使用方法

```bash
cd /Users/mahaoxuan/Desktop/学术灵感项目_2026-04-07/final/04_paper/figures
python3 generate_figures.py
```

### 5.3 依赖环境

- Python 3.8+
- matplotlib >= 3.5
- numpy >= 1.20
- macOS中文字体：Songti SC / Heiti TC

---

## 六、Git提交计划

### 6.1 待提交内容

```
文件变更：
A  04_paper/figures/FIGURE_PLAN.md (新增)
A  04_paper/figures/generate_figures.py (新增脚本)
A  04_paper/figures/Fig2_Coefplot_Merged.png (新图)
A  04_paper/figures/Fig5_1_Coefplot_AllOutcomes.png (新图)
A  04_paper/figures/Fig5_5_Mechanism_Results.png (新图)
```

### 6.2 提交信息

```
feat: 生成v2.1核心图片(Batch 1)

- Fig5_1: 四outcome系数对比图（表5-1可视化）
- Fig5_5: 六机制变量系数图（表5-5可视化）
- Fig2_Merged: OLS/RF/IV合并对比图
- FIGURE_PLAN.md: 图片规划与进度追踪
- generate_figures.py: 图片生成脚本
```

---

*本方案按Batch分批执行，确保图片与论文章节严格对应。*
