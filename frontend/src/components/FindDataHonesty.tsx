/**
 * FD-FE-honesty labels. Sketch (econpaper-ui-temp/flow-sketch) is draft intent only.
 * This is not attach, not find success for teaching shelf or captain-local-real.
 */

import { useT } from '../lib/i18n'
import {
  displayKindForGroup,
  groupFindDataHonesty,
  honestyKindCopyKey,
} from '../lib/findDataHonesty'
import type {
  FindDataHonestyCandidate,
  FindDataHonestyInput,
  FindDataHonestyLists,
} from '../types/findDataHonesty'

function CandidateRow({
  row,
  group,
}: {
  row: FindDataHonestyCandidate
  group: keyof FindDataHonestyLists
}) {
  const { t } = useT()
  const displayKind = displayKindForGroup(row, group)
  const kindKey = honestyKindCopyKey(displayKind)
  return (
    <li
      data-testid={`find-data-card-${row.source_id}`}
      data-source-kind={displayKind ?? ''}
      className="rounded-md border border-wb-line bg-wb-surface px-3 py-2.5"
    >
      <p className="text-[14px] leading-6 text-wb-ink">{row.title}</p>
      {kindKey ? (
        <p className="mt-1 font-mono text-[11px] text-wb-muted">{t(kindKey)}</p>
      ) : null}
      <p className="mt-1 break-all font-mono text-[11px] text-wb-faint">{row.url_or_fixture}</p>
    </li>
  )
}

function HonestySection({
  testId,
  titleKey,
  hintKey,
  rows,
  group,
}: {
  testId: string
  titleKey: string
  hintKey: string
  rows: FindDataHonestyCandidate[]
  group: keyof FindDataHonestyLists
}) {
  const { t } = useT()
  if (rows.length === 0) return null
  return (
    <section data-testid={testId} className="space-y-2">
      <header>
        <h3 className="font-serif text-[1.05rem] text-wb-ink">{t(titleKey)}</h3>
        <p className="mt-1 text-[12px] leading-5 text-wb-muted">{t(hintKey)}</p>
      </header>
      <ul className="space-y-2">
        {rows.map((row) => (
          <CandidateRow key={row.source_id} row={row} group={group} />
        ))}
      </ul>
    </section>
  )
}

export function FindDataHonesty({ candidates, teaching_shelf }: FindDataHonestyInput) {
  const { t } = useT()
  const lists = groupFindDataHonesty({ candidates, teaching_shelf })
  const hasAny =
    lists.findResults.length +
      lists.externalLinks.length +
      lists.captainLocalReal.length +
      lists.teachingShelf.length +
      lists.userUploads.length >
    0
  if (!hasAny) return null

  return (
    <div data-testid="find-data-honesty" className="space-y-6">
      <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-wb-faint">
        {t('findData.kicker')}
      </p>
      <HonestySection
        testId="find-data-find-results"
        titleKey="findData.findResults"
        hintKey="findData.findResultsHint"
        rows={lists.findResults}
        group="findResults"
      />
      <HonestySection
        testId="find-data-external-links"
        titleKey="findData.externalLink"
        hintKey="findData.externalLinkHint"
        rows={lists.externalLinks}
        group="externalLinks"
      />
      <HonestySection
        testId="find-data-captain-local-real"
        titleKey="findData.captainLocalReal"
        hintKey="findData.captainLocalRealHint"
        rows={lists.captainLocalReal}
        group="captainLocalReal"
      />
      <HonestySection
        testId="find-data-teaching-shelf"
        titleKey="findData.teachingShelf"
        hintKey="findData.teachingShelfHint"
        rows={lists.teachingShelf}
        group="teachingShelf"
      />
      <HonestySection
        testId="find-data-user-upload"
        titleKey="findData.userUpload"
        hintKey="findData.userUploadHint"
        rows={lists.userUploads}
        group="userUploads"
      />
    </div>
  )
}
