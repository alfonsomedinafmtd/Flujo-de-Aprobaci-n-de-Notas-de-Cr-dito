import { Navigate, Outlet } from 'react-router-dom'

import { useAuth } from '../auth/AuthContext'

export function AdminRoute() {
  const { user } = useAuth()

  if (!user) return null
  if (user.role !== 'ADMIN') return <Navigate to="/" replace />
  return <Outlet />
}
