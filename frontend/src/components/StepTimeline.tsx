/* Hallmark · genre: editorial · design-system: DESIGN.md · designed-as-app · macrostructure: Workbench(步骤卡时间线)
 * 空桌步骤卡时间线（Phase B：把 Agent 循环亮在产品上）。
 *
 * 每步一张卡：方向凝练 → 清洗八步 → 估计门（可展开看轮次摘要/最终代码）→ 各章写作。
 * 数据全部来自既有 state 字段（estimate payload 含 iterations/history_compact/final_code），
 * 不新增接口。门禁语义原样：无主表 ⇒ 结果章锁定。
 */
import { useEffect, useState } from 'react'
import { useT } from '../lib/i18n'
import { apiFetch } from '../lib/apiBase'

export interface StepTimelineProps {
  sessionId?: string | null
  directionSummary: string | null
  cleaningReport: any | null
  estimate: any | null
  estimateBusy: boolean
  hasReadout: boolean
  identFailed: boolean
  outline: Array<{ type: string; title?: string }>
  currentChapterIndex: number
  writtenChapters: Array<{ type: string; content?: string | null }>
  writeBusy: boolean
}

type CardTone = 'done' | 'busy' | 'locked' | 'error'

function Card({
  tone,
  index,
  title,
  meta,
  body,
  children,
  testId,
}: {
  tone: CardTone
  index: string
  title: string
  meta?: string
  body?: string
  children?: React.ReactNode
  testId: string
}) {
  const toneText =
    tone === 'done' ? 'text-accent' : tone === 'error' ? 'text-danger' : tone === 'locked' ? 'text-muted' : 'text-ink'
  const border = tone === 'error' ? 'border-danger/40' : tone === 'done' ? 'border-accent/30' : 'border-border'
  return (
    <section data-testid={testId} className={`rounded-lg border ${border} bg-panel p-3`}>
      <div className="flex items-baseline justify-between gap-3">
        <h3 className={`font-serif text-[15px] leading-snug ${toneText}`}>
          <span className="mr-1.5 font-mono text-xs text-muted">{index}</span>
          {title}
        </h3>
        {meta && <span className={`shrink-0 font-mono text-[11px] ${toneText}`}>{meta}</span>}
      </div>
      {body && <p className="mt-1 text-[12.5px] leading-5 text-muted">{body}</p>}
      {children}
    </section>
  )
}

