import { useEffect, useRef, useState } from 'react'
import type { RefObject } from 'react'
import type { ResizableWorkspaceHandle } from './ResizableWorkspace'

export interface ReadingFocusProps {
  enabled: boolean
  workspaceRef: RefObject<ResizableWorkspaceHandle>
}

const READING_NOTICE_MS = 2 * 60 * 1000
const CAPSULE_DELAY_MS = 8 * 1000

/**
 * 阅读提示只在论文页连续停留后出现，不修改任何研究状态。
 * 进入专注阅读必须由用户点击；提示自身八秒无人操作后收成胶囊。
 */
export default function ReadingFocus({ enabled, workspaceRef }: ReadingFocusProps) {
  const [promptVisible, setPromptVisible] = useState(false)
  const [capsuleVisible, setCapsuleVisible] = useState(false)
  const [engaged, setEngaged] = useState(false)
  const engagedRef = useRef(false)
  const capsuleTimer = useRef<number | null>(null)

  useEffect(() => {
    const workspace = workspaceRef.current
    if (!enabled) {
      if (engagedRef.current) workspace?.expandSides()
      engagedRef.current = false
      setPromptVisible(false)
      setCapsuleVisible(false)
      setEngaged(false)
      if (capsuleTimer.current !== null) window.clearTimeout(capsuleTimer.current)
      capsuleTimer.current = null
      return
    }

    const noticeTimer = window.setTimeout(() => setPromptVisible(true), READING_NOTICE_MS)
    return () => {
      window.clearTimeout(noticeTimer)
      if (capsuleTimer.current !== null) window.clearTimeout(capsuleTimer.current)
      capsuleTimer.current = null
      if (engagedRef.current) workspace?.expandSides()
      engagedRef.current = false
    }
  }, [enabled, workspaceRef])

  useEffect(() => {
    if (!enabled || !promptVisible || capsuleVisible) return
    capsuleTimer.current = window.setTimeout(() => setCapsuleVisible(true), CAPSULE_DELAY_MS)
    return () => {
      if (capsuleTimer.current !== null) window.clearTimeout(capsuleTimer.current)
      capsuleTimer.current = null
    }
  }, [enabled, promptVisible, capsuleVisible])

  if (!enabled || (!promptVisible && !capsuleVisible && !engaged)) return null

  function enterFocus() {
    engagedRef.current = true
    setEngaged(true)
    workspaceRef.current?.collapseSides()
  }

  function restoreAll() {
    engagedRef.current = false
    setEngaged(false)
    setPromptVisible(false)
    setCapsuleVisible(false)
    workspaceRef.current?.expandSides()
  }

  function expandCapsule() {
    setCapsuleVisible(false)
    setPromptVisible(true)
    if (engaged) {
      engagedRef.current = false
      setEngaged(false)
      workspaceRef.current?.expandSides()
    }
  }

  function restoreLeft() {
    workspaceRef.current?.expandLeft()
  }

  function restoreRight() {
    workspaceRef.current?.expandRight()
  }

  return (
    <div data-testid="reading-focus" className="pointer-events-none fixed inset-x-0 bottom-4 z-40 flex justify-center px-4">
      <div className="flex w-full max-w-xl flex-col items-center gap-2">
        {capsuleVisible ? (
          <button
            type="button"
            data-testid="focus-reading-capsule"
            onClick={expandCapsule}
            className="pointer-events-auto rounded-full border border-border bg-panel px-4 py-2 text-xs text-ink shadow-lg transition-colors hover:bg-white"
          >
            专注阅读
          </button>
        ) : (
          <aside
            data-testid="focus-reading-prompt"
            role="status"
            className="pointer-events-auto w-full rounded-xl border border-border bg-panel px-4 py-3 shadow-lg"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="font-serif text-sm text-ink">要进入专注阅读吗？</p>
                <p className="mt-1 text-xs leading-5 text-muted">两侧栏会收起，论文仍保留在中栏。你的研究状态不会改变。</p>
              </div>
              <button
                type="button"
                data-testid="focus-reading-enter"
                onClick={enterFocus}
                className="rounded-full bg-ink px-3.5 py-1.5 text-xs text-white transition-opacity hover:opacity-90"
              >
                进入专注阅读
              </button>
            </div>
          </aside>
        )}

        {engaged || capsuleVisible ? (
          <div className="pointer-events-auto flex flex-wrap justify-center gap-2 text-[11px]">
            <button
              type="button"
              data-testid="focus-reading-open-left"
              onClick={restoreLeft}
              className="rounded-full border border-border bg-panel px-2.5 py-1 text-muted shadow-sm hover:text-ink"
            >
              恢复左栏
            </button>
            <button
              type="button"
              data-testid="focus-reading-open-right"
              onClick={restoreRight}
              className="rounded-full border border-border bg-panel px-2.5 py-1 text-muted shadow-sm hover:text-ink"
            >
              恢复右栏
            </button>
            <button
              type="button"
              data-testid="focus-reading-exit"
              onClick={restoreAll}
              className="rounded-full border border-border bg-panel px-2.5 py-1 text-muted shadow-sm hover:text-ink"
            >
              退出专注
            </button>
          </div>
        ) : null}
      </div>
    </div>
  )
}

export { CAPSULE_DELAY_MS, READING_NOTICE_MS }
