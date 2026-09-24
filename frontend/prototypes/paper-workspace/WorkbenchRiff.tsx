import { useEffect, useRef, useState, type ReactNode } from 'react'
import './riffs.css'
import { FIRST_STAGE, IV, OLS, ci, fmt, stars, type Run } from './data'
import { useFollow, usePaper, useTicker, type BlockId, type Main, type Paper } from './usePaper'

// Riff · 工作台 — modelled on Claude Science: floating panes on a warm surface,
// the manuscript in the middle, a live notebook on the right that writes and runs
// the code while the paper updates. Numbers trace back to the line that made them.

const PANE = 'rounded-[14px] border border-black/[.07] bg-white shadow-[0_1px_2px_rgba(24,21,21,.04)]'
const SERIF = { fontFamily: '"Instrument Serif", "Noto Serif SC", "Songti SC", Georgia, serif' }
const BLUE = '#3b6fd8'

type Cell = { id: number; code: string; out: string[]; typed: number; status: 'typing' | 'running' | 'done'; source?: Main }
type Trace = { cell: number; line: number; n: number }

const CELLS: Omit<Cell, 'typed' | 'status'>[] = [
  { id: 1, code: 'import pandas as pd\nimport statspai\ndf = pd.read_csv("data_card1995.csv")\ndf.shape', out: ['(3010, 34)'] },
  {
    id: 2,
    code: `ols = ${OLS.code}`,
    out: [`educ   ${fmt(OLS.coef)}   (${fmt(OLS.se)})   ***   n=3010`],
    source: 'OLS',
  },
  {
    id: 3,
    code: `iv = ${IV.code}\nftest = statspai.effective_f_test(\n    df, endog="educ", instruments=["nearc4"],\n    exog=controls, vcov="HC1")`,
    out: [`first-stage F = ${FIRST_STAGE.f}   effective F = ${FIRST_STAGE.fEff}`, `educ   ${fmt(IV.coef)}   (${fmt(IV.se)})   **    n=3010`],
    source: 'IV',
  },
]

