import { describe, expect, test, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, act } from '@testing-library/react'
import type { Ref } from 'react'
import AgentCursorRoot from '../AgentCursorLayer'
import { useSemanticTarget } from '../../lib/agentCursor/useSemanticTarget'
import { semanticTargetRegistry } from '../../lib/agentCursor/registry'
import { useAgentCursor } from '../../lib/agentCursor/context'
import { travelDurationMs } from '../../lib/agentCursor/player'

function Target({ id }: { id: string }) {
  const ref = useSemanticTarget(id)
  return (
    <div ref={ref as Ref<HTMLDivElement>} data-semantic-id={id} data-testid={id}>
      {id}
    </div>
  )
}

function Controls() {
  const { playShowMe, cancel, replay, resume, presentation } = useAgentCursor()
  return (
    <div>
      <button type="button" data-testid="agent-cursor-show-me" data-agent-cursor-control="" onClick={playShowMe}>
        Show me
      </button>
      <button type="button" data-testid="agent-cursor-cancel" data-agent-cursor-control="" onClick={cancel}>
        Cancel
      </button>
      <button type="button" data-testid="agent-cursor-replay" data-agent-cursor-control="" onClick={replay}>
        Replay
      </button>
      <button type="button" data-testid="agent-cursor-resume" data-agent-cursor-control="" onClick={resume}>
        Resume
      </button>
      <span data-testid="cursor-status">{presentation.status}</span>
      <span data-testid="cursor-highlight-count">{presentation.highlighted.length}</span>
    </div>
  )
}

