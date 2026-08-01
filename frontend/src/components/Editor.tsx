// 中栏流式编辑器 - 接收 chunks 数组拼接显示，收到 interrupt 时显示暂停提示
// 打字机淡入效果（通过 key 变化触发 CSS 动画）+ 骨架屏加载态

import { useRef, useEffect, useState, useMemo } from 'react'
import { latexToHtml } from '../lib/latexToHtml'
import { useT } from '../lib/i18n'

export interface EditorProps {
  chapterId?: string
  chunks?: string[]
  interrupt?: string
  /** 是否正在生成（显示骨架屏占位） */
  generating?: boolean
  /** F7: Whether any degradation has occurred */
  degraded?: boolean
  /** F7: List of degradation records */
  degradations?: Array<{
    node: string
    reason: string
    fallback: string
    timestamp: string
  }>
  /** 用户确认继续生成 */
  onContinue?: () => void
  /** 用户点击修改标题 */
  onEditTitle?: (currentTitle: string) => void
}

export default function Editor({ chunks = [], interrupt, generating, degraded, degradations = [], onContinue, onEditTitle }: EditorProps) {
  const { t } = useT()
  const content = chunks.join('')
  const prevContentRef = useRef('')
  const [animKey, setAnimKey] = useState(0)
  const [showRaw, setShowRaw] = useState(false)

  // 判断内容是否包含 LaTeX 命令
  const hasLatex = useMemo(() => /\\[a-zA-Z]+(\{|\[)/.test(content), [content])

  // 格式化后的 HTML
  const formattedHtml = useMemo(() => {
    if (!content) return ''
    return latexToHtml(content)
  }, [content])

  // 内容变化时触发重渲染动画
  useEffect(() => {
    if (content !== prevContentRef.current) {
      prevContentRef.current = content
      setAnimKey((k) => k + 1)
    }
  }, [content])

  return (
    <div
      data-testid="editor-content"
      className="min-h-[60vh] rounded border border-border bg-paper p-6 text-sm"
    >
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xs uppercase tracking-wider text-muted font-mono">{t('editor.title')}</h2>

        {/* LaTeX 格式化切换按钮 */}
        {hasLatex && content && (
          <button
            type="button"
            onClick={() => setShowRaw((v) => !v)}
            className="rounded border border-border px-2 py-1 font-serif text-xs text-ink transition-colors hover:bg-panel"
          >
            {showRaw ? t('editor.showFormatted') : t('editor.showRaw')}
          </button>
        )}
      </div>

      {/* 无内容且未生成 → 空态引导 */}
      {!content && !interrupt && !generating && (
        <div className="flex flex-col items-center justify-center py-16 text-muted">
          <svg
            className="mb-4 h-12 w-12 opacity-30"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"
            />
          </svg>
          <p className="text-sm">{t('editor.emptyHint')}</p>
          <p className="mt-1 text-xs opacity-60">{t('editor.emptyDesc')}</p>
        </div>
      )}

      {/* 骨架屏（生成中且无内容时显示） */}
      {generating && !content && !interrupt && (
        <div className="space-y-3" data-testid="skeleton-screen">
          <div className="animate-skeleton h-4 w-3/4" />
          <div className="animate-skeleton h-4 w-full" />
          <div className="animate-skeleton h-4 w-5/6" />
          <div className="animate-skeleton h-4 w-2/3" />
          <div className="animate-skeleton h-4 w-full" />
          <div className="animate-skeleton h-4 w-4/5" />
        </div>
      )}

      {/* 正文内容 - 打字机淡入效果 */}
      {content && (
        <div
          key={animKey}
          className="font-serif leading-relaxed text-ink animate-fade-in"
        >
          {hasLatex && !showRaw ? (
            <div dangerouslySetInnerHTML={{ __html: formattedHtml }} />
          ) : (
            <div className="whitespace-pre-wrap">{content}</div>
          )}
        </div>
      )}

      {interrupt && (
        <div className="mt-4 animate-slide-up rounded border border-yellow-200 bg-yellow-50 p-4 text-yellow-800">
          <div className="flex items-center justify-between">
            <span className="font-mono text-xs uppercase tracking-wide">{t('editor.paused')}</span>
          </div>
          <p className="mt-1 text-sm">{t('editor.continueHint')}</p>
          <div className="mt-3 flex gap-2">
            <button
              type="button"
              onClick={onContinue}
              className="rounded bg-accent px-4 py-1.5 text-xs text-white transition-colors hover:bg-accent/90"
            >
              {t('editor.confirmContinue')}
            </button>
            <button
              type="button"
              onClick={() => onEditTitle?.(content)}
              className="rounded border border-border px-4 py-1.5 text-xs text-ink transition-colors hover:bg-panel"
            >
              {t('editor.editTitle')}
            </button>
          </div>
        </div>
      )}

      {/* F7: 降级详情（导出页面等场景） */}
      {degraded && degradations.length > 0 && (
        <div
          data-testid="degradation-details"
          className="mt-4 animate-slide-up rounded border border-yellow-200 bg-yellow-50 p-3 text-yellow-800"
        >
          <span className="font-mono text-xs uppercase tracking-wide">{t('editor.degradationTitle')}</span>
          <ul className="mt-2 space-y-1 text-xs">
            {degradations.map((d, i) => (
              <li key={i} className="text-yellow-700">
                <span className="font-mono">{d.node}</span> 使用 {d.fallback} 降级导出
                <br />
                <span className="text-yellow-500">{d.reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}