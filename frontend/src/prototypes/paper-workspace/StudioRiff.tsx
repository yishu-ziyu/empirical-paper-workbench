import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react'
import { AnimatePresence, motion, useMotionValue, animate } from 'motion/react'
import './riffs.css'
import { CONTROLS, DATA_SHA256, FIRST_STAGE, IV, OLS, ci, fmt, stars, type Run } from './data'
import { reducedMotion, useTicker } from './usePaper'

// Riff · 创作台 — 工作台 × 排印, laid out like the Kimi / Claude desktop clients:
// studies on the left, the conversation with the research assistant in the middle,
// the manuscript as a typeset artifact on the right. The assistant edits the paper
// with a visible cursor: it travels to a semantic target, selects, then types.
// Trust comes from asking before wide edits and from one-click undo, not from gates.

const SERIF = { fontFamily: '"Times New Roman", "Noto Serif SC", "Songti SC", Times, serif' }
const DISPLAY = { fontFamily: '"Instrument Serif", "Noto Serif SC", Georgia, serif' }
const sleep = (ms: number) => new Promise((r) => setTimeout(r, reducedMotion() ? 0 : ms))

type Main = 'OLS' | 'IV'
type Tool = { id: string; label: string; detail: string; code: string; status: 'running' | 'done' }
type Msg =
  | { id: string; role: 'user'; text: string }
  | { id: string; role: 'agent'; author?: 'user'; text: string; shown: number; tools: Tool[]; ask?: { q: string; state: 'open' | 'yes' | 'no' }; edits?: { n: number; undone: boolean; undo: () => void } }

const RESULT: Record<Main | 'short', string> = {
  OLS: '控制工作经验、种族、城乡与 1966 年居住地区后，每多受一年教育，小时工资的对数约提高 0.075（约 7.5%），在 1% 水平上显著。',
  IV: '以是否在四年制大学附近长大作为教育年限的工具变量，每多受一年教育，小时工资的对数约提高 0.132（约 13.2%），在 5% 水平上显著；估计高于 OLS，但置信区间明显更宽。',
  short: '每多一年教育，小时工资约提高 7.5%（OLS，1% 水平显著）。',
}
const INTRO_OLD = '已有研究普遍发现，教育的工资回报约为 10%'
const INTRO_NEW = '本文 OLS 估计约为 7.5%，与已有研究量级相近'
const TABLE_NOTE = `第一阶段有效 F = ${FIRST_STAGE.fEff}，介于 10 与 23.1 之间，IV 的 t 检验可能过度拒绝。`

type Note = { id: number; target: string; tag: string; text: string; status: 'open' | 'done' }
const NOTES: Note[] = [
  { id: 1, target: 'intro', tag: '一致性', text: '引言说回报“约为 10%”，结果段主估计是 7.5%，读者会以为两处说的是同一个数。', status: 'open' },
  { id: 3, target: 'table', tag: '推断', text: `IV 第一阶段 F = ${FIRST_STAGE.f}，偏弱但可用，表注应说明。`, status: 'open' },
]

let uid = 0
const nid = () => `m${++uid}`

