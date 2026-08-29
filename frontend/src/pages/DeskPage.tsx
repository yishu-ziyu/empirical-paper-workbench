import { useEffect, useRef, useState } from 'react'
import { useT } from '../lib/i18n'
import { discussDesk, speakDesk, transcribeDesk } from '../lib/deskDiscuss'
import type { DeskCard, DeskTurn } from '../lib/deskDiscuss'
import { nextPrompt, shapeQuestion } from '../lib/shapeQuestion'
import type { ShapeAnswers } from '../lib/shapeQuestion'
import { appendTranscript } from '../lib/voice'
import type { VoiceStatus } from '../lib/voice'

export interface DeskPageProps {
  onConfirm: (title: string) => void
  onPickData: () => void
  uploading?: boolean
  uploadError?: string | null
  onLogin?: () => void
  onRegister?: () => void
  authed?: boolean
}

const IDLE_MS = 1400

function shortLabel(label: string): string {
  return label.replace(/（.*?）|\(.*?\)/g, '').trim() || label
}

function localCard(notes: string, answers: ShapeAnswers): DeskCard {
  const draft = shapeQuestion(notes, answers)
  const prompt = nextPrompt(answers)
  return {
    reflection: draft.reflection,
    title: draft.title,
    heard: draft.heard.map((item) => item.label),
    comparison: draft.comparison,
    outcome: draft.outcome,
    question: draft.ready || !prompt ? '' : prompt.question,
    options: draft.ready || !prompt ? [] : prompt.options,
    explain: '',
    ready: draft.ready,
    source: 'heuristic',
  }
}

