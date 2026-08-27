r"""T-10 RED tests for export_docx 节点 + LaTeX 模板.

契约（任务规格 §T-10）：
1. render_template(template_name, title, author, chapters) 用 Jinja2 填充模板
   → 返回 LaTeX 源码，包含 \title{...} / \author{...} / \section{...} / 章节内容
2. 4 个模板均可用：cn_journal / undergraduate / master_thesis / english_submission
3. 未知模板名抛 ValueError
4. export_docx(state) 返回
   {"latex_source": str, "pdf_path": Optional[str], "docx_path": Optional[str],
    "degraded": bool}
5. latexmk 不可用时 pdf_path=None 且 degraded=True（降级）
6. 模板可从 state.title_chapter 提取 title
"""
from __future__ import annotations

import pytest

from nodes.export_docx import (
    export_docx,
    normalize_template,
    render_template,
    TEMPLATE_NAMES,
)

from conftest import make_state, make_title_chapter, make_body_chapters


_TITLE = "教育回报率研究"


def _full_state(**overrides) -> dict:
    """构造一个含 title_chapter + body_chapters 的 state（基于根 conftest 工厂）。"""
    return make_state(
        title_chapter=make_title_chapter(_TITLE),
        body_chapters=make_body_chapters(),
        **overrides,
    )


# ---------------------------------------------------------------------------
# render_template 纯函数
# ---------------------------------------------------------------------------
def test_render_template_fills_title_and_author():
    """render_template 把 title / author 填进 \\title{} / \\author{}。"""
    tex = render_template(
        "cn_journal",
        title="教育回报率研究",
        author="张三",
        chapters=[{"title": "引言", "content": "正文内容"}],
    )
    assert "\\title{教育回报率研究}" in tex
    assert "\\author{张三}" in tex


def test_render_template_fills_chapter_sections():
    """render_template 把每章渲染为 \\section{title}\\ncontent。"""
    tex = render_template(
        "cn_journal",
        title="T",
        author="A",
        chapters=[
            {"title": "引言", "content": "引言正文"},
            {"title": "结论", "content": "结论正文"},
        ],
    )
    assert "\\section{引言}" in tex
    assert "引言正文" in tex
    assert "\\section{结论}" in tex
    assert "结论正文" in tex


@pytest.mark.parametrize("name", sorted(TEMPLATE_NAMES))
def test_render_template_supports_all_four_templates(name):
    """4 个模板都能加载并渲染出 \\begin{document}。"""
    tex = render_template(
        name,
        title="T",
        author="A",
        chapters=[{"title": "S", "content": "C"}],
    )
    assert "\\begin{document}" in tex
    assert "\\end{document}" in tex


def test_render_template_unknown_name_raises():
    """未知模板名抛 ValueError。"""
    with pytest.raises(ValueError):
        render_template("nonexistent", title="T", author="A", chapters=[])


@pytest.mark.parametrize(
    "alias,canonical",
    [
        ("undergrad", "undergraduate"),
        ("master", "master_thesis"),
        ("en_submission", "english_submission"),
        ("undergraduate", "undergraduate"),
        ("cn_journal", "cn_journal"),
    ],
)
def test_normalize_template_aliases(alias, canonical):
    """DirectionForm / sample write-loop aliases map onto TEMPLATE_NAMES."""
    assert normalize_template(alias) == canonical


def test_render_template_undergrad_alias_matches_undergraduate():
    """template=undergrad renders the undergraduate template, not ValueError."""
    kwargs = dict(
        title="T",
        author="A",
        chapters=[{"title": "S", "content": "C"}],
    )
    aliased = render_template("undergrad", **kwargs)
    canonical = render_template("undergraduate", **kwargs)
    assert aliased == canonical
    assert "本科毕业论文模板" in aliased


def test_export_docx_undergrad_alias_from_state(tmp_path, monkeypatch):
    """state.export_template='undergrad' must not raise; uses undergraduate.tex."""
    monkeypatch.setattr("nodes.export_docx.compile_pdf", lambda tex, outdir: None)
    monkeypatch.setattr("nodes.export_docx.convert_docx", lambda tex, outdir: None)
    result = export_docx(_full_state(export_template="undergrad"))
    assert "本科毕业论文模板" in result["latex_source"]
    assert "\\begin{document}" in result["latex_source"]


