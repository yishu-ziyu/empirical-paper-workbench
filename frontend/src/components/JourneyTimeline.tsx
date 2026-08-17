import { useState } from 'react'
import { useT } from '../lib/i18n'
import type { JourneyStage } from '../types/journey'

export interface JourneyTimelineProps {
  sessionId: string | null
  currentStage: number
  stages: JourneyStage[]
  onStageClick?: (stageIndex: number) => void
}

function getStatusBgColor(status: JourneyStage['status']): string {
  switch (status) {
    case 'active':
      return 'bg-paper border-accent'
    case 'completed':
      return 'bg-panel border-border'
    case 'interrupt':
      return 'bg-paper border-accent'
    case 'pending':
      return 'bg-bg border-border'
  }
}

function getStatusTextColor(status: JourneyStage['status']): string {
  switch (status) {
    case 'active':
      return 'text-accent'
    case 'completed':
      return 'text-ink'
    case 'interrupt':
      return 'text-accent'
    case 'pending':
      return 'text-muted'
  }
}

export default function JourneyTimeline({
  sessionId,
  currentStage,
  stages,
  onStageClick,
}: JourneyTimelineProps) {
  const { t } = useT()
  const [expandedStage, setExpandedStage] = useState<number | null>(null)

  if (stages.length === 0) {
    return null
  }

  const handleClick = (index: number) => {
    setExpandedStage(expandedStage === index ? null : index)
    onStageClick?.(index)
  }

  // Step 0 → journey.step{i+1}  1-indexed stage keys
  const stepKeys = Array.from({ length: stages.length }, (_, i) => i + 1)

  return (
    <div className="border-b border-border bg-panel/50 px-6 py-4">
      <h2 className="mb-3 text-sm font-semibold text-ink">{t('journey.title')}</h2>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3 lg:grid-cols-8">
        {stepKeys.map((stepNum, index) => {
          const stage = stages[index]
          const isExpanded = expandedStage === index
          const statusBg = getStatusBgColor(stage.status)
          const statusText = getStatusTextColor(stage.status)

          return (
            <div
              key={index}
              data-testid={`journey-stage-${index}`}
              className={`group cursor-pointer rounded-lg border p-3 transition-colors duration-200 ${statusBg} ${
                currentStage === index ? 'border-accent' : ''
              } ${isExpanded ? 'row-span-2' : ''}`}
              onClick={() => handleClick(index)}
            >
              <div className="flex items-start justify-between gap-2">
                <h3 className={`text-xs font-semibold ${statusText}`}>
                  {t(`journey.step${stepNum}.title`)}
                </h3>
                {stage.canIntervene && (
                  <span className="inline-flex items-center rounded-full bg-accent/10 px-2 py-0.5 text-[10px] font-medium text-accent">
                    {t('journey.intervene')}
                  </span>
                )}
              </div>
              {isExpanded && (
                <p className={`mt-2 text-xs leading-relaxed ${statusText} opacity-80`}>
                  {t(`journey.step${stepNum}.desc`)}
                </p>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}