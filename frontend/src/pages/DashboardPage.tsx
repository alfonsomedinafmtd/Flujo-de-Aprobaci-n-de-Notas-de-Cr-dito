import { Link } from 'react-router-dom'

import { useAuth } from '../auth/AuthContext'
import { canCreateCreditNote, canDecideCreditNote, roleLabel } from '../utils/permissions'

export function DashboardPage() {
  const { user } = useAuth()
  if (!user) return null

  return (
    <div className="page">
      <header className="page-header hero-header">
        <div>
          <span className="eyebrow">Resumen de sesión</span>
          <h1>Hola, {user.full_name.split(' ')[0]}</h1>
          <p>Tu acceso corresponde a {roleLabel(user.role).toLowerCase()} en {user.department_name}.</p>
        </div>
        <span className="scope-pill">Alcance: {user.role === 'ADMIN' ? 'Global' : user.department_name}</span>
      </header>

      <section className="module-grid" aria-label="Módulos disponibles">
        <Link className="module-card" to="/organization">
          <span className="module-number">01</span>
          <h2>Organización</h2>
          <p>Consulta colaboradores dentro del alcance permitido por tu sesión.</p>
          <span className="card-link">Abrir directorio →</span>
        </Link>
        <Link className="module-card" to="/positions">
          <span className="module-number">02</span>
          <h2>Cargos y funciones</h2>
          <p>Revisa seniority, responsabilidades y pertenencia departamental.</p>
          <span className="card-link">Ver catálogo →</span>
        </Link>
        <Link className="module-card module-card-accent" to="/credit-notes">
          <span className="module-number">03</span>
          <h2>Notas de crédito</h2>
          <p>
            {canCreateCreditNote(user.role) && 'Crea solicitudes y consulta su trazabilidad.'}
            {canDecideCreditNote(user.role) && 'Revisa solicitudes pendientes y registra decisiones auditables.'}
          </p>
          <span className="card-link">Gestionar solicitudes →</span>
        </Link>
      </section>

      <section className="security-note">
        <strong>Control aplicado en backend</strong>
        <p>El rol y el departamento provienen de tu sesión. Cambiar la interfaz no amplía los permisos de la API.</p>
      </section>
    </div>
  )
}

