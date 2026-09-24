import { useEffect, useRef, useState, type ReactNode } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import './riffs.css'
import { FIRST_STAGE, IV, OLS, ci, fmt, pct, stars, type Run } from './data'
import { useFollow, usePaper, useTicker, type BlockId, type Main, type Paper } from './usePaper'

// Riff · 专注 — Apple-style: the paper fills the screen; an island at the top morphs to show
// what the agent is doing; the block being rewritten glows; provenance slides in as a glass sheet.

const SANS = '-apple-system, BlinkMacSystemFont, "SF Pro Text", "PingFang SC", "Helvetica Neue", sans-serif'
const DISPLAY = '-apple-system, BlinkMacSystemFont, "SF Pro Display", "PingFang SC", sans-serif'
const spring = { type: 'spring' as const, stiffness: 420, damping: 34 }
const soft = { type: 'spring' as const, bounce: 0.18, duration: 0.55 }

export default function FocusRiff() {
  const p = usePaper({ bootStep: 320 })
  const [sheet, setSheet] = useState<{ run: Run; field: string } | null>(null)
  const [done, setDone] = useState<string | null>(null)
  const [elapsed, setElapsed] = useState(0)
  const prevDiff = useRef(p.diff)

  // island "done" beat after a diff is accepted
  useEffect(() => {
    if (prevDiff.current && !p.diff) {
      setDone(p.stale ? '已保留原稿' : '已更新到稿子')
      const t = window.setTimeout(() => setDone(null), 1600)
      prevDiff.current = p.diff
      return () => clearTimeout(t)
    }
    prevDiff.current = p.diff
  }, [p.diff, p.stale])

  useEffect(() => {
    if (!p.working) return setElapsed(0)
    const t0 = Date.now()
    const id = window.setInterval(() => setElapsed((Date.now() - t0) / 1000), 100)
    return () => clearInterval(id)
  }, [p.working])

  return (
    <div className="min-h-screen bg-[#fbfbfd] text-[#1d1d1f]" style={{ fontFamily: SANS }}>
      <Island working={p.working?.label ?? null} elapsed={elapsed} done={done} pending={!!p.diff} />

      <article className="mx-auto max-w-[700px] px-8 pb-56 pt-28">
        <motion.p initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={soft} className="text-[13px] font-medium text-[#6e6e73]">
          工作稿 · NLS Young Men 1976 · 3,010 人
        </motion.p>
        <motion.h1
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ ...soft, delay: 0.06 }}
          className="mt-2 text-[46px] font-semibold leading-[1.08] tracking-[-.025em]"
          style={{ fontFamily: DISPLAY }}
        >
          教育的工资回报
          <span className="block text-[#86868b]">来自大学邻近性的证据</span>
        </motion.h1>

        <Section p={p} id="intro" title="引言" note={1}>
          <p>教育能在多大程度上提高收入，是劳动经济学最基本的问题之一。{p.introText}本文先给出 OLS 基准，再以大学邻近性作为工具变量。</p>
        </Section>
        <Section p={p} id="data" title="数据">
          <p>
            样本来自全国青年男性追踪调查（NLS），使用 1976 年的工资与教育信息，共 <Token value={OLS.n} digits={0} onOpen={() => setSheet({ run: OLS, field: 'n' })} /> 个观测。
          </p>
        </Section>
        <Section p={p} id="strategy" title="实证策略" note={2}>
          <p>OLS 可能因能力等遗漏变量而有偏，因此以“是否在四年制大学附近长大”作为教育的工具变量。</p>
          {p.strategyExtra && <p className="mt-3">{p.strategyExtra}</p>}
        </Section>
        <Section p={p} id="table" title="结果" note={3}>
          <Tiles p={p} onOpen={(run) => setSheet({ run, field: 'coef' })} />
        </Section>
        <Section p={p} id="results">
          <p>
            {p.resultText}
            <span className="ml-1 text-[14px] text-[#6e6e73]">
              β̂ <Token value={p.shownRun.coef} stale={p.stale} onOpen={() => setSheet({ run: p.shownRun, field: 'coef' })} />
            </span>
          </p>
        </Section>
        <Section p={p} id="figure">
          <Forest p={p} />
        </Section>
        <Section p={p} id="discussion" title="结论">
          <p className="text-[#86868b]">还没写。在下面告诉它先起个头。</p>
        </Section>
      </article>

      <Toolbar p={p} />

      <AnimatePresence>{sheet && <Sheet key="sheet" {...sheet} onClose={() => setSheet(null)} />}</AnimatePresence>
    </div>
  )
}

