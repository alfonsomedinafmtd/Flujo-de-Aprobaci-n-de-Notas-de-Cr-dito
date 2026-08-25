import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { ApiError, apiRequest } from '../api'
import { EmptyState, ErrorMessage, Loading } from '../components/Feedback'
import type {
  CreditNoteAnalytics,
  CreditNoteAnalyticsAmount,
  CreditNoteAnalyticsGroup,
  CreditNoteStatus,
} from '../types'
import { formatDate, formatMoney } from '../utils/format'

interface AnalyticsFilters {
  dateFrom: string
  dateTo: string
  departmentId: string
  status: '' | CreditNoteStatus
}

const EMPTY_FILTERS: AnalyticsFilters = {
  dateFrom: '',
  dateTo: '',
  departmentId: '',
  status: '',
}

function formatAmounts(amounts: CreditNoteAnalyticsAmount[]): string {
  if (amounts.length === 0) return 'Sin monto'
  return amounts.map((item) => formatMoney(item.total_amount, item.currency)).join(' · ')
}

function formatResolutionTime(hours: number | null): string {
  if (hours === null) return 'Sin decisiones'
  if (hours < 24) return `${hours.toLocaleString('es-VE')} h`
  return `${(hours / 24).toLocaleString('es-VE', { maximumFractionDigits: 1 })} días`
}

function formatPeriod(period: string): string {
  return new Intl.DateTimeFormat('es-VE', {
    month: 'short',
    year: 'numeric',
    timeZone: 'UTC',
  }).format(new Date(`${period}-01T00:00:00Z`))
}

function StatusDistribution({ group }: { group: CreditNoteAnalyticsGroup }) {
  const percentage = (value: number) => (group.total ? `${(value * 100) / group.total}%` : '0%')
  return (
    <div className="status-distribution" aria-label={`Distribución de ${group.label}`}>
      <span className="distribution-approved" style={{ width: percentage(group.approved) }} />
      <span className="distribution-pending" style={{ width: percentage(group.pending) }} />
      <span className="distribution-rejected" style={{ width: percentage(group.rejected) }} />
    </div>
  )
}

