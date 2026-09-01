/**
 * 将 LaTeX 源码转换为可读的 HTML 文本
 * 使用简单的正则替换，不依赖外部库
 * 专注在让用户能读懂内容，不需要完美渲染所有 LaTeX
 */

function escapeHtml(str: string): string {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

export function latexToHtml(latex: string): string {
  // 安全不变式：先整体 HTML 转义，再做 LaTeX→HTML 变换。
  // 后续所有替换注入的都是本文件内的已知安全标签，捕获组内容永远是已转义文本，
  // 因此章节内容（LLM 生成 / 用户编辑）中的 <script>、事件属性等无法进入 DOM。
  let html = escapeHtml(latex)

  // ── 0. 保护 verbatim / lstlisting 环境 ──
  const verbatimBlocks: string[] = []
  html = html.replace(
    /\\begin\{(verbatim|lstlisting)\}[\s\S]*?\\end\{\1\}/g,
    (match) => {
      // 提取内容（去掉 \begin 和 \end 行）；输入已整体转义，无需再次 escapeHtml
      const content = match
        .replace(/\\begin\{(verbatim|lstlisting)\}\s*\n?/, '')
        .replace(/\\end\{(verbatim|lstlisting)\}\s*$/, '')
      const idx = verbatimBlocks.length
      verbatimBlocks.push(
        `<pre class="bg-panel p-2 rounded text-xs font-mono overflow-x-auto my-2">${content}</pre>`
      )
      // 占位符不能用 % 开头：会被步骤 1 的 LaTeX 注释清除规则误删（存量 bug）。
      return `@@VERBATIM_${idx}@@`
    }
  )

  // ── 1. 移除注释 ──
  html = html.replace(/^[ \t]*%.*$/gm, '')

  // ── 2. 移除 preamble 命令 ──
  html = html.replace(/\\documentclass(\[[^\]]*\])?\{[^}]*\}/g, '')
  html = html.replace(/\\usepackage(\[[^\]]*\])?\{[^}]*\}/g, '')
  html = html.replace(
    /\\newcommand(\[[^\]]*\])?\{[^}]*\}(\[[\d]+\])?\{[^}]*\}/g,
    ''
  )
  html = html.replace(/\\renewcommand(\[[^\]]*\])?\{[^}]*\}(\[[\d]+\])?\{[^}]*\}/g, '')
  html = html.replace(/\\newenvironment(\[[^\]]*\])?\{[^}]*\}/g, '')
  html = html.replace(/\\begin\{document\}/g, '')
  html = html.replace(/\\end\{document\}/g, '')
  html = html.replace(/\\maketitle/g, '')
  html = html.replace(/\\thispagestyle\{[^}]*\}/g, '')
  html = html.replace(/\\setcounter\{[^}]*\}\{[^}]*\}/g, '')
  html = html.replace(/\\addtocounter\{[^}]*\}\{[^}]*\}/g, '')
  html = html.replace(/\\bibliographystyle\{[^}]*\}/g, '')
  html = html.replace(/\\bibliography\{[^}]*\}/g, '')

  // ── 3. 标题／作者／日期 ──
  html = html.replace(
    /\\title\{([^}]*)\}/g,
    '<h1 class="text-xl font-bold mt-4 mb-2 text-accent">$1</h1>'
  )
  html = html.replace(
    /\\author\{([^}]*)\}/g,
    '<p class="text-sm text-muted mt-1 mb-1">作者：$1</p>'
  )
  html = html.replace(
    /\\date\{([^}]*)\}/g,
    '<p class="text-sm text-muted mb-3">日期：$1</p>'
  )

  // ── 4. 章节标题 ──
  html = html.replace(
    /\\chapter\*?\{([^}]*)\}/g,
    '<h1 class="text-lg font-bold mt-6 mb-3 text-ink">$1</h1>'
  )
  html = html.replace(
    /\\section\*?\{([^}]*)\}/g,
    '<h2 class="text-base font-bold mt-5 mb-2 text-ink border-b border-border pb-1">$1</h2>'
  )
  html = html.replace(
    /\\subsection\*?\{([^}]*)\}/g,
    '<h3 class="text-sm font-bold mt-4 mb-1 text-ink">$1</h3>'
  )
  html = html.replace(
    /\\subsubsection\*?\{([^}]*)\}/g,
    '<h4 class="text-sm font-semibold mt-3 mb-1 text-muted">$1</h4>'
  )
  html = html.replace(
    /\\paragraph\*?\{([^}]*)\}/g,
    '<p class="font-semibold mt-2 mb-1">$1</p>'
  )

  // ── 5. 内联文本格式 ──
  html = html.replace(/\\textbf\{([^}]*)\}/g, '<strong>$1</strong>')
  html = html.replace(/\\textit\{([^}]*)\}/g, '<em>$1</em>')
  html = html.replace(/\\underline\{([^}]*)\}/g, '<u>$1</u>')
  html = html.replace(/\\emph\{([^}]*)\}/g, '<em>$1</em>')
  html = html.replace(
    /\\texttt\{([^}]*)\}/g,
    '<code class="bg-panel px-1 rounded text-xs font-mono">$1</code>'
  )
  html = html.replace(
    /\\textsc\{([^}]*)\}/g,
    '<span class="uppercase tracking-wider text-xs">$1</span>'
  )

  // ── 6. 引用／标签 ──
  html = html.replace(/\\label\{[^}]*\}/g, '')
  html = html.replace(
    /\\ref\{([^}]*)\}/g,
    '<span class="text-accent">[$1]</span>'
  )
  html = html.replace(
    /\\cite\{([^}]*)\}/g,
    '<span class="text-accent">[$1]</span>'
  )
  html = html.replace(
    /\\pageref\{([^}]*)\}/g,
    '<span class="text-accent">[$1页]</span>'
  )

  // ── 7. 列表环境 ──
  html = html.replace(
    /\\begin\{itemize\}/g,
    '<ul class="list-disc pl-6 space-y-1 my-2">'
  )
  html = html.replace(/\\end\{itemize\}/g, '</li></ul>')
  html = html.replace(
    /\\begin\{enumerate\}/g,
    '<ol class="list-decimal pl-6 space-y-1 my-2">'
  )
  html = html.replace(/\\end\{enumerate\}/g, '</li></ol>')
  // \item[label] → <li><strong>label</strong>
  html = html.replace(
    /\\item\[([^\]]*)\]\s*/g,
    '</li><li><strong>$1</strong> '
  )
  // \item → <li>
  html = html.replace(/\\item\s*/g, '</li><li>')
  // 修复第一个 <li> 前的空 </li>
  html = html.replace(
    /<ul class="list-disc pl-6 space-y-1 my-2"><\/li>/g,
    '<ul class="list-disc pl-6 space-y-1 my-2"><li>'
  )
  html = html.replace(
    /<ol class="list-decimal pl-6 space-y-1 my-2"><\/li>/g,
    '<ol class="list-decimal pl-6 space-y-1 my-2"><li>'
  )

  // ── 8. 数学环境 ──
  html = html.replace(
    /\\begin\{equation\*\}/g,
    '<div class="my-6 flex items-center justify-center rounded-lg bg-[#f3f3f3] px-5 py-3.5 text-center font-mono text-sm overflow-x-auto">'
  )
  html = html.replace(/\\end\{equation\*\}/g, '</div>')
  html = html.replace(
    /\\begin\{equation\}/g,
    '<div class="my-6 flex items-center justify-center rounded-lg bg-[#f3f3f3] px-5 py-3.5 text-center font-mono text-sm overflow-x-auto">'
  )
  html = html.replace(/\\end\{equation\}/g, '</div>')
  html = html.replace(
    /\\begin\{align\*\}/g,
    '<div class="my-6 rounded-lg bg-[#f3f3f3] px-5 py-3.5 font-mono text-sm overflow-x-auto">'
  )
  html = html.replace(/\\end\{align\*\}/g, '</div>')
  html = html.replace(
    /\\begin\{align\}/g,
    '<div class="my-6 rounded-lg bg-[#f3f3f3] px-5 py-3.5 font-mono text-sm overflow-x-auto">'
  )
  html = html.replace(/\\end\{align\}/g, '</div>')
  html = html.replace(
    /\\begin\{gather\*\}/g,
    '<div class="my-6 rounded-lg bg-[#f3f3f3] px-5 py-3.5 font-mono text-sm overflow-x-auto">'
  )
  html = html.replace(/\\end\{gather\*\}/g, '</div>')
  html = html.replace(
    /\\begin\{gather\}/g,
    '<div class="my-6 rounded-lg bg-[#f3f3f3] px-5 py-3.5 font-mono text-sm overflow-x-auto">'
  )
  html = html.replace(/\\end\{gather\}/g, '</div>')
  html = html.replace(
    /\\\[\s*/g,
    '<div class="my-6 flex items-center justify-center rounded-lg bg-[#f3f3f3] px-5 py-3.5 text-center font-mono text-sm overflow-x-auto">'
  )
  html = html.replace(/\s*\\\]/g, '</div>')
  html = html.replace(
    /\$\$([\s\S]*?)\$\$/g,
    '<div class="my-6 rounded-lg bg-[#f3f3f3] px-5 py-3.5 text-center font-mono text-sm">$1</div>'
  )
  html = html.replace(
    /\$([^$\n]*?)\$/g,
    '<span class="font-mono text-sm text-accent">$1</span>'
  )

  // ── 9. Abstract ──
  html = html.replace(
    /\\begin\{abstract\}/g,
    '<div class="my-3 p-3 border-l-2 border-accent bg-panel rounded italic text-sm">'
  )
  html = html.replace(/\\end\{abstract\}/g, '</div>')

  // ── 10. 表格 ──
  html = html.replace(
    /\\begin\{tabular\}(\[[^\]]*\])?\{[^}]*\}/g,
    '<div class="my-2 font-mono text-xs bg-panel rounded p-2 overflow-x-auto">'
  )
  html = html.replace(/\\end\{tabular\}/g, '</div>')
  html = html.replace(
    /\\begin\{table\}(\[[^\]]*\])?/g,
    '<div class="my-3">'
  )
  html = html.replace(/\\end\{table\}/g, '</div>')
  html = html.replace(
    /\\caption\{([^}]*)\}/g,
    '<p class="text-xs text-center text-muted mt-1">表：$1</p>'
  )
  html = html.replace(/\\hline/g, '')

  // ── 11. 图片 ──
  html = html.replace(
    /\\includegraphics(\[[^\]]*\])?\{[^}]*\}/g,
    '<span class="text-accent text-xs">[图片]</span>'
  )
  html = html.replace(
    /\\begin\{figure\}(\[[^\]]*\])?/g,
    '<div class="my-3">'
  )
  html = html.replace(/\\end\{figure\}/g, '</div>')

  // ── 12. 参考文献 ──
  html = html.replace(
    /\\begin\{thebibliography\}\{[^}]*\}/g,
    '<div class="my-4 pt-3 border-t border-border"><h3 class="font-bold text-sm mb-2">参考文献</h3>'
  )
  html = html.replace(/\\end\{thebibliography\}/g, '</div>')
  html = html.replace(
    /\\bibitem\{([^}]*)\}/g,
    '<div class="text-xs my-1 pl-4 -indent-4">[$1] '
  )

  // ── 13. 居中 ──
  html = html.replace(/\\centering/g, '')
  html = html.replace(
    /\\begin\{center\}/g,
    '<div class="text-center my-2">'
  )
  html = html.replace(/\\end\{center\}/g, '</div>')

  // ── 14. 移除剩余未处理的 \begin{...} / \end{...} ──
  html = html.replace(/\\begin\{[^}]*\}\s*/g, '')
  html = html.replace(/\\end\{[^}]*\}\s*/g, '')

  // ── 15. 移除剩余未处理的 LaTeX 命令（有参数时保留参数内容） ──
  // 处理 \command{content} 形式 → 保留 content
  html = html.replace(/\\([a-zA-Z]+)\*?(\[[^\]]*\])?\{([^}]*)\}/g, '$3')
  // 处理 \command[opt]{content} 形式
  html = html.replace(/\\([a-zA-Z]+)\*?(\[[^\]]*\])?/g, '')

  // ── 16. 特殊字符 ──
  html = html.replace(/\\%/g, '%')
  html = html.replace(/\\&amp;/g, '&amp;')
  html = html.replace(/\\#/g, '#')
  html = html.replace(/\\_/g, '_')
  html = html.replace(/\\\$/g, '$')
  html = html.replace(/\\\{/g, '{')
  html = html.replace(/\\\}/g, '}')
  html = html.replace(/\\textbackslash\s*/g, '\\')
  html = html.replace(/\\textasciitilde\s*/g, '~')
  html = html.replace(/\\textasciicircum\s*/g, '^')

  // ── 17. 行内分隔符 ──
  html = html.replace(/\\~/g, ' ')
  html = html.replace(/\\,/g, ' ')
  html = html.replace(/\\;/g, ' ')
  html = html.replace(/\\!/g, '')
  html = html.replace(/\\@/g, '')
  html = html.replace(/\\\s+/g, ' ')

  // ── 18. 换行 ──
  html = html.replace(/\\\\/g, '\n')

  // ── 19. 恢复 verbatim 块 ──
  html = html.replace(/@@VERBATIM_(\d+)@@/g, (_, idx) => {
    return verbatimBlocks[parseInt(idx)] || ''
  })

  // ── 20. 段落包装 ──
  const blockTagRe = /^<(h[1-4]|ul|ol|div|pre|table|p|blockquote)/
  // 用双换行分割，保留结构
  const paragraphs = html.split(/\n{2,}/)
  html = paragraphs
    .map((p) => p.trim())
    .filter((p) => p.length > 0)
    .map((p) => {
      // 如果已经是块级元素开头，不额外包装
      if (blockTagRe.test(p)) return p
      // 纯空白行跳过
      return `<p class="mb-2 leading-relaxed">${p}</p>`
    })
    .join('\n')

  return html
}