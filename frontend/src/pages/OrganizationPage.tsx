import { useEffect, useState } from 'react'

import { ApiError, apiRequest } from '../api'
import { EmptyState, ErrorMessage, Loading } from '../components/Feedback'
import { StatusBadge } from '../components/StatusBadge'
import type { EmployeeDirectoryItem } from '../types'

export function OrganizationPage() {
  const [employees, setEmployees] = useState<EmployeeDirectoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    apiRequest<EmployeeDirectoryItem[]>('/organization/directory')
      .then((data) => active && setEmployees(data))
      .catch((caught) => active && setError(caught instanceof ApiError ? caught.message : 'No fue posible cargar el directorio.'))
      .finally(() => active && setLoading(false))
    return () => { active = false }
  }, [])

  return (
    <div className="page">
      <header className="page-header">
        <div><span className="eyebrow">Módulo organizacional</span><h1>Directorio de colaboradores</h1></div>
        <p>La API limita automáticamente los resultados al alcance de tu sesión.</p>
      </header>
      {loading && <Loading label="Consultando colaboradores…" />}
      {error && <ErrorMessage message={error} />}
      {!loading && !error && employees.length === 0 && (
        <EmptyState title="Sin colaboradores" detail="No hay registros disponibles dentro de tu alcance." />
      )}
      {employees.length > 0 && (
        <div className="table-card">
          <table>
            <thead><tr><th>Colaborador</th><th>Cargo</th><th>Seniority</th><th>Departamento</th><th>Estado</th></tr></thead>
            <tbody>
              {employees.map((employee) => (
                <tr key={employee.id}>
                  <td><strong>{employee.full_name}</strong></td>
                  <td>{employee.position_title}</td>
                  <td>{employee.seniority.replace('_', ' ')}</td>
                  <td>{employee.department_name}</td>
                  <td><StatusBadge status={employee.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

