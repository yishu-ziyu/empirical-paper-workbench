import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import InstrumentReadout from '../InstrumentReadout'

describe('InstrumentReadout', () => {
  test('shows claim, NONE star, treatment row, and literature source', () => {
    render(
      <InstrumentReadout
        claim="association"
        starRating={null}
        treatmentRow="| age | 0.1234 | 0.0456 | 0.0078 |"
        literatureSource="mock"
      />,
    )
    expect(screen.getByTestId('readout-claim')).toHaveTextContent('association')
    expect(screen.getByTestId('readout-star')).toHaveTextContent('NONE')
    expect(screen.getByTestId('readout-table')).toHaveTextContent('| age | 0.1234 |')
    expect(screen.getByTestId('readout-lit')).toHaveTextContent('mock')
    expect(screen.queryByTestId('readout-block')).not.toBeInTheDocument()
  })

  test('empty table tells the user results cannot be written', () => {
    render(<InstrumentReadout claim="association" />)
    expect(screen.getByTestId('readout-table-empty')).toBeInTheDocument()
  })

  test('zero star lights the block line', () => {
    render(
      <InstrumentReadout
        starRating={0}
        identificationFailed
        writeBlockers={['star_0']}
      />,
    )
    expect(screen.getByTestId('readout-star')).toHaveTextContent('0')
    expect(screen.getByTestId('readout-block')).toHaveTextContent('0 星')
  })
})
