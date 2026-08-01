import { useState, FormEvent } from 'react'
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
    <div data-testid="login-page" className="flex min-h-screen items-center justify-center bg-bg px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold font-serif text-ink">
            {t('app.title')}
          </h1>
          <p className="mt-1 text-sm text-muted">{t('login.subtitle')}</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="login-email" className="block text-xs font-medium text-muted mb-1">
              {t('login.email')}
            </label>
            <input
              id="login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded border border-border bg-white px-3 py-2 text-sm text-ink outline-none transition-colors duration-200 focus:border-accent focus:ring-1 focus:ring-accent"
              placeholder={t('login.emailPlaceholder')}
            />
          </div>

          <div>
            <label htmlFor="login-password" className="block text-xs font-medium text-muted mb-1">
              {t('login.password')}
            </label>
            <input
              id="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              className="w-full rounded border border-border bg-white px-3 py-2 text-sm text-ink outline-none transition-colors duration-200 focus:border-accent focus:ring-1 focus:ring-accent"
              placeholder={t('login.passwordPlaceholder')}
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
            {loading ? t('login.signingIn') : t('login.signIn')}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-muted">
          {t('login.noAccount')}{' '}
          <button
            type="button"
            onClick={onSwitchToRegister}
            className="text-accent transition-colors duration-200 hover:text-accent/80"
          >
            {t('login.createOne')}
          </button>
        </p>
      </div>
    </div>
  )
}