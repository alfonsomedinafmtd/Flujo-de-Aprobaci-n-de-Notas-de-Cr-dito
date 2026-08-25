import type { UserRole } from '../types'

export function canCreateCreditNote(role: UserRole): boolean {
  return role === 'COLLABORATOR'
}

export function canDecideCreditNote(role: UserRole): boolean {
  return role === 'ADMIN' || role === 'DEPARTMENT_HEAD'
}

export function canViewAnalytics(role: UserRole): boolean {
  return role === 'ADMIN'
}

export function roleLabel(role: UserRole): string {
  const labels: Record<UserRole, string> = {
    ADMIN: 'Administrador',
    DEPARTMENT_HEAD: 'Jefe de departamento',
    COLLABORATOR: 'Colaborador',
  }
  return labels[role]
}