export default function StudioRiff() {
  // ---- manuscript state (in the real product: Document blocks + Refs resolved against Evidence)
  const [main, setMain] = useState<Main>('OLS')
  const [results, setResults] = useState(RESULT.OLS)
  const [intro, setIntro] = useState(INTRO_OLD)
  const [tableNote, setTableNote] = useState('')
  const [notes, setNotes] = useState(NOTES)
  const [booted, setBooted] = useState(0)
  const [slip, setSlip] = useState<{ run: Run; key: number } | null>(null)
  const [tab, setTab] = useState<'paper' | 'notebook'>('paper')
  const [traceCell, setTraceCell] = useState<number | null>(null)

  // ---- assistant state (in the real product: agent turn stream over SSE)
  const [msgs, setMsgs] = useState<Msg[]>([])
  // a study can hold several threads; only 改稿 is scripted in the prototype
  const [threads, setThreads] = useState<{ id: string; name: string; msgs: Msg[] }[]>([
    { id: 'edit', name: '改稿', msgs: [] },
    { id: 'data', name: '找数据', msgs: [
      { id: 'd1', role: 'user', text: '还有没有别的数据能做同一个问题？' },
      { id: 'd2', role: 'agent', text: 'CFPS 有受教育年限和收入，可以做中国的版本；但没有“大学邻近性”这类工具，只能做 OLS 或找别的工具。要我先列一下 CFPS 里可用的变量吗？', shown: 999, tools: [] },
    ] },
  ])
  const [active, setActive] = useState('edit')
  const [conclusion, setConclusion] = useState('')
  const [busy, setBusy] = useState(false)
  const pendingAsk = useRef<((yes: boolean) => void) | null>(null)
  const alive = useRef(true)
  useEffect(() => {
    alive.current = true
    return () => {
      alive.current = false
    }
  }, [])

  // ---- cursor state (in the real product: cursor.intent events → semantic target registry)
  const paperRef = useRef<HTMLDivElement>(null)
  const cx = useMotionValue(40)
  const cy = useMotionValue(40)
  const [cursor, setCursor] = useState<{ on: boolean; label: string; clicking: boolean }>({ on: false, label: '', clicking: false })
  const [selecting, setSelecting] = useState<string | null>(null)
  const [typing, setTyping] = useState<string | null>(null)

  const cursorTo = useCallback(async (target: string, label: string) => {
    const host = paperRef.current
    const el = host?.querySelector(`[data-target="${target}"]`) as HTMLElement | null
    if (!host || !el) return
    el.scrollIntoView({ block: 'center', behavior: reducedMotion() ? 'auto' : 'smooth' })
    await sleep(380)
    const h = host.getBoundingClientRect()
    const r = el.getBoundingClientRect()
    setCursor((c) => ({ ...c, on: true, label }))
    const x = r.left - h.left + Math.min(r.width * 0.15, 60)
    const y = r.top - h.top + host.scrollTop + 6
    await Promise.all([
      animate(cx, x, { type: 'spring', stiffness: 170, damping: 24 }),
      animate(cy, y, { type: 'spring', stiffness: 170, damping: 24 }),
    ])
  }, [cx, cy])

  const click = async () => {
    setCursor((c) => ({ ...c, clicking: true }))
    await sleep(160)
    setCursor((c) => ({ ...c, clicking: false }))
  }

  /** select the old text, then type the new text into `set` char by char */
  const retype = async (target: string, next: string, set: (s: string) => void) => {
    setSelecting(target)
    await sleep(520)
    setSelecting(null)
    setTyping(target)
    set('')
    const step = reducedMotion() ? next.length : 2
    for (let i = step; i <= next.length + step - 1 && alive.current; i += step) {
      set(next.slice(0, Math.min(i, next.length)))
      await sleep(22)
    }
    set(next)
    setTyping(null)
  }

  // ---- boot: history of this study, paper typesets
  useEffect(() => {
    const t: number[] = []
    for (let i = 1; i <= 6; i++) t.push(window.setTimeout(() => setBooted(i), 120 + i * 260))
    setMsgs([
      { id: nid(), role: 'user', text: '用 Card (1995) 的数据估计教育的工资回报，先 OLS 再 IV，写成一篇小论文的初稿。' },
      {
        id: nid(),
        role: 'agent',
        text: '初稿写好了，在右边。结果段用 OLS 作主设定：每多一年教育，工资约高 7.5%。IV 估计更大（约 13.2%），但区间很宽。审稿人在页边留了 2 条意见。',
        shown: 999,
        tools: [
          { id: 't1', label: '读取数据', detail: 'card1995.csv · 3,010 × 34', code: 'df = pd.read_csv("data_card1995.csv")', status: 'done' },
          { id: 't2', label: '运行 OLS', detail: `β = ${fmt(OLS.coef)} · HC1`, code: OLS.code, status: 'done' },
          { id: 't3', label: '运行 IV · nearc4', detail: `β = ${fmt(IV.coef)} · F ${FIRST_STAGE.f}`, code: IV.code, status: 'done' },
          { id: 't4', label: '起草 5 节', detail: '引言、数据、策略、结果、结论', code: '# 起草不产生数字；正文里的数字都引用上面三次运行', status: 'done' },
        ],
      },
    ])
    return () => t.forEach(clearTimeout)
  }, [])

  // ---- thread helpers
  const say = async (text: string, extra: Partial<Extract<Msg, { role: 'agent' }>> = {}) => {
    const id = nid()
    setMsgs((m) => [...m, { id, role: 'agent', text, shown: 0, tools: [], ...extra }])
    for (let i = 0; i <= text.length && alive.current; i += 3) {
      setMsgs((m) => m.map((x) => (x.id === id && x.role === 'agent' ? { ...x, shown: i } : x)))
      await sleep(16)
    }
    setMsgs((m) => m.map((x) => (x.id === id && x.role === 'agent' ? { ...x, shown: 999 } : x)))
    return id
  }
  const tool = async (msgId: string, t: Omit<Tool, 'status'>, ms = 700) => {
    setMsgs((m) => m.map((x) => (x.id === msgId && x.role === 'agent' ? { ...x, tools: [...x.tools, { ...t, status: 'running' }] } : x)))
    await sleep(ms)
    setMsgs((m) => m.map((x) => (x.id === msgId && x.role === 'agent' ? { ...x, tools: x.tools.map((y) => (y.id === t.id ? { ...y, status: 'done' } : y)) } : x)))
  }
  const ask = (msgId: string, q: string) =>
    new Promise<boolean>((resolve) => {
      setMsgs((m) => m.map((x) => (x.id === msgId && x.role === 'agent' ? { ...x, ask: { q, state: 'open' } } : x)))
      pendingAsk.current = (yes) => {
        setMsgs((m) => m.map((x) => (x.id === msgId && x.role === 'agent' && x.ask ? { ...x, ask: { ...x.ask, state: yes ? 'yes' : 'no' } } : x)))
        resolve(yes)
      }
    })
  const edits = (msgId: string, n: number, undo: () => void) =>
    setMsgs((m) => m.map((x) => (x.id === msgId && x.role === 'agent' ? { ...x, edits: { n, undone: false, undo } } : x)))

  /** a direct edit by the author: same ChangeSet shape as the assistant's, author = user */
  const userEdit = (label: string, before: string, after: string, set: (v: string) => void) => {
    if (before === after) return
    set(after)
    const id = nid()
    setMsgs((m) => [...m, { id, role: 'agent', text: `你改了${label}。`, shown: 999, tools: [], author: 'user', edits: { n: 1, undone: false, undo: () => set(before) } }])
  }

  // ---- scenarios
  async function switchToIV() {
    const m1 = await say('好。换成 IV 之前，我先确认一下工具强度。')
    await tool(m1, { id: 'fs', label: '检查第一阶段', detail: `F = ${FIRST_STAGE.f} · 有效 F = ${FIRST_STAGE.fEff}`, code: 'statspai.effective_f_test(df, endog="educ",\n    instruments=["nearc4"], exog=controls, vcov="HC1")' })
    const m2 = await say('工具强度中等，可以用，但要在表注里说明。换主设定会改到 3 处：表 1 的主列、结果段和图 1。')
    const yes = await ask(m2, '直接改吗？改完可以一键撤销。')
    if (!yes) return say('好，先不动。需要时再说。')
    const before = { main, results, tableNote }
    setCursor((c) => ({ ...c, on: true }))
    await cursorTo('table-main', '研究助手 · 改表 1')
    await click()
    setMain('IV')
    await sleep(500)
    await cursorTo('figure', '研究助手 · 重画图 1')
    await click()
    await sleep(700)
    await cursorTo('results', '研究助手 · 改结果段')
    await retype('results', RESULT.IV, setResults)
    await cursorTo('table-note', '研究助手 · 补表注')
    await retype('table-note', TABLE_NOTE, setTableNote)
    setNotes((ns) => ns.map((n) => (n.id === 3 ? { ...n, status: 'done' } : n)))
    setCursor((c) => ({ ...c, on: false }))
    const m3 = await say('改好了：主设定换成 IV，结果段、表 1、图 1 都已更新，表注也补上了，顺带处理了审稿意见 3。')
    edits(m3, 4, () => {
      setMain(before.main)
      setResults(before.results)
      setTableNote(before.tableNote)
      setNotes((ns) => ns.map((n) => (n.id === 3 ? { ...n, status: 'open' } : n)))
    })
  }

  async function fixIntro() {
    const m1 = await say('审稿意见 1：引言和结果段的数字对不上。我把引言那句改成和本文估计一致。')
    const before = intro
    await cursorTo('intro-claim', '研究助手 · 改引言')
    await retype('intro-claim', INTRO_NEW, setIntro)
    setNotes((ns) => ns.map((n) => (n.id === 1 ? { ...n, status: 'done' } : n)))
    setCursor((c) => ({ ...c, on: false }))
    edits(m1, 1, () => {
      setIntro(before)
      setNotes((ns) => ns.map((n) => (n.id === 1 ? { ...n, status: 'open' } : n)))
    })
  }

  async function shorten() {
    const m1 = await say('好，结果段压成一句。')
    const before = results
    await cursorTo('results', '研究助手 · 改结果段')
    await retype('results', main === 'OLS' ? RESULT.short : '每多一年教育，小时工资约提高 13.2%（IV，5% 水平显著），但区间较宽。', setResults)
    setCursor((c) => ({ ...c, on: false }))
    edits(m1, 1, () => setResults(before))
  }

  async function send(text: string) {
    const t = text.trim()
    if (!t || busy) return
    setBusy(true)
    setMsgs((m) => [...m, { id: nid(), role: 'user', text: t }])
    await sleep(350)
    try {
      if (/iv|主设定|工具/i.test(t) && main === 'OLS') await switchToIV()
      else if (/意见|引言|审稿|一致/.test(t)) await fixIntro()
      else if (/短|精简|一句/.test(t)) await shorten()
      else await say('这个原型只接了三件事：把主设定换成 IV、处理审稿意见 1、把结果段写短。真实产品里这里接的是研究助手。')
    } finally {
      if (alive.current) setBusy(false)
    }
  }

  const suggestions = [main === 'OLS' && '把主设定换成 IV', notes[0].status === 'open' && '处理审稿意见 1', '把结果段写短一点'].filter(Boolean) as string[]

  return (
    <div className="flex h-screen bg-[#f7f5f0] text-ink">
      <Sidebar
        threads={threads.map((t) => ({ id: t.id, name: t.name, count: t.id === 'edit' ? msgs.length : t.msgs.length }))}
        active={active}
        onPick={setActive}
        onNew={() => {
          const id = `t${threads.length + 1}`
          setThreads((ts) => [...ts, { id, name: `新对话 ${ts.length - 1}`, msgs: [] }])
          setActive(id)
        }}
      />
      <Thread
        title={threads.find((t) => t.id === active)?.name ?? '改稿'}
        msgs={active === 'edit' ? msgs : threads.find((t) => t.id === active)?.msgs ?? []}
        busy={busy}
        suggestions={active === 'edit' ? suggestions : []}
        onSend={(t) => {
          if (active === 'edit') return send(t)
          setThreads((ts) => ts.map((x) => (x.id === active ? { ...x, msgs: [...x.msgs, { id: nid(), role: 'user', text: t }, { id: nid(), role: 'agent', text: '这条线程在原型里没有接脚本。真实产品里每条线程是独立的对话，共用同一份稿子和数据。', shown: 999, tools: [] }] } : x)))
        }}
        onAnswer={(y) => pendingAsk.current?.(y)}
        onUndo={(id) =>
          setMsgs((ms) =>
            ms.map((x) => {
              if (x.id !== id || x.role !== 'agent' || !x.edits || x.edits.undone) return x
              x.edits.undo()
              return { ...x, edits: { ...x.edits, undone: true } }
            }),
          )
        }
      />

      {/* artifact: the manuscript */}
      <section className="flex min-w-0 flex-1 flex-col border-l border-black/[.06] bg-[#efece5]">
        <div className="flex h-12 shrink-0 items-center gap-1 border-b border-black/[.06] bg-[#f7f5f0] px-4 text-[13px]">
          {(['paper', 'notebook'] as const).map((t) => (
            <button key={t} onClick={() => setTab(t)} className={`rounded-lg px-3 py-1.5 transition-colors duration-150 ${tab === t ? 'bg-white text-ink shadow-[0_1px_2px_rgba(0,0,0,.06)]' : 'text-muted hover:text-ink'}`}>
              {t === 'paper' ? '稿子' : 'Notebook'}
            </button>
          ))}
          <span className="ml-3 font-mono text-[11px] text-muted">manuscript · v{3 + msgs.filter((m) => m.role === 'agent' && m.edits && !m.edits.undone).length}</span>
          <span className="ml-auto flex items-center gap-1.5 text-[12px] text-muted">
            主设定
            <motion.span key={main} initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} className="rounded-md bg-white px-2 py-0.5 font-mono text-[11px] text-ink shadow-[0_1px_2px_rgba(0,0,0,.06)]">
              {main}
            </motion.span>
          </span>
        </div>

        {tab === 'paper' ? (
          <div ref={paperRef} className="relative flex-1 overflow-y-auto px-8 pb-40 pt-8" onClick={() => setSlip(null)}>
            <article className="relative mx-auto w-full max-w-[860px] rounded-[3px] bg-[#fffdf9] px-14 pb-20 pt-12 text-[#151515] shadow-[0_1px_2px_rgba(0,0,0,.05),0_12px_40px_rgba(24,21,21,.08)]" style={SERIF}>
              <p className="mb-7 flex justify-between font-mono text-[10px] uppercase tracking-[.18em] text-[#8a857c]">
                <span>Working draft · econpaper</span>
                <span>Education &amp; Earnings</span>
              </p>
              <h1 className="rf-set text-[30px] leading-[1.2]" style={DISPLAY}>教育的工资回报：来自大学邻近性的证据</h1>
              <p className="rf-rise mt-2 text-[13px] italic text-[#666]" style={{ animationDelay: '.15s' }}>NLS Young Men 1976 · 3,010 人 · Card (1995)</p>

              <Row show={booted >= 1} margin={<NoteCard note={notes[0]} onFix={() => send('处理审稿意见 1')} busy={busy} />}>
                <H n={1}>引言</H>
                <p className="indent-[2em]">
                  教育能在多大程度上提高收入，是劳动经济学最基本的问题之一。
                  <Typed target="intro-claim" selecting={selecting} typing={typing}>{intro}</Typed>
                  ，但这些估计可能混入了能力差异。本文先给出 OLS 基准，再以大学邻近性作为工具变量。
                </p>
              </Row>

              <Row show={booted >= 2}>
                <H n={2}>数据</H>
                <p className="indent-[2em]">
                  样本来自全国青年男性追踪调查（NLS），使用 1976 年的工资与教育信息，共 <Ref run={OLS} value={OLS.n} digits={0} onOpen={(r) => setSlip({ run: r, key: Date.now() })} /> 个观测。
                </p>
              </Row>

              <Row show={booted >= 3}>
                <H n={3}>实证策略</H>
                <p className="my-2 text-center italic">ln w<sub>i</sub> = α + β·educ<sub>i</sub> + X<sub>i</sub>′γ + ε<sub>i</sub></p>
                <p className="indent-[2em]">OLS 可能因能力等遗漏变量而有偏，因此以“是否在四年制大学附近长大”作为教育的工具变量。</p>
              </Row>

              <Row
                show={booted >= 4}
                margin={
                  <>
                    <NoteCard note={notes[1]} onFix={() => send('把主设定换成 IV')} busy={busy} />
                    <AnimatePresence>{slip && <Slip key={slip.key} run={slip.run} onOpen={() => { setTab('notebook'); setTraceCell(slip.run.method === 'OLS' ? 2 : 3) }} />}</AnimatePresence>
                  </>
                }
              >
                <H n={4}>结果</H>
                <Table main={main} note={tableNote} selecting={selecting} typing={typing} onOpen={(r) => setSlip({ run: r, key: Date.now() })} />
              </Row>

              <Row show={booted >= 5}>
                <Editable value={results} locked={busy} onSave={(v) => userEdit('结果段', results, v, setResults)}>
                  <p className="indent-[2em]">
                    <Typed target="results" selecting={selecting} typing={typing}>{results}</Typed>
                    <span className="ml-1 font-sans text-[12.5px] text-[#8a857c]">
                      （β̂ = <Ref run={main === 'OLS' ? OLS : IV} value={(main === 'OLS' ? OLS : IV).coef} onOpen={(r) => setSlip({ run: r, key: Date.now() })} />）
                    </span>
                  </p>
                </Editable>
              </Row>

              <Row show={booted >= 5}>
                <Figure main={main} />
              </Row>

              <Row show={booted >= 6}>
                <H n={5}>结论</H>
                <Editable value={conclusion} locked={busy} onSave={(v) => userEdit('结论', conclusion, v, setConclusion)} placeholder="点这里直接写，或让研究助手先起个头。">
                  <p className={`indent-[2em] ${conclusion ? '' : 'text-[#8a857c]'}`}>{conclusion || '（待写。点这里直接写，或让研究助手先起个头。）'}</p>
                </Editable>
              </Row>
            </article>

            <AgentCursor x={cx} y={cy} {...cursor} />
          </div>
        ) : (
          <Notebook trace={traceCell} main={main} />
        )}
      </section>
    </div>
  )
}

