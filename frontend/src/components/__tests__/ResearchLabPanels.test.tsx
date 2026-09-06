import { describe, expect, test, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { ExpectationEditor, SpecificationSpacePanel } from '../ResearchLabPanels'
import type { components } from '../../types/api'
import type { ResearchLab } from '../../lib/workspace'

type Expectation = NonNullable<ResearchLab['expectation']>
type ExpectationCriterion = components['schemas']['ExpectationCriterion']
type SavePayload = {
  text: string
  confidence: 'low' | 'medium' | 'high'
  criteria?: ExpectationCriterion[]
}

const seedExpectation: Expectation = {
  text: 'I expect OLS to be positive.',
  confidence: 'medium',
  version: 1,
  history: [],
  criteria: [
    {
      id: 'criterion.seed.iv-below-ols',
      kind: 'ordering',
      operator: 'lt',
      left: { metric: 'estimate.coef', estimator: 'iv', label: 'IV estimate' },
      right: { metric: 'estimate.coef', estimator: 'ols', label: 'OLS estimate' },
      label: 'IV estimate < OLS estimate',
      source: 'seed',
    },
  ],
}

function renderEditor(
  onSave: (payload: SavePayload) => Promise<void> = async () => undefined,
  expectation: Expectation = seedExpectation,
) {
  return render(<ExpectationEditor expectation={expectation} onSave={onSave} />)
}

describe('ExpectationEditor surprise criteria (M1)', () => {
  test('renders the explicit surprise condition block below the textarea', () => {
    renderEditor()
    expect(screen.getByTestId('expectation-criteria-block')).toHaveTextContent(
      'Surprise condition',
    )
    expect(screen.getByTestId('expectation-criterion')).toHaveTextContent(
      'IV estimate < OLS estimate',
    )
    expect(screen.getByTestId('expectation-criterion')).toHaveAttribute('data-source', 'seed')
  })

  test('editing the textarea text does not change the criterion block', () => {
    renderEditor()
    fireEvent.change(screen.getByRole('textbox'), {
      target: { value: '我觉得 IV 应该会更小一些，但并不确定。' },
    })
    expect(screen.getByTestId('expectation-criterion')).toHaveTextContent(
      'IV estimate < OLS estimate',
    )
    expect(screen.getByTestId('expectation-criterion-select')).toHaveValue('iv-lt-ols')
  })

  test('explicit control flips the criterion direction and submits it with the save', async () => {
    const onSave = vi.fn(async (_payload: SavePayload): Promise<void> => undefined)
    renderEditor(onSave)
    fireEvent.change(screen.getByTestId('expectation-criterion-select'), {
      target: { value: 'iv-gt-ols' },
    })
    expect(screen.getByTestId('expectation-criterion')).toHaveTextContent(
      'IV estimate > OLS estimate',
    )
    fireEvent.click(screen.getByRole('button', { name: 'Save expectation' }))
    await waitFor(() => expect(onSave).toHaveBeenCalledOnce())
    const payload = onSave.mock.calls[0]![0]
    expect(payload.criteria).toHaveLength(1)
    expect(payload.criteria![0]!.operator).toBe('gt')
    expect(payload.criteria![0]!.kind).toBe('ordering')
    expect(payload.criteria![0]!.source).toBe('user')
  })

  test('approx and sign options map to their criterion kinds', async () => {
    const onSave = vi.fn(async (_payload: SavePayload): Promise<void> => undefined)
    renderEditor(onSave)
    fireEvent.change(screen.getByTestId('expectation-criterion-select'), {
      target: { value: 'iv-approx-ols' },
    })
    expect(screen.getByTestId('expectation-criterion')).toHaveTextContent('IV estimate ≈ OLS')
    fireEvent.change(screen.getByTestId('expectation-criterion-select'), {
      target: { value: 'iv-positive' },
    })
    expect(screen.getByTestId('expectation-criterion')).toHaveTextContent(
      'IV estimate is positive',
    )
    fireEvent.click(screen.getByRole('button', { name: 'Save expectation' }))
    await waitFor(() => expect(onSave).toHaveBeenCalledOnce())
    const payload = onSave.mock.calls[0]![0]
    expect(payload.criteria![0]!.kind).toBe('sign')
    expect(payload.criteria![0]!.operator).toBe('positive')
  })

  test('save failure shows an in-editor error and keeps the draft text; retry succeeds', async () => {
    let attempts = 0
    const onSave = vi.fn(async (_payload: SavePayload): Promise<void> => {
      attempts += 1
      if (attempts === 1) throw new Error('HTTP 503')
    })
    renderEditor(onSave)
    fireEvent.change(screen.getByRole('textbox'), {
      target: { value: '未保存的修改必须留下' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Save expectation' }))
    const error = await screen.findByTestId('expectation-save-error')
    expect(error).toBeInTheDocument()
    expect(screen.getByRole('textbox')).toHaveValue('未保存的修改必须留下')
    fireEvent.click(screen.getByTestId('expectation-save-retry'))
    await waitFor(() => expect(attempts).toBe(2))
    await waitFor(() =>
      expect(screen.queryByTestId('expectation-save-error')).not.toBeInTheDocument(),
    )
  })
})

describe('SpecificationSpacePanel run state (M2)', () => {
  const space = {
    status: 'frozen',
    frozen_at: '2026-09-06T00:00:00+00:00',
    frozen_before_results: true,
    revealed: false,
    definitions: [
      {
        id: 'ols_full_controls',
        label: 'OLS · full controls',
        rationale: 'r',
        dimension: 'estimator',
        value: 'ols',
        admissible: true,
        user_decision: 'include',
        choices: [],
      },
      {
        id: 'iv_nearc4_full',
        label: 'IV · full controls',
        rationale: 'r',
        dimension: 'identification',
        value: 'nearc4',
        admissible: true,
        user_decision: 'include',
        choices: [],
      },
    ],
  }

  test('running state disables the button with counted progress from global state', () => {
    render(
      <SpecificationSpacePanel
        space={space}
        onFreeze={vi.fn(async () => undefined)}
        onRun={vi.fn(async () => undefined)}
        running
        progress={{ done: 3, total: 12 }}
      />,
    )
    const button = screen.getByTestId('spec-space-run')
    expect(button).toHaveTextContent('Running 3/12')
    expect(button).toBeDisabled()
    expect(screen.getByTestId('spec-space-run-status')).toHaveTextContent('正在运行规格 3/12')
  })

  test('indeterminate progress shows non-fabricated label', () => {
    render(
      <SpecificationSpacePanel
        space={space}
        onFreeze={vi.fn(async () => undefined)}
        onRun={vi.fn(async () => undefined)}
        running
        progress={null}
      />,
    )
    expect(screen.getByTestId('spec-space-run')).toHaveTextContent('Running specifications…')
    expect(screen.getByTestId('spec-space-run-status')).toHaveTextContent('正在运行规格…')
  })

  test('terminal failure shows the stable category with a Retry that re-runs', async () => {
    const onRetryRun = vi.fn()
    render(
      <SpecificationSpacePanel
        space={space}
        onFreeze={vi.fn(async () => undefined)}
        onRun={vi.fn(async () => undefined)}
        failure={{ category: 'spec_run_failed' }}
        onRetryRun={onRetryRun}
      />,
    )
    const error = screen.getByTestId('spec-space-run-error')
    expect(error).toHaveTextContent('spec_run_failed')
    fireEvent.click(screen.getByTestId('spec-space-run-retry'))
    expect(onRetryRun).toHaveBeenCalledOnce()
    expect(screen.getByTestId('spec-space-run')).toBeEnabled()
  })
})
