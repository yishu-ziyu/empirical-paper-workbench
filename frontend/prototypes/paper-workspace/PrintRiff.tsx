import { useEffect, useRef, useState, type ReactNode } from 'react'
import './riffs.css'
import { FIRST_STAGE, IV, OLS, ci, fmt, stars, type Run } from './data'
import { useFollow, usePaper, useTicker, type BlockId, type Paper } from './usePaper'

// Riff · 排印纸面 — bunsen#stage: the draft is a Letter sheet on the desk, typeset in two columns.
// Reviewer notes live outside the sheet as marginalia; provenance arrives as a slip in the margin.

const SHEET = 'relative mx-auto w-[860px] border border-ink bg-[#fffdf9] px-16 pb-16 pt-14 text-[#111]'
const SERIF = { fontFamily: '"Times New Roman", "Noto Serif SC", "Songti SC", Times, serif' }
const MONO = 'font-mono text-[11px] tracking-[.02em]'

type Slip = { run: Run; label: string; y: number; key: number }

export default function PrintRiff() {
  const p = usePaper({ bootStep: 380 })
  const [slip, setSlip] = useState<Slip | null>(null)
  const deskRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!p.diff) return
      const t = e.target as HTMLElement
      if (/^(INPUT|TEXTAREA)$/.test(t.tagName)) return
      if (e.key === 'Enter') p.acceptDiff()
      if (e.key === 'Escape') p.rejectDiff()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [p])

  const openSlip = (run: Run, label: string, el: HTMLElement) => {
    const desk = deskRef.current!.getBoundingClientRect()
    const r = el.getBoundingClientRect()
    setSlip({ run, label, y: r.top - desk.top - 8, key: Date.now() })
  }

  return (
    <div className="min-h-screen bg-paper text-ink" onClick={() => setSlip(null)}>
      {/* hudbar (bunsen): ink hairline, mono controls */}
      <header className="sticky top-0 z-30 flex h-11 items-center gap-4 border-b border-ink bg-paper px-6">
        <span className="italic" style={SERIF}>econpaper</span>
        <span className={`${MONO} text-muted`}>教育的工资回报 · 第 3 稿 · 3,010 obs</span>
        <div className="ml-auto flex items-center gap-2">
          <span className={`${MONO} text-muted`}>主设定</span>
          {(['OLS', 'IV'] as const).map((m) => (
            <button
              key={m}
              onClick={() => p.switchMain(m)}
              disabled={p.busy}
              className={`${MONO} border border-ink px-2.5 py-1 transition-colors duration-150 disabled:cursor-not-allowed ${
                p.main === m ? 'bg-ink text-[#fffdf7]' : 'bg-transparent text-muted hover:bg-ink/5'
              }`}
            >
              {m}
            </button>
          ))}
          <span className={`${MONO} ml-3 text-muted`}>审稿 {p.openNotes}/3</span>
        </div>
      </header>

      <div ref={deskRef} className="relative mx-auto flex max-w-[1320px] justify-center gap-10 px-8 pb-48 pt-12">
        <article className={SHEET} style={SERIF}>
          <p className={`absolute left-16 right-16 top-6 text-center ${MONO} uppercase tracking-[.18em] text-[#555]`}>
            Education and Earnings · Working Draft
          </p>
          <Mast />
          <div className="mt-8 columns-2 gap-9 text-[14.5px] leading-[1.72] [text-align:justify]">
            <Section p={p} id="intro" title="1　引言" marker={1}>
              <Proof p={p} id="intro">
                <p>
                  教育能在多大程度上提高收入，是劳动经济学最基本的问题之一。{p.introText}本文使用 Card (1995) 的数据，先给出 OLS 基准，再以大学邻近性作为工具变量。
                </p>
              </Proof>
            </Section>

            <Section p={p} id="data" title="2　数据">
              <p className="indent-[2em]">
                样本来自 1966 年启动的全国青年男性追踪调查（NLS），使用 1976 年的工资与教育信息，共{' '}
                <Num run={OLS} label="n" value={OLS.n} digits={0} onOpen={openSlip} active={p.isBooted('data')} />{' '}
                个观测。被解释变量是小时工资的对数。
              </p>
            </Section>

            <Section p={p} id="strategy" title="3　实证策略" marker={2}>
              <p className="indent-[2em]">基准模型为</p>
              <p className="my-2 text-center italic">
                ln <i>w</i><sub>i</sub> = α + β·educ<sub>i</sub> + <b>X</b><sub>i</sub>′γ + ε<sub>i</sub>
              </p>
              <p className="indent-[2em]">OLS 可能因能力等遗漏变量而有偏，因此以“是否在四年制大学附近长大”作为教育的工具变量。</p>
              <Proof p={p} id="strategy">{p.strategyExtra && <p className="indent-[2em]">{p.strategyExtra}</p>}</Proof>
            </Section>

            <Section p={p} id="table" title="4　结果" marker={3}>
              <Table p={p} onOpen={openSlip} />
            </Section>

            <Section p={p} id="results">
              <Proof p={p} id="results">
                <p className="indent-[2em]">
                  {p.resultText}主估计为{' '}
                  <Num run={p.shownRun} label="β̂" value={p.shownRun.coef} stale={p.stale} onOpen={openSlip} active={p.isBooted('results')} />
                  ，标准误{' '}
                  <Num run={p.shownRun} label="SE" value={p.shownRun.se} stale={p.stale} onOpen={openSlip} active={p.isBooted('results')} />。
                </p>
              </Proof>
            </Section>

            <Section p={p} id="figure">
              <Figure p={p} />
            </Section>

            <Section p={p} id="discussion" title="5　结论">
              <p className="indent-[2em] text-[#777]">（待写。可在下方交代 agent 起草。）</p>
            </Section>
          </div>
          <p className={`absolute bottom-6 left-0 right-0 text-center ${MONO} text-[#555]`}>— 1 —</p>
        </article>

        {/* marginalia */}
        <aside className="relative w-[250px] shrink-0 pt-44" style={SERIF}>
          <div className="space-y-7">
            {p.notes.map((n) => (
              <div
                key={n.id}
                onMouseEnter={() => p.setFocusBlock(n.block)}
                onMouseLeave={() => p.setFocusBlock(null)}
                className={`rf-rise text-[13.5px] leading-[1.6] transition-opacity duration-200 ${n.status === 'resolved' ? 'opacity-40' : ''}`}
                style={{ animationDelay: `${1.6 + n.id * 0.18}s` }}
              >
                <p className="italic">
                  <sup className="mr-1 not-italic text-accent">{n.id}</sup>
                  {n.text}
                </p>
                {n.status === 'open' ? (
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      p.fixNote(n)
                    }}
                    disabled={p.busy}
                    className={`${MONO} mt-1.5 text-accent underline decoration-accent/40 underline-offset-4 hover:decoration-accent disabled:text-muted disabled:no-underline`}
                  >
                    {n.action} ⟶
                  </button>
                ) : (
                  <p className={`${MONO} mt-1.5 text-accent`}>✓ 已改</p>
                )}
              </div>
            ))}
          </div>
          {p.working && (
            <p className={`rf-rise mt-10 ${MONO} text-accent`}>
              agent · {p.working.label}
              <span className="rf-caret">▍</span>
            </p>
          )}
        </aside>

        {slip && <SlipNote slip={slip} />}
      </div>

      <CommandLine p={p} />
    </div>
  )
}

