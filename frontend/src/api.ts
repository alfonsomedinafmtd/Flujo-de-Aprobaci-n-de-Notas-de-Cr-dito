const API_URL = import.meta.env.VITE_API_URL ?? '/api'

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

interface ApiOptions extends Omit<RequestInit, 'body'> {
  body?: unknown
  csrfToken?: string | null
}

export async function apiRequest<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const { body, csrfToken, ...requestOptions } = options
  const headers = new Headers(requestOptions.headers)
  if (body !== undefined) {
    headers.set('Content-Type', 'application/json')
  }
  if (csrfToken) {
    headers.set('X-CSRF-Token', csrfToken)
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...requestOptions,
    body: body === undefined ? undefined : JSON.stringify(body),
    credentials: 'include',
    headers,
  })

  if (response.status === 204) {
    return undefined as T
  }

  const data = (await response.json().catch(() => null)) as { detail?: string } | T | null
  if (!response.ok) {
    const message = data && typeof data === 'object' && 'detail' in data && typeof data.detail === 'string'
      ? data.detail
      : 'No fue posible completar la operación.'
    throw new ApiError(response.status, message)
  }
  return data as T
}
