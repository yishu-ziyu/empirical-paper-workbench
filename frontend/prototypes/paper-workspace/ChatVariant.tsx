import { useEffect, useRef, useState, type ReactNode } from 'react'
import { FIRST_STAGE, IV, OLS, fmt, stars } from './data'

type Section = 'intro' | 'table' | 'results' | 'figure'
type Msg =
  | { id: number; from: 'user'; text: string; quote?: string }
  | { id: number; from: 'agent'; text: string; work?: { title: string; code: string }; choices?: string[] }

const STEPS: { match: RegExp; user: string; work?: { title: string; code: string }; reply: string; adds: Section[]; choices?: string[] }[] = [
  {
    match: /ols|基准|先跑/i,
    user: '先跑一个 OLS 基准',
    work: { title: 'OLS · 16 个变量 · HC1 · 0.4 秒', code: OLS.code },
    reply: `教育每多一年，小时工资约高 7.5%（β = ${fmt(OLS.coef)}，SE ${fmt(OLS.se)}，n = 3,010）。表 1 和一段结果我放进右边的稿子了。`,
    adds: ['table', 'results'],
  },
  {
    match: /iv|工具|能力/i,
    user: 'OLS 可能有能力偏误，试试工具变量',
    reply: '数据里有两个候选工具：nearc4（是否在四年制大学附近长大）和 nearc2（两年制）。先用哪个？',
    adds: [],
    choices: ['nearc4', 'nearc2'],
  },
  {
    match: /nearc/i,
    user: 'nearc4',
    work: { title: `2SLS · 工具 nearc4 · 第一阶段 F ${FIRST_STAGE.f}`, code: IV.code },
    reply: `IV 估计 ${fmt(IV.coef)}（SE ${fmt(IV.se)}），比 OLS 大，但置信区间宽得多。第一阶段 F = ${FIRST_STAGE.f}，工具强度中等，我在表注里写明了，也加了一张系数图。`,
    adds: ['figure'],
  },
  {
    match: /引言|intro/i,
    user: '帮我起草引言',
    reply: '写好了，放在稿子最前面。我没有写具体的“10%”这种文献数字，等你补了参考文献再加。',
    adds: ['intro'],
  },
]

