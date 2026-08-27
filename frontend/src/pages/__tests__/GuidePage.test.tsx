import { describe, test, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { ComponentProps } from 'react'
import GuidePage from '../GuidePage'
import { I18nProvider } from '../../lib/i18n'

function renderGuide(props: Partial<ComponentProps<typeof GuidePage>> = {}) {
  return render(
    <I18nProvider>
      <GuidePage
        onPickData={vi.fn()}
        onTrySample={vi.fn()}
        onWritePaper={vi.fn()}
        {...props}
      />
    </I18nProvider>,
  )
}

describe('GuidePage 进门介绍', () => {
  test('说清产品做什么，并列出四步', () => {
    renderGuide()
    expect(screen.getByTestId('guide-page')).toBeInTheDocument()
    expect(screen.getByText('用数据写实证论文')).toBeInTheDocument()
    expect(screen.getByTestId('guide-steps')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: '四步写出论文' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: '上传 CSV' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: '填写研究设计' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: '看估计' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: '按章写，再导出' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: '生成论文长什么样' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: '从上传到导出，你都在场' })).toBeInTheDocument()
    expect(screen.queryByTestId('direction-section')).not.toBeInTheDocument()
  })

  test('我有数据 / 课设样例 / 先写在纸上 都能点', async () => {
    const user = userEvent.setup()
    const onPickData = vi.fn()
    const onTrySample = vi.fn()
    const onWritePaper = vi.fn()
    renderGuide({ onPickData, onTrySample, onWritePaper })
    await user.click(screen.getByTestId('guide-upload-btn'))
    await user.click(screen.getByTestId('guide-sample-btn'))
    await user.click(screen.getByTestId('guide-write-paper'))
    expect(onPickData).toHaveBeenCalledTimes(1)
    expect(onTrySample).toHaveBeenCalledTimes(1)
    expect(onWritePaper).toHaveBeenCalledTimes(1)
  })
})
