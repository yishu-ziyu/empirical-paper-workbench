import { describe, expect, test, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import EvidenceLab from '../EvidenceLab'
import type { ResearchLab } from '../../lib/workspace'

function choice(dimension: string, value: string) {
  return { dimension, value }
}

const research = {
  teaching_case: 'card_1995',
  canonical_spec_id: 'iv_region_dummies',
  surprise: {
    status: 'Unexpected',
    kind: 'ordering_mismatch',
    expected: 'IV may be smaller than OLS',
    observed: 'IV > OLS',
  },
  next_challenge: {
    id: 'challenge.instrument_strength',
    rationale:
      'Instrument strength deserves inspection. Effective F = 14.14. Strength diagnostics alone do not establish instrument validity.',
    rationale_zh:
      '工具变量强度值得检查。Effective F = 14.14。强度诊断本身不能证明工具变量有效。',
    status: 'proposed',
  },
  specification_space: {
    status: 'frozen',
    frozen_at: '2026-09-06T00:00:00+00:00',
    definitions: [],
  },
  claims: [
    {
      id: 'claim.card.education-earnings',
      claim_text: 'Education is positively associated with earnings.',
      claim_type: 'association',
      supported_wording: 'Education is positively associated with earnings.',
      conditionally_supported_wording:
        'Under the college-proximity IV assumptions, IV estimates suggest a positive local causal return to schooling.',
      unsupported_wording: "One more year of education raises everyone's wage by 13%.",
      supporting_run_ids: ['run-ols', 'run-iv'],
      unresolved_assumptions: ['IV exclusion restriction', 'monotonicity', 'LATE is not ATE'],
      approved_by_user: false,
      version: 1,
      evidence_status: 'supported',
    },
  ],
  current_claim_id: 'claim.card.education-earnings',
  claim: {
    id: 'claim.card.education-earnings',
    claim_text: 'Education is positively associated with earnings.',
    claim_type: 'association',
    supported_wording: 'Education is positively associated with earnings.',
    conditionally_supported_wording:
      'Under the college-proximity IV assumptions, IV estimates suggest a positive local causal return to schooling.',
    unsupported_wording: "One more year of education raises everyone's wage by 13%.",
    supporting_run_ids: ['run-ols', 'run-iv'],
    unresolved_assumptions: ['IV exclusion restriction', 'monotonicity', 'LATE is not ATE'],
    approved_by_user: false,
    version: 1,
    evidence_status: 'supported',
  },
  specification_runs: [
    {
      id: 'run-ols',
      spec_id: 'ols_region_dummies',
      label: 'OLS · 1966 region dummies',
      estimator: 'statspai.feols',
      method: 'ols',
      formula: 'lwage ~ educ + exper',
      covariance: 'HC1',
      coef: 0.08,
      se: 0.01,
      p: 0.001,
      n: 3010,
      status: 'ok',
      relation: 'exploratory',
      choices: [
        choice('estimator', 'ols'),
        choice('identification', 'none'),
        choice('experience', 'quadratic'),
        choice('demographics', 'black'),
        choice('region', 'reg66'),
      ],
    },
    {
      id: 'run-iv',
      spec_id: 'iv_region_dummies',
      label: 'IV · nearc4 with 1966 region dummies',
      estimator: 'statspai.ivreg',
      method: 'iv',
      formula: 'lwage ~ (educ ~ nearc4) + exper',
      covariance: 'nonrobust',
      coef: 0.13,
      se: 0.05,
      p: 0.01,
      n: 3010,
      status: 'ok',
      relation: 'canonical',
      diagnostics: { F_eff: 14.1, first_stage_F: 13.2 },
      choices: [
        choice('estimator', 'iv'),
        choice('identification', 'nearc4'),
        choice('experience', 'quadratic'),
        choice('demographics', 'black'),
        choice('region', 'reg66'),
      ],
    },
  ],
} as unknown as ResearchLab

describe('EvidenceLab', () => {
  test('renders results space, matrix and compare from research payload', async () => {
    const onCompare = vi.fn(async () => ({
      coef_a: 0.08,
      coef_b: 0.13,
      delta_abs: 0.05,
      delta_pct: 62.5,
      changed: [
        { dimension: 'estimator', a: 'ols', b: 'iv' },
        { dimension: 'identification', a: 'none', b: 'nearc4' },
      ],
      unchanged: [
        { dimension: 'experience', a: 'quadratic', b: 'quadratic' },
      ],
      why_moved: 'Identification strategy changed',
    }))
    render(
      <EvidenceLab
        research={research}
        onPromote={vi.fn(async () => undefined)}
        onRevert={vi.fn(async () => undefined)}
        onAcceptChallenge={vi.fn(async () => undefined)}
        onCompare={onCompare}
      />,
    )
    expect(screen.getByTestId('evidence-lab')).toBeInTheDocument()
    expect(screen.getByTestId('evidence-results-space')).toBeInTheDocument()
    expect(screen.getByTestId('evidence-spec-ols')).toBeInTheDocument()
    expect(screen.getByTestId('evidence-spec-iv')).toBeInTheDocument()
    expect(screen.getByTestId('evidence-choice-matrix')).toBeInTheDocument()
    expect(screen.getByTestId('evidence-matrix-ols_region_dummies')).toBeInTheDocument()
    expect(screen.getByTestId('evidence-surprise')).toHaveTextContent('Unexpected')
    expect(screen.getByTestId('evidence-surprise')).toHaveTextContent('Expected')
    expect(screen.getByTestId('evidence-surprise')).toHaveTextContent('Observed')
    expect(screen.getByTestId('evidence-challenge')).toHaveTextContent('Instrument strength deserves inspection')
    expect(screen.getByTestId('evidence-challenge')).toHaveTextContent('Effective F = 14.14')
    expect(screen.getByTestId('evidence-challenge')).not.toHaveTextContent('may be a weak instrument')

    fireEvent.click(screen.getByTestId('evidence-matrix-ols_region_dummies'))
    fireEvent.click(screen.getByTestId('evidence-matrix-iv_region_dummies'))
    expect(await screen.findByTestId('evidence-compare-intent')).toHaveTextContent(
      'Identification strategy changed',
    )
    expect(screen.getByTestId('evidence-compare-delta')).toHaveTextContent('βA → βB')
    expect(screen.getByTestId('evidence-compare-delta')).toHaveTextContent('Δ')
    expect(onCompare).toHaveBeenCalled()
  })

  test('renders claim ledger and approve control after reviewing claim', async () => {
    const onApproveClaim = vi.fn(async () => undefined)
    render(
      <EvidenceLab
        research={research}
        onPromote={vi.fn(async () => undefined)}
        onRevert={vi.fn(async () => undefined)}
        onAcceptChallenge={vi.fn(async () => undefined)}
        onApproveClaim={onApproveClaim}
      />,
    )
    // Before review: lightweight card shown, full claim ledger folded
    expect(screen.getByTestId('evidence-claim-ledger')).toBeInTheDocument()
    expect(screen.getByTestId('evidence-review-claim')).toBeInTheDocument()
    expect(screen.getByText(/Draft claim ready · 已可以整理结论/)).toBeInTheDocument()
    expect(screen.queryByTestId('claim-ledger')).not.toBeInTheDocument()

    // Clicking review claim expands full claim ledger
    fireEvent.click(screen.getByTestId('evidence-review-claim'))
    expect(screen.getByTestId('claim-ledger')).toBeInTheDocument()
    expect(screen.getByTestId('claim-supported')).toHaveTextContent(
      'Education is positively associated with earnings.',
    )
    expect(screen.getByTestId('claim-conditional')).toHaveTextContent(
      'college-proximity IV assumptions',
    )
    expect(screen.getByTestId('claim-unsupported')).toHaveTextContent(
      "One more year of education raises everyone's wage by 13%.",
    )
    fireEvent.click(screen.getByTestId('claim-approve'))
    expect(onApproveClaim).toHaveBeenCalledWith('claim.card.education-earnings')
  })

  test('C1 Visual order: Results space and Compare precede Claim Ledger; Compare expands claim', () => {
    render(
      <EvidenceLab
        research={research}
        onPromote={vi.fn(async () => undefined)}
        onRevert={vi.fn(async () => undefined)}
        onAcceptChallenge={vi.fn(async () => undefined)}
      />,
    )
    const resultsSpace = screen.getByTestId('evidence-results-space')
    const compare = screen.getByTestId('evidence-compare')
    const claimLedgerWrapper = screen.getByTestId('evidence-claim-ledger')

    // DOM order check: results space precedes compare, and compare precedes claim ledger
    expect(resultsSpace.compareDocumentPosition(compare) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
    expect(compare.compareDocumentPosition(claimLedgerWrapper) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()

    // Selecting two specifications automatically expands Claim Ledger
    fireEvent.click(screen.getByTestId('evidence-matrix-ols_region_dummies'))
    fireEvent.click(screen.getByTestId('evidence-matrix-iv_region_dummies'))
    expect(screen.getByTestId('claim-ledger')).toBeInTheDocument()
  })

  test('C4 Spec runs UI deduplication with multiple runs for same spec_id and history switcher', () => {
    const multiRunResearch = {
      ...research,
      specification_runs: [
        {
          id: 'run-ols-1',
          spec_id: 'ols_region_dummies',
          label: 'OLS · 1966 region dummies',
          method: 'ols',
          coef: 0.074,
          status: 'ok',
          relation: 'exploratory',
          choices: [choice('estimator', 'ols')],
        },
        {
          id: 'run-ols-2',
          spec_id: 'ols_region_dummies',
          label: 'OLS · 1966 region dummies',
          method: 'ols',
          coef: 0.08,
          status: 'ok',
          relation: 'exploratory',
          choices: [choice('estimator', 'ols')],
        },
        {
          id: 'run-iv',
          spec_id: 'iv_region_dummies',
          label: 'IV · nearc4 with 1966 region dummies',
          method: 'iv',
          coef: 0.13,
          status: 'ok',
          relation: 'canonical',
          choices: [choice('estimator', 'iv')],
        },
      ],
    } as unknown as ResearchLab

    render(
      <EvidenceLab
        research={multiRunResearch}
        onPromote={vi.fn(async () => undefined)}
        onRevert={vi.fn(async () => undefined)}
        onAcceptChallenge={vi.fn(async () => undefined)}
      />,
    )

    // Only 1 row for ols_region_dummies is rendered in choice matrix
    const rows = screen.getAllByTestId('evidence-matrix-ols_region_dummies')
    expect(rows).toHaveLength(1)

    // History button shows 2 runs
    const historyBtn = screen.getByTestId('evidence-history-ols_region_dummies')
    expect(historyBtn).toBeInTheDocument()
    expect(historyBtn).toHaveTextContent(/2 runs/i)
    expect(historyBtn).toHaveTextContent(/History 2/i)

    // Default displayed is latest run (run-ols-2: 0.0800)
    expect(rows[0]).toHaveTextContent('0.0800')

    // Click history switcher to switch to run-ols-1 (0.0740)
    fireEvent.click(historyBtn)
    expect(screen.getByTestId('evidence-matrix-ols_region_dummies')).toHaveTextContent('0.0740')
  })

  test('mismatch after approve offers explicit promote and still allows write results', () => {
    const onPromote = vi.fn(async () => undefined)
    const onPreparePaper = vi.fn(async () => undefined)
    const approved = {
      ...research.claim!,
      id: 'claim.card.education-earnings',
      approved_by_user: true,
      stale: false,
      provenance: { iv_spec_id: 'iv_region_dummies', iv_run_id: 'run-iv' },
    }
    render(
      <EvidenceLab
        research={{
          ...research,
          canonical_spec_id: 'ols_region_dummies',
          claim: approved,
          claims: [approved],
        }}
        onPromote={onPromote}
        onPreparePaper={onPreparePaper}
      />,
    )
    expect(screen.getByTestId('claim-canonical-mismatch')).toHaveTextContent(
      '当前 Claim 依赖 IV specification，但正式主规格不是该 IV。',
    )
    expect(screen.getByTestId('claim-promote-supporting')).toBeInTheDocument()
    expect(screen.getByTestId('claim-write-results')).toBeInTheDocument()
    fireEvent.click(screen.getByTestId('claim-write-results'))
    expect(onPreparePaper).toHaveBeenCalled()
    fireEvent.click(screen.getByTestId('claim-promote-supporting'))
    expect(onPromote).toHaveBeenCalledWith('run-iv')
  })
})