export default function WorkbenchRiff() {
  const p = usePaper({ bootStep: 400 })
  const [cells, setCells] = useState<Cell[]>([])
  const [trace, setTrace] = useState<Trace | null>(null)
  const [pin, setPin] = useState<number | null>(null)
  const [elapsed, setElapsed] = useState(0)
  const running = cells.some((c) => c.status !== 'done')
  const busy = p.busy || running

  // boot: the notebook writes and runs the first three cells while the paper typesets
  useEffect(() => {
    const t = [150, 750, 1450].map((ms, i) => window.setTimeout(() => addCell(CELLS[i]), ms))
    return () => t.forEach(clearTimeout)
  }, [])

  // typing + running loop for the newest unfinished cell
  useEffect(() => {
    const live = cells.find((c) => c.status !== 'done')
    if (!live) return
    const id = window.setTimeout(() => {
      setCells((cs) =>
        cs.map((c) => {
          if (c.id !== live.id) return c
          if (c.status === 'typing') return c.typed >= c.code.length ? { ...c, status: 'running' } : { ...c, typed: c.typed + 4 }
          return { ...c, status: 'done' }
        }),
      )
    }, live.status === 'typing' ? 16 : 420)
    return () => clearTimeout(id)
  }, [cells])

  useEffect(() => {
    if (!busy) return setElapsed(0)
    const t0 = Date.now()
    const id = window.setInterval(() => setElapsed((Date.now() - t0) / 1000), 100)
    return () => clearInterval(id)
  }, [busy])

  function addCell(c: Omit<Cell, 'typed' | 'status'>) {
    setCells((cs) => [...cs, { ...c, typed: 0, status: 'typing' }])
  }

  function switchMain(next: Main) {
    if (busy || next === p.main) return
    const id = cells.length + 1
    addCell({
      id,
      code: `main = ${next.toLowerCase()}   # 主设定改为 ${next}\npaper.rebind(main)`,
      out: ['3 处引用依赖主设定 → 结果段、表 1、图 1', '已标记待更新，正在起草修改'],
    })
    const wait = 16 * 16 + 420 + 150
    window.setTimeout(() => p.switchMain(next), wait)
  }

  function traceRun(run: Run) {
    const cell = run.method === 'OLS' ? 2 : 3
    setTrace({ cell, line: 0, n: Date.now() })
  }

  const statusText = running ? `正在运行 cell [${cells.find((c) => c.status !== 'done')?.id}]` : p.working ? `agent · ${p.working.label}` : null

  return (
    <div className="flex h-screen gap-2.5 bg-[#f4f2ec] p-2.5 text-ink" onClick={() => setPin(null)}>
      {/* sessions */}
      <aside className={`${PANE} flex w-[216px] shrink-0 flex-col p-3 text-[13px]`}>
        <div className="px-1.5 pb-3">
          <p className="text-[22px] leading-none" style={SERIF}>econpaper</p>
          <p className="mt-1 text-[11px] text-muted">工作稿</p>
        </div>
        <button className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-left text-muted hover:bg-black/[.04]">
          <span className="text-[12px]">▤</span> 文件
        </button>
        <p className="mt-4 px-2 text-[11px] text-muted">今天</p>
        {['教育回报 · 稿子', '教育回报 · 审稿', '设定对比', '数据清洗记录'].map((s, i) => (
          <button key={s} className={`mt-0.5 flex items-center gap-2 rounded-lg px-2 py-1.5 text-left ${i === 0 ? 'bg-black/[.05] text-ink' : 'text-ink/80 hover:bg-black/[.03]'}`}>
            <span className={`h-1.5 w-1.5 rounded-full ${i === 0 ? 'bg-accent' : 'bg-black/20'}`} />
            {s}
          </button>
        ))}
        <p className="mt-5 px-2 text-[11px] text-muted">大纲</p>
        {['引言', '数据', '实证策略', '结果', '结论'].map((s, i) => (
          <a key={s} href={`#wb-${i}`} className="mt-0.5 rounded-lg px-2 py-1 text-[12.5px] text-ink/70 hover:bg-black/[.03] hover:text-ink">
            {i + 1}　{s}
          </a>
        ))}
        <span className="mt-auto px-2 text-muted">⚙︎</span>
      </aside>

      {/* manuscript */}
      <main className={`${PANE} relative flex min-w-0 flex-1 flex-col overflow-hidden`}>
        <div className="flex h-11 shrink-0 items-center gap-3 border-b border-black/[.06] px-4 text-[12.5px]">
          <span className="font-medium">manuscript.md</span>
          <span className="text-muted">v3</span>
          <div className="ml-auto flex items-center gap-2">
            <span className="text-muted">主设定</span>
            <Segmented value={p.main} onChange={switchMain} disabled={busy} />
            <span className="ml-2 rounded-full bg-black/[.04] px-2 py-0.5 text-[11.5px] text-muted">审稿 {p.openNotes}</span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          <article className="mx-auto max-w-[640px] px-10 pb-40 pt-10 text-[16px] leading-[1.9] [font-family:'Noto_Serif_SC','Songti_SC',serif]">
            <h1 className="rf-set text-[34px] leading-[1.15] tracking-[-.01em]" style={SERIF}>
              教育的工资回报：来自大学邻近性的证据
            </h1>
            <p className="rf-rise mt-2 font-sans text-[12.5px] text-muted" style={{ animationDelay: '.2s' }}>
              NLS Young Men 1976 · 3,010 人 · 3 个 cell 支撑本文数字
            </p>

            <Block p={p} id="intro" idx={0} title="引言" note={1} pin={pin} setPin={setPin} busy={busy}>
              <p>教育能在多大程度上提高收入，是劳动经济学最基本的问题之一。{p.introText}本文先给出 OLS 基准，再以大学邻近性作为工具变量。</p>
            </Block>
            <Block p={p} id="data" idx={1} title="数据" pin={pin} setPin={setPin} busy={busy}>
              <p>
                样本来自全国青年男性追踪调查（NLS），使用 1976 年的工资与教育信息，共 <Num value={OLS.n} digits={0} onTrace={() => setTrace({ cell: 1, line: 2, n: Date.now() })} /> 个观测。
              </p>
            </Block>
            <Block p={p} id="strategy" idx={2} title="实证策略" note={2} pin={pin} setPin={setPin} busy={busy}>
              <p>OLS 可能因能力等遗漏变量而有偏，因此以“是否在四年制大学附近长大”（nearc4）作为教育的工具变量。</p>
              {p.strategyExtra && <p className="mt-3">{p.strategyExtra}</p>}
            </Block>
            <Block p={p} id="table" idx={3} title="结果" note={3} pin={pin} setPin={setPin} busy={busy}>
              <ResultTable p={p} onTrace={traceRun} />
            </Block>
            <Block p={p} id="results" pin={pin} setPin={setPin} busy={busy}>
              <p>
                {p.resultText}
                <span className="ml-1 font-sans text-[12.5px] text-muted">
                  β̂ = <Num value={p.shownRun.coef} stale={p.stale} onTrace={() => traceRun(p.shownRun)} />，SE ={' '}
                  <Num value={p.shownRun.se} stale={p.stale} onTrace={() => traceRun(p.shownRun)} />
                </span>
              </p>
            </Block>
            <Block p={p} id="figure" pin={pin} setPin={setPin} busy={busy}>
              <CoefPlot p={p} />
            </Block>
            <Block p={p} id="discussion" idx={4} title="结论" pin={pin} setPin={setPin} busy={busy}>
              <p className="text-muted">还没写。</p>
            </Block>
          </article>
        </div>

        <Composer p={p} status={statusText} elapsed={elapsed} busy={busy} />
      </main>

      {/* live notebook */}
      <aside className={`${PANE} flex w-[440px] shrink-0 flex-col overflow-hidden`}>
        <div className="flex h-11 shrink-0 items-center gap-2 border-b border-black/[.06] px-4 text-[12.5px]">
          <span className="font-medium">analysis.ipynb</span>
          <span className="rounded bg-black/[.04] px-1.5 text-[11px] text-muted">{cells.length} cells</span>
          <span className="ml-auto text-[11.5px] text-muted">与稿子同步</span>
        </div>
        <Notebook cells={cells} trace={trace} />
        <div className="shrink-0 border-t border-black/[.06] bg-[#fafaf8] px-4 py-2.5 font-mono text-[11px] leading-5 text-muted">
          <p className="text-ink/70">Python — statspai kernel</p>
          <p>已连接 agent 的内核，变量与状态共享。输入表达式后回车。</p>
        </div>
      </aside>
    </div>
  )
}

