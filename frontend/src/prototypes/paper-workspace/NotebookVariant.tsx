import { useEffect, useRef, useState, type ReactNode } from 'react'
import { FIRST_STAGE, IV, OLS, ci, fmt, pct, stars, type Run } from './data'

type Main = 'OLS' | 'IV'
type BlockId = 'intro' | 'data' | 'strategy' | 'table' | 'results' | 'figure' | 'discussion'
type Diff = { block: BlockId; before: string; after: string; reason: string; onAccept?: () => void; onReject?: () => void }
type Note = { id: number; block: BlockId; tag: string; text: string; action: string; status: 'open' | 'resolved' }

const RESULT_TEXT: Record<Main, string> = {
  OLS: '控制工作经验、种族、城乡与 1966 年居住地区后，每多受一年教育，小时工资的对数约提高 0.075（约 7.5%），在 1% 水平上显著。',
  IV: '以是否在四年制大学附近长大作为教育年限的工具变量，每多受一年教育，小时工资的对数约提高 0.132（约 13.2%），在 5% 水平上显著；估计值高于 OLS，但置信区间明显更宽。',
}
const RESULT_SHORT = '每多一年教育，小时工资约提高 7.5%（OLS，1% 水平显著）。'
const INTRO_BEFORE = '已有研究普遍发现，教育的工资回报约为 10%，但这些估计可能混入了能力差异。'
const INTRO_AFTER = '已有研究发现教育与工资强相关；本文 OLS 估计约为 7.5%，但它可能混入了能力差异，因此还需要一个外生的教育变动来源。'
const EXCLUSION =
  '工具变量需要满足排他性：大学邻近性只通过教育影响工资。一个担忧是，靠近大学的地区本身工资更高或家庭背景更好；我们控制了 1966 年的城乡与地区虚拟变量来缓解这一点，但无法完全排除。'

const INITIAL_NOTES: Note[] = [
  { id: 1, block: 'intro', tag: '一致性', text: '引言写“回报约为 10%”，但结果段的主估计是 7.5%。读者会以为两处说的是同一个数。', action: '改引言', status: 'open' },
  { id: 2, block: 'strategy', tag: '识别', text: '用了 nearc4 作工具，但没有讨论排他性：大学邻近性可能通过地区劳动力市场直接影响工资。', action: '补一段排他性讨论', status: 'open' },
  { id: 3, block: 'table', tag: '推断', text: `第一阶段 F = ${FIRST_STAGE.f}，高于 10 但低于 23.1，t 检验可能过度拒绝。建议在表注里说明。`, action: '加表注', status: 'open' },
]

