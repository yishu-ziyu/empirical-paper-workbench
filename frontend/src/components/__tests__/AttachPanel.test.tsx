import { describe, expect, test, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { ComponentProps } from 'react'
import AttachPanel from '../AttachPanel'
import { I18nProvider } from '../../lib/i18n'
import { fileCandidate } from '../../lib/attachCandidate'

const FORBIDDEN = ['鉴表', '写章', '带走', '先见表']

function renderPanel(
  props: Partial<ComponentProps<typeof AttachPanel>> = {},
) {
  const onBrowse = props.onBrowse ?? vi.fn()
  return render(
    <I18nProvider>
      <AttachPanel onBrowse={onBrowse} {...props} />
    </I18nProvider>,
  )
}

describe('AttachPanel formal TITLE/TOPIC chrome', () => {
  test('renders 找 / 选 / 传 / 确认挂接 and keeps confirm disabled without a candidate', () => {
    renderPanel({ topic: '养老金并轨之后，临近退休的人是不是更早离开劳动力市场？' })

    const panel = screen.getByTestId('attach-panel')
    expect(panel).toHaveTextContent('找')
    expect(panel).toHaveTextContent('选')
    expect(panel).toHaveTextContent('传')
    expect(panel).toHaveTextContent('确认挂接')
    expect(screen.getByTestId('attach-topic')).toHaveTextContent('养老金')
    expect(screen.getByTestId('attach-catalog')).toHaveTextContent('classic-5')
    expect(screen.getByTestId('attach-catalog')).toHaveTextContent('不是你自己的研究')
    expect(screen.queryByText(/sample_wage|sample_panel_mini|wage_panel/)).not.toBeInTheDocument()
    expect(screen.getByTestId('attach-confirm-btn')).toBeDisabled()
    expect(screen.getByTestId('attach-confirm-btn')).toHaveAttribute(
      'title',
      expect.stringMatching(/候选/),
    )
    expect(screen.queryByTestId('table1-pause')).not.toBeInTheDocument()
    expect(screen.queryByTestId('equation-pause')).not.toBeInTheDocument()
    expect(screen.queryByTestId('eda-sidebar')).not.toBeInTheDocument()
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
    for (const slogan of FORBIDDEN) {
      expect(panel).not.toHaveTextContent(slogan)
    }
  })

  test('prefill is a candidate only until confirm-attach', async () => {
    const user = userEvent.setup()
    const onConfirmAttach = vi.fn()
    renderPanel({
      prefill: fileCandidate('own-panel.csv'),
      onConfirmAttach,
    })

    expect(screen.getByTestId('attach-prefill-note')).toBeInTheDocument()
    expect(screen.getByTestId('attach-candidate')).toHaveTextContent('own-panel.csv')
    expect(screen.getByTestId('attach-candidate-status')).toHaveTextContent('候选（未挂接）')
    const confirm = screen.getByTestId('attach-confirm-btn')
    expect(confirm).toBeEnabled()
    expect(onConfirmAttach).not.toHaveBeenCalled()

    await user.click(confirm)
    expect(onConfirmAttach).toHaveBeenCalledTimes(1)
    expect(onConfirmAttach).toHaveBeenCalledWith(fileCandidate('own-panel.csv'))
    expect(screen.getByTestId('attach-candidate-status')).toHaveTextContent('已挂接')
    expect(confirm).toBeDisabled()
    expect(screen.queryByTestId('table1-pause')).not.toBeInTheDocument()
    expect(screen.queryByRole('table')).not.toBeInTheDocument()
  })

  test('dropping a csv on 传 sets candidate and leaves confirm-attach unfired', async () => {
    const user = userEvent.setup()
    const onFile = vi.fn()
    const onConfirmAttach = vi.fn()
    renderPanel({ onFile, onConfirmAttach })

    await user.click(screen.getByTestId('attach-own-file'))
    const zone = screen.getByTestId('csv-drop-zone')
    const file = new File(['a,b\n1,2'], 'wages.csv', { type: 'text/csv' })
    fireEvent.drop(zone, { dataTransfer: { files: [file] } })

    expect(onFile).toHaveBeenCalledWith(file)
    expect(onConfirmAttach).not.toHaveBeenCalled()
    expect(screen.getByTestId('attach-candidate')).toHaveTextContent('wages.csv')
    expect(screen.getByTestId('attach-candidate-status')).toHaveTextContent('候选（未挂接）')
    expect(screen.getByTestId('attach-confirm-btn')).toBeEnabled()
  })

  test('confirm-attach stays disabled while ingest is PROCESSING', () => {
    renderPanel({
      prefill: fileCandidate('panel.csv'),
      uploadReadiness: 'PROCESSING',
    })
    expect(screen.getByTestId('attach-confirm-btn')).toBeDisabled()
    expect(screen.getByTestId('attach-confirm-btn')).toHaveAttribute(
      'title',
      expect.stringMatching(/处理完成/),
    )
    expect(screen.getByTestId('attach-candidate-status')).toHaveTextContent('候选（未挂接）')
  })
})
