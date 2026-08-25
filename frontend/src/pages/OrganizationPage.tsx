import { useEffect, useState } from 'react'

import { ApiError, apiRequest } from '../api'
import { useAuth } from '../auth/AuthContext'
import { EmptyState, ErrorMessage, Loading } from '../components/Feedback'
import { StatusBadge } from '../components/StatusBadge'
import type { Department, EmployeeDetail } from '../types'
import { formatCalendarDate } from '../utils/format'
import { roleLabel } from '../utils/permissions'

export function OrganizationPage() {
  const { user } = useAuth()
  const [departments, setDepartments] = useState<Department[]>([])
  const [employees, setEmployees] = useState<EmployeeDetail[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!user) return
    let active = true
    const employeesRequest = user.role === 'COLLABORATOR'
      ? apiRequest<EmployeeDetail>('/organization/profile').then((profile) => [profile])
      : apiRequest<EmployeeDetail[]>('/organization/employees')

    setLoading(true)
    setError('')
    Promise.all([
      apiRequest<Department[]>('/organization/departments'),
      employeesRequest,
    ])
      .then(([visibleDepartments, visibleEmployees]) => {
        if (!active) return
        setDepartments(visibleDepartments)
        setEmployees(visibleEmployees)
      })
      .catch((caught) => active && setError(caught instanceof ApiError ? caught.message : 'No fue posible cargar la estructura organizacional.'))
      .finally(() => active && setLoading(false))
    return () => { active = false }
  }, [user])

  const isCollaborator = user?.role === 'COLLABORATOR'

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <span className="eyebrow">Módulo organizacional</span>
          <h1>{isCollaborator ? 'Mi perfil y departamento' : 'Estructura organizacional'}</h1>
        </div>
        <p>La API limita automáticamente departamentos y colaboradores al alcance de tu sesión.</p>
      </header>
      {loading && <Loading label="Consultando estructura organizacional…" />}
      {error && <ErrorMessage message={error} />}

      {!loading && !error && departments.length > 0 && (
        <section className="organization-section">
          <div className="section-heading">
            <span className="eyebrow">Alcance autorizado</span>
            <h2>{departments.length === 1 ? 'Departamento' : 'Departamentos'}</h2>
          </div>
          <div className="department-grid">
            {departments.map((department) => (
              <article className="department-card" key={department.id}>
                <span className="eyebrow">{department.code}</span>
                <h3>{department.name}</h3>
                <p>{department.description ?? 'Sin descripción disponible.'}</p>
              </article>
            ))}
          </div>
        </section>
      )}

      {!loading && !error && employees.length === 0 && (
        <EmptyState title="Sin colaboradores" detail="No hay registros disponibles dentro de tu alcance." />
      )}
      {employees.length > 0 && (
        <section className="organization-section">
          <div className="section-heading">
            <span className="eyebrow">Información detallada</span>
            <h2>{isCollaborator ? 'Mi perfil' : 'Colaboradores'}</h2>
          </div>
          <div className="table-card">
            <table>
              <thead><tr><th>Colaborador</th><th>Acceso al portal</th><th>Cargo</th><th>Seniority</th><th>Departamento</th><th>País</th><th>Ingreso</th><th>Estado</th></tr></thead>
              <tbody>
                {employees.map((employee) => (
                  <tr key={employee.id}>
                    <td><strong>{employee.full_name}</strong><small className="cell-detail">{employee.internal_email}</small></td>
                    <td>
                      <strong>{employee.portal_role ? roleLabel(employee.portal_role) : 'Sin acceso'}</strong>
                      <small className="cell-detail">{employee.username ? `@${employee.username}` : 'Sin usuario'}</small>
                    </td>
                    <td>{employee.position_title}</td>
                    <td>{employee.seniority.replace('_', ' ')}</td>
                    <td>{employee.department_name}</td>
                    <td>{employee.country}</td>
                    <td>{formatCalendarDate(employee.hire_date)}</td>
                    <td><StatusBadge status={employee.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  )
}
