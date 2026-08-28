import { useState } from 'react'
import { describe, test, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import LoginPage from '../pages/LoginPage'
import RegisterPage from '../pages/RegisterPage'
import App from '../App'
import { I18nProvider } from '../lib/i18n'

function renderWithI18n(ui: React.ReactElement) {
  return render(ui, { wrapper: I18nProvider })
}

describe('LoginPage', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
    localStorage.clear()
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  test('renders login form with email and password inputs', () => {
    renderWithI18n(<LoginPage onLogin={() => {}} onSwitchToRegister={() => {}} />)

    expect(screen.getByLabelText(/邮箱|email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^密码$|^password$/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /登录|sign in/i })).toBeInTheDocument()
  })

  test('shows link to switch to register page', () => {
    const onSwitch = vi.fn()
    renderWithI18n(<LoginPage onLogin={() => {}} onSwitchToRegister={onSwitch} />)

    const createLink = screen.getByText(/创建一个|create one/i)
    expect(createLink).toBeInTheDocument()
    fireEvent.click(createLink)
    expect(onSwitch).toHaveBeenCalledTimes(1)
  })

  test('calls onLogin when login succeeds', async () => {
    const onLogin = vi.fn()
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ access_token: 'test-token-123', token_type: 'bearer' }),
      }),
    )

    renderWithI18n(<LoginPage onLogin={onLogin} onSwitchToRegister={() => {}} />)

    fireEvent.change(screen.getByLabelText(/邮箱|email/i), { target: { value: 'test@example.com' } })
    fireEvent.change(screen.getByLabelText(/^密码$|^password$/i), { target: { value: 'secret123' } })
    fireEvent.click(screen.getByRole('button', { name: /登录|sign in/i }))

    await waitFor(() => {
      expect(onLogin).toHaveBeenCalledWith('test-token-123')
    })
  })

  test('shows error message when login fails', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        json: () => Promise.resolve({ detail: 'Invalid email or password' }),
      }),
    )

    renderWithI18n(<LoginPage onLogin={() => {}} onSwitchToRegister={() => {}} />)

    fireEvent.change(screen.getByLabelText(/邮箱|email/i), { target: { value: 'test@example.com' } })
    fireEvent.change(screen.getByLabelText(/^密码$|^password$/i), { target: { value: 'wrong' } })
    fireEvent.click(screen.getByRole('button', { name: /登录|sign in/i }))

    await waitFor(() => {
      expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument()
    })
  })

  test('shows "Signing in..." while loading', async () => {
    // fetch that never resolves
    vi.stubGlobal('fetch', vi.fn().mockReturnValue(new Promise(() => {})))

    renderWithI18n(<LoginPage onLogin={() => {}} onSwitchToRegister={() => {}} />)

    fireEvent.change(screen.getByLabelText(/邮箱|email/i), { target: { value: 'test@example.com' } })
    fireEvent.change(screen.getByLabelText(/^密码$|^password$/i), { target: { value: 'secret123' } })
    fireEvent.click(screen.getByRole('button', { name: /登录|sign in/i }))

    await waitFor(() => {
      expect(screen.getByText(/登录中\.\.\.|signing in\.\.\./i)).toBeInTheDocument()
    })
  })
})

