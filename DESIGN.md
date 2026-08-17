# Design System of econpaper

来源：`docs/specs/design-sources.md`。
Notion「Will's S Design Note」已实载；本机 `Documents/design-notes/living/` 也读了。
旧锁「暖墨暗房 + 蜡笔红 `#e35342`」作废，不要再抄。

## 1. Visual Theme & Atmosphere

econpaper 是一张写实证论文的桌。
人上传数据、填方向、批章节。
机器先交出识别、主表、稳健戳和文献，再允许按章写。
它不是暗房仪器展，也不是普通 SaaS 后台。

身份一句话：**先看见数字，再写正文。** 中栏是纸，左栏是章，右栏是步骤。
颜色只表达意义：绿是可点的下一步，金是写不了，红不当品牌。

**Key Characteristics:**
- 浅纸台面（`#f4efe4`），浅壳（`#f1f0ed`），字是墨（`#181515`）
- 唯一交互 accent 是货架绿（`#2f6b4f`）：主按钮、当前章、链
- 蜡笔红（`#e35342` / `#8B2C2C`）不再出现
- 写不了、0 星用告警金，删除/失败才用语义红 `#9b3d30`
- 不必填满整屏；邻近的控件挨着放
- 读数台是「展示工作步骤」，不是彩虹卡
- 中文正文用 Noto Serif SC；界面用 Instrument Sans；标题可用 Instrument Serif
- 常规不用阴影，层级靠纸面和线

## 2. Color Palette & Roles

### Primary
- **纸**（`#f4efe4`）：主底、正文底。
- **浅壳**（`#f1f0ed`）：顶栏、次级面。
- **面板**（`#fffdf7`）：读数台、卡片。

### Accent
- **绿**（`#2f6b4f`）：唯一交互 accent。主 CTA、当前章、链、选中。
- **绿淡**（`rgba(47,107,79,0.12)`）：hover / active tint。

### Neutrals & Text
- **墨**（`#181515`）：正文。
- **弱化**（`#515151`）：标签、元信息。
- **边**（`#d8d2c6`）：分割、输入框。

### Semantic & Status
- **成功**（`#2f6b4f`）：完成态，与 accent 同色。
- **告警**（`#8a6a12`）：写不了、需要改设计。
- **失败**（`#9b3d30`）：删除、中断。不当主按钮。

### Borders
- **默认边框**（`#d8d2c6`）。

> 阴影纪律：常规卡片不用阴影。不要为了「仪器感」再铺暗房。

## 3. Typography Rules

### Font Family
- **界面无衬线**：`Instrument Sans`，fallback `system-ui, sans-serif`。按钮、卡片、UI 文本。
- **标题衬线**：`Instrument Serif`，fallback `Georgia, serif`。页内大标题。
- **中文衬线**：`Noto Serif SC`，fallback `serif`。论文正文、长读。
- **等宽 mono**：`JetBrains Mono`，fallback `monospace`。标签、读数、代码。
- **OpenType Features**：`"tnum"` 用于数字对齐。

### Hierarchy

| Role | Font | Size | Weight | Line Height | Letter Spacing | Notes |
|------|------|------|--------|-------------|----------------|-------|
| 读数 | JetBrains Mono | 16px | 500 | 1.2 | 0 | 主张、星、系数 |
| 章节标题 | Instrument Serif | 22px | 400 | 1.3 | -0.4px | 面板标题、章节题 |
| 论文主标题 | Noto Serif SC | 28px | 600 | 1.4 | 0 | 中栏论文标题 |
| 论文正文 | Noto Serif SC | 16px | 400 | 1.8 | 0 | 长读正文，行高放宽 |
| 按钮 | Instrument Sans | 14px | 500 | 1.0 | 0 | 交互控件 |
| Mono 标签 | JetBrains Mono | 12px | 400 | 1.4 | 0.08em | 大写标签 |
| 代码 | JetBrains Mono | 13px | 400 | 1.5 | 0 | 代码块、数据表 |
| 微文案 | Instrument Sans | 12px | 400 | 1.4 | 0 | 提示、辅助说明 |

### Principles
- 数字和标签用 mono，正文用衬线。不要第三套花体。
- 中栏论文正文用 Noto Serif SC，行高 1.8。
- 不超过三种尺寸层次。
- 中文标点全角。

## 4. Component Stylings

### Buttons

**Primary**
- Background: `#2f6b4f`
- Text: `#FFFFFF`
- Padding: `10px 20px`
- Radius: `8px`
- Font: `14px Instrument Sans` weight `500`
- Hover: 略加深绿
- Use: 上传、提交方向、写这一章

**Secondary / Ghost**
- Background: transparent
- Text: `#181515`
- Border: `1px solid #d8d2c6`
- Hover: background `#f1f0ed`

**Tertiary**
- Background: `#fffdf7`
- Text: `#181515`
- Border: none

