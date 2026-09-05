# 设计来源（2026-08-17 实载）

交互和颜色不再跟旧的「暖墨暗房 + 蜡笔红」走。
那是以前锁死的，本轮作废。

## 两处都要读

```
Notion「Will's S Design Note」     原则、AI 交互、引用、间距
Documents/design-notes/living/     现在看得见的纸、墨、绿
```

Notion 不是奕枢色板。
工作区：`Will's S Design Note`（`yishuziyu@gmail.com`）。
本窗用 MCP 实拉了 24 页，不是只看 doctor。

本机货架从 `Documents/design-notes/living/INDEX.md` 进。
`DESIGN.md` 里蜡笔红段落是旧档案，不是现行命令。

## Notion 这轮读过的页

| 页 | ID | 用在台上的一句话 |
| --- | --- | --- |
| Design Principles | `382886bc60ff8083b3ecfd0522c47ed4` | 先做事；不打扰；人能决定下一步 |
| Color System and Branding | `380886bc60ff80fcb3bbeaa4bf654d9d` | 颜色只表达意义；accent 用在控件上；Slack 式少用 |
| Typography and Fonts | `380886bc60ff8077ad56c00edabbb24a` | 可读优先；衬线给长读；字能放大 |
| 5 Principles of Visual Design | `1f8886bc60ff81cb84cde615a14b840c` | 比例 / 层次 / 平衡 / 对比 / 邻近；红留给删除一类危险 |
| Layout and Spacing | `226886bc60ff8123bf40f8925f0c1389` | 不必填满整屏 |
| Establish a spacing system | `226886bc60ff8136b36bdf20a44dd788` | 先定一档尺寸，相邻差约 25% |
| You assist me | `1f8886bc60ff81d2bbe1e6aa3f751726` | 机器在后；人可接管 |
| Human in the loop | `1f8886bc60ff81ed9691ffd4e2b68db1` | AI 是助手不是老板 |
| Show the work | `1f8886bc60ff814d9368f3b9f19264b4` | 先亮步骤和数字，再写正文 |
| Governors | `1f8886bc60ff81eb992df7d57d2b7efe` | 人随时能看懂、能改方向 |
| Citations | `1f8886bc60ff81f68355c7267648878c` | 正文必须能点回来源 |
| ProductsAIGuidelines | `1f8886bc60ff81f8ba2bdf6c65d28bef` | 写论文的主路径不能只靠 AI |

全文在 Notion。
不要把带签名的 S3 图链写进仓库。

## 本机货架（现行看得见的色）

`Documents/design-notes/living/shelf/index.html` 和货架首页：

| Token | Hex | 用途 |
| --- | --- | --- |
| ink | `#181515` | 字 |
| cream | `#f1f0ed` | 顶栏 / 浅壳 |
| paper | `#f4efe4` | 台面和正文底 |
| muted | `#515151` | 元信息 |
| green | `#2f6b4f` | 唯一交互 accent |

网点页写明：信号色跟这一局走，不要从落地页抄蜡笔红。
红只留在滑杆上当试色。

字体：Instrument Serif / Instrument Sans；中文长读仍用 Noto Serif SC。

## 台上因此改掉的东西

- 不再用 `#e35342` / `#8B2C2C` 当品牌或主按钮。
- 不再把整站铺成暖墨暗房 `#161411`。
- 主按钮、当前章、链：绿 `#2f6b4f`。
- 写不了、0 星：告警金，不是红品牌灯。
- 删除/失败才用语义红 `#9b3d30`，不当 CTA。

## 外部参考（2026-09-05 追加）

三个库/演示，做界面和动效时按需取用。都受上一节色板约束：绿仍是唯一交互 accent，外部组件的玻璃拟态、彩虹渐变、亮底彩段一律不搬。

| 来源 | 是什么 | 拿什么 |
| --- | --- | --- |
| [libraries.dev](https://libraries.dev) | 5 个 MIT React 特效库（Border Beam 流光边框 / Thinking Orbs 加载 / Gooey / Liquid Metal / WebGL 加载器），装法：复制提示词给代理 | 落地页点缀动效；与墨色海报风协调着用，不为特效而特效 |
| [BoardUI](https://boardui.com) | MIT 开源 React 仪表盘设计系统（72 组件 / 17 图表 / 8 模板，React 19 + Tailwind v4），`npx boardui@latest add <组件>`，另有 MCP | Agent progress、Agent thinking、Composer loader、Recharts 图表、数据表格——空桌工作台直接可用 |
| [RAG 轨迹卡视频](https://x.com/jeetnirnejak/status/2095507715556831429) | 38s demo：一张单列卡片 trace 完整五阶段管道运行 | Phase B 步骤卡时间线的直接参照，手法拆解见下 |

### RAG 轨迹卡手法拆解（步骤卡照这个长）

1. **卡片骨架**：header=标题+右上计时药丸（idle 显"5 stages"→运行实时 ms→完成定格 ms）；左竖脊线串阶段图标，当前阶段彩色填充、完成后回灰描边但保留右对齐耗时；每阶段=名称+mono 耗时+一行 mono 摘要+专属微型可视化；footer=彩点+进行时动词+主按钮（Run→完成变 Replay）。
2. **颜色=身份（最值钱）**：每个证据源固定一色，同色出现在源徽章、分数条、组装条段、正文引用标；悬停任一端，另一端亮同色光环。这是「设定卡↔估计产物无指纹绑定」缺口的 UI 级答案：解读里提到的系数，悬停高亮回归表对应行和设定卡对应变量。落地时身份色是新的语义层（不是装饰色），选 2–3 个在 paper 底上够稳的莫兰迪调，绿仍留给交互。
3. **每阶段一个微型可视化，不是日志行**：向量=条码条带；检索=排名列表（徽章+mono 名+分数条+mono 分数）；组装=分段堆叠条按 token 占比。我们对应：诊断画缺失率条带、估计画置信区间微图。
4. **状态机语言**：进行时动词（正在读数据/正在估计…），完成语报证据数（"结论由 3 张表支撑"式）。
5. **ghost 占位态**：未运行时骨架可见（虚线圈+灰条+"--"），重放交叉淡变回 ghost。空桌步骤卡先展示"将会出现什么"。
6. **动效全部同位交叉淡变，零布局跳动**：分数条从 0 生长、分段条按源顺序画出；仍按 animate 决策序取舍。
7. **双字体**：sans 只给阶段名/标题，数字、摘要、答案全 mono。

不抄：演示用假毫秒（必须真计时）、60fps 表演节奏（按真实时长）。

