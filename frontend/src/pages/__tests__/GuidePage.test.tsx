import { describe, test, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
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
    expect(screen.getByRole('heading', { name: '上传数据' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: '设定研究方向' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: '按章写作' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: '润色并导出' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: '生成论文长什么样' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: '从上传到导出，你都在场' })).toBeInTheDocument()
    expect(screen.getByText('从你的想法开始')).toBeInTheDocument()
    expect(screen.getAllByText(/Word · LaTeX/).length).toBeGreaterThan(0)
    expect(screen.getByText(/Stata \/ R/)).toBeInTheDocument()
    expect(screen.queryByText('guide.statCode')).not.toBeInTheDocument()
    expect(screen.getAllByText('OLS · DiD · IV · RD · SCM').length).toBeGreaterThan(0)
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

  test('可以在首屏直接输入研究想法并发送到对话工作台', async () => {
    const user = userEvent.setup()
    const onWritePaper = vi.fn()
    renderGuide({ onWritePaper })

    const input = screen.getByTestId('guide-idea-input')
    expect(input).toHaveAttribute('placeholder', '描述你的研究想法、问题，或你手头已有的数据…')
    expect(screen.getByTestId('guide-send-idea')).toBeDisabled()

    await user.type(input, '我想研究高铁开通是否促进县域创业')
    await user.click(screen.getByTestId('guide-send-idea'))

    expect(onWritePaper).toHaveBeenCalledWith('我想研究高铁开通是否促进县域创业')
  })

  test('composer accepts table files and rejects other files', () => {
    const onFile = vi.fn()
    renderGuide({ onFile })
    const composer = screen.getByTestId('guide-composer')
    fireEvent.drop(composer, {
      dataTransfer: { files: [new File(['not csv'], 'notes.txt', { type: 'text/plain' })] },
    })
    expect(onFile).not.toHaveBeenCalled()
    expect(screen.getByTestId('upload-error')).toHaveTextContent('CSV')
    fireEvent.drop(composer, {
      dataTransfer: { files: [new File(['a,b\n1,2'], 'panel.CSV', { type: 'text/csv' })] },
    })
    expect(onFile).toHaveBeenCalledTimes(1)
    expect(screen.queryByTestId('upload-error')).not.toBeInTheDocument()
    fireEvent.drop(composer, {
      dataTransfer: { files: [new File(['binary-ish'], 'panel.dta', { type: 'application/octet-stream' })] },
    })
    expect(onFile).toHaveBeenCalledTimes(2)
  })

  test('CSV tile picks a file, sample tile uses the course file, methods is not a station', async () => {
    const user = userEvent.setup()
    const onPickData = vi.fn()
    const onTrySample = vi.fn()
    renderGuide({ onPickData, onTrySample })
    await user.click(screen.getByTestId('guide-source-csv'))
    await user.click(screen.getByTestId('guide-source-sample'))
    expect(onPickData).toHaveBeenCalledTimes(1)
    expect(onTrySample).toHaveBeenCalledTimes(1)
    expect(screen.getByTestId('guide-source-csv').tagName).toBe('BUTTON')
    expect(screen.getByTestId('guide-source-sample').tagName).toBe('BUTTON')
    expect(screen.getByText('识别方法').closest('button')).toBeNull()
  })
})
