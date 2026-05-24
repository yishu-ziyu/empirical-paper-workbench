# Nothing Design System — Empirical OS 适配文档

> 版本: v1.0.0
> 基于: Nothing Design System v3.0.0
> 适配目标: 实证论文项目模板框架前端 (`Product/web/`)

---

## 1. 设计哲学

### Nothing 核心原则

- **Subtract, don't add.** 每个元素必须证明其存在的必要性。默认删除。
- **Structure is ornament.** 暴露网格、数据、层级本身。
- **Monochrome is the canvas.** 色彩是事件，不是默认。
- **Type does the heavy lifting.** 字号、字重、间距创造层级——不是颜色、不是图标、不是边框。
- **Industrial warmth.** 技术精确，但从不冰冷。

### Empirical OS 适配原则

数据密集型学术界面需要：
- **精确对齐**: 回归系数、标准误、p值必须严格对齐
- **状态可辨**: passed/blocked 不用彩色，用边框/背景/透明度区分
- **信息密度**: 三线表、证据卡片、任务队列在有限空间内清晰呈现
- **学术严谨**: 不花哨，不干扰数据阅读

---

## 2. 字体系统

### Google Fonts 加载

```html
<link href="https://fonts.googleapis.com/css2?family=Doto:wght@400..700&family=Space+Grotesk:wght@300;400;500;700&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
```

### 字体栈

| 角色 | 字体 | 回退 | 字重 |
|------|------|------|------|
| **Display** | Doto | Space Mono, monospace | 400–700 |
| **Body / UI** | Space Grotesk | DM Sans, system-ui, sans-serif | 300, 400, 500, 700 |
| **Data / Labels** | Space Mono | JetBrains Mono, SF Mono, monospace | 400, 700 |

### 字体使用纪律

- **每屏最多 2 种字体** (Space Grotesk + Space Mono。Doto 仅用于 hero 时刻)
- **每屏最多 3 个字号** (一个大、一个中、一个小)
- **每屏最多 2 个字重** (Regular + 一个其他)

### 字号层级

| Token | 大小 | 行高 | 字间距 | 用途 |
|-------|------|------|--------|------|
| `--text-display-xl` | 72px | 1.0 | -0.03em | Hero 数字 |
| `--text-display-lg` | 48px | 1.05 | -0.02em | 区块 hero |
| `--text-display-md` | 36px | 1.1 | -0.02em | 页面标题 |
| `--text-heading` | 24px | 1.2 | -0.01em | 区块标题 |
| `--text-subheading` | 18px | 1.3 | 0 | 子标题 |
| `--text-body` | 16px | 1.5 | 0 | 正文 |
| `--text-body-sm` | 14px | 1.5 | 0.01em | 次要正文 |
| `--text-caption` | 12px | 1.4 | 0.04em | 时间戳、脚注 |
| `--text-label` | 11px | 1.2 | 0.08em | **全部大写** 标签 |

---

## 3. 颜色系统

### 暗色模式 (OLED 优先)

| Token | Hex | 对比度 | 用途 |
|-------|-----|--------|------|
| `--nt-black` | `#000000` | — | 主背景 (OLED) |
| `--nt-surface` | `#111111` | 1.3:1 | 卡片、面板背景 |
| `--nt-surface-raised` | `#1A1A1A` | 1.5:1 | 次级提升表面 |
| `--nt-border` | `#222222` | — | 微妙分隔线 |
| `--nt-border-visible` | `#333333` | — | 有意边框、线框 |
| `--nt-text-disabled` | `#666666` | 4.0:1 | 禁用文本 |
| `--nt-text-secondary` | `#999999` | 6.3:1 | 标签、说明、元数据 |
| `--nt-text-primary` | `#E8E8E8` | 16.5:1 | 正文 |
| `--nt-text-display` | `#FFFFFF` | 21:1 | 标题、hero 数字 |

### 强调色与状态色