export default function ChatVariant() {
  const [msgs, setMsgs] = useState<Msg[]>([
    { id: 0, from: 'agent', text: '我读完了 card1995.csv：3,010 行，34 列，里面有工资、教育年限、工作经验和 1966 年居住地信息。你想先看什么？' },
  ])
  const [step, setStep] = useState(0)
  const [typing, setTyping] = useState(false)
  const [sections, setSections] = useState<Section[]>([])
  const [fresh, setFresh] = useState<Section[]>([])
  const [ivDone, setIvDone] = useState(false)
  const [tab, setTab] = useState<'paper' | 'notebook'>('paper')
  const [input, setInput] = useState('')
  const [quote, setQuote] = useState<string | null>(null)
  const listRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' })
  }, [msgs, typing])

  function send(text: string) {
    const t = text.trim()
    if (!t || typing) return
    setMsgs((m) => [...m, { id: Date.now(), from: 'user', text: t, quote: quote ?? undefined }])
    setInput('')
    setQuote(null)
    const idx = STEPS.findIndex((s, i) => i >= step && s.match.test(t))
    const s = STEPS[idx >= 0 ? idx : Math.min(step, STEPS.length - 1)]
    const next = idx >= 0 ? idx + 1 : step + 1
    setTyping(true)
    window.setTimeout(() => {
      setTyping(false)
      if (step >= STEPS.length) {
        setMsgs((m) => [...m, { id: Date.now() + 1, from: 'agent', text: '好的，我记下了。这一版原型的对话脚本到这里就结束了。' }])
        return
      }
      setMsgs((m) => [...m, { id: Date.now() + 1, from: 'agent', text: s.reply, work: s.work, choices: s.choices }])
      if (s.adds.length) {
        setSections((cur) => [...new Set([...cur, ...s.adds])])
        setFresh(s.adds)
        window.setTimeout(() => setFresh([]), 2400)
      }
      if (s.user === 'nearc4') setIvDone(true)
      setStep(next)
    }, 900)
  }

  const awaitingChoice = !!STEPS[step - 1]?.choices
  const suggestion = awaitingChoice ? null : STEPS[step]?.user

  return (
    <div className="flex h-screen bg-paper text-ink">
      {/* conversation */}
      <div className="flex w-[42%] min-w-[360px] flex-col border-r border-border bg-cream">
        <header className="flex h-12 items-center gap-2 border-b border-border px-5 text-sm">
          <span className="font-serif text-lg italic">econpaper</span>
          <span className="text-muted">· 教育的工资回报</span>
        </header>
        <div ref={listRef} className="flex-1 space-y-4 overflow-y-auto px-5 py-6 text-[14px] leading-6">
          {msgs.map((m) =>
            m.from === 'user' ? (
              <div key={m.id} className="pp-enter ml-auto max-w-[80%]">
                {m.quote && <p className="mb-1 border-l-2 border-accent/50 pl-2 text-xs text-muted">{m.quote}</p>}
                <div className="rounded-2xl rounded-br-md bg-ink px-3.5 py-2 text-paper">{m.text}</div>
              </div>
            ) : (
              <div key={m.id} className="pp-enter max-w-[92%]">
                {m.work && <WorkCard {...m.work} />}
                <p>{m.text}</p>
                {m.choices && (
                  <div className="mt-2 flex gap-2">
                    {m.choices.map((c) => (
                      <button
                        key={c}
                        onClick={() => send(c)}
                        disabled={typing || step !== STEPS.findIndex((s) => s.user === 'nearc4')}
                        className="rounded-full border border-accent/50 px-3 py-1 text-accent transition-transform duration-100 hover:bg-accent/10 active:scale-[0.97] disabled:border-border disabled:text-muted"
                      >
                        {c}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ),
          )}
          {typing && (
            <div className="pp-enter flex items-center gap-1 text-muted">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-muted" />
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-muted [animation-delay:150ms]" />
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-muted [animation-delay:300ms]" />
            </div>
          )}
        </div>
        <div className="border-t border-border p-4 pb-20">
          {suggestion && !typing && (
            <button
              onClick={() => send(suggestion)}
              className="pp-enter mb-2 rounded-full border border-border bg-panel px-3 py-1 text-xs text-muted transition-colors duration-150 hover:border-ink/30 hover:text-ink"
            >
              {suggestion}
            </button>
          )}
          {quote && (
            <div className="pp-enter mb-2 flex items-center gap-2 rounded-md bg-accent/10 px-2 py-1 text-xs text-accent">
              <span className="truncate">引用：{quote}</span>
              <button onClick={() => setQuote(null)} className="ml-auto">×</button>
            </div>
          )}
          <form
            onSubmit={(e) => {
              e.preventDefault()
              send(input)
            }}
            className="flex items-end gap-2 rounded-xl border border-border bg-panel px-3 py-2"
          >
            <textarea
              ref={inputRef}
              rows={1}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  send(input)
                }
              }}
              placeholder="说你想研究什么，或者让它跑点什么…"
              className="max-h-32 flex-1 resize-none bg-transparent text-sm outline-none placeholder:text-muted/70"
            />
            <button type="submit" disabled={!input.trim() || typing} className="rounded-md bg-ink px-2.5 py-1 text-xs text-paper disabled:opacity-30">↵</button>
          </form>
        </div>
      </div>

      {/* living document */}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-12 items-center gap-1 border-b border-border px-5 text-sm">
          {(['paper', 'notebook'] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`rounded-md px-3 py-1 transition-colors duration-150 ${tab === t ? 'bg-ink/5 text-ink' : 'text-muted hover:text-ink'}`}
            >
              {t === 'paper' ? '论文' : 'Notebook'}
            </button>
          ))}
          <span className="ml-auto text-xs text-muted">同一份研究的两个视图</span>
        </header>
        <div className="flex-1 overflow-y-auto">
          {tab === 'paper' ? (
            <Paper sections={sections} fresh={fresh} ivDone={ivDone} onQuote={(q) => { setQuote(q); inputRef.current?.focus() }} />
          ) : (
            <Notebook sections={sections} ivDone={ivDone} />
          )}
        </div>
      </div>
    </div>
  )
}

