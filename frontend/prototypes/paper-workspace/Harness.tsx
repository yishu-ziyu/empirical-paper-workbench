import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'
import './picker.css'
import NotebookVariant from './NotebookVariant'
import StudioRiff from './StudioRiff'
import PrintRiff from './PrintRiff'
import WorkbenchRiff from './WorkbenchRiff'
import FocusRiff from './FocusRiff'

// Round 3: 创作台 = 工作台 × 排印. Round 2: riffs on "论文即 notebook". Round 1 variants (ChatVariant, AutopilotVariant) stay on disk.
const VARIANTS = [
  { name: '创作台', Component: StudioRiff },
  { name: '工作台', Component: WorkbenchRiff },
  { name: '专注', Component: FocusRiff },
  { name: '排印纸面', Component: PrintRiff },
  { name: '原版', Component: NotebookVariant },
]

function initial() {
  const v = parseInt(new URLSearchParams(location.search).get('v') ?? '', 10)
  return v >= 1 && v <= VARIANTS.length ? v - 1 : 0
}

export default function Harness() {
  const [current, setCurrent] = useState(initial)
  const [mountKey, setMountKey] = useState(0)
  const [ready, setReady] = useState(false)
  const pickerRef = useRef<HTMLElement>(null)
  const highlightRef = useRef<HTMLSpanElement>(null)
  const itemRefs = useRef<(HTMLButtonElement | null)[]>([])

  const moveHighlight = useCallback(() => {
    const el = itemRefs.current[current]
    const hl = highlightRef.current
    if (!el || !hl) return
    hl.style.width = `${el.offsetWidth}px`
    hl.style.transform = `translateX(${el.offsetLeft}px)`
  }, [current])

  useLayoutEffect(moveHighlight, [moveHighlight])

  useEffect(() => {
    window.addEventListener('resize', moveHighlight)
    return () => window.removeEventListener('resize', moveHighlight)
  }, [moveHighlight])

  useEffect(() => {
    const id = requestAnimationFrame(() => requestAnimationFrame(() => setReady(true)))
    return () => cancelAnimationFrame(id)
  }, [])

  const setActive = useCallback((i: number) => {
    if (i < 0 || i >= VARIANTS.length) return
    setCurrent(i)
    setMountKey((k) => k + 1)
    const url = new URL(location.href)
    url.searchParams.set('v', String(i + 1))
    history.replaceState(null, '', url)
  }, [])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement
      if (/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.isContentEditable) return
      if (e.metaKey || e.ctrlKey || e.altKey) return
      const num = parseInt(e.key, 10)
      if (num >= 1 && num <= VARIANTS.length) setActive(num - 1)
      else if (e.key === 'ArrowRight') setActive((current + 1) % VARIANTS.length)
      else if (e.key === 'ArrowLeft') setActive((current - 1 + VARIANTS.length) % VARIANTS.length)
      else if (e.key === 'r' || e.key === 'R') setMountKey((k) => k + 1)
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [current, setActive])

  const { Component } = VARIANTS[current]

  return (
    <>
      <Component key={mountKey} />
      <nav
        ref={pickerRef}
        className="proto-picker"
        aria-label="Prototype variants"
        {...(ready ? { 'data-ready': '' } : {})}
      >
        <span ref={highlightRef} className="proto-picker-highlight" aria-hidden="true" />
        {VARIANTS.map((v, i) => (
          <button
            key={v.name}
            ref={(el) => {
              itemRefs.current[i] = el
            }}
            className="proto-picker-item"
            {...(i === current ? { 'data-active': '', 'aria-current': 'true' as const } : {})}
            onClick={() => setActive(i)}
          >
            {v.name}
          </button>
        ))}
        <span className="proto-picker-divider" aria-hidden="true" />
        <button
          className="proto-picker-item proto-picker-replay"
          aria-label="Replay animation (R)"
          onClick={() => setMountKey((k) => k + 1)}
        >
          ↻
        </button>
      </nav>
    </>
  )
}