| Token | Hex | 用途 |
|-------|-----|------|
| `--nt-accent` | `#D71921` | 信号灯：激活状态、破坏性、紧急。每屏一个。 |
| `--nt-success` | `#4A9E5C` | 确认、完成 |
| `--nt-warning` | `#D4A843` | 注意、待处理 |
| `--nt-error` | `#D71921` | 与 accent 共享红色 |
| `--nt-info` | `#999999` | 使用 secondary 文本色 |
| `--nt-interactive` | `#5B9BF6` | 可点击文本 |

### Empirical OS 状态色 (单色)

Nothing 风格**不使用彩色**区分状态。状态区分通过：
- 透明度变化
- 字体粗细变化
- 边框有无
- 背景灰阶变化

| 状态 | 文本 | 背景 | 边框 |
|------|------|------|------|
| Passed | `#FFFFFF` | `#1A1A1A` | `#333333` |
| Blocked | `#888888` | `#111111` | `#222222` |
| Active | `#E8E8E8` | `#111111` | `#333333` |
| Inactive | `#666666` | `#000000` | `#222222` |

---

## 4. 间距系统

基于 8px 网格：

| Token | 值 | 用途 |
|-------|-----|------|
| `--space-2xs` | 2px | 光学调整 |
| `--space-xs` | 4px | 图标到标签间隙 |
| `--space-sm` | 8px | 组件内部间距 |
| `--space-md` | 16px | 标准 padding |
| `--space-lg` | 24px | 组间距 |
| `--space-xl` | 32px | 区块边距 |
| `--space-2xl` | 48px | 主要区块分隔 |
| `--space-3xl` | 64px | 页面级垂直节奏 |
| `--space-4xl` | 96px | Hero 呼吸空间 |

### 间距即意义

```
Tight (4–8px)    = "这些属于一起" (图标+标签, 数字+单位)
Medium (16px)    = "同组，不同项" (列表项, 表单字段)
Wide (32–48px)   = "新组开始" (区块分隔)
Vast (64–96px)   = "新上下文" (hero 到内容)
```

---

## 5. 边框与圆角

| Token | 值 | 用途 |
|-------|-----|------|
| `--radius-none` | 0px | 技术组件、表格 |
| `--radius-sm` | 4px | 紧凑卡片、技术元素 |
| `--radius-md` | 8px | 标准卡片 |
| `--radius-lg` | 12px | 大卡片 |
| `--radius-xl` | 16px | 浮层、模态框 |
| `--radius-pill` | 999px | 按钮、标签 |

| Token | 值 | 用途 |
|-------|-----|------|
| `--border-width-hairline` | 0.5px | 微妙分隔 |
| `--border-width-thin` | 1px | 标准边框 |
| `--border-width-medium` | 1.5px | 表格顶线/底线 |
| `--border-width-thick` | 2px | 激活指示器 |

---

## 6. 组件规范

### 6.1 FindingCard (结果卡片)

**用途**: 显示回归系数、标准误、p值、样本量

**结构**:
```html
<div class="finding-card">
  <div class="finding-card-header">
    <h4 class="finding-card-title">培训对工资的影响</h4>
    <span class="finding-card-badge">OLS</span>
  </div>
  <div class="finding-card-body">
    <div class="finding-stat">
      <span class="finding-stat-label">系数</span>
      <span class="finding-stat-value is-significant">0.1995</span>
      <span class="finding-stat-se">0.0423</span>
    </div>
    <div class="finding-stat">
      <span class="finding-stat-label">P 值</span>
      <span class="finding-stat-value is-significant">0.003</span>
    </div>
    <div class="finding-stat">
      <span class="finding-stat-label">样本量</span>
      <span class="finding-stat-value">12,847</span>
    </div>
    <div class="finding-stat">
      <span class="finding-stat-label">R²</span>
      <span class="finding-stat-value">0.342</span>
    </div>
  </div>
</div>
```

