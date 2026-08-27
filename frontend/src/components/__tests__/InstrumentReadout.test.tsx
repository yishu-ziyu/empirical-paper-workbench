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
    render(<InstrumentReadout claim="association" />)
    expect(screen.getByTestId('readout-table-empty')).toBeInTheDocument()
  })

  test('ran robustness shows on the readout', () => {
    render(<InstrumentReadout claim="association" robustnessStatus="ran" />)
    expect(screen.getByTestId('readout-robust')).toHaveTextContent('已跑')
  })

  test('lists papers with doi url and stance toward the research direction', () => {
    render(
      <InstrumentReadout
        claim="association"
        literatureSource="crossref"
        literatureEntries={[
          {
            title: 'Household catastrophic health expenditure',
            authors: ['Xu', 'Evans'],
            year: 2003,
            url: 'https://doi.org/10.1016/S0140-6736(03)13861-5',
            stance: '支持',
          },
          {
            title: 'Health systems financing',
            authors: ['WHO'],
            year: 2010,
            url: '',
            stance: '说不清',
          },
        ]}
      />,
    )
    const list = screen.getByTestId('readout-literature-list')
    expect(list).toHaveTextContent('Household catastrophic health expenditure')
    expect(list).toHaveTextContent('https://doi.org/10.1016/S0140-6736(03)13861-5')
    expect(list).toHaveTextContent('对研究方向：支持')
    expect(list).toHaveTextContent('对研究方向：说不清')
    expect(list.querySelector('a')?.getAttribute('href')).toBe(
      'https://doi.org/10.1016/S0140-6736(03)13861-5',
    )
    expect(list.querySelectorAll('a')).toHaveLength(1)
  })

  test('does not link non-doi urls', () => {
    render(
      <InstrumentReadout
        claim="association"
        literatureEntries={[
          { title: 'Landing page', url: 'https://example.com/paper', stance: '支持' },
        ]}
      />,
    )
    const list = screen.getByTestId('readout-literature-list')
    expect(list.querySelector('a')).toBeNull()
    expect(list).toHaveTextContent('对研究方向：支持')
  })

  test('zero star lights the block line', () => {
    render(
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