describe('AgentCursorLayer', () => {
  beforeEach(() => {
    semanticTargetRegistry.clear()
  })
  afterEach(() => {
    semanticTargetRegistry.clear()
  })

  test('mounts overlay with pointer-events none and Agent identity', () => {
    render(
      <AgentCursorRoot
        workbenchTab="evidence"
        research={null}
        onOpenEvidence={vi.fn()}
        onRunPreview={vi.fn(async () => undefined)}
      >
        <Target id="evidence.spec.ols" />
        <Controls />
      </AgentCursorRoot>,
    )
    const layer = screen.getByTestId('agent-cursor-layer')
    expect(layer).toHaveClass('pointer-events-none')
    expect(screen.getByTestId('agent-cursor')).toHaveClass('pointer-events-none')
    expect(screen.getByTestId('agent-cursor')).toHaveTextContent('Agent')
  })

  test('Show me / cancel / replay are available', () => {
    render(
      <AgentCursorRoot
        workbenchTab="evidence"
        research={null}
        onOpenEvidence={vi.fn()}
        onRunPreview={vi.fn(async () => undefined)}
      >
        <Target id="evidence.spec.ols" />
        <Target id="evidence.spec.iv" />
        <Target id="evidence.choice.estimator" />
        <Controls />
      </AgentCursorRoot>,
    )
    fireEvent.click(screen.getByTestId('agent-cursor-show-me'))
    fireEvent.click(screen.getByTestId('agent-cursor-cancel'))
    expect(screen.getByTestId('cursor-status')).toHaveTextContent('idle')
    fireEvent.click(screen.getByTestId('agent-cursor-replay'))
  })

  test('reduced-motion attribute path exists', () => {
    const restore = window.matchMedia
    window.matchMedia = ((query: string) =>
      ({
        matches: query.includes('prefers-reduced-motion'),
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      }) as unknown as MediaQueryList)
    render(
      <AgentCursorRoot
        workbenchTab="evidence"
        research={null}
        onOpenEvidence={vi.fn()}
        onRunPreview={vi.fn(async () => undefined)}
      >
        <Controls />
      </AgentCursorRoot>,
    )
    expect(screen.getByTestId('agent-cursor')).toHaveAttribute('data-reduced-motion', 'true')
    expect(travelDurationMs(true)).toBe(0)
    window.matchMedia = restore
  })

  test('cursor clamps to y >= 56 to avoid sticky header clipping', async () => {
    render(
      <AgentCursorRoot
        workbenchTab="evidence"
        research={null}
        onOpenEvidence={vi.fn()}
        onRunPreview={vi.fn(async () => undefined)}
      >
        <Target id="evidence.spec.ols" />
        <Controls />
      </AgentCursorRoot>,
    )
    const targetEl = screen.getByTestId('evidence.spec.ols')
    targetEl.getBoundingClientRect = () => ({
      left: 100,
      top: 10,
      width: 20,
      height: 20,
      right: 120,
      bottom: 30,
      x: 100,
      y: 10,
      toJSON: () => {},
    })
    targetEl.scrollIntoView = vi.fn()
    fireEvent.click(screen.getByTestId('agent-cursor-show-me'))
    await vi.waitFor(() => {
      expect(targetEl.scrollIntoView).toHaveBeenCalledWith({ block: 'nearest', inline: 'nearest' })
    })
  })

  test('M3 full Show me finishes without hanging (<=6s of script time)', async () => {
    vi.useFakeTimers()
    try {
      render(
        <AgentCursorRoot
          workbenchTab="evidence"
          research={null}
          onOpenEvidence={vi.fn()}
          onRunPreview={vi.fn(async () => undefined)}
        >
          <Target id="evidence.spec.ols" />
          <Target id="evidence.spec.iv" />
          <Target id="evidence.choice.estimator" />
          <Controls />
        </AgentCursorRoot>,
      )
      fireEvent.click(screen.getByTestId('agent-cursor-show-me'))
      expect(screen.getByTestId('cursor-status')).toHaveTextContent('running')
      // 旧实现（motion thenable 永不 settle）即使时间推进也永远停在 running；
      // 修复后整个脚本 5720ms 内到达 done。
      await act(async () => {
        await vi.advanceTimersByTimeAsync(6000)
      })
      expect(screen.getByTestId('cursor-status')).toHaveTextContent('done')
    } finally {
      vi.useRealTimers()
    }
  })

  test('M3 reduced-motion completes the full script quickly', async () => {
    const restore = window.matchMedia
    window.matchMedia = ((query: string) =>
      ({
        matches: query.includes('prefers-reduced-motion'),
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      }) as unknown as MediaQueryList)
    vi.useFakeTimers()
    try {
      render(
        <AgentCursorRoot
          workbenchTab="evidence"
          research={null}
          onOpenEvidence={vi.fn()}
          onRunPreview={vi.fn(async () => undefined)}
        >
          <Target id="evidence.spec.ols" />
          <Target id="evidence.spec.iv" />
          <Target id="evidence.choice.estimator" />
          <Controls />
        </AgentCursorRoot>,
      )
      fireEvent.click(screen.getByTestId('agent-cursor-show-me'))
      await act(async () => {
        await vi.advanceTimersByTimeAsync(1200)
      })
      expect(screen.getByTestId('cursor-status')).toHaveTextContent('done')
      expect(screen.getByTestId('agent-cursor')).toHaveAttribute('data-reduced-motion', 'true')
    } finally {
      vi.useRealTimers()
      window.matchMedia = restore
    }
  })

  test('M3 cancel removes highlight boxes from the DOM (no layer residue)', async () => {
    vi.useFakeTimers()
    try {
      render(
        <AgentCursorRoot
          workbenchTab="evidence"
          research={null}
          onOpenEvidence={vi.fn()}
          onRunPreview={vi.fn(async () => undefined)}
        >
          <Target id="evidence.spec.ols" />
          <Target id="evidence.spec.iv" />
          <Target id="evidence.choice.estimator" />
          <Controls />
        </AgentCursorRoot>,
      )
      fireEvent.click(screen.getByTestId('agent-cursor-show-me'))
      await act(async () => {
        await vi.advanceTimersByTimeAsync(700)
      })
      // 运行中：第一个 point 目标有高亮方框
      expect(screen.getByTestId('agent-cursor-highlight-evidence.spec.ols')).toBeInTheDocument()
      fireEvent.click(screen.getByTestId('agent-cursor-cancel'))
      await act(async () => {
        await vi.advanceTimersByTimeAsync(50)
      })
      expect(screen.getByTestId('cursor-status')).toHaveTextContent('idle')
      expect(screen.queryByTestId('agent-cursor-highlight-evidence.spec.ols')).not.toBeInTheDocument()
      expect(screen.queryByTestId('agent-cursor-highlight-evidence.spec.iv')).not.toBeInTheDocument()
      expect(screen.getByTestId('cursor-highlight-count')).toHaveTextContent('0')
    } finally {
      vi.useRealTimers()
    }
  })

  test('M3 pointerdown pauses mid-play and Resume continues to done', async () => {
    vi.useFakeTimers()
    try {
      render(
        <AgentCursorRoot
          workbenchTab="evidence"
          research={null}
          onOpenEvidence={vi.fn()}
          onRunPreview={vi.fn(async () => undefined)}
        >
          <Target id="evidence.spec.ols" />
          <Target id="evidence.spec.iv" />
          <Target id="evidence.choice.estimator" />
          <Controls />
        </AgentCursorRoot>,
      )
      fireEvent.click(screen.getByTestId('agent-cursor-show-me'))
      await act(async () => {
        await vi.advanceTimersByTimeAsync(700)
      })
      // 真实用户输入：非控件区域的 pointerdown 立即暂停
      fireEvent.pointerDown(document.body)
      expect(screen.getByTestId('cursor-status')).toHaveTextContent('paused')
      // 已暂停——继续：从当前步续播而非重播
      fireEvent.click(screen.getByTestId('agent-cursor-resume'))
      expect(screen.getByTestId('cursor-status')).toHaveTextContent('running')
      await act(async () => {
        await vi.advanceTimersByTimeAsync(6000)
      })
      expect(screen.getByTestId('cursor-status')).toHaveTextContent('done')
    } finally {
      vi.useRealTimers()
    }
  })
})