### Cards & Containers
- Background: `#fffdf7`
- Border: `1px solid #d8d2c6`
- Radius: `8px`
- Shadow: none
- Padding: `16px` 或 `24px`

### Badges
- **当前 / 可点**：绿淡底 + `#2f6b4f` 字
- **写不了**：告警金
- **失败**：语义红 `#9b3d30`，不当主按钮
- **中性**：`#515151`

### Inputs & Forms
- Border: `1px solid #d8d2c6`
- Radius: `8px`
- Focus: `border-color #2f6b4f`
- Error: `border-color #9b3d30`
- Label 贴着输入（邻近原则）

### Navigation
- 顶栏浅壳。品牌用 serif，会话 ID 用 mono。
- 左栏章名。当前章 = 绿。
- 右栏步骤：当前节点、真审/假审。
- 移动端左右栏收成抽屉。

### Distinctive
读数台：方向提交后立刻出现主张、星、主表、文献、阻断。
这就是「展示工作步骤」。低风险自动跑完再亮数字；写章是高风险，没数字不能点。

## 5. Layout Principles

### Spacing System
- Base unit: `8px`
- Scale: `0, 4, 8, 12, 16, 24, 32, 48, 64`
- Component padding: `20px`（卡片）、`16px`（面板内边距）
- Section spacing: `48px`（区块间）、`24px`（面板内段）

### Grid & Container
- Max content width: `1527px`（给现代大屏）
- 三栏：左 `260px`，中 `1fr`，右 `320px`（对应 Outline / Editor / Agent）
- Gutter: `16px`
- 中栏论文正文：`620px` 内宽（约 70ch），居中，长读最优

### Whitespace Philosophy
- 台面（外层）留白大，光线感；仪器（面板）密度高，信息感。
- 中栏论文正文给足呼吸：`80px` 上下、`64px` 左右，行高 1.8。
- 面板内用 `16px` 节奏，不堆叠。
- 区块间距随视口增大而增大。

### Border Radius Scale

| Category | Radius | Use |
|----------|--------|-----|
| Micro | `4px` | 小徽章、内嵌元素 |
| Subtle | `8px` | 输入框、图标按钮 |
| Standard | `12px` | 卡片、面板 |
| Comfortable | `20px` | 大容器、纸卡 |
| Pill | `60px` | 按钮、标签 |
| 撕纸角 | `20px 20px 4px 4px` | 纸卡（顶大圆底小方） |

## 6. Depth & Elevation

常规不用阴影。层级靠纸面 `#fffdf7` 和边线 `#d8d2c6`。
焦点环用绿淡，不用蜡笔红。

## 7. Do's and Don'ts

### Do
- 用浅纸 `#f4efe4` 做长时界面底。
- 唯一 accent 用绿 `#2f6b4f`，只点在控件和当前章上。
- 中栏正文用 Noto Serif SC，行高 1.8。
- 先亮读数，再允许写。
- 引用必须能点回本次文献。
- 中文标点全角。

### Don't
- 不要再用蜡笔红 `#e35342` / `#8B2C2C`。
- 不要把整站铺成暖墨暗房 `#161411`。
- 不要多 accent 混打。
- 不要给普通卡片加阴影。
- 不要用正文出现代表估计完成。

## 8. Responsive Behavior

### Breakpoints

| Name | Width | Key Changes |
|------|-------|-------------|
| Mobile Small | <`480px` | 三栏折叠为单栏，左右栏变抽屉，顶栏收核心操作 |
| Mobile | `480`–`768px` | 中栏纸卡全宽，面板图标化 |
| Tablet | `768`–`1024px` | 左栏保留，右栏可折叠 |
| Desktop | `1024`–`1440px` | 三栏全开 |
| Large Desktop | >`1440px` | 中栏正文限制 `620px` 内宽，两侧留白 |

### Touch Targets
- 最小触摸目标 `44×44px`（图标按钮）。
- 移动端按钮 padding 加到 `12px 24px`。
- 链接间隔至少 `8px`。

### Collapsing Strategy
- 读数标签随视口收紧。
- 导航：移动端左右栏收进抽屉，顶栏保留上传/导出/语言。
- 三栏网格：`lg` 断点以下中栏优先，左右栏抽屉化。
- 间距：`48px` 节距降到 `32px`，卡片 padding `20px` 降到 `16px`。

## 9. Agent Prompt Guide

### Quick Color Reference
- Background: `#f4efe4`
- Cream: `#f1f0ed`
- Panel: `#fffdf7`
- Accent: `#2f6b4f`
- Ink: `#181515`
- Muted: `#515151`
- Border: `#d8d2c6`
- Warning: `#8a6a12`
- Danger: `#9b3d30`

不要写蜡笔红，不要写暖墨暗房。

详见 `docs/specs/design-sources.md`。