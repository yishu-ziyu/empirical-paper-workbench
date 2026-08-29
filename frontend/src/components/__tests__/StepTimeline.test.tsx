import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import StepTimeline from '../StepTimeline'
import { I18nProvider } from '../../lib/i18n'

function renderTimeline(props: Partial<Parameters<typeof StepTimeline>[0]> = {}) {
  const base = {
    directionSummary: null,
    cleaningReport: null,
    estimate: null,
    estimateBusy: false,
    hasReadout: false,
    identFailed: false,
    outline: [],
    currentChapterIndex: -1,
    writtenChapters: [],
    writeBusy: false,
    ...props,
  }
  return render(
    <I18nProvider>
      <StepTimeline {...base} />
    </I18nProvider>,
  )
}

describe('StepTimeline 空桌步骤卡', () => {
  test('五张卡齐全，无数据时方向/清洗/估计为待运行', () => {
    renderTimeline({
      outline: [
        { type: 'intro', title: '引言' },
        { type: 'results', title: '实证结果' },
      ],
    })
    expect(screen.getByTestId('step-card-direction')).toBeInTheDocument()
    expect(screen.getByTestId('step-card-cleaning')).toBeInTheDocument()
    expect(screen.getByTestId('step-card-estimate')).toBeInTheDocument()
    expect(screen.getByTestId('step-card-chapter-intro')).toBeInTheDocument()
    // 门禁：无主表 ⇒ 结果章锁定
    expect(screen.getByText('没有主表，不能写这一章')).toBeInTheDocument()
  })

  test('估计卡：agent 跑通后显示迭代数，展开可见六段轮次摘要与最终代码', () => {
    renderTimeline({
      estimate: {
        status: 'ok',
        estimator: 'estimate_agent',
        iterations: 3,
        treatment_row: '| treat | 2.37 | 0.31 | 0.000 |',
        history_compact: '## Goal\n完成 did 估计',
        final_code: 'import statspai',
      },
    })
    const card = screen.getByTestId('step-card-estimate')
    expect(card.textContent).toContain('estimate_agent')
    expect(card.textContent).toContain('3')
    expect(screen.getByTestId('step-estimate-trace')).toBeInTheDocument()
    expect(screen.getByText(/## Goal/)).toBeInTheDocument()
    expect(screen.getByText(/import statspai/)).toBeInTheDocument()
  })

  test('清洗卡：8 步全成功显示 ✓，估计失败显示红字错误', () => {
    renderTimeline({
      cleaningReport: {
        steps: Array.from({ length: 8 }, (_, i) => ({ name: `s${i}`, status: 'success' })),
      },
      estimate: { status: 'error', error: '识别失败：处理变量无变异' },
    })
    expect(screen.getByText('8/8 ✓')).toBeInTheDocument()
    const est = screen.getByTestId('step-card-estimate')
    expect(est.textContent).toContain('识别失败：处理变量无变异')
  })
})