/* ---------- island ---------- */

function Island({ working, elapsed, done, pending }: { working: string | null; elapsed: number; done: string | null; pending: boolean }) {
  const state = working ? 'working' : done ? 'done' : pending ? 'pending' : 'idle'
  return (
    <div className="pointer-events-none fixed left-1/2 top-3 z-40 -translate-x-1/2">
      <motion.div layout transition={spring} className="pointer-events-auto overflow-hidden rounded-[22px] bg-black text-white shadow-[0_8px_30px_rgba(0,0,0,.18)]" style={{ borderRadius: 22 }}>
        <AnimatePresence mode="popLayout" initial={false}>
          <motion.div
            key={state}
            initial={{ opacity: 0, scale: 0.92, filter: 'blur(4px)' }}
            animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
            exit={{ opacity: 0, scale: 0.92, filter: 'blur(4px)' }}
            transition={{ duration: 0.22, ease: [0.23, 1, 0.32, 1] }}
            className="flex items-center gap-3 whitespace-nowrap px-4"
            style={{ height: state === 'working' ? 52 : 36 }}
          >
            {state === 'idle' && (
              <>
                <span className="h-2 w-2 rounded-full bg-[#30d158]" />
                <span className="text-[13px] font-medium">教育的工资回报</span>
                <span className="text-[12px] text-white/50">v3</span>
              </>
            )}
            {state === 'working' && (
              <>
                <Ring />
                <span className="flex flex-col leading-tight">
                  <span className="text-[13.5px] font-medium">{working}</span>
                  <span className="text-[11.5px] text-white/55">agent 正在工作</span>
                </span>
                <span className="rf-tnum ml-6 font-mono text-[13px] text-white/70">{elapsed.toFixed(1)}s</span>
              </>
            )}
            {state === 'pending' && (
              <>
                <span className="h-2 w-2 rounded-full bg-[#ff9f0a]" />
                <span className="text-[13px] font-medium">有一处修改等你确认</span>
              </>
            )}
            {state === 'done' && (
              <>
                <motion.span initial={{ scale: 0.4 }} animate={{ scale: 1 }} transition={{ type: 'spring', bounce: 0.5, duration: 0.45 }} className="grid h-5 w-5 place-items-center rounded-full bg-[#30d158] text-[12px] text-black">
                  ✓
                </motion.span>
                <span className="text-[13px] font-medium">{done}</span>
              </>
            )}
          </motion.div>
        </AnimatePresence>
      </motion.div>
    </div>
  )
}

function Ring() {
  return (
    <svg width="22" height="22" viewBox="0 0 22 22" className="animate-spin [animation-duration:1.1s]">
      <circle cx="11" cy="11" r="8.5" fill="none" stroke="rgba(255,255,255,.18)" strokeWidth="2.5" />
      <circle cx="11" cy="11" r="8.5" fill="none" stroke="url(#ig)" strokeWidth="2.5" strokeLinecap="round" strokeDasharray="20 60" />
      <defs>
        <linearGradient id="ig" x1="0" x2="1">
          <stop offset="0" stopColor="#5ac8fa" />
          <stop offset="1" stopColor="#bf5af2" />
        </linearGradient>
      </defs>
    </svg>
  )
}

/* ---------- sections ---------- */