function Segmented({ value, onChange, disabled }: { value: Main; onChange: (m: Main) => void; disabled: boolean }) {
  return (
    <div className="relative flex rounded-lg bg-black/[.05] p-0.5">
      <span
        className="absolute bottom-0.5 top-0.5 w-[calc(50%-2px)] rounded-md bg-white shadow-[0_1px_2px_rgba(0,0,0,.08)] transition-transform duration-200 [transition-timing-function:cubic-bezier(.23,1,.32,1)]"
        style={{ transform: value === 'IV' ? 'translateX(100%)' : 'none' }}
      />
      {(['OLS', 'IV'] as Main[]).map((m) => (
        <button
          key={m}
          disabled={disabled}
          onClick={() => onChange(m)}
          className={`relative w-12 py-0.5 text-[12px] transition-colors duration-150 disabled:cursor-not-allowed ${value === m ? 'text-ink' : 'text-muted'}`}
        >
          {m}
        </button>
      ))}
    </div>
  )
}

function Block(props: {
  p: Paper
  id: BlockId
  idx?: number
  title?: string
  note?: number
  pin: number | null
  setPin: (n: number | null) => void
  busy: boolean
  children: ReactNode
}) {
  const { p, id, idx, title, note, pin, setPin, busy, children } = props
  const ref = useRef<HTMLElement>(null)
  const d = p.diff?.block === id ? p.diff : null
  const working = p.working?.block === id
  useFollow(ref, working || !!d)
  if (!p.isBooted(id)) return null
  const n = note ? p.notes.find((x) => x.id === note) : null
  return (
    <section ref={ref} id={idx !== undefined ? `wb-${idx}` : undefined} className="rf-set relative mt-7 scroll-mt-4">
      {title && <h2 className="mb-2 text-[22px] leading-tight" style={SERIF}>{title}</h2>}
      <div className={`relative rounded-lg transition-[background-color] duration-300 ${p.focusBlock === id || working ? 'bg-[#3b6fd8]/[.05]' : ''}`}>
        {working && <div className="rf-sweep absolute -top-1.5 left-0 right-0 h-[2px] rounded text-[#3b6fd8]" />}
        {d ? (
          <div>
            {d.before && <p className="text-muted"><span className="rf-strike">{d.before}</span></p>}
            <p className="rf-ink mt-1 rounded-md bg-accent/[.07] px-2 py-1 text-ink" style={{ animationDelay: '.3s' }}>{d.after}</p>
            <div className="rf-ink mt-2 flex items-center gap-2 font-sans text-[12px]" style={{ animationDelay: '.45s' }}>
              <span className="text-muted">{d.reason}</span>
              <button onClick={p.acceptDiff} className="ml-auto rounded-md bg-ink px-2.5 py-1 text-white active:scale-[.97]">接受</button>
              <button onClick={p.rejectDiff} className="rounded-md px-2.5 py-1 text-muted hover:bg-black/[.04] active:scale-[.97]">不要</button>
            </div>
          </div>
        ) : (
          children
        )}
      </div>

      {/* reviewer pin, the way Claude Science anchors a comment on a figure */}
      {n && (
        <div className="absolute -right-8 top-1" onClick={(e) => e.stopPropagation()}>
          <button
            onClick={() => setPin(pin === n.id ? null : n.id)}
            onMouseEnter={() => p.setFocusBlock(id)}
            onMouseLeave={() => p.setFocusBlock(null)}
            className={`pp-pop grid h-5 w-5 place-items-center rounded-full font-sans text-[10.5px] text-white shadow-[0_0_0_3px_rgba(59,111,216,.15)] transition-transform duration-150 hover:scale-110 ${n.status === 'resolved' ? 'bg-accent' : ''}`}
            style={{ background: n.status === 'resolved' ? undefined : BLUE, animationDelay: '.5s' }}
          >
            {n.status === 'resolved' ? '✓' : n.id}
          </button>
          {pin === n.id && (
            <div className="pp-pop absolute right-0 top-7 z-20 w-[260px] origin-top-right rounded-xl border border-black/[.08] bg-white p-3 font-sans text-[12.5px] leading-5 shadow-[0_8px_28px_rgba(24,21,21,.12)]">
              <p className="mb-1 flex items-center gap-1.5 text-[11px] text-muted">
                <span className="h-1.5 w-1.5 rounded-full" style={{ background: BLUE }} /> 审稿 · {n.tag}
              </p>
              <p>{n.text}</p>
              {n.status === 'open' ? (
                <button
                  disabled={busy}
                  onClick={() => {
                    setPin(null)
                    p.fixNote(n)
                  }}
                  className="mt-2 float-right rounded-md bg-ink px-2.5 py-1 text-[11.5px] text-white active:scale-[.97] disabled:opacity-40"
                >
                  {n.action}
                </button>
              ) : (
                <p className="mt-2 text-accent">已处理</p>
              )}
            </div>
          )}
        </div>
      )}
    </section>
  )
}

