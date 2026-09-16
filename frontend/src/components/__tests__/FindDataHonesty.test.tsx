import { describe, expect, test } from 'vitest'
import { render, screen } from '@testing-library/react'
import { FindDataHonesty } from '../FindDataHonesty'
import { I18nProvider } from '../../lib/i18n'
import { FIND_DATA_FORBIDDEN_FOUND_COPY } from '../../lib/findDataHonesty'
import type { FindDataHonestyCandidate } from '../../types/findDataHonesty'

function row(
  partial: Partial<FindDataHonestyCandidate> & Pick<FindDataHonestyCandidate, 'source_id'>,
): FindDataHonestyCandidate {
  return {
    title: partial.title ?? partial.source_id,
    url_or_fixture: partial.url_or_fixture ?? 'https://doi.org/10.7910/DVN/EXAMPLE',
    license: partial.license ?? 'CC0',
    ...partial,
    source_id: partial.source_id,
  }
}

function renderHonesty(props: {
  candidates?: FindDataHonestyCandidate[]
  teaching_shelf?: FindDataHonestyCandidate[]
}) {
  return render(
    <I18nProvider>
      <FindDataHonesty {...props} />
    </I18nProvider>,
  )
}

const MIX: FindDataHonestyCandidate[] = [
  row({
    source_id: 'dataverse:doi:10.7910/DVN/EXAMPLE',
    source_kind: 'discovered',
    title: 'Example replication package',
  }),
  row({
    source_id: 'wdi:fetched',
    source_kind: 'fetched',
    title: 'WDI series in session',
    url_or_fixture: 'https://data.worldbank.org/indicator/NY.GDP.PCAP.CD',
  }),
  row({
    source_id: 'ipums:cps',
    source_kind: 'external_link',
    title: 'IPUMS CPS / USA extracts',
    url_or_fixture: 'https://cps.ipums.org/cps/',
  }),
  row({
    source_id: 'captain-local-real:upload',
    source_kind: 'captain_local_real',
    source: 'captain-local-real',
    title: 'Captain-local real panel',
    url_or_fixture: '(session upload; .dta or CSV)',
  }),
  row({
    source_id: 'classic-5:ck1994_long',
    source_kind: 'teaching_fixture',
    title: 'Card and Krueger minimum wage',
    url_or_fixture: 'fixtures/classic-5/ck1994_long.csv',
  }),
  row({
    source_id: 'user:own',
    source_kind: 'user_upload',
    title: 'Own panel',
    url_or_fixture: '(session upload)',
  }),
  row({
    source_id: 'toy-course',
    source_kind: 'discovered',
    title: 'course-panel.csv',
    url_or_fixture: '/samples/course-panel.csv',
  }),
]

describe('FindDataHonesty labels', () => {
  test('separates discovered, fetched, external_link, captain-local-real, teaching shelf, upload', () => {
    renderHonesty({ candidates: MIX })

    const find = screen.getByTestId('find-data-find-results')
    expect(find).toHaveTextContent('检索结果')
    expect(find).toHaveTextContent('检索到')
    expect(find).toHaveTextContent('已下载到本会话')
    expect(find).toHaveTextContent('Example replication package')
    expect(find).not.toHaveTextContent('Card and Krueger')
    expect(find).not.toHaveTextContent('Captain-local')
    expect(find).not.toHaveTextContent('IPUMS')
    expect(find).not.toHaveTextContent('course-panel.csv')

    const shelf = screen.getByTestId('find-data-teaching-shelf')
    expect(shelf).toHaveTextContent('教学已知样本（不是检索结果）')
    expect(shelf).toHaveTextContent('Card and Krueger minimum wage')
    expect(shelf).not.toHaveTextContent('Example replication package')

    const captain = screen.getByTestId('find-data-captain-local-real')
    expect(captain).toHaveTextContent('船长本地真实面板（不是检索结果）')
    expect(captain).toHaveTextContent('Captain-local real panel')
    expect(captain).not.toHaveTextContent('检索到')

    const link = screen.getByTestId('find-data-external-links')
    expect(link).toHaveTextContent('公开链接；请下载后上传')
    expect(link).toHaveTextContent('IPUMS CPS')
    expect(link).not.toHaveTextContent('检索到')

    const upload = screen.getByTestId('find-data-user-upload')
    expect(upload).toHaveTextContent('上传你自己的文件')
    expect(upload).toHaveTextContent('Own panel')

    expect(screen.queryByTestId('find-data-card-toy-course')).not.toBeInTheDocument()
  })

  test('fixture and captain regions do not use found-data copy', () => {
    renderHonesty({ candidates: MIX })
    const surfaces = [
      screen.getByTestId('find-data-teaching-shelf'),
      screen.getByTestId('find-data-captain-local-real'),
      screen.getByTestId('find-data-external-links'),
      screen.getByTestId('find-data-user-upload'),
    ]
    for (const node of surfaces) {
      const text = node.textContent ?? ''
      for (const phrase of FIND_DATA_FORBIDDEN_FOUND_COPY) {
        expect(text.toLowerCase()).not.toContain(phrase.toLowerCase())
      }
    }
  })

  test('empty input renders nothing (missing shelf is not a find failure)', () => {
    const { container } = renderHonesty({ candidates: [] })
    expect(container.querySelector('[data-testid="find-data-honesty"]')).toBeNull()
  })
})
