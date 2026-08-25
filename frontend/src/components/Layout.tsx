import { NavLink, Outlet, useLocation } from 'react-router-dom'

import farmatodoLogo from '../assets/logo-farmatodo.svg'
import { useAuth } from '../auth/AuthContext'
import { canCreateCreditNote, roleLabel } from '../utils/permissions'

interface NavigationItem {
  to: string
  label: string
  end: boolean
  relatedPaths?: string[]
}

export function Layout() {
  const { user, logout } = useAuth()
  const location = useLocation()
  if (!user) return null

  const navigation: NavigationItem[] = [
    ...(user.role === 'ADMIN'
      ? [{ to: '/analytics', label: 'Analítica', end: true }]
      : [{ to: '/', label: 'Inicio', end: true }]),
    { to: '/organization', label: 'Estructura organizacional', end: true, relatedPaths: ['/positions'] },
    { to: '/credit-notes', label: 'Notas de crédito', end: true },
    ...(canCreateCreditNote(user.role)
      ? [{ to: '/credit-notes/new', label: 'Solicitar nota de crédito', end: true }]
      : []),
  ]

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <img className="brand-logo" src={farmatodoLogo} alt="Farmatodo" />
        </div>

        <nav aria-label="Navegación principal">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => (
                isActive || item.relatedPaths?.includes(location.pathname)
                  ? 'nav-link active'
                  : 'nav-link'
              )}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="user-panel">
          <span className="avatar" aria-hidden="true">{user.full_name.charAt(0)}</span>
          <div className="user-copy">
            <strong>{user.full_name}</strong>
            <span>{roleLabel(user.role)}</span>
            <small>{user.department_name}</small>
          </div>
          <button className="text-button" type="button" onClick={() => void logout()}>
            Cerrar sesión
          </button>
        </div>
      </aside>

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}
