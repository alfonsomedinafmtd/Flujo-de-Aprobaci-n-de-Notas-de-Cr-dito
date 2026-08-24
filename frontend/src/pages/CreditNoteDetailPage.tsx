import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { ApiError, apiRequest } from '../api'
import { useAuth } from '../auth/AuthContext'
import { ErrorMessage, Loading } from '../components/Feedback'
import { StatusBadge } from '../components/StatusBadge'
import type { CreditNote } from '../types'
import { formatDate, formatMoney } from '../utils/format'
import { canDecideCreditNote, roleLabel } from '../utils/permissions'

export function CreditNoteDetailPage() {
  const { noteId } = useParams()
  const { user, csrfToken } = useAuth()
  const [note, setNote] = useState<CreditNote | null>(null)
  const [comment, setComment] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    setError('')
    apiRequest<CreditNote>(`/credit-notes/${noteId}`)
      .then(setNote)
      .catch((caught) => setError(caught instanceof ApiError ? caught.message : 'No fue posible cargar la solicitud.'))
  }, [noteId])

  async function decide(action: 'approve' | 'reject') {
    if (!note) return
    setError('')
    setSubmitting(true)
    try {
      const updated = await apiRequest<CreditNote>(`/credit-notes/${note.id}/${action}`, {
        method: 'POST',
        csrfToken,
        body: { expected_version: note.version, comment: comment || null },
      })
      setNote(updated)
      setComment('')
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'No fue posible registrar la decisión.')
    } finally {
      setSubmitting(false)
    }
  }

  if (error && !note) return <div className="page"><ErrorMessage message={error} /><Link to="/credit-notes">← Volver</Link></div>
  if (!note) return <Loading label="Consultando solicitud…" />

  const canDecide = user && canDecideCreditNote(user.role) && note.status === 'PENDING'

  return (
    <div className="page">
      <Link className="back-link" to="/credit-notes">← Volver a solicitudes</Link>
      <header className="page-header detail-header">
        <div><span className="eyebrow">Solicitud NC-{String(note.id).padStart(4, '0')}</span><h1>{note.reason}</h1><p>Creada por {note.creator_username} · {formatDate(note.created_at)}</p></div>
        <StatusBadge status={note.status} />
      </header>
      {error && <ErrorMessage message={error} />}

      <section className="detail-grid">
        <article className="detail-card">
          <span>Monto</span><strong>{formatMoney(note.amount, note.currency)}</strong>
        </article>
        <article className="detail-card"><span>Departamento</span><strong>{note.requesting_department.name}</strong></article>
        <article className="detail-card"><span>Tienda</span><strong>{note.store.name}</strong></article>
        <article className="detail-card"><span>Compañía</span><strong>{note.company.name}</strong></article>
      </section>

      {canDecide && (
        <section className="decision-card">
          <div><span className="eyebrow">Segregación de funciones</span><h2>Registrar decisión</h2><p>La acción quedará asociada a tu usuario y no podrá editarse.</p></div>
          <label>Comentario<textarea rows={3} maxLength={1000} value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Obligatorio para rechazar" /></label>
          <div className="form-actions">
            <button className="button button-danger" disabled={submitting || !comment.trim()} type="button" onClick={() => void decide('reject')}>Rechazar</button>
            <button className="button button-primary" disabled={submitting} type="button" onClick={() => void decide('approve')}>Aprobar</button>
          </div>
        </section>
      )}

      <section className="timeline-section">
        <div className="section-heading"><span className="eyebrow">Auditoría</span><h2>Historial de la solicitud</h2></div>
        <ol className="timeline">
          {note.events.map((event) => (
            <li key={event.id}>
              <span className="timeline-dot" aria-hidden="true" />
              <div className="timeline-content">
                <div><strong>{event.action === 'CREATED' ? 'Solicitud creada' : event.action === 'APPROVED' ? 'Solicitud aprobada' : 'Solicitud rechazada'}</strong><time>{formatDate(event.occurred_at)}</time></div>
                <p>{event.comment ?? 'Sin comentario'}</p>
                <small>{event.actor_username} · {roleLabel(event.actor_role)}</small>
              </div>
            </li>
          ))}
        </ol>
      </section>
    </div>
  )
}

