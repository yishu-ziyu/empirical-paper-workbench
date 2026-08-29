export type HeardItem = {
  id: string
  label: string
}

export type ClarifyOption = {
  id: string
  label: string
}

export type ClarifyPrompt = {
  id: 'compare' | 'outcome' | 'who'
  question: string
  options: ClarifyOption[]
}

export type QuestionDraft = {
  intent: 'research' | 'conversation'
  title: string
  comparison: string
  outcome: string
  heard: HeardItem[]
  missing: string[]
  ready: boolean
  reflection: string
}

export type ShapeAnswers = {
  compare?: string
  outcome?: string
  who?: string
}

const COMPARE_OPTIONS: ClarifyOption[] = [
  { id: 'policy', label: '政策有没有效果' },
  { id: 'who', label: '谁受到了影响' },
  { id: 'gap', label: '差距有没有变大' },
]

const OUTCOME_OPTIONS: ClarifyOption[] = [
  { id: 'work', label: '工作和退休' },
  { id: 'wage', label: '工资或收入' },
  { id: 'health', label: '健康或消费' },
]

const COMPARE_TEXT: Record<string, string> = {
  policy: '比较政策前后',
  who: '比较受影响更大的人和更小的人',
  gap: '比较不同群体之间的差距',
}

const OUTCOME_TEXT: Record<string, string> = {
  work: '看就业、工时或退休',
  wage: '看工资或收入',
  health: '看健康或消费',
}

const CONVERSATION_REPLY =
  '你好！你可以随便说一句最近想研究的现象或问题，我会陪你一步步把它变成可检验的研究问题。如果已经有数据，也可以直接上传。'

// Conservative degraded-mode boundary: generic research language only, never
// domain-specific templates or inferred variables.
const RESEARCH_INTENT_PATTERN =
  /研究|论文|课题|导师|老师让|开题|复现|数据|问什么|能发|是否|有没有|会不会|影响|效应|关系|相关|导致|提高|降低|差异|变化|比较|research|study|whether|effect|impact|relationship|data/i

export function hasResearchIntent(text: string): boolean {
  return RESEARCH_INTENT_PATTERN.test(text.replace(/\s+/g, ' ').trim())
}

function userIntentTitle(text: string): string {
  const cleaned = text.replace(/\s+/g, ' ').trim()
  return cleaned || '这还是一个方向，还不是一个可以估计的问题。'
}

export function nextPrompt(answers: ShapeAnswers): ClarifyPrompt | null {
  if (!answers.compare) {
    return {
      id: 'compare',
      question: '你现在更想弄清哪一件事？',
      options: COMPARE_OPTIONS,
    }
  }
  if (!answers.outcome) {
    return {
      id: 'outcome',
      question: '结果你更想看哪一类？',
      options: OUTCOME_OPTIONS,
    }
  }
  return null
}

export function reflect(text: string, answers: ShapeAnswers): string {
  if (!text.trim()) return '你先说，我听着。'
  if (!answers.compare) {
    return '我先保留你的原话。现在只确认要比较什么。'
  }
  if (!answers.outcome) {
    return `比较这边有了：${COMPARE_TEXT[answers.compare]}。还差结果看什么。`
  }
  return `可以停在这里了。拿着这个问题往下走。`
}

export function shapeQuestion(text: string, answers: ShapeAnswers = {}): QuestionDraft {
  if (!hasResearchIntent(text)) {
    return {
      intent: 'conversation',
      title: '',
      comparison: '还没定',
      outcome: '还没定',
      heard: [],
      missing: [],
      ready: false,
      reflection: CONVERSATION_REPLY,
    }
  }
  const missing: string[] = []
  if (!answers.compare) missing.push('还不知道要比较什么')
  if (!answers.outcome) missing.push('还不知道结果看什么')

  return {
    intent: 'research',
    title: userIntentTitle(text),
    comparison: answers.compare ? COMPARE_TEXT[answers.compare] : '还没定',
    outcome: answers.outcome ? OUTCOME_TEXT[answers.outcome] : '还没定',
    heard: [],
    missing,
    ready: Boolean(answers.compare && answers.outcome),
    reflection: reflect(text, answers),
  }
}
