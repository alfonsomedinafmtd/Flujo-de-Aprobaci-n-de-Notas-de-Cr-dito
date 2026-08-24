import { createContext, useContext, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'

import { ApiError, apiRequest } from '../api'
import type { CurrentUser } from '../types'

interface LoginResponse {
  user: CurrentUser
  csrf_token: string
}

interface AuthContextValue {
  user: CurrentUser | null
  csrfToken: string | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null)
  const [csrfToken, setCsrfToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const bootstrapped = useRef(false)

  useEffect(() => {
    if (bootstrapped.current) return
    bootstrapped.current = true

    async function restoreSession() {
      try {
        const currentUser = await apiRequest<CurrentUser>('/auth/me')
        const csrf = await apiRequest<{ csrf_token: string }>('/auth/csrf', { method: 'POST' })
        setUser(currentUser)
        setCsrfToken(csrf.csrf_token)
      } catch (error) {
        if (!(error instanceof ApiError) || error.status !== 401) {
          console.error('No fue posible restaurar la sesión', error)
        }
        setUser(null)
        setCsrfToken(null)
      } finally {
        setLoading(false)
      }
    }

    void restoreSession()
  }, [])

  async function login(username: string, password: string) {
    const result = await apiRequest<LoginResponse>('/auth/login', {
      method: 'POST',
      body: { username, password },
    })
    setUser(result.user)
    setCsrfToken(result.csrf_token)
  }

  async function logout() {
    try {
      await apiRequest<void>('/auth/logout', { method: 'POST', csrfToken })
    } finally {
      setUser(null)
      setCsrfToken(null)
    }
  }

  const value = useMemo(
    () => ({ user, csrfToken, loading, login, logout }),
    [user, csrfToken, loading],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider')
  }
  return context
}