export function AnalyticsPage() {
  const [filters, setFilters] = useState<AnalyticsFilters>(EMPTY_FILTERS)
  const [analytics, setAnalytics] = useState<CreditNoteAnalytics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    const query = new URLSearchParams()
    if (filters.dateFrom) query.set('date_from', filters.dateFrom)
    if (filters.dateTo) query.set('date_to', filters.dateTo)
    if (filters.departmentId) query.set('department_id', filters.departmentId)
    if (filters.status) query.set('status', filters.status)

    setLoading(true)
    setError('')
    apiRequest<CreditNoteAnalytics>(`/credit-notes/analytics?${query.toString()}`)
      .then((data) => active && setAnalytics(data))
      .catch((caught) => {
        if (active) setError(caught instanceof ApiError ? caught.message : 'No fue posible cargar la analítica.')
      })
      .finally(() => active && setLoading(false))
    return () => { active = false }
  }, [filters])

  const maxDepartmentTotal = useMemo(
    () => Math.max(...(analytics?.by_department.map((item) => item.total) ?? [1]), 1),
    [analytics],
  )

  function updateFilter<Key extends keyof AnalyticsFilters>(key: Key, value: AnalyticsFilters[Key]) {
    setFilters((current) => ({ ...current, [key]: value }))
  }

  return (
    <div className="page analytics-page">
      <header className="page-header analytics-header">
        <div>
          <span className="eyebrow">Planificación Financiera</span>
          <h1>Analítica de notas de crédito</h1>
          <p>Visión consolidada de solicitudes, montos, responsables y tiempos de atención.</p>
        </div>
        <span className="admin-only-pill">Acceso exclusivo · Administrador</span>
      </header>

      <section className="analytics-filters" aria-label="Filtros del reporte">
        <label>
          Desde
          <input type="date" value={filters.dateFrom} onChange={(event) => updateFilter('dateFrom', event.target.value)} />
        </label>
        <label>
          Hasta
          <input type="date" value={filters.dateTo} onChange={(event) => updateFilter('dateTo', event.target.value)} />
        </label>
        <label>
          Área
          <select value={filters.departmentId} onChange={(event) => updateFilter('departmentId', event.target.value)}>
            <option value="">Todas las áreas</option>
            {analytics?.departments.map((department) => (
              <option key={department.id} value={department.id}>{department.name}</option>
            ))}
          </select>
        </label>
        <label>
          Estado
          <select value={filters.status} onChange={(event) => updateFilter('status', event.target.value as AnalyticsFilters['status'])}>
            <option value="">Todos los estados</option>
            <option value="PENDING">Pendiente</option>
            <option value="APPROVED">Aprobada</option>
            <option value="REJECTED">Rechazada</option>
          </select>
        </label>
        <button className="button button-secondary" type="button" onClick={() => setFilters(EMPTY_FILTERS)}>
          Limpiar filtros
        </button>
      </section>

      {loading && <Loading label="Consolidando indicadores…" />}
      {error && <ErrorMessage message={error} />}

      {!loading && !error && analytics && (
        <>
          <section className="analytics-metric-grid" aria-label="Indicadores principales">
            <article className="analytics-metric-card">
              <span>Solicitudes</span>
              <strong>{analytics.summary.total}</strong>
              <small>{analytics.summary.pending} pendientes</small>
            </article>
            <article className="analytics-metric-card metric-approved">
              <span>Aprobación</span>
              <strong>{analytics.summary.approval_rate.toLocaleString('es-VE')}%</strong>
              <small>Sobre solicitudes resueltas</small>
            </article>
            <article className="analytics-metric-card metric-rejected">
              <span>Rechazo</span>
              <strong>{analytics.summary.rejection_rate.toLocaleString('es-VE')}%</strong>
              <small>{analytics.summary.rejected} solicitudes</small>
            </article>
            <article className="analytics-metric-card metric-pending">
              <span>Tiempo promedio</span>
              <strong>{formatResolutionTime(analytics.summary.average_resolution_hours)}</strong>
              <small>Desde creación hasta decisión</small>
            </article>
          </section>

          <section className="amount-grid" aria-label="Montos por moneda">
            {analytics.amounts.map((amount) => (
              <article className="amount-card" key={amount.currency}>
                <div><span className="eyebrow">Monto total · {amount.currency}</span><strong>{formatMoney(amount.total_amount, amount.currency)}</strong></div>
                <small>Promedio {formatMoney(amount.average_amount, amount.currency)} por solicitud</small>
              </article>
            ))}
          </section>

          {analytics.summary.total === 0 ? (
            <EmptyState title="Sin datos para los filtros" detail="Ajusta el período, área o estado seleccionado." />
          ) : (
            <>
              <section className="analytics-panel" aria-labelledby="department-analytics-title">
                <div className="section-heading">
                  <span className="eyebrow">Comparativo por área</span>
                  <h2 id="department-analytics-title">Solicitudes por departamento</h2>
                </div>
                <div className="department-bars">
                  {analytics.by_department.map((group) => (
                    <article className="department-bar-row" key={group.key}>
                      <div className="bar-copy">
                        <strong>{group.label}</strong>
                        <small>{formatAmounts(group.amounts)}</small>
                      </div>
                      <div className="bar-visual">
                        <div className="bar-track"><span style={{ width: `${(group.total * 100) / maxDepartmentTotal}%` }} /></div>
                        <strong>{group.total}</strong>
                      </div>
                      <StatusDistribution group={group} />
                      <small className="distribution-caption">{group.approved} aprobadas · {group.pending} pendientes · {group.rejected} rechazadas</small>
                    </article>
                  ))}
                </div>
              </section>

              <section className="analytics-two-column">
                <div className="analytics-panel">
                  <div className="section-heading"><span className="eyebrow">Evolución</span><h2>Tendencia mensual</h2></div>
                  <div className="trend-list">
                    {analytics.trend.map((item) => (
                      <div className="trend-row" key={item.period}>
                        <strong>{formatPeriod(item.period)}</strong>
                        <span>{item.total} solicitudes</span>
                        <small>{item.approved} aprobadas · {item.pending} pendientes · {item.rejected} rechazadas</small>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="analytics-panel">
                  <div className="section-heading"><span className="eyebrow">Distribución</span><h2>Actividad por cargo</h2></div>
                  <div className="compact-ranking">
                    {analytics.by_position.map((group, index) => (
                      <div className="ranking-row" key={group.key}>
                        <span>{String(index + 1).padStart(2, '0')}</span>
                        <div><strong>{group.label}</strong><small>{formatAmounts(group.amounts)}</small></div>
                        <strong>{group.total}</strong>
                      </div>
                    ))}
                  </div>
                </div>
              </section>

              <section className="analytics-panel" aria-labelledby="requester-title">
                <div className="section-heading"><span className="eyebrow">Trazabilidad operativa</span><h2 id="requester-title">Actividad por solicitante</h2></div>
                <div className="table-card analytics-table">
                  <table>
                    <thead><tr><th>Solicitante</th><th>Área y cargo</th><th>Total</th><th>Pendientes</th><th>Aprobadas</th><th>Rechazadas</th><th>Montos</th></tr></thead>
                    <tbody>
                      {analytics.by_requester.map((requester) => (
                        <tr key={requester.user_id}>
                          <td><strong>{requester.full_name}</strong><small className="cell-detail">@{requester.username}</small></td>
                          <td><strong>{requester.department_name}</strong><small className="cell-detail">{requester.position_title}</small></td>
                          <td><strong>{requester.total}</strong></td>
                          <td>{requester.pending}</td>
                          <td>{requester.approved}</td>
                          <td>{requester.rejected}</td>
                          <td>{formatAmounts(requester.amounts)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>

              <section className="analytics-panel" aria-labelledby="pending-title">
                <div className="section-heading"><span className="eyebrow">Atención requerida</span><h2 id="pending-title">Pendientes más antiguas</h2></div>
                {analytics.oldest_pending.length === 0 ? (
                  <EmptyState title="Sin solicitudes pendientes" detail="No hay solicitudes que requieran decisión para los filtros actuales." />
                ) : (
                  <div className="table-card analytics-table">
                    <table>
                      <thead><tr><th>Solicitud</th><th>Solicitante</th><th>Área y cargo</th><th>Monto</th><th>Antigüedad</th><th>Creada</th><th></th></tr></thead>
                      <tbody>
                        {analytics.oldest_pending.map((note) => (
                          <tr key={note.id}>
                            <td><strong>NC-{String(note.id).padStart(4, '0')}</strong></td>
                            <td>{note.requester_full_name}</td>
                            <td><strong>{note.department_name}</strong><small className="cell-detail">{note.position_title}</small></td>
                            <td>{formatMoney(note.amount, note.currency)}</td>
                            <td><span className="age-pill">{note.age_days} días</span></td>
                            <td>{formatDate(note.created_at)}</td>
                            <td><Link className="table-link" to={`/credit-notes/${note.id}`}>Revisar</Link></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </section>
            </>
          )}
        </>
      )}
    </div>
  )
}
