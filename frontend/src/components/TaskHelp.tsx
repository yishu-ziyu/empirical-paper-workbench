import { useId, useState } from 'react'
import { useT } from '../lib/i18n'

export function TaskHelp({
  summary,
  details,
  testId = 'task-help',
}: {
  summary: string
  details?: string
  testId?: string
}) {
  const { t } = useT()
  const [open, setOpen] = useState(false)
  const detailsId = useId()
  return (
    <span data-testid={testId} className="mt-1 block max-w-[36rem] text-[12px] leading-5 text-wb-muted">
      <span data-testid={`${testId}-summary`}>{summary}</span>
      {details ? (
        <>
          {' '}
          <button
            type="button"
            data-testid={`${testId}-toggle`}
            aria-expanded={open}
            aria-controls={detailsId}
            onClick={() => setOpen((value) => !value)}
            className="text-wb-ink underline underline-offset-2 hover:opacity-80"
          >
            {open ? t('help.close') : t('help.more')}
          </button>
          {open ? (
            <span
              id={detailsId}
              data-testid={`${testId}-details`}
              role="note"
              className="mt-1 block text-[12px] leading-5 text-wb-faint"
            >
              {details}
            </span>
          ) : null}
        </>
      ) : null}
    </span>
  )
}

export function MethodHelp({ method }: { method: 'OLS' | 'IV' }) {
  const { t } = useT()
  const testId = method === 'OLS' ? 'help-ols' : 'help-iv'
  return (
    <span className="inline-flex items-baseline gap-1">
      <abbr title={t(method === 'OLS' ? 'help.olsSummary' : 'help.ivSummary')} className="no-underline">
        {method}
      </abbr>
      <TaskHelp
        testId={testId}
        summary={t(method === 'OLS' ? 'help.olsSummary' : 'help.ivSummary')}
        details={t(method === 'OLS' ? 'help.olsMore' : 'help.ivMore')}
      />
    </span>
  )
}
