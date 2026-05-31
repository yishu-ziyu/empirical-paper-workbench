# CGSS PDF 预检

- 状态：`pdf_preflight_ready`
- Markdown 来源：`Manuscripts/generated/cgss_social_capital_happiness_paper.md`
- PDF：`Submissions/cgss_social_capital_happiness/paper.pdf`
- PDF 存在：`true`
- PDF 字节：187318
- HTML：`Submissions/cgss_social_capital_happiness/paper.html`
- HTML 存在：`false`
- 正式层写回：`false`

## 渲染器
- `pandoc+xelatex` returncode=0

## Agent Team 调用节奏
- call_when: after_pdf_or_html_preflight_artifact_is_created
- called_agents: ['VerifierAgent', 'ManuscriptAgent', 'ExportAgent']
- recall_when: after_human_opens_rendered_artifact
- next_call_when: before_formal_package_or_revision_round
- boundary: 当前渲染状态为 pdf_preflight_ready；只做草案预检，不提升正式层。

## 下一步
- `human_review_pdf_candidate`
- `build_aer_like_method_gate`
- `generate_reviewer_report_and_revision_queue`
