/* 方向对话：空桌的第一交互不再是表单，而是聊天。
 *
 * 用户用自然语言说念头 → /desk/design-chat 一轮轮追问（一次只问一件事）→
 * 已知设定即时回填到内嵌的"研究设定卡"（DirectionForm 原样保留，可随时手改）
 * → 卡上的提交键才是进入管线的门。跳过对话直接填表：右上角"直接填设定"。
 * Hallmark · design-system: DESIGN.md · designed-as-app
 */
import { useEffect, useRef, useState, type FormEvent } from 'react'
import { useT } from '../lib/i18n'
import DirectionForm, { type DirectionFormData } from './DirectionForm'

const API_BASE = 'http://localhost:8000'

type Turn = { role: 'user' | 'agent'; text: string }

export interface DirectionChatProps {
  columns?: string[]
  initialNotes?: string
  /** 第一条消息发出时回调（宿主切换界面状态用） */
  onFirstSend?: () => void
  /** 首页主视觉形态：输入框加大居中 */
  hero?: boolean
  /** 预填设定（样例方向 / 已知设定）：卡片直接以此打底，对话抽取在其上增量合并 */
  initial?: Partial<DirectionFormData>
  /** 占满可用高度（消息区滚动 + 输入钉底） */
  fillHeight?: boolean
  /** 数据是否已就位（决定"开始估计"按钮的行为） */
  hasData?: boolean
  onSubmit: (data: DirectionFormData) => void
  busy?: boolean
}

