import type { ReactNode } from 'react'

interface ProtectedRouteProps {
  isAuthenticated: boolean
  children: ReactNode
  fallback?: ReactNode
}

/**
 * Route guard that renders children only when the user is authenticated.
 * Otherwise renders the fallback (login page) or nothing.
 */
export default function ProtectedRoute({
  isAuthenticated,
  children,
  fallback,
}: ProtectedRouteProps) {
  if (isAuthenticated) {
    return <>{children}</>
  }
  return <>{fallback ?? null}</>
}