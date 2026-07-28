// 38 种计量方法选择器 (T-06)
// 方法列表从 spec §6 / StatsPAI registry 提取，硬编码于此。
// 模板：中文核心期刊 / 本科 / 硕论 / 英文投稿

export const METHODS_38: string[] = [
  'OLS',
  'IV',
  'GMM',
  '2SLS',
  'LIML',
  'JIVE',
  'DiD',
  'Event Study',
  'Synthetic Control',
  'Synthetic DiD',
  'RDD',
  'RKD',
  'Multi-cutoff RDD',
  'DML',
  'Causal Forest',
  'BCF',
  'BART',
  'PSM',
  'IPW',
  'DR-learner',
  'R-learner',
  'X-learner',
  'QTE',
  'CIC',
  'Bounds',
  'Bartik IV',
  'Shift-share',
  'Panel FE',
  'Panel RE',
  'GMM Panel',
  'Spatial DiD',
  'Spatial IV',
  'Bayesian DID',
  'Bayesian DML',
  'TMLE',
  'LTMLE',
  'Mediation',
  'Surrogate',
]

export const TEMPLATES: { value: string; label: string }[] = [
  { value: 'cn_journal', label: '中文核心期刊' },
  { value: 'undergrad', label: '本科论文' },
  { value: 'master', label: '硕论' },
  { value: 'en_submission', label: '英文投稿' },
]

export interface MethodSelectorProps {
  value?: string
  onChange?: (method: string) => void
}

export default function MethodSelector({
  value = '',
  onChange,
}: MethodSelectorProps) {
  return (
    <select
      data-testid="method-selector"
      aria-label="方法"
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
      className="mt-1 w-full rounded border border-border p-2"
    >
      <option value="">选择方法…</option>
      {METHODS_38.map((m) => (
        <option key={m} value={m}>
          {m}
        </option>
      ))}
    </select>
  )
}
