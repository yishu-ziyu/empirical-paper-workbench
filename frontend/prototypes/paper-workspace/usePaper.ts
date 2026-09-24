import { useEffect, useRef, useState, type RefObject } from 'react'
import { FIRST_STAGE, IV, OLS, type Run } from './data'

// Shared state + behaviour for the "paper is the notebook" riffs.
// Each riff only decides how this looks and moves.

export type Main = 'OLS' | 'IV'
export type BlockId = 'intro' | 'data' | 'strategy' | 'table' | 'results' | 'figure' | 'discussion'
export type Diff = { block: BlockId; before: string; after: string; reason: string; onAccept?: () => void; onReject?: () => void }
export type Note = { id: number; block: BlockId; tag: string; text: string; action: string; status: 'open' | 'resolved' }

export const RESULT_TEXT: Record<Main, string> = {
  OLS: '控制工作经验、种族、城乡与 1966 年居住地区后，每多受一年教育，小时工资的对数约提高 0.075（约 7.5%），在 1% 水平上显著。',
  IV: '以是否在四年制大学附近长大作为教育年限的工具变量，每多受一年教育，小时工资的对数约提高 0.132（约 13.2%），在 5% 水平上显著；估计值高于 OLS，但置信区间明显更宽。',
}
const RESULT_SHORT = '每多一年教育，小时工资约提高 7.5%（OLS，1% 水平显著）。'
export const INTRO_BEFORE = '已有研究普遍发现，教育的工资回报约为 10%，但这些估计可能混入了能力差异。'
const INTRO_AFTER = '已有研究发现教育与工资强相关；本文 OLS 估计约为 7.5%，但它可能混入了能力差异，因此还需要一个外生的教育变动来源。'
const EXCLUSION =
  '工具变量需要满足排他性：大学邻近性只通过教育影响工资。一个担忧是，靠近大学的地区本身工资更高或家庭背景更好；我们控制了 1966 年的城乡与地区虚拟变量来缓解这一点，但无法完全排除。'

export const INITIAL_NOTES: Note[] = [
  { id: 1, block: 'intro', tag: '一致性', text: '引言写“回报约为 10%”，但结果段的主估计是 7.5%。读者会以为两处说的是同一个数。', action: '改引言', status: 'open' },
  { id: 2, block: 'strategy', tag: '识别', text: '用了 nearc4 作工具，但没有讨论排他性：大学邻近性可能通过地区劳动力市场直接影响工资。', action: '补一段排他性讨论', status: 'open' },
  { id: 3, block: 'table', tag: '推断', text: `第一阶段 F = ${FIRST_STAGE.f}，高于 10 但低于 23.1，t 检验可能过度拒绝。建议在表注里说明。`, action: '加表注', status: 'open' },
]

// Order the paper "typesets" itself on first load.
export const BOOT_ORDER: BlockId[] = ['intro', 'data', 'strategy', 'table', 'results', 'figure', 'discussion']

export const reducedMotion = () =>
  typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