function Section({ p, id, title, note, children }: { p: Paper; id: BlockId; title?: string; note?: number; children: ReactNode }) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLElement>(null)
  const d = p.diff?.block === id ? p.diff : null
  const working = p.working?.block === id
  useFollow(ref, working || !!d)
  if (!p.isBooted(id)) return null
  const n = note ? p.notes.find((x) => x.id === note) : null
  return (
    <motion.section ref={ref} initial={{ opacity: 0, y: 18, scale: 0.99 }} animate={{ opacity: 1, y: 0, scale: 1 }} transition={soft} className="relative mt-12">
      {title && (
        <h2 className="mb-3 flex items-center gap-2 text-[24px] font-semibold tracking-[-.015em]" style={{ fontFamily: DISPLAY }}>
          {title}
          {n && (
            <button
              onClick={() => setOpen((o) => !o)}
              onMouseEnter={() => p.setFocusBlock(id)}
              onMouseLeave={() => p.setFocusBlock(null)}
              className="relative grid h-5 w-5 place-items-center"
              aria-label="审稿意见"
            >
              {n.status === 'open' && <span className="absolute h-5 w-5 animate-ping rounded-full bg-[#ff9f0a]/30 [animation-duration:2.4s]" />}
              <span className={`h-2.5 w-2.5 rounded-full ${n.status === 'open' ? 'bg-[#ff9f0a]' : 'bg-[#30d158]'}`} />
            </button>
          )}
        </h2>
      )}
      <AnimatePresence>
        {open && n && (
          <motion.div
            initial={{ opacity: 0, y: -6, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -4, scale: 0.98 }}
            transition={{ duration: 0.18, ease: [0.23, 1, 0.32, 1] }}
            className="mb-4 origin-top-left rounded-2xl bg-[#f5f5f7] p-4 text-[14px] leading-[1.6]"
          >
            <p className="text-[12px] font-medium text-[#ff9f0a]">审稿 · {n.tag}</p>
            <p className="mt-1">{n.text}</p>
            {n.status === 'open' ? (
              <button
                disabled={p.busy}
                onClick={() => {
                  setOpen(false)
                  p.fixNote(n)
                }}
                className="mt-3 rounded-full bg-[#1d1d1f] px-4 py-1.5 text-[13px] font-medium text-white transition-transform duration-100 active:scale-[.96] disabled:opacity-40"
              >
                {n.action}
              </button>
            ) : (
              <p className="mt-2 text-[13px] text-[#30d158]">已处理</p>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      <Glow on={working || !!d}>
        <div className={`text-[17px] leading-[1.8] transition-opacity duration-300 ${p.focusBlock === id ? 'opacity-100' : ''}`}>
          {d ? (
            <div>
              {d.before && <p className="text-[#86868b] line-through decoration-[#86868b]/50">{d.before}</p>}
              <motion.p initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={{ ...soft, delay: 0.15 }} className="ai-text mt-2">
                {d.after}
              </motion.p>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.35 }} className="mt-4 flex items-center gap-2 text-[13px]">
                <button onClick={p.acceptDiff} className="rounded-full bg-[#1d1d1f] px-4 py-1.5 font-medium text-white transition-transform duration-100 active:scale-[.96]">
                  使用新版本
                </button>
                <button onClick={p.rejectDiff} className="rounded-full bg-black/[.05] px-4 py-1.5 font-medium transition-transform duration-100 active:scale-[.96]">
                  保留原稿
                </button>
                <span className="ml-2 text-[#86868b]">{d.reason}</span>
              </motion.div>
            </div>
          ) : (
            children
          )}
        </div>
      </Glow>
    </motion.section>
  )
}

/** Apple-Intelligence-style edge glow around the block the agent is touching. */
function Glow({ on, children }: { on: boolean; children: ReactNode }) {
  return (
    <div className="relative">
      <AnimatePresence>
        {on && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
            className="pointer-events-none absolute -inset-x-5 -inset-y-4 overflow-hidden rounded-[22px]"
          >
            <div className="ai-spin absolute left-1/2 top-1/2 aspect-square w-[160%] -translate-x-1/2 -translate-y-1/2" />
            <div className="absolute inset-[2px] rounded-[20px] bg-[#fbfbfd]/[.94]" />
          </motion.div>
        )}
      </AnimatePresence>
      <AnimatePresence>
        {on && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 0.55 }} exit={{ opacity: 0 }} className="pointer-events-none absolute -inset-x-6 -inset-y-5 -z-10 overflow-hidden rounded-[26px] blur-xl">
            <div className="ai-spin absolute left-1/2 top-1/2 aspect-square w-[160%] -translate-x-1/2 -translate-y-1/2" />
          </motion.div>
        )}
      </AnimatePresence>
      <div className="relative">{children}</div>
    </div>
  )
}

