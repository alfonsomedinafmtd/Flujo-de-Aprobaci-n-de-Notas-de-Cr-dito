import { useState, type FormEvent } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'

import { ApiError } from '../api'
import { useAuth } from '../auth/AuthContext'

export function LoginPage() {
  const { user, loading, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (!loading && user) {
    return <Navigate to="/" replace />
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(username, password)
      const destination = (location.state as { from?: string } | null)?.from ?? '/'
      navigate(destination, { replace: true })
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'No fue posible iniciar sesión.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="login-page">
      <section className="login-intro">
        <div className="brand brand-light">
          <span className="brand-mark" aria-hidden="true">F</span>
          <div><strong>Finanzas</strong><small>Portal interno</small></div>
        </div>
        <div>
          <span className="eyebrow">Transformación financiera</span>
          <h1>Decisiones claras.<br />Procesos trazables.</h1>
          <p>Consulta la estructura de la VP y gestiona notas de crédito con controles por rol y departamento.</p>
        </div>
        <small>Información ficticia para fines de evaluación técnica.</small>
      </section>

      <section className="login-form-panel">
        <form className="login-card" onSubmit={handleSubmit}>
          <div>
            <span className="eyebrow">Acceso seguro</span>
            <h2>Iniciar sesión</h2>
            <p>Ingresa con las credenciales generadas por el seed.</p>
          </div>
          {error && <div className="alert alert-error" role="alert">{error}</div>}
          <label>
            Usuario
            <input
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
          </label>
          <label>
            Contraseña
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          <button className="button button-primary" disabled={submitting} type="submit">
            {submitting ? 'Validando…' : 'Entrar al portal'}
          </button>
        </form>
      </section>
    </main>
  )
}

