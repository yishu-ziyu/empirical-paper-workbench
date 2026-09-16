import { describe, expect, test } from 'vitest'
import { I18N_MESSAGES } from '../i18n'
import {
  FIND_DATA_FORBIDDEN_FOUND_COPY,
  groupFindDataHonesty,
  honestyKindCopyKey,
  isBannedToyCandidate,
  isFindSuccessKind,
  isInRepoFixtureSignal,
} from '../findDataHonesty'
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

describe('findDataHonesty grouping', () => {
  test('discovered and fetched stay in find results', () => {
    const lists = groupFindDataHonesty({
      candidates: [
        row({ source_id: 'dataverse:1', source_kind: 'discovered', title: 'Dataverse hit' }),
        row({
          source_id: 'card-zip',
          source_kind: 'fetched',
          title: 'Card zip in session',
          url_or_fixture: 'https://davidcard.berkeley.edu/data_sets.html',
        }),
      ],
    })
    expect(lists.findResults.map((c) => c.source_id)).toEqual(['dataverse:1', 'card-zip'])
    expect(lists.teachingShelf).toEqual([])
    expect(isFindSuccessKind('discovered')).toBe(true)
    expect(isFindSuccessKind('fetched')).toBe(true)
  })

  test('teaching_fixture and classic-5 paths never join find results', () => {
    const lists = groupFindDataHonesty({
      candidates: [
        row({
          source_id: 'classic-5:ck1994_long',
          source_kind: 'teaching_fixture',
          title: 'Card and Krueger minimum wage',
          url_or_fixture: 'fixtures/classic-5/ck1994_long.csv',
        }),
        row({
          source_id: 'ck1994_long',
          source_kind: 'discovered',
          title: 'laundered catalog id',
          url_or_fixture: 'fixtures/classic-5/ck1994_long.csv',
        }),
      ],
    })
    expect(lists.findResults).toEqual([])
    expect(lists.teachingShelf.map((c) => c.source_id)).toEqual([
      'classic-5:ck1994_long',
      'ck1994_long',
    ])
    expect(isInRepoFixtureSignal(lists.teachingShelf[0])).toBe(true)
  })

  test('optional teaching_shelf stays a distinct list', () => {
    const lists = groupFindDataHonesty({
      candidates: [
        row({ source_id: 'dataverse:1', source_kind: 'discovered' }),
      ],
      teaching_shelf: [
        row({
          source_id: 'classic-5:barro1991_growth',
          source_kind: 'teaching_fixture',
          url_or_fixture: 'fixtures/classic-5/barro1991_growth.csv',
          title: 'Barro growth extract',
        }),
      ],
    })
    expect(lists.findResults.map((c) => c.source_id)).toEqual(['dataverse:1'])
    expect(lists.teachingShelf.map((c) => c.source_id)).toEqual(['classic-5:barro1991_growth'])
  })

  test('captain_local_real is acquire, never find', () => {
    const lists = groupFindDataHonesty({
      candidates: [
        row({
          source_id: 'captain-local-real:upload',
          source_kind: 'captain_local_real',
          source: 'captain-local-real',
          title: 'Captain-local real panel',
          url_or_fixture: '(session upload; .dta or CSV)',
        }),
        row({
          source_id: 'launder-captain',
          source_kind: 'discovered',
          source: 'captain-local-real',
          title: 'should not be a Dataverse hit',
        }),
      ],
    })
    expect(lists.findResults).toEqual([])
    expect(lists.captainLocalReal.map((c) => c.source_id)).toEqual([
      'captain-local-real:upload',
      'launder-captain',
    ])
    expect(isFindSuccessKind('captain_local_real')).toBe(false)
  })

  test('external_link is honest path, not find success', () => {
    const lists = groupFindDataHonesty({
      candidates: [
        row({
          source_id: 'ipums:cps',
          source_kind: 'external_link',
          title: 'IPUMS CPS',
          url_or_fixture: 'https://cps.ipums.org/cps/',
        }),
      ],
    })
    expect(lists.findResults).toEqual([])
    expect(lists.externalLinks.map((c) => c.source_id)).toEqual(['ipums:cps'])
    expect(isFindSuccessKind('external_link')).toBe(false)
  })

  test('user_upload is not a search hit', () => {
    const lists = groupFindDataHonesty({
      candidates: [
        row({
          source_id: 'user:own',
          source_kind: 'user_upload',
          title: 'Own file',
          url_or_fixture: '(session upload)',
        }),
      ],
    })
    expect(lists.findResults).toEqual([])
    expect(lists.userUploads.map((c) => c.source_id)).toEqual(['user:own'])
  })

  test('missing kind and laundered kinds fail closed (not found)', () => {
    const lists = groupFindDataHonesty({
      candidates: [
        row({ source_id: 'no-kind', title: 'mystery' }),
        row({ source_id: 'rec', source_kind: 'recommended', title: 'launder' }),
        row({ source_id: 'builtin', source_kind: 'builtin_match' }),
      ],
    })
    expect(lists.findResults).toEqual([])
    expect(lists.withheld.map((c) => c.source_id)).toEqual(['no-kind', 'rec', 'builtin'])
  })

  test('banned toys never appear as found, shelf, captain, or link (synthetic names)', () => {
    const toys = [
      row({
        source_id: 'toy-minwage',
        source_kind: 'discovered',
        url_or_fixture: 'agent/spike/fixtures/minimum_wage.csv',
        title: 'minimum_wage.csv',
      }),
      row({
        source_id: 'toy-course',
        source_kind: 'teaching_fixture',
        url_or_fixture: '/samples/course-panel.csv',
        title: 'course-panel.csv',
      }),
      row({
        source_id: 'toy-cfps',
        source_kind: 'captain_local_real',
        url_or_fixture: 'fixtures/cfps_association/sanitized_sample.csv',
        title: 'sanitized_sample.csv',
      }),
    ]
    expect(toys.every(isBannedToyCandidate)).toBe(true)
    const lists = groupFindDataHonesty({ candidates: toys, teaching_shelf: toys })
    expect(lists.findResults).toEqual([])
    expect(lists.teachingShelf).toEqual([])
    expect(lists.captainLocalReal).toEqual([])
    expect(lists.externalLinks).toEqual([])
    expect(lists.withheld).toHaveLength(3)
  })

  test('empty real fetch is not padded with classic-5', () => {
    const lists = groupFindDataHonesty({ candidates: [] })
    expect(lists.findResults).toEqual([])
    expect(lists.teachingShelf).toEqual([])
  })
})

