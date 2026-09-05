import type { RefObject } from 'react'
import PaperPath, { type PaperPathState } from './PaperPath'
import ReviewPanel from './ReviewPanel'
import RunTracePanel from './RunTracePanel'
import type { PaperNodeId } from '../lib/paperPath'
import { useT } from '../lib/i18n'
import type { components } from '../types/api'

type ReviewInfo = components['schemas']['ReviewInfoResponse']
type EstimateRecord = {
  history_compact?: string | null
  status?: string | null
}

export interface ResearchComputerProps {
  paperPath: PaperPathState
  onSelectPath: (id: PaperNodeId) => void
  sessionId: string | null
  review: ReviewInfo | null
  onDecision: () => void
  degradations: Array<{ node: string; reason: string }>
  csvName: string | null
  csvRows: number | null
  csvCols: number | null
  directionSummary: string | null
  directionMethod?: string | null
  directionDv?: string | null
  directionIv?: string | null
  hasReadout: boolean
  hasSuccessfulEstimate: boolean
  identFailed: boolean
  identReport: string | null
  robustnessStatus: string | null
  estimate: EstimateRecord | null
  evidenceOpen: boolean
  evidenceRef: RefObject<HTMLDetailsElement>
  onEvidenceOpenChange: (open: boolean) => void
}

function recorded(value: string | number | null | undefined, empty = '尚无记录') {
  return value === null || value === undefined || value === '' ? empty : String(value)
}

/** 右侧研究电脑：只组织现有状态和已有证据组件，不创造新的研究结果。 */
export default function ResearchComputer({
  paperPath,
  onSelectPath,
  sessionId,
  review,
  onDecision,
  degradations,
  csvName,
  csvRows,
  csvCols,
  directionSummary,
  directionMethod,
  directionDv,
  directionIv,
  hasReadout,
  hasSuccessfulEstimate,
  identFailed,
  identReport,
  robustnessStatus,
  estimate,
  evidenceOpen,
  evidenceRef,
  onEvidenceOpenChange,
}: ResearchComputerProps) {
  const { t } = useT()

  return (
    <section data-testid="research-computer" className="space-y-5">
      <header className="border-b border-border pb-4">
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted">进度 · 证据 · 记录</p>
        <h2 className="mt-1 font-serif text-[1.2rem] text-ink">研究进度</h2>
        <p className="mt-1 text-xs leading-5 text-muted">研究结构、数据与设计、证据与写作、运行记录</p>
      </header>

      <section data-testid="research-structure" className="rounded-lg border border-border bg-panel p-3">
        <h3 className="mb-3 font-serif text-sm text-ink">研究结构</h3>
        <PaperPath {...paperPath} onSelect={onSelectPath} />
      </section>

      <section data-testid="research-data-design" className="rounded-lg border border-border bg-panel p-3">
        <h3 className="font-serif text-sm text-ink">数据与设计</h3>
        <dl className="mt-3 space-y-2 text-xs leading-5">
          <div>
            <dt className="text-muted">数据集</dt>
            <dd data-testid="research-dataset" className="text-ink">{recorded(csvName, '尚未上传')}</dd>
          </div>
          <div>
            <dt className="text-muted">样本</dt>
            <dd data-testid="research-sample" className="text-ink">
              {csvRows == null && csvCols == null
                ? '尚无样本记录'
                : `${recorded(csvRows, '—')} 行 × ${recorded(csvCols, '—')} 列`}
            </dd>
          </div>
          <div>
            <dt className="text-muted">研究方向</dt>
            <dd data-testid="research-direction" className="text-ink">{recorded(directionSummary, '尚未提交')}</dd>
          </div>
          <div>
            <dt className="text-muted">变量 / 方法</dt>
            <dd data-testid="research-design" className="text-ink">
              {(() => {
                const parts = [
                  directionDv ? `结果 ${directionDv}` : null,
                  directionIv ? `解释 ${directionIv}` : null,
                  directionMethod ? `方法 ${directionMethod}` : null,
                ].filter(Boolean)
                return parts.length > 0 ? parts.join(' · ') : '尚未形成设计'
              })()}
            </dd>
          </div>
        </dl>
      </section>

      <section data-testid="research-evidence-writing" className="rounded-lg border border-border bg-panel p-3">
        <h3 className="font-serif text-sm text-ink">证据 / 写作</h3>
        <details
          ref={evidenceRef}
          data-testid="research-evidence-explanation"
          open={evidenceOpen}
          onToggle={(event) => onEvidenceOpenChange(event.currentTarget.open)}
          className="mt-3 border-t border-border pt-3"
        >
          <summary className="cursor-pointer text-xs text-ink">为什么能这么读：识别说明、稳健性检查、主结果记录</summary>
          <dl className="mt-3 space-y-2 text-xs leading-5">
            <div>
              <dt className="text-muted">识别说明</dt>
              <dd data-testid="research-identification-report" className="whitespace-pre-wrap text-ink">
                {identReport || (identFailed ? '识别未通过，等待重新打开研究设计。' : '尚无识别说明')}
              </dd>
            </div>
            <div>
              <dt className="text-muted">稳健性</dt>
              <dd data-testid="research-robustness" className="text-ink">
                {recorded(robustnessStatus)}
              </dd>
            </div>
            <div>
              <dt className="text-muted">主结果记录</dt>
              <dd data-testid="research-estimate-record" className="whitespace-pre-wrap text-ink">
                {estimate?.history_compact || estimate?.status || (hasSuccessfulEstimate ? '主结果已记录' : '还没有主结果记录')}
              </dd>
            </div>
          </dl>
        </details>

        {sessionId && review ? (
          <div className="mt-4 border-t border-border pt-4">
            <ReviewPanel sessionId={sessionId} review={review} onDecision={onDecision} />
          </div>
        ) : (
          <p data-testid="review-idle" className="mt-4 border-t border-border pt-3 text-xs leading-6 text-muted">
            {hasReadout ? t('bench.reviewAfterWrite') : t('bench.reviewAfterDirection')}
          </p>
        )}
      </section>

      <section data-testid="research-run-records" className="rounded-lg border border-border bg-panel p-3">
        <h3 className="font-serif text-sm text-ink">运行记录</h3>
        {sessionId ? <RunTracePanel sessionId={sessionId} /> : <p className="mt-2 text-xs text-muted">尚无运行记录</p>}
        {degradations.length > 0 ? (
          <p data-testid="research-degradation" className="mt-3 border-t border-border pt-3 text-[11px] leading-5 text-muted">
            {degradations[0].node}: {degradations[0].reason}
          </p>
        ) : null}
      </section>
    </section>
  )
}