**样式要点**:
- 等宽字体展示数字
- 严格对齐 (tabular-nums)
- 极细边框 (1px solid #333)
- 无圆角或 4px 小圆角
- 显著性通过字重区分 (700 vs 400)，不用彩色

### 6.2 VerifierGate (核验门)

**用途**: 8个检查项，passed/blocked 状态

**结构**:
```html
<div class="verifier-gate">
  <div class="verifier-gate-header">
    <h3 class="verifier-gate-title">验证闸门</h3>
    <div class="verifier-gate-progress">
      <div class="verifier-gate-segment is-passed"></div>
      <div class="verifier-gate-segment is-passed"></div>
      <div class="verifier-gate-segment is-blocked"></div>
      <!-- ... -->
    </div>
  </div>
  <div class="verifier-gate-list">
    <div class="verifier-gate-item is-passed">
      <span class="verifier-gate-icon">01</span>
      <span class="verifier-gate-label">数据文件存在且可读</span>
      <span class="verifier-gate-status">PASSED</span>
    </div>
    <div class="verifier-gate-item is-blocked">
      <span class="verifier-gate-icon">03</span>
      <span class="verifier-gate-label">变量角色已确认</span>
      <span class="verifier-gate-status">BLOCKED</span>
    </div>
  </div>
</div>
```

**样式要点**:
- 分段进度条：机械感、仪器感
- 状态用边框/背景区分，不用彩色
- Passed: 白边框 + 提升背景
- Blocked: 暗边框 + 基础背景
- 编号用等宽字体

### 6.3 MethodExecutionEvidence (方法执行证据)

**用途**: 模型公式、样本量、诊断统计量

**结构**:
```html
<div class="method-evidence">
  <div class="method-evidence-header">
    <h4 class="method-evidence-title">方法执行证据</h4>
    <span class="method-evidence-badge">OLS local execution</span>
  </div>
  <div class="method-evidence-formula">
    <code>wage ~ trained + edu + experience | year + city</code>
  </div>
  <div class="method-evidence-grid">
    <div class="method-evidence-stat">
      <span class="method-evidence-stat-label">样本量</span>
      <span class="method-evidence-stat-value">12,847</span>
    </div>
    <div class="method-evidence-stat">
      <span class="method-evidence-stat-label">R²</span>
      <span class="method-evidence-stat-value">0.342</span>
    </div>
    <div class="method-evidence-stat">
      <span class="method-evidence-stat-label">F 统计量</span>
      <span class="method-evidence-stat-value">184.32</span>
    </div>
  </div>
</div>
```

**样式要点**:
- 纯黑背景 (#000000) 模拟终端
- 等宽字体、代码块风格
- 公式用 code 标签，白色高亮
- 诊断统计量网格排列

### 6.4 ReviewerScorecard (审稿评分卡)

**用途**: 五维评分（新颖性、识别可信度、数据质量、表达清晰度、政策相关性）

**结构**:
```html
<div class="reviewer-scorecard">
  <div class="reviewer-scorecard-header">
    <h3 class="reviewer-scorecard-title">审稿评分</h3>
    <span class="reviewer-scorecard-overall">3.8</span>
  </div>
  <div class="reviewer-scorecard-list">
    <div class="reviewer-scorecard-row is-high">
      <div class="reviewer-scorecard-dimension">
        <span class="reviewer-scorecard-label">识别可信度</span>
        <div class="reviewer-scorecard-bar">
          <div class="reviewer-scorecard-bar-fill" style="width: 92%"></div>
        </div>
      </div>
      <span class="reviewer-scorecard-value">4.6</span>
    </div>
    <!-- ... -->
  </div>
</div>
```

**样式要点**:
- 极简评分条：4px 高，无圆角
- 数字突出 (等宽、大字号)
- 左侧边框粗细表示等级
- 不用彩色，用灰阶填充

### 6.5 AgentTaskQueue (任务队列)

**用途**: 任务列表、状态、阻塞关系

**结构**:
```html
<div class="agent-task-queue">
  <div class="agent-task-item is-completed">
    <div class="agent-task-indent">
      <div class="agent-task-indent-dot"></div>
    </div>
    <div class="agent-task-content">
      <span class="agent-task-name">数据清洗</span>
      <div class="agent-task-meta">
        <span>ID: 001</span>
        <span>耗时: 2.3s</span>
      </div>
    </div>
    <span class="agent-task-status">DONE</span>
  </div>
  <div class="agent-task-item is-active">
    <!-- ... -->
  </div>
</div>
```

**样式要点**:
- 清单式布局
- 层级缩进 (16px)
- 状态标签：pill 形状，边框区分
- 缩进线表示层级关系

### 6.6 RegressionTable (三线表)

**用途**: 经济学回归表——框架核心展示组件

**结构**:
```html
<table class="regression-table">
  <thead>
    <tr>
      <th>变量</th>
      <th class="is-numeric">(1) 基线</th>
      <th class="is-numeric">(2) 加入控制</th>
      <th class="is-numeric">(3) 固定效应</th>
    </tr>
  </thead>
  <tbody>
    <tr class="is-coefficient">
      <td>培训</td>
      <td class="is-numeric">0.1995***</td>
      <td class="is-numeric">0.1842***</td>
      <td class="is-numeric">0.1756**</td>
    </tr>
    <tr class="is-standard-error">
      <td></td>
      <td class="is-numeric">(0.0423)</td>
      <td class="is-numeric">(0.0381)</td>
      <td class="is-numeric">(0.0712)</td>
    </tr>
    <!-- ... -->
    <tr class="is-model-info">
      <td>样本量</td>
      <td class="is-numeric">12,847</td>
      <td class="is-numeric">12,847</td>
      <td class="is-numeric">12,847</td>
    </tr>
  </tbody>
</table>
```

**样式要点**:
- 顶线 1.5px solid white
- 底线 1.5px solid white
- 表头下边框 0.75px solid #333
- 等宽字体、严格对齐
- 系数行粗体，标准误行浅色
- 无斑马纹、无单元格背景
- 悬停行：微妙背景提升 + 左侧 2px 白线指示

---

## 7. 按钮规范

| 变体 | 背景 | 边框 | 文本 | 圆角 |
|------|------|------|------|------|
| Primary | `#FFFFFF` | none | `#000000` | pill (999px) |
| Secondary | transparent | `1px solid #333` | `#E8E8E8` | pill |
| Ghost | transparent | none | `#999999` | 0 |
| Technical | transparent | `1px solid #333` | `#E8E8E8` | 4px |

所有按钮:
- 字体: Space Mono
- 大小: 13px
- **全部大写**
- 字间距: 0.06em
- 最小高度: 44px

---

## 8. 反模式 (永远不要做)

- [ ] 渐变背景
- [ ] 阴影、模糊效果
- [ ] 骨架屏 loading — 用 `[LOADING]` 文本或分段 spinner
- [ ] Toast 弹窗 — 用内联状态文本 `[SAVED]`
- [ ] 表情符号、吉祥物
- [ ] 表格斑马纹
- [ ] 填充图标、多色图标
- [ ] 弹性动画 — 只用 subtle ease-out
- [ ] 卡片圆角 > 16px
- [ ] 数据可视化：在引入颜色前，先用**透明度**或**图案**区分

---

## 9. 文件位置

| 文件 | 路径 | 说明 |
|------|------|------|
| Token 定义 | `Product/web/styles/nothing-tokens.css` | CSS 变量：颜色、字体、间距、边框、组件 Token |
| 组件样式 | `Product/web/styles/components.css` | 6大组件 + 按钮/面板/标签/输入框等 |
| 设计文档 | `docs/ui-design/nothing-design-system.md` | 本文档 |

---

## 10. 迁移路径

从当前 `archive-shell` (档案壳风格) 迁移到 Nothing 风格：

1. **引入字体**: 在 `index.html` `<head>` 添加 Google Fonts 链接
2. **引入 Token**: 在 `styles.css` 顶部 `@import './styles/nothing-tokens.css'`
3. **引入组件**: 在 `styles.css` 顶部 `@import './styles/components.css'`
4. **逐步替换**:
   - `:root` 颜色变量 → `--nt-*` 变量
   - 卡片样式 → `.nt-panel`
   - 按钮样式 → `.nt-button`
   - 表格样式 → `.regression-table`
   - 状态标签 → `.nt-tag`
5. **验证**: 检查所有状态不再依赖彩色背景，改用边框/字重/透明度

---

## 11. 参考

- Nothing Design System Skill: `~/.claude/skills/nothing-design/SKILL.md`
- Token 参考: `~/.claude/skills/nothing-design/references/tokens.md`
- 组件参考: `~/.claude/skills/nothing-design/references/components.md`