function Num({ value, digits = 4, stale, onTrace }: { value: number; digits?: number; stale?: boolean; onTrace: () => void }) {
  const v = useTicker(value)
  return (
    <button
      onClick={(e) => {
        e.stopPropagation()
        onTrace()
      }}
      title={stale ? '主设定已改，待更新' : '在 notebook 里找到它'}
      className={`rf-tnum rounded px-0.5 font-mono text-[.9em] transition-colors duration-150 ${
        stale ? 'text-warning line-through decoration-warning/50' : 'text-ink underline decoration-[#3b6fd8]/40 decoration-dotted underline-offset-4 hover:bg-[#3b6fd8]/[.08]'
      }`}
    >
      {digits ? v.toFixed(digits) : Math.round(v).toLocaleString()}
    </button>
  )
}

function ResultTable({ p, onTrace }: { p: Paper; onTrace: (r: Run) => void }) {
  const rev = p.revision.table ?? 0
  return (
    <div className={`my-1 rounded-xl border border-black/[.07] bg-[#fcfcfa] px-5 py-4 font-sans text-[13px] transition-opacity duration-200 ${p.rerun === 'table' ? 'opacity-40' : ''}`}>
      <p className="mb-2 text-[12px] text-muted">表 1 · 教育对小时工资对数的影响</p>
      <div key={`a${rev}`} className="rf-draw-x h-px bg-ink/70" />
      <div className="grid grid-cols-[1fr_110px_110px] py-1.5 text-muted">
        <span />
        {[OLS, IV].map((r) => (
          <span key={r.method} className={`text-right transition-colors duration-300 ${p.main === r.method ? 'font-medium text-ink' : ''}`}>
            {r.method}
            {p.main === r.method && <span className="ml-1 rounded bg-accent/10 px-1 text-[10px] text-accent">主</span>}
          </span>
        ))}
      </div>
      <div key={`b${rev}`} className="rf-draw-x h-px bg-ink/25" style={{ animationDelay: '.12s' }} />
      <div className="grid grid-cols-[1fr_110px_110px] items-start py-2">
        <span>受教育年限</span>
        {[OLS, IV].map((r) => (
          <span key={r.method} className="text-right">
            <Num value={r.coef} onTrace={() => onTrace(r)} />
            <sup className="text-muted">{stars(r.p)}</sup>
            <span className="block font-mono text-[11.5px] text-muted">({fmt(r.se)})</span>
          </span>
        ))}
      </div>
      <div className="grid grid-cols-[1fr_110px_110px] py-1 text-muted">
        <span>第一阶段 F</span>
        <span className="text-right">—</span>
        <span className="rf-tnum text-right font-mono">{FIRST_STAGE.f}</span>
      </div>
      <div key={`c${rev}`} className="rf-draw-x h-px bg-ink/70" style={{ animationDelay: '.24s' }} />
      <p className="mt-2 text-[11.5px] leading-5 text-muted">
        括号内为标准误；OLS 为 HC1 稳健标准误。N = 3,010。
        {p.tableNote && <span className="rf-ink text-ink"> 第一阶段有效 F = {FIRST_STAGE.fEff}，介于 10 与 23.1 之间，IV 推断需谨慎。</span>}
      </p>
    </div>
  )
}

