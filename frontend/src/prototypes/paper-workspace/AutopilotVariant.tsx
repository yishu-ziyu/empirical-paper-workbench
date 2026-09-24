import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { EXTRA_SPECS, FIRST_STAGE, IV, OLS, ci, fmt, pct, stars, type Run } from './data'

type Phase = 'brief' | 'running' | 'review'
type Finding = { id: string; title: string; body: string; runs: string[]; paragraph: string }

const SPECS: Run[] = [OLS, IV, ...EXTRA_SPECS]
const BUDGETS = [5, 10, 30]
const SCOPES = [
  { id: 'ols', label: '跑 OLS 基准', on: true },
  { id: 'iv', label: '找工具变量，做 IV', on: true },
  { id: 'controls', label: '换控制变量组合', on: true },
  { id: 'sub', label: '子样本检验', on: true },
  { id: 'write', label: '直接改稿子', on: false },
]

// Each log line appears at `at` (fraction of the budget). Simulated: 10 minutes play in ~8 seconds.
const LOG: { at: number; text: string; run?: string }[] = [
  { at: 0.03, text: '读取 card1995.csv · 3,010 行 × 34 列' },
  { at: 0.12, text: `OLS 基准 · β = ${fmt(OLS.coef)}（SE ${fmt(OLS.se)}）`, run: OLS.id },
  { at: 0.26, text: '检查候选工具：nearc4、nearc2 的第一阶段' },
  { at: 0.38, text: `IV · nearc4 · β = ${fmt(IV.coef)}，第一阶段 F = ${FIRST_STAGE.f}`, run: IV.id },
  { at: 0.52, text: `去掉地区虚拟变量 · β = ${fmt(EXTRA_SPECS[0].coef)}`, run: 'spec-3' },
  { at: 0.66, text: `仅南方样本 · β = ${fmt(EXTRA_SPECS[1].coef)}（n = 1,215）`, run: 'spec-4' },
  { at: 0.78, text: `IV · nearc2 · β = ${fmt(EXTRA_SPECS[2].coef)}，工具偏弱`, run: 'spec-5' },
  { at: 0.9, text: '整理对比表和发现' },
]

const FINDINGS: Finding[] = [
  {
    id: 'f1',
    title: 'OLS 估计很稳',
    body: '三种 OLS 设定都落在 0.071–0.075 之间，换控制变量、只看南方样本都没有明显变化。',
    runs: [OLS.id, 'spec-3', 'spec-4'],
    paragraph: '在不同控制变量组合和南方子样本中，OLS 估计稳定在 0.071 至 0.075 之间（表 2）。',
  },
  {
    id: 'f2',
    title: 'IV 更大，但精度低',
    body: `nearc4 作工具时 β = ${fmt(IV.coef)}，约为 OLS 的 1.8 倍；95% 置信区间 [${fmt(ci(IV)[0], 3)}, ${fmt(ci(IV)[1], 3)}] 很宽。第一阶段 F = ${FIRST_STAGE.f}，工具强度中等。`,
    runs: [IV.id],
    paragraph: `以大学邻近性为工具的 IV 估计为 ${fmt(IV.coef, 3)}，高于 OLS，但置信区间较宽；第一阶段 F 为 ${FIRST_STAGE.f}，工具强度中等，推断需谨慎。`,
  },
  {
    id: 'f3',
    title: 'nearc2 不适合作工具',
    body: '两年制大学邻近性的第一阶段很弱，估计值不稳定。建议正文不用，放附录说明试过。',
    runs: ['spec-5'],
    paragraph: '我们也尝试以两年制大学邻近性为工具，但其第一阶段较弱，结果列于附录。',
  },
]

