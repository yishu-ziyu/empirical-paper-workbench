import { describe, test, expect, vi } from 'vitest'
import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { I18nProvider } from '../../lib/i18n'
import JourneyTimeline from '../JourneyTimeline'
import type { JourneyTimelineProps } from '../JourneyTimeline'
import type { JourneyStage } from '../../types/journey'

const baseProps: JourneyTimelineProps = {
  sessionId: 'test-sess-123',
  currentStage: 0,
  stages: [
    { status: 'active', canIntervene: true },   // 0: topic
    { status: 'pending', canIntervene: false }, // 1: lit review
    { status: 'pending', canIntervene: true },   // 2: data
    { status: 'pending', canIntervene: true },   // 3: identification
    { status: 'pending', canIntervene: false },  // 4: estimation
    { status: 'pending', canIntervene: true },   // 5: robustness
    { status: 'pending', canIntervene: true },   // 6: writing
    { status: 'pending', canIntervene: false },  // 7: export
  ],
}

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

describe('JourneyTimeline 8阶段研究旅程（收敛版）', () => {
  test('渲染全部8个阶段，每个都有 data-testid', () => {
    renderWithI18n(<JourneyTimeline {...baseProps} />)
    for (let i = 0; i < 8; i++) {
      expect(screen.getByTestId(`journey-stage-${i}`)).toBeInTheDocument()
    }
  })

  test('active阶段（当前站）应有蓝色背景和文本', () => {
    renderWithI18n(<JourneyTimeline {...baseProps} />)
    const activeStage = screen.getByTestId('journey-stage-0')
    expect(activeStage.className).toContain('bg-paper')
    const titleEl = within(activeStage).getByText(/①/)
    expect(titleEl.className).toContain('text-accent')
  })

  test('completed阶段是绿色背景文本', () => {
    const props = {
      ...baseProps,
      currentStage: 1,
      stages: baseProps.stages.map((s, i): JourneyStage => ({
        ...s,
        status: i === 0 ? 'completed' : s.status,
      })),
    }
    renderWithI18n(<JourneyTimeline {...props} />)
    const completedStage = screen.getByTestId('journey-stage-0')
    expect(completedStage.className).toContain('bg-panel')
    const titleEl = within(completedStage).getByText(/①/)
    expect(titleEl.className).toContain('text-ink')
  })

  test('interrupt暂停阶段是黄色背景文本', () => {
    const props = {
      ...baseProps,
      currentStage: 0,
      stages: baseProps.stages.map((s, i): JourneyStage => ({
        ...s,
        status: i === 0 ? 'interrupt' : s.status,
      })),
    }
    renderWithI18n(<JourneyTimeline {...props} />)
    const interruptStage = screen.getByTestId('journey-stage-0')
    expect(interruptStage.className).toContain('bg-paper')
    const titleEl = within(interruptStage).getByText(/①/)
    expect(titleEl.className).toContain('text-accent')
  })

  test('pending阶段是灰色（muted）文本', () => {
    renderWithI18n(<JourneyTimeline {...baseProps} />)
    const pendingStage = screen.getByTestId('journey-stage-1')
    const titleEl = within(pendingStage).getByText(/②/)
    expect(titleEl.className).toContain('text-muted')
  })

  test('canIntervene为true时显示可介入徽标（核心5站）', () => {
    renderWithI18n(<JourneyTimeline {...baseProps} />)
    // 5 stations are intervenable in base props
    const badges = screen.getAllByText(/可介入|Intervene/)
    expect(badges).toHaveLength(5)
    // At least one badge is present
    expect(badges[0]).toBeInTheDocument()
  })

  test('点击卡片展开显示描述文本，再次点击折叠', async () => {
    const user = userEvent.setup()
    renderWithI18n(<JourneyTimeline {...baseProps} />)
    const stage0 = screen.getByTestId('journey-stage-0')
    // 初始折叠，描述不可见
    expect(stage0.textContent).not.toContain('四问')
    // 点击展开 → 描述文本出现
    await user.click(stage0)
    expect(stage0.textContent).toContain('四问')
    // 再次点击折叠 → 描述文本消失
    await user.click(stage0)
    expect(stage0.textContent).not.toContain('四问')
  })

  test('点击卡片触发 onStageClick 回调', async () => {
    const user = userEvent.setup()
    const onStageClick = vi.fn()
    renderWithI18n(<JourneyTimeline {...baseProps} onStageClick={onStageClick} />)
    await user.click(screen.getByTestId('journey-stage-3'))
    expect(onStageClick).toHaveBeenCalledWith(3)
  })

  test('sessionId为null时仍渲染旅程', () => {
    renderWithI18n(<JourneyTimeline {...baseProps} sessionId={null} />)
    expect(screen.getByTestId('journey-stage-0')).toBeInTheDocument()
  })
})