/* ------------------------------------------------------------------ sidebar */

function Sidebar({ threads, active, onPick, onNew }: { threads: { id: string; name: string; count: number }[]; active: string; onPick: (id: string) => void; onNew: () => void }) {
  return (
    <aside className="flex w-[232px] shrink-0 flex-col px-3 pb-3 pt-4 text-[13px]">
      <div className="flex items-center justify-between px-2">
        <span className="text-[21px] leading-none" style={DISPLAY}>econpaper</span>
        <span className="text-muted">⌘</span>
      </div>
      <button className="mt-5 flex items-center gap-2 rounded-xl border border-black/[.08] bg-white px-3 py-2 text-left shadow-[0_1px_2px_rgba(0,0,0,.04)] transition-transform duration-100 active:scale-[.98]">
        <span className="text-accent">＋</span> 新研究
      </button>
      <p className="mt-6 px-2 text-[11px] text-muted">研究</p>
      <div className="mt-1 rounded-xl bg-black/[.05] px-3 py-2">
        <p className="truncate font-medium">教育的工资回报</p>
        <p className="mt-0.5 truncate text-[11.5px] text-muted">初稿 · 稿子与数据共用</p>
        <div className="mt-2 space-y-0.5 border-l border-black/10 pl-2">
          {threads.map((t) => (
            <button key={t.id} onClick={() => onPick(t.id)} className={`flex w-full items-center gap-2 rounded-lg px-2 py-1 text-left text-[12.5px] transition-colors duration-150 ${t.id === active ? 'bg-white text-ink shadow-[0_1px_2px_rgba(0,0,0,.05)]' : 'text-ink/70 hover:bg-white/60'}`}>
              <span className="truncate">{t.name}</span>
              <span className="ml-auto text-[11px] text-muted">{t.count}</span>
            </button>
          ))}
          <button onClick={onNew} className="w-full rounded-lg px-2 py-1 text-left text-[12.5px] text-muted hover:bg-white/60 hover:text-ink">＋ 新对话</button>
        </div>
      </div>
      {[
        ['最低工资与就业', '数据检查中'],
        ['数字金融与创业', '只有想法'],
      ].map(([t, s]) => (
        <button key={t} className="mt-1 rounded-xl px-3 py-2 text-left transition-colors duration-150 hover:bg-black/[.03]">
          <p className="truncate">{t}</p>
          <p className="mt-0.5 truncate text-[11.5px] text-muted">{s}</p>
        </button>
      ))}
      <div className="mt-auto flex items-center gap-2 px-2 text-muted">
        <span className="grid h-6 w-6 place-items-center rounded-full bg-ink text-[11px] text-paper">奕</span>
        <span className="text-[12.5px]">我的研究</span>
      </div>
    </aside>
  )
}