function CoefPlot({ p }: { p: Paper }) {
  const rev = p.revision.figure ?? 0
  const W = 560
  const x = (v: number) => 48 + (Math.max(0, v) / 0.26) * (W - 70)
  return (
    <figure className="my-1 rounded-xl border border-black/[.07] bg-[#fcfcfa] px-5 pb-3 pt-4 font-sans">
      <svg key={rev} viewBox={`0 0 ${W} 120`} className="w-full">
        {[0, 0.05, 0.1, 0.15, 0.2, 0.25].map((t) => (
          <g key={t}>
            <line x1={x(t)} x2={x(t)} y1={10} y2={92} stroke="rgba(24,21,21,.08)" />
            <text x={x(t)} y={110} fontSize={10} textAnchor="middle" fill="#8a857c">{t.toFixed(2)}</text>
          </g>
        ))}
        {[OLS, IV].map((r, i) => {
          const [lo, hi] = ci(r)
          const y = 34 + i * 36
          const on = p.main === r.method
          const color = on ? '#2f6b4f' : '#9a958c'
          return (
            <g key={r.method}>
              <text x={6} y={y + 4} fontSize={11} fill={on ? '#181515' : '#8a857c'}>{r.method}</text>
              <line x1={x(lo)} x2={x(hi)} y1={y} y2={y} stroke={color} strokeWidth={on ? 3 : 2} strokeLinecap="round" className="rf-stroke" style={{ ['--len' as string]: x(hi) - x(lo), animationDelay: `${0.15 + i * 0.18}s` }} />
              <circle cx={x(r.coef)} cy={y} r={on ? 5.5 : 4.5} fill="#fff" stroke={color} strokeWidth={2.5} className="pp-pop" style={{ animationDelay: `${0.7 + i * 0.18}s`, transformOrigin: `${x(r.coef)}px ${y}px` }} />
            </g>
          )
        })}
      </svg>
      <figcaption className="text-[12px] text-muted">图 1 · 点估计与 95% 置信区间。主设定以绿色标出。</figcaption>
    </figure>
  )
}

