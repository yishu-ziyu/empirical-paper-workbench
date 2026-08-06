# 开发日志 · 2026-08-06 → 2026-08-07

Session focus: Continuous Empirical Loop 成文质量 + 文献核验（Crossref + CNKI）

## 背景

产品定位为 Continuous Empirical Loop（`docs/PRODUCT.md`）：题目+数据 → 设计→估计→写稿→复现→修订外环。  
Demo 题：`parent_education_wage`（CFPS 修复样本，OLS+HC1 关联，非 IV 因果）。

## 问题与处理

### 1. 正文像工程审计日志

**现象：** 论文里出现 `tables/...`、`（证据：Results/json/...）`、claim register、Continuous Loop 等产品词。  
**根因：** expand_fallback / LLM 扩写把路径当「证据绑定」写进正文；评价器曾给路径戳加 craft 分。  
**处理：**

- `course_paper_builder.py`：纯学术中文，表号 + 合理小数位。
- `full_pipeline.step_06_writing`：builder 优先；LLM 仅润色干净稿；路径泄漏则丢弃。
- `sanitize_manuscript_prose` / `manuscript_has_path_leaks` 落地。
- `_expand_fallback` 去掉路径附录。
- `evolve_evaluator`：路径泄漏 craft=0。
- `latex_pdf`：去掉 Results/json 页脚与 Continuous Loop 作者行；表内浮点四舍五入。

### 2. 文献 verified_count=0

**现象：** 文献节只能写「待核验」，无法正式引用。  
**处理：**

- 新增 `runtime/literature_pack.py`：种子 DOI → Crossref 解析 → CSV/bib/矩阵/文献节。
- 经典文献（Becker-Tomes, Card, Black et al., Oreopoulos et al., China twins/CFPS returns 等）DOI 核验通过。
- `step_02` / `step_08` 接入；citation_gate 在 verified_count>0 时 passed。

### 3. 中文 CNKI

**方案来源：** GitHub `cookjohn/cnki-skills`（Chrome DevTools / CDP）+ 本机 `~/.claude/cnki-*`。  
**处理：**

- Chrome CDP 端口 9333 + Playwright 多主题检索。
- 详情页抓取 12 篇（管理世界、社会、人口与发展、教育与经济、经济评论等 + 直接相关学位论文）。
- 落盘 `litreview/cnki/`；`runtime/cnki_client.py` 固化检索客户端。
- `step_02` **合并** CNKI 磁盘包，避免 quality loop 只写 Crossref 冲掉中文。
- 作者字段清洗（去掉单位名串进 cite）。

### 4. 持续环

- 曾跑 `scripts/41_quality_loop_2h.py`（Grok 4.5）；日志 `.hour-loop/cnki_quality_loop.log`。
- 停环：`kill $(cat .hour-loop/cnki_quality_loop.pid)`（若存在）。

## 关键产物

| 类型 | 路径 |
|------|------|
| 写稿器 | `runtime/course_paper_builder.py` |
| 文献包 | `runtime/literature_pack.py` |
| CNKI | `runtime/cnki_client.py` · `litreview/cnki/` |
| 流水线 | `runtime/full_pipeline.py` |
| PDF | `runtime/latex_pdf.py` |
| 规范 | `docs/superpowers/specs/2026-08-07-continuous-loop-literature-cnki-spec.md` |
| 交接 | `docs/superpowers/handoffs/2026-08-07-continuous-loop-literature-cnki-handoff.md` |
| Bib | `references.bib` |

## 指标（末次已知）

- OLS parent_education ≈ 0.059 (se≈0.008), n=12582, HC1.
- verified_count = 25 (13 Crossref + 12 CNKI).
- 正文 path_leaks = false.
- PDF 可重建：`Submissions/parent_education_wage_loop_paper.pdf`（通常 gitignore）。

## 教训（已写入 AGENTS.md Lessons）

1. 正文只给人读；路径与 claim 只进复现侧。
2. 文献必须 DOI/页面核验后才允许作者—年份。

## 未完成 / 下次优先

1. CNKI 作者清洗边角 + 中文刊 DOI 补全。
2. 写厚学术段落但不回路径注水。
3. Dashboard 展示 verified_count / path-leak / PDF。
4. 第二题干跑，证明非单例。
