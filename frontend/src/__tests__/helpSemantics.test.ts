// @ts-nocheck
import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, test } from 'vitest'
import { I18N_MESSAGES } from '../lib/i18n'

const here = dirname(fileURLToPath(import.meta.url))
const terminology = readFileSync(resolve(here, '../../../docs/product/terminology.md'), 'utf8')
const i18nSource = readFileSync(resolve(here, '../lib/i18nWorkbench.ts'), 'utf8')

const FORBIDDEN = [
  '研究结论所依据的数字，以及导出代码里的主估计，都会跟着当前主分析走',
  '论文结果章、研究结论所依据的数字，以及导出代码里的主估计，都会跟着当前主分析走',
  '主分析或估计更新后，旧结论不会自动当作仍成立',
  '估计或主分析变了，旧结论不能继续当作已核对',
  'The results chapter, research claims, and exported main estimate follow the primary analysis',
  'After the primary analysis or estimates update, an old claim is not still checked',
]

describe('Promote / Stale help semantics', () => {
  test('forbidden phrases do not reappear in terminology or i18nWorkbench', () => {
    const haystack = `${terminology}\n${i18nSource}\n${I18N_MESSAGES.zh['evidence.helpPromoteMore']}\n${I18N_MESSAGES.en['evidence.helpPromoteMore']}\n${I18N_MESSAGES.zh['claim.helpStaleMore']}\n${I18N_MESSAGES.en['claim.helpStaleMore']}`
    for (const phrase of FORBIDDEN) {
      expect(haystack).not.toContain(phrase)
    }
  })

  test('Promote copy keeps claims bound and does not rewrite them', () => {
    const promoteZh = I18N_MESSAGES.zh['evidence.helpPromoteMore']
    const promoteEn = I18N_MESSAGES.en['evidence.helpPromoteMore']
    expect(promoteZh).toMatch(/绑定/)
    expect(promoteZh).toMatch(/mismatch/)
    expect(promoteZh).toMatch(/不会改写结论/)
    expect(promoteEn).toMatch(/stay bound/i)
    expect(promoteEn).toMatch(/mismatch/i)
    expect(promoteEn).toMatch(/does not rewrite/i)
  })

  test('Stale copy is evidence-set change, distinct from Promote and mismatch', () => {
    const staleZh = I18N_MESSAGES.zh['claim.helpStaleMore']
    const staleEn = I18N_MESSAGES.en['claim.helpStaleMore']
    expect(staleZh).toMatch(/证据集合|相关证据/)
    expect(staleZh).toMatch(/设为主分析或恢复已有运行本身不会/)
    expect(staleZh).toMatch(/mismatch 与 stale/)
    expect(staleEn).toMatch(/evidence set/i)
    expect(staleEn).toMatch(/Promote and revert do not/i)
    expect(staleEn).toMatch(/Mismatch and stale are different/i)
    expect(terminology).toMatch(/相关证据更新了/)
    expect(terminology).not.toMatch(/估计或主分析变了，旧结论不能继续当作已核对/)
  })
})
