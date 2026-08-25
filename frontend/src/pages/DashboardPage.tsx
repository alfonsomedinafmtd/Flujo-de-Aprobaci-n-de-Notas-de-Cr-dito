import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { ApiError, apiRequest } from '../api'
import { useAuth } from '../auth/AuthContext'
import { ErrorMessage, Loading } from '../components/Feedback'
import type { CreditNoteSummary } from '../types'
import { canCreateCreditNote, canDecideCreditNote, roleLabel } from '../utils/permissions'

export function DashboardPage() {
  const { user } = useAuth()
  const [summary, setSummary] = useState<CreditNoteSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    apiRequest<CreditNoteSummary>('/credit-notes/summary')
      .then((data) => active && setSummary(data))
      .catch((caught) => active && setError(caught instanceof ApiError ? caught.message : 'No fue posible cargar el resumen.'))
      .finally(() => active && setLoading(false))
    return () => { active = false }
  }, [])

  if (!user) return null

  const canCreate = canCreateCreditNote(user.role)

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

      <section className="summary-section" aria-labelledby="summary-title">
        <div className="section-heading">
          <span className="eyebrow">Notas dentro de tu alcance</span>
          <h2 id="summary-title">Estado del proceso</h2>
        </div>
        {loading && <Loading label="Calculando resumen…" />}
        {error && <ErrorMessage message={error} />}
        {summary && (
          <div className="metric-grid">
            <article className="metric-card"><span>Total</span><strong>{summary.total}</strong></article>
            <article className="metric-card metric-pending"><span>Pendientes</span><strong>{summary.pending}</strong></article>
            <article className="metric-card metric-approved"><span>Aprobadas</span><strong>{summary.approved}</strong></article>
            <article className="metric-card metric-rejected"><span>Rechazadas</span><strong>{summary.rejected}</strong></article>
          </div>
        )}
      </section>

      <section className="module-grid module-grid-compact" aria-label="Módulos disponibles">
        <Link className="module-card" to="/organization">
          <span className="module-number">01</span>
          <h2>Estructura organizacional</h2>
          <p>Consulta colaboradores, departamentos, cargos, seniority y funciones desde dos vistas relacionadas.</p>
          <span className="card-link">Explorar estructura →</span>
        </Link>
        <Link className="module-card module-card-accent" to={canCreate ? '/credit-notes/new' : '/credit-notes'}>
          <span className="module-number">02</span>
          <h2>{canCreate ? 'Solicitud de nota de crédito' : 'Notas de crédito'}</h2>
          <p>
            {canCreate && 'Registra una solicitud para tu departamento; el proceso conservará su trazabilidad.'}
            {canDecideCreditNote(user.role) && 'Revisa solicitudes pendientes y registra decisiones auditables.'}
          </p>
          <span className="card-link">{canCreate ? 'Crear solicitud →' : 'Gestionar solicitudes →'}</span>
        </Link>
      </section>

      <section className="security-note">
        <strong>Control aplicado en backend</strong>
        <p>El rol y el departamento provienen de tu sesión. Cambiar la interfaz no amplía los permisos de la API.</p>
      </section>
    </div>
  )
}
