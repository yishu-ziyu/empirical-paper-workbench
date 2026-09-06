import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react'
import { animate } from 'motion'
import { motion, useMotionValue } from 'motion/react'
import { AgentCursorProvider, useAgentCursor, type AgentCursorHost } from '../lib/agentCursor/context'
import { prefersReducedMotion } from '../lib/agentCursor/previewSpec'
import { travelDurationMs } from '../lib/agentCursor/player'
import { semanticTargetRegistry } from '../lib/agentCursor/registry'
import type { ResearchLab } from '../lib/workspace'

type HighlightBox = { id: string; left: number; top: number; width: number; height: number }

function boxesFor(ids: string[]): HighlightBox[] {
  const boxes: HighlightBox[] = []
  for (const id of ids) {
    try {
      const rect = semanticTargetRegistry.rect(id)
      if (!rect) continue
      boxes.push({
        id,
        left: rect.left,
        top: rect.top,
        width: Math.max(rect.width, 12),
        height: Math.max(rect.height, 12),
      })
    } catch {
      // overlay must not throw on a missing or invalid id
    }
  }
  return boxes
}

function moveCursorTo(
  x: ReturnType<typeof useMotionValue<number>>,
  y: ReturnType<typeof useMotionValue<number>>,
  opacity: ReturnType<typeof useMotionValue<number>>,
  el: Element,
  reduced: boolean,
): Promise<void> {
  if (typeof el.scrollIntoView === 'function') {
    el.scrollIntoView({ block: 'nearest', inline: 'nearest' })
  }
  const rect = el.getBoundingClientRect()
  const targetX = rect.left + rect.width / 2 - 6
  const targetY = Math.max(56, rect.top + rect.height / 2 - 6)
  const duration = travelDurationMs(reduced) / 1000
  opacity.set(1)
  if (reduced || duration <= 0) {
    x.set(targetX)
    y.set(targetY)
    return Promise.resolve()
  }
  return Promise.all([
    animate(x, targetX, { duration, ease: [0.23, 1, 0.32, 1] }),
    animate(y, targetY, { duration, ease: [0.23, 1, 0.32, 1] }),
  ]).then(() => undefined)
}

function AgentCursorOverlay() {
  const { presentation } = useAgentCursor()
  const [boxes, setBoxes] = useState<HighlightBox[]>([])

  const relayout = useCallback(() => {
    setBoxes(boxesFor(presentation.highlighted))
  }, [presentation.highlighted])

  useEffect(() => {
    if (presentation.highlighted.length === 0) {
      setBoxes((current) => (current.length === 0 ? current : []))
      return undefined
    }
    const onResize = () => relayout()
    window.addEventListener('resize', onResize)
    window.addEventListener('scroll', onResize, true)
    const unsub = semanticTargetRegistry.subscribe(onResize)
    relayout()
    return () => {
      window.removeEventListener('resize', onResize)
      window.removeEventListener('scroll', onResize, true)
      unsub()
    }
  }, [presentation.highlighted, relayout])

  const visible =
    presentation.status === 'running' ||
    presentation.status === 'paused' ||
    presentation.status === 'awaiting-confirm' ||
    presentation.status === 'done'

  return (
    <div
      data-testid="agent-cursor-layer"
      className="pointer-events-none fixed inset-0 z-[60]"
      aria-hidden={!visible}
    >
      {boxes.map((box) => (
        <div
          key={box.id}
          data-testid={`agent-cursor-highlight-${box.id}`}
          className="pointer-events-none absolute rounded-sm border border-wb-ink/35 bg-transparent"
          style={{
            left: box.left,
            top: box.top,
            width: box.width,
            height: box.height,
          }}
        />
      ))}
    </div>
  )
}

function AgentCursorPointer({
  x,
  y,
  opacity,
}: {
  x: ReturnType<typeof useMotionValue<number>>
  y: ReturnType<typeof useMotionValue<number>>
  opacity: ReturnType<typeof useMotionValue<number>>
}) {
  const { presentation } = useAgentCursor()
  const visible =
    presentation.status === 'running' ||
    presentation.status === 'paused' ||
    presentation.status === 'awaiting-confirm' ||
    presentation.status === 'done'
  const reduced = prefersReducedMotion()

  useEffect(() => {
    if (!visible) opacity.set(0)
  }, [opacity, visible])

  return (
    <motion.div
      data-testid="agent-cursor"
      data-reduced-motion={reduced ? 'true' : 'false'}
      className="pointer-events-none fixed left-0 top-0 z-[61]"
      style={{ x, y, opacity }}
    >
      <div className="flex items-start gap-2">
        <span
          aria-hidden
          className="mt-0.5 h-2.5 w-2.5 rotate-45 border border-wb-ink bg-wb-surface"
        />
        <div className="max-w-[16rem] rounded-md border border-wb-line bg-wb-surface px-2 py-1 shadow-sm">
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">Agent</p>
          {presentation.intent ? (
            <p data-testid="agent-cursor-intent" className="text-[12px] leading-4 text-wb-ink">
              {presentation.intent}
            </p>
          ) : (
            <p className="text-[12px] leading-4 text-wb-muted">Looking</p>
          )}
          {presentation.intentZh ? (
            <p className="text-[11px] leading-4 text-wb-muted">{presentation.intentZh}</p>
          ) : null}
        </div>
      </div>
    </motion.div>
  )
}

export default function AgentCursorRoot({
  workbenchTab,
  research,
  onOpenEvidence,
  onRunPreview,
  onPromote,
  children,
}: {
  workbenchTab: string
  research: ResearchLab | null | undefined
  onOpenEvidence: () => void
  onRunPreview: (specId: string) => Promise<void>
  onPromote?: () => Promise<void>
  children: ReactNode
}) {
  const x = useMotionValue(24)
  const y = useMotionValue(96)
  const opacity = useMotionValue(0)
  const activeTargetRef = useRef<Element | null>(null)

  const moveTo = useCallback<AgentCursorHost['moveTo']>(
    (el, opts) => {
      activeTargetRef.current = el
      return moveCursorTo(x, y, opacity, el, opts.reduced)
    },
    [opacity, x, y],
  )

  useEffect(() => {
    const handleScrollOrResize = () => {
      const el = activeTargetRef.current
      if (!el || !document.body.contains(el)) return
      const rect = el.getBoundingClientRect()
      const targetX = rect.left + rect.width / 2 - 6
      const targetY = Math.max(56, rect.top + rect.height / 2 - 6)
      x.set(targetX)
      y.set(targetY)
    }
    window.addEventListener('scroll', handleScrollOrResize, true)
    window.addEventListener('resize', handleScrollOrResize)
    return () => {
      window.removeEventListener('scroll', handleScrollOrResize, true)
      window.removeEventListener('resize', handleScrollOrResize)
    }
  }, [x, y])

  return (
    <AgentCursorProvider
      host={{
        workbenchTab,
        research,
        onOpenEvidence,
        onRunPreview,
        onPromote,
        moveTo,
      }}
    >
      {children}
      <AgentCursorOverlay />
      <AgentCursorPointer x={x} y={y} opacity={opacity} />
    </AgentCursorProvider>
  )
}