def test_render_template_cn_journal_uses_ctex():
    """中文期刊模板包含 ctex 包（中文支持）。"""
    tex = render_template(
        "cn_journal", title="T", author="A", chapters=[]
    )
    assert "ctex" in tex


def test_render_template_english_no_ctex():
    """英文投稿模板不含 ctex（用 source serif / 标准 article）。"""
    tex = render_template(
        "english_submission", title="T", author="A", chapters=[]
    )
    assert "ctex" not in tex.lower()


# ---------------------------------------------------------------------------
# export_docx 节点
# ---------------------------------------------------------------------------
def test_export_docx_returns_latex_source(tmp_path, monkeypatch):
    """export_docx(state) 返回 latex_source 字符串，包含 title。"""
    # 让编译函数返回 None（模拟 latexmk 不可用），只验证 latex_source
    monkeypatch.setattr(
        "nodes.export_docx.compile_pdf", lambda tex, outdir: None
    )
    monkeypatch.setattr(
        "nodes.export_docx.convert_docx", lambda tex, outdir: None
    )
    state = _full_state()
    result = export_docx(state)
    assert "latex_source" in result
    assert isinstance(result["latex_source"], str)
    # title 章节的标题应出现在 latex 源码里
    assert "教育回报率研究" in result["latex_source"]


def test_export_docx_extracts_title_from_title_chapter(tmp_path, monkeypatch):
    """export_docx 从 state.title_chapter 提取 title 填入 \\title{}。"""
    monkeypatch.setattr(
        "nodes.export_docx.compile_pdf", lambda tex, outdir: None
    )
    monkeypatch.setattr(
        "nodes.export_docx.convert_docx", lambda tex, outdir: None
    )
    state = _full_state()
    result = export_docx(state)
    assert "\\title{教育回报率研究}" in result["latex_source"]


def test_export_docx_degraded_when_compilers_unavailable(tmp_path, monkeypatch):
    """latexmk/pandoc 不可用时 pdf_path/docx_path=None 且 degraded=True。"""
    monkeypatch.setattr(
        "nodes.export_docx.compile_pdf", lambda tex, outdir: None
    )
    monkeypatch.setattr(
        "nodes.export_docx.convert_docx", lambda tex, outdir: None
    )
    state = _full_state()
    result = export_docx(state)
    assert result["pdf_path"] is None
    assert result["docx_path"] is None
    assert result["degraded"] is True


def test_export_docx_returns_paths_when_compilers_succeed(tmp_path, monkeypatch):
    """compile_pdf / convert_docx 成功时返回路径且 degraded=False。"""
    pdf = tmp_path / "out.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    docx = tmp_path / "out.docx"
    docx.write_bytes(b"PK fake docx")
    monkeypatch.setattr(
        "nodes.export_docx.compile_pdf", lambda tex, outdir: str(pdf)
    )
    monkeypatch.setattr(
        "nodes.export_docx.convert_docx", lambda tex, outdir: str(docx)
    )
    state = _full_state()
    result = export_docx(state)
    assert result["pdf_path"] == str(pdf)
    assert result["docx_path"] == str(docx)
    assert result["degraded"] is False


def test_export_docx_uses_template_from_state(tmp_path, monkeypatch):
    """export_docx 读取 state['export_template'] 选择模板（默认 cn_journal）。"""
    captured = {}

    def fake_compile(tex, outdir):
        captured["tex"] = tex
        return None

    monkeypatch.setattr("nodes.export_docx.compile_pdf", fake_compile)
    monkeypatch.setattr(
        "nodes.export_docx.convert_docx", lambda tex, outdir: None
    )
    state = _full_state(export_template="master_thesis")
    result = export_docx(state)
    # master_thesis 模板特征：包含 硕士 或 thesis 关键词
    assert "硕士" in result["latex_source"] or "thesis" in result["latex_source"].lower()


def test_export_docx_no_chapters_still_returns_tex(tmp_path, monkeypatch):
    """无 title_chapter / body_chapters 时仍返回 latex_source（用 Untitled 兜底）。"""
    monkeypatch.setattr(
        "nodes.export_docx.compile_pdf", lambda tex, outdir: None
    )
    monkeypatch.setattr(
        "nodes.export_docx.convert_docx", lambda tex, outdir: None
    )
    state = make_state()
    result = export_docx(state)
    assert "latex_source" in result
    assert "\\begin{document}" in result["latex_source"]