describe('RegisterPage', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
    localStorage.clear()
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  test('renders registration form with all fields', () => {
    renderWithI18n(<RegisterPage onRegister={() => {}} onSwitchToLogin={() => {}} />)

    expect(screen.getByLabelText(/邮箱|email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/用户名|username/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/^密码$|^password$/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/确认密码|confirm password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /创建账户|create account/i })).toBeInTheDocument()
  })

  test('shows link to switch to login page', () => {
    const onSwitch = vi.fn()
    renderWithI18n(<RegisterPage onRegister={() => {}} onSwitchToLogin={onSwitch} />)

    const signInLink = screen.getByText(/登录|sign in/i)
    expect(signInLink).toBeInTheDocument()
    fireEvent.click(signInLink)
    expect(onSwitch).toHaveBeenCalledTimes(1)
  })

  test('validates email format before submitting', () => {
    renderWithI18n(<RegisterPage onRegister={() => {}} onSwitchToLogin={() => {}} />)

    fireEvent.change(screen.getByLabelText(/邮箱|email/i), { target: { value: 'invalid' } })
    fireEvent.change(screen.getByLabelText(/用户名|username/i), { target: { value: 'testuser' } })
    fireEvent.change(screen.getByLabelText(/^密码$|^password$/i), { target: { value: 'secret123' } })
    fireEvent.change(screen.getByLabelText(/确认密码|confirm password/i), { target: { value: 'secret123' } })
    fireEvent.submit(screen.getByRole('button', { name: /创建账户|create account/i }).closest('form')!)

    expect(screen.getByText(/请输入有效的邮箱地址|please enter a valid email address/i)).toBeInTheDocument()
  })

  test('validates password match before submitting', () => {
    renderWithI18n(<RegisterPage onRegister={() => {}} onSwitchToLogin={() => {}} />)

    fireEvent.change(screen.getByLabelText(/邮箱|email/i), { target: { value: 'test@example.com' } })
    fireEvent.change(screen.getByLabelText(/用户名|username/i), { target: { value: 'testuser' } })
    fireEvent.change(screen.getByLabelText(/^密码$|^password$/i), { target: { value: 'secret123' } })
    fireEvent.change(screen.getByLabelText(/确认密码|confirm password/i), { target: { value: 'different' } })
    fireEvent.click(screen.getByRole('button', { name: /创建账户|create account/i }))

    expect(screen.getByText(/两次密码不一致|passwords do not match/i)).toBeInTheDocument()
  })

  test('validates password minimum length', () => {
    renderWithI18n(<RegisterPage onRegister={() => {}} onSwitchToLogin={() => {}} />)

    fireEvent.change(screen.getByLabelText(/邮箱|email/i), { target: { value: 'test@example.com' } })
    fireEvent.change(screen.getByLabelText(/用户名|username/i), { target: { value: 'testuser' } })
    fireEvent.change(screen.getByLabelText(/^密码$|^password$/i), { target: { value: '12345' } })
    fireEvent.change(screen.getByLabelText(/确认密码|confirm password/i), { target: { value: '12345' } })
    fireEvent.click(screen.getByRole('button', { name: /创建账户|create account/i }))

    expect(screen.getByText(/至少需要 8 个字符|at least 8 characters/i)).toBeInTheDocument()
  })

  test('calls onRegister after successful registration + login', async () => {
    const onRegister = vi.fn()
    // First call: register
    // Second call: login
    vi.stubGlobal(
      'fetch',
      vi
        .fn()
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ id: 1, email: 'test@example.com', username: 'testuser' }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ access_token: 'reg-token-456', token_type: 'bearer' }),
        }),
    )

    renderWithI18n(<RegisterPage onRegister={onRegister} onSwitchToLogin={() => {}} />)

    fireEvent.change(screen.getByLabelText(/邮箱|email/i), { target: { value: 'test@example.com' } })
    fireEvent.change(screen.getByLabelText(/用户名|username/i), { target: { value: 'testuser' } })
    fireEvent.change(screen.getByLabelText(/^密码$|^password$/i), { target: { value: 'secret123' } })
    fireEvent.change(screen.getByLabelText(/确认密码|confirm password/i), { target: { value: 'secret123' } })
    fireEvent.click(screen.getByRole('button', { name: /创建账户|create account/i }))

    await waitFor(() => {
      expect(onRegister).toHaveBeenCalledWith('reg-token-456')
    })
  })

  test('shows error message when registration fails', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        json: () => Promise.resolve({ detail: 'Email already registered' }),
      }),
    )

    renderWithI18n(<RegisterPage onRegister={() => {}} onSwitchToLogin={() => {}} />)

    fireEvent.change(screen.getByLabelText(/邮箱|email/i), { target: { value: 'test@example.com' } })
    fireEvent.change(screen.getByLabelText(/用户名|username/i), { target: { value: 'testuser' } })
    fireEvent.change(screen.getByLabelText(/^密码$|^password$/i), { target: { value: 'secret123' } })
    fireEvent.change(screen.getByLabelText(/确认密码|confirm password/i), { target: { value: 'secret123' } })
    fireEvent.click(screen.getByRole('button', { name: /创建账户|create account/i }))

    await waitFor(() => {
      expect(screen.getByText(/email already registered/i)).toBeInTheDocument()
    })
  })
})

describe('App auth flow', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
    localStorage.clear()
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  test('useState lazy initializer reads from localStorage', () => {
    function TestComponent() {
      const [value] = useState(() => localStorage.getItem('test-key'))
      return <div data-testid="test-value">{value === null ? 'null' : value}</div>
    }
    localStorage.clear()
    renderWithI18n(<TestComponent />)
    expect(screen.getByTestId('test-value')).toHaveTextContent('null')
  })

  test('renders login page when not authenticated', () => {
    localStorage.clear()
    // Verify localStorage is empty
    expect(localStorage.getItem('econpaper_access_token')).toBeNull()
    expect(localStorage.getItem('econpaper_session_id')).toBeNull()
    const getItemSpy = vi.spyOn(Storage.prototype, 'getItem')
    renderWithI18n(<App />)
    // Check what localStorage.getItem was called with
    const calls = getItemSpy.mock.calls.map(c => c[0])
    console.error('localStorage.getItem calls:', calls)
    getItemSpy.mockRestore()
    expect(screen.getByTestId('guide-page')).toBeInTheDocument()
    expect(screen.getAllByText(/econpaper/i).length).toBeGreaterThan(0)
  })

  test('renders main app when token exists in localStorage', async () => {
    localStorage.setItem('econpaper_access_token', 'test-token')
    // Mock the session verify call
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ exists: false }),
      }),
    )

    renderWithI18n(<App />)
    // With token, should show main app (upload button, outline, etc.)
    await waitFor(() => {
      expect(screen.getByTestId('guide-upload-btn')).toBeInTheDocument()
    })
  })
})