function Mast() {
  return (
    <header className="rf-set text-center">
      <h1 className="text-[27px] font-normal leading-tight tracking-[-.01em]">教育的工资回报：来自大学邻近性的证据</h1>
      <p className="mt-2 text-[13px] italic text-[#444]">工作稿 · 数据 NLS Young Men 1976（Card, 1995）</p>
      <p className="mx-auto mt-5 max-w-[600px] text-left text-[13px] leading-[1.7] text-[#333]">
        <b className="mr-1 not-italic">摘要</b>
        本文估计受教育年限对小时工资的影响。OLS 基准约为 7.5%；以大学邻近性为工具的 IV 估计更大，但精度较低。
      </p>
    </header>
  )
}

function Section({ p, id, title, marker, children }: { p: Paper; id: BlockId; title?: string; marker?: number; children: ReactNode }) {
  const ref = useRef<HTMLElement>(null)
  const working = p.working?.block === id
  useFollow(ref, working || p.diff?.block === id)
  if (!p.isBooted(id)) return null
  const focused = p.focusBlock === id
  return (
    <section ref={ref} className={`rf-set relative mb-4 break-inside-avoid`}>
      {title && (
        <h2 className="mb-1 text-[14.5px] font-bold">
          {title}
          {marker && <sup className="ml-1 font-normal text-accent">{marker}</sup>}
        </h2>
      )}
      {working && <div className="rf-sweep mb-1 h-px text-accent" />}
      <div className={`transition-[box-shadow] duration-200 ${focused ? 'shadow-[inset_2px_0_0_#2f6b4f] pl-2' : ''}`}>{children}</div>
    </section>
  )
}

