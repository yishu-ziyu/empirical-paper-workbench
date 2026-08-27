import { useState } from 'react'
import type { FormEvent } from 'react'
import UnauthHeader from '../components/UnauthHeader'
import { API_BASE } from '../lib/apiBase'
import { useT } from '../lib/i18n'

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
      const registerResp = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, username, password }),
      })

      if (!registerResp.ok) {
        const data = await registerResp.json()
        throw new Error(data.detail || 'Registration failed')
      }

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
    <div className="min-h-screen bg-bg text-ink">
      <UnauthHeader />
      <main className="mx-auto flex w-full max-w-[420px] flex-col px-6 pb-24 pt-24">
        <h1 className="font-serif text-[2rem] leading-tight tracking-tight text-ink">
          {t('register.subtitle')}
        </h1>
        <p className="mt-2 text-[14px] text-muted">{t('app.title')}</p>

        <form onSubmit={handleSubmit} className="mt-10 space-y-4">
          <div>
            <label htmlFor="reg-email" className="block text-[12px] text-muted mb-1.5">
              {t('register.email')}
            </label>
            <input
              id="reg-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded-lg border border-border bg-white px-3.5 py-2.5 text-sm text-ink outline-none transition-colors duration-200 focus:border-ink/30"
              placeholder={t('register.emailPlaceholder')}
            />
          </div>

          <div>
            <label htmlFor="reg-username" className="block text-[12px] text-muted mb-1.5">
              {t('register.username')}
            </label>
            <input
              id="reg-username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={1}
              className="w-full rounded-lg border border-border bg-white px-3.5 py-2.5 text-sm text-ink outline-none transition-colors duration-200 focus:border-ink/30"
              placeholder={t('register.usernamePlaceholder')}
            />
          </div>

          <div>
            <label htmlFor="reg-password" className="block text-[12px] text-muted mb-1.5">
              {t('register.password')}
            </label>
            <input
              id="reg-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className="w-full rounded-lg border border-border bg-white px-3.5 py-2.5 text-sm text-ink outline-none transition-colors duration-200 focus:border-ink/30"
              placeholder={t('register.passwordPlaceholder')}
            />
          </div>

          <div>
            <label htmlFor="reg-confirm-password" className="block text-[12px] text-muted mb-1.5">
              {t('register.confirmPassword')}
            </label>
            <input
              id="reg-confirm-password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={6}
              className="w-full rounded-lg border border-border bg-white px-3.5 py-2.5 text-sm text-ink outline-none transition-colors duration-200 focus:border-ink/30"
              placeholder={t('register.confirmPasswordPlaceholder')}
            />
          </div>

          {error && (
            <div className="rounded-lg border border-danger/20 bg-danger/5 px-3 py-2 text-xs text-danger">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-accent px-4 py-2.5 text-sm font-medium text-white transition-opacity duration-200 hover:opacity-90 disabled:opacity-50"
          >
            {loading ? t('register.creating') : t('register.createAccount')}
          </button>
        </form>

        <p className="mt-6 text-center text-[13px] text-muted">
          {t('register.hasAccount')}{' '}
          <button
            type="button"
            onClick={onSwitchToLogin}
            className="text-ink underline-offset-4 transition-colors duration-200 hover:underline"
          >
            {t('register.signIn')}
          </button>
        </p>
      </main>
    </div>
  )
}