function Notebook({ cells, trace }: { cells: Cell[]; trace: Trace | null }) {
  const refs = useRef<Record<number, HTMLDivElement | null>>({})
  const endRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (trace) refs.current[trace.cell]?.scrollIntoView({ block: 'center', behavior: 'smooth' })
  }, [trace])
  useEffect(() => {
    if (!trace) endRef.current?.scrollIntoView({ block: 'end', behavior: 'smooth' })
  }, [cells.length, trace])
  let lineNo = 0
  return (
    <div className="flex-1 space-y-3 overflow-y-auto bg-[#fafaf8] p-3">
      {cells.map((c) => {
        const text = c.code.slice(0, c.typed)
        const lines = text.split('\n')
        const traced = trace?.cell === c.id
        return (
          <div
            key={`${c.id}-${traced ? trace?.n : ''}`}
            ref={(el) => {
              refs.current[c.id] = el
            }}
            className={`rf-rise overflow-hidden rounded-xl border bg-white transition-shadow duration-300 ${traced ? 'border-[#3b6fd8]/50 shadow-[0_0_0_4px_rgba(59,111,216,.12)]' : 'border-black/[.07]'}`}
          >
            <div className="flex items-center gap-2 border-b border-black/[.05] px-3 py-1.5 font-mono text-[10.5px] text-muted">
              <span>[{c.id}]</span>
              {c.status === 'done' ? <span className="text-accent">✓</span> : <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-[#3b6fd8]" />}
              <span>{c.status === 'typing' ? 'agent 正在写' : c.status === 'running' ? '运行中…' : '完成'}</span>
            </div>
            <pre className="overflow-x-auto px-0 py-2 font-mono text-[11.5px] leading-[1.7]">
              {lines.map((l, i) => {
                lineNo += 1
                return (
                  <div key={i} className="flex">
                    <span className="w-9 shrink-0 select-none pr-3 text-right text-black/25">{lineNo}</span>
                    <Code line={l} />
                    {c.status === 'typing' && i === lines.length - 1 && <span className="rf-caret text-[#3b6fd8]">▍</span>}
                  </div>
                )
              })}
            </pre>
            {c.status === 'done' && (
              <div className="border-t border-black/[.05] px-3 py-2 font-mono text-[11.5px] leading-[1.7]">
                <p className="text-[10.5px] text-muted">⌄ output</p>
                {c.out.map((o, i) => (
                  <p key={o} className={`rf-rise ${traced ? 'rounded bg-[#3b6fd8]/[.08] px-1 text-ink' : 'text-ink/80'}`} style={{ animationDelay: `${i * 0.08}s` }}>
                    {o}
                  </p>
                ))}
              </div>
            )}
          </div>
        )
      })}
      <div ref={endRef} />
    </div>
  )
}

function Code({ line }: { line: string }) {
  // tiny highlighter: strings, comments, numbers, keywords
  const parts = line.split(/("[^"]*"?|#.*$|\b\d+(?:\.\d+)?\b|\b(?:import|as|for|in)\b)/g)
  return (
    <span className="whitespace-pre">
      {parts.map((s, i) =>
        !s ? null : s.startsWith('"') ? (
          <span key={i} className="text-[#1f6fb2]">{s}</span>
        ) : s.startsWith('#') ? (
          <span key={i} className="text-[#9a958c]">{s}</span>
        ) : /^\d/.test(s) ? (
          <span key={i} className="text-[#b35a1f]">{s}</span>
        ) : /^(import|as|for|in)$/.test(s) ? (
          <span key={i} className="text-[#8a4bd6]">{s}</span>
        ) : (
          <span key={i}>{s}</span>
        ),
      )}
    </span>
  )
}

function Composer({ p, status, elapsed, busy }: { p: Paper; status: string | null; elapsed: number; busy: boolean }) {
  const [text, setText] = useState('')
  return (
    <div className="absolute bottom-[66px] left-1/2 w-[min(620px,calc(100%-32px))] -translate-x-1/2">
      {status && (
        <div className="rf-rise mx-3 flex items-center gap-2 rounded-t-xl border border-b-0 border-black/[.07] bg-[#f4f2ec] px-3 py-1.5 font-sans text-[11.5px] text-muted">
          <span className="inline-block h-3 w-3 animate-spin rounded-full border-[1.5px] border-[#3b6fd8] border-t-transparent" />
          {status}
          <span className="rf-tnum ml-auto font-mono">{elapsed.toFixed(1)}s</span>
        </div>
      )}
      <form
        onSubmit={(e) => {
          e.preventDefault()
          p.command(text)
          setText('')
        }}
        className="rounded-2xl border border-black/[.09] bg-white p-3 shadow-[0_6px_24px_rgba(24,21,21,.08)]"
      >
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={busy}
          placeholder={p.diff ? '先处理稿子里的修改' : '让 agent 改稿、换设定、补一个稳健性检验…'}
          className="w-full bg-transparent font-sans text-[14px] outline-none placeholder:text-muted/70"
        />
        <div className="mt-2 flex items-center gap-3 font-sans text-[13px] text-muted">
          <span>＋</span>
          <span>⌘</span>
          <button type="submit" disabled={busy || !text.trim()} className="ml-auto grid h-7 w-7 place-items-center rounded-lg bg-accent text-white transition-transform duration-100 active:scale-[.94] disabled:opacity-35">
            ↑
          </button>
        </div>
      </form>
    </div>
  )
}
