import { describe, test, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ErrorBoundary } from '../ErrorBoundary'
import { I18nProvider } from '../../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

const GoodChild = () => <div data-testid="good-child">Hello</div>

const BadChild = () => {
  throw new Error('oops')
}

describe('ErrorBoundary', () => {
  test('渲染正常子组件', () => {
    renderWithI18n(
      <ErrorBoundary>
        <GoodChild />
      </ErrorBoundary>,
    )
    expect(screen.getByTestId('good-child')).toBeInTheDocument()
  })

  test('捕获渲染错误并显示回退 UI', () => {
    // Suppress console.error from React for the intentional error
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})

    renderWithI18n(
      <ErrorBoundary>
        <BadChild />
      </ErrorBoundary>,
    )

    expect(screen.getByTestId('error-boundary-fallback')).toBeInTheDocument()
    expect(screen.getByTestId('error-boundary-message')).toBeInTheDocument()
    expect(screen.getByTestId('error-boundary-retry')).toBeInTheDocument()

    spy.mockRestore()
  })

  test('重试按钮恢复渲染', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})

    // Use a component that initially throws but can be reset
    let shouldThrow = true
    function ConditionalChild() {
      if (shouldThrow) throw new Error('conditional')
      return <div data-testid="recovered">Recovered</div>
    }

    renderWithI18n(
      <ErrorBoundary>
        <ConditionalChild />
      </ErrorBoundary>,
    )

    // Should show error fallback
    expect(screen.getByTestId('error-boundary-fallback')).toBeInTheDocument()

    // Fix the condition and click retry
    shouldThrow = false
    fireEvent.click(screen.getByTestId('error-boundary-retry'))

    // Should now show recovered child
    expect(screen.getByTestId('recovered')).toBeInTheDocument()
    expect(screen.queryByTestId('error-boundary-fallback')).not.toBeInTheDocument()

    spy.mockRestore()
  })

  test('使用自定义 fallback', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})

    renderWithI18n(
      <ErrorBoundary fallback={<div data-testid="custom-fallback">Custom Error</div>}>
        <BadChild />
      </ErrorBoundary>,
    )

    expect(screen.getByTestId('custom-fallback')).toBeInTheDocument()
    expect(screen.queryByTestId('error-boundary-fallback')).not.toBeInTheDocument()

    spy.mockRestore()
  })

  test('onError 回调被调用', () => {
    const spy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const onError = vi.fn()

    renderWithI18n(
      <ErrorBoundary onError={onError}>
        <BadChild />
      </ErrorBoundary>,
    )

    expect(onError).toHaveBeenCalledTimes(1)
    expect(onError).toHaveBeenCalledWith(expect.any(Error))

    spy.mockRestore()
  })
})