/* ------------------------------------------------------------------ thread */

function Thread({ title, msgs, busy, suggestions, onSend, onAnswer, onUndo }: { title: string; msgs: Msg[]; busy: boolean; suggestions: string[]; onSend: (t: string) => void; onAnswer: (y: boolean) => void; onUndo: (id: string) => void }) {
  const [text, setText] = useState('')
  const end = useRef<HTMLDivElement>(null)
  useEffect(() => {
    end.current?.scrollIntoView({ block: 'end', behavior: 'smooth' })
  }, [msgs])
  return (
    <main className="flex w-[430px] shrink-0 flex-col border-l border-black/[.06] bg-[#faf9f6]">
      <div className="flex h-12 shrink-0 items-center border-b border-black/[.06] px-5 text-[13px]">
        <span className="font-medium">{title}</span>
        <span className="ml-2 text-muted">· 教育的工资回报</span>
      </div>
      <div className="flex-1 space-y-5 overflow-y-auto px-5 py-5 text-[14px] leading-[1.7]">
        {msgs.map((m) =>
          m.role === 'user' ? (
            <div key={m.id} className="rf-rise ml-auto max-w-[85%] rounded-2xl bg-[#ebe8e0] px-3.5 py-2">{m.text}</div>
          ) : (
            m.author === 'user' ? (
              <div key={m.id} className="rf-rise flex items-center gap-2 rounded-xl border border-dashed border-black/10 px-3 py-2 text-[12.5px] text-muted">
                <span>✎ {m.text}</span>
                {m.edits && (m.edits.undone ? <span className="ml-auto">已撤销</span> : <button disabled={busy} onClick={() => onUndo(m.id)} className="ml-auto rounded-md px-2 py-0.5 hover:bg-black/[.05] hover:text-ink">撤销</button>)}
              </div>
            ) : (
            <div key={m.id} className="rf-rise">
              <div className="mb-1.5 flex items-center gap-1.5 text-[12px] text-muted">
                <span className="grid h-4 w-4 place-items-center rounded-full bg-accent text-[9px] text-white">研</span> 研究助手
              </div>
              {m.tools.length > 0 && (
                <div className="mb-2 space-y-1">
                  {m.tools.map((t) => <ToolCard key={t.id} t={t} />)}
                </div>
              )}
              <p>
                {m.text.slice(0, m.shown)}
                {m.shown < m.text.length && <span className="rf-caret text-accent">▍</span>}
              </p>
              {m.ask && (
                <div className="rf-rise mt-2 rounded-xl border border-black/[.08] bg-white p-3">
                  <p className="text-[13.5px]">{m.ask.q}</p>
                  {m.ask.state === 'open' ? (
                    <div className="mt-2 flex gap-2 text-[13px]">
                      <button onClick={() => onAnswer(true)} className="rounded-lg bg-ink px-3 py-1 text-white transition-transform duration-100 active:scale-[.97]">改吧</button>
                      <button onClick={() => onAnswer(false)} className="rounded-lg px-3 py-1 text-muted hover:bg-black/[.04] active:scale-[.97]">先不改</button>
                    </div>
                  ) : (
                    <p className="mt-1 text-[12.5px] text-muted">{m.ask.state === 'yes' ? '你选了：改吧' : '你选了：先不改'}</p>
                  )}
                </div>
              )}
              {m.edits && (
                <div className="rf-rise mt-2 flex items-center gap-2 rounded-xl bg-accent/[.07] px-3 py-2 text-[12.5px]">
                  <span className="text-accent">✓</span>
                  {m.edits.undone ? <span className="text-muted">已撤销，稿子回到改之前</span> : <span>稿子里改了 {m.edits.n} 处</span>}
                  {!m.edits.undone && (
                    <button
                      disabled={busy}
                      onClick={() => onUndo(m.id)}
                      className="ml-auto rounded-md px-2 py-0.5 text-muted hover:bg-black/[.05] hover:text-ink"
                    >
                      撤销
                    </button>
                  )}
                </div>
              )}
            </div>
            )
          ),
        )}
        <div ref={end} />
      </div>
      <div className="shrink-0 px-4 pb-[72px] pt-2">
        {!busy && suggestions.length > 0 && (
          <div className="mb-2 flex flex-wrap gap-1.5">
            {suggestions.map((s) => (
              <button key={s} onClick={() => onSend(s)} className="rf-rise rounded-full border border-black/[.08] bg-white px-3 py-1 text-[12.5px] text-muted transition-colors duration-150 hover:border-black/20 hover:text-ink">
                {s}
              </button>
            ))}
          </div>
        )}
        <form
          onSubmit={(e) => {
            e.preventDefault()
            onSend(text)
            setText('')
          }}
          className="rounded-2xl border border-black/[.09] bg-white p-3 shadow-[0_4px_18px_rgba(24,21,21,.06)]"
        >
          <textarea
            rows={2}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                onSend(text)
                setText('')
              }
            }}
            disabled={busy}
            placeholder={busy ? '研究助手正在改稿…' : '让研究助手改稿、换设定、补检验…'}
            className="w-full resize-none bg-transparent text-[14px] outline-none placeholder:text-muted/70"
          />
          <div className="mt-1 flex items-center gap-3 text-[13px] text-muted">
            <span title="附加数据">＋</span>
            <span title="引用稿子里的一段">¶</span>
            <button type="submit" disabled={busy || !text.trim()} className="ml-auto grid h-7 w-7 place-items-center rounded-lg bg-ink text-white transition-transform duration-100 active:scale-[.94] disabled:opacity-30">↑</button>
          </div>
        </form>
      </div>
    </main>
  )
}