function WorkCard({ title, code }: { title: string; code: string }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="mb-2 rounded-lg border border-border bg-panel text-xs">
      <button onClick={() => setOpen((o) => !o)} className="flex w-full items-center gap-2 px-3 py-2 text-left">
        <span className="text-accent">✓</span>
        <span className="flex-1 font-mono">{title}</span>
        <span className={`text-muted transition-transform duration-150 ${open ? 'rotate-90' : ''}`}>›</span>
      </button>
      {open && <pre className="pp-enter overflow-x-auto border-t border-border px-3 py-2 font-mono text-[11px] leading-5">{code}</pre>}
    </div>
  )
}

function Paper({ sections, fresh, ivDone, onQuote }: { sections: Section[]; fresh: Section[]; ivDone: boolean; onQuote: (q: string) => void }) {
  if (!sections.length)
    return (
      <div className="flex h-full items-center justify-center text-center text-sm text-muted">
        <p>稿子还是空的。<br />在左边跑出第一个结果后，它会自己长出来。</p>
      </div>
    )
  const S = ({ id, label, children }: { id: Section; label: string; children: ReactNode }) =>
    sections.includes(id) ? (
      <section className={`group relative mb-6 border-l-2 pl-4 transition-colors duration-500 ${fresh.includes(id) ? 'pp-enter border-accent' : 'border-transparent'}`}>
        {fresh.includes(id) && <span className="absolute -left-[2px] -top-5 font-sans text-[11px] text-accent">刚更新</span>}
        <button
          onClick={() => onQuote(label)}
          className="absolute -right-2 top-0 rounded-md border border-border bg-panel px-2 py-0.5 font-sans text-[11px] text-muted opacity-0 transition-opacity duration-150 hover:text-ink group-hover:opacity-100"
        >
          ↩ 引用到对话
        </button>
        {children}
      </section>
    ) : null
  return (
    <article className="mx-auto max-w-[680px] px-8 py-10 font-serif text-[16.5px] leading-[1.85]">
      <h1 className="mb-6 text-[28px] leading-tight">教育的工资回报：来自大学邻近性的证据</h1>
      <S id="intro" label="引言">
        <h2 className="mb-1 text-xl">1 引言</h2>
        <p>教育能在多大程度上提高收入，是劳动经济学最基本的问题之一。简单比较高学历与低学历者的工资，会把能力、家庭背景的差异也算作教育的作用。本文使用 Card (1995) 的数据，先给出 OLS 基准，再以是否在大学附近长大作为教育的工具变量。</p>
      </S>
      <S id="table" label="表 1">
        <h2 className="mb-2 text-xl">4 结果</h2>
        <table className="mx-auto my-2 border-y border-ink/70 font-sans text-sm">
          <thead>
            <tr className="border-b border-ink/30 text-muted">
              <th className="px-4 py-1.5 text-left font-normal" />
              <th className="px-4 py-1.5 text-right font-normal">(1) OLS</th>
              {ivDone && <th className="pp-enter px-4 py-1.5 text-right font-normal">(2) IV</th>}
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="px-4 py-1.5">受教育年限</td>
              <td className="px-4 py-1.5 text-right font-mono">{fmt(OLS.coef)}{stars(OLS.p)}<div className="text-xs text-muted">({fmt(OLS.se)})</div></td>
              {ivDone && <td className="pp-enter px-4 py-1.5 text-right font-mono">{fmt(IV.coef)}{stars(IV.p)}<div className="text-xs text-muted">({fmt(IV.se)})</div></td>}
            </tr>
            <tr className="border-t border-ink/20 text-muted"><td className="px-4 py-1">N</td><td className="px-4 py-1 text-right">3,010</td>{ivDone && <td className="px-4 py-1 text-right">3,010</td>}</tr>
          </tbody>
        </table>
        {ivDone && <p className="pp-enter text-center font-sans text-xs text-muted">IV 第一阶段 F = {FIRST_STAGE.f}，工具强度中等，t 检验可能过度拒绝。</p>}
      </S>
      <S id="results" label="结果段">
        <p>控制工作经验、种族、城乡与 1966 年居住地区后，每多受一年教育，小时工资的对数约提高 0.075（约 7.5%），在 1% 水平上显著。{ivDone && <span className="pp-enter">以大学邻近性为工具的 IV 估计为 0.132，高于 OLS，但置信区间明显更宽。</span>}</p>
      </S>
      <S id="figure" label="图 1">
        <div className="rounded-md border border-border bg-panel p-4 font-sans text-xs text-muted">
          <div className="space-y-3">
            {[OLS, IV].map((r) => (
              <div key={r.method} className="flex items-center gap-3">
                <span className="w-8 text-ink">{r.method}</span>
                <div className="relative h-2 flex-1 rounded-full bg-ink/5">
                  <div
                    className="absolute top-0 h-2 rounded-full bg-accent/30"
                    style={{ left: `${Math.max(0, (r.coef - 1.96 * r.se) / 0.26) * 100}%`, width: `${((Math.min(0.26, r.coef + 1.96 * r.se) - Math.max(0, r.coef - 1.96 * r.se)) / 0.26) * 100}%` }}
                  />
                  <div className="absolute -top-0.5 h-3 w-3 -translate-x-1/2 rounded-full bg-accent" style={{ left: `${(r.coef / 0.26) * 100}%` }} />
                </div>
                <span className="w-14 text-right font-mono text-ink">{fmt(r.coef)}</span>
              </div>
            ))}
          </div>
          <p className="mt-3 text-center">图 1 · 估计值与 95% 置信区间（横轴 0–0.26）</p>
        </div>
      </S>
    </article>
  )
}

