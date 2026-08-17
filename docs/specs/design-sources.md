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
