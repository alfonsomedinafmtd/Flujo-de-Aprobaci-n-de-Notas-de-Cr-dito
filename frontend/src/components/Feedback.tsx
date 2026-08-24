export function Loading({ label = 'Cargando…' }: { label?: string }) {
  return <div className="feedback">{label}</div>
}

export function ErrorMessage({ message }: { message: string }) {
  return <div className="alert alert-error" role="alert">{message}</div>
}

export function EmptyState({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="empty-state">
      <strong>{title}</strong>
      <p>{detail}</p>
    </div>
  )
}

