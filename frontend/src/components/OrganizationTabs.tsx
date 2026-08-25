import { NavLink } from 'react-router-dom'

export function OrganizationTabs() {
  return (
    <nav className="organization-tabs" aria-label="Vistas de estructura organizacional">
      <NavLink
        className={({ isActive }) => (isActive ? 'organization-tab active' : 'organization-tab')}
        end
        to="/organization"
      >
        Colaboradores
      </NavLink>
      <NavLink
        className={({ isActive }) => (isActive ? 'organization-tab active' : 'organization-tab')}
        end
        to="/positions"
      >
        Cargos y funciones
      </NavLink>
    </nav>
  )
}
