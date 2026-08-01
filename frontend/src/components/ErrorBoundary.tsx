import { Component, type ReactNode } from 'react'
import { I18nContext } from '../lib/i18n'

export interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error) => void
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, error: null }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error) {
    console.error('[ErrorBoundary] Caught error:', error)
    this.props.onError?.(error)
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <I18nContext.Consumer>
          {(ctx) => {
            const t = ctx?.t ?? ((key: string) => key)
            return (
              <div
                data-testid="error-boundary-fallback"
                className="flex flex-col items-center justify-center rounded border border-red-200 bg-red-50 p-6 text-center"
              >
                <svg
                  className="mb-3 h-10 w-10 text-red-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
                  />
                </svg>
                <p className="mb-1 text-sm font-medium text-red-700" data-testid="error-boundary-message">
                  {t('error.panelError')}
                </p>
                <p className="mb-3 text-xs text-red-500">
                  {this.state.error?.message || 'Unknown error'}
                </p>
                <button
                  data-testid="error-boundary-retry"
                  onClick={this.handleRetry}
                  className="rounded bg-red-600 px-3 py-1 text-xs text-white hover:bg-red-700"
                >
                  {t('error.retry')}
                </button>
              </div>
            )
          }}
        </I18nContext.Consumer>
      )
    }

    return this.props.children
  }
}