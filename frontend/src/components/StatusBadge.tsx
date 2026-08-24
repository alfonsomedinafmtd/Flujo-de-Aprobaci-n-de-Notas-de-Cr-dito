import type { CreditNoteStatus, EmployeeStatus } from '../types'

type Status = CreditNoteStatus | EmployeeStatus

const labels: Record<Status, string> = {
  PENDING: 'Pendiente',
  APPROVED: 'Aprobada',
  REJECTED: 'Rechazada',
  ACTIVE: 'Activo',
  INACTIVE: 'Inactivo',
}

export function StatusBadge({ status }: { status: Status }) {
  return <span className={`status status-${status.toLowerCase()}`}>{labels[status]}</span>
}

