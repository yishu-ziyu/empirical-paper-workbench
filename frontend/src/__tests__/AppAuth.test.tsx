import { test, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from '../App'
import { I18nProvider } from '../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

beforeEach(() => {
  localStorage.clear()
})

test('renders login page when not authenticated', () => {
  renderWithI18n(<App />)
  expect(screen.getByTestId('login-page')).toBeInTheDocument()
})