describe('findDataHonesty copy families', () => {
  test('teaching and captain copy keys are not find-success families', () => {
    expect(honestyKindCopyKey('teaching_fixture')).toBe('findData.kind.teaching')
    expect(honestyKindCopyKey('captain_local_real')).toBe('findData.kind.captainLocalReal')
    expect(honestyKindCopyKey('external_link')).toBe('findData.kind.externalLink')
    expect(honestyKindCopyKey('discovered')).toBe('findData.kind.discovered')
    expect(honestyKindCopyKey('fetched')).toBe('findData.kind.fetched')
  })

  test('zh and en teaching/captain/link copy never use found-data phrases', () => {
    const keys = [
      'findData.kind.teaching',
      'findData.kind.captainLocalReal',
      'findData.kind.externalLink',
      'findData.teachingShelf',
      'findData.teachingShelfHint',
      'findData.captainLocalReal',
      'findData.captainLocalRealHint',
      'findData.externalLink',
      'findData.externalLinkHint',
      'findData.userUpload',
      'findData.userUploadHint',
    ] as const
    for (const lang of ['zh', 'en'] as const) {
      for (const key of keys) {
        const text = I18N_MESSAGES[lang][key]
        expect(text).toBeTruthy()
        for (const phrase of FIND_DATA_FORBIDDEN_FOUND_COPY) {
          expect(text.toLowerCase()).not.toContain(phrase.toLowerCase())
        }
      }
      expect(I18N_MESSAGES[lang]['findData.teachingShelf']).toMatch(/不是检索结果|not a find result/)
      expect(I18N_MESSAGES[lang]['findData.captainLocalReal']).toMatch(/不是检索结果|not a find result/)
    }
    expect(I18N_MESSAGES.zh['findData.kind.discovered']).toBe('检索到')
    expect(I18N_MESSAGES.en['findData.kind.discovered']).toBe('Search hit')
    expect(I18N_MESSAGES.zh['findData.kind.teaching']).not.toBe('检索结果')
    expect(I18N_MESSAGES.zh['findData.kind.teaching']).not.toMatch(/发现/)
  })
})
