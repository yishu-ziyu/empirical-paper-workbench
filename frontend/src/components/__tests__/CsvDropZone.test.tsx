import { describe, test, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { CsvDropZone } from '../CsvDropZone'
import { I18nProvider } from '../../lib/i18n'

function renderZone(onFile: (file: File) => void = vi.fn()) {
  return render(
    <I18nProvider>
      <CsvDropZone onBrowse={vi.fn()} onFile={onFile} />
    </I18nProvider>,
  )
}

describe('CsvDropZone', () => {
  test('rejects a non-table drop and does not forward the file', () => {
    const onFile = vi.fn()
    renderZone(onFile)
    const zone = screen.getByTestId('csv-drop-zone')
    const file = new File(['not csv'], 'notes.txt', { type: 'text/plain' })
    fireEvent.drop(zone, { dataTransfer: { files: [file] } })
    expect(onFile).not.toHaveBeenCalled()
    expect(screen.getByTestId('upload-error')).toHaveTextContent('CSV')
  })

  test('forwards a .csv drop', () => {
    const onFile = vi.fn()
    renderZone(onFile)
    const zone = screen.getByTestId('csv-drop-zone')
    const file = new File(['a,b\n1,2'], 'panel.CSV', { type: 'text/csv' })
    fireEvent.drop(zone, { dataTransfer: { files: [file] } })
    expect(onFile).toHaveBeenCalledWith(file)
    expect(screen.queryByTestId('upload-error')).not.toBeInTheDocument()
  })

  test.each(['panel.dta', 'panel.xlsx', 'panel.xls'])('forwards %s', (name) => {
    const onFile = vi.fn()
    renderZone(onFile)
    const file = new File(['binary-ish'], name, { type: 'application/octet-stream' })
    fireEvent.drop(screen.getByTestId('csv-drop-zone'), { dataTransfer: { files: [file] } })
    expect(onFile).toHaveBeenCalledWith(file)
  })
})
