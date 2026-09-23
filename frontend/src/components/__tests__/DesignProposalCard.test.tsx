// R5: an approval names the draft revision the user is looking at. Unsaved
// edits cannot approve the previous draft, and a confirmed design keeps an
// explicit revision entry instead of becoming uneditable.
import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'

import DesignProposalCard from '../DesignProposalCard'
import { I18nProvider } from '../../lib/i18n'
import type { SessionDesign } from '../../lib/workspace'

function design(overrides: Partial<SessionDesign> = {}): SessionDesign {
  return {
    status: 'draft',
    confirmed: false,
    revision: 'draft-a',
    proposed_at: '2026-09-17T10:00:00Z',
    confirmed_at: null,
    source: { title: '教育年限与工资', question: '' },
    method: 'ols',
    outcome: 'income',
    treatment: 'schooling',
    controls: [],
    group: '',
    treated: '',
    period: '',
    time_col: '',
    id_col: '',
    first_treat_col: '',
    interactions: [],
    qType: 'average',
    heterogeneity_groups: [],
    catalog_entry_id: null,
    ...overrides,
  } as SessionDesign
}

function renderCard(props: Partial<React.ComponentProps<typeof DesignProposalCard>> = {}) {
  const onPropose = vi.fn()
  const onConfirm = vi.fn()
  render(
    <I18nProvider>
      <DesignProposalCard
        shapedQuestion="教育年限与工资"
        design={design()}
        proposing={false}
        confirming={false}
        error={null}
        onPropose={onPropose}
        onConfirm={onConfirm}
        {...props}
      />
    </I18nProvider>,
  )
  return { onPropose, onConfirm }
}

describe('DesignProposalCard — approving the version on screen (R5)', () => {
  it('cannot approve the previous draft after the title was edited', () => {
    const { onConfirm } = renderCard()
    fireEvent.change(screen.getByTestId('design-title-input'), {
      target: { value: '另一个问题 B' },
    })

    const confirmBtn = screen.getByTestId('design-confirm-btn')
    expect(confirmBtn).toBeDisabled()
    expect(screen.getByTestId('design-dirty-hint')).toBeInTheDocument()
    fireEvent.click(confirmBtn)
    expect(onConfirm).not.toHaveBeenCalled()
  })

  it('confirms the revision the user is looking at', () => {
    const { onConfirm } = renderCard()
    expect(screen.getByTestId('design-confirm-btn')).toBeEnabled()
    fireEvent.click(screen.getByTestId('design-confirm-btn'))
    expect(onConfirm).toHaveBeenCalledWith({ expectedRevision: 'draft-a' })
  })

  it('turns an unsaved edit into the saved draft before it can be confirmed', () => {
    const { onPropose, onConfirm } = renderCard()
    fireEvent.change(screen.getByTestId('design-title-input'), {
      target: { value: '另一个问题 B' },
    })
    fireEvent.click(screen.getByTestId('design-propose-btn'))

    expect(onPropose).toHaveBeenCalledWith('另一个问题 B', '', { revise: false })
    expect(onConfirm).not.toHaveBeenCalled()
  })

  it('keeps an explicit revision entry after the design was confirmed', () => {
    const { onPropose } = renderCard({
      design: design({ status: 'confirmed', confirmed: true, confirmed_at: '2026-09-17T10:05:00Z' }),
    })
    expect(screen.getByTestId('design-confirmed')).toBeInTheDocument()

    fireEvent.click(screen.getByTestId('design-revise-btn'))
    const input = screen.getByTestId('design-title-input')
    expect(input).toHaveValue('教育年限与工资')

    fireEvent.change(input, { target: { value: '教育年限与工资（修订）' } })
    fireEvent.click(screen.getByTestId('design-propose-btn'))
    expect(onPropose).toHaveBeenCalledWith('教育年限与工资（修订）', '', { revise: true })
  })

  it('lets the revision entry be dismissed without touching the design', () => {
    renderCard({
      design: design({ status: 'confirmed', confirmed: true, confirmed_at: '2026-09-17T10:05:00Z' }),
    })
    fireEvent.click(screen.getByTestId('design-revise-btn'))
    expect(screen.getByTestId('design-title-input')).toBeInTheDocument()
    fireEvent.click(screen.getByTestId('design-revise-cancel'))
    expect(screen.getByTestId('design-confirmed')).toBeInTheDocument()
  })
})