export default function DeskPage({
  onConfirm,
  onPickData,
  uploading = false,
  uploadError = null,
  onLogin,
  onRegister,
  authed,
}: DeskPageProps) {
  const { t } = useT()
  const [text, setText] = useState('')
  const [turns, setTurns] = useState<DeskTurn[]>([])
  const [card, setCard] = useState<DeskCard | null>(null)
  const [titleOverride, setTitleOverride] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [voiceStatus, setVoiceStatus] = useState<VoiceStatus>('idle')
  const [speaking, setSpeaking] = useState(false)
  const [asking, setAsking] = useState(false)
  const [askText, setAskText] = useState('')
  const [asked, setAsked] = useState('')
  const [agentPane, setAgentPane] = useState<'shape' | 'clean' | 'estimate' | 'write'>('shape')
  const paperRef = useRef<HTMLTextAreaElement>(null)
  const timerRef = useRef<number | null>(null)
  const mediaRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const lastSpokenRef = useRef('')
  const requestRef = useRef(0)

  const title = titleOverride ?? card?.title ?? ''
  const canShape = text.trim().length >= 6

  // 未登录点「开始」会先去注册/登录；想法暂存 sessionStorage，回来即恢复
  useEffect(() => {
    const draft = sessionStorage.getItem('desk_idea_draft')
    if (draft && !text) {
      handleChange(draft)
      sessionStorage.removeItem('desk_idea_draft')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function growPaper() {
    const el = paperRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.max(220, el.scrollHeight)}px`
  }

  async function askModel(notes: string, nextTurns: DeskTurn[]) {
    const ticket = requestRef.current + 1
    requestRef.current = ticket
    setBusy(true)
    try {
      const next = await discussDesk(notes, nextTurns)
      if (requestRef.current !== ticket) return
      setCard(next)
      setTitleOverride(null)
      setAsking(false)
    } catch {
      if (requestRef.current !== ticket) return
      const askedNow = [...nextTurns].reverse().find((item) => item.id === 'ask')
      if (askedNow) {
        setAsking(true)
        return
      }
      const answers: ShapeAnswers = {}
      for (const turn of nextTurns) {
        if (turn.id === 'policy' || turn.id === 'who' || turn.id === 'gap') answers.compare = turn.id
        if (turn.id === 'work' || turn.id === 'wage' || turn.id === 'health') answers.outcome = turn.id
      }
      setCard(localCard(notes, answers))
      setTitleOverride(null)
      setAsking(false)
    } finally {
      if (requestRef.current === ticket) setBusy(false)
    }
  }

  function handleChange(value: string) {
    setText(value)
    if (timerRef.current) window.clearTimeout(timerRef.current)
    if (value.trim().length < 6) {
      setCard(null)
      setTurns([])
      setTitleOverride(null)
      return
    }
    timerRef.current = window.setTimeout(() => {
      void askModel(value, turns)
    }, IDLE_MS)
  }

  function choose(optionId: string, label: string) {
    if (timerRef.current) window.clearTimeout(timerRef.current)
    const nextTurns = [
      ...turns,
      { question: card?.question || '', answer: label, id: optionId },
    ]
    setTurns(nextTurns)
    setAsking(false)
    setAskText('')
    setAsked('')
    void askModel(text, nextTurns)
  }

  function askAboutOptions() {
    const note = askText.trim() || '这几个选项分别是什么意思？我该怎么选？'
    if (timerRef.current) window.clearTimeout(timerRef.current)
    const nextTurns = [
      ...turns,
      { question: card?.question || '', answer: note, id: 'ask' },
    ]
    setTurns(nextTurns)
    setAsked(note)
    void askModel(text, nextTurns)
  }

  function stopPlayback() {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    setSpeaking(false)
  }

  async function finishListening(chunks: Blob[]) {
    setVoiceStatus('idle')
    if (!chunks.length) return
    setBusy(true)
    try {
      const blob = new Blob(chunks, { type: chunks[0]?.type || 'audio/webm' })
      const heard = await transcribeDesk(blob)
      if (!heard) return
      handleChange(appendTranscript(text, heard))
    } catch {
      setVoiceStatus('unsupported')
    } finally {
      setBusy(false)
    }
  }

  async function startListening() {
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') {
      setVoiceStatus('unsupported')
      return
    }
    stopPlayback()
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream)
      chunksRef.current = []
      recorder.ondataavailable = (ev) => {
        if (ev.data.size > 0) chunksRef.current.push(ev.data)
      }
      recorder.onstop = () => {
        stream.getTracks().forEach((track) => track.stop())
        mediaRef.current = null
        void finishListening(chunksRef.current)
      }
      mediaRef.current = recorder
      recorder.start()
      setVoiceStatus('listening')
    } catch {
      setVoiceStatus('denied')
    }
  }

  function stopListening() {
    const recorder = mediaRef.current
    if (recorder && recorder.state !== 'inactive') recorder.stop()
    else setVoiceStatus('idle')
  }

  function toggleListen() {
    if (voiceStatus === 'listening') stopListening()
    else void startListening()
  }

  async function speakLine(line: string) {
    const next = line.trim()
    if (!next) return
    if (speaking && lastSpokenRef.current === next) {
      stopPlayback()
      return
    }
    lastSpokenRef.current = next
    stopPlayback()
    setSpeaking(true)
    try {
      const audio = await speakDesk(next)
      audioRef.current = audio
      audio.onended = () => setSpeaking(false)
      audio.onerror = () => setSpeaking(false)
      await audio.play()
    } catch {
      setSpeaking(false)
    }
  }

  useEffect(() => {
    growPaper()
  }, [text])

  useEffect(() => {
    paperRef.current?.focus()
    return () => {
      if (timerRef.current) window.clearTimeout(timerRef.current)
      if (mediaRef.current && mediaRef.current.state !== 'inactive') mediaRef.current.stop()
      stopPlayback()
    }
  }, [])

  const listenLabel =
    voiceStatus === 'listening'
      ? t('desk.stopListen')
      : voiceStatus === 'unsupported'
        ? t('desk.voiceUnsupported')
        : voiceStatus === 'denied'
          ? t('desk.voiceDenied')
          : t('desk.listen')

  const paneTitle =
    agentPane === 'clean'
      ? '清洗 8 步 · audit 留痕'
      : agentPane === 'estimate'
        ? '估计门 · 主表会出现在这里'
        : agentPane === 'write'
          ? '按章写作 · 串行 HITL'
          : '方向凝练 · 可追溯'

  return (
    <div data-testid="desk-page" className="flex h-screen min-h-0 bg-white text-ink">
      <aside className="flex w-56 shrink-0 flex-col border-r border-black/[0.06] p-3">
        <div className="mb-3 flex items-center justify-between px-1">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-ink font-serif text-[15px] text-white">
            e
          </span>
        </div>
        <button
          type="button"
          className="mb-3 flex items-center gap-2 rounded-[10px] bg-[#f7f8fa] px-3 py-2 text-left text-[13.5px]"
        >
          <span className="flex h-[18px] w-[18px] items-center justify-center rounded-full border border-[#4e5969] text-[12px] leading-none">
            +
          </span>
          新论文
        </button>
        <p className="px-2 pb-1 pt-2 text-[12px] text-[#86909c]">论文</p>
        <div className="min-h-0 flex-1 overflow-y-auto text-[13.5px]">
          <div className="rounded-lg bg-[#f2f3f5] px-2.5 py-1.5 font-medium">
            {title || t('desk.heading')}
          </div>
          <div className="px-2.5 py-1.5 text-[#4e5969]">课设样例：年龄与收入</div>
        </div>
        <p className="px-2 pb-1 pt-3 text-[12px] text-[#86909c]">数据</p>
        <button
          type="button"
          onClick={onPickData}
          disabled={uploading}
          className="rounded-lg px-2.5 py-1.5 text-left text-[13.5px] hover:bg-[#f7f8fa] disabled:opacity-50"
        >
          ＋ {uploading ? t('app.uploading') : t('desk.uploadCta')}
        </button>
        <div className="mt-auto flex items-center gap-2 border-t border-black/[0.06] pt-2.5">
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-ink text-[12px] text-white">
            e
          </span>
          <span className="text-[13px] font-medium">econpaper</span>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 shrink-0 items-center justify-between border-b border-black/[0.06] px-6">
          <p className="text-[14px] font-medium">{title || t('desk.heading')}</p>
          <div className="flex items-center gap-3 text-[13px]">
            {onLogin && (
              <button type="button" onClick={onLogin} className="text-muted hover:text-ink">
                {t('app.login')}
              </button>
            )}
            {onRegister && (
              <button
                type="button"
                onClick={onRegister}
                className="rounded-full bg-ink px-3 py-1.5 text-white"
              >
                {t('app.signUp')}
              </button>
            )}
          </div>
        </header>

        <main className="min-h-0 flex-1 overflow-y-auto px-8 pb-8 pt-6">
        <p className="mb-6 text-[12.5px] tracking-wide text-[#8a8a8a]">✓ {t('desk.trust')}</p>

        <label className="relative block">
          <span className="sr-only">{t('desk.paperLabel')}</span>
          <div
            className={`composer-shell ${
              voiceStatus === 'listening' ? 'animate-listen ring-1 ring-accent/40' : ''
            }`}
          >
            <textarea
              ref={paperRef}
              data-testid="desk-paper"
              value={text}
              onChange={(e) => handleChange(e.target.value)}
              placeholder={text ? '' : t('desk.placeholder')}
              className="min-h-[140px] w-full resize-none rounded-[24px] bg-transparent px-5 pt-5 font-serif text-[18px] leading-8 text-ink outline-none placeholder:text-muted/55"
            />
            <div className="flex items-center gap-2 px-3 pb-3">
              <button
                type="button"
                onClick={onPickData}
                disabled={uploading}
                aria-label={t('desk.haveData')}
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-black/[0.08] text-[22px] leading-none text-ink transition-colors hover:bg-black/[0.04] disabled:opacity-50"
              >
                +
              </button>
              <button
                type="button"
                data-testid="desk-listen-btn"
                onClick={toggleListen}
                disabled={voiceStatus === 'unsupported'}
                className={`rounded-full px-3.5 py-2 text-[13px] transition-colors duration-200 disabled:cursor-not-allowed disabled:opacity-40 ${
                  voiceStatus === 'listening'
                    ? 'bg-accent text-white'
                    : 'text-muted hover:bg-black/[0.04] hover:text-ink'
                }`}
              >
                {listenLabel}
              </button>
              {voiceStatus === 'listening' && (
                <span className="text-[13px] text-muted">{t('desk.listening')}</span>
              )}
              <button
                type="button"
                data-testid="desk-shape-btn"
                onClick={() => {
                  if (!canShape || busy) return
                  if (!authed) {
                    // 边界态：未登录先注册/登录，想法暂存 sessionStorage，回来即恢复
                    sessionStorage.setItem('desk_idea_draft', text)
                    onLogin?.()
                    return
                  }
                  void askModel(text, turns)
                }}
                disabled={!canShape || busy}
                className="ml-auto rounded-full bg-accent px-4 py-2 text-[13px] font-medium text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-35"
                aria-label={t('desk.shape')}
              >
                {busy ? t('desk.shaping') : t('desk.shape')} →
              </button>
            </div>
          </div>
        </label>

        {!text && (
          <div className="mt-4 flex flex-wrap gap-2">
            {(['desk.starter1', 'desk.starter2', 'desk.starter3'] as const).map((key) => (
              <button
                key={key}
                type="button"
                onClick={() => handleChange(t(key))}
                className="rounded-full border border-black/[0.08] bg-white px-3.5 py-2 text-left text-[13px] leading-5 text-muted transition-colors duration-200 hover:bg-black/[0.03] hover:text-ink"
              >
                {t(key)}
              </button>
            ))}
          </div>
        )}

        {!text && (
          <p className="mt-5 text-[13px] text-muted">
            {t('desk.haveDataQ')}{' '}
            <button
              type="button"
              data-testid="desk-upload-inline"
              onClick={onPickData}
              disabled={uploading}
              className="text-ink underline underline-offset-4 transition-colors hover:opacity-80 disabled:opacity-50"
            >
              {uploading ? t('app.uploading') : t('desk.uploadCta')}
            </button>
          </p>
        )}

        {uploadError && (
          <p data-testid="upload-error" className="mt-3 text-sm text-danger">
            {uploadError}
          </p>
        )}

        {card && (
          <section
            data-testid="question-card"
            className="animate-slide-up thread-card mt-8 p-6"
          >
            <div className="flex items-start justify-end">
              <button
                type="button"
                data-testid="desk-speak-btn"
                onClick={() => void speakLine(card.ready ? title : card.question || title)}
                className="rounded-md px-2 py-1 text-xs text-muted underline-offset-4 hover:text-ink hover:underline"
              >
                {speaking ? t('desk.speakStop') : t('desk.speakAsk')}
              </button>
            </div>
            <textarea
              data-testid="question-title"
              value={title}
              onChange={(e) => setTitleOverride(e.target.value)}
              className="w-full resize-none bg-transparent font-serif text-xl leading-8 text-ink outline-none"
              rows={3}
            />

            {card.question && (
              <div className="mt-6">
                <p className="text-sm leading-7 text-ink">{card.question}</p>
                {asked && busy && (
                  <p data-testid="desk-ask-pending" className="mt-2 text-sm leading-7 text-muted">
                    {asked} — {t('desk.shaping')}
                  </p>
                )}
                {card.explain && !(asked && busy) && (
                  <p data-testid="desk-explain" className="mt-2 text-sm leading-7 text-muted">
                    {card.explain}
                  </p>
                )}
                <div className="mt-3 flex flex-wrap gap-2">
                  {card.options.map((option) => (
                    <button
                      key={option.id}
                      type="button"
                      data-testid={`desk-option-${option.id}`}
                      onClick={() => choose(option.id, option.label)}
                      className="rounded-full border border-border bg-bg px-3.5 py-2 text-[13px] text-ink transition-colors duration-200 hover:border-ink/20 hover:bg-panel"
                    >
                      {shortLabel(option.label)}
                    </button>
                  ))}
                  <button
                    type="button"
                    data-testid="desk-ask-btn"
                    onClick={() => setAsking((open) => !open)}
                    className="rounded-full px-3.5 py-2 text-[13px] text-muted hover:bg-panel hover:text-ink"
                  >
                    {t('desk.askWhat')}
                  </button>
                </div>
                {asking && (
                  <div className="mt-3 flex gap-2">
                    <input
                      data-testid="desk-ask-input"
                      value={askText}
                      onChange={(e) => setAskText(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          e.preventDefault()
                          askAboutOptions()
                        }
                      }}
                      placeholder={t('desk.askPlaceholder')}
                      className="min-w-0 flex-1 rounded-md border border-border bg-bg px-3 py-2 text-sm text-ink outline-none focus:border-accent"
                    />
                    <button
                      type="button"
                      data-testid="desk-ask-send"
                      onClick={askAboutOptions}
                      disabled={busy}
                      className="rounded-full border border-border px-3 py-2 text-[13px] text-ink hover:bg-panel disabled:opacity-40"
                    >
                      {busy ? t('desk.shaping') : t('desk.askSend')}
                    </button>
                  </div>
                )}
              </div>
            )}

            {card.ready && (
              <div className="mt-6 flex justify-end">
                <button
                  type="button"
                  data-testid="desk-confirm-btn"
                  onClick={() => onConfirm(title)}
                      className="rounded-lg bg-accent px-4 py-2 text-[13px] font-medium text-white transition-opacity duration-200 hover:opacity-90"
                >
                  {t('desk.confirm')}
                </button>
              </div>
            )}
          </section>
        )}

        {card && (
          <div className="mt-6 space-y-2" data-testid="agent-queue">
            <p className="text-[13px] text-muted">每一步一个 agent。点开，右边是它的工作台。写章串行，不并行代写整篇。</p>
            {(
              [
                ['shape', '问', '方向凝练', '乱问 → Y/X/方法'],
                ['clean', '洗', '清洗 8 步', '数据进来之后才跑'],
                ['estimate', '估', '估计门', '主表先于正文'],
                ['write', '章', 'Write Queue · 6 章串行', '没有主表，结果章锁定'],
              ] as const
            ).map(([id, mark, name, hint]) => (
              <button
                key={id}
                type="button"
                data-testid={`agent-row-${id}`}
                onClick={() => setAgentPane(id)}
                className={`flex w-full items-center gap-3 rounded-[14px] border px-3.5 py-3 text-left text-[13.5px] ${
                  agentPane === id ? 'border-ink/20 bg-[#f2f3f5]' : 'border-black/[0.08] bg-white'
                }`}
              >
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-black/[0.08] text-[12px]">
                  {mark}
                </span>
                <span className="min-w-0 flex-1">
                  <span className="font-medium">{name}</span>
                  <span className="mt-0.5 block text-[12px] text-muted">{hint}</span>
                </span>
                <span className="text-muted">›</span>
              </button>
            ))}
          </div>
        )}
        </main>
      </div>

      <aside className="flex w-[400px] shrink-0 flex-col border-l border-black/[0.06]" data-testid="agent-window">
        <div className="border-b border-black/[0.06] px-4 py-3">
          <p className="font-mono text-[14px] font-bold">econpaper Computer</p>
          <p className="mt-1 text-[13px] text-muted">{paneTitle}</p>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto px-4 py-4 text-[13.5px] leading-7">
          {agentPane === 'shape' && (
            <>
              <p className="mb-3 text-[12px] text-muted">用户原话不会被丢掉。agent 只补可估计的骨架。</p>
              {card ? (
                <dl className="space-y-2">
                  <div>
                    <dt className="text-[12px] text-muted">问题</dt>
                    <dd>{title || '—'}</dd>
                  </div>
                  <div>
                    <dt className="text-[12px] text-muted">线索</dt>
                    <dd>{card.heard.join(' · ') || '—'}</dd>
                  </div>
                  <div>
                    <dt className="text-[12px] text-muted">比较 / 结果</dt>
                    <dd>
                      {card.comparison} · {card.outcome}
                    </dd>
                  </div>
                </dl>
              ) : (
                <p className="text-muted">先把一句话倒进中间。开始之后，设定会出现在这里。</p>
              )}
            </>
          )}
          {agentPane === 'clean' && (
            <ul className="space-y-1 text-muted">
              <li>profiling · 契约</li>
              <li>missing · 缺失值</li>
              <li>outliers · 异常值</li>
              <li>audit · clean.py 留痕</li>
              <li className="pt-2">CSV 进来之后这些才会亮。</li>
            </ul>
          )}
          {agentPane === 'estimate' && (
            <p className="text-muted">还没有估计。数据进来之后，系数先于正文。结果章必须引用这张表。</p>
          )}
          {agentPane === 'write' && (
            <ol className="space-y-1 text-muted">
              <li>01 引言 · 排队</li>
              <li>02 文献综述 · 排队</li>
              <li>03 数据描述 · 排队</li>
              <li>04 方法 · 排队</li>
              <li>05 结果 · 锁（没有主表不能写）</li>
              <li>06 结论 · 排队</li>
            </ol>
          )}
        </div>
      </aside>
    </div>
  )
}
