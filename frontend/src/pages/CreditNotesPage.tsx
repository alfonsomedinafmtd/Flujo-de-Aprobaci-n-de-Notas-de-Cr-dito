import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { ApiError, apiRequest } from '../api'
import { useAuth } from '../auth/AuthContext'
import { EmptyState, ErrorMessage, Loading } from '../components/Feedback'
import { StatusBadge } from '../components/StatusBadge'
import type { CreditNote, CreditNoteList, CreditNoteStatus } from '../types'
import { formatDate, formatMoney } from '../utils/format'
import { canCreateCreditNote, roleLabel } from '../utils/permissions'

type Filter = 'ALL' | CreditNoteStatus
const PAGE_SIZE = 10

export function CreditNotesPage() {
  const { user } = useAuth()
  const [notes, setNotes] = useState<CreditNote[]>([])
  const [total, setTotal] = useState(0)
  const [filter, setFilter] = useState<Filter>('ALL')
  const [page, setPage] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    const query = new URLSearchParams({
      limit: String(PAGE_SIZE),
      offset: String(page * PAGE_SIZE),
    })
    if (filter !== 'ALL') query.set('status', filter)

    setLoading(true)
    setError('')
    apiRequest<CreditNoteList>(`/credit-notes?${query.toString()}`)
      .then((data) => {
        if (active) { setNotes(data.items); setTotal(data.total) }
      })
      .catch((caught) => active && setError(caught instanceof ApiError ? caught.message : 'No fue posible cargar las solicitudes.'))
      .finally(() => active && setLoading(false))
    return () => { active = false }
  }, [filter, page])

  const pageCount = Math.ceil(total / PAGE_SIZE)

  return (
    <div className="page">
      <header className="page-header">
        <div><span className="eyebrow">Proceso auditable</span><h1>Notas de crédito</h1><p>{total} {total === 1 ? 'solicitud' : 'solicitudes'} para el filtro seleccionado.</p></div>
        {user && canCreateCreditNote(user.role) && <Link className="button button-primary" to="/credit-notes/new">Nueva solicitud</Link>}
      </header>

      <div className="filter-bar" role="group" aria-label="Filtrar por estado">
        {(['ALL', 'PENDING', 'APPROVED', 'REJECTED'] as Filter[]).map((item) => (
          <button
            key={item}
            aria-pressed={filter === item}
            className={filter === item ? 'filter active' : 'filter'}
            onClick={() => { setFilter(item); setPage(0) }}
            type="button"
          >
            {item === 'ALL' ? 'Todas' : item === 'PENDING' ? 'Pendientes' : item === 'APPROVED' ? 'Aprobadas' : 'Rechazadas'}
          </button>
        ))}
      </div>

      {loading && <Loading label="Consultando solicitudes…" />}
      {error && <ErrorMessage message={error} />}
      {!loading && !error && notes.length === 0 && (
        <EmptyState title="Sin resultados" detail="No existen solicitudes para el filtro seleccionado." />
      )}
      {!loading && !error && notes.length > 0 && (
        <div className="table-card">
          <table>
            <thead><tr><th>Solicitud</th><th>Solicitante</th><th>Creada</th><th>Departamento</th><th>Monto</th><th>Estado</th><th></th></tr></thead>
            <tbody>
              {notes.map((note) => (
                <tr key={note.id}>
                  <td className="cell-summary">
                    <strong>NC-{String(note.id).padStart(4, '0')} · {note.reason}</strong>
                    <small className="cell-detail">{note.store.name} · {note.company.name}</small>
                  </td>
                  <td>
                    <strong>{note.creator_full_name}</strong>
                    <small className="cell-detail">@{note.creator_username} · {note.requester_position_title}</small>
                  </td>
                  <td>{formatDate(note.created_at)}</td>
                  <td>{note.requesting_department.name}</td>
                  <td>{formatMoney(note.amount, note.currency)}</td>
                  <td><StatusBadge status={note.status} /></td>
                  <td><Link className="table-link" to={`/credit-notes/${note.id}`}>Ver detalle</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {!loading && !error && pageCount > 1 && (
        <nav className="pagination" aria-label="Paginación de solicitudes">
          <button className="button button-secondary" disabled={page === 0} onClick={() => setPage((current) => current - 1)} type="button">Anterior</button>
          <span>Página {page + 1} de {pageCount}</span>
          <button className="button button-secondary" disabled={page + 1 >= pageCount} onClick={() => setPage((current) => current + 1)} type="button">Siguiente</button>
        </nav>
      )}
    </div>
  )
}