function ToolCard({ t }: { t: Tool }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="overflow-hidden rounded-lg border border-black/[.07] bg-white text-[12.5px]">
      <button onClick={() => setOpen((o) => !o)} className="flex w-full items-center gap-2 px-2.5 py-1.5 text-left">
        {t.status === 'running' ? (
          <span className="inline-block h-3 w-3 animate-spin rounded-full border-[1.5px] border-accent border-t-transparent" />
        ) : (
          <span className="text-accent">✓</span>
        )}
        <span>{t.label}</span>
        <span className="truncate font-mono text-[11px] text-muted">{t.status === 'running' ? '运行中…' : t.detail}</span>
        <span className={`ml-auto text-muted transition-transform duration-150 ${open ? 'rotate-90' : ''}`}>›</span>
      </button>
      {open && <pre className="rf-rise overflow-x-auto border-t border-black/[.05] bg-[#fafaf8] px-2.5 py-2 font-mono text-[11px] leading-5">{t.code}</pre>}
    </div>
  )
}

/* ------------------------------------------------------------------ manuscript pieces */

function Row({ show, margin, children }: { show: boolean; margin?: ReactNode; children: ReactNode }) {
  if (!show) return null
  return (
    <div className="rf-set mt-6 grid grid-cols-[minmax(0,1fr)_190px] gap-8 text-[15.5px] leading-[1.85] [text-align:justify]">
      <div className="min-w-0">{children}</div>
      <div className="relative space-y-3 text-left" style={{ fontFamily: '-apple-system, "PingFang SC", sans-serif' }}>{margin}</div>
    </div>
  )
}

