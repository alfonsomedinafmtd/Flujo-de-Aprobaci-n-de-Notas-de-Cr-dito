import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { ApiError, apiRequest } from '../api'
import { useAuth } from '../auth/AuthContext'
import { EmptyState, ErrorMessage, Loading } from '../components/Feedback'
import { StatusBadge } from '../components/StatusBadge'
import type { CreditNote, CreditNoteList, CreditNoteStatus } from '../types'
import { formatDate, formatMoney } from '../utils/format'
import { canCreateCreditNote } from '../utils/permissions'

type Filter = 'ALL' | CreditNoteStatus

export function CreditNotesPage() {
  const { user } = useAuth()
  const [notes, setNotes] = useState<CreditNote[]>([])
  const [total, setTotal] = useState(0)
  const [filter, setFilter] = useState<Filter>('ALL')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    apiRequest<CreditNoteList>('/credit-notes?limit=100')
      .then((data) => {
        if (active) { setNotes(data.items); setTotal(data.total) }
      })
      .catch((caught) => active && setError(caught instanceof ApiError ? caught.message : 'No fue posible cargar las solicitudes.'))
      .finally(() => active && setLoading(false))
    return () => { active = false }
  }, [])

  const visibleNotes = useMemo(
    () => filter === 'ALL' ? notes : notes.filter((note) => note.status === filter),
    [filter, notes],
  )

  return (
    <div className="page">
      <header className="page-header">
        <div><span className="eyebrow">Proceso auditable</span><h1>Notas de crédito</h1><p>{total} solicitudes dentro de tu alcance.</p></div>
        {user && canCreateCreditNote(user.role) && <Link className="button button-primary" to="/credit-notes/new">Nueva solicitud</Link>}
      </header>

      <div className="filter-bar" role="group" aria-label="Filtrar por estado">
        {(['ALL', 'PENDING', 'APPROVED', 'REJECTED'] as Filter[]).map((item) => (
          <button key={item} className={filter === item ? 'filter active' : 'filter'} onClick={() => setFilter(item)} type="button">
            {item === 'ALL' ? 'Todas' : item === 'PENDING' ? 'Pendientes' : item === 'APPROVED' ? 'Aprobadas' : 'Rechazadas'}
          </button>
        ))}
      </div>

      {loading && <Loading label="Consultando solicitudes…" />}
      {error && <ErrorMessage message={error} />}
      {!loading && !error && visibleNotes.length === 0 && (
        <EmptyState title="Sin resultados" detail="No existen solicitudes para el filtro seleccionado." />
      )}
      {visibleNotes.length > 0 && (
        <div className="table-card">
          <table>
            <thead><tr><th>Solicitud</th><th>Creada</th><th>Departamento</th><th>Monto</th><th>Estado</th><th></th></tr></thead>
            <tbody>
              {visibleNotes.map((note) => (
                <tr key={note.id}>
                  <td><strong>NC-{String(note.id).padStart(4, '0')}</strong><small className="cell-detail">{note.company.name}</small></td>
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
    </div>
  )
}