export default function DirectionChat({
  columns = [],
  initialNotes = '',
  initial,
  onSubmit,
  onFirstSend,
  hero = false,
  fillHeight = false,
  hasData = false,
  busy = false,
}: DirectionChatProps) {
  const { t } = useT()
  // 对话线持久化：刷新/跨视图切换后从 sessionStorage 恢复（同一条线不断）
  const saved = (() => {
    try {
      return JSON.parse(sessionStorage.getItem('econpaper_chat_thread') || 'null') as {
        notes?: string
        turns?: Turn[]
        design?: Partial<DirectionFormData>
        ready?: boolean
      } | null
    } catch {
      return null
    }
  })()
  const [notes, setNotes] = useState(initialNotes || saved?.notes || '')
  const [turns, setTurns] = useState<Turn[]>(saved?.turns ?? [])
  const [design, setDesign] = useState<Partial<DirectionFormData>>(saved?.design ?? initial ?? {})
  const [ready, setReady] = useState(Boolean(saved?.ready))
  const [need, setNeed] = useState('')
  const [thinking, setThinking] = useState(false)
  const [draft, setDraft] = useState('')
  const [formMode, setFormMode] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  // 问题先行页的交接：想法作为第一条消息自动发出（一次）
  const handoffRef = useRef(false)
  useEffect(() => {
    if (handoffRef.current) return
    handoffRef.current = true
    try {
      const handoff = JSON.parse(sessionStorage.getItem('econpaper_chat_handoff') || 'null') as { notes?: string } | null
      if (handoff?.notes && turns.length === 0) {
        setNotes(handoff.notes)
        sessionStorage.removeItem('econpaper_chat_handoff')
        void send(handoff.notes)
      }
    } catch {
      /* 无交接，正常空场 */
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function send(text: string) {
    const clean = text.trim()
    if (!clean || thinking) return
    const nextTurns: Turn[] = [...turns, { role: 'user' as const, text: clean }]
    if (turns.length === 0) onFirstSend?.()
    setTurns(nextTurns)
    setDraft('')
    setThinking(true)
    try {
      const resp = await fetch(`${API_BASE}/desk/design-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          notes: notes || nextTurns[0]?.text || '',
          turns: nextTurns.map((tn) => ({ role: tn.role, text: tn.text })),
          columns,
        }),
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const data = (await resp.json()) as {
        reply: string
        design: Partial<DirectionFormData>
        need: string
        ready: boolean
      }
      setTurns([...nextTurns, { role: 'agent', text: data.reply || data.need }])
      setDesign((prev) => ({ ...prev, ...cleanDesign(data.design) }))
      setNeed(data.need ?? '')
      setReady(Boolean(data.ready))
    } catch (err) {
      setTurns([
        ...nextTurns,
        { role: 'agent', text: t('directionChat.error') },
      ])
    } finally {
      setThinking(false)
      bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
    }
  }

  // 对话线存档：刷新/视图切换不丢
  useEffect(() => {
    if (!turns.length && !design.question) return
    try {
      sessionStorage.setItem(
        'econpaper_chat_thread',
        JSON.stringify({ notes, turns, design, ready }),
      )
    } catch {
      /* 存储满等异常静默 */
    }
  }, [turns, design, notes, ready])

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const data: DirectionFormData = {
      question: design.question ?? '',
      dv: design.dv ?? '',
      iv: design.iv ?? '',
      controls: design.controls ?? [],
      method: design.method ?? '',
      template: 'undergrad',
    }
    sessionStorage.removeItem('econpaper_chat_thread')
    sessionStorage.removeItem('econpaper_chat_handoff')
    onSubmit(data)
  }

  const knownFields: Array<[string, string | undefined]> = [
    [t('direction.question'), design.question],
    [t('direction.dv'), design.dv],
    [t('direction.iv'), design.iv],
    [t('direction.controls'), Array.isArray(design.controls) ? (design.controls as string[]).join('、') : (design.controls as string | undefined)],
    [t('direction.method'), design.method],
  ]
  const hasKnown = knownFields.some(([, v]) => Boolean(v))

  function requestStart() {
    // 设定齐了但还没数据：在对话流里要资源（Elicit 式"过程内要资源"）
    if (!hasData) {
      setTurns((prev) => [
        ...prev,
        { role: 'agent', text: t('directionChat.needData') },
      ])
      bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
      return
    }
    const data: DirectionFormData = {
      question: design.question ?? '',
      dv: design.dv ?? '',
      iv: design.iv ?? '',
      controls: design.controls ?? [],
      method: design.method ?? '',
      template: 'undergrad',
    }
    sessionStorage.removeItem('econpaper_chat_thread')
    sessionStorage.removeItem('econpaper_chat_handoff')
    onSubmit(data)
  }

  return (
    <div
      data-testid="direction-chat"
      className={`flex flex-col ${fillHeight ? 'h-[calc(100svh-140px)]' : ''}`}
    >
      {/* ── 消息滚动区 ── */}
      <div className={`flex flex-col gap-2.5 ${fillHeight ? 'flex-1 min-h-0 overflow-y-auto px-1' : ''}`}>
        {turns.map((turn, idx) =>
          turn.role === 'user' ? (
            <p
              key={idx}
              data-testid={idx === 0 ? 'chat-user-first' : undefined}
              className="self-end rounded-2xl rounded-br-sm bg-accent/10 px-3 py-2 text-[13.5px] leading-6 text-ink"
            >
              {turn.text}
            </p>
          ) : (
            <p
              key={idx}
              className="self-start rounded-2xl rounded-bl-sm border border-border bg-panel px-3 py-2 font-serif text-[14px] leading-6 text-ink"
            >
              {turn.text}
            </p>
          ),
        )}
        {thinking && (
          <p className="self-start font-mono text-[12px] text-muted">{t('directionChat.thinking')}</p>
        )}
        <div ref={bottomRef} />
      </div>

      {/* 输入行 */}
      <form
        className="mt-3 flex items-end gap-2"
        onSubmit={(e: FormEvent) => {
          e.preventDefault()
          void send(draft)
        }}
      >
        <textarea
          data-testid="direction-chat-input"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              void send(draft)
            }
          }}
          rows={hero ? 2 : 2}
          placeholder={turns.length === 0 ? t('directionChat.placeholder') : t('directionChat.placeholderNext')}
          className={`flex-1 resize-none rounded-xl border border-border bg-white ${hero ? 'p-4 text-[15px] leading-7' : 'p-2.5 text-[13.5px] leading-6'} transition-colors duration-150 focus:border-accent focus:outline-none`}
        />
        <button
          type="submit"
          disabled={!draft.trim() || thinking}
          className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors duration-150 hover:bg-accent/90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {t('directionChat.send')}
        </button>
      </form>
      {/* ── 研究设定摘要卡（紧凑只读行；点"展开编辑"才露出完整表单）── */}
      {!hasKnown && (
        <button
          type="button"
          data-testid="direction-chat-to-form"
          onClick={() => setFormMode(true)}
          className="mr-auto mt-1.5 text-[11px] text-muted transition-colors duration-150 hover:text-ink"
        >
          {t('directionChat.skipToForm')}
        </button>
      )}
      {(hasKnown || formMode) && (
        <section
          data-testid="direction-design-card"
          className={`mr-auto w-full max-w-[560px] rounded-xl border bg-panel px-3.5 py-3 ${
            ready ? 'border-accent/40' : 'border-border'
          }`}
        >
          <div className="flex items-center justify-between gap-3">
            <p className="font-serif text-[13.5px] text-ink">
              {t('directionChat.cardTitle')}
              {ready && <span className="ml-2 font-mono text-[11px] text-accent">{t('directionChat.ready')}</span>}
            </p>
            <button
              type="button"
              data-testid="direction-chat-to-form"
              onClick={() => setFormMode((v) => !v)}
              className="shrink-0 text-[11px] text-muted transition-colors duration-150 hover:text-ink"
            >
              {formMode ? t('directionChat.collapse') : t('directionChat.expandEdit')}
            </button>
          </div>
          {!formMode && (
            <dl className="mt-2 grid grid-cols-[64px_1fr] gap-x-3 gap-y-1 text-[12.5px] leading-5">
              {knownFields.map(([label, value]) => (
                <div key={label} className="contents">
                  <dt className="text-muted">{label}</dt>
                  <dd className={value ? 'text-ink' : 'text-muted/60'}>
                    {value || t('directionChat.pending')}
                  </dd>
                </div>
              ))}
            </dl>
          )}
          {formMode && (
            <div className="mt-2 border-t border-border pt-2">
              <DirectionForm
                key={JSON.stringify([design.question, design.dv, design.iv, design.method])}
                columns={columns}
                initial={{
                  question: design.question,
                  dv: design.dv,
                  iv: design.iv,
                  controls: Array.isArray(design.controls) ? (design.controls as string[]).join(', ') : '',
                  method: design.method,
                }}
                onSubmit={onSubmit}
              />
            </div>
          )}
          {ready && (
            <button
              type="button"
              data-testid="direction-start-btn"
              onClick={requestStart}
              className="mt-3 w-full rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white transition-colors duration-150 hover:bg-accent/90"
            >
              {hasData ? t('directionChat.start') : t('directionChat.needDataToStart')}
            </button>
          )}
        </section>
      )}
      {busy && <p className="mt-2 text-xs text-muted">{t('app.directionWorking')}</p>}
    </div>
  )
}

function cleanDesign(raw: Partial<DirectionFormData> | undefined): Partial<DirectionFormData> {
  if (!raw) return {}
  const out: Partial<DirectionFormData> = {}
  if (raw.question) out.question = raw.question
  if (raw.dv) out.dv = raw.dv
  if (raw.iv) out.iv = raw.iv
  if (Array.isArray(raw.controls) && raw.controls.length) out.controls = raw.controls
  if (raw.method) out.method = raw.method
  return out
}
