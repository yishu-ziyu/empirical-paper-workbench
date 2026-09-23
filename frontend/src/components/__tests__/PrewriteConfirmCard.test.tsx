// R6 + R8: the estimate entry consumes the #40 tri-state permission and names
// the one thing it is still waiting for. Unknown never reads as passed, and a
// forbid never opens the entry.
import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'

import PrewriteConfirmCard from '../PrewriteConfirmCard'
import { I18nProvider } from '../../lib/i18n'

const TABLE1 = {
  produced_by: 'prewrite_preview',
  columns: ['variable', 'count'],
  rows: [{ variable: 'income', count: 5 }],
  n: 5,
}

function renderCard(props: Partial<React.ComponentProps<typeof PrewriteConfirmCard>> = {}) {
  const onConfirmTable1 = vi.fn()
  const onConfirmSpec = vi.fn()
  const onStartEstimate = vi.fn()
  const onConfirmRisk = vi.fn()
  render(
    <I18nProvider>
      <PrewriteConfirmCard
        table1={TABLE1}
        specificationEquation="income = β₀ + β₁ age + ε"
        table1Confirmed={false}
        specConfirmed={false}
        blockingDecision={null}
        confirmBusy={null}
        confirmError={null}
        estimateStarting={false}
        awaitingEstimate
        estimateComplete={false}
        continuePermission="allow"
        riskConfirmed={false}
        onConfirmTable1={onConfirmTable1}
        onConfirmSpec={onConfirmSpec}
        onStartEstimate={onStartEstimate}
        onConfirmRisk={onConfirmRisk}
        {...props}
      />
    </I18nProvider>,
  )
  return { onConfirmTable1, onConfirmSpec, onStartEstimate, onConfirmRisk }
}

const BOTH_CONFIRMED = { table1Confirmed: true, specConfirmed: true }

describe('PrewriteConfirmCard — the sample confirmation comes first', () => {
  it('waits for the sample confirmation before the setting confirmation', () => {
    renderCard()
    expect(screen.getByTestId('confirm-spec-btn')).toBeDisabled()
  })
})

describe('PrewriteConfirmCard — #40 permission tri-state (R6)', () => {
  it('asks for a risk decision when the permission is confirm', () => {
    const { onConfirmRisk } = renderCard({
      continuePermission: 'confirm',
      ...BOTH_CONFIRMED,
    })
    const riskBtn = screen.getByTestId('confirm-risk-btn')
    expect(riskBtn).toBeInTheDocument()
    expect(screen.getByTestId('risk-flag')).toHaveTextContent('未')
    expect(screen.getByTestId('start-estimate-btn')).toBeDisabled()
    expect(screen.getByTestId('prewrite-start-reason')).toHaveTextContent('风险')

    fireEvent.click(riskBtn)
    expect(onConfirmRisk).toHaveBeenCalled()
  })

  it('opens the estimate only after the risk decision came back', () => {
    renderCard({ continuePermission: 'confirm', riskConfirmed: true, ...BOTH_CONFIRMED })
    expect(screen.getByTestId('risk-flag')).toHaveTextContent('已作出风险决定')
    expect(screen.getByTestId('start-estimate-btn')).toBeEnabled()
  })

  it('never opens the estimate when the permission is forbid', () => {
    const { onStartEstimate } = renderCard({
      continuePermission: 'forbid',
      ...BOTH_CONFIRMED,
    })
    const start = screen.getByTestId('start-estimate-btn')
    expect(start).toBeDisabled()
    expect(screen.getByTestId('prewrite-forbid-reason')).toBeInTheDocument()
    expect(screen.queryByTestId('confirm-risk-btn')).not.toBeInTheDocument()
    fireEvent.click(start)
    expect(onStartEstimate).not.toHaveBeenCalled()
  })

  it('adds no gate of its own for allow', () => {
    renderCard({ continuePermission: 'allow', ...BOTH_CONFIRMED })
    expect(screen.queryByTestId('confirm-risk-btn')).not.toBeInTheDocument()
    expect(screen.getByTestId('start-estimate-btn')).toBeEnabled()
  })

  it('does not read an unknown permission as passed', () => {
    renderCard({ continuePermission: 'unknown', ...BOTH_CONFIRMED })
    const note = screen.getByTestId('prewrite-permission-note')
    expect(note.textContent).toContain('尚未')
    expect(screen.getByTestId('prewrite-confirm').textContent).not.toContain('核查已通过')
    expect(screen.queryByTestId('confirm-risk-btn')).not.toBeInTheDocument()
    expect(screen.getByTestId('start-estimate-btn')).toBeEnabled()
  })
})

describe('PrewriteConfirmCard — honest wording (R8)', () => {
  it('states known facts instead of announcing a passed check', () => {
    renderCard({ continuePermission: 'allow' })
    const text = screen.getByTestId('prewrite-confirm').textContent || ''
    expect(text).not.toContain('方向核查已通过')
    expect(text).not.toContain('核查已通过')
    expect(text).toContain('样本')
  })

  it('reports the forbid reason from the permission, not from the block decision', () => {
    renderCard({ continuePermission: 'forbid', ...BOTH_CONFIRMED })
    expect(screen.getByTestId('prewrite-forbid-reason').textContent).not.toBe('')
  })
})
