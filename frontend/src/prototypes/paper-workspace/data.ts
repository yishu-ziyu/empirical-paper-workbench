// Shared example for all prototype variants: Card (1995) return to schooling.
// OLS / IV numbers come from docs/design/first-value-entry/card-pair.json (a real run).
// Rows marked `illustrative` are placeholders for the prototype only.
// Code strings mirror the real calls in backend/services/spec_run.py + agent/nodes/estimate.py.

export type Run = {
  id: string
  label: string
  method: 'OLS' | 'IV'
  coef: number
  se: number
  p: number
  n: number
  cov: string
  formula: string
  code: string
  ranAt: string
  illustrative?: boolean
}

const controls =
  'exper + expersq + black + smsa + south + smsa66 + reg661 + … + reg668'

export const OLS: Run = {
  id: 'run-3d4c·ols',
  label: 'OLS · 1966 地区虚拟变量',
  method: 'OLS',
  coef: 0.0747,
  se: 0.0035,
  p: 0,
  n: 3010,
  cov: 'HC1',
  formula: `lwage ~ educ + ${controls}`,
  code: `statspai.feols(\n    "lwage ~ educ + ${controls}",\n    data=df)`,
  ranAt: '09-07 16:16',
}

export const IV: Run = {
  id: 'run-3d4c·iv',
  label: 'IV · nearc4 工具',
  method: 'IV',
  coef: 0.1315,
  se: 0.055,
  p: 0.0168,
  n: 3010,
  cov: 'nonrobust',
  formula: `lwage ~ (educ ~ nearc4) + ${controls}`,
  code: `statspai.ivreg(\n    "lwage ~ (educ ~ nearc4) + ${controls}",\n    data=df)`,
  ranAt: '09-07 16:16',
}

export const FIRST_STAGE = { f: 13.26, fEff: 14.14 }

export const EXTRA_SPECS: Run[] = [
  { ...OLS, id: 'spec-3', label: 'OLS · 去掉地区虚拟变量', coef: 0.0751, se: 0.0036, illustrative: true,
    code: 'statspai.feols(\n    "lwage ~ educ + exper + expersq + black + smsa + south",\n    data=df)' },
  { ...OLS, id: 'spec-4', label: 'OLS · 仅南方样本', coef: 0.0712, se: 0.0052, n: 1215, illustrative: true,
    code: `statspai.feols(\n    "lwage ~ educ + ${controls}",\n    data=df[df.south == 1])` },
  { ...IV, id: 'spec-5', label: 'IV · nearc2 工具', coef: 0.1602, se: 0.0921, p: 0.082, illustrative: true,
    code: `statspai.ivreg(\n    "lwage ~ (educ ~ nearc2) + ${controls}",\n    data=df)` },
]

export const pct = (b: number) => `${(b * 100).toFixed(1)}%`
export const ci = (r: Run) => [r.coef - 1.96 * r.se, r.coef + 1.96 * r.se] as const
export const fmt = (x: number, d = 4) => x.toFixed(d)
export const stars = (p: number) => (p < 0.01 ? '***' : p < 0.05 ? '**' : p < 0.1 ? '*' : '')

export const CONTROLS = ['exper', 'expersq', 'black', 'smsa', 'south', 'smsa66', 'reg661', 'reg662', 'reg663', 'reg664', 'reg665', 'reg666', 'reg667', 'reg668']
export const DATA_SHA256 = 'eda514228a77327ab9aa20df72b89256cdec579482fa9dbbe4e3d757748c9bf2'
