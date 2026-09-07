import { describe, expect, test, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { ExpectationEditor, SpecificationSpacePanel } from '../ResearchLabPanels'
import type { components } from '../../types/api'
import type { ResearchLab } from '../../lib/workspace'
import { I18nProvider } from '../../lib/i18n'

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
      left: {
        metric: 'estimate.coef',
        estimator: 'iv',
        spec_id: 'iv_region_dummies',
        label: 'IV estimate',
      },
      right: {
        metric: 'estimate.coef',
        estimator: 'ols',
        spec_id: 'ols_region_dummies',
        label: 'OLS estimate',
      },
      label: 'IV estimate < OLS estimate',
      source: 'seed',
    },
  ],
}

type SpecSpace = NonNullable<ResearchLab['specification_space']>

function specSpace(
  definitions: Array<{ id: string; admissible: boolean }>,
): SpecSpace {
  return {
    status: 'proposed',
    frozen_before_results: false,
    revealed: false,
    definitions: definitions.map((item) => ({
      id: item.id,
      label: item.id,
      rationale: '',
      dimension: 'estimator',
      value: item.id,
      admissible: item.admissible,
      user_decision: 'include',
      choices: [],
    })),
  }
}

function renderEditor(
  onSave: (payload: SavePayload) => Promise<void> = async () => undefined,
  expectation: Expectation = seedExpectation,
  criteriaLocked = false,
  specificationSpace?: SpecSpace,
) {
  return render(
    <I18nProvider>
      <ExpectationEditor
        expectation={expectation}
        onSave={onSave}
        criteriaLocked={criteriaLocked}
        specificationSpace={specificationSpace}
      />
    </I18nProvider>,
  )
}