# ---------------------------------------------------------------------------
# ADR-0009: references_list → thebibliography 渲染
# ---------------------------------------------------------------------------
def test_export_docx_renders_bibliography_when_references_present(tmp_path, monkeypatch):
    """ADR-0009: references_list 非空时 latex_source 含 thebibliography 环境。"""
    monkeypatch.setattr(
        "nodes.export_docx.compile_pdf", lambda tex, outdir: None
    )
    monkeypatch.setattr(
        "nodes.export_docx.convert_docx", lambda tex, outdir: None
    )
    state = _full_state(
        references_list=[
            {"index": 1, "text": "Smith (2023). Test. https://doi.org/10.1/x",
             "doi": "10.1/x", "entry": {}},
            {"index": 2, "text": "Jones (2022). Another.", "doi": None, "entry": {}},
        ]
    )
    result = export_docx(state)
    tex = result["latex_source"]
    assert "\\begin{thebibliography}" in tex
    assert "\\end{thebibliography}" in tex
    assert "\\bibitem{[1]}" in tex
    assert "\\bibitem{[2]}" in tex
    assert "Smith (2023)" in tex
    # thebibliography 必须在 \end{document} 之前
    assert tex.index("\\begin{thebibliography}") < tex.index("\\end{document}")


def test_export_docx_no_bibliography_when_references_empty(tmp_path, monkeypatch):
    """ADR-0009: references_list 为空时不渲染 thebibliography。"""
    monkeypatch.setattr(
        "nodes.export_docx.compile_pdf", lambda tex, outdir: None
    )
    monkeypatch.setattr(
        "nodes.export_docx.convert_docx", lambda tex, outdir: None
    )
    state = _full_state(references_list=[])
    result = export_docx(state)
    tex = result["latex_source"]
    assert "\\begin{thebibliography}" not in tex


def test_export_docx_no_bibliography_when_references_missing(tmp_path, monkeypatch):
    """ADR-0009: references_list 缺失时不渲染 thebibliography（向后兼容）。"""
    monkeypatch.setattr(
        "nodes.export_docx.compile_pdf", lambda tex, outdir: None
    )
    monkeypatch.setattr(
        "nodes.export_docx.convert_docx", lambda tex, outdir: None
    )
    state = _full_state()  # 不设 references_list
    result = export_docx(state)
    tex = result["latex_source"]
    assert "\\begin{thebibliography}" not in tex


def test_render_bibliography_empty_returns_empty_string():
    """_render_bibliography 空列表返回空字符串。"""
    from nodes.export_docx import _render_bibliography
    assert _render_bibliography([]) == ""


def test_render_bibliography_renders_bibitems():
    """_render_bibliography 渲染 thebibliography + bibitem。"""
    from nodes.export_docx import _render_bibliography
    refs = [
        {"index": 1, "text": "A (2020).", "doi": "10.1/a", "entry": {}},
        {"index": 2, "text": "B (2021).", "doi": "10.1/b", "entry": {}},
    ]
    bib = _render_bibliography(refs)
    assert "\\begin{thebibliography}{2}" in bib
    assert "\\bibitem{[1]} A (2020)." in bib
    assert "\\bibitem{[2]} B (2021)." in bib
    assert bib.endswith("\\end{thebibliography}")


def test_append_bibliography_inserts_before_end_document():
    """_append_bibliography 在 \\end{document} 前插入。"""
    from nodes.export_docx import _append_bibliography
    tex = "\\begin{document}\nHello\n\\end{document}"
    refs = [{"index": 1, "text": "Ref.", "doi": None, "entry": {}}]
    result = _append_bibliography(tex, refs)
    assert result.index("\\begin{thebibliography}") < result.index("\\end{document}")
    assert result.endswith("\\end{document}")


def test_append_bibliography_empty_returns_unchanged():
    """_append_bibliography 空列表原样返回。"""
    from nodes.export_docx import _append_bibliography
    tex = "\\begin{document}\n\\end{document}"
    assert _append_bibliography(tex, []) == tex
