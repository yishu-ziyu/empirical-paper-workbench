import { useEffect, useMemo, useRef, useState, type FormEvent } from 'react'
import {
  createSpikeSessionId,
  pauseSpike,
  persistSpikeSessionId,
  readSpikeSessionId,
  readSpikeState,
  resumeSpike,
  streamSpike,
  type SpikeDecision,
  type SpikeEvent,
  type SpikeInterrupt,
  type SpikeState,
} from '../lib/agentSpike'

type Phase =
  | 'idle'
  | 'working'
  | 'waiting_user'
  | 'waiting_approval'
  | 'paused_by_user'
  | 'completed'
  | 'stopped'
  | 'error'

type StageStatus = 'pending' | 'active' | 'done'

interface ConversationLine {
  id: string
  role: 'user' | 'assistant'
  text: string
}

const IDEA = '我想研究最低工资提高后，会不会减少就业。'
const EXAMPLES = [IDEA, '我有一份问卷，不知道里面什么值得研究。']
const STAGES = ['明确关心结果', '查看公开数据', '形成研究方向']

function newStages(): StageStatus[] {
  return ['pending', 'pending', 'pending']
}

function statusCopy(phase: Phase): string {
  switch (phase) {
    case 'working':
      return '正在把你的想法变成下一步行动'
    case 'waiting_user':
      return '需要你决定研究先回答什么'
    case 'waiting_approval':
      return '等你的确认后才会改动临时副本'
    case 'paused_by_user':
      return '已暂停，可稍后继续'
    case 'completed':
      return '这一步已完成，结果会留在当前研究里'
    case 'stopped':
      return '已停止等待；当前研究状态仍保留'
    case 'error':
      return '这一步没有完成，需要重试'
    default:
      return ''
  }
}

function eventDecision(event: SpikeEvent): SpikeDecision | null {
  return event.decision || null
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError'
}

