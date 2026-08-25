import { Navigate } from 'react-router-dom'

import { useAuth } from '../auth/AuthContext'
import { DashboardPage } from '../pages/DashboardPage'

export function RoleHome() {
  const { user } = useAuth()

  if (!user) return null
  if (user.role === 'ADMIN') return <Navigate to="/analytics" replace />
  return <DashboardPage />
}
