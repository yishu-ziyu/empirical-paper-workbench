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

  test('clicking confirm without a backend confirmation never shows 已挂接 (C3 defect)', async () => {
    const user = userEvent.setup()
    const onConfirmAttach = vi.fn()
    renderPanel({
      prefill: fileCandidate('own-panel.csv'),
      onConfirmAttach,
    })

    const confirm = screen.getByTestId('attach-confirm-btn')
    expect(confirm).toBeEnabled()
    await user.click(confirm)

    // The click was delivered, but the backend has not confirmed anything:
    // the panel must keep showing the candidate as unattached (no local
    // success verdict) and stay retryable.
    expect(onConfirmAttach).toHaveBeenCalledTimes(1)
    expect(screen.getByTestId('attach-candidate-status')).toHaveTextContent('候选（未挂接）')
    expect(screen.getByTestId('attach-confirm-btn')).toBeEnabled()
  })

  test('attached state comes from the backend snapshot, not from the click', async () => {
    const user = userEvent.setup()
    const onConfirmAttach = vi.fn()
    const { rerender } = renderPanel({
      prefill: fileCandidate('own-panel.csv'),
      onConfirmAttach,
    })

    await user.click(screen.getByTestId('attach-confirm-btn'))
    expect(screen.getByTestId('attach-candidate-status')).toHaveTextContent('候选（未挂接）')

    // Backend snapshot now reports dataAttached=true.
    rerender(
      <I18nProvider>
        <AttachPanel
          onBrowse={vi.fn()}
          prefill={fileCandidate('own-panel.csv')}
          attached
        />
      </I18nProvider>,
    )
    expect(screen.getByTestId('attach-candidate-status')).toHaveTextContent('已挂接')
    expect(screen.getByTestId('attach-confirm-btn')).toBeDisabled()
  })

  test('waiting shows only waiting; a failure keeps the candidate and allows retry', async () => {
    const user = userEvent.setup()
    const onConfirmAttach = vi.fn()
    const { rerender } = renderPanel({
      prefill: fileCandidate('own-panel.csv'),
      onConfirmAttach,
    })

    await user.click(screen.getByTestId('attach-confirm-btn'))
    // In flight: waiting state only, no success wording.
    rerender(
      <I18nProvider>
        <AttachPanel
          onBrowse={vi.fn()}
          prefill={fileCandidate('own-panel.csv')}
          confirming
        />
      </I18nProvider>,
    )
    expect(screen.getByTestId('attach-confirm-btn')).toBeDisabled()
    expect(screen.getByTestId('attach-candidate-status')).not.toHaveTextContent('已挂接')
    expect(screen.getByTestId('attach-confirming')).toBeInTheDocument()

    // Backend refused (e.g. 409 upload_not_ready): error surface, candidate
    // preserved, button retryable.
    rerender(
      <I18nProvider>
        <AttachPanel
          onBrowse={vi.fn()}
          prefill={fileCandidate('own-panel.csv')}
          confirmError="数据处理尚未完成，请稍后重试。"
        />
      </I18nProvider>,
    )
    expect(screen.getByTestId('attach-confirm-error')).toHaveTextContent('尚未完成')
    expect(screen.getByTestId('attach-candidate')).toHaveTextContent('own-panel.csv')
    expect(screen.getByTestId('attach-confirm-btn')).toBeEnabled()
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