describe('ExpectationEditor surprise criteria (M1)', () => {
  test('renders the explicit surprise condition block below the textarea', () => {
    renderEditor()
    expect(screen.getByTestId('expectation-criteria-block')).toHaveTextContent(
      '意外判定',
    )
    expect(screen.getByTestId('expectation-criterion')).toHaveTextContent(
      'IV 估计 < OLS 估计',
    )
    expect(screen.getByTestId('expectation-criterion')).not.toHaveTextContent(
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
      'IV 估计 < OLS 估计',
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
      'IV 估计 > OLS 估计',
    )
    fireEvent.click(screen.getByTestId('expectation-save'))
    await waitFor(() => expect(onSave).toHaveBeenCalledOnce())
    const payload = onSave.mock.calls[0]![0]
    expect(payload.criteria).toHaveLength(1)
    expect(payload.criteria![0]!.operator).toBe('gt')
    expect(payload.criteria![0]!.kind).toBe('ordering')
    expect(payload.criteria![0]!.source).toBe('user')
  })

  test('preserves exact spec_id refs when the direction control changes', async () => {
    const onSave = vi.fn(async (_payload: SavePayload): Promise<void> => undefined)
    renderEditor(onSave)
    fireEvent.change(screen.getByTestId('expectation-criterion-select'), {
      target: { value: 'iv-gt-ols' },
    })
    fireEvent.click(screen.getByTestId('expectation-save'))
    await waitFor(() => expect(onSave).toHaveBeenCalledOnce())
    const payload = onSave.mock.calls[0]![0]
    const next = payload.criteria![0]!
    expect(next.operator).toBe('gt')
    expect(next.kind).toBe('ordering')
    expect(next.left.spec_id).toBe('iv_region_dummies')
    expect(next.left.estimator).toBe('iv')
    expect((next.right as { spec_id?: string }).spec_id).toBe('ols_region_dummies')
    expect((next.right as { estimator?: string }).estimator).toBe('ols')
  })

  test('preserves exact spec_id through sign and approx and back', async () => {
    const onSave = vi.fn(async (_payload: SavePayload): Promise<void> => undefined)
    renderEditor(onSave)
    fireEvent.change(screen.getByTestId('expectation-criterion-select'), {
      target: { value: 'iv-positive' },
    })
    fireEvent.change(screen.getByTestId('expectation-criterion-select'), {
      target: { value: 'iv-approx-ols' },
    })
    fireEvent.change(screen.getByTestId('expectation-criterion-select'), {
      target: { value: 'iv-lt-ols' },
    })
    fireEvent.click(screen.getByTestId('expectation-save'))
    await waitFor(() => expect(onSave).toHaveBeenCalledOnce())
    const next = onSave.mock.calls[0]![0].criteria![0]!
    expect(next.kind).toBe('ordering')
    expect(next.operator).toBe('lt')
    expect(next.left.spec_id).toBe('iv_region_dummies')
    expect((next.right as { spec_id?: string }).spec_id).toBe('ols_region_dummies')
  })

  test('fabricated criterion binds comparable 34-col spec_ids, not estimator-only refs', async () => {
    const onSave = vi.fn(async (_payload: SavePayload): Promise<void> => undefined)
    renderEditor(
      onSave,
      { text: 'no criteria yet', confidence: 'medium', version: 1, history: [], criteria: [] },
      false,
      specSpace([
        { id: 'ols_region_dummies', admissible: true },
        { id: 'iv_region_dummies', admissible: true },
      ]),
    )
    fireEvent.change(screen.getByTestId('expectation-criterion-select'), {
      target: { value: 'iv-lt-ols' },
    })
    fireEvent.click(screen.getByTestId('expectation-save'))
    await waitFor(() => expect(onSave).toHaveBeenCalledOnce())
    const next = onSave.mock.calls[0]![0].criteria![0]!
    expect(next.left.spec_id).toBe('iv_region_dummies')
    expect(next.left.estimator).toBe('iv')
    expect((next.right as { spec_id?: string }).spec_id).toBe('ols_region_dummies')
    expect((next.right as { estimator?: string }).estimator).toBe('ols')
  })

  test('fabricated criterion binds 9-col comparable spec_ids when region specs are inadmissible', async () => {
    const onSave = vi.fn(async (_payload: SavePayload): Promise<void> => undefined)
    renderEditor(
      onSave,
      { text: 'no criteria yet', confidence: 'medium', version: 1, history: [], criteria: [] },
      false,
      specSpace([
        { id: 'ols_region_dummies', admissible: false },
        { id: 'iv_region_dummies', admissible: false },
        { id: 'ols_full_controls', admissible: true },
        { id: 'iv_nearc4_full', admissible: true },
      ]),
    )
    fireEvent.change(screen.getByTestId('expectation-criterion-select'), {
      target: { value: 'iv-gt-ols' },
    })
    fireEvent.click(screen.getByTestId('expectation-save'))
    await waitFor(() => expect(onSave).toHaveBeenCalledOnce())
    const next = onSave.mock.calls[0]![0].criteria![0]!
    expect(next.left.spec_id).toBe('iv_nearc4_full')
    expect((next.right as { spec_id?: string }).spec_id).toBe('ols_full_controls')
  })

  test('locked criterion select stays disabled after results are revealed', () => {
    renderEditor(async () => undefined, seedExpectation, true)
    expect(screen.getByTestId('expectation-criterion-select')).toBeDisabled()
    expect(screen.getByTestId('expectation-criterion-locked')).toHaveTextContent(
      '结果已经揭晓；本轮意外判定已锁定，不能事后改写。',
    )
    fireEvent.change(screen.getByTestId('expectation-criterion-select'), {
      target: { value: 'iv-gt-ols' },
    })
    expect(screen.getByTestId('expectation-criterion')).toHaveTextContent(
      'IV 估计 < OLS 估计',
    )
  })

  test('approx and sign options map to their criterion kinds', async () => {
    const onSave = vi.fn(async (_payload: SavePayload): Promise<void> => undefined)
    renderEditor(onSave)
    fireEvent.change(screen.getByTestId('expectation-criterion-select'), {
      target: { value: 'iv-approx-ols' },
    })
    expect(screen.getByTestId('expectation-criterion')).toHaveTextContent('IV 估计 ≈ OLS 估计')
    fireEvent.change(screen.getByTestId('expectation-criterion-select'), {
      target: { value: 'iv-positive' },
    })
    expect(screen.getByTestId('expectation-criterion')).toHaveTextContent(
      'IV 估计 为正',
    )
    fireEvent.click(screen.getByTestId('expectation-save'))
    await waitFor(() => expect(onSave).toHaveBeenCalledOnce())
    const payload = onSave.mock.calls[0]![0]
    expect(payload.criteria![0]!.kind).toBe('sign')
    expect(payload.criteria![0]!.operator).toBe('positive')
    expect(payload.criteria![0]!.left.spec_id).toBe('iv_region_dummies')
    expect(payload.criteria![0]!.right).toBeUndefined()
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
    fireEvent.click(screen.getByTestId('expectation-save'))
    const error = await screen.findByTestId('expectation-save-error')
    expect(error).toBeInTheDocument()
    expect(screen.getByRole('textbox')).toHaveValue('未保存的修改必须留下')
    fireEvent.click(screen.getByTestId('expectation-save-retry'))
    await waitFor(() => expect(attempts).toBe(2))
    await waitFor(() =>
      expect(screen.queryByTestId('expectation-save-error')).not.toBeInTheDocument(),
    )
  })

  test('C3 approx criterion label carries the effective tolerance in the real component', () => {
    const approx: Expectation = {
      ...seedExpectation,
      criteria: [
        {
          id: 'criterion.user.iv-approx-ols',
          kind: 'distance',
          operator: 'approx',
          left: {
            metric: 'estimate.coef',
            estimator: 'iv',
            spec_id: 'iv_region_dummies',
            label: 'IV estimate',
          },
          right: {
            metric: 'estimate.coef',
            estimator: 'ols',
            spec_id: 'ols_region_dummies',
            label: 'OLS estimate',
          },
          tolerance: { rel: 0.05 },
          label: 'IV ≈ OLS (±5%)',
          source: 'user',
        },
      ],
    }
    renderEditor(async () => undefined, approx)
    expect(screen.getByTestId('expectation-criterion')).toHaveTextContent(
      'IV 估计 ≈ OLS 估计 ±5%',
    )
    expect(screen.getByTestId('expectation-criterion')).not.toHaveTextContent('±25%')
    // ±25% (and the both-empty backend default) must be distinguishable
    const defaulted = {
      ...approx,
      criteria: [{ ...approx.criteria[0]!, tolerance: undefined }],
    }
    renderEditor(async () => undefined, defaulted)
    expect(screen.getAllByTestId('expectation-criterion')[1]).toHaveTextContent('±25%')
  })

  test('C3 ordering against a numeric constant shows the full string, not generic', () => {
    const orderingConst: Expectation = {
      ...seedExpectation,
      criteria: [
        {
          id: 'criterion.user.iv-lt-const',
          kind: 'ordering',
          operator: 'lt',
          left: {
            metric: 'estimate.coef',
            estimator: 'iv',
            spec_id: 'iv_nearc4_full',
            label: 'IV estimate',
          },
          right: 0.1,
          label: 'IV estimate < 0.1',
          source: 'user',
        } as ExpectationCriterion,
      ],
    }
    renderEditor(async () => undefined, orderingConst)
    expect(screen.getByTestId('expectation-criterion')).toHaveTextContent('IV 估计 < 0.1')
    expect(screen.getByTestId('expectation-criterion')).not.toHaveTextContent('可检验判定')
  })

  test('C3 same-estimator different-spec refs expose their spec identity visibly', () => {
    const twoIvSpecs: Expectation = {
      ...seedExpectation,
      criteria: [
        {
          id: 'criterion.user.iv-approx-ols',
          kind: 'distance',
          operator: 'approx',
          left: {
            metric: 'estimate.coef',
            estimator: 'iv',
            spec_id: 'iv_nearc4_full',
            label: 'IV estimate',
          },
          right: {
            metric: 'estimate.coef',
            estimator: 'iv',
            spec_id: 'iv_region_dummies',
            label: 'IV estimate (region dummies)',
          },
          tolerance: { rel: 0.25 },
          label: 'IV ≈ IV (region)',
          source: 'user',
        },
      ],
    }
    renderEditor(async () => undefined, twoIvSpecs)
    const identity = screen.getByTestId('criterion-spec-ids')
    expect(identity).toHaveTextContent('iv_nearc4_full')
    expect(identity).toHaveTextContent('iv_region_dummies')
    expect(identity).toBeVisible()
  })

  test('C3 criteria block stays display-only: no criterion mutation on render', async () => {
    const onSave = vi.fn(async (_payload: SavePayload): Promise<void> => undefined)
    renderEditor(onSave)
    expect(screen.getByTestId('expectation-criterion')).toHaveTextContent('IV 估计 < OLS 估计')
    // The stored snapshot (spec ids, label) is untouched until an explicit save
    expect(screen.getByTestId('criterion-spec-ids')).toHaveTextContent(
      'iv_region_dummies · ols_region_dummies',
    )
    expect(onSave).not.toHaveBeenCalled()
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
      <I18nProvider>
        <SpecificationSpacePanel
          space={space}
          onFreeze={vi.fn(async () => undefined)}
          onRun={vi.fn(async () => undefined)}
          running
          progress={{ done: 3, total: 12 }}
        />
      </I18nProvider>,
    )
    const button = screen.getByTestId('spec-space-run')
    expect(button).toHaveTextContent('正在运行 3/12')
    expect(button).toBeDisabled()
    expect(screen.getByTestId('spec-space-run-status')).toHaveTextContent('正在运行分析方案 3/12')
  })

  test('indeterminate progress shows non-fabricated label', () => {
    render(
      <I18nProvider>
        <SpecificationSpacePanel
          space={space}
          onFreeze={vi.fn(async () => undefined)}
          onRun={vi.fn(async () => undefined)}
          running
          progress={null}
        />
      </I18nProvider>,
    )
    expect(screen.getByTestId('spec-space-run')).toHaveTextContent('正在运行分析方案…')
    expect(screen.getByTestId('spec-space-run-status')).toHaveTextContent('正在运行分析方案…')
  })

  test('terminal failure shows the stable category with a Retry that re-runs', async () => {
    const onRetryRun = vi.fn()
    render(
      <I18nProvider>
        <SpecificationSpacePanel
          space={space}
          onFreeze={vi.fn(async () => undefined)}
          onRun={vi.fn(async () => undefined)}
          failure={{ category: 'spec_run_failed' }}
          onRetryRun={onRetryRun}
        />
      </I18nProvider>,
    )
    const error = screen.getByTestId('spec-space-run-error')
    expect(error).toHaveTextContent('spec_run_failed')
    fireEvent.click(screen.getByTestId('spec-space-run-retry'))
    expect(onRetryRun).toHaveBeenCalledOnce()
    expect(screen.getByTestId('spec-space-run')).toBeEnabled()
  })
})