export function usePaper({ bootStep = 420 }: { bootStep?: number } = {}) {
  const [main, setMain] = useState<Main>('OLS')
  const [shown, setShown] = useState<Main>('OLS')
  const [resultText, setResultText] = useState(RESULT_TEXT.OLS)
  const [introText, setIntroText] = useState(INTRO_BEFORE)
  const [strategyExtra, setStrategyExtra] = useState<string | null>(null)
  const [tableNote, setTableNote] = useState(false)
  const [diff, setDiff] = useState<Diff | null>(null)
  const [notes, setNotes] = useState(INITIAL_NOTES)
  const [focusBlock, setFocusBlock] = useState<BlockId | null>(null)
  const [working, setWorking] = useState<{ block: BlockId; label: string } | null>(null)
  const [rerun, setRerun] = useState<BlockId | null>(null)
  // Bumps whenever a block's content is (re)computed, so riffs can replay draw-in motion.
  const [revision, setRevision] = useState<Partial<Record<BlockId, number>>>({})
  const [booted, setBooted] = useState(0)
  const timers = useRef<number[]>([])

  useEffect(() => {
    if (reducedMotion()) {
      setBooted(BOOT_ORDER.length)
      return
    }
    BOOT_ORDER.forEach((_, i) => {
      timers.current.push(window.setTimeout(() => setBooted(i + 1), 250 + i * bootStep))
    })
    const t = timers.current
    return () => t.forEach(clearTimeout)
  }, [bootStep])

  const isBooted = (b: BlockId) => BOOT_ORDER.indexOf(b) < booted
  const bump = (b: BlockId) => setRevision((r) => ({ ...r, [b]: (r[b] ?? 0) + 1 }))
  const shownRun: Run = shown === 'OLS' ? OLS : IV
  const stale = shown !== main
  const busy = !!diff || !!working

  function agent(block: BlockId, label: string, then: () => void, ms = 900) {
    setWorking({ block, label })
    window.setTimeout(() => {
      setWorking(null)
      then()
    }, ms)
  }

  function switchMain(next: Main) {
    if (next === main || busy) return
    const prev = main
    setMain(next)
    bump('table')
    bump('figure')
    agent('results', '重写结果段', () =>
      setDiff({
        block: 'results',
        before: resultText,
        after: RESULT_TEXT[next],
        reason: `主设定 ${prev} → ${next}，这段引用的数字已过时`,
        onAccept: () => setShown(next),
        onReject: () => {
          setMain(prev)
          bump('table')
          bump('figure')
        },
      }),
    )
  }

  function acceptDiff() {
    if (!diff) return
    if (diff.block === 'results') setResultText(diff.after)
    if (diff.block === 'intro') setIntroText(diff.after)
    if (diff.block === 'strategy') setStrategyExtra(diff.after)
    diff.onAccept?.()
    bump(diff.block)
    setDiff(null)
  }

  function rejectDiff() {
    diff?.onReject?.()
    setDiff(null)
  }

  function fixNote(n: Note) {
    if (busy) return
    const resolve = () => setNotes((ns) => ns.map((x) => (x.id === n.id ? { ...x, status: 'resolved' } : x)))
    setFocusBlock(n.block)
    if (n.id === 1)
      agent('intro', '改引言', () => setDiff({ block: 'intro', before: introText, after: INTRO_AFTER, reason: '审稿 · 一致性', onAccept: resolve }))
    if (n.id === 2)
      agent('strategy', '写排他性讨论', () => setDiff({ block: 'strategy', before: '', after: EXCLUSION, reason: '审稿 · 识别', onAccept: resolve }))
    if (n.id === 3)
      agent('table', '加表注', () => {
        setTableNote(true)
        resolve()
        bump('table')
      })
  }

  function doRerun(b: BlockId) {
    if (rerun) return
    setRerun(b)
    window.setTimeout(() => {
      setRerun(null)
      bump(b)
    }, 900)
  }

  function command(text: string) {
    if (!text.trim() || busy) return
    agent('results', '改结果段', () =>
      setDiff({ block: 'results', before: resultText, after: main === 'OLS' ? RESULT_SHORT : RESULT_TEXT.IV, reason: `“${text.trim()}”` }),
    )
  }

  return {
    main, shown, shownRun, stale, resultText, introText, strategyExtra, tableNote, diff, notes,
    focusBlock, setFocusBlock, working, rerun, revision, booted, isBooted, busy,
    switchMain, acceptDiff, rejectDiff, fixNote, doRerun, command,
    openNotes: notes.filter((n) => n.status === 'open').length,
  }
}

export type Paper = ReturnType<typeof usePaper>

/** Animate a number from its previous value to `value` (count-up on first show). */
export function useTicker(value: number, { ms = 650, from = 0, active = true } = {}) {
  const [display, setDisplay] = useState(active ? from : value)
  const prev = useRef(from)
  useEffect(() => {
    if (!active) return
    if (reducedMotion()) {
      setDisplay(value)
      prev.current = value
      return
    }
    const start = performance.now()
    const a = prev.current
    let raf = 0
    const step = (t: number) => {
      const k = Math.min(1, (t - start) / ms)
      const e = 1 - Math.pow(1 - k, 3)
      setDisplay(a + (value - a) * e)
      if (k < 1) raf = requestAnimationFrame(step)
      else prev.current = value
    }
    raf = requestAnimationFrame(step)
    return () => cancelAnimationFrame(raf)
  }, [value, ms, active])
  return display
}

/** Keep the block the agent is touching in view, so the process is actually seen. */
export function useFollow(ref: RefObject<HTMLElement | null>, active: boolean) {
  useEffect(() => {
    if (active) ref.current?.scrollIntoView({ block: 'center', behavior: reducedMotion() ? 'auto' : 'smooth' })
  }, [active, ref])
}
