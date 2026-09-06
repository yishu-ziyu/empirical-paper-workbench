import { beforeEach, describe, test, expect } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import ThreeColumn from '../ThreeColumn'

describe('ThreeColumn 桌面三栏', () => {
  beforeEach(() => localStorage.clear())

  test('左右功能保留，并允许用户收起或调整宽度', () => {
    render(
      <ThreeColumn
        outline={<p>sidebar</p>}
        editor={<p>paper</p>}
        agent={<p data-testid="agent-rail">steps</p>}
      />,
    )
    const right = screen.getByTestId('agent-panel')
    expect(screen.getByTestId('sidebar-panel')).toBeInTheDocument()
    expect(screen.getByTestId('editor-panel')).toBeInTheDocument()
    expect(right).toContainElement(screen.getByTestId('agent-rail'))
    expect(right).toHaveAttribute('data-open', 'true')
    expect(right.className).toMatch(/border-l/)
    const main = screen.getByTestId('desk-columns')
    expect(main).toContainElement(right)
    expect(screen.getByTestId('sidebar-panel')).toHaveStyle({ width: '236px' })
    expect(right).toHaveStyle({ width: '304px' })

    fireEvent.keyDown(screen.getByTestId('left-resize-handle'), { key: 'ArrowRight' })
    expect(screen.getByTestId('sidebar-panel')).toHaveStyle({ width: '248px' })

    fireEvent.click(screen.getByTestId('right-collapse-btn'))
    expect(right).toHaveClass('hidden')
    expect(screen.getByTestId('right-expand-btn')).toBeInTheDocument()
  })

  test('左右开合状态独立持久化，中栏始终保留', () => {
    const view = render(
      <ThreeColumn
        outline={<p>sidebar</p>}
        editor={<p>paper</p>}
        agent={<p>research</p>}
      />,
    )

    fireEvent.click(screen.getByTestId('left-collapse-btn'))
    expect(screen.getByTestId('sidebar-panel')).toHaveAttribute('data-open', 'false')
    expect(screen.getByTestId('editor-panel')).toBeVisible()
    expect(screen.getByTestId('agent-panel')).toHaveAttribute('data-open', 'true')

    view.unmount()
    render(
      <ThreeColumn
        outline={<p>sidebar</p>}
        editor={<p>paper</p>}
        agent={<p>research</p>}
      />,
    )

    expect(screen.getByTestId('sidebar-panel')).toHaveAttribute('data-open', 'false')
    expect(screen.getByTestId('agent-panel')).toHaveAttribute('data-open', 'true')
    expect(screen.getByTestId('editor-panel')).toBeVisible()

    fireEvent.click(screen.getByTestId('left-expand-btn'))
    fireEvent.click(screen.getByTestId('right-collapse-btn'))
    expect(screen.getByTestId('sidebar-panel')).toHaveAttribute('data-open', 'true')
    expect(screen.getByTestId('agent-panel')).toHaveAttribute('data-open', 'false')
  })
})
