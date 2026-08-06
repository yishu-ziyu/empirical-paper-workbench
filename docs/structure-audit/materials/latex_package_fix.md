# continuous_loop package · LaTeX PDF 修复

日期：2026-08-06

## 问题

`ContinuousEmpiricalLoop._package` 有时 `latex_ok=False` 且 `package['pdf']=""`，
即使 `Manuscripts/generated/*_full_pipeline_paper.md` 存在、离线
`render_markdown_paper_to_pdf(...)` 可成功出 PDF。

观察：

- 质量外环多轮 `package.pdf` 空、`latex_ok=False`
- 同机离线编译 `Submissions/parent_education_wage_loop_paper.pdf` 正常
- 评分器 `latex_pdf` 仍可能因磁盘上旧 PDF 给 1.0，与 package 字段不一致
- 共享 `Submissions/latex_build/{slug}/` 并发 xelatex 会互相踩 aux/log/pdf

## 根因（territory）

1. **共享 build 目录竞态**：package 与手工/外环同时写同一 `latex_build/{slug}/`，偶发 returncode≠0。
2. **失败路径丢 PDF 指针**：`LatexPdfResult` 在 `ok=False` 时强制 `pdf_path=""`，即使 `Submissions/{slug}_loop_paper.pdf` 仍是上一次成功产物。
3. **错误只进 json、不进 loop 可读 log**；异常虽不抛死 package，但调用方看到空 pdf，像「没编」。

不是 `has_blocking_quality` / red-not-green 的问题；质量红灯仍禁止 `completed_green`。

## 修复

### `runtime/latex_pdf.py`

- 成功：`ok=True`，`pdf_path` = 相对路径 `Submissions/{slug}_loop_paper.pdf`（仅 rc==0 且体积足够时 copy deliver）。
- 失败：**不覆盖** deliver PDF；若 last-good 存在则 `pdf_path` 指向它，`used_last_good=True`，`errors` 含 `using_last_good_pdf`。
- 路径一律尽量相对 project root（`_rel_to_root`）。
- 超时 / spawn 错误捕获，不把异常抛出调用方。

### `runtime/continuous_loop.py` · `_package`

1. **始终**用 paper 路径调用 `render_markdown_paper_to_pdf`（ctx 缺失则回退 canonical generated md）。
2. **隔离 build 目录**：`out_dir = loop_dir / "latex_build"`，避免外环并发踩共享目录。
3. 编译失败：保留 last-good PDF 路径；写 `loop_dir/latex_pdf_result.json` + `loop_dir/latex_pdf_errors.log`；**不中断 package**。
4. `package['pdf']`：有产物时为 **相对路径**；`latex_ok` 仅反映**本轮**编译是否成功；`latex_note=using_last_good_pdf` 标记沿用旧 PDF。
5. `completed_green` + blocking 仍强制降为 `halted_honest`（`has_blocking_quality` 不变）。

## 验收

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板
PYTHONPATH=. python3 - <<'PY'
from runtime.full_pipeline import FullPaperPipeline
from runtime.continuous_loop import ContinuousEmpiricalLoop, has_blocking_quality

# 1) no-llm pipeline 先落 paper
pipe = FullPaperPipeline(use_llm=False)
rec = pipe.run()
assert rec.status == "completed", rec.status

# 2) continuous loop package 应 latex_ok
loop = ContinuousEmpiricalLoop(use_llm=False, max_rounds=1)
result = loop.run()
pkg = result.package
print("status", result.status)
print("package", pkg)
assert pkg.get("latex_ok") == "True", pkg
assert pkg.get("pdf") == "Submissions/parent_education_wage_loop_paper.pdf", pkg
assert not str(pkg.get("pdf","")).startswith("/"), "pdf must be relative"
# red-not-green still holds when blocking present
assert has_blocking_quality(evaluation={"blocking": ["too_thin"], "verdict": ["too_thin"]})
print("LATEX_PACKAGE_OK")
PY
```

期望：

- `latex_ok == "True"`
- `pdf == Submissions/parent_education_wage_loop_paper.pdf`（相对路径）
- `state/runs/continuous_loop_*/latex_pdf_result.json` 中 `ok: true`
- 若人为破坏 tex 使编译失败：`latex_ok=False` 但 `pdf` 仍指向 last-good，且 `latex_pdf_errors.log` 有记录

## 非目标

- 不把质量红灯改成绿；`too_thin` / `evidence_integrity_blocked` 等仍可 `halted_honest` / `max_rounds`。
- 不在失败时把 `latex_ok` 伪造成 True（last-good 只填 `pdf` + `latex_note`）。
