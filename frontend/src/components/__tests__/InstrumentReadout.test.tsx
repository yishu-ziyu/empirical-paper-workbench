import type { ReactElement } from 'react'
import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import InstrumentReadout from '../InstrumentReadout'
import { I18nProvider } from '../../lib/i18n'

function renderReadout(ui: ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

describe('InstrumentReadout', () => {
  test('shows claim, NONE star, treatment row, and literature source', () => {
    renderReadout(
      <InstrumentReadout
        claim="association"
        starRating={null}
        treatmentRow="| age | 0.1234 | 0.0456 | 0.0078 |"
        literatureSource="mock"
      />,
    )
    expect(screen.getByTestId('readout-claim')).toHaveTextContent('相关')
    expect(screen.getByTestId('readout-star')).toHaveTextContent('无因果评级')
    expect(screen.getByTestId('readout-table')).toHaveTextContent('变量')
    expect(screen.getByTestId('readout-table')).toHaveTextContent('age')
    expect(screen.getByTestId('readout-table')).toHaveTextContent('0.1234')
    expect(screen.getByTestId('readout-lit')).toHaveTextContent('示例文献')
    expect(screen.getByTestId('readout-robust')).toHaveTextContent('—')
    expect(screen.queryByTestId('readout-block')).not.toBeInTheDocument()
  })

  test('empty table tells the user results cannot be written', () => {
    renderReadout(<InstrumentReadout claim="association" />)
    expect(screen.getByTestId('readout-table-empty')).toBeInTheDocument()
  })

  test('ran robustness shows on the readout', () => {
    renderReadout(<InstrumentReadout claim="association" robustnessStatus="ran" />)
    expect(screen.getByTestId('readout-robust')).toHaveTextContent('已跑')
  })

  test('zero star lights the block line', () => {
    renderReadout(
      <InstrumentReadout
        starRating={0}
        identificationFailed
        writeBlockers={['star_0']}
      />,
    )
    expect(screen.getByTestId('readout-star')).toHaveTextContent('0 星')
    expect(screen.getByTestId('readout-block')).toHaveTextContent('0 星')
  })
})
