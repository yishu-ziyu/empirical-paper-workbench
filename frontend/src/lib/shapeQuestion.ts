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

const SIGNALS: { id: string; label: string; pattern: RegExp }[] = [
  { id: 'charls', label: 'CHARLS', pattern: /charls|中国健康与养老|养老追踪/i },
  { id: 'cfps', label: 'CFPS', pattern: /cfps|家庭追踪/i },
  { id: 'cgss', label: 'CGSS', pattern: /cgss|综合社会调查/i },
  { id: 'pension', label: '养老', pattern: /养老|退休|养老金|并轨/ },
  { id: 'digital', label: '数字经济', pattern: /数字经济|数字化|互联网/ },
  { id: 'wage', label: '最低工资', pattern: /最低工资|调薪|工资/ },
  { id: 'reproduce', label: '想复现一篇', pattern: /复现|那篇|看了篇|模仿/ },
  { id: 'advisor', label: '导师给的方向', pattern: /导师|老师让|作业|开题/ },
]

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

export function extractHeard(text: string): HeardItem[] {
  return SIGNALS.filter((item) => item.pattern.test(text)).map(({ id, label }) => ({
    id,
    label,
  }))
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

function pickTitle(text: string, heard: HeardItem[], answers: ShapeAnswers): string {
  const ids = new Set(heard.map((item) => item.id))
  const compare = answers.compare
  const outcome = answers.outcome

  if (ids.has('pension')) {
    if (compare === 'who') return '养老金变化之后，临近退休的人是不是比更年轻的人更早离开劳动力市场？'
    if (outcome === 'health') return '养老金变化之后，老年人的消费和健康有没有跟着变？'
    return '养老金并轨之后，临近退休的人是不是更早离开劳动力市场？'
  }
  if (ids.has('digital')) {
    if (compare === 'gap' || outcome === 'wage') return '数字经济发展有没有拉大不同技能工人的工资差距？'
    return '数字经济发展之后，企业的用工和工资发生了什么变化？'
  }
  if (ids.has('wage')) {
    return '最低工资上调之后，低技能工人的就业是不是下降了？'
  }
  if (ids.has('reproduce')) {
    return '把那篇论文的问题放到中国数据上，重新问一遍。'
  }

  const cleaned = text
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/[。！？.!?]+$/, '')
  if (cleaned.length >= 12 && cleaned.length <= 48) return `${cleaned}？`
  if (cleaned.length > 48) return `${cleaned.slice(0, 36)}…？`
  return '这还是一个方向，还不是一个可以估计的问题。'
}

export function reflect(text: string, heard: HeardItem[], answers: ShapeAnswers): string {
  const names = heard.map((item) => item.label)
  if (names.length === 0) {
    return text.trim()
      ? '我听到了一些念头，但还抓不住一个可以估计的对象。'
      : '你先说，我听着。'
  }
  if (!answers.compare) {
    return `我听到了${names.join('、')}。现在比较像一个方向，还不太像一个问题。`
  }
  if (!answers.outcome) {
    return `比较这边有了：${COMPARE_TEXT[answers.compare]}。还差结果看什么。`
  }
  return `可以停在这里了。拿着这个问题往下走。`
}

export function shapeQuestion(text: string, answers: ShapeAnswers = {}): QuestionDraft {
  const heard = extractHeard(text)
  const missing: string[] = []
  if (!answers.compare) missing.push('还不知道要比较什么')
  if (!answers.outcome) missing.push('还不知道结果看什么')
  if (heard.length === 0) missing.push('还听不太清具体对象')

  return {
    title: pickTitle(text, heard, answers),
    comparison: answers.compare ? COMPARE_TEXT[answers.compare] : '还没定',
    outcome: answers.outcome ? OUTCOME_TEXT[answers.outcome] : '还没定',
    heard,
    missing,
    ready: Boolean(answers.compare && answers.outcome),
    reflection: reflect(text, heard, answers),
  }
}
