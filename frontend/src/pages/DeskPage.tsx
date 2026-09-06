import { useEffect, useRef, useState } from 'react'
import { useT } from '../lib/i18n'
import { discussDesk, speakDesk, transcribeDesk } from '../lib/deskDiscuss'
import type { DeskCard, DeskTurn } from '../lib/deskDiscuss'
import { nextPrompt, shapeQuestion } from '../lib/shapeQuestion'
import type { ShapeAnswers } from '../lib/shapeQuestion'
import { appendTranscript } from '../lib/voice'
import type { VoiceStatus } from '../lib/voice'
import ResizableWorkspace from '../components/ResizableWorkspace'

export interface DeskPageProps {
  onConfirm: (title: string) => void
  onPickData: () => void
  uploading?: boolean
  uploadError?: string | null
  onOpenGuide?: () => void
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
    intent: draft.intent,
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
  onOpenGuide,
  onLogin,
  onRegister,
  authed,
}: DeskPageProps) {
  const { t } = useT()
  const initialDraft = useRef(sessionStorage.getItem('desk_idea_draft') || '').current
  const [text, setText] = useState(initialDraft)
  const [conversationHistory, setConversationHistory] = useState<Array<{ user: string; assistant: string }>>([])
  const [turns, setTurns] = useState<DeskTurn[]>([])
  const [card, setCard] = useState<DeskCard | null>(null)
  const [titleOverride, setTitleOverride] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [voiceStatus, setVoiceStatus] = useState<VoiceStatus>('idle')
  const [speaking, setSpeaking] = useState(false)
  const [asking, setAsking] = useState(false)
  const [askText, setAskText] = useState('')
  const [asked, setAsked] = useState('')
  const [replyError, setReplyError] = useState('')
  const paperRef = useRef<HTMLTextAreaElement>(null)
  const timerRef = useRef<number | null>(null)
  const mediaRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const lastSpokenRef = useRef('')
  const requestRef = useRef(0)

  const title = titleOverride ?? card?.title ?? ''
  const canShape = text.trim().length > 0
  const conversational = card?.intent === 'conversation'
  const inReplyFlow = Boolean(card) || turns.length > 0

  // 首屏或登录流程带来的原话会自动发起第一轮讨论。
  // initialDraft 在 effect 重放前已缓存，React StrictMode 清掉首个 timer 后仍能重新调度。
  useEffect(() => {
    if (!initialDraft) return
    timerRef.current = window.setTimeout(() => {
      void askModel(initialDraft, [])
    }, IDLE_MS)
    sessionStorage.removeItem('desk_idea_draft')
    return () => {
      if (timerRef.current) window.clearTimeout(timerRef.current)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function growPaper() {
    const el = paperRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(160, Math.max(56, el.scrollHeight))}px`
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
      setReplyError('')
    } catch {
      if (requestRef.current !== ticket) return
      if (nextTurns.length > 0) {
        setCard(null)
        setReplyError('刚才没有完成回答，请重试。')
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
    if (!value.trim()) {
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
    setReplyError('')
    setCard(null)
    void askModel(text, nextTurns)
  }

  function submitCardReply() {
    const note = askText.trim() || '这几个选项分别是什么意思？我该怎么选？'
    if (timerRef.current) window.clearTimeout(timerRef.current)
    const nextTurns = [
      ...turns,
      { question: card?.question || '', answer: note, id: asking ? 'ask' : 'freeform' },
    ]
    setTurns(nextTurns)
    setAsked(asking ? note : '')
    setReplyError('')
    setCard(null)
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
      if (card) setAskText((current) => appendTranscript(current, heard))
      else handleChange(appendTranscript(text, heard))
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
  }, [askText, card, text])

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

  function sendComposer() {
    if (busy) return
    if (card?.intent === 'conversation') {
      const next = askText.trim()
      if (!next) return
      setConversationHistory((history) => [
        ...history,
        { user: text, assistant: card.reflection },
      ])
      setText(next)
      setAskText('')
      setTurns([])
      setCard(null)
      setAsked('')
      setTitleOverride(null)
      void askModel(next, [])
      return
    }
    if (card) {
      submitCardReply()
      setAskText('')
      return
    }
    if (!canShape) return
    if (!authed) {
      sessionStorage.setItem('desk_idea_draft', text)
      onLogin?.()
      return
    }
    if (timerRef.current) window.clearTimeout(timerRef.current)
    void askModel(text, turns)
  }

  const leftPane = (
    <div className="flex h-full min-h-0 flex-col p-3">
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
    </div>
  )

  const centerPane = (
    <div className="flex h-full min-h-0 flex-col bg-[#fffefb]">
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-black/[0.06] px-6">
        <p className="truncate text-[14px] font-medium">{title || t('desk.heading')}</p>
        <div className="flex items-center gap-3 text-[13px]">
          {onOpenGuide && (
            <button
              type="button"
              data-testid="desk-open-guide"
              onClick={onOpenGuide}
              className="text-muted transition-colors hover:text-ink"
            >
              {t('desk.openGuide')}
            </button>
          )}
          {onLogin && (
            <button
              type="button"
              data-testid="open-login-btn"
              onClick={onLogin}
              className="text-muted hover:text-ink"
            >
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

      <main data-testid="desk-conversation" className="min-h-0 flex-1 overflow-y-auto">
        <div className="mx-auto flex min-h-full w-full max-w-[780px] flex-col px-6 pb-8 pt-7 sm:px-10">
          <p className="mb-8 text-[12.5px] tracking-wide text-[#8a8a8a]">✓ {t('desk.trust')}</p>

          {!text && (
            <section className="my-auto pb-16" data-testid="desk-empty-state">
              <p className="font-serif text-[30px] leading-tight text-ink">先说一句你想研究什么。</p>
              <p className="mt-3 max-w-[34rem] text-[14px] leading-7 text-muted">
                我会保留你的原话，一次只追问一个决定；数据入口和研究进度始终留在两侧。
              </p>
              <div className="mt-7 flex flex-wrap gap-2">
                {(['desk.starter1', 'desk.starter2', 'desk.starter3'] as const).map((key) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => handleChange(t(key))}
                    className="rounded-full border border-black/[0.08] bg-white px-3.5 py-2 text-left text-[13px] leading-5 text-muted transition-colors hover:bg-black/[0.03] hover:text-ink"
                  >
                    {t(key)}
                  </button>
                ))}
              </div>
              <p className="mt-5 text-[13px] text-muted">
                {t('desk.haveDataQ')}{' '}
                <button
                  type="button"
                  data-testid="desk-upload-inline"
                  onClick={onPickData}
                  disabled={uploading}
                  className="text-ink underline underline-offset-4 hover:opacity-80 disabled:opacity-50"
                >
                  {uploading ? t('app.uploading') : t('desk.uploadCta')}
                </button>
              </p>
            </section>
          )}

          {text && (
            <div className="space-y-7" data-testid="desk-thread">
              {conversationHistory.map((item, index) => (
                <div key={`${item.user}-${index}`} className="space-y-4">
                  <div className="ml-auto max-w-[82%] rounded-[18px] rounded-br-[5px] bg-[#f0ede5] px-4 py-3 text-[15px] leading-7 text-ink">
                    {item.user}
                  </div>
                  <div className="max-w-[92%]">
                    <span className="text-[12px] font-medium text-accent">econpaper</span>
                    <p className="mt-2 text-[15px] leading-7 text-ink">{item.assistant}</p>
                  </div>
                </div>
              ))}
              <div className="ml-auto max-w-[82%] rounded-[18px] rounded-br-[5px] bg-[#f0ede5] px-4 py-3 text-[15px] leading-7 text-ink">
                {text}
              </div>

              {turns.map((turn, index) => (
                <div key={`${turn.id}-${index}`} className="space-y-3">
                  <p className="max-w-[88%] text-[14px] leading-7 text-muted">{turn.question}</p>
                  <p className="ml-auto max-w-[82%] rounded-[18px] rounded-br-[5px] bg-[#f0ede5] px-4 py-3 text-[14px] leading-6 text-ink">
                    {turn.answer}
                  </p>
                </div>
              ))}

              {busy && !card && (
                <p className="text-[14px] text-muted" data-testid="desk-thinking">{t('desk.shaping')}</p>
              )}

              {replyError && !busy && (
                <div data-testid="desk-reply-error" className="flex items-center gap-3 text-[14px] text-danger">
                  <span>{replyError}</span>
                  <button
                    type="button"
                    onClick={() => {
                      setReplyError('')
                      void askModel(text, turns)
                    }}
                    className="underline underline-offset-4"
                  >
                    重试
                  </button>
                </div>
              )}

              {card?.intent === 'conversation' && (
                <section data-testid="conversation-reply" className="animate-slide-up max-w-[92%] pb-4">
                  <span className="text-[12px] font-medium text-accent">econpaper</span>
                  <p className="mt-2 text-[15px] leading-7 text-ink">{card.reflection}</p>
                </section>
              )}

              {card?.intent === 'research' && (
                <section data-testid="question-card" className="animate-slide-up max-w-[92%] pb-4">
                  <div className="mb-3 flex items-center justify-between">
                    <span className="text-[12px] font-medium text-accent">econpaper</span>
                    <button
                      type="button"
                      data-testid="desk-speak-btn"
                      onClick={() => void speakLine(card.ready ? title : card.question || title)}
                      className="rounded-md px-2 py-1 text-xs text-muted hover:text-ink"
                    >
                      {speaking ? t('desk.speakStop') : t('desk.speakAsk')}
                    </button>
                  </div>
                  <p data-testid="desk-reflection" className="mb-4 text-[15px] leading-7 text-ink">
                    {card.reflection}
                  </p>
                  <textarea
                    data-testid="question-title"
                    value={title}
                    onChange={(e) => setTitleOverride(e.target.value)}
                    className="w-full resize-none border-l-2 border-accent/45 bg-transparent py-1 pl-4 font-serif text-[21px] leading-8 text-ink outline-none"
                    rows={3}
                  />

                  {card.question && (
                    <div className="mt-5">
                      <p className="text-[14px] leading-7 text-ink">{card.question}</p>
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
                            className="rounded-full border border-border bg-panel px-3.5 py-2 text-[13px] text-ink transition-colors hover:border-ink/20 hover:bg-cream"
                          >
                            {shortLabel(option.label)}
                          </button>
                        ))}
                        <button
                          type="button"
                          data-testid="desk-ask-btn"
                          onClick={() => {
                            setAsking(true)
                            requestAnimationFrame(() => paperRef.current?.focus())
                          }}
                          className="rounded-full px-3.5 py-2 text-[13px] text-muted hover:bg-cream hover:text-ink"
                        >
                          {t('desk.askWhat')}
                        </button>
                      </div>
                    </div>
                  )}

                  {card.ready && (
                    <div className="mt-6 flex justify-end">
                      <button
                        type="button"
                        data-testid="desk-confirm-btn"
                        onClick={() => onConfirm(title)}
                        className="rounded-lg bg-accent px-4 py-2 text-[13px] font-medium text-white hover:opacity-90"
                      >
                        {t('desk.confirm')}
                      </button>
                    </div>
                  )}
                </section>
              )}
            </div>
          )}

          {uploadError && (
            <p data-testid="upload-error" className="mt-3 text-sm text-danger">
              {uploadError}
            </p>
          )}
        </div>
      </main>

      <div className="shrink-0 border-t border-black/[0.06] bg-[#fffefb]/95 px-5 py-3 backdrop-blur sm:px-8">
        <label className="relative mx-auto block w-full max-w-[780px]">
          <span className="sr-only">{inReplyFlow && !conversational ? t('desk.askPlaceholder') : t('desk.paperLabel')}</span>
          <div
            className={`rounded-[18px] border bg-white transition-colors ${
              asking ? 'border-accent/40' : 'border-black/[0.1]'
            } ${voiceStatus === 'listening' ? 'animate-listen ring-1 ring-accent/40' : ''}`}
          >
            <textarea
              ref={paperRef}
              data-testid={conversational ? 'desk-conversation-input' : inReplyFlow ? 'desk-ask-input' : 'desk-paper'}
              value={inReplyFlow ? askText : text}
              onChange={(event) => {
                if (inReplyFlow) setAskText(event.target.value)
                else handleChange(event.target.value)
              }}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault()
                  sendComposer()
                }
              }}
              placeholder={conversational ? '继续说你的想法…' : inReplyFlow ? t('desk.askPlaceholder') : t('desk.placeholder')}
              className="min-h-[56px] w-full resize-none rounded-[18px] bg-transparent px-4 pt-3 text-[15px] leading-6 text-ink outline-none placeholder:text-muted/55"
            />
            <div className="flex items-center gap-2 px-2.5 pb-2.5">
              <button
                type="button"
                onClick={onPickData}
                disabled={uploading}
                aria-label={t('desk.haveData')}
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-black/[0.08] text-[18px] leading-none text-ink hover:bg-black/[0.04] disabled:opacity-50"
              >
                +
              </button>
              <button
                type="button"
                data-testid="desk-listen-btn"
                onClick={toggleListen}
                disabled={voiceStatus === 'unsupported'}
                className={`rounded-full px-3 py-1.5 text-[12.5px] disabled:opacity-40 ${
                  voiceStatus === 'listening' ? 'bg-accent text-white' : 'text-muted hover:bg-black/[0.04] hover:text-ink'
                }`}
              >
                {listenLabel}
              </button>
              {voiceStatus === 'listening' && <span className="text-[12px] text-muted">{t('desk.listening')}</span>}
              <button
                type="button"
                data-testid={inReplyFlow ? 'desk-ask-send' : 'desk-shape-btn'}
                onClick={sendComposer}
                disabled={busy || (conversational ? !askText.trim() : !card && !canShape)}
                className="ml-auto rounded-full bg-accent px-4 py-1.5 text-[13px] font-medium text-white hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-35"
                aria-label={conversational ? t('desk.shape') : inReplyFlow ? t('desk.askSend') : t('desk.shape')}
              >
                {busy ? t('desk.shaping') : conversational ? t('desk.shape') : inReplyFlow ? t('desk.askSend') : t('desk.shape')} →
              </button>
            </div>
          </div>
        </label>
      </div>
    </div>
  )

  return (
    <ResizableWorkspace
      storageKey="econpaper.direction.layout.v2"
      testId="desk-page"
      leftTestId="desk-left-sidebar"
      centerTestId="desk-center"
      className="h-screen bg-white text-ink"
      leftDefault={224}
      leftClassName="border-r border-black/[0.06] bg-white"
      centerClassName="bg-[#fffefb]"
      left={leftPane}
      center={centerPane}
    />
  )
}