function H({ n, children }: { n: number; children: ReactNode }) {
  return (
    <h2 className="mb-1.5 text-[16px] font-bold tracking-[.02em]">
      <span className="mr-2 font-normal text-[#8a857c]">{n}</span>
      {children}
    </h2>
  )
}

/** Text the assistant can select and retype. data-target is its semantic id. */
function Typed({ target, selecting, typing, children }: { target: string; selecting: string | null; typing: string | null; children: ReactNode }) {
  return (
    <span data-target={target}>
      <span className={`rounded-sm [box-decoration-break:clone] transition-colors duration-150 ${selecting === target ? 'bg-accent/25' : ''}`}>{children}</span>
      {typing === target && <span className="rf-caret -ml-px font-sans text-accent">|</span>}
    </span>
  )
}

function Ref({ run, value, digits = 4, stale, onOpen }: { run: Run; value: number; digits?: number; stale?: boolean; onOpen: (r: Run) => void }) {
  const v = useTicker(value)
  return (
    <button
      onClick={(e) => {
        e.stopPropagation()
        onOpen(run)
      }}
      className={`rf-tnum border-b border-dotted transition-colors duration-150 ${stale ? 'border-warning text-warning' : 'border-accent/50 hover:text-accent'}`}
      title="这个数字从哪来"
    >
      {digits ? v.toFixed(digits) : Math.round(v).toLocaleString()}
    </button>
  )
}

function Table({ main, note, selecting, typing, onOpen }: { main: Main; note: string; selecting: string | null; typing: string | null; onOpen: (r: Run) => void }) {
  const col = main === 'OLS' ? 0 : 1
  return (
    <figure className="my-2 text-[13.5px]">
      <figcaption className="mb-1.5 text-center text-[13px]">表 1　教育对小时工资对数的影响</figcaption>
      <div className="rf-draw-x h-[1.2px] bg-[#151515]" />
      <div className="relative">
        {/* the main-spec column highlight slides between columns */}
        <motion.div data-target="table-main" className="absolute bottom-0 top-0 w-[27%] rounded-sm bg-accent/[.08]" animate={{ left: col === 0 ? '46%' : '73%' }} transition={{ type: 'spring', stiffness: 260, damping: 28 }} />
        <div className="relative grid grid-cols-[46%_27%_27%] py-1">
          <span />
          {[OLS, IV].map((r, i) => (
            <span key={r.method} className={`text-right transition-colors duration-300 ${i === col ? 'text-accent' : ''}`}>({i + 1}) {r.method}{i === col && ' · 主'}</span>
          ))}
        </div>
        <div className="rf-draw-x h-[.6px] bg-[#151515]" style={{ animationDelay: '.12s' }} />
        <div className="relative grid grid-cols-[46%_27%_27%] py-1.5">
          <span>受教育年限</span>
          {[OLS, IV].map((r) => (
            <span key={r.method} className="text-right">
              <Ref run={r} value={r.coef} onOpen={onOpen} />
              <sup>{stars(r.p)}</sup>
              <span className="block text-[12px] text-[#666]">({fmt(r.se)})</span>
            </span>
          ))}
        </div>
        <div className="relative grid grid-cols-[46%_27%_27%] pb-1.5 text-[#666]">
          <span>第一阶段 F</span>
          <span className="text-right">—</span>
          <span className="rf-tnum text-right">{FIRST_STAGE.f}</span>
        </div>
      </div>
      <div className="rf-draw-x h-[1.2px] bg-[#151515]" style={{ animationDelay: '.24s' }} />
      <p className="mt-1.5 text-[12px] leading-[1.6] text-[#666]">
        注：括号内为标准误，OLS 为 HC1 稳健标准误；N = 3,010。*** p&lt;0.01，** p&lt;0.05。{' '}
        <Typed target="table-note" selecting={selecting} typing={typing}>{note}</Typed>
      </p>
    </figure>
  )
}

function Figure({ main }: { main: Main }) {
  const W = 520
  const x = (v: number) => 40 + (Math.max(0, v) / 0.26) * (W - 60)
  return (
    <figure data-target="figure" className="my-2">
      <svg key={main} viewBox={`0 0 ${W} 104`} className="w-full" style={{ fontFamily: 'ui-monospace, Menlo, monospace' }}>
        <line x1={x(0)} x2={x(0.26)} y1={80} y2={80} stroke="#151515" strokeWidth={0.7} />
        {[0, 0.1, 0.2].map((t) => (
          <text key={t} x={x(t)} y={96} fontSize={9} textAnchor="middle" fill="#777">{t.toFixed(1)}</text>
        ))}
        {[OLS, IV].map((r, i) => {
          const [lo, hi] = ci(r)
          const y = 26 + i * 30
          const on = main === r.method
          return (
            <g key={r.method}>
              <text x={2} y={y + 3} fontSize={10} fill={on ? '#2f6b4f' : '#151515'}>{r.method}</text>
              <line x1={x(lo)} x2={x(hi)} y1={y} y2={y} stroke={on ? '#2f6b4f' : '#151515'} strokeWidth={on ? 2 : 1} className="rf-stroke" style={{ ['--len' as string]: x(hi) - x(lo), animationDelay: `${i * 0.15}s` }} />
              <circle cx={x(r.coef)} cy={y} r={on ? 4 : 3} fill={on ? '#2f6b4f' : '#151515'} className="rf-rise" style={{ animationDelay: `${0.5 + i * 0.15}s` }} />
            </g>
          )
        })}
      </svg>
      <figcaption className="text-[12.5px] leading-[1.6]">图 1　两种估计及其 95% 置信区间：IV 高于 OLS，但区间宽得多。主设定以绿色标出。</figcaption>
    </figure>
  )
}

