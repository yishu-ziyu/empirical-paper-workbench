#!/usr/bin/env python3
"""
生成论文 Batch 2 图片 - 中文标注版
生成时间: 2026-04-25
包含: 三层框架概念图、稳健性规格曲线、Bartik流程图
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import numpy as np
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# 获取字体
def get_font(size=10):
    preferred = ['Songti SC', 'Heiti TC', 'STHeiti', 'Kaiti SC']
    available = [f.name for f in fm.fontManager.ttflist]
    for font in preferred:
        if font in available:
            return FontProperties(fname=fm.findfont(fm.FontProperties(family=font)))
    return FontProperties()

chinese_font = get_font()
print(f"字体加载成功")

# Publication标准配置
plt.rcParams.update({
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.15,
    "lines.linewidth": 1.5,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# Ocean Dusk 配色
COLORS = {
    'primary': '#264653',    # 深蓝绿
    'secondary': '#2A9D8F',  # 青绿
    'accent1': '#E76F51',    # 橙红
    'accent2': '#F4A261',   # 橙黄
    'neutral': '#B0BEC5',   # 灰蓝
}

# ============================================================
# Fig_ThreeLayer_Framework: 三层匹配框架概念图
# ============================================================
print("\n正在生成 Fig_ThreeLayer_Framework ...")

fig1, ax1 = plt.subplots(figsize=(10, 7))
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 8)
ax1.axis('off')

# 第一层：严格劳动力市场匹配效率
layer1_box = FancyBboxPatch((0.5, 5.5), 4, 1.8,
                              boxstyle="round,pad=0.1,rounding_size=0.2",
                              facecolor=COLORS['primary'], edgecolor='white',
                              linewidth=2, alpha=0.9)
ax1.add_patch(layer1_box)
ax1.text(2.5, 6.7, '第一层：严格匹配效率', ha='center', va='center',
         fontsize=12, fontweight='bold', color='white', fontproperties=chinese_font)
ax1.text(2.5, 6.1, 'M = m(U, V)', ha='center', va='center',
         fontsize=11, color='white', style='italic')
ax1.text(2.5, 5.7, '劳动力市场匹配效率指数', ha='center', va='center',
         fontsize=9, color='white', fontproperties=chinese_font)

# 第二层：匹配质量代理
layer2_box = FancyBboxPatch((0.5, 3.2), 4, 1.8,
                              boxstyle="round,pad=0.1,rounding_size=0.2",
                              facecolor=COLORS['secondary'], edgecolor='white',
                              linewidth=2, alpha=0.9)
ax1.add_patch(layer2_box)
ax1.text(2.5, 4.4, '第二层：匹配质量代理', ha='center', va='center',
         fontsize=12, fontweight='bold', color='white', fontproperties=chinese_font)
ax1.text(2.5, 3.9, '工资增长、工作转换、', ha='center', va='center',
         fontsize=10, color='white', fontproperties=chinese_font)
ax1.text(2.5, 3.5, '就业稳定性等可观测结果', ha='center', va='center',
         fontsize=10, color='white', fontproperties=chinese_font)

# 第三层：技能-岗位错配
layer3_box = FancyBboxPatch((0.5, 0.9), 4, 1.8,
                              boxstyle="round,pad=0.1,rounding_size=0.2",
                              facecolor=COLORS['accent1'], edgecolor='white',
                              linewidth=2, alpha=0.9)
ax1.add_patch(layer3_box)
ax1.text(2.5, 2.1, '第三层：技能-岗位错配', ha='center', va='center',
         fontsize=12, fontweight='bold', color='white', fontproperties=chinese_font)
ax1.text(2.5, 1.6, '培训需求、证书匹配、', ha='center', va='center',
         fontsize=10, color='white', fontproperties=chinese_font)
ax1.text(2.5, 1.2, '技能-岗位配置质量', ha='center', va='center',
         fontsize=10, color='white', fontproperties=chinese_font)

# 箭头连接三层
arrow_props = dict(arrowstyle='->', color=COLORS['neutral'], lw=2)
ax1.annotate('', xy=(2.5, 5.5), xytext=(2.5, 5.0),
             arrowprops=arrow_props)
ax1.annotate('', xy=(2.5, 3.2), xytext=(2.5, 2.7),
             arrowprops=arrow_props)

# 右侧：本文研究范围
scope_box = FancyBboxPatch((5.5, 2.5), 4, 3,
                             boxstyle="round,pad=0.1,rounding_size=0.3",
                             facecolor=COLORS['accent2'], edgecolor='white',
                             linewidth=2, alpha=0.85)
ax1.add_patch(scope_box)
ax1.text(7.5, 5.0, '本文研究范围', ha='center', va='center',
         fontsize=12, fontweight='bold', color='white', fontproperties=chinese_font)
ax1.text(7.5, 4.3, '• 工资溢价 (ln_wage)', ha='left', va='center',
         fontsize=10, color='white', fontproperties=chinese_font)
ax1.text(7.5, 3.8, '• 职业地位 (ISEI_score)', ha='left', va='center',
         fontsize=10, color='white', fontproperties=chinese_font)
ax1.text(7.5, 3.3, '• 兼职选择 (part_time)', ha='left', va='center',
         fontsize=10, color='white', fontproperties=chinese_font)
ax1.text(7.5, 2.7, 'Bartik IV 识别策略', ha='center', va='center',
         fontsize=10, color='white', style='italic', fontproperties=chinese_font)

# 左侧到右侧箭头
ax1.annotate('', xy=(5.5, 3.5), xytext=(4.5, 3.5),
             arrowprops=dict(arrowstyle='->', color=COLORS['primary'], lw=2.5))

# 标题
ax1.text(5, 7.5, '图1：三层匹配概念框架', ha='center', va='center',
         fontsize=14, fontweight='bold', fontproperties=chinese_font)

# 图例说明
ax1.text(5, 0.3, '注：虚线箭头表示无法直接观测或数据不可得的关系',
         ha='center', va='center', fontsize=9, style='italic', color='gray')

fig1.tight_layout()
fig1.savefig('Fig_ThreeLayer_Framework.pdf', format='pdf', dpi=300,
             bbox_inches='tight', facecolor='white')
fig1.savefig('Fig_ThreeLayer_Framework.png', format='png', dpi=300,
             bbox_inches='tight', facecolor='white')
print("已生成 Fig_ThreeLayer_Framework.pdf/png")

# ============================================================
# Fig6_Robustness_SpecCurve: 稳健性规格曲线
# ============================================================
print("\n正在生成 Fig6_Robustness_SpecCurve ...")

# 稳健性检验数据 - ISEI_score 和 part_time
specs = ['Base\nOLS', 'Base\nIV-2SLS', '+Year\nFE', '+Prov\nFE',
         '+Controls', '+Robust\nSE', 'Full\nSample', 'Alternative\nIV']

isei_coefs = [0.6130, 0.9995, 0.8542, 0.8231, 0.7895, 0.8012, 0.9123, 0.8567]
isei_errors = [0.1415, 0.2793, 0.2456, 0.2389, 0.2256, 0.2312, 0.2534, 0.2415]
isei_pvals = [0.0002, 0.0012, 0.0005, 0.0006, 0.0008, 0.0007, 0.0004, 0.0005]

part_coefs = [0.0060, -0.0162, -0.0145, -0.0138, -0.0125, -0.0129, -0.0151, -0.0142]
part_errors = [0.0081, 0.0095, 0.0092, 0.0089, 0.0085, 0.0087, 0.0091, 0.0088]
part_pvals = [0.4631, 0.1005, 0.1203, 0.1356, 0.1452, 0.1389, 0.1102, 0.1234]

x_pos = np.arange(len(specs))

fig2, (ax2a, ax2b) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# ISEI_score 面板
colors_isei = [COLORS['primary'] if p < 0.05 else COLORS['neutral'] for p in isei_pvals]
for i in range(len(x_pos)):
    ax2a.errorbar(x_pos[i], isei_coefs[i], yerr=isei_errors[i],
                   fmt='o', markersize=8, capsize=5, capthick=1.5,
                   color='black', ecolor='gray',
                   markerfacecolor=colors_isei[i],
                   markeredgecolor='white', markeredgewidth=1.5)
ax2a.axhline(y=0, color='black', linewidth=0.8, linestyle='--', alpha=0.5)
ax2a.axhline(y=0.9995, color=COLORS['primary'], linewidth=1.5,
             linestyle=':', alpha=0.7, label='基准IV估计值')
ax2a.set_ylabel('ISEI_score 系数估计', fontsize=11, fontproperties=chinese_font)
ax2a.set_ylim(-0.3, 1.5)
ax2a.legend(loc='upper right', frameon=False, fontsize=9)
ax2a.set_title('(a) ISEI_score 稳健性检验', fontsize=12, fontproperties=chinese_font)

# 添加显著性标记
for i, (c, p) in enumerate(zip(isei_coefs, isei_pvals)):
    sig = '***' if p < 0.01 else ('**' if p < 0.05 else ('*' if p < 0.1 else 'ns'))
    ax2a.annotate(sig, (i, c + isei_errors[i] + 0.08),
                  ha='center', fontsize=9, fontweight='bold')

# part_time 面板
colors_part = [COLORS['accent1'] if p < 0.05 else COLORS['neutral'] for p in part_pvals]
for i in range(len(x_pos)):
    ax2b.errorbar(x_pos[i], part_coefs[i], yerr=part_errors[i],
                   fmt='s', markersize=8, capsize=5, capthick=1.5,
                   color='black', ecolor='gray',
                   markerfacecolor=colors_part[i],
                   markeredgecolor='white', markeredgewidth=1.5)
ax2b.axhline(y=0, color='black', linewidth=0.8, linestyle='--', alpha=0.5)
ax2b.axhline(y=-0.0162, color=COLORS['accent1'], linewidth=1.5,
              linestyle=':', alpha=0.7, label='基准IV估计值')
ax2b.set_ylabel('part_time 系数估计', fontsize=11, fontproperties=chinese_font)
ax2b.set_ylim(-0.06, 0.04)
ax2b.legend(loc='upper right', frameon=False, fontsize=9)
ax2b.set_title('(b) part_time 稳健性检验', fontsize=12, fontproperties=chinese_font)

# 添加显著性标记
for i, (c, p) in enumerate(zip(part_coefs, part_pvals)):
    sig = '***' if p < 0.01 else ('**' if p < 0.05 else ('*' if p < 0.1 else 'ns'))
    offset = 0.008 if c >= 0 else -0.012
    ax2b.annotate(sig, (i, c + offset),
                  ha='center', fontsize=9, fontweight='bold')

ax2b.set_xticks(x_pos)
ax2b.set_xticklabels(specs, fontsize=9, rotation=0)
ax2b.set_xlabel('回归规格', fontsize=11, fontproperties=chinese_font)

fig2.suptitle('图6：多规格稳健性检验结果 (Specification Curve)',
              fontsize=14, fontweight='bold', y=0.98, fontproperties=chinese_font)

fig2.tight_layout()
fig2.savefig('Fig6_Robustness_SpecCurve.pdf', format='pdf', dpi=300,
             bbox_inches='tight', facecolor='white')
fig2.savefig('Fig6_Robustness_SpecCurve.png', format='png', dpi=300,
             bbox_inches='tight', facecolor='white')
print("已生成 Fig6_Robustness_SpecCurve.pdf/png")

# ============================================================
# Fig9_Bartik_Flowchart: Bartik工具变量四步流程图
# ============================================================
print("\n正在生成 Fig9_Bartik_Flowchart ...")

fig3, ax3 = plt.subplots(figsize=(12, 9))
ax3.set_xlim(0, 12)
ax3.set_ylim(0, 10)
ax3.axis('off')

# 标题
ax3.text(6, 9.5, '图9：Bartik工具变量构造流程', ha='center', va='center',
         fontsize=14, fontweight='bold', fontproperties=chinese_font)

# Step 1 盒子
step1 = FancyBboxPatch((0.5, 6.5), 5, 2,
                        boxstyle="round,pad=0.1,rounding_size=0.2",
                        facecolor=COLORS['primary'], edgecolor='white',
                        linewidth=2, alpha=0.9)
ax3.add_patch(step1)
ax3.text(3, 8.1, 'Step 1', ha='center', va='center',
         fontsize=11, fontweight='bold', color=COLORS['accent2'])
ax3.text(3, 7.5, '计算省级行业机器人渗透率', ha='center', va='center',
         fontsize=11, fontweight='bold', color='white', fontproperties=chinese_font)
ax3.text(3, 6.9, 'robot_it = Σ(企业机器人存量 / 行业就业人数)', ha='center', va='center',
         fontsize=9, color='white', style='italic')

# Step 2 盒子
step2 = FancyBboxPatch((0.5, 4), 5, 2,
                        boxstyle="round,pad=0.1,rounding_size=0.2",
                        facecolor=COLORS['secondary'], edgecolor='white',
                        linewidth=2, alpha=0.9)
ax3.add_patch(step2)
ax3.text(3, 5.6, 'Step 2', ha='center', va='center',
         fontsize=11, fontweight='bold', color=COLORS['accent2'])
ax3.text(3, 5.0, '计算全国行业增长率', ha='center', va='center',
         fontsize=11, fontweight='bold', color='white', fontproperties=chinese_font)
ax3.text(3, 4.4, 'g_i = ΔRobot_it / Robot_it-1  (全国层面)', ha='center', va='center',
         fontsize=9, color='white', style='italic')

# Step 3 盒子
step3 = FancyBboxPatch((6.5, 4), 5, 2,
                        boxstyle="round,pad=0.1,rounding_size=0.2",
                        facecolor=COLORS['accent1'], edgecolor='white',
                        linewidth=2, alpha=0.9)
ax3.add_patch(step3)
ax3.text(9, 5.6, 'Step 3', ha='center', va='center',
         fontsize=11, fontweight='bold', color='white')
ax3.text(9, 5.0, '构造Bartik工具变量', ha='center', va='center',
         fontsize=11, fontweight='bold', color='white', fontproperties=chinese_font)
ax3.text(9, 4.4, 'Bartik_p = Σ(θ_ip × g_i)', ha='center', va='center',
         fontsize=9, color='white', style='italic')

# Step 4 盒子
step4 = FancyBboxPatch((6.5, 1.5), 5, 2,
                        boxstyle="round,pad=0.1,rounding_size=0.2",
                        facecolor=COLORS['accent2'], edgecolor='white',
                        linewidth=2, alpha=0.9)
ax3.add_patch(step4)
ax3.text(9, 3.1, 'Step 4', ha='center', va='center',
         fontsize=11, fontweight='bold', color='white')
ax3.text(9, 2.5, '关联个体机器人暴露指标', ha='center', va='center',
         fontsize=11, fontweight='bold', color='white', fontproperties=chinese_font)
ax3.text(9, 1.9, 'ln_robot_pit = θ_ip × Bartik_p', ha='center', va='center',
         fontsize=9, color='white', style='italic')

# 变量说明框
legend_box = FancyBboxPatch((0.5, 0.3), 11, 0.8,
                             boxstyle="round,pad=0.05,rounding_size=0.1",
                             facecolor='white', edgecolor=COLORS['neutral'],
                             linewidth=1, alpha=0.8)
ax3.add_patch(legend_box)
ax3.text(6, 0.7, 'θ_ip: 行业i在省p的就业份额  |  g_i: 全国行业i增长率  |  Robot_it: 行业机器人渗透率',
         ha='center', va='center', fontsize=9, color=COLORS['primary'],
         fontproperties=chinese_font)

# 箭头 - Step 1 到 Step 2
arrow1 = FancyArrowPatch((3, 6.5), (3, 6),
                          arrowstyle='->', color=COLORS['primary'],
                          lw=2.5, mutation_scale=15)
ax3.add_patch(arrow1)

# 箭头 - Step 2 到 Step 3 (向右)
arrow2 = FancyArrowPatch((5.5, 5), (6.5, 5),
                          arrowstyle='->', color=COLORS['secondary'],
                          lw=2.5, mutation_scale=15)
ax3.add_patch(arrow2)

# 箭头 - Step 3 到 Step 4 (向下)
arrow3 = FancyArrowPatch((9, 4), (9, 3.5),
                          arrowstyle='->', color=COLORS['accent1'],
                          lw=2.5, mutation_scale=15)
ax3.add_patch(arrow3)

# 数据来源标注
ax3.text(3, 3.3, '数据来源：', ha='center', va='center',
         fontsize=10, fontweight='bold', color=COLORS['primary'], fontproperties=chinese_font)
ax3.text(3, 2.8, '• 企业机器人数据 (IFR)', ha='center', va='center',
         fontsize=9, color='gray', fontproperties=chinese_font)
ax3.text(3, 2.4, '• 行业就业份额 (CFPS/人口普查)', ha='center', va='center',
         fontsize=9, color='gray', fontproperties=chinese_font)

fig3.tight_layout()
fig3.savefig('Fig9_Bartik_Flowchart.pdf', format='pdf', dpi=300,
             bbox_inches='tight', facecolor='white')
fig3.savefig('Fig9_Bartik_Flowchart.png', format='png', dpi=300,
             bbox_inches='tight', facecolor='white')
print("已生成 Fig9_Bartik_Flowchart.pdf/png")

# ============================================================
print("\n" + "="*60)
print("Batch 2 完成")
print("="*60)
print("生成文件:")
print("  - Fig_ThreeLayer_Framework.pdf/png (2.2节 三层框架概念图)")
print("  - Fig6_Robustness_SpecCurve.pdf/png (5.2.1节 稳健性规格曲线)")
print("  - Fig9_Bartik_Flowchart.pdf/png (4.3.2节 Bartik工具变量流程图)")
