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
    rationale: 'Inspect first-stage strength of college proximity.',
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
    expect(screen.getByTestId('evidence-challenge')).toHaveTextContent('first-stage')

    fireEvent.click(screen.getByTestId('evidence-matrix-ols_region_dummies'))
    fireEvent.click(screen.getByTestId('evidence-matrix-iv_region_dummies'))
    expect(await screen.findByTestId('evidence-compare-intent')).toHaveTextContent(
      'Identification strategy changed',
    )
    expect(screen.getByTestId('evidence-compare-delta')).toHaveTextContent('βA → βB')
    expect(screen.getByTestId('evidence-compare-delta')).toHaveTextContent('Δ')
    expect(onCompare).toHaveBeenCalled()
  })

  test('renders claim ledger and approve control', async () => {
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
