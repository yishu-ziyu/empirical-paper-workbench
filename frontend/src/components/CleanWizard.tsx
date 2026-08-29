import { useT } from '../lib/i18n'

export interface VariableInfo {
  dtype: string
  missing_rate: number
  n_unique: number
  is_numeric: boolean
}

export interface DistStats {
  min: number
  max: number
  mean: number
}

export interface Profile {
  n_rows: number
  n_cols: number
  variables: Record<string, VariableInfo>
}

export interface OutlierReport {
  before: Record<string, DistStats>
  after: Record<string, DistStats>
}

interface CleanWizardProps {
  profile: Profile
  outliers: OutlierReport
  onSelectStrategy: (strategy: string) => void
  selectedStrategy?: string
}

const STRATEGIES: { id: string; label: string }[] = [
  { id: 'drop', label: '删除 (Drop)' },
  { id: 'impute', label: '插补 (Impute)' },
  { id: 'mice', label: 'MICE' },
]

function pct(rate: number): string {
  return `${(rate * 100).toFixed(0)}%`
}

export default function CleanWizard({
  profile,
  outliers,
  onSelectStrategy,
  selectedStrategy,
}: CleanWizardProps) {
  const { t } = useT()
  const varNames = Object.keys(profile.variables)
  const outlierVars = Object.keys(outliers.before)

  return (
    <div className="clean-wizard space-y-6 p-4">
      {/* Sub-step 1: profiling report */}
      <section
        data-testid="profile-report"
        className="rounded-lg border border-gray-200 p-4"
      >
        <h2 className="mb-3 text-lg font-semibold">{t('clean.profiling')}</h2>
        <p className="mb-3 text-sm text-gray-600">
          {t('clean.rows')}：<span data-testid="profile-n-rows">{profile.n_rows}</span>
          {' / '}
          {t('clean.cols')}：<span data-testid="profile-n-cols">{profile.n_cols}</span>
        </p>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left">
              <th className="py-1">{t('clean.variable')}</th>
              <th className="py-1">{t('clean.type')}</th>
              <th className="py-1">{t('clean.missingRate')}</th>
              <th className="py-1">{t('clean.unique')}</th>
              <th className="py-1">{t('clean.isNumeric')}</th>
            </tr>
          </thead>
          <tbody>
            {varNames.map((name) => {
              const v = profile.variables[name]
              return (
                <tr key={name} data-testid={`var-${name}`} className="border-b">
                  <td className="py-1 font-mono">{name}</td>
                  <td className="py-1 font-mono">{v.dtype}</td>
                  <td className="py-1">{pct(v.missing_rate)}</td>
                  <td className="py-1">{v.n_unique}</td>
                  <td className="py-1">{v.is_numeric ? '是' : '否'}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </section>

      {/* Sub-step 3: missing-value strategy selector */}
      <section className="rounded-lg border border-gray-200 p-4">
        <h2 className="mb-3 text-lg font-semibold">{t('clean.strategy')}</h2>
        <div className="flex gap-2">
          {STRATEGIES.map((s) => (
            <button
              key={s.id}
              data-testid={`strategy-${s.id}`}
              onClick={() => onSelectStrategy(s.id)}
              className={`rounded px-3 py-1 text-sm ${
                selectedStrategy === s.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </section>

      {/* Sub-step 4: outlier before/after comparison */}
      <section
        data-testid="outlier-comparison"
        className="rounded-lg border border-gray-200 p-4"
      >
        <h2 className="mb-3 text-lg font-semibold">{t('clean.outlier')}</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left">
              <th className="py-1">{t('clean.variable')}</th>
              <th className="py-1">{t('clean.before')}</th>
              <th className="py-1">{t('clean.after')}</th>
            </tr>
          </thead>
          <tbody>
            {outlierVars.map((name) => (
              <tr key={name} className="border-b">
                <td className="py-1 font-mono">{name}</td>
                <td
                  className="py-1 font-mono"
                  data-testid={`outlier-before-${name}`}
                >
                  {outliers.before[name].max}
                </td>
                <td
                  className="py-1 font-mono"
                  data-testid={`outlier-after-${name}`}
                >
                  {outliers.after[name].max}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}
