import { useState, type FormEvent } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'

import { ApiError } from '../api'
import farmatodoLogo from '../assets/logo-farmatodo.svg'
import { useAuth } from '../auth/AuthContext'

export function LoginPage() {
  const { user, loading, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const requestedDestination = (location.state as { from?: string } | null)?.from

  if (!loading && user) {
    return <Navigate to="/" replace />
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(username, password)
      const destination = requestedDestination ?? '/'
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
          <img className="brand-logo" src={farmatodoLogo} alt="Farmatodo" />
        </div>
        <div className="login-intro-copy">
          <span className="eyebrow">Planificación Financiera</span>
          <h1>Portal interno de gestión financiera</h1>
          <p>Consulta la estructura organizacional y gestiona solicitudes de notas de crédito mediante controles de acceso, segregación de funciones y trazabilidad.</p>
        </div>
        <small>Vicepresidencia de Finanzas · Entorno de evaluación con información ficticia.</small>
      </section>

      <section className="login-form-panel">
        <form className="login-card" onSubmit={handleSubmit}>
          <div>
            <span className="eyebrow">Autenticación</span>
            <h2>Acceso al portal</h2>
            <p>Utiliza las credenciales asignadas según tu rol.</p>
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
