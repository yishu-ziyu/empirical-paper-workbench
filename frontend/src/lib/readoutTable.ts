export type EstimateRow = {
  variable: string
  coef: string
  se: string
  p: string
}

export function parsePipeCells(line: string): string[] {
  return line
    .split('|')
    .map((cell) => cell.trim())
    .filter(Boolean)
}

function isMarkdownTableChrome(cells: string[]): boolean {
  if (cells.every((cell) => /^:?-+:?$/.test(cell))) return true
  const head = cells.map((cell) => cell.toLowerCase())
  return (
    head[0] === '变量' ||
    head[0] === 'variable' ||
    (head.includes('系数') && head.includes('p')) ||
    (head.includes('coef') && (head.includes('p') || head.includes('pvalue')))
  )
}

export function normalizeEstimateTableSource(raw: unknown): string | null {
  if (raw == null) return null
  if (Array.isArray(raw)) {
    const lines = raw.filter((row): row is string => typeof row === 'string')
    return lines.length ? lines.join('\n') : null
  }
  if (typeof raw === 'string') return raw
  return null
}

export function parseEstimateRows(raw: string | null | undefined): EstimateRow[] {
  if (!raw) return []
  const rows: EstimateRow[] = []
  const seen = new Set<string>()
  for (const line of raw.replace(/\r\n/g, '\n').split('\n')) {
    const cells = parsePipeCells(line)
    if (cells.length < 4) continue
    if (isMarkdownTableChrome(cells)) continue
    const key = cells.join('|')
    if (seen.has(key)) continue
    seen.add(key)
    rows.push({
      variable: cells[0],
      coef: cells[1],
      se: cells[2],
      p: cells[3],
    })
  }
  return rows
}

export function claimLabel(claim: string | null | undefined): string {
  const value = (claim || '').trim().toLowerCase()
  if (value === 'association' || value === 'assoc' || value === 'correlation') {
    return '相关'
  }
  if (value === 'causal_with_caveat') return '有限因果'
  return claim || '—'
}

export function starHumanLabel(star: number | null | undefined): string {
  if (star === 0) return '0 星'
  if (star == null) return '无因果评级'
  return `${star} 星`
}

export function literatureLabel(source: string | null | undefined): string {
  if (!source) return '—'
  if (source === 'crossref') return 'Crossref'
  if (source === 'mock') return '示例文献'
  return source
}

// Evidence 大数字的人读格式：显示层定长，精确值仍由接口与 title 保留。
export function formatStatValue(
  value: unknown,
  kind: 'coef' | 'se' | 'p' | 'n',
): string {
  const n = Number(value)
  if (value == null || !Number.isFinite(n)) return '—'
  if (kind === 'n') return n.toLocaleString('en-US')
  if (kind === 'p') return n < 1e-4 ? '< 0.0001' : n.toFixed(4)
  if (n !== 0 && (Math.abs(n) >= 1e5 || Math.abs(n) < 1e-4)) return n.toExponential(3)
  return n.toFixed(4)
}