function Token({ value, digits = 4, stale, onOpen }: { value: number; digits?: number; stale?: boolean; onOpen: () => void }) {
  const v = useTicker(value, { ms: 800 })
  return (
    <motion.button
      whileHover={{ scale: 1.04 }}
      whileTap={{ scale: 0.96 }}
      transition={spring}
      onClick={onOpen}
      className={`rf-tnum mx-0.5 inline-block rounded-full px-2 font-mono text-[.88em] ${stale ? 'bg-[#ff9f0a]/15 text-[#c93400] line-through' : 'bg-[#e8e8ed] text-[#1d1d1f] hover:bg-[#dedee5]'}`}
    >
      {digits ? v.toFixed(digits) : Math.round(v).toLocaleString()}
    </motion.button>
  )
}

function Tiles({ p, onOpen }: { p: Paper; onOpen: (r: Run) => void }) {
  return (
    <div className="grid grid-cols-2 gap-3">
      {[OLS, IV].map((r) => (
        <Tile key={r.method} run={r} on={p.main === r.method} onOpen={() => onOpen(r)} />
      ))}
      {p.tableNote && (
        <motion.p initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} transition={soft} className="col-span-2 rounded-2xl bg-[#f5f5f7] px-4 py-3 text-[13px] leading-[1.6] text-[#6e6e73]">
          第一阶段有效 F = {FIRST_STAGE.fEff}，介于 10 与 23.1 之间，IV 的 t 检验可能过度拒绝，结论宜谨慎。
        </motion.p>
      )}
    </div>
  )
}

function Tile({ run: r, on, onOpen }: { run: Run; on: boolean; onOpen: () => void }) {
  const v = useTicker(r.coef, { ms: 900 })
  const [lo, hi] = ci(r)
  return (
    <button onClick={onOpen} className="relative rounded-[22px] p-5 text-left">
      {on ? (
        <motion.span layoutId="main-tile" transition={soft} className="absolute inset-0 rounded-[22px] bg-white shadow-[0_2px_4px_rgba(0,0,0,.04),0_12px_32px_rgba(0,0,0,.08)]" />
      ) : (
        <span className="absolute inset-0 rounded-[22px] bg-[#f5f5f7]" />
      )}
      <span className="relative block">
        <span className="flex items-center gap-2 text-[13px] font-medium text-[#6e6e73]">
          {r.method === 'OLS' ? 'OLS 基准' : 'IV · nearc4'}
          {on && <span className="rounded-full bg-[#30d158]/15 px-2 text-[11px] text-[#248a3d]">主设定</span>}
        </span>
        <span className="rf-tnum mt-2 block text-[40px] font-semibold leading-none tracking-[-.02em]" style={{ fontFamily: DISPLAY }}>
          {v.toFixed(4)}
          <span className="ml-1 align-top text-[16px] text-[#86868b]">{stars(r.p)}</span>
        </span>
        <span className="mt-2 block text-[13px] text-[#6e6e73]">
          每多一年教育 ≈ +{pct(r.coef)} · SE {fmt(r.se)}
        </span>
        <span className="relative mt-4 block h-1.5 rounded-full bg-black/[.06]">
          <motion.span
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ ...soft, delay: 0.2 }}
            className="absolute top-0 h-1.5 origin-left rounded-full"
            style={{ left: `${(Math.max(lo, 0) / 0.26) * 100}%`, width: `${((hi - Math.max(lo, 0)) / 0.26) * 100}%`, background: on ? 'linear-gradient(90deg,#34c759,#30d158)' : '#c7c7cc' }}
          />
        </span>
        <span className="mt-1.5 block text-[11.5px] text-[#86868b]">
          95% 区间 [{fmt(Math.max(lo, 0), 3)}, {fmt(hi, 3)}]{r.method === 'IV' && ` · 第一阶段 F ${FIRST_STAGE.f}`}
        </span>
      </span>
    </button>
  )
}