/** Proofreading marks: strike the old, insert the new in green ink. */
function Proof({ p, id, children }: { p: Paper; id: BlockId; children: ReactNode }) {
  const d = p.diff?.block === id ? p.diff : null
  if (!d) return <>{children}</>
  return (
    <div>
      {d.before && (
        <p className="rf-ink indent-[2em] text-[#9b3d30] line-through decoration-[#9b3d30]/70">
          {d.before}
        </p>
      )}
      <p className="rf-ink mt-1 indent-[2em] italic text-accent" style={{ animationDelay: '.35s' }}>
        <span className="-ml-4 mr-1 not-italic">‸</span>
        {d.after}
      </p>
      <p className="rf-ink mt-2 flex gap-3 font-mono text-[11px] not-italic" style={{ animationDelay: '.5s' }}>
        <span className="text-muted">{d.reason}</span>
        <button onClick={p.acceptDiff} className="text-accent underline underline-offset-4">接受 ⏎</button>
        <button onClick={p.rejectDiff} className="text-muted underline underline-offset-4">不要 ⎋</button>
      </p>
    </div>
  )
}

function Num({ run, label, value, digits = 4, stale, onOpen, active = true }: { run: Run; label: string; value: number; digits?: number; stale?: boolean; onOpen: (r: Run, l: string, el: HTMLElement) => void; active?: boolean }) {
  const shown = useTicker(value, { active })
  return (
    <button
      onClick={(e) => {
        e.stopPropagation()
        onOpen(run, label, e.currentTarget)
      }}
      title={stale ? '设定已改，这个数字待更新' : '看来源'}
      className={`rf-tnum border-b border-dotted transition-colors duration-150 ${stale ? 'border-[#9b3d30] text-[#9b3d30]' : 'border-accent/60 hover:text-accent'}`}
    >
      {digits ? shown.toFixed(digits) : Math.round(shown).toLocaleString()}
    </button>
  )
}

function Table({ p, onOpen }: { p: Paper; onOpen: (r: Run, l: string, el: HTMLElement) => void }) {
  const rev = p.revision.table ?? 0
  const running = p.rerun === 'table'
  const Rule = ({ w, delay }: { w: string; delay: number }) => (
    <div key={`${rev}-${delay}`} className="rf-draw-x bg-[#111]" style={{ height: w, animationDelay: `${delay}s` }} />
  )
  const cell = (r: Run) => (
    <td className={`py-1 text-right ${p.main === r.method ? 'text-accent' : ''}`}>
      <Num run={r} label="β̂" value={r.coef} onOpen={onOpen} />
      <sup>{stars(r.p)}</sup>
      <div className="rf-tnum text-[12px] text-[#555]">({fmt(r.se)})</div>
    </td>
  )
  return (
    <figure className={`group relative my-2 text-[13px] transition-opacity duration-200 ${running ? 'opacity-40' : ''}`}>
      <figcaption className="mb-1.5 text-center text-[12.5px]">表 1　教育对小时工资对数的影响</figcaption>
      <Rule w="1.2px" delay={0} />
      <table className="w-full">
        <thead>
          <tr>
            <th />
            <th className="py-1 text-right font-normal">(1) OLS</th>
            <th className="py-1 text-right font-normal">(2) IV</th>
          </tr>
        </thead>
      </table>
      <Rule w="0.6px" delay={0.15} />
      <table className="w-full">
        <tbody>
          <tr>
            <td className="py-1">受教育年限</td>
            {cell(OLS)}
            {cell(IV)}
          </tr>
          <tr className="text-[#555]">
            <td className="py-0.5">第一阶段 F</td>
            <td className="text-right">—</td>
            <td className="rf-tnum text-right">{FIRST_STAGE.f}</td>
          </tr>
          <tr className="text-[#555]">
            <td className="py-0.5">N</td>
            <td className="rf-tnum text-right">3,010</td>
            <td className="rf-tnum text-right">3,010</td>
          </tr>
        </tbody>
      </table>
      <Rule w="1.2px" delay={0.3} />
      <p className="mt-1.5 text-[11.5px] leading-[1.5] text-[#555]">
        注：括号内为标准误，OLS 为 HC1 稳健标准误。*** p&lt;0.01，** p&lt;0.05。主设定以绿色标出。
        {p.tableNote && <span className="rf-ink"> 第一阶段有效 F = {FIRST_STAGE.fEff}，介于 10 与 23.1 之间，IV 的 t 检验可能过度拒绝。</span>}
      </p>
      <button
        onClick={(e) => {
          e.stopPropagation()
          p.doRerun('table')
        }}
        className={`absolute -right-[76px] top-6 font-mono text-[11px] text-muted opacity-0 transition-opacity duration-150 hover:text-ink group-hover:opacity-100`}
      >
        ↻ 重跑
      </button>
    </figure>
  )
}