function NoteCard({ note, onFix, busy }: { note: Note; onFix: () => void; busy: boolean }) {
  return (
    <div className={`rf-rise border-l-2 pl-3 text-[12.5px] leading-[1.6] transition-opacity duration-300 ${note.status === 'done' ? 'border-accent opacity-50' : 'border-[#d6a23a]'}`} style={{ animationDelay: '.4s' }}>
      <p className="text-[11px] font-medium text-[#a8791c]">审稿 · {note.tag}</p>
      <p className="mt-0.5 text-[#3a3834]">{note.text}</p>
      {note.status === 'open' ? (
        <button disabled={busy} onClick={(e) => { e.stopPropagation(); onFix() }} className="mt-1 text-accent hover:underline disabled:text-muted disabled:no-underline">让助手处理 →</button>
      ) : (
        <p className="mt-1 text-accent">✓ 已处理</p>
      )}
    </div>
  )
}

function Slip({ run, onOpen }: { run: Run; onOpen: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -6 }}
      transition={{ duration: 0.2, ease: [0.23, 1, 0.32, 1] }}
      onClick={(e) => e.stopPropagation()}
      className="rounded-lg border border-black/[.08] bg-white p-2.5 text-[12px] shadow-[0_4px_16px_rgba(0,0,0,.06)]"
    >
      <p className="text-[11px] text-muted">这个数字来自</p>
      <p className="font-medium">{run.label}</p>
      <p className="mt-0.5 font-mono text-[10.5px] text-muted">{run.id} · {run.cov}</p>
      <button onClick={onOpen} className="mt-1.5 text-accent hover:underline">在 Notebook 里看 →</button>
    </motion.div>
  )
}

