import { useState } from 'react'
import { apiFetch, API_BASE } from '../lib/apiBase'
import { useT } from '../lib/i18n'

// 代码导出对话框 (T-09)
// - 第一项：复现包 / 复现脚本 = 研究中实际运行的代码
//   GET /sessions/{id}/replication-package | replication-script
//   （docs/acceptance/replication-script.md）
// - 其后 4 个翻译版：Python / Stata / R / EViews，数值未核对
//   GET /sessions/{id}/code-export?format=xxx
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

// 触发浏览器下载：apiFetch 拿 blob → createObjectURL → click 隐藏 <a>
// 鉴权走 httpOnly cookie（apiFetch 自动携带 + 401 静默刷新），
// 不再读 localStorage 的遗留 Bearer token（XSS 暴露面）。
class DownloadError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

async function downloadCode(sessionId: string, format: string): Promise<void> {
  const fallback = `analysis.${format === 'R' ? 'R' : format}`
  await downloadFrom(`${API_BASE}/sessions/${sessionId}/code-export?format=${format}`, fallback)
}

async function downloadFrom(url: string, fallback: string): Promise<void> {
  const resp = await apiFetch(url)
  if (!resp.ok) {
    const text = await resp.text().catch(() => '')
    throw new DownloadError(resp.status, `下载失败 (${resp.status}): ${text}`)
  }
  const blob = await resp.blob()
  // 从 Content-Disposition 提取 filename，回退到默认
  const cd = resp.headers.get('content-disposition') || ''
  const m = cd.match(/filename="?([^"]+)"?/)
  const filename = m ? m[1] : fallback
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
  const [replicationError, setReplicationError] = useState<string | null>(null)
  if (!isOpen) return null

  const handleDownload = async (format: string) => {
    try {
      await downloadCode(sessionId, format)
    } catch (e) {
      // 静默失败：组件不显示 toast，由上层处理
      console.error('code export failed:', e)
    }
  }

  // 复现包 / 复现脚本：失败原因要说清楚（没有运行、数据已变），不静默
  const handleReplication = async (kind: 'package' | 'script') => {
    setReplicationError(null)
    const path = kind === 'package' ? 'replication-package' : 'replication-script'
    const fallback = kind === 'package' ? 'replication-package.zip' : 'replication.py'
    try {
      await downloadFrom(`${API_BASE}/sessions/${sessionId}/${path}`, fallback)
    } catch (e) {
      const status = e instanceof DownloadError ? e.status : 0
      setReplicationError(
        status === 404
          ? t('codeExport.replication.noRuns')
          : status === 409
            ? t('codeExport.replication.dataChanged')
            : t('codeExport.replication.failed'),
      )
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
            <svg
              viewBox="0 0 16 16"
              className="h-4 w-4"
              fill="none"
              stroke="currentColor"
              strokeWidth={1.8}
              aria-hidden="true"
            >
              <path strokeLinecap="round" d="M4 4l8 8M12 4l-8 8" />
            </svg>
          </button>
        </div>

        {/* 说明 */}
        <p className="mb-4 font-serif text-xs text-muted">
          {t('codeExport.desc')}
        </p>

        {/* 复现包：实际运行的代码 + 分析数据 */}
        <button
          type="button"
          data-testid="replication-package-button"
          onClick={() => handleReplication('package')}
          className="mb-1 flex w-full items-center justify-between rounded border border-accent/50 bg-accent/5 px-4 py-3 text-left transition-colors hover:bg-accent/10"
        >
          <div className="flex flex-col">
            <span className="font-serif text-sm font-semibold text-ink">
              {t('codeExport.replication.title')}
            </span>
            <span className="font-serif text-xs text-muted">
              {t('codeExport.replication.desc')}
            </span>
          </div>
          <span className="rounded bg-accent px-2 py-1 font-mono text-xs text-white">.zip</span>
        </button>
        <button
          type="button"
          data-testid="replication-script-button"
          onClick={() => handleReplication('script')}
          className="mb-1 font-serif text-xs text-accent underline-offset-4 hover:underline"
        >
          {t('codeExport.replication.scriptOnly')}
        </button>
        {replicationError && (
          <p role="alert" data-testid="replication-error" className="mb-1 font-serif text-xs text-danger">
            {replicationError}
          </p>
        )}

        {/* 翻译版：4 个下载按钮 */}
        <p className="mb-2 mt-4 font-serif text-xs font-semibold text-muted">
          {t('codeExport.translatedHeading')}
        </p>
        <div data-testid="code-export-translated" className="flex flex-col gap-2">
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
