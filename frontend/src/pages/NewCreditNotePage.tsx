import { useEffect, useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'

import { ApiError, apiRequest } from '../api'
import { useAuth } from '../auth/AuthContext'
import { ErrorMessage, Loading } from '../components/Feedback'
import type { CreditNote, CreditNoteCatalog, Currency } from '../types'
import { canCreateCreditNote } from '../utils/permissions'

export function NewCreditNotePage() {
  const { user, csrfToken } = useAuth()
  const navigate = useNavigate()
  const [catalog, setCatalog] = useState<CreditNoteCatalog | null>(null)
  const [amount, setAmount] = useState('')
  const [currency, setCurrency] = useState<Currency>('USD')
  const [reason, setReason] = useState('')
  const [storeId, setStoreId] = useState('')
  const [companyId, setCompanyId] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    apiRequest<CreditNoteCatalog>('/credit-notes/catalog')
      .then(setCatalog)
      .catch((caught) => setError(caught instanceof ApiError ? caught.message : 'No fue posible cargar el catálogo.'))
  }, [])

  if (user && !canCreateCreditNote(user.role)) {
    return <Navigate to="/credit-notes" replace />
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const note = await apiRequest<CreditNote>('/credit-notes', {
        method: 'POST',
        csrfToken,
        body: {
          amount,
          currency,
          reason,
          store_id: Number(storeId),
          company_id: Number(companyId),
        },
      })
      navigate(`/credit-notes/${note.id}`)
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'No fue posible crear la solicitud.')
    } finally {
      setSubmitting(false)
    }
  }

  if (!catalog && !error) return <Loading label="Preparando formulario…" />

  return (
    <div className="page narrow-page">
      <header className="page-header">
        <div><span className="eyebrow">Nueva solicitud</span><h1>Crear nota de crédito</h1></div>
        <p>El departamento solicitante se asignará desde tu sesión: <strong>{user?.department_name}</strong>.</p>
      </header>
      {error && <ErrorMessage message={error} />}
      {catalog && (
        <form className="form-card" onSubmit={handleSubmit}>
          <div className="form-row">
            <label>Monto<input inputMode="decimal" min="0.01" step="0.01" value={amount} onChange={(e) => setAmount(e.target.value)} required /></label>
            <label>Moneda<select value={currency} onChange={(e) => setCurrency(e.target.value as Currency)}><option value="USD">USD</option><option value="VES">VES</option></select></label>
          </div>
          <label>Tienda<select value={storeId} onChange={(e) => setStoreId(e.target.value)} required><option value="">Selecciona una tienda</option>{catalog.stores.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
          <label>Compañía<select value={companyId} onChange={(e) => setCompanyId(e.target.value)} required><option value="">Selecciona una compañía</option>{catalog.companies.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
          <label>Motivo<textarea minLength={5} maxLength={1000} rows={5} value={reason} onChange={(e) => setReason(e.target.value)} required /></label>
          <div className="form-actions"><button className="button button-secondary" type="button" onClick={() => navigate(-1)}>Cancelar</button><button className="button button-primary" disabled={submitting || !csrfToken} type="submit">{submitting ? 'Creando…' : 'Crear solicitud'}</button></div>
        </form>
      )}
    </div>
  )
}

