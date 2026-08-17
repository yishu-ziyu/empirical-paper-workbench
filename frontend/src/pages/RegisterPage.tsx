import { useState } from 'react'
import type { FormEvent } from 'react'
import { useT } from '../lib/i18n'

const API_BASE = 'http://localhost:8000'

interface RegisterPageProps {
  onRegister: (token: string) => void
  onSwitchToLogin: () => void
}

export default function RegisterPage({ onRegister, onSwitchToLogin }: RegisterPageProps) {
  const { t } = useT()
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const validate = (): string | null => {
    if (!email.includes('@')) return t('register.validateEmail')
    if (username.length < 1) return t('register.validateUsername')
    if (password.length < 6) return t('register.validatePassword')
    if (password !== confirmPassword) return t('register.validatePasswordMatch')
    return null
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    const validationError = validate()
    if (validationError) {
      setError(validationError)
      return
    }

    setLoading(true)

    try {
      // 1. Register
      const registerResp = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, username, password }),
      })

      if (!registerResp.ok) {
        const data = await registerResp.json()
        throw new Error(data.detail || 'Registration failed')
      }

      // 2. Login to get a token
      const loginResp = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!loginResp.ok) {
        throw new Error('Account created but login failed — please sign in')
      }

      const data = await loginResp.json()
      onRegister(data.access_token)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-bg px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold font-serif text-ink">
            {t('app.title')}
          </h1>
          <p className="mt-1 text-sm text-muted">{t('register.subtitle')}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="reg-email" className="block text-xs font-medium text-muted mb-1">
              {t('register.email')}
            </label>
            <input
              id="reg-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded border border-border bg-white px-3 py-2 text-sm text-ink outline-none transition-colors duration-200 focus:border-accent focus:ring-1 focus:ring-accent"
              placeholder={t('register.emailPlaceholder')}
            />
          </div>

          <div>
            <label htmlFor="reg-username" className="block text-xs font-medium text-muted mb-1">
              {t('register.username')}
            </label>
            <input
              id="reg-username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={1}
              className="w-full rounded border border-border bg-white px-3 py-2 text-sm text-ink outline-none transition-colors duration-200 focus:border-accent focus:ring-1 focus:ring-accent"
              placeholder={t('register.usernamePlaceholder')}
            />
          </div>

          <div>
            <label htmlFor="reg-password" className="block text-xs font-medium text-muted mb-1">
              {t('register.password')}
            </label>
            <input
              id="reg-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className="w-full rounded border border-border bg-white px-3 py-2 text-sm text-ink outline-none transition-colors duration-200 focus:border-accent focus:ring-1 focus:ring-accent"
              placeholder={t('register.passwordPlaceholder')}
            />
          </div>

          <div>
            <label htmlFor="reg-confirm-password" className="block text-xs font-medium text-muted mb-1">
              {t('register.confirmPassword')}
            </label>
            <input
              id="reg-confirm-password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={6}
              className="w-full rounded border border-border bg-white px-3 py-2 text-sm text-ink outline-none transition-colors duration-200 focus:border-accent focus:ring-1 focus:ring-accent"
              placeholder={t('register.confirmPasswordPlaceholder')}
            />
          </div>

          {error && (
            <div className="rounded border border-red-100 bg-red-50 px-3 py-2 text-xs text-red-600">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded bg-accent px-4 py-2 text-sm text-white transition-colors duration-200 hover:bg-accent/90 disabled:opacity-50"
          >
            {loading ? t('register.creating') : t('register.createAccount')}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-muted">
          {t('register.hasAccount')}{' '}
          <button
            type="button"
            onClick={onSwitchToLogin}
            className="text-accent transition-colors duration-200 hover:text-accent/80"
          >
            {t('register.signIn')}
          </button>
        </p>
      </div>
    </div>
  )
}