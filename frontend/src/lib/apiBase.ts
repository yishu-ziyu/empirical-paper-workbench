/** Same-origin prefix. Vite (dev/preview) and nginx proxy /api → backend :8000. */
export const API_BASE = '/api'

/**
 * fetch wrapper for API calls.
 *
 * Auth rides on the httpOnly cookie pair (same-origin requests carry it
 * automatically), and a 401 from an expired short-lived access token
 * triggers one silent POST /auth/refresh before replaying the original
 * request. /auth/* calls are returned as-is so the refresh itself can
 * never loop.
 */
export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  const resp = await fetch(path, { ...init, credentials: 'include' })
  if (resp.status !== 401 || path.includes('/auth/')) return resp
  const refreshed = await fetch(`${API_BASE}/auth/refresh`, {
    method: 'POST',
    credentials: 'include',
  })
  if (!refreshed.ok) return resp
  return fetch(path, { ...init, credentials: 'include' })
}
