// 方法列只承诺发动机真会跑的五类。
// 38 个名字不再出现在选择器里，避免人选了 Causal Forest 以为会跑森林。

import { useT } from '../lib/i18n'

export const ENGINE_METHODS: string[] = ['OLS', 'DiD', 'IV', 'RD', 'SCM']

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
  const { t } = useT()
  return (
    <div>
      <select
        data-testid="method-selector"
        aria-label={t('direction.method')}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        className="mt-1 w-full rounded border border-border p-2"
      >
        <option value="">{t('method.select')}</option>
        {ENGINE_METHODS.map((m) => (
          <option key={m} value={m}>
            {m}
          </option>
        ))}
      </select>
      <p className="mt-1 text-[11px] leading-5 text-muted">{t('method.hint')}</p>
    </div>
  )
}
