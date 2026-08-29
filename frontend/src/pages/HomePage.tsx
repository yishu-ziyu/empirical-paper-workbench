/* 首页 = 产品的第一个交互面。构图对齐 Elicit：居中对称、衬线大标题、
 * 大量留白——但主视觉不是 CTA 按钮，而是对话输入框本身（进来就能说话）。
 * 上传/示例是对话中的动作，不是首页按钮。
 * Hallmark · genre: editorial · design-system: DESIGN.md · designed-as-app
 */
import { useEffect, useState } from 'react'
import { useT } from '../lib/i18n'
import DirectionChat from '../components/DirectionChat'

export interface HomePageProps {
  uploading?: boolean
  uploadError?: string | null
  onPickData: () => void
  onTrySample: () => void
  onLogin?: () => void
}

const EXAMPLES = [
  '我导师让我看加州的烟草税政策，想拿它练手',
  '最低工资上调之后，低收入岗位发生了什么？',
  '感觉数字经济影响了工资，但不知道怎么问',
]

export default function HomePage({
  uploading = false,
  uploadError = null,
  onPickData,
  onTrySample,
  onLogin,
}: HomePageProps) {
  const { t, lang, setLang } = useT()
  const [started, setStarted] = useState(false)
  const [play, setPlay] = useState(false)
  useEffect(() => {
    // 挂载即开始描线（rAF 在后台标签页被冻结，不能依赖）
    const id = window.setTimeout(() => setPlay(true), 30)
    return () => window.clearTimeout(id)
  }, [])

  // DirectionChat 发出第一条消息后，海报态收起、对话态接管
  function handleFirstSend() {
    setStarted(true)
  }

  return (
    <div
      data-testid="home-page"
      className={`relative flex min-h-[100svh] flex-col overflow-hidden bg-bg text-ink ${play ? 'is-play' : ''}`}
    >
      {/* 图纸层：识别策略图纸还在画（低对比、不接事件，Will's S：先做事不打扰） */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-0">
        <div className="blueprint-dots" />
        <div className="blueprint-glow" />
        <div className="blueprint-rail-y" />
        <div className="blueprint-rail-x" />
        <div className="blueprint-pin" />
      </div>
      <header className="relative z-10 flex items-center justify-between px-6 py-5 sm:px-10 lg:px-16">
        <p className="font-serif text-[17px] tracking-tight">econpaper</p>
        <div className="flex items-center gap-5 text-[13px] text-muted">
          {onLogin && (
            <button
              type="button"
              data-testid="open-login-btn"
              onClick={onLogin}
              className="transition-colors duration-150 hover:text-ink"
            >
              {t('app.login')}
            </button>
          )}
          <button
            type="button"
            onClick={() => setLang(lang === 'zh' ? 'en' : 'zh')}
            className="transition-colors duration-150 hover:text-ink"
          >
            {t('app.langSwitch')}
          </button>
        </div>
      </header>

      {/* 居中英雄区：衬线大标题 + 副题（首条消息发出后收起，让位给对话） */}
      {!started && (
        <div className="relative z-10 mx-auto flex w-full max-w-[880px] flex-col items-center px-6 pt-[9svh] text-center">
          <h1 className="font-serif text-[clamp(2.6rem,6.2vw,4.25rem)] leading-[1.12] tracking-tight">
            {t('home.heading')}
          </h1>
          <p className="mt-4 max-w-[30em] text-[16.5px] leading-7 text-muted">
            {t('home.sub')}
          </p>
        </div>
      )}

      {/* 对话输入：主页的主视觉（居中、加宽、白色面板） */}
      <div className={`relative z-10 mx-auto w-full max-w-[680px] px-6 ${started ? 'pt-8' : 'pt-9'}`}>
        <DirectionChat
          columns={[]}
          hero={!started}
          fillHeight={started}
          hasData={false}
          onSubmit={() => {
            /* 首页无会话：确认走"给数据"流程，提交在进桌后的卡上完成 */
          }}
          onFirstSend={handleFirstSend}
        />
      </div>

      {/* 示例念头芯片（居中，未开始时展示） */}
      {!started && (
        <div className="relative z-10 mx-auto mt-5 flex w-full max-w-[680px] flex-wrap items-center justify-center gap-2 px-6">
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              type="button"
              onClick={() => {
                const input = document.querySelector('[data-testid="direction-chat-input"]')
                if (!input) return
                Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(input, ex)
                input.dispatchEvent(new Event('input', { bubbles: true }))
                input.focus()
              }}
              className="rounded-full border border-border bg-panel px-3.5 py-1.5 text-left text-[12.5px] text-muted transition-colors duration-150 hover:border-accent/40 hover:text-ink"
            >
              {ex}
            </button>
          ))}
        </div>
      )}

      {/* 数据入口：对话中的动作（居中一行，上传 / 示例） */}
      <div
        data-testid="home-data-row"
        className="mx-auto mt-auto flex w-full max-w-[680px] flex-wrap items-center justify-center gap-3 px-6 pb-10 pt-10 text-[12.5px] text-muted"
      >
        <span>{t('home.dataRow')}</span>
        <button
          type="button"
          data-testid="home-upload-btn"
          onClick={onPickData}
          disabled={uploading}
          className="rounded-full border border-border bg-panel px-3.5 py-1.5 text-[12.5px] text-ink transition-colors duration-150 hover:border-accent/40 disabled:opacity-50"
        >
          {uploading ? t('app.uploading') : t('home.upload')}
        </button>
        <button
          type="button"
          data-testid="home-sample-btn"
          onClick={onTrySample}
          disabled={uploading}
          className="rounded-full border border-border bg-panel px-3.5 py-1.5 text-[12.5px] text-ink transition-colors duration-150 hover:border-accent/40 disabled:opacity-50"
        >
          {t('home.sample')}
        </button>
        {uploadError && (
          <span data-testid="upload-error" className="text-danger">
            {uploadError}
          </span>
        )}
      </div>
    </div>
  )
}
