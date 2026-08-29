import { useT } from '../lib/i18n'

// 步骤指示器 - 显示当前所处的阶段 (Upload Data → Explore Data → Generate Paper)

export interface StepIndicatorProps {
  sessionId: string | null
  currentStatus: 'running' | 'paused' | 'done' | 'idle'
}

function getStepStatus(step: number, sessionId: string | null, currentStatus: string) {
  if (step === 1) {
    return sessionId ? 'completed' : 'pending'
  }
  if (step === 2) {
    if (!sessionId) return 'pending'
    if (currentStatus === 'idle') return 'active'
    return 'completed'
  }
  // step === 3
  if (!sessionId || currentStatus === 'idle') return 'pending'
  if (currentStatus === 'done') return 'completed'
  return 'active'
}

export default function StepIndicator({ sessionId, currentStatus }: StepIndicatorProps) {
  const { t } = useT()

  const STEPS = [
    { id: 1, label: t('step.uploadData') },
    { id: 2, label: t('step.exploreData') },
    { id: 3, label: t('step.generatePaper') },
  ]

  return (
    <div
      data-testid="step-indicator"
      className="hidden items-center gap-1 text-xs sm:flex"
    >
      {STEPS.map((step, index) => {
        const status = getStepStatus(step.id, sessionId, currentStatus)
        return (
          <div key={step.id} className="flex items-center gap-1">
            {index > 0 && (
              <span className="mx-1 text-muted/40" aria-hidden="true">
                <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                </svg>
              </span>
            )}
            <span
              className={`inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 transition-colors duration-200 ${
                status === 'completed'
                  ? 'text-accent'
                  : status === 'active'
                    ? 'bg-accent/10 font-medium text-accent'
                    : 'text-muted/60'
              }`}
            >
              {status === 'completed' ? (
                <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
              ) : (
                <span className="flex h-3.5 w-3.5 items-center justify-center text-[10px] font-medium">
                  {step.id}
                </span>
              )}
              <span>{step.label}</span>
            </span>
          </div>
        )
      })}
    </div>
  )
}