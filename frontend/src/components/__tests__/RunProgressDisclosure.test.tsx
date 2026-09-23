import { describe, expect, test } from 'vitest'
import { render, screen } from '@testing-library/react'
import { I18nProvider } from '../../lib/i18n'
import {
  appendRunProgressEvent,
  createRunProgressState,
} from '../../lib/runSteps'
import RunProgressDisclosure from '../RunProgressDisclosure'
import type { RunProgressEvent } from '../../lib/runEvents'

const ev = (over: Partial<RunProgressEvent>): RunProgressEvent => ({
  type: 'run.progress',
  ...over,
})

function renderDisclosure(events: RunProgressEvent[]) {
  const owner = { sessionId: 'session-1', runId: 'run-1', kind: 'prewrite' }
  const progress = events.reduce(
    (state, event) => appendRunProgressEvent(state, owner, event),
    createRunProgressState(owner),
  )
  return render(
    <I18nProvider>
      <RunProgressDisclosure progress={progress} />
    </I18nProvider>,
  )
}

describe('RunProgressDisclosure', () => {
  test('没有真实事件时整块不出现', () => {
    renderDisclosure([])
    expect(screen.queryByTestId('run-progress-disclosure')).toBeNull()
    expect(screen.queryByTestId('run-progress-steps')).toBeNull()
  })

  test('只有非进度事件时也不出现', () => {
    renderDisclosure([ev({ type: 'run.accepted' }), ev({ type: 'run.succeeded' })])
    expect(screen.queryByTestId('run-progress-disclosure')).toBeNull()
  })

  test('默认折叠：路径是次级信息，用户主动展开才看', () => {
    renderDisclosure([ev({ node: 'run_estimate', status: 'started' })])
    const details = screen.getByTestId('run-progress-disclosure')
    expect(details.tagName).toBe('DETAILS')
    expect((details as HTMLDetailsElement).open).toBe(false)
  })

  test('一句当前动作来自真实事件的节点，不是写死的阶段名', () => {
    renderDisclosure([
      ev({ node: 'identification_verify', status: 'completed' }),
      ev({ node: 'run_estimate', status: 'started' }),
    ])
    expect(screen.getByTestId('run-progress-active')).toHaveTextContent('估计主结果')
  })

  test('步骤条数与真实不同节点数一致：不多出一个「假步骤」', () => {
    renderDisclosure([
      ev({ node: 'set_direction', status: 'completed' }),
      ev({ node: 'identification_verify', status: 'completed' }),
      ev({ node: 'run_estimate', status: 'started' }),
      ev({ node: 'run_estimate', status: 'completed' }),
    ])
    const steps = screen.getAllByTestId('run-progress-step')
    expect(steps).toHaveLength(3)
    expect(steps.map((s) => s.getAttribute('data-node'))).toEqual([
      'set_direction',
      'identification_verify',
      'run_estimate',
    ])
    expect(steps.map((s) => s.getAttribute('data-step-status'))).toEqual([
      'done',
      'done',
      'done',
    ])
  })

  test('被拦住时折叠摘要也明确写出，不靠琥珀色圆点暗示', () => {
    renderDisclosure([ev({ node: 'identification_verify', status: 'blocked' })])
    const step = screen.getByTestId('run-progress-step')
    expect(step).toHaveAttribute('data-step-status', 'blocked')
    expect(step).toHaveTextContent('被拦住')
    expect(screen.getByTestId('run-progress-active')).toHaveTextContent('核对识别策略 · 被拦住')
  })

  test('未知节点用诚实的用户文案，技术标识只留在展开详情', () => {
    renderDisclosure([ev({ node: 'legacy_node_x', status: 'started' })])
    expect(screen.getByTestId('run-progress-active')).toHaveTextContent('一个尚未命名的后台步骤')
    expect(screen.getByTestId('run-progress-step')).toHaveTextContent('legacy_node_x')
  })

  test('已收到的步骤都完成但 run 尚未终结时只说等待结果', () => {
    renderDisclosure([
      ev({ node: 'upload_data', status: 'completed' }),
      ev({ node: 'clean_data', status: 'completed' }),
    ])
    expect(screen.getByTestId('run-progress-active')).toHaveTextContent(
      '已收到的步骤完成，正在等待运行结果',
    )
    expect(screen.getByTestId('run-progress-active')).not.toHaveTextContent('这一步已完成')
  })

  test('页面里不出现百分比或倒计时', () => {
    renderDisclosure([
      ev({ node: 'run_estimate', status: 'started' }),
      ev({ node: 'search_literature', status: 'completed' }),
    ])
    const text = screen.getByTestId('run-progress-disclosure').textContent || ''
    expect(text).not.toMatch(/\d+\s*%/)
    expect(text).not.toMatch(/剩余|还剩|预计|倒计时|ETA/i)
  })
})