export default function AutopilotVariant() {
  const [phase, setPhase] = useState<Phase>('brief')
  const [goal, setGoal] = useState('估计教育对工资的回报，看结论在不同设定下稳不稳，并判断 OLS 是否低估。')
  const [scopes, setScopes] = useState(SCOPES)
  const [budget, setBudget] = useState(10)
  const [progress, setProgress] = useState(0)
  const [stopped, setStopped] = useState(false)

  useEffect(() => {
    if (phase !== 'running' || stopped) return
    const id = window.setInterval(() => setProgress((p) => Math.min(1, p + 0.0125)), 100)
    return () => window.clearInterval(id)
  }, [phase, stopped])

  useEffect(() => {
    if (phase !== 'running' || progress < 1) return
    const id = window.setTimeout(() => setPhase('review'), 400)
    return () => window.clearTimeout(id)
  }, [phase, progress])

  const doneRuns = new Set(LOG.filter((l) => l.at <= progress && l.run).map((l) => l.run as string))

  return (
    <div className="min-h-screen bg-paper text-ink">
      <header className="flex h-12 items-center gap-3 border-b border-border bg-cream px-5 text-sm">
        <span className="font-serif text-lg italic">econpaper</span>
        <span className="text-muted">/ 教育的工资回报</span>
        <div className="ml-auto flex items-center gap-1 text-xs text-muted">
          {(['brief', 'running', 'review'] as Phase[]).map((p, i) => (
            <span key={p} className={`rounded-full px-2 py-0.5 ${phase === p ? 'bg-ink text-paper' : ''}`}>
              {i + 1} {p === 'brief' ? '交代' : p === 'running' ? '在跑' : '回来审'}
            </span>
          ))}
        </div>
      </header>

      {phase === 'brief' && (
        <Brief
          {...{ goal, setGoal, scopes, setScopes, budget, setBudget }}
          onStart={() => {
            setProgress(0)
            setStopped(false)
            setPhase('running')
          }}
        />
      )}
      {phase === 'running' && (
        <Running
          progress={progress}
          budget={budget}
          stopped={stopped}
          onPeek={() => setPhase('review')}
          onToggle={() => setStopped((s) => !s)}
        />
      )}
      {phase === 'review' && <Review doneRuns={progress >= 1 ? new Set(SPECS.map((s) => s.id)) : doneRuns} partial={progress < 1} budget={budget} onResume={() => setPhase('running')} />}
    </div>
  )
}

function Brief(props: {
  goal: string
  setGoal: (g: string) => void
  scopes: typeof SCOPES
  setScopes: (s: typeof SCOPES) => void
  budget: number
  setBudget: (b: number) => void
  onStart: () => void
}) {
  const { goal, setGoal, scopes, setScopes, budget, setBudget, onStart } = props
  return (
    <main className="pp-enter mx-auto max-w-[620px] px-6 pb-32 pt-16">
      <h1 className="font-serif text-[30px] leading-tight">交代一下，然后去做别的</h1>
      <p className="mt-2 text-sm text-muted">它会自己跑一轮，你回来时看到的是一张对比表和几条发现，稿子不会被偷偷改掉。</p>

      <label className="mt-8 block text-xs text-muted">想弄清什么</label>
      <textarea
        value={goal}
        onChange={(e) => setGoal(e.target.value)}
        rows={3}
        className="mt-1 w-full resize-none rounded-lg border border-border bg-panel px-3 py-2 font-serif text-[16px] leading-7 outline-none focus:border-accent/60"
      />

      <div className="mt-4 flex items-center gap-2 rounded-lg border border-border bg-panel px-3 py-2 text-sm">
        <span className="rounded bg-accent/10 px-1.5 py-0.5 font-mono text-xs text-accent">csv</span>
        card1995.csv
        <span className="ml-auto text-xs text-muted">3,010 行 × 34 列</span>
      </div>

      <p className="mt-6 text-xs text-muted">允许它做的事</p>
      <div className="mt-2 grid grid-cols-2 gap-2">
        {scopes.map((s) => (
          <label
            key={s.id}
            className={`flex cursor-pointer items-center gap-2 rounded-lg border px-3 py-2 text-sm transition-colors duration-150 ${s.on ? 'border-accent/50 bg-accent/5' : 'border-border bg-panel text-muted'}`}
          >
            <input
              type="checkbox"
              checked={s.on}
              onChange={() => setScopes(scopes.map((x) => (x.id === s.id ? { ...x, on: !x.on } : x)))}
              className="accent-[#2f6b4f]"
            />
            {s.label}
          </label>
        ))}
      </div>

      <p className="mt-6 text-xs text-muted">最多跑多久</p>
      <div className="mt-2 inline-flex rounded-lg border border-border bg-panel p-0.5 text-sm">
        {BUDGETS.map((b) => (
          <button
            key={b}
            onClick={() => setBudget(b)}
            className={`rounded-md px-3 py-1 transition-colors duration-150 ${budget === b ? 'bg-ink text-paper' : 'text-muted hover:text-ink'}`}
          >
            {b} 分钟
          </button>
        ))}
      </div>

      <div className="mt-10 flex items-center gap-4">
        <button
          onClick={onStart}
          disabled={!goal.trim() || !scopes.some((s) => s.on)}
          className="rounded-lg bg-accent px-5 py-2.5 text-sm text-white transition-transform duration-100 active:scale-[0.97] disabled:opacity-40"
        >
          开始跑
        </button>
        <span className="text-xs text-muted">原型里 {budget} 分钟压缩成几秒钟</span>
      </div>
    </main>
  )
}

