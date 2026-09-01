// ApprovalBadge：只在 approved_forced=true 时显示"已绕过核对"徽标
import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import ApprovalBadge from '../ApprovalBadge'
import { I18nProvider } from '../../lib/i18n'
import type { components } from '../../types/api'

type Chapter = components['schemas']['ChapterResponse']

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

const base: Chapter = {
  type: 'intro',
  title: '引言',
  content: 'x',
  versions: [],
  generation_degraded: false,
  review_degraded: false,
  review_typed: false,
}

describe('ApprovalBadge 绕过核对徽标', () => {
  test('正常审批的章节不渲染徽标', () => {
    const { container } = renderWithI18n(<ApprovalBadge chapter={{ ...base, status: 'approved' }} />)
    expect(container.querySelector('[data-testid="approval-bypassed-badge"]')).toBeNull()
  })

  test('force 放行的章节渲染危险态徽标', () => {
    renderWithI18n(<ApprovalBadge chapter={{ ...base, status: 'approved', approved_forced: true }} />)
    const badge = screen.getByTestId('approval-bypassed-badge')
    expect(badge).toBeInTheDocument()
    expect(badge.className).toContain('text-danger')
  })
})
