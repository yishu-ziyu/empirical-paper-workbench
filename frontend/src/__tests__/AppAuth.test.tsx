import { test, expect, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from '../App'
import { I18nProvider } from '../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

beforeEach(() => {
  localStorage.clear()
})

test('opens guide without forcing login', () => {
  renderWithI18n(<App />)
  expect(screen.queryByTestId('login-page')).not.toBeInTheDocument()
  expect(screen.getByTestId('guide-page')).toBeInTheDocument()
})

test('header login button opens the login page', async () => {
  const user = userEvent.setup()
  renderWithI18n(<App />)
  await user.click(screen.getByTestId('open-login-btn'))
  expect(screen.getByTestId('login-page')).toBeInTheDocument()
})