function Running({ progress, budget, stopped, onPeek, onToggle }: { progress: number; budget: number; stopped: boolean; onPeek: () => void; onToggle: () => void }) {
  const elapsed = Math.round(progress * budget * 60 * 0.97)
  const mmss = (s: number) => `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`
  const lines = LOG.filter((l) => l.at <= progress)
  const endRef = useRef<HTMLLIElement>(null)
  useEffect(() => {
    endRef.current?.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
  }, [lines.length])
  return (
    <main className="pp-enter mx-auto max-w-[620px] px-6 pb-32 pt-16">
      <div className="flex items-baseline justify-between">
        <h1 className="font-serif text-[26px]">{stopped ? '已暂停' : '正在跑'}</h1>
        <span className="font-mono text-sm text-muted">{mmss(elapsed)} / {mmss(budget * 60)}</span>
      </div>
      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-ink/10">
        <div className="h-full origin-left rounded-full bg-accent transition-transform duration-100 ease-linear" style={{ transform: `scaleX(${progress})` }} />
      </div>
      <p className="mt-3 text-sm text-muted">可以关掉这页，跑完会通知你。已经完成 {lines.filter((l) => l.run).length} 个设定。</p>

      <ol className="mt-8 space-y-0 border-l border-border pl-5 text-sm">
        {lines.map((l, i) => (
          <li key={l.text} ref={i === lines.length - 1 ? endRef : undefined} className="pp-enter relative py-2">
            <span className={`absolute -left-[25px] top-3.5 h-2 w-2 rounded-full ${i === lines.length - 1 && !stopped && progress < 1 ? 'animate-pulse bg-accent' : 'bg-ink/30'}`} />
            <span className="mr-2 font-mono text-xs text-muted">{mmss(Math.round(l.at * budget * 60))}</span>
            {l.text}
          </li>
        ))}
      </ol>

      <div className="mt-8 flex gap-3 text-sm">
        <button onClick={onPeek} disabled={lines.filter((l) => l.run).length === 0} className="rounded-lg border border-border bg-panel px-4 py-2 hover:border-ink/30 active:scale-[0.97] disabled:opacity-40">
          先看已有结果
        </button>
        <button onClick={onToggle} className="rounded-lg px-4 py-2 text-muted hover:text-ink active:scale-[0.97]">
          {stopped ? '继续' : '暂停'}
        </button>
      </div>
    </main>
  )
}