export default function NotebookVariant() {
  const [main, setMain] = useState<Main>('OLS')
  const [resultText, setResultText] = useState(RESULT_TEXT.OLS)
  const [introText, setIntroText] = useState(INTRO_BEFORE)
  const [strategyExtra, setStrategyExtra] = useState<string | null>(null)
  const [tableNote, setTableNote] = useState(false)
  const [diff, setDiff] = useState<Diff | null>(null)
  const [shown, setShown] = useState<Main>('OLS') // which spec the prose currently reflects
  const [fork, setFork] = useState(false)
  const [notes, setNotes] = useState(INITIAL_NOTES)
  const [focusBlock, setFocusBlock] = useState<BlockId | null>(null)
  const [flash, setFlash] = useState<{ block: BlockId; n: number } | null>(null)
  const [working, setWorking] = useState<string | null>(null)
  const [source, setSource] = useState<{ run: Run; field: string; x: number; y: number } | null>(null)
  const [code, setCode] = useState<Partial<Record<BlockId, boolean>>>({})
  const [rerun, setRerun] = useState<BlockId | null>(null)

  const shownRun = shown === 'OLS' ? OLS : IV
  const stale = shown !== main
  const pulse = (block: BlockId) => setFlash({ block, n: Date.now() })

  function agent(label: string, then: () => void) {
    setWorking(label)
    window.setTimeout(() => {
      setWorking(null)
      then()
    }, 700)
  }

  function switchMain(next: Main) {
    if (next === main) return
    const prev = main
    setMain(next)
    agent('结果段', () =>
      setDiff({
        block: 'results',
        before: resultText,
        after: RESULT_TEXT[next],
        reason: `主设定从 ${prev} 改为 ${next}，这段引用的 3 个数字已过时`,
        onAccept: () => setShown(next),
        onReject: () => setMain(prev),
      }),
    )
  }

  function acceptDiff() {
    if (!diff) return
    if (diff.block === 'results') setResultText(diff.after)
    if (diff.block === 'intro') setIntroText(diff.after)
    if (diff.block === 'strategy') setStrategyExtra(diff.after)
    diff.onAccept?.()
    pulse(diff.block)
    setDiff(null)
  }

  function rejectDiff() {
    diff?.onReject?.()
    setDiff(null)
  }

  function fixNote(n: Note) {
    const resolve = () => setNotes((ns) => ns.map((x) => (x.id === n.id ? { ...x, status: 'resolved' } : x)))
    setFocusBlock(n.block)
    if (n.id === 1)
      agent('引言', () => setDiff({ block: 'intro', before: introText, after: INTRO_AFTER, reason: '审稿意见 · 一致性', onAccept: resolve }))
    if (n.id === 2)
      agent('实证策略', () => setDiff({ block: 'strategy', before: '', after: EXCLUSION, reason: '审稿意见 · 识别', onAccept: resolve }))
    if (n.id === 3)
      agent('表 1', () => {
        setTableNote(true)
        resolve()
        pulse('table')
      })
  }

  function doRerun(b: BlockId) {
    setRerun(b)
    window.setTimeout(() => {
      setRerun(null)
      pulse(b)
    }, 800)
  }

  function command(text: string) {
    if (!text.trim()) return
    agent('结果段', () =>
      setDiff({ block: 'results', before: resultText, after: main === 'OLS' ? RESULT_SHORT : RESULT_TEXT.IV, reason: `“${text.trim()}”` }),
    )
  }

  const openNotes = notes.filter((n) => n.status === 'open').length

  const chip = (run: Run, field: 'coef' | 'se' | 'n' | 'f', isMain = false) => {
    const value = field === 'coef' ? fmt(run.coef) : field === 'se' ? fmt(run.se) : field === 'n' ? run.n.toLocaleString() : String(FIRST_STAGE.f)
    const isStale = isMain && stale
    return (
      <button
        className={`mx-0.5 rounded px-1 font-mono text-[0.86em] transition-colors duration-150 ${
          isStale
            ? 'bg-warning/10 text-warning line-through decoration-warning/60'
            : 'bg-accent/10 text-accent hover:bg-accent/20'
        }`}
        title={isStale ? '设定已改，这个数字待更新' : '点开看来源'}
        onClick={(e) => {
          const r = (e.currentTarget as HTMLElement).getBoundingClientRect()
          setSource({ run, field, x: r.left, y: r.bottom + 6 })
        }}
      >
        {value}
      </button>
    )
  }

  return (
    <div className="min-h-screen bg-paper text-ink" onClick={() => source && setSource(null)}>
      {/* toolbar */}
      <header className="sticky top-0 z-20 flex h-12 items-center gap-3 border-b border-border bg-cream/95 px-5 text-sm backdrop-blur">
        <span className="font-serif text-lg italic">econpaper</span>
        <span className="text-muted">/</span>
        <span className="truncate">教育的工资回报</span>
        <div className="ml-auto flex items-center gap-2">
          <span className="text-muted">主设定</span>
          <div className="flex rounded-md border border-border bg-panel p-0.5">
            {(['OLS', 'IV'] as Main[]).map((m) => (
              <button
                key={m}
                onClick={() => switchMain(m)}
                disabled={!!diff || !!working}
                title={diff ? '先处理稿子里的修改建议' : undefined}
                className={`rounded px-2.5 py-1 text-xs transition-colors duration-150 disabled:cursor-not-allowed ${main === m ? 'bg-accent text-white' : 'text-muted hover:text-ink'}`}
              >
                {m}
              </button>
            ))}
          </div>
          <button
            onClick={() => setFork((f) => !f)}
            className={`rounded-md border px-2.5 py-1 text-xs transition-colors duration-150 ${fork ? 'border-accent bg-accent/10 text-accent' : 'border-border bg-panel hover:border-ink/30'}`}
          >
            ⑂ {fork ? '收起分叉' : '分叉比较'}
          </button>
          <span className="ml-2 rounded-full bg-panel px-2 py-0.5 text-xs text-muted">审稿 {openNotes} 条待处理</span>
        </div>
      </header>

      <div className="mx-auto flex max-w-[1180px] gap-8 px-6 pb-40 pt-10">
        {/* paper */}
        <article className="min-w-0 flex-1 font-serif text-[17px] leading-[1.85]">
          <h1 className="mb-1 text-[30px] leading-tight">教育的工资回报：来自大学邻近性的证据</h1>
          <p className="mb-8 font-sans text-sm text-muted">数据：NLS 青年男性，1976 · 3,010 人 · 最后运行 09-07 16:16</p>

          <Block id="intro" title="1 引言" {...{ focusBlock, flash, diff, acceptDiff, rejectDiff }}>
            <p>
              教育能在多大程度上提高收入，是劳动经济学最基本的问题之一。{introText}本文使用 Card (1995) 的数据，先给出 OLS 基准，再以大学邻近性作为工具变量。
            </p>
          </Block>

          <Block id="data" title="2 数据" {...{ focusBlock, flash, diff, acceptDiff, rejectDiff }}>
            <p>
              样本来自 1966 年启动的全国青年男性追踪调查（NLS），我们使用 1976 年的工资与教育信息，共 {chip(OLS, 'n')} 个观测。被解释变量是小时工资的对数，核心解释变量是受教育年限。
            </p>
          </Block>

          <Block id="strategy" title="3 实证策略" {...{ focusBlock, flash, diff, acceptDiff, rejectDiff }}>
            <p>基准模型为：</p>
            <pre className="my-3 overflow-x-auto rounded-md border border-border bg-panel px-4 py-3 font-mono text-[13px] leading-6">
              {OLS.formula}
            </pre>
            <p>OLS 估计可能因能力等遗漏变量而有偏。我们用“是否在四年制大学附近长大”（nearc4）作为教育的工具变量。</p>
            {strategyExtra && <p className="mt-3">{strategyExtra}</p>}
          </Block>

          {fork ? (
            <ForkView main={main} onPick={(m) => { setFork(false); switchMain(m) }} />
          ) : (
            <>
              <Block
                id="table"
                title="4 结果"
                onRerun={() => doRerun('table')}
                onCode={() => setCode((c) => ({ ...c, table: !c.table }))}
                running={rerun === 'table'}
                {...{ focusBlock, flash, diff, acceptDiff, rejectDiff }}
              >
                <ResultTable main={main} chip={chip} note={tableNote} />
                {code.table && <CodeCell runs={[OLS, IV]} />}
              </Block>

              <Block id="results" {...{ focusBlock, flash, diff, acceptDiff, rejectDiff }}>
                <p>
                  {resultText}
                  <span className="ml-1 font-sans text-xs text-muted">
                    （主估计 {chip(shownRun, 'coef', true)}，标准误 {chip(shownRun, 'se', true)}）
                  </span>
                </p>
              </Block>

              <Block
                id="figure"
                onRerun={() => doRerun('figure')}
                onCode={() => setCode((c) => ({ ...c, figure: !c.figure }))}
                running={rerun === 'figure'}
                {...{ focusBlock, flash, diff, acceptDiff, rejectDiff }}
              >
                <CoefPlot main={main} />
                <p className="mt-1 text-center font-sans text-xs text-muted">图 1 · 教育回报估计与 95% 置信区间</p>
                {code.figure && <CodeCell runs={[OLS, IV]} plot />}
              </Block>
            </>
          )}

          <Block id="discussion" title="5 结论" {...{ focusBlock, flash, diff, acceptDiff, rejectDiff }}>
            <p className="text-muted">（还没写。可以在下面让 agent 起草，或者自己动笔。）</p>
          </Block>
        </article>

        {/* reviewer margin */}
        <aside className="hidden w-[270px] shrink-0 lg:block">
          <div className="sticky top-20 space-y-3">
            <p className="font-sans text-xs uppercase tracking-wider text-muted">审稿人</p>
            {notes.map((n) => (
              <div
                key={n.id}
                onMouseEnter={() => setFocusBlock(n.block)}
                onMouseLeave={() => setFocusBlock(null)}
                className={`rounded-lg border bg-panel p-3 font-sans text-[13px] leading-5 transition-opacity duration-200 ${
                  n.status === 'resolved' ? 'border-border opacity-50' : 'border-border hover:border-ink/25'
                }`}
              >
                <div className="mb-1 flex items-center gap-2">
                  <span className="rounded bg-ink/5 px-1.5 py-0.5 text-[11px] text-muted">{n.tag}</span>
                  {n.status === 'resolved' && <span className="text-[11px] text-accent">✓ 已处理</span>}
                </div>
                <p>{n.text}</p>
                {n.status === 'open' && (
                  <button
                    onClick={() => fixNote(n)}
                    disabled={!!working || !!diff}
                    className="mt-2 text-accent hover:underline disabled:text-muted disabled:no-underline"
                  >
                    {n.action} →
                  </button>
                )}
              </div>
            ))}
          </div>
        </aside>
      </div>

      <CommandBar working={working} busy={!!diff} onSubmit={command} />

      {source && <SourcePopover {...source} onRerun={() => { setSource(null); doRerun('table') }} />}
    </div>
  )
}