function Forest({ p }: { p: Paper }) {
  return (
    <div className="rounded-[22px] bg-[#f5f5f7] p-6">
      <p className="text-[13px] font-medium text-[#6e6e73]">图 1 · 两种估计放在一起看</p>
      <div className="mt-5 space-y-5">
        {[OLS, IV].map((r, i) => {
          const [lo, hi] = ci(r)
          const on = p.main === r.method
          return (
            <div key={r.method} className="flex items-center gap-4">
              <span className={`w-10 text-[13px] font-medium ${on ? 'text-[#1d1d1f]' : 'text-[#86868b]'}`}>{r.method}</span>
              <div className="relative h-8 flex-1">
                <div className="absolute inset-y-[15px] left-0 right-0 rounded-full bg-black/[.05]" />
                <motion.div
                  initial={{ scaleX: 0, opacity: 0 }}
                  animate={{ scaleX: 1, opacity: 1 }}
                  transition={{ ...soft, delay: 0.1 + i * 0.12 }}
                  className="absolute inset-y-[13px] origin-left rounded-full"
                  style={{ left: `${(Math.max(lo, 0) / 0.26) * 100}%`, width: `${((hi - Math.max(lo, 0)) / 0.26) * 100}%`, background: on ? '#30d158' : '#c7c7cc' }}
                />
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: 'spring', bounce: 0.45, duration: 0.5, delay: 0.45 + i * 0.12 }}
                  className="absolute top-1/2 h-4 w-4 rounded-full border-[3px] bg-white"
                  style={{ left: `${(r.coef / 0.26) * 100}%`, x: '-50%', y: '-50%', borderColor: on ? '#30d158' : '#aeaeb2' }}
                />
              </div>
              <span className="rf-tnum w-14 text-right font-mono text-[13px]">{fmt(r.coef)}</span>
            </div>
          )
        })}
      </div>
      <div className="mt-2 flex justify-between pl-14 pr-[70px] text-[11px] text-[#86868b]">
        {[0, 0.05, 0.1, 0.15, 0.2, 0.25].map((t) => <span key={t}>{t.toFixed(2)}</span>)}
      </div>
    </div>
  )
}

/* ---------- toolbar + sheet ---------- */

