import { useState } from 'react'
import type { FormEvent } from 'react'
import UnauthHeader from '../components/UnauthHeader'
import { useT } from '../lib/i18n'

const API_BASE = 'http://localhost:8000'

interface LoginPageProps {
  onLogin: (token: string) => void
  onSwitchToRegister: () => void
}

export default function LoginPage({ onLogin, onSwitchToRegister }: LoginPageProps) {
  const { t } = useT()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const resp = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!resp.ok) {
        const data = await resp.json()
        throw new Error(data.detail || 'Login failed')
      }

      const data = await resp.json()
      onLogin(data.access_token)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div data-testid="login-page" className="min-h-screen bg-bg text-ink">
      <UnauthHeader onRegister={onSwitchToRegister} />
      <main className="mx-auto flex w-full max-w-[420px] flex-col px-6 pb-24 pt-24">
        <h1 className="font-serif text-[2rem] leading-tight tracking-tight text-ink">
          {t('login.subtitle')}
        </h1>
        <p className="mt-2 text-[14px] text-muted">{t('app.title')}</p>

        <form onSubmit={handleSubmit} className="mt-10 space-y-4">
          <div>
            <label htmlFor="login-email" className="block text-[12px] text-muted mb-1.5">
              {t('login.email')}
            </label>
            <input
              id="login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded-lg border border-border bg-white px-3.5 py-2.5 text-sm text-ink outline-none transition-colors duration-200 focus:border-ink/30"
              placeholder={t('login.emailPlaceholder')}
            />
          </div>

          <div>
            <label htmlFor="login-password" className="block text-[12px] text-muted mb-1.5">
              {t('login.password')}
            </label>
            <input
              id="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className="w-full rounded-lg border border-border bg-white px-3.5 py-2.5 text-sm text-ink outline-none transition-colors duration-200 focus:border-ink/30"
              placeholder={t('login.passwordPlaceholder')}
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
            {loading ? t('login.signingIn') : t('login.signIn')}
          </button>
        </form>

        <p className="mt-6 text-center text-[13px] text-muted">
          {t('login.noAccount')}{' '}
          <button
            type="button"
            onClick={onSwitchToRegister}
            className="text-ink underline-offset-4 transition-colors duration-200 hover:underline"
          >
            {t('login.createOne')}
          </button>
        </p>
      </main>
    </div>
  )
}
