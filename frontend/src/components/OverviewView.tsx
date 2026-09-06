import type { WorkspaceApi } from '../lib/workspace'
import type { WorkbenchViewId } from './WorkbenchSidebar'
import { formatStatValue, parseEstimateRows } from '../lib/readoutTable'

export interface OverviewViewProps {
  ws: WorkspaceApi
  sessionId: string | null
  hasSuccessfulEstimate: boolean
  onSelectView: (id: WorkbenchViewId) => void
  onOpenEvidence: () => void
  onOpenDirection: () => void
}

type StationStatus = 'done' | 'active' | 'pending' | 'blocked'

interface Station {
  id: string
  label: string
  view: WorkbenchViewId
  status: StationStatus
  hint: string
}

/**
 * Overview（契约 C2）：统计卡行 + 六站研究进度 + Key Results + 最近记录。
 * 全部输入来自 snapshot 投影（ws）；拿不准的状态宁可显示 pending，
 * 不虚报进度，也不伪造时间戳（snapshot 里没有 last-run 时间字段）。
 */
export default function OverviewView({
  ws,
  sessionId,
  hasSuccessfulEstimate,
  onSelectView,
  onOpenEvidence,
  onOpenDirection,
}: OverviewViewProps) {
  const cleanedCount = Array.isArray(ws.cleaningReport?.steps)
    ? (ws.cleaningReport.steps as Array<{ status?: string }>).filter(
        (step) => step?.status === 'success',
      ).length
    : 0
  const uploadFailed =
    ws.uploadReadiness === 'FAILED' || ws.uploadReadiness === 'CANCELLED'

  const writtenCount = ws.writtenChapters.filter((ch) => Boolean(ch.content)).length
  const pendingApprovals = ws.writtenChapters.filter(
    (ch) => Boolean(ch.content) && ch.status !== 'approved',
  ).length

  const stations: Station[] = [
    {
      id: 'data',
      label: '数据清洗',
      view: 'data',
      status: uploadFailed
        ? 'blocked'
        : cleanedCount > 0
          ? 'done'
          : ws.dataset
            ? 'done'
            : 'pending',
      hint: uploadFailed
        ? '清理未完成'
        : cleanedCount > 0
          ? `${cleanedCount} 步完成`
          : ws.dataset
            ? '数据已就位'
            : '待上传',
    },
    {
      id: 'design',
      label: '设计设定',
      view: 'design',
      status: ws.identFailed
        ? 'blocked'
        : ws.directionSummary
          ? 'done'
          : ws.directionBusy
            ? 'active'
            : 'pending',
      hint: ws.identFailed
        ? '识别未通过'
        : ws.directionSummary
          ? ws.directionRecord?.method || '已提交'
          : '待方向',
    },
    {
      id: 'estimate',
      label: '主结果',
      view: 'evidence',
      status:
        ws.estimateMeta?.status === 'error' || (ws.identFailed && Boolean(ws.directionSummary))
          ? 'blocked'
          : hasSuccessfulEstimate
            ? 'done'
            : ws.directionBusy
              ? 'active'
              : 'pending',
      hint: hasSuccessfulEstimate
        ? `β ${formatStatValue(ws.estimateMeta?.coef, 'coef')}`
        : ws.estimateMeta?.status === 'error'
          ? '估计失败'
          : ws.directionBusy
            ? '估计中'
            : '待估计',
    },
    {
      id: 'robustness',
      label: '稳健性',
      view: 'evidence',
      status:
        ws.robustnessStatus === 'ran' || ws.robustnessStatus === 'degraded'
          ? 'done'
          : ws.robustnessStatus === 'error' || ws.robustnessStatus === 'failed'
            ? 'blocked'
            : 'pending',
      hint:
        ws.robustnessStatus === 'degraded'
          ? '已跑（降级）'
          : ws.robustnessStatus === 'ran'
            ? '已跑'
            : ws.robustnessStatus
              ? String(ws.robustnessStatus)
              : '未运行',
    },
    {
      id: 'literature',
      label: '文献',
      view: 'literature',
      status: ws.literatureSource ? 'done' : 'pending',
      hint: ws.literatureSource ? String(ws.literatureSource) : '未检索',
    },
    {
      id: 'paper',
      label: '论文',
      view: 'paper',
      status:
        writtenCount > 0
          ? ws.canExport && pendingApprovals === 0 && !ws.writeBusy
            ? 'done'
            : 'active'
          : ws.outline.length > 0 || ws.writeBusy
            ? 'active'
            : 'pending',
      hint:
        ws.outline.length > 0
          ? `${writtenCount}/${ws.outline.length} 章有正文`
          : '待大纲',
    },
  ]

  const doneCount = stations.filter((s) => s.status === 'done').length
  const tableRows = parseEstimateRows(
    (ws.mainResults as string | null) ??
      (ws.estimateMeta?.results as string | null) ??
      (ws.estimateMeta?.table_rows as string | null) ??
      (ws.estimateMeta?.treatment_row as string | null),
  )

  const lastRunText = ws.activeRun
    ? `运行中 · ${ws.activeRun.kind === 'upload_pipeline' ? '数据管道' : '研究流程'}`
    : ws.uploading
      ? '数据管道运行中'
      : ws.directionBusy
        ? '估计运行中'
        : ws.runFailure
          ? '上次运行失败'
          : hasSuccessfulEstimate
            ? '主结果已生成'
            : cleanedCount > 0
              ? '数据清理完成'
              : '暂无运行'

  return (
    <div data-testid="overview-view" className="wb-pane-enter mx-auto max-w-[52rem] px-6 py-8 sm:px-8">
      {/* 统计卡行：全部来自 snapshot 事实，无时间戳就不显示时间 */}
      <div data-testid="overview-stats" className="wb-stagger grid grid-cols-2 gap-3 lg:grid-cols-4">
        <div
          data-testid="overview-stat-dataset"
          className="rounded-lg border border-wb-line bg-wb-surface px-4 py-3"
        >
          <p className="text-[11px] font-medium text-wb-muted">数据集</p>
          <p className="mt-1 truncate text-[15px] font-semibold text-wb-ink" title={ws.csvName ?? undefined}>
            {ws.csvName || '未上传'}
          </p>
          <p className="mt-0.5 text-[11px] text-wb-faint">
            {ws.dataset ? `${ws.dataset.columns?.length ?? 0} 列` : '—'}
          </p>
        </div>
        <div
          data-testid="overview-stat-sample"
          className="rounded-lg border border-wb-line bg-wb-surface px-4 py-3"
        >
          <p className="text-[11px] font-medium text-wb-muted">样本行数</p>
          <p className="mt-1 font-mono text-[15px] font-semibold tabular-nums text-wb-ink">
            {ws.csvRows != null ? `N ${formatStatValue(ws.csvRows, 'n')}` : '—'}
          </p>
          <p className="mt-0.5 text-[11px] text-wb-faint">{ws.csvRows != null ? '行' : '待上传'}</p>
        </div>
        <div
          data-testid="overview-stat-method"
          className="rounded-lg border border-wb-line bg-wb-surface px-4 py-3"
        >
          <p className="text-[11px] font-medium text-wb-muted">主方法</p>
          <p className="mt-1 truncate font-mono text-[15px] font-semibold text-wb-ink">
            {ws.directionRecord?.method || (ws.estimateMeta?.method as string | undefined) || '—'}
          </p>
          <p className="mt-0.5 text-[11px] text-wb-faint">
            {ws.directionSummary ? '来自研究设定' : '未设定'}
          </p>
        </div>
        <div
          data-testid="overview-stat-run"
          className="rounded-lg border border-wb-line bg-wb-surface px-4 py-3"
        >
          <p className="text-[11px] font-medium text-wb-muted">上次运行</p>
          <p
            className={`mt-1 truncate text-[15px] font-semibold ${
              ws.runFailure ? 'text-wb-danger' : 'text-wb-ink'
            }`}
          >
            {lastRunText}
          </p>
          <p className="mt-0.5 text-[11px] text-wb-faint">
            {ws.activeRun ? String(ws.activeRun.status) : '—'}
          </p>
        </div>
      </div>

      {/* 六站研究进度 stepper */}
      <section
        data-testid="overview-stepper"
        className="mt-4 rounded-lg border border-wb-line bg-wb-surface px-4 py-4"
      >
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-[13px] font-semibold text-wb-ink">研究进度</h2>
          <span data-testid="overview-progress-count" className="font-mono text-[11px] text-wb-muted">
            {doneCount} / 6 完成
          </span>
        </div>
        <ol className="grid grid-cols-3 gap-y-3 sm:grid-cols-6 sm:gap-y-0">
          {stations.map((station, index) => (
            <li key={station.id} className="relative">
              {index < stations.length - 1 && (
                <span
                  aria-hidden
                  className={`absolute left-[calc(50%+14px)] right-[calc(-50%+14px)] top-[11px] hidden h-px sm:block ${
                    stations[index].status === 'done' ? 'bg-wb-success/50' : 'bg-wb-line'
                  }`}
                />
              )}
              <button
                type="button"
                data-testid={`overview-step-${station.id}`}
                data-status={station.status}
                onClick={() => onSelectView(station.view)}
                className="wb-press group flex w-full flex-col items-center gap-1.5 px-1 py-1"
              >
                <span
                  aria-hidden
                  className={`flex h-[22px] w-[22px] items-center justify-center rounded-full border text-[11px] font-semibold ${
                    station.status === 'done'
                      ? 'border-wb-success bg-wb-success text-white'
                      : station.status === 'active'
                        ? 'border-wb-primary bg-wb-primary-soft text-wb-primary'
                        : station.status === 'blocked'
                          ? 'border-wb-danger bg-wb-danger-soft text-wb-danger'
                          : 'border-wb-line-strong bg-wb-surface text-wb-faint'
                  }`}
                >
                  {station.status === 'done'
                    ? '✓'
                    : station.status === 'blocked'
                      ? '!'
                      : station.status === 'active'
                        ? '●'
                        : index + 1}
                </span>
                <span
                  className={`text-center text-[11px] leading-4 ${
                    station.status === 'pending'
                      ? 'text-wb-faint'
                      : station.status === 'blocked'
                        ? 'text-wb-danger'
                        : 'text-wb-ink'
                  }`}
                >
                  {station.label}
                  <span className="block truncate font-mono text-[10px] text-wb-faint" title={station.hint}>
                    {station.hint}
                  </span>
                </span>
              </button>
            </li>
          ))}
        </ol>
      </section>

      {/* Key Results：真实 estimate 表 */}
      <section
        data-testid="overview-key-results"
        className="mt-4 rounded-lg border border-wb-line bg-wb-surface px-4 py-4"
      >
        <div className="mb-3 flex items-center justify-between gap-3">
          <div>
            <h2 className="text-[13px] font-semibold text-wb-ink">主结果</h2>
            <p className="mt-0.5 text-[11px] text-wb-faint">当前设定下的主要估计</p>
          </div>
          {ws.hasReadout ? (
            <button
              type="button"
              data-testid="evidence-why"
              onClick={onOpenEvidence}
              className="wb-press rounded-md border border-wb-line px-2.5 py-1 text-[12px] text-wb-ink hover:bg-wb-subtle"
            >
              为什么？看证据 →
            </button>
          ) : null}
        </div>
        {tableRows.length > 0 ? (
          <div className="overflow-x-auto">
            <table data-testid="overview-results-table" className="w-full border-collapse text-left">
              <thead>
                <tr className="border-b border-wb-line-strong text-[11px] text-wb-muted">
                  <th className="py-1.5 pr-3 font-medium">变量</th>
                  <th className="py-1.5 pr-3 text-right font-medium">系数</th>
                  <th className="py-1.5 pr-3 text-right font-medium">标准误</th>
                  <th className="py-1.5 text-right font-medium">p 值</th>
                </tr>
              </thead>
              <tbody className="font-mono text-[12.5px] tabular-nums text-wb-ink">
                {tableRows.map((row) => (
                  <tr key={`${row.variable}-${row.coef}`} className="border-b border-wb-line last:border-0">
                    <td className="py-1.5 pr-3">{row.variable}</td>
                    <td className="py-1.5 pr-3 text-right">{row.coef}</td>
                    <td className="py-1.5 pr-3 text-right">{row.se}</td>
                    <td className="py-1.5 text-right">{row.p}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-dashed border-wb-line-strong px-3 py-4">
            <p className="text-[12.5px] text-wb-muted">
              {ws.estimateMeta?.status === 'error'
                ? '上次估计失败，尚无可引用的主结果。'
                : '还没有主结果。提交研究方向后系统会真实估计。'}
            </p>
            <button
              type="button"
              data-testid="overview-run-cta"
              onClick={onOpenDirection}
              className="wb-press rounded-md bg-wb-primary px-3 py-1.5 text-[12px] font-medium text-white hover:bg-wb-primary-strong"
            >
              {ws.directionBusy ? '估计中…' : 'Run'}
            </button>
          </div>
        )}
      </section>

      {/* Recent：降级记录 / 运行失败；都没有就如实说，不造假活动流 */}
      <section
        data-testid="overview-recent"
        className="mt-4 rounded-lg border border-wb-line bg-wb-surface px-4 py-4"
      >
        <h2 className="mb-2 text-[13px] font-semibold text-wb-ink">最近记录</h2>
        {ws.degradations.length > 0 || ws.runFailure ? (
          <ul className="space-y-1.5">
            {ws.runFailure ? (
              <li data-testid="overview-recent-item" className="text-[12.5px] leading-5 text-wb-danger">
                上次运行失败：{ws.runFailure}
              </li>
            ) : null}
            {ws.degradations.slice(0, 4).map((deg, i) => (
              <li
                key={`${deg.node}-${i}`}
                data-testid="overview-recent-item"
                className="text-[12.5px] leading-5 text-wb-muted"
              >
                <span className="font-mono text-[11px] text-wb-warning">{deg.node}</span>{' '}
                {deg.reason}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-[12.5px] text-wb-muted">{lastRunText}；降级与异常会记录在这里。</p>
        )}
        {!sessionId ? (
          <p className="mt-2 text-[11px] text-wb-faint">上传数据后这里开始记录研究过程。</p>
        ) : null}
      </section>
    </div>
  )
}
