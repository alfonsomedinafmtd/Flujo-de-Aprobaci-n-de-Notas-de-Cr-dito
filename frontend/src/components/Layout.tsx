import { NavLink, Outlet } from 'react-router-dom'

import { useAuth } from '../auth/AuthContext'
import { roleLabel } from '../utils/permissions'

const navigation = [
  { to: '/', label: 'Inicio', end: true },
  { to: '/organization', label: 'Organización' },
  { to: '/positions', label: 'Cargos y funciones' },
  { to: '/credit-notes', label: 'Notas de crédito' },
]

export function Layout() {
  const { user, logout } = useAuth()
  if (!user) return null

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">F</span>
          <div>
            <strong>Finanzas</strong>
            <small>Portal interno</small>
          </div>
        </div>

        <nav aria-label="Navegación principal">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
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

