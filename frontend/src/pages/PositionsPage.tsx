import { useEffect, useState } from 'react'

import { ApiError, apiRequest } from '../api'
import { EmptyState, ErrorMessage, Loading } from '../components/Feedback'
import type { Position } from '../types'

export function PositionsPage() {
  const [positions, setPositions] = useState<Position[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    apiRequest<Position[]>('/organization/positions')
      .then((data) => active && setPositions(data))
      .catch((caught) => active && setError(caught instanceof ApiError ? caught.message : 'No fue posible cargar los cargos.'))
      .finally(() => active && setLoading(false))
    return () => { active = false }
  }, [])

  return (
    <div className="page">
      <header className="page-header">
        <div><span className="eyebrow">Modelo de responsabilidades</span><h1>Cargos y funciones</h1></div>
        <p>Las funciones se relacionan con el cargo y el departamento sin duplicarse por colaborador.</p>
      </header>
      {loading && <Loading label="Consultando cargos…" />}
      {error && <ErrorMessage message={error} />}
      {!loading && !error && positions.length === 0 && (
        <EmptyState title="Sin cargos" detail="No hay cargos disponibles dentro de tu alcance." />
      )}
      <section className="position-grid">
        {positions.map((position) => (
          <article className="position-card" key={position.id}>
            <span className="eyebrow">{position.department.code} · {position.seniority.replace('_', ' ')}</span>
            <h2>{position.title}</h2>
            <p>{position.department.name}</p>
            <div className="tag-list">
              {position.functions.map((item) => <span className="tag" key={item.id}>{item.name}</span>)}
            </div>
          </article>
        ))}
      </section>
    </div>
  )
}