/** Full disclosure: every computation that produced a number in the paper, as it actually ran. */
function Notebook({ trace, main }: { trace: number | null; main: Main }) {
  const ctrl = CONTROLS.join(' + ')
  const cells = [
    { id: 1, used: '数据节：3,010 个观测', code: `import pandas as pd\nimport statspai\n\ndf = pd.read_csv("data_card1995.csv")\ndf = df.drop(columns=[c for c in df.columns if c.lower() in {"rownames", "unnamed: 0"}])\ncontrols = ${JSON.stringify(CONTROLS)}`, out: 'df.shape = (3010, 34)' },
    { id: 2, used: `表 1 第 (1) 列${main === 'OLS' ? '、结果段' : ''}`, code: `ols = statspai.feols(\n    "lwage ~ educ + ${ctrl}",\n    data=df)`, out: `educ  ${fmt(OLS.coef)}  (${fmt(OLS.se)})  p<0.001  n=3010  · 标准误 HC1` },
    { id: 3, used: `表 1 第 (2) 列${main === 'IV' ? '、结果段' : ''}、图 1`, code: `iv = statspai.ivreg(\n    "lwage ~ (educ ~ nearc4) + ${ctrl}",\n    data=df)`, out: `educ  ${fmt(IV.coef)}  (${fmt(IV.se)})  p=${IV.p}  n=3010  · 标准误 nonrobust` },
    { id: 4, used: '表 1 第一阶段 F、表注', code: 'ftest = statspai.effective_f_test(\n    df, endog="educ", instruments=["nearc4"],\n    exog=controls, vcov="HC1")', out: `first_stage_F = ${FIRST_STAGE.f}   F_eff = ${FIRST_STAGE.fEff}   strength = Moderate` },
  ]
  const py = [
    '# econpaper 复现脚本 · 教育的工资回报（Card, 1995）',
    '# 这是本研究实际运行的调用，按运行顺序排列；注释里是本次记录的结果。',
    `# 数据：StatsPAI 仓库 papers/data_card1995.csv，sha256 ${DATA_SHA256}`,
    '',
    ...cells.flatMap((c) => [`# [${c.id}] 用于：${c.used}`, c.code.replace(/\\n/g, '\n'), `# 记录：${c.out}`, '']),
    'print(ols, iv, ftest, sep="\\n\\n")',
  ].join('\n')
  const stata = [
    '* econpaper · 教育的工资回报 · Stata 版',
    '* 翻译自实际运行的 Python 代码，数值尚未与 Python 结果核对。',
    'import delimited "data_card1995.csv", clear',
    `local controls ${CONTROLS.join(' ')}`,
    "regress lwage educ `controls', vce(robust)",
    "ivregress 2sls lwage (educ = nearc4) `controls'",
    'estat firststage',
  ].join('\n')
  const r = [
    '# econpaper · 教育的工资回报 · R 版',
    '# 翻译自实际运行的 Python 代码，数值尚未与 Python 结果核对。',
    'library(fixest)',
    'df <- read.csv("data_card1995.csv")',
    `ctrl <- "${ctrl}"`,
    'ols <- feols(as.formula(paste("lwage ~ educ +", ctrl)), data = df, vcov = "hetero")',
    'iv  <- feols(as.formula(paste("lwage ~", ctrl, "| educ ~ nearc4")), data = df, vcov = "iid")',
    'fitstat(iv, "ivf")',
  ].join('\n')
  const download = (name: string, text: string) => {
    const url = URL.createObjectURL(new Blob([text], { type: 'text/plain;charset=utf-8' }))
    const a = document.createElement('a')
    a.href = url
    a.download = name
    a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }
  return (
    <div className="flex-1 overflow-y-auto px-8 pb-40 pt-6">
      <div className="mx-auto max-w-[780px]">
        <div className="rounded-xl border border-black/[.07] bg-white p-4 text-[13px]">
          <p className="font-medium">这份稿子里的每个数字，都来自下面这些代码</p>
          <p className="mt-1 text-[12.5px] leading-[1.6] text-muted">按实际运行顺序记录，只读。代码会随稿子一起交给读者：可以复制，也可以下载后在自己的电脑上重跑。</p>
          <dl className="mt-3 grid grid-cols-[88px_1fr] gap-y-1 font-mono text-[11.5px]">
            <dt className="text-muted">数据</dt><dd>data_card1995.csv · 3,010 × 34</dd>
            <dt className="text-muted">sha256</dt><dd className="truncate">{DATA_SHA256}</dd>
            <dt className="text-muted">环境</dt><dd>Python 3.12 · statspai（本地源码依赖）</dd>
          </dl>
          <div className="mt-3 flex flex-wrap gap-2 text-[12.5px]">
            <button onClick={() => download('analysis.py', py)} className="rounded-lg bg-ink px-3 py-1.5 text-white active:scale-[.97]">下载 analysis.py · 实际运行的代码</button>
            <button onClick={() => download('analysis.do', stata)} className="rounded-lg border border-black/10 px-3 py-1.5 active:scale-[.97]">Stata · 翻译版，数值未核对</button>
            <button onClick={() => download('analysis.R', r)} className="rounded-lg border border-black/10 px-3 py-1.5 active:scale-[.97]">R · 翻译版，数值未核对</button>
          </div>
        </div>
        <div className="mt-3 space-y-3">
          {cells.map((c) => (
            <div key={c.id} className={`overflow-hidden rounded-xl border bg-white transition-shadow duration-300 ${trace === c.id ? 'border-accent/50 shadow-[0_0_0_4px_rgba(47,107,79,.12)]' : 'border-black/[.07]'}`}>
              <div className="flex items-center gap-2 border-b border-black/[.05] px-3 py-1.5 font-mono text-[10.5px] text-muted">
                <span>[{c.id}] ✓</span>
                <span className="ml-auto rounded bg-accent/[.08] px-1.5 py-0.5 font-sans text-[11px] text-accent">用于：{c.used}</span>
              </div>
              <pre className="overflow-x-auto px-4 py-2.5 font-mono text-[12px] leading-[1.7]">{c.code}</pre>
              <pre className="border-t border-black/[.05] bg-[#fafaf8] px-4 py-2 font-mono text-[12px] text-ink/80">{c.out}</pre>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

/** Author edits prose directly. Numbers stay refs and are not editable; locked while the assistant works. */
function Editable({ value, locked, onSave, placeholder, children }: { value: string; locked: boolean; onSave: (v: string) => void; placeholder?: string; children: ReactNode }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(value)
  const ref = useRef<HTMLTextAreaElement>(null)
  useEffect(() => {
    if (editing && ref.current) {
      ref.current.focus()
      ref.current.style.height = `${ref.current.scrollHeight}px`
    }
  }, [editing])
  if (editing)
    return (
      <div className="rounded-sm ring-1 ring-accent/40">
        <textarea
          ref={ref}
          value={draft}
          placeholder={placeholder}
          onChange={(e) => {
            setDraft(e.target.value)
            e.target.style.height = `${e.target.scrollHeight}px`
          }}
          onKeyDown={(e) => {
            if (e.key === 'Escape') setEditing(false)
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
              onSave(draft.trim())
              setEditing(false)
            }
          }}
          onBlur={() => {
            onSave(draft.trim())
            setEditing(false)
          }}
          className="block w-full resize-none bg-transparent px-1 indent-[2em] leading-[1.85] outline-none"
        />
        <p className="px-1 pb-1 text-right font-sans text-[11px] text-muted">⌘↵ 保存 · Esc 取消 · 数字由计算生成，不在这里改</p>
      </div>
    )
  return (
    <div
      onClick={(e) => {
        if (locked || (e.target as HTMLElement).closest('button')) return
        setDraft(value)
        setEditing(true)
      }}
      title={locked ? '研究助手正在改稿，稍后再编辑' : '点击直接编辑'}
      className={`group relative rounded-sm transition-colors duration-150 ${locked ? '' : 'cursor-text hover:bg-black/[.025]'}`}
    >
      {children}
      {!locked && <span className="absolute -left-6 top-1 font-sans text-[12px] text-muted opacity-0 transition-opacity duration-150 group-hover:opacity-100">✎</span>}
    </div>
  )
}

/* ------------------------------------------------------------------ agent cursor */

function AgentCursor({ x, y, on, label, clicking }: { x: ReturnType<typeof useMotionValue<number>>; y: ReturnType<typeof useMotionValue<number>>; on: boolean; label: string; clicking: boolean }) {
  return (
    <motion.div className="pointer-events-none absolute left-0 top-0 z-30" style={{ x, y }} animate={{ opacity: on ? 1 : 0 }} transition={{ duration: 0.2 }}>
      <motion.svg width="18" height="20" viewBox="0 0 18 20" animate={{ scale: clicking ? 0.82 : 1 }} transition={{ type: 'spring', stiffness: 600, damping: 20 }} className="drop-shadow-[0_2px_4px_rgba(0,0,0,.25)]">
        <path d="M1 1 L1 16 L5.5 12 L8.5 19 L11 18 L8 11 L14 11 Z" fill="#2f6b4f" stroke="#fff" strokeWidth="1.4" strokeLinejoin="round" />
      </motion.svg>
      <AnimatePresence>
        {clicking && <motion.span initial={{ scale: 0.3, opacity: 0.6 }} animate={{ scale: 1.8, opacity: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.35 }} className="absolute -left-2 -top-2 h-6 w-6 rounded-full border-2 border-accent" />}
      </AnimatePresence>
      {label && (
        <span className="absolute left-4 top-4 whitespace-nowrap rounded-md bg-accent px-2 py-0.5 font-sans text-[11.5px] text-white shadow-[0_2px_8px_rgba(47,107,79,.35)]">{label}</span>
      )}
    </motion.div>
  )
}