function Toolbar({ p }: { p: Paper }) {
  const [text, setText] = useState('')
  const [notes, setNotes] = useState(false)
  return (
    <div className="fixed bottom-[76px] left-1/2 z-30 -translate-x-1/2">
      <AnimatePresence>
        {notes && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.98 }}
            transition={{ duration: 0.2, ease: [0.23, 1, 0.32, 1] }}
            className="absolute bottom-[62px] left-0 w-[380px] origin-bottom-left space-y-2 rounded-[24px] border border-white/70 bg-white/75 p-3 shadow-[0_20px_50px_rgba(0,0,0,.14)] backdrop-blur-2xl"
          >
            {p.notes.map((n) => (
              <div key={n.id} className={`rounded-2xl bg-white/80 p-3 text-[13px] leading-[1.55] ${n.status === 'resolved' ? 'opacity-50' : ''}`}>
                <p className="text-[11.5px] font-medium text-[#ff9f0a]">{n.tag}</p>
                <p>{n.text}</p>
                {n.status === 'open' && (
                  <button
                    disabled={p.busy}
                    onClick={() => {
                      setNotes(false)
                      p.fixNote(n)
                    }}
                    className="mt-2 rounded-full bg-[#1d1d1f] px-3 py-1 text-[12px] font-medium text-white active:scale-[.96] disabled:opacity-40"
                  >
                    {n.action}
                  </button>
                )}
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex items-center gap-2 rounded-full border border-white/70 bg-white/70 p-1.5 shadow-[0_10px_40px_rgba(0,0,0,.12)] backdrop-blur-2xl">
        <div className="relative flex rounded-full bg-black/[.06] p-0.5">
          {(['OLS', 'IV'] as Main[]).map((m) => (
            <button key={m} disabled={p.busy} onClick={() => p.switchMain(m)} className="relative z-10 w-14 py-1.5 text-[13px] font-medium disabled:cursor-not-allowed">
              {p.main === m && <motion.span layoutId="seg-thumb" transition={spring} className="absolute inset-0 -z-10 rounded-full bg-white shadow-[0_1px_3px_rgba(0,0,0,.12)]" />}
              {m}
            </button>
          ))}
        </div>
        <button onClick={() => setNotes((o) => !o)} className="flex items-center gap-1.5 rounded-full px-3 py-1.5 text-[13px] font-medium hover:bg-black/[.04] active:scale-[.96]">
          <span className="h-2 w-2 rounded-full bg-[#ff9f0a]" /> 审稿 {p.openNotes}
        </button>
        <form
          onSubmit={(e) => {
            e.preventDefault()
            p.command(text)
            setText('')
          }}
          className="flex items-center"
        >
          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={p.busy}
            placeholder={p.diff ? '先确认上面的修改' : '告诉它要做什么'}
            className="w-[260px] bg-transparent px-2 text-[14px] outline-none placeholder:text-[#86868b]"
          />
          <motion.button whileTap={{ scale: 0.9 }} type="submit" disabled={p.busy || !text.trim()} className="grid h-8 w-8 place-items-center rounded-full bg-[#1d1d1f] text-white disabled:opacity-25">
            ↑
          </motion.button>
        </form>
      </div>
    </div>
  )
}

function Sheet({ run, field, onClose }: { run: Run; field: string; onClose: () => void }) {
  return (
    <>
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }} className="fixed inset-0 z-40 bg-black/[.08]" onClick={onClose} />
      <motion.aside
        initial={{ x: 460, opacity: 0.6 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 460, opacity: 0.6 }}
        transition={soft}
        drag="x"
        dragConstraints={{ left: 0, right: 0 }}
        dragElastic={{ left: 0.05, right: 0.6 }}
        onDragEnd={(_, info) => {
          if (info.offset.x > 120 || info.velocity.x > 500) onClose()
        }}
        className="fixed bottom-3 right-3 top-3 z-50 w-[420px] cursor-grab overflow-y-auto rounded-[28px] border border-white/70 bg-white/80 p-6 shadow-[0_30px_80px_rgba(0,0,0,.2)] backdrop-blur-2xl active:cursor-grabbing"
      >
        <div className="mx-auto mb-5 h-1 w-9 rounded-full bg-black/15" />
        <p className="text-[12px] font-medium text-[#6e6e73]">这个数字从哪来 · {field}</p>
        <h3 className="mt-1 text-[24px] font-semibold tracking-[-.015em]" style={{ fontFamily: DISPLAY }}>{run.label}</h3>
        <div className="mt-5 grid grid-cols-3 gap-2">
          {[
            ['估计', fmt(run.coef)],
            ['标准误', fmt(run.se)],
            ['样本', run.n.toLocaleString()],
          ].map(([k, v]) => (
            <div key={k} className="rounded-2xl bg-[#f5f5f7] p-3">
              <p className="text-[11px] text-[#86868b]">{k}</p>
              <p className="rf-tnum mt-0.5 font-mono text-[15px] font-medium">{v}</p>
            </div>
          ))}
        </div>
        <p className="mt-5 text-[12px] font-medium text-[#6e6e73]">代码</p>
        <pre className="mt-2 overflow-x-auto rounded-2xl bg-[#1d1d1f] p-4 font-mono text-[11.5px] leading-[1.7] text-[#f5f5f7]">{run.code}</pre>
        <p className="mt-5 text-[12px] font-medium text-[#6e6e73]">运行</p>
        <div className="mt-2 space-y-1.5 text-[13px]">
          {[
            ['运行编号', run.id],
            ['时间', run.ranAt],
            ['标准误类型', run.cov],
          ].map(([k, v]) => (
            <div key={k} className="flex justify-between rounded-xl bg-[#f5f5f7] px-3 py-2">
              <span className="text-[#6e6e73]">{k}</span>
              <span className="font-mono">{v}</span>
            </div>
          ))}
        </div>
        <p className="mt-5 text-[11.5px] text-[#86868b]">向右拖或点空白处关闭</p>
      </motion.aside>
    </>
  )
}