function Notebook({ sections, ivDone }: { sections: Section[]; ivDone: boolean }) {
  const cells: { code: string; out: string }[] = [{ code: 'import pandas as pd\nimport statspai\ndf = pd.read_csv("data_card1995.csv")\ndf.shape', out: '(3010, 34)' }]
  if (sections.includes('table')) cells.push({ code: `ols = ${OLS.code}`, out: `educ  ${fmt(OLS.coef)}  (${fmt(OLS.se)})  n=3010` })
  if (ivDone) cells.push({ code: `iv = ${IV.code}`, out: `educ  ${fmt(IV.coef)}  (${fmt(IV.se)})\nfirst-stage F = ${FIRST_STAGE.f}  effective F = ${FIRST_STAGE.fEff}` })
  return (
    <div className="mx-auto max-w-[760px] space-y-4 px-8 py-10">
      {cells.map((c, i) => (
        <div key={i} className="pp-enter overflow-hidden rounded-lg border border-border bg-panel font-mono text-[12px] leading-5">
          <div className="flex">
            <span className="w-10 shrink-0 border-r border-border py-2 text-center text-muted">[{i + 1}]</span>
            <pre className="overflow-x-auto px-3 py-2">{c.code}</pre>
          </div>
          <pre className="border-t border-border bg-cream px-3 py-2 pl-[52px] text-muted">{c.out}</pre>
        </div>
      ))}
    </div>
  )
}