function Block(props: {
  id: BlockId
  title?: string
  children: ReactNode
  focusBlock: BlockId | null
  flash: { block: BlockId; n: number } | null
  diff: Diff | null
  acceptDiff: () => void
  rejectDiff: () => void
  onRerun?: () => void
  onCode?: () => void
  running?: boolean
}) {
  const { id, title, children, focusBlock, flash, diff, acceptDiff, rejectDiff, onRerun, onCode, running } = props
  const focused = focusBlock === id
  const flashing = flash?.block === id
  const myDiff = diff?.block === id ? diff : null
  return (
    <section className="group relative mb-6">
      {title && <h2 className="mb-2 font-serif text-[21px]">{title}</h2>}
      {(onRerun || onCode) && (
        <div className="absolute -left-12 top-1 flex flex-col gap-1 opacity-0 transition-opacity duration-150 group-hover:opacity-100">
          {onRerun && (
            <button onClick={onRerun} title="重跑这一块" className="h-7 w-7 rounded-md border border-border bg-panel font-sans text-sm hover:border-ink/30">
              <span className={running ? 'inline-block animate-spin' : ''}>↻</span>
            </button>
          )}
          {onCode && (
            <button onClick={onCode} title="展开代码" className="h-7 w-7 rounded-md border border-border bg-panel font-mono text-[11px] hover:border-ink/30">
              {'</>'}
            </button>
          )}
        </div>
      )}
      <div
        key={flashing ? flash?.n : 'still'}
        className={`rounded-md transition-shadow duration-200 ${focused ? 'shadow-[0_0_0_2px_rgba(47,107,79,0.35)]' : ''} ${flashing ? 'pp-flash' : ''} ${running ? 'opacity-60' : ''}`}
      >
        {children}
      </div>
      {myDiff && (
        <div className="pp-enter mt-3 rounded-lg border border-accent/40 bg-panel p-4 font-sans text-sm shadow-sm">
          <p className="mb-2 text-xs text-muted">agent 建议修改 · {myDiff.reason}</p>
          {myDiff.before && <p className="font-serif text-[15px] leading-7 text-muted line-through decoration-muted/50">{myDiff.before}</p>}
          <p className="mt-1 font-serif text-[15px] leading-7 text-ink underline decoration-accent/40 decoration-2 underline-offset-4">{myDiff.after}</p>
          <div className="mt-3 flex gap-2">
            <button onClick={acceptDiff} className="rounded-md bg-accent px-3 py-1 text-white transition-transform duration-100 active:scale-[0.97]">接受</button>
            <button onClick={rejectDiff} className="rounded-md border border-border px-3 py-1 hover:border-ink/30 active:scale-[0.97]">不要</button>
          </div>
        </div>
      )}
    </section>
  )
}

