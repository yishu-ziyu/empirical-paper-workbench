// ── Session identity ───────────────────────────────────────────────
// Auth rides on the httpOnly cookie pair: same-origin fetch sends it
// automatically. The browser only keeps a handle (the session id) in
// localStorage to stitch the workspace back together after a reload.

import { useState, useEffect } from 'react'
import { API_BASE } from './apiBase'

export const LS_KEY = 'econpaper_session_id'
export const DEV_AUTH_BYPASS =
  import.meta.env.DEV && import.meta.env.VITE_DEV_SKIP_AUTH === 'true'

export function readStoredSessionId(): string | null {
  return localStorage.getItem(LS_KEY) || null
}

export function persistSessionId(id: string): void {
  localStorage.setItem(LS_KEY, id)
}

export function clearStoredSessionId(): void {
  localStorage.removeItem(LS_KEY)
}

/**
 * Owns the two identity primitives the rest of the app depends on:
 * whether the current httpOnly cookie pair is considered logged in (authed)
 * and which session the workspace is bound to (sessionId). On reload the
 * httpOnly cookies outlive the tab, so we ask the server who we are
 * instead of trusting a localStorage token.
 */
export function useSession() {
  const [authed, setAuthed] = useState(DEV_AUTH_BYPASS)
  const [sessionId, setSessionId] = useState<string | null>(readStoredSessionId)

  useEffect(() => {
    let cancelled = false
    void (async () => {
      try {
        const r = await fetch(`${API_BASE}/auth/me`)
        if (!cancelled && r && r.ok) setAuthed(true)
      } catch {
        /* stay anonymous */
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  const clearSession = () => {
    setSessionId(null)
    clearStoredSessionId()
  }

  return { authed, setAuthed, sessionId, setSessionId, clearSession }
}