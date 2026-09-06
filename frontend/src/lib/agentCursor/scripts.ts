/**
 * Card demo scripts. Data only — no LLM, no DOM queries, no coordinates.
 * Every target is a semantic product id.
 */

export const CARD_SHOW_ME_SCRIPT_ID = 'card.show-me'
export const CARD_CHALLENGE_EXPERIENCE_SCRIPT_ID = 'card.challenge-experience'

export const TARGET = {
  ols: 'evidence.spec.ols',
  iv: 'evidence.spec.iv',
  estimator: 'evidence.choice.estimator',
  experience: 'evidence.choice.experience',
  experienceLinear: 'evidence.spec.experience.linear',
  experienceQuadratic: 'evidence.spec.experience.quadratic',
} as const

export const PREVIEW_EXPERIENCE = 'experience.linear-quadratic'

export type AgentScriptStep =
  | { op: 'point'; target: string; intent?: string; intentZh?: string }
  | { op: 'compare'; a: string; b: string; intent?: string; intentZh?: string }
  | { op: 'preview'; command: string; intent?: string; intentZh?: string }
  | { op: 'runPreview' }
  | { op: 'promote' }
  | { op: 'pause'; ms: number }
  | { op: 'awaitConfirm'; kind: 'runPreview' | 'promote' }
  | { op: 'fadeUnchanged' }
  | { op: 'stop' }

export type AgentScript = {
  id: string
  steps: AgentScriptStep[]
}

export const CARD_SHOW_ME_SCRIPT: AgentScript = {
  id: CARD_SHOW_ME_SCRIPT_ID,
  steps: [
    { op: 'point', target: TARGET.ols },
    { op: 'pause', ms: 640 },
    { op: 'point', target: TARGET.iv },
    { op: 'pause', ms: 480 },
    {
      op: 'compare',
      a: TARGET.ols,
      b: TARGET.iv,
      intent: 'Identification strategy changed',
      intentZh: '识别策略发生变化',
    },
    { op: 'pause', ms: 520 },
    {
      op: 'point',
      target: TARGET.estimator,
      intent: 'Identification strategy changed',
      intentZh: '识别策略发生变化',
    },
    { op: 'fadeUnchanged' },
    { op: 'stop' },
  ],
}

export const CARD_CHALLENGE_EXPERIENCE_SCRIPT: AgentScript = {
  id: CARD_CHALLENGE_EXPERIENCE_SCRIPT_ID,
  steps: [
    { op: 'point', target: TARGET.experience },
    {
      op: 'preview',
      command: PREVIEW_EXPERIENCE,
      intent: 'Experience linear ↔ quadratic',
    },
    { op: 'awaitConfirm', kind: 'runPreview' },
    { op: 'runPreview' },
    {
      op: 'compare',
      a: TARGET.experienceQuadratic,
      b: TARGET.experienceLinear,
    },
    { op: 'stop' },
  ],
}

export const CARD_SCRIPTS: Record<string, AgentScript> = {
  [CARD_SHOW_ME_SCRIPT_ID]: CARD_SHOW_ME_SCRIPT,
  [CARD_CHALLENGE_EXPERIENCE_SCRIPT_ID]: CARD_CHALLENGE_EXPERIENCE_SCRIPT,
}
