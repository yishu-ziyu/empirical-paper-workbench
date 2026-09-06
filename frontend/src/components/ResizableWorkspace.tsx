import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
  type CSSProperties,
  type ReactNode,
} from 'react'

export interface ResizableWorkspaceHandle {
  collapseSides: () => void
  expandSides: () => void
  expandLeft: () => void
  expandRight: () => void
}

export interface ResizableWorkspaceProps {
  left: ReactNode
  center: ReactNode
  right?: ReactNode
  storageKey: string
  leftDefault?: number
  leftMin?: number
  leftMax?: number
  rightDefault?: number
  rightMin?: number
  rightMax?: number
  className?: string
  leftClassName?: string
  centerClassName?: string
  rightClassName?: string
  testId?: string
  leftTestId?: string
  centerTestId?: string
  rightTestId?: string
}

type StoredLayout = {
  leftWidth?: number
  rightWidth?: number
  leftOpen?: boolean
  rightOpen?: boolean
}

type FocusLayout = StoredLayout & {
  compactPane: 'left' | 'right' | null
}

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value))
}

function readLayout(key: string): StoredLayout {
  try {
    return JSON.parse(localStorage.getItem(key) || '{}') as StoredLayout
  } catch {
    return {}
  }
}

const ResizableWorkspace = forwardRef<ResizableWorkspaceHandle, ResizableWorkspaceProps>(
  function ResizableWorkspace({
      left,
      center,
      right,
      storageKey,
      leftDefault = 224,
      leftMin = 176,
      leftMax = 360,
      rightDefault = 320,
      rightMin = 240,
      rightMax = 440,
      className = '',
      leftClassName = '',
      centerClassName = '',
      rightClassName = '',
      testId = 'resizable-workspace',
      leftTestId = 'workspace-left-panel',
      centerTestId = 'workspace-center-panel',
      rightTestId = 'workspace-right-panel',
    }, ref) {
    const initial = useRef(readLayout(storageKey)).current
    const [leftWidth, setLeftWidth] = useState(() =>
      clamp(initial.leftWidth ?? leftDefault, leftMin, leftMax),
    )
    const [rightWidth, setRightWidth] = useState(() =>
      clamp(initial.rightWidth ?? rightDefault, rightMin, rightMax),
    )
    const [leftOpen, setLeftOpen] = useState(initial.leftOpen ?? true)
    const [rightOpen, setRightOpen] = useState(initial.rightOpen ?? true)
    const [compact, setCompact] = useState(false)
    const [compactPane, setCompactPane] = useState<'left' | 'right' | null>(null)
    const compactRef = useRef(compact)
    const layoutRef = useRef<FocusLayout>({ leftOpen, rightOpen, compactPane })
    const focusLayoutRef = useRef<FocusLayout | null>(null)

    layoutRef.current = { leftOpen, rightOpen, compactPane }
    compactRef.current = compact

    useImperativeHandle(
      ref,
      () => ({
        collapseSides: () => {
          focusLayoutRef.current ??= layoutRef.current
          setLeftOpen(false)
          setRightOpen(false)
          setCompactPane(null)
        },
        expandSides: () => {
          const previous = focusLayoutRef.current
          setLeftOpen(previous?.leftOpen ?? true)
          setRightOpen(previous?.rightOpen ?? true)
          setCompactPane(previous?.compactPane ?? null)
          focusLayoutRef.current = null
        },
        expandLeft: () => {
          setLeftOpen(true)
          if (compactRef.current) setCompactPane('left')
        },
        expandRight: () => {
          setRightOpen(true)
          if (compactRef.current) setCompactPane('right')
        },
      }),
      [],
    )

    useEffect(() => {
      const media = window.matchMedia?.('(max-width: 900px)')
      if (!media) return
      const sync = () => {
        setCompact(media.matches)
        if (!media.matches) setCompactPane(null)
      }
      sync()
      media.addEventListener?.('change', sync)
      return () => media.removeEventListener?.('change', sync)
    }, [])

    useEffect(() => {
      localStorage.setItem(storageKey, JSON.stringify({ leftWidth, rightWidth, leftOpen, rightOpen }))
    }, [leftOpen, leftWidth, rightOpen, rightWidth, storageKey])

    function resizeWithKeyboard(side: 'left' | 'right', key: string) {
      if (key !== 'ArrowLeft' && key !== 'ArrowRight') return
      const direction = key === 'ArrowRight' ? 1 : -1
      if (side === 'left') setLeftWidth((value) => clamp(value + direction * 12, leftMin, leftMax))
      else setRightWidth((value) => clamp(value - direction * 12, rightMin, rightMax))
    }

    function startResize(side: 'left' | 'right', startX: number) {
      const startWidth = side === 'left' ? leftWidth : rightWidth
      const move = (event: PointerEvent) => {
        const delta = event.clientX - startX
        if (side === 'left') setLeftWidth(clamp(startWidth + delta, leftMin, leftMax))
        else setRightWidth(clamp(startWidth - delta, rightMin, rightMax))
      }
      const stop = () => {
        window.removeEventListener('pointermove', move)
        window.removeEventListener('pointerup', stop)
        document.body.style.cursor = ''
        document.body.style.userSelect = ''
      }
      document.body.style.cursor = 'col-resize'
      document.body.style.userSelect = 'none'
      window.addEventListener('pointermove', move)
      window.addEventListener('pointerup', stop, { once: true })
    }

    const paneStyle = (width: number): CSSProperties => ({ width, flexBasis: width })
    const leftVisible = compact ? compactPane === 'left' : leftOpen
    const rightVisible = compact ? compactPane === 'right' : rightOpen

    return (
      <main data-testid={testId} className={`relative flex min-h-0 min-w-0 overflow-hidden ${className}`}>
      {compact && compactPane && (
        <button
          type="button"
          aria-label="关闭侧栏"
          data-testid="workspace-backdrop"
          onClick={() => setCompactPane(null)}
          className="absolute inset-0 z-20 bg-black/10"
        />
      )}

      <aside
        data-testid={leftTestId}
        data-open={leftVisible}
        style={paneStyle(leftWidth)}
        className={`min-h-0 shrink-0 ${leftClassName} ${
          compact ? `absolute inset-y-0 left-0 z-30 shadow-xl ${leftVisible ? '' : 'hidden'}` : leftVisible ? '' : 'hidden'
        }`}
      >
        {left}
      </aside>

      {!compact && (
        <div className="group relative z-10 flex w-3 shrink-0 items-center justify-center border-r border-black/[0.05] bg-white/70">
          {leftOpen ? (
            <>
              <div
                role="separator"
                aria-label="调整左侧栏宽度"
                aria-orientation="vertical"
                aria-valuemin={leftMin}
                aria-valuemax={leftMax}
                aria-valuenow={leftWidth}
                tabIndex={0}
                data-testid="left-resize-handle"
                onPointerDown={(event) => startResize('left', event.clientX)}
                onKeyDown={(event) => resizeWithKeyboard('left', event.key)}
                className="absolute inset-y-0 left-0 w-3 cursor-col-resize"
              />
              <button
                type="button"
                aria-label="收起左侧栏"
                data-testid="left-collapse-btn"
                onClick={() => setLeftOpen(false)}
                className="relative rounded-full bg-white px-0.5 text-[11px] text-muted opacity-0 shadow-sm transition-opacity group-hover:opacity-100 focus:opacity-100"
              >
                ‹
              </button>
            </>
          ) : (
            <button
              type="button"
              aria-label="展开左侧栏"
              data-testid="left-expand-btn"
              onClick={() => setLeftOpen(true)}
              className="relative rounded-full bg-white px-0.5 text-[11px] text-muted shadow-sm"
            >
              ›
            </button>
          )}
        </div>
      )}

      <section data-testid={centerTestId} className={`min-h-0 min-w-0 flex-1 ${centerClassName}`}>
        {center}
      </section>

      {!compact && right != null && (
        <div className="group relative z-10 flex w-3 shrink-0 items-center justify-center border-l border-black/[0.05] bg-white/70">
          {rightOpen ? (
            <>
              <div
                role="separator"
                aria-label="调整右侧栏宽度"
                aria-orientation="vertical"
                aria-valuemin={rightMin}
                aria-valuemax={rightMax}
                aria-valuenow={rightWidth}
                tabIndex={0}
                data-testid="right-resize-handle"
                onPointerDown={(event) => startResize('right', event.clientX)}
                onKeyDown={(event) => resizeWithKeyboard('right', event.key)}
                className="absolute inset-y-0 left-0 w-3 cursor-col-resize"
              />
              <button
                type="button"
                aria-label="收起右侧栏"
                data-testid="right-collapse-btn"
                onClick={() => setRightOpen(false)}
                className="relative rounded-full bg-white px-0.5 text-[11px] text-muted opacity-0 shadow-sm transition-opacity group-hover:opacity-100 focus:opacity-100"
              >
                ›
              </button>
            </>
          ) : (
            <button
              type="button"
              aria-label="展开右侧栏"
              data-testid="right-expand-btn"
              onClick={() => setRightOpen(true)}
              className="relative rounded-full bg-white px-0.5 text-[11px] text-muted shadow-sm"
            >
              ‹
            </button>
          )}
        </div>
      )}

      {right != null && (
        <aside
          data-testid={rightTestId}
          data-open={rightVisible}
          style={paneStyle(rightWidth)}
          className={`min-h-0 shrink-0 ${rightClassName} ${
            compact ? `absolute inset-y-0 right-0 z-30 shadow-xl ${rightVisible ? '' : 'hidden'}` : rightVisible ? '' : 'hidden'
          }`}
        >
          {right}
        </aside>
      )}

      {compact && (
        <>
          <button
            type="button"
            aria-label={compactPane === 'left' ? '关闭左侧栏' : '打开左侧栏'}
            onClick={() => setCompactPane((pane) => (pane === 'left' ? null : 'left'))}
            className="absolute left-2 top-1/2 z-40 -translate-y-1/2 rounded-full border border-border bg-panel px-2.5 py-1 text-xs text-ink shadow-sm"
          >
            目录
          </button>
          {right != null && (
            <button
              type="button"
              aria-label={compactPane === 'right' ? '关闭右侧栏' : '打开右侧栏'}
              onClick={() => setCompactPane((pane) => (pane === 'right' ? null : 'right'))}
              className="absolute right-2 top-1/2 z-40 -translate-y-1/2 rounded-full border border-border bg-panel px-2.5 py-1 text-xs text-ink shadow-sm"
            >
              进度
            </button>
          )}
        </>
      )}
      </main>
    )
  },
)

ResizableWorkspace.displayName = 'ResizableWorkspace'

export default ResizableWorkspace