function ResultTable({ main, chip, note }: { main: Main; chip: (r: Run, f: 'coef' | 'se' | 'n' | 'f', isMain?: boolean) => ReactNode; note: boolean }) {
  const col = (r: Run) => (
    <td className={`px-4 py-2 text-right ${main === r.method ? 'bg-accent/5' : ''}`}>
      {chip(r, 'coef')}
      <sup className="text-accent">{stars(r.p)}</sup>
      <div className="text-xs text-muted">({fmt(r.se)})</div>
    </td>
  )
  return (
    <div className="my-2 font-sans text-sm">
      <p className="mb-2 text-center font-serif">表 1 · 教育对小时工资对数的影响</p>
      <table className="mx-auto border-y border-ink/70">
        <thead>
          <tr className="border-b border-ink/30 text-muted">
            <th className="px-4 py-2 text-left font-normal"></th>
            {[OLS, IV].map((r) => (
              <th key={r.method} className={`px-4 py-2 text-right font-normal ${main === r.method ? 'bg-accent/5 text-accent' : ''}`}>
                ({r.method === 'OLS' ? 1 : 2}) {r.method}
                {main === r.method && <span className="ml-1 text-[10px]">主</span>}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <tr>
            <td className="px-4 py-2">受教育年限</td>
            {col(OLS)}
            {col(IV)}
          </tr>
          <tr className="text-muted">
            <td className="px-4 py-1">控制变量</td>
            <td className="px-4 py-1 text-right">是</td>
            <td className="px-4 py-1 text-right">是</td>
          </tr>
          <tr className="text-muted">
            <td className="px-4 py-1">第一阶段 F</td>
            <td className="px-4 py-1 text-right">—</td>
            <td className="px-4 py-1 text-right">{chip(IV, 'f')}</td>
          </tr>
          <tr className="border-t border-ink/20 text-muted">
            <td className="px-4 py-1">N</td>
            <td className="px-4 py-1 text-right">3,010</td>
            <td className="px-4 py-1 text-right">3,010</td>
          </tr>
        </tbody>
      </table>
      <p className="mx-auto mt-2 max-w-[520px] text-xs leading-5 text-muted">
        注：括号内为标准误（OLS 为 HC1 稳健标准误）。*** p&lt;0.01, ** p&lt;0.05。
        {note && <span className="pp-enter"> 第一阶段有效 F = {FIRST_STAGE.fEff}，处于 10 到 23.1 之间，IV 的 t 检验可能过度拒绝，结论宜谨慎解读。</span>}
      </p>
    </div>
  )
}

function CoefPlot({ main }: { main: Main }) {
  const W = 520
  const x = (v: number) => 60 + (v / 0.26) * (W - 90)
  const rows = [OLS, IV]
  return (
    <svg viewBox={`0 0 ${W} 120`} className="mx-auto block w-full max-w-[520px] font-sans">
      {[0, 0.05, 0.1, 0.15, 0.2, 0.25].map((t) => (
        <g key={t}>
          <line x1={x(t)} x2={x(t)} y1={10} y2={96} stroke="#d8d2c6" strokeDasharray={t === 0 ? '' : '2 3'} />
          <text x={x(t)} y={112} fontSize={10} textAnchor="middle" fill="#515151">{t.toFixed(2)}</text>
        </g>
      ))}
      {rows.map((r, i) => {
        const [lo, hi] = ci(r)
        const y = 34 + i * 40
        const on = r.method === main
        return (
          <g key={r.method}>
            <text x={8} y={y + 4} fontSize={12} fill={on ? '#2f6b4f' : '#181515'}>{r.method}</text>
            <line x1={x(Math.max(lo, 0))} x2={x(hi)} y1={y} y2={y} stroke={on ? '#2f6b4f' : '#181515'} strokeWidth={on ? 2.5 : 1.5} />
            <circle cx={x(r.coef)} cy={y} r={on ? 5 : 4} fill={on ? '#2f6b4f' : '#181515'} />
          </g>
        )
      })}
    </svg>
  )
}

function CodeCell({ runs, plot }: { runs: Run[]; plot?: boolean }) {
  return (
    <pre className="pp-enter mt-3 overflow-x-auto rounded-md bg-ink px-4 py-3 font-mono text-[12px] leading-5 text-[#e8e4da]">
      {`import pandas as pd\nimport statspai\ndf = pd.read_csv("data_card1995.csv")\n\n`}
      {runs.map((r) => `${r.method.toLowerCase()} = ${r.code}\n`).join('')}
      {plot ? `\n# 图 1：两个估计的点估计与 95% 置信区间` : `\n# 表 1：两列 educ 系数与标准误`}
    </pre>
  )
}

function ForkView({ main, onPick }: { main: Main; onPick: (m: Main) => void }) {
  return (
    <section className="pp-enter mb-6">
      <h2 className="mb-3 font-serif text-[21px]">4 结果 · 分叉比较</h2>
      <div className="grid grid-cols-2 gap-4 font-sans text-sm">
        {[OLS, IV].map((r) => {
          const [lo, hi] = ci(r)
          return (
            <div key={r.method} className={`rounded-lg border bg-panel p-4 ${main === r.method ? 'border-accent/50' : 'border-border'}`}>
              <p className="mb-1 text-xs text-muted">分支 {r.method === 'OLS' ? 'A' : 'B'} · {r.label}</p>
              <p className="font-mono text-2xl">{fmt(r.coef)}<sup className="text-sm text-accent">{stars(r.p)}</sup></p>
              <p className="text-xs text-muted">SE {fmt(r.se)} · 95% CI [{fmt(lo, 3)}, {fmt(hi, 3)}] · 约 {pct(r.coef)}</p>
              <p className="mt-3 font-serif text-[15px] leading-7">{RESULT_TEXT[r.method]}</p>
              <button
                onClick={() => onPick(r.method)}
                disabled={main === r.method}
                className="mt-3 rounded-md border border-accent px-3 py-1 text-accent transition-transform duration-100 hover:bg-accent/10 active:scale-[0.97] disabled:border-border disabled:text-muted"
              >
                {main === r.method ? '当前主设定' : '用这一支作主设定'}
              </button>
            </div>
          )
        })}
      </div>
    </section>
  )
}

function SourcePopover({ run, field, x, y, onRerun }: { run: Run; field: string; x: number; y: number; onRerun: () => void }) {
  const [copied, setCopied] = useState(false)
  const left = Math.min(x, window.innerWidth - 400)
  return (
    <div
      onClick={(e) => e.stopPropagation()}
      className="pp-pop fixed z-30 w-[380px] origin-top-left rounded-lg border border-border bg-panel p-4 font-sans text-[13px] shadow-lg"
      style={{ left, top: y }}
    >
      <p className="text-xs text-muted">这个数字来自</p>
      <p className="mt-0.5 font-medium">{run.label}</p>
      <dl className="mt-2 grid grid-cols-[72px_1fr] gap-y-1 text-xs">
        <dt className="text-muted">字段</dt><dd className="font-mono">{field === 'f' ? 'first_stage_F' : field}</dd>
        <dt className="text-muted">运行</dt><dd className="font-mono">{run.id} · {run.ranAt}</dd>
        <dt className="text-muted">标准误</dt><dd>{run.cov}</dd>
        <dt className="text-muted">样本</dt><dd>{run.n.toLocaleString()} 人</dd>
      </dl>
      <pre className="mt-2 overflow-x-auto rounded bg-ink px-3 py-2 font-mono text-[11px] leading-5 text-[#e8e4da]">{run.code}</pre>
      <div className="mt-3 flex gap-2">
        <button
          onClick={() => {
            void navigator.clipboard?.writeText(run.code)
            setCopied(true)
          }}
          className="rounded-md border border-border px-2.5 py-1 hover:border-ink/30 active:scale-[0.97]"
        >
          {copied ? '已复制' : '复制代码'}
        </button>
        <button onClick={onRerun} className="rounded-md border border-border px-2.5 py-1 hover:border-ink/30 active:scale-[0.97]">重跑</button>
      </div>
    </div>
  )
}

function CommandBar({ working, busy, onSubmit }: { working: string | null; busy: boolean; onSubmit: (t: string) => void }) {
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
    <div className="fixed bottom-[76px] left-1/2 z-20 w-[min(640px,calc(100vw-32px))] -translate-x-1/2">
      <form
        onSubmit={(e) => {
          e.preventDefault()
          onSubmit(text)
          setText('')
        }}
        className="flex items-center gap-2 rounded-xl border border-border bg-panel px-3 py-2 font-sans text-sm shadow-[0_8px_24px_rgba(24,21,21,0.08)]"
      >
        {working ? (
          <span className="pp-enter flex items-center gap-2 text-muted">
            <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-accent" />
            agent 正在改 · {working}
          </span>
        ) : (
          <input
            ref={ref}
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={busy}
            placeholder={busy ? '先处理上面的修改建议' : '让 agent 改这份稿子… 例如“把结果段写短一点”   ⌘K'}
            className="flex-1 bg-transparent outline-none placeholder:text-muted/70"
          />
        )}
        <button type="submit" disabled={!!working || busy || !text.trim()} className="rounded-md bg-ink px-2.5 py-1 text-xs text-paper disabled:opacity-30">
          ↵
        </button>
      </form>
    </div>
  )
}