export default function StepTimeline({
  sessionId,
  directionSummary,
  cleaningReport,
  estimate,
  estimateBusy,
  hasReadout,
  identFailed,
  outline,
  currentChapterIndex,
  writtenChapters,
  writeBusy,
}: StepTimelineProps) {
  const { t, lang } = useT()
  const [stage, setStage] = useState<string | null>(null)

  // 估计运行中：轮询 trace 事件流，把当前节点翻成阶段名（对齐 compaction 的"等待=阶段化反馈"）
  useEffect(() => {
    if (!estimateBusy || !sessionId) {
      setStage(null)
      return
    }
    let alive = true
    const STAGES: Record<string, string> = {
      upload_data: lang === 'zh' ? '读取数据' : 'Reading data',
      clean_data: lang === 'zh' ? '清洗八步' : 'Cleaning data',
      set_direction: lang === 'zh' ? '方向凝练' : 'Refining direction',
      identification_verify: lang === 'zh' ? '识别校验' : 'Verifying identification',
      run_estimate: lang === 'zh' ? '估计中' : 'Estimating',
      robustness_check: lang === 'zh' ? '稳健性检查' : 'Robustness checks',
      search_literature: lang === 'zh' ? '文献检索' : 'Searching literature',
      build_citation_graph: lang === 'zh' ? '引文图' : 'Citation graph',
      generate_title: lang === 'zh' ? '拟定标题' : 'Drafting title',
      generate_outline: lang === 'zh' ? '生成大纲' : 'Generating outline',
      hitl_pause: lang === 'zh' ? '等待人工确认' : 'Waiting for human',
    }
    const poll = async () => {
      try {
        const resp = await apiFetch(`/api/sessions/${sessionId}/trace?limit=5`)
        if (!resp.ok) return
        const data = (await resp.json()) as { events?: Array<{ node: string; status: string }> }
        const last = (data.events ?? []).at(-1)
        if (!alive || !last) return
        const zh = STAGES[last.node]
        if (!zh) return
        // trace 事件状态协议是 ok / error / blocked（见 run_store.append_event），
        // 没有 'done'。ok = 该节点已完成（流水线已推进到这里）→ 展示该阶段；
        // error / blocked = 终态失败/暂停 → 不再展示"进行中"的阶段。
        if (last.status === 'ok') setStage(zh)
        else setStage(null)
      } catch {
        /* 静默：trace 拉不到就不显示阶段 */
      }
    }
    void poll()
    const timer = window.setInterval(poll, 2000)
    return () => {
      alive = false
      window.clearInterval(timer)
    }
  }, [estimateBusy, sessionId, lang])

  // —— 清洗八步：steps 全 success 才算 done ——
  const steps = Array.isArray(cleaningReport?.steps) ? cleaningReport.steps : null
  const stepTotal = steps?.length ?? 0
  const stepOk = steps?.filter((s: any) => s?.status === 'success').length ?? 0
  const cleaningDone = stepTotal > 0 && stepOk === stepTotal

  // —— 估计门：payload 驱动（estimate payload 来自 estimate_agent 或固定分派）——
  const estStatus = estimate?.status
  const estOk = estStatus === 'ok'
  const estError = estStatus === 'error'
  const estTone: CardTone = estimateBusy ? 'busy' : estError ? 'error' : estOk ? 'done' : 'locked'
  const estMeta = estimateBusy
    ? t('deskSteps.running')
    : estOk
      ? `${estimate.estimator ?? ''} · ${estimate.iterations ?? 1} ${t('deskSteps.iterations')}`
      : estError
        ? t('deskSteps.failed')
        : undefined
  const hasAgentTrace = Boolean(estimate?.history_compact || estimate?.final_code)

  const contentOf = (type: string) => writtenChapters.find((ch) => ch.type === type)?.content
  return (
    <div data-testid="step-timeline" className="mb-6 flex flex-col gap-2.5">
      <p className="font-mono text-[11px] uppercase tracking-[0.14em] text-muted">
        {lang === 'zh' ? '步骤卡 · 每步可追溯' : 'Steps · traceable'}
      </p>

      <Card
        testId="step-card-direction"
        tone={directionSummary ? 'done' : 'locked'}
        index="1"
        title={t('deskSteps.direction')}
        meta={directionSummary ? t('deskSteps.approved') : undefined}
        body={directionSummary ?? t('deskSteps.directionWaiting')}
      />

      <Card
        testId="step-card-cleaning"
        tone={cleaningDone ? 'done' : 'locked'}
        index="2"
        title={t('deskSteps.cleaning')}
        meta={cleaningDone ? `${stepOk}/${stepTotal} ✓` : undefined}
        body={
          cleaningDone
            ? t('deskSteps.cleaningDone')
            : steps
              ? t('deskSteps.cleaningPartial').replace('{ok}', String(stepOk)).replace('{total}', String(stepTotal))
              : t('deskSteps.cleaningWaiting')
        }
      />

      <Card
        testId="step-card-estimate"
        tone={estTone}
        index="3"
        title={t('deskSteps.estimate')}
        meta={estMeta}
        body={
          estimateBusy
            ? `${t('deskSteps.estimateRunning')}${stage ? ` — ${t('deskSteps.stageLabel')}: ${stage}` : ''}`
            : estOk
              ? `${estimate.treatment_row ?? ''}`
              : estError
                ? (estimate.error ?? '').slice(0, 160)
                : t('deskSteps.estimateWaiting')
        }
      >
        {estOk && (
          <button
            type="button"
            data-testid="step-see-main-table"
            onClick={() =>
              document
                .querySelector('[data-testid="estimate-readout"]')
                ?.scrollIntoView({ behavior: 'smooth', block: 'start' })
            }
            className="mt-2 text-[12px] text-accent transition-colors duration-150 hover:text-accent/80"
          >
            {t('deskSteps.seeMainTable')}
          </button>
        )}
        {estOk && hasAgentTrace && (
          <details data-testid="step-estimate-trace" className="mt-2">
            <summary className="cursor-pointer font-mono text-[11px] text-muted hover:text-ink">
              {t('deskSteps.trace')}
            </summary>
            {estimate.history_compact && (
              <pre className="mt-1.5 whitespace-pre-wrap rounded bg-cream px-2.5 py-2 font-mono text-[11px] leading-4 text-ink/80">
                {estimate.history_compact}
              </pre>
            )}
            {estimate.final_code && (
              <pre className="mt-1.5 overflow-x-auto whitespace-pre rounded bg-ink/95 px-2.5 py-2 font-mono text-[11px] leading-4 text-paper/90">
                {estimate.final_code}
              </pre>
            )}
          </details>
        )}
      </Card>

      {outline.map((ch, idx) => {
        const content = contentOf(ch.type)
        const isResults = ch.type === 'results'
        const locked = isResults && (!hasReadout || identFailed)
        const tone: CardTone = content ? 'done' : locked ? 'locked' : writeBusy && idx === currentChapterIndex ? 'busy' : 'locked'
        const meta = content
          ? t('deskSteps.written')
          : tone === 'busy'
            ? t('deskSteps.writing')
            : locked
              ? t('deskSteps.locked')
              : t('deskSteps.waitingWrite')
        return (
          <Card
            key={ch.type}
            testId={`step-card-chapter-${ch.type}`}
            tone={tone}
            index={`4.${idx + 1}`}
            title={`${t('deskSteps.write')} · ${ch.title || ch.type}`}
            meta={meta}
            body={locked ? t('deskSteps.needMainTable') : undefined}
          />
        )
      })}
    </div>
  )
}