export default function AgentSpikePage() {
  const explicitSessionId = new URLSearchParams(window.location.search).get('session')
  const storedSessionId = explicitSessionId || readSpikeSessionId()
  const [sessionId] = useState(() => {
    if (explicitSessionId) {
      persistSpikeSessionId(explicitSessionId)
      return explicitSessionId
    }
    return storedSessionId || createSpikeSessionId()
  })
  const [composerText, setComposerText] = useState('')
  const [lines, setLines] = useState<ConversationLine[]>([])
  const [decision, setDecision] = useState<SpikeDecision | null>(null)
  const [interrupt, setInterrupt] = useState<SpikeInterrupt | null>(null)
  const [phase, setPhase] = useState<Phase>('idle')
  const [stages, setStages] = useState<StageStatus[]>(newStages)
  const [error, setError] = useState<string | null>(null)
  const [attachment, setAttachment] = useState<string | null>(null)
  const [detailsOpen, setDetailsOpen] = useState(true)
  const abortRef = useRef<AbortController | null>(null)
  const lineCounter = useRef(0)
  const lastRequest = useRef<{
    suffix: 'turn/stream' | 'decision/stream'
    payload: Record<string, unknown>
    display?: string
  } | null>(null)

  const approvalRequest = interrupt?.action_requests?.[0]
  const preview = decision?.preview
  const descriptionPreview = approvalRequest?.description.match(/预计保留\s*(\d+)\s*行（原始\s*(\d+)\s*行）/)
  const previewAfter = typeof preview?.n_after === 'number' ? preview.n_after : descriptionPreview ? Number(descriptionPreview[1]) : null
  const previewBefore = typeof preview?.n_before === 'number' ? preview.n_before : descriptionPreview ? Number(descriptionPreview[2]) : null
  const busy = phase === 'working'
  const interactionBlocked = busy || phase === 'paused_by_user'
  const hasConversation = lines.length > 0
  const composerPlaceholder = hasConversation ? '补充一句，或告诉我继续' : '说一个还不成熟的想法，或放入一份数据'

  const addLine = (role: ConversationLine['role'], text: string) => {
    const value = text.trim()
    if (!value) return
    lineCounter.current += 1
    setLines((current) => [
      ...current,
      { id: `${role}-${lineCounter.current}`, role, text: value },
    ])
  }

  const applyEvent = (event: SpikeEvent) => {
    if (event.kind === 'update') {
      const nodes = event.nodes || []
      if (nodes.includes('model')) {
        setStages((current) => ['done', current[1] === 'done' ? 'done' : 'active', current[2]])
      }
      return
    }
    if (event.kind === 'message') {
      if (event.message_type === 'ai' && event.tool_calls?.some((call) => call.name === 'filter_fixture_data')) {
        setStages((current) => ['done', 'active', current[2]])
      }
      if (event.message_type === 'tool') {
        setStages(['done', 'done', 'active'])
      }
      return
    }
    if (event.kind === 'interrupt') {
      const nextInterrupt = event.value || null
      setInterrupt(nextInterrupt)
      setPhase('waiting_approval')
      setStages(['done', 'active', 'pending'])
      return
    }
    if (event.kind !== 'state') return
    const nextDecision = eventDecision(event)
    if (nextDecision) setDecision(nextDecision)
    if (event.interrupt) setInterrupt(event.interrupt)
    if (event.status === 'waiting_user') {
      setPhase('waiting_user')
      setInterrupt(null)
      setStages(['done', 'pending', 'pending'])
      if (nextDecision?.message) addLine('assistant', nextDecision.message)
    } else if (event.status === 'waiting_approval') {
      setPhase('waiting_approval')
      setStages(['done', 'active', 'pending'])
      if (nextDecision?.message) addLine('assistant', nextDecision.message)
    } else if (event.status === 'completed') {
      setPhase('completed')
      setInterrupt(null)
      setStages(['done', 'done', 'done'])
      if (nextDecision?.message) addLine('assistant', nextDecision.message)
    } else if (event.status === 'failed' || event.status === 'degraded' || event.status === 'skipped') {
      setPhase('error')
      if (nextDecision?.message) addLine('assistant', nextDecision.message)
    }
  }

  function applyCheckpointState(state: SpikeState) {
    setDecision(state.decision || null)
    setInterrupt(state.interrupt || null)
    if (state.status === 'paused_by_user') {
      setPhase('paused_by_user')
      setStages(['done', 'active', 'pending'])
    } else if (state.status === 'waiting_approval') {
      setPhase('waiting_approval')
      setStages(['done', 'active', 'pending'])
    } else if (state.status === 'completed') {
      setPhase('completed')
      setInterrupt(null)
      setStages(['done', 'done', 'done'])
    }
  }

  useEffect(() => {
    if (!storedSessionId) return
    let cancelled = false
    void readSpikeState(storedSessionId)
      .then((state: SpikeState | null) => {
        if (cancelled || !state) return
        if (state.decision) setDecision(state.decision)
        if (state.interrupt) setInterrupt(state.interrupt)
        if (state.status === 'waiting_approval') {
          setPhase('waiting_approval')
          setStages(['done', 'active', 'pending'])
          addLine('assistant', '上次停在这里。原始文件没有被覆盖，等你决定是否继续。')
        } else if (state.status === 'paused_by_user') {
          setPhase('paused_by_user')
          setStages(['done', 'active', 'pending'])
          addLine('assistant', '已暂停，可稍后继续。原始文件和临时副本都没有变化。')
        } else if (state.status === 'waiting_user') {
          setPhase('waiting_user')
          if (state.decision?.message) addLine('assistant', state.decision.message)
        } else if (state.status === 'completed') {
          setPhase('completed')
          setStages(['done', 'done', 'done'])
        }
      })
      .catch(() => {
        // A missing checkpoint is the normal first visit; no fixed answer is shown.
      })
    return () => {
      cancelled = true
    }
    // The stored id is intentionally captured from the first render.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(
    () => () => {
      abortRef.current?.abort()
    },
    [],
  )

  async function runStream(
    suffix: 'turn/stream' | 'decision/stream',
    payload: Record<string, unknown>,
    display?: string,
    appendUser = false,
  ) {
    if (busy) return
    if (appendUser && display) addLine('user', display)
    lastRequest.current = { suffix, payload, display }
    setError(null)
    setPhase('working')
    setInterrupt(null)
    const controller = new AbortController()
    abortRef.current = controller
    try {
      await streamSpike(sessionId, suffix, payload, applyEvent, controller.signal)
    } catch (caught) {
      if (controller.signal.aborted || isAbortError(caught)) {
        setPhase('stopped')
      } else {
        setPhase('error')
        setError(caught instanceof Error ? caught.message : '服务暂时不可用，请重试。')
      }
    } finally {
      if (abortRef.current === controller) abortRef.current = null
    }
  }

  function sendTurn(message: string, display = message) {
    const value = message.trim()
    if (!value || interactionBlocked) return
    setComposerText('')
    void runStream('turn/stream', { message: value }, display, true)
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    sendTurn(composerText)
  }

  function chooseOption(label: string, consequence: string) {
    setDecision(null)
    sendTurn(`我选择“${label}”。${consequence}`, label)
  }

  async function pauseApproval() {
    if (busy) return
    setError(null)
    setPhase('working')
    try {
      const state = await pauseSpike(sessionId)
      applyCheckpointState(state)
    } catch (caught) {
      setPhase('waiting_approval')
      setError(caught instanceof Error ? caught.message : '暂停没有保存成功，请重试。')
    }
  }

  async function resumeApproval() {
    if (busy) return
    setError(null)
    setPhase('working')
    try {
      const state = await resumeSpike(sessionId)
      applyCheckpointState(state)
    } catch (caught) {
      setPhase('paused_by_user')
      setError(caught instanceof Error ? caught.message : '暂时无法继续，请重试。')
    }
  }

  function approve(decisionType: 'approve' | 'reject', display: string, message?: string) {
    if (busy) return
    if (display) addLine('user', display)
    void runStream(
      'decision/stream',
      { decision: decisionType, ...(message ? { message } : {}) },
      undefined,
      false,
    )
  }

  function stopWaiting() {
    abortRef.current?.abort()
    setPhase('stopped')
  }

  function retry() {
    const request = lastRequest.current
    if (!request) return
    void runStream(request.suffix, request.payload, undefined, false)
  }

  const status = useMemo(() => statusCopy(phase), [phase])

  return (
    <div data-testid="spike-page" className="spike-page min-h-screen overflow-x-hidden bg-[#f7f3eb] text-[#211f1c]">
      <header className="spike-header mx-auto flex w-full max-w-[1120px] items-center justify-between px-6 py-6 sm:px-10">
        <div className="flex items-center gap-3">
          <span className="spike-wordmark font-serif text-[19px] tracking-[-0.03em]">研究桌</span>
          <span className="spike-kicker hidden text-[11px] uppercase tracking-[0.22em] text-black/35 sm:inline">Research desk</span>
        </div>
        <span data-testid="spike-session-id" className="font-mono text-[10px] text-black/30">
          {sessionId.slice(0, 8)}
        </span>
      </header>

      <main className="mx-auto flex w-full max-w-[900px] flex-col px-5 pb-16 pt-10 sm:px-10 sm:pt-16">
        <section className="spike-intro text-center">
          <p className="mb-3 text-[11px] uppercase tracking-[0.25em] text-black/35">从一个想法开始</p>
          <h1 className="font-serif text-[38px] leading-[1.12] tracking-[-0.04em] sm:text-[56px]">你最近在想什么？</h1>
          <p className="mx-auto mt-4 max-w-[34rem] text-[14px] leading-7 text-black/50">
            不用先想清楚方法。先告诉我你真正想知道的事。
          </p>
        </section>

        {lines.length > 0 && (
          <section data-testid="spike-thread" className="spike-thread mx-auto mt-14 w-full max-w-[700px]">
            {lines.map((line) => (
              <div key={line.id} className={`mb-7 ${line.role === 'user' ? 'text-right' : 'text-left'}`}>
                <span className="mb-2 block text-[11px] uppercase tracking-[0.18em] text-black/30">
                  {line.role === 'user' ? '你' : '研究桌'}
                </span>
                <p className={`inline-block max-w-[90%] text-[18px] leading-8 sm:text-[20px] ${line.role === 'user' ? 'text-black/80' : 'font-serif text-black/90'}`}>
                  {line.text}
                </p>
              </div>
            ))}
          </section>
        )}

        {decision?.action === 'ask' && decision.question && phase === 'waiting_user' && (
          <section data-testid="spike-ask" className="mx-auto mt-5 w-full max-w-[700px]">
            <h2 className="mb-5 font-serif text-[25px] tracking-[-0.02em]">{decision.question}</h2>
            <div className="space-y-3">
              {(decision.options || []).slice(0, 2).map((option, index) => (
                <button
                  key={option.id}
                  type="button"
                  data-testid={`spike-option-${option.id}`}
                  onClick={() => chooseOption(option.label, option.consequence)}
                  className="spike-option group flex w-full items-start gap-4 rounded-[18px] border border-black/10 bg-white/55 px-5 py-4 text-left transition hover:border-[#47745b] hover:bg-white"
                >
                  <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-black/20 text-[11px] text-black/45 group-hover:border-[#47745b] group-hover:text-[#47745b]">
                    {index + 1}
                  </span>
                  <span>
                    <span className="block text-[15px] leading-6 text-black/85">{option.label}</span>
                    <span className="mt-1 block text-[13px] leading-6 text-black/48">{option.consequence}</span>
                  </span>
                  <span aria-hidden className="ml-auto pt-1 text-[18px] text-black/30 transition group-hover:translate-x-0.5">→</span>
                </button>
              ))}
              <button
                type="button"
                data-testid="spike-option-uncertain"
                onClick={() => sendTurn('我还不确定，先帮我解释这两个方向的差别。', '我还不确定')}
                className="px-1 pt-2 text-[14px] text-[#47745b] underline decoration-[#47745b]/35 underline-offset-4"
              >
                我还不确定
              </button>
            </div>
          </section>
        )}

        {(phase === 'working' || phase === 'waiting_approval' || phase === 'paused_by_user' || phase === 'completed' || phase === 'stopped') && (
          <section data-testid="spike-progress" className="mx-auto mt-12 w-full max-w-[700px]">
            <div className="mb-3 flex items-center justify-between text-[13px] text-black/50">
              <span className={busy ? 'spike-status-dot' : ''}>{status}</span>
              {busy && (
                <button type="button" onClick={stopWaiting} className="text-[12px] text-black/45 underline decoration-black/20 underline-offset-4">
                  停止等待
                </button>
              )}
            </div>
            <details open={detailsOpen || phase === 'waiting_approval' || phase === 'paused_by_user'} onToggle={(event) => setDetailsOpen(event.currentTarget.open)} className="spike-progress-details rounded-[16px] border border-black/10 bg-white/40">
              <summary className="cursor-pointer list-none px-5 py-4 text-[14px] text-black/72">
                <span className="mr-2 text-black/35">路径</span>这一步怎样推进
                <span aria-hidden className="float-right text-black/35">⌄</span>
              </summary>
              <ol className="border-t border-black/8 px-5 py-3">
                {STAGES.map((stage, index) => (
                  <li key={stage} data-testid={`spike-step-${index}`} data-status={stages[index]} className="flex items-center gap-3 py-2.5 text-[14px]">
                    <span className={`h-2.5 w-2.5 rounded-full border ${stages[index] === 'done' ? 'border-[#47745b] bg-[#47745b]' : stages[index] === 'active' ? 'border-[#47745b]' : 'border-black/20'}`} />
                    <span className={stages[index] === 'pending' ? 'text-black/38' : 'text-black/72'}>{stage}</span>
                    {stages[index] === 'active' && <span className="ml-auto text-[11px] text-[#47745b]">进行中</span>}
                  </li>
                ))}
              </ol>
            </details>
          </section>
        )}

        {interrupt && phase === 'paused_by_user' && (
          <section data-testid="spike-paused" className="mx-auto mt-6 w-full max-w-[700px] rounded-[20px] border border-black/10 bg-white/55 px-5 py-5 sm:px-7">
            <h2 className="font-serif text-[23px] tracking-[-0.02em]">已暂停，可稍后继续</h2>
            <p className="mt-2 text-[14px] leading-6 text-black/62">这一步已保留，原始文件和临时副本都没有变化。准备好后可以回到确认。</p>
            <button type="button" data-testid="spike-resume" onClick={resumeApproval} className="mt-5 rounded-[10px] bg-[#282725] px-5 py-2.5 text-[14px] text-white transition hover:bg-black" disabled={busy}>继续处理</button>
          </section>
        )}

        {interrupt && phase === 'waiting_approval' && (
          <section data-testid="spike-approval-panel" className="spike-approval mx-auto mt-6 w-full max-w-[700px] rounded-[20px] border border-[#b99750]/45 bg-[#fffaf0] px-5 py-5 sm:px-7">
            <div className="flex items-start gap-3">
              <span aria-hidden className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-[#b99750]/55 text-[#92722c]">!</span>
              <div>
                <h2 className="font-serif text-[23px] tracking-[-0.02em]">开始整理分析数据？</h2>
                <p className="mt-2 text-[14px] leading-6 text-black/62">{approvalRequest?.description || decision?.message || '这一步会改变临时分析副本。'}</p>
              </div>
            </div>
            <div className="mt-5 space-y-2 border-t border-black/8 pt-4 text-[13px] text-black/62">
              <p>▧ 原始文件不会被覆盖</p>
              <p>▦ {previewAfter !== null ? `预计保留 ${previewAfter} 行（原始 ${previewBefore ?? '—'} 行）` : '预计保留数量以预检结果为准'}</p>
              <p>✎ 之后可以调整这条规则</p>
            </div>
            <div className="mt-6 flex flex-wrap items-center gap-2.5 border-t border-black/8 pt-4">
              <button type="button" data-testid="spike-approve" onClick={() => approve('approve', '继续')} className="rounded-[10px] bg-[#282725] px-5 py-2.5 text-[14px] text-white transition hover:bg-black disabled:opacity-45" disabled={busy}>继续</button>
              <button type="button" data-testid="spike-adjust" onClick={() => approve('reject', '调整规则', '我想调整规则，先不要改数据。')} className="rounded-[10px] px-4 py-2.5 text-[14px] text-black/65 transition hover:bg-black/5" disabled={busy}>调整规则</button>
              <button type="button" data-testid="spike-pause" onClick={pauseApproval} className="rounded-[10px] px-4 py-2.5 text-[14px] text-black/65 transition hover:bg-black/5" disabled={busy}>先暂停</button>
            </div>
          </section>
        )}

        {error && (
          <section data-testid="spike-error" className="mx-auto mt-7 flex w-full max-w-[700px] items-center justify-between gap-4 rounded-[14px] border border-[#9b3d30]/25 bg-[#fff8f6] px-4 py-3 text-[13px] text-[#8d3a30]">
            <span>{error}</span>
            <button type="button" data-testid="spike-retry" onClick={retry} className="shrink-0 underline underline-offset-4">重试</button>
          </section>
        )}

        {!hasConversation && (
          <div className="mx-auto mt-11 w-full max-w-[700px] space-y-2 px-1">
            {EXAMPLES.map((example, index) => (
              <button key={example} type="button" data-testid={`spike-example-${index}`} onClick={() => setComposerText(example)} className="group flex w-full items-center justify-between border-b border-black/8 py-3 text-left text-[14px] text-black/58 transition hover:text-black/85">
                <span>{example}</span><span aria-hidden className="text-[18px] text-black/28 transition group-hover:translate-x-1">→</span>
              </button>
            ))}
          </div>
        )}

        <form onSubmit={handleSubmit} className={`spike-composer mx-auto mt-12 flex w-full max-w-[700px] items-end gap-3 rounded-[18px] border bg-white/75 p-3 ${busy ? 'is-working border-[#47745b]/55' : 'border-black/12'}`}>
          <label className="flex h-10 w-10 shrink-0 cursor-pointer items-center justify-center rounded-[11px] border border-black/10 text-black/50 transition hover:bg-black/5" aria-label="添加数据">
            <input type="file" accept=".csv,.dta,.xlsx,.xls" className="sr-only" onChange={(event) => setAttachment(event.target.files?.[0]?.name || null)} />
            <span aria-hidden className="text-[21px] leading-none">⌕</span>
          </label>
          <textarea
            data-testid="spike-idea-input"
            value={composerText}
            onChange={(event) => setComposerText(event.target.value)}
            placeholder={composerPlaceholder}
            rows={1}
            disabled={interactionBlocked}
            className="min-h-10 max-h-28 flex-1 resize-none bg-transparent px-1 py-2 text-[15px] leading-6 text-black/82 outline-none placeholder:text-black/35"
          />
          <button data-testid="spike-send" type="submit" disabled={!composerText.trim() || interactionBlocked} className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#282725] text-[21px] text-white transition hover:bg-black disabled:cursor-not-allowed disabled:opacity-30" aria-label="发送">→</button>
        </form>
        {attachment && <p className="mx-auto mt-2 w-full max-w-[700px] px-1 text-[11px] text-black/42">已附加：{attachment}</p>}
        <p className="mt-6 text-center text-[11px] tracking-[0.06em] text-black/30">研究方向会在每个重要取舍处由你确认</p>
      </main>
    </div>
  )
}