function Review({ doneRuns, partial, budget, onResume }: { doneRuns: Set<string>; partial: boolean; budget: number; onResume: () => void }) {
  const [selected, setSelected] = useState<string | null>(null)
  const [decisions, setDecisions] = useState<Record<string, 'adopt' | 'drop'>>({})
  const [writing, setWriting] = useState(false)
  const [written, setWritten] = useState(false)
  const runs = SPECS.filter((s) => doneRuns.has(s.id))
  const findings = FINDINGS.filter((f) => f.runs.every((r) => doneRuns.has(r)))
  const adopted = findings.filter((f) => decisions[f.id] === 'adopt')
  const decide = (id: string, d: 'adopt' | 'drop') =>
    setDecisions((m) => {
      const next = { ...m }
      if (next[id] === d) delete next[id]
      else next[id] = d
      return next
    })
  const x = (v: number) => `${(Math.max(0, Math.min(0.34, v)) / 0.34) * 100}%`

  return (
    <main className="pp-enter mx-auto grid max-w-[1120px] grid-cols-[1fr_340px] gap-8 px-6 pb-40 pt-10">
      <section>
        <p className="text-xs text-muted">{partial ? '中途查看 · 还在跑' : `跑完了 · 用时 ${Math.round(budget * 0.97)} 分钟`}</p>
        <h1 className="mt-1 font-serif text-[26px] leading-tight">
          {partial ? `已完成 ${runs.length} 个设定` : 'OLS 很稳，约 7.5%；IV 更大，约 13%，但不够精确'}
        </h1>
        {partial && (
          <button onClick={onResume} className="mt-2 text-sm text-accent hover:underline">回去继续跑 →</button>
        )}

        <div className="mt-6 overflow-hidden rounded-lg border border-border bg-panel text-sm">
          <div className="grid grid-cols-[1fr_90px_80px_minmax(160px,1.2fr)] gap-3 border-b border-border px-4 py-2 text-xs text-muted">
            <span>设定</span><span className="text-right">β</span><span className="text-right">SE</span><span>95% 置信区间（0 – 0.34）</span>
          </div>
          {runs.map((r) => {
            const [lo, hi] = ci(r)
            const on = selected === r.id
            return (
              <button
                key={r.id}
                onClick={() => setSelected(on ? null : r.id)}
                className={`pp-enter grid w-full grid-cols-[1fr_90px_80px_minmax(160px,1.2fr)] items-center gap-3 border-b border-border px-4 py-2.5 text-left last:border-b-0 transition-colors duration-150 ${on ? 'bg-accent/5' : 'hover:bg-ink/[0.02]'}`}
              >
                <span>
                  {r.label}
                  {r.illustrative && <span className="ml-2 rounded bg-warning/10 px-1 text-[10px] text-warning">示意</span>}
                </span>
                <span className="text-right font-mono">{fmt(r.coef)}<sup className="text-accent">{stars(r.p)}</sup></span>
                <span className="text-right font-mono text-muted">{fmt(r.se)}</span>
                <span className="relative h-3">
                  <span className="absolute top-1/2 h-px w-full bg-ink/10" />
                  <span className="absolute top-1/2 h-1 -translate-y-1/2 rounded-full bg-accent/40" style={{ left: x(lo), right: `calc(100% - ${x(hi)})` }} />
                  <span className="absolute top-1/2 h-2.5 w-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-accent" style={{ left: x(r.coef) }} />
                </span>
              </button>
            )
          })}
        </div>

        {selected && <RunDetail run={SPECS.find((s) => s.id === selected)!} />}
      </section>

      <aside className="space-y-3">
        <p className="text-xs text-muted">发现 · 逐条决定要不要进稿子</p>
        {findings.length === 0 && <p className="text-sm text-muted">还没有足够的结果形成发现。</p>}
        {findings.map((f) => {
          const d = decisions[f.id]
          return (
            <div key={f.id} className={`pp-enter rounded-lg border bg-panel p-3 text-[13px] leading-5 transition-opacity duration-200 ${d === 'drop' ? 'border-border opacity-45' : d === 'adopt' ? 'border-accent/50' : 'border-border'}`}>
              <p className="font-medium">{f.title}</p>
              <p className="mt-1 text-muted">{f.body}</p>
              <div className="mt-2 flex gap-2">
                <button
                  onClick={() => decide(f.id, 'adopt')}
                  className={`rounded-md px-2.5 py-1 transition-transform duration-100 active:scale-[0.97] ${d === 'adopt' ? 'bg-accent text-white' : 'border border-accent/50 text-accent hover:bg-accent/10'}`}
                >
                  {d === 'adopt' ? '✓ 已采纳' : '采纳进稿'}
                </button>
                <button
                  onClick={() => decide(f.id, 'drop')}
                  className="rounded-md px-2.5 py-1 text-muted hover:text-ink active:scale-[0.97]"
                >
                  {d === 'drop' ? '撤销' : '不要'}
                </button>
              </div>
            </div>
          )
        })}
      </aside>

      {adopted.length > 0 && !writing && createPortal(
        <div className="pp-pop fixed bottom-6 right-6 z-20 flex origin-bottom-right items-center gap-3 rounded-xl border border-border bg-panel px-4 py-3 text-sm shadow-[0_8px_24px_rgba(24,21,21,0.1)]">
          {written ? <span className="text-accent">✓ 已写进第 4 节</span> : <span>已采纳 {adopted.length} 条</span>}
          <button onClick={() => setWriting(true)} className="rounded-md bg-ink px-3 py-1 text-paper active:scale-[0.97]">
            {written ? '再看一眼' : '写进稿子 →'}
          </button>
        </div>,
        document.body,
      )}

      {writing && createPortal(
        <div className="fixed inset-0 z-30 flex items-center justify-center bg-ink/20 p-6" onClick={() => setWriting(false)}>
          <div onClick={(e) => e.stopPropagation()} className="pp-pop w-full max-w-[560px] rounded-xl border border-border bg-panel p-6 shadow-xl">
            <p className="text-xs text-muted">将加到第 4 节“结果”末尾 · 你可以先改</p>
            <div contentEditable suppressContentEditableWarning className="mt-3 rounded-md border border-border bg-paper px-4 py-3 font-serif text-[16px] leading-8 outline-none focus:border-accent/60">
              {adopted.map((f) => f.paragraph).join('')}
            </div>
            <p className="mt-2 text-xs text-muted">引用的设定：{adopted.flatMap((f) => f.runs).map((id) => SPECS.find((s) => s.id === id)?.label).join('、')}</p>
            <div className="mt-5 flex justify-end gap-2 text-sm">
              <button onClick={() => setWriting(false)} className="rounded-md px-3 py-1.5 text-muted hover:text-ink">取消</button>
              <button
                onClick={() => {
                  setWritten(true)
                  setWriting(false)
                }}
                className="rounded-md bg-accent px-4 py-1.5 text-white active:scale-[0.97]"
              >
                放进稿子
              </button>
            </div>
          </div>
        </div>,
        document.body,
      )}
    </main>
  )
}

function RunDetail({ run }: { run: Run }) {
  const [lo, hi] = ci(run)
  return (
    <div className="pp-enter mt-4 rounded-lg border border-border bg-panel p-4 text-sm">
      <p className="font-medium">{run.label}</p>
      <p className="mt-1 text-muted">
        β = {fmt(run.coef)}（约 {pct(run.coef)}），95% CI [{fmt(lo, 3)}, {fmt(hi, 3)}]，n = {run.n.toLocaleString()}，标准误 {run.cov}
        {run.illustrative && '。这一行是原型示意数据，不是真实运行结果。'}
      </p>
      <pre className="mt-3 overflow-x-auto rounded bg-ink px-3 py-2 font-mono text-[11px] leading-5 text-[#e8e4da]">{run.code}</pre>
    </div>
  )
}