function Figure({ p }: { p: Paper }) {
  const rev = p.revision.figure ?? 0
  const W = 360
  const x = (v: number) => 34 + (Math.max(0, v) / 0.26) * (W - 50)
  return (
    <figure className="my-2">
      <svg key={rev} viewBox={`0 0 ${W} 110`} className="w-full" style={{ fontFamily: 'ui-monospace, Menlo, monospace' }}>
        <line x1={x(0)} x2={x(0)} y1={8} y2={86} stroke="#111" strokeWidth={0.8} className="rf-stroke" style={{ ['--len' as string]: 80 }} />
        <line x1={x(0)} x2={x(0.26)} y1={86} y2={86} stroke="#111" strokeWidth={0.8} className="rf-stroke" style={{ ['--len' as string]: 320 }} />
        {[0, 0.1, 0.2].map((t) => (
          <text key={t} x={x(t)} y={100} fontSize={8.5} textAnchor="middle" fill="#555">{t.toFixed(1)}</text>
        ))}
        {[OLS, IV].map((r, i) => {
          const [lo, hi] = ci(r)
          const y = 30 + i * 32
          const on = p.main === r.method
          const len = x(hi) - x(lo)
          return (
            <g key={r.method}>
              <text x={4} y={y + 3} fontSize={9} fill={on ? '#2f6b4f' : '#111'}>{r.method}</text>
              <line x1={x(lo)} x2={x(hi)} y1={y} y2={y} stroke={on ? '#2f6b4f' : '#111'} strokeWidth={on ? 1.8 : 1} className="rf-stroke" style={{ ['--len' as string]: len, animationDelay: `${0.3 + i * 0.2}s` }} />
              <circle cx={x(r.coef)} cy={y} r={on ? 3.6 : 3} fill={on ? '#2f6b4f' : '#111'} className="rf-rise" style={{ animationDelay: `${0.9 + i * 0.2}s` }} />
            </g>
          )
        })}
      </svg>
      <figcaption className="mt-1 text-[12px] leading-[1.5]">
        图 1　两种估计的点估计与 95% 置信区间：IV 高于 OLS，但区间宽得多，下限接近 0.02。
      </figcaption>
    </figure>
  )
}

function SlipNote({ slip }: { slip: Slip }) {
  const { run, label, y } = slip
  return (
    <div key={slip.key} className="pointer-events-none absolute left-1/2 z-20 ml-[430px] w-[260px]" style={{ top: y }} onClick={(e) => e.stopPropagation()}>
      <div className="rf-draw-x absolute -left-10 top-4 h-px w-10 bg-accent" />
      <div className="rf-ink pointer-events-auto border border-ink bg-[#fffdf9] p-3" style={{ animationDelay: '.25s' }}>
        <p className="font-mono text-[10.5px] uppercase tracking-[.12em] text-muted">来源 · {label}</p>
        <p className="mt-1 text-[13px]" style={SERIF}>{run.label}</p>
        <p className="mt-1 font-mono text-[10.5px] leading-[1.6] text-[#444]">
          {run.id} · {run.ranAt}
          <br />
          {run.cov} · n = {run.n.toLocaleString()}
        </p>
        <pre className="mt-2 overflow-x-auto bg-ink px-2 py-1.5 font-mono text-[10px] leading-[1.5] text-[#f4efe4]">{run.code}</pre>
      </div>
    </div>
  )
}

function CommandLine({ p }: { p: Paper }) {
  const [text, setText] = useState('')
  const ref = useRef<HTMLInputElement>(null)
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        ref.current?.focus()
      }
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [])
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        p.command(text)
        setText('')
      }}
      className="fixed bottom-[76px] left-1/2 z-30 flex w-[560px] -translate-x-1/2 items-center gap-2 border border-ink bg-paper px-3 py-2 font-mono text-[12px]"
      onClick={(e) => e.stopPropagation()}
    >
      <span className="text-accent">›</span>
      <input
        ref={ref}
        value={text}
        onChange={(e) => setText(e.target.value)}
        disabled={p.busy}
        placeholder={p.diff ? '先处理稿子上的校对（⏎ 接受 · ⎋ 不要）' : '交代 agent 改稿，例如：把结果段写短一点　⌘K'}
        className="flex-1 bg-transparent outline-none placeholder:text-muted/70"
      />
    </form>
  )
}
