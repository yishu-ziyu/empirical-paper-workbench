import { API_BASE } from '../lib/apiBase'
import { useT } from '../lib/i18n'

// 代码导出对话框 (T-09)
// - 4 个下载按钮：Python (.py) / Stata (.do) / R (.R) / EViews (.m)
// - 点击下载 → 调 GET /sessions/{id}/code-export?format=xxx
// - 用 Tailwind 样式
// 设计：Editorial Academic Refined — 衬线字体 + 暖色调

export interface CodeExportDialogProps {
  sessionId: string
  isOpen: boolean
  onClose: () => void
}

// 4 种格式配置：format query 值 + 显示名 + 文件扩展名 + 描述
interface FormatConfig {
  format: string
  label: string
  extension: string
  description: string
}

const FORMATS: FormatConfig[] = [
  {
    format: 'py',
    label: 'Python',
    extension: '.py',
    description: 'pandas + statsmodels 原生代码',
  },
  {
    format: 'do',
    label: 'Stata',
    extension: '.do',
    description: 'regress / summarize / correlate',
  },
  {
    format: 'R',
    label: 'R',
    extension: '.R',
    description: 'lm() / summary() / read.csv()',
  },
  {
    format: 'm',
    label: 'EViews',
    extension: '.m',
    description: 'ls / stats / cor',
  },
]

// 触发浏览器下载：fetch 拿 blob → createObjectURL → click 隐藏 <a>
const LS_TOKEN_KEY = 'econpaper_access_token'

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem(LS_TOKEN_KEY)
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function downloadCode(sessionId: string, format: string): Promise<void> {
  const url = `${API_BASE}/sessions/${sessionId}/code-export?format=${format}`
  const resp = await fetch(url, { method: 'GET', headers: authHeaders() })
  if (!resp.ok) {
    const text = await resp.text().catch(() => '')
    throw new Error(`下载失败 (${resp.status}): ${text}`)
  }
  const blob = await resp.blob()
  // 从 Content-Disposition 提取 filename，回退到默认
  const cd = resp.headers.get('content-disposition') || ''
  const m = cd.match(/filename="?([^"]+)"?/)
  const filename = m ? m[1] : `analysis.${format === 'R' ? 'R' : format}`
  // 触发下载
  const objectUrl = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = objectUrl
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(objectUrl)
}

export default function CodeExportDialog({
  sessionId,
  isOpen,
  onClose,
}: CodeExportDialogProps) {
  const { t } = useT()
  if (!isOpen) return null

  const handleDownload = async (format: string) => {
    try {
      await downloadCode(sessionId, format)
    } catch (e) {
      // 静默失败：组件不显示 toast，由上层处理
      console.error('code export failed:', e)
    }
  }

  return (
    <div
      data-testid="code-export-dialog"
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40"
    >
      <div className="w-full max-w-md rounded-lg border border-border bg-paper p-6 shadow-xl">
        {/* 头部 */}
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-serif text-lg font-semibold text-ink">
            {t('codeExport.title')}
          </h2>
          <button
            type="button"
            data-testid="code-export-close"
            onClick={onClose}
            className="rounded p-1 text-muted hover:bg-panel hover:text-ink"
            aria-label={t('codeExport.close')}
          >
            ✕
          </button>
        </div>

        {/* 说明 */}
        <p className="mb-4 font-serif text-xs text-muted">
          {t('codeExport.desc')}
        </p>

        {/* 4 个下载按钮 */}
        <div className="flex flex-col gap-2">
          {FORMATS.map((cfg) => (
            <button
              key={cfg.format}
              type="button"
              data-testid="code-export-button"
              onClick={() => handleDownload(cfg.format)}
              className="flex items-center justify-between rounded border border-border bg-panel px-4 py-3 text-left transition-colors hover:border-accent hover:bg-accent/5"
            >
              <div className="flex flex-col">
                <span className="font-serif text-sm font-semibold text-ink">
                  {cfg.label}
                </span>
                <span className="font-serif text-xs text-muted">
                  {cfg.description}
                </span>
              </div>
              <span className="rounded bg-accent/10 px-2 py-1 font-mono text-xs text-accent">
                {cfg.extension}
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
