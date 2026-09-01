// latexToHtml 安全与渲染契约测试。
//
// 安全背景（审查 P1-7）：输出经 Editor.tsx 的 dangerouslySetInnerHTML 进入 DOM，
// 内容来自 LLM 生成 / 用户编辑，属于不可信输入。管线必须保证：
// 先整体 HTML 转义、后 LaTeX 变换 —— 任何注入内容只能以文本形式出现。
import { describe, test, expect } from 'vitest'
import { latexToHtml } from '../latexToHtml'

describe('latexToHtml XSS 防线（恶意输入只能以文本出现）', () => {
  test('裸 <script> 不进入输出', () => {
    const out = latexToHtml('前文 <script>alert(1)</script> 后文')
    expect(out).not.toContain('<script>')
    expect(out).toContain('&lt;script&gt;')
  })

  test('事件属性载体 <img onerror> 不进入输出', () => {
    const out = latexToHtml('<img src=x onerror=alert(1)>')
    expect(out).not.toContain('<img')
    expect(out).toContain('&lt;img')
  })

  test('LaTeX 命令参数里的 HTML 被转义后保留', () => {
    const out = latexToHtml('\\title{<script>x</script>}')
    expect(out).toContain('<h1')
    expect(out).toContain('&lt;script&gt;x&lt;/script&gt;')
    expect(out).not.toContain('<script>')
  })

  test('数学环境里的注入内容被转义', () => {
    const out = latexToHtml('$$<svg onload=alert(1)>$$')
    expect(out).not.toContain('<svg')
    expect(out).toContain('&lt;svg')
  })

  test('verbatim 块内容转义且不双转义', () => {
    const out = latexToHtml('\\begin{verbatim}\n<b>&i</b>\n\\end{verbatim}')
    expect(out).toContain('<pre')
    expect(out).toContain('&lt;b&gt;&amp;i&lt;/b&gt;')
    expect(out).not.toContain('&amp;lt;')
    expect(out).not.toContain('<b>')
  })

  test('\\href 的 javascript: URI 不会变成可点击链接（未生成 <a>）', () => {
    const out = latexToHtml('\\href{javascript:alert(1)}{点我}')
    expect(out).not.toContain('<a ')
    expect(out).toContain('点我')
  })
})

describe('latexToHtml 正常渲染不受转义影响', () => {
  test('章节标题 / 加粗 / 行内数学照常渲染', () => {
    const out = latexToHtml('\\section{引言}\n\n\\textbf{核心} 结论 $p<0.05$ 显著。')
    expect(out).toContain('<h2')
    expect(out).toContain('引言')
    expect(out).toContain('<strong>核心</strong>')
    expect(out).toContain('p&lt;0.05')
  })

  test('列表环境照常渲染', () => {
    const out = latexToHtml('\\begin{itemize}\n\\item 第一\n\\item 第二\n\\end{itemize}')
    expect(out).toContain('<ul')
    expect(out).toContain('<li>')
    expect(out).toContain('第一')
  })

  test('LaTeX 转义字符照常还原（\\& → &）', () => {
    const out = latexToHtml('A \\& B')
    expect(out).toContain('&amp;')
  })
})
