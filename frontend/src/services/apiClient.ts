export interface ApiClientOptions {
  baseUrl?: string
  timeoutMs?: number
}

export interface ApiEnvelope<T> {
  data: T | null
  meta: { request_id?: string | null; page?: number | null; page_size?: number | null; total?: number | null }
  error: { code: string; message: string; details?: unknown } | null
}

export interface ApiRequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown
}

export class ApiClientError extends Error {
  readonly status: number
  readonly details: unknown

  constructor(message: string, status: number, details?: unknown) {
    super(message)
    this.name = 'ApiClientError'
    this.status = status
    this.details = details
  }
}

function readBaseUrl() {
  const configuredUrl = import.meta.env.VITE_API_BASE_URL?.trim()
  return configuredUrl ? configuredUrl.replace(/\/$/, '') : ''
}

export class ApiClient {
  private readonly baseUrl: string
  private readonly timeoutMs: number

  constructor(options: ApiClientOptions = {}) {
    this.baseUrl = options.baseUrl?.replace(/\/$/, '') ?? readBaseUrl()
    this.timeoutMs = options.timeoutMs ?? 10_000
  }

  async request<TResponse>(path: string, options: ApiRequestOptions = {}): Promise<TResponse> {
    if (!this.baseUrl) throw new ApiClientError('API base URL is not configured. Set VITE_API_BASE_URL to enable backend requests.', 0)

    const controller = new AbortController()
    const timeout = window.setTimeout(() => controller.abort(), this.timeoutMs)
    const headers = new Headers(options.headers)
    headers.set('Accept', 'application/json')
    if (options.body !== undefined) headers.set('Content-Type', 'application/json')

    try {
      const response = await fetch(`${this.baseUrl}${path.startsWith('/') ? path : `/${path}`}`, { ...options, body: options.body === undefined ? undefined : JSON.stringify(options.body), headers, signal: controller.signal })
      const contentType = response.headers.get('content-type') ?? ''
      const payload: unknown = response.status === 204 ? undefined : contentType.includes('application/json') ? await response.json() : await response.text()
      if (!response.ok) throw new ApiClientError(`API request failed with status ${response.status}.`, response.status, payload)
      return payload as TResponse
    } catch (error) {
      if (error instanceof ApiClientError) throw error
      if (error instanceof DOMException && error.name === 'AbortError') throw new ApiClientError('The API request timed out.', 408)
      throw new ApiClientError(error instanceof Error ? error.message : 'The API request failed.', 0)
    } finally {
      window.clearTimeout(timeout)
    }
  }

  get<TResponse>(path: string, options?: Omit<ApiRequestOptions, 'method' | 'body'>) { return this.request<TResponse>(path, { ...options, method: 'GET' }) }
  post<TRequest, TResponse>(path: string, body: TRequest, options?: Omit<ApiRequestOptions, 'method' | 'body'>) { return this.request<TResponse>(path, { ...options, method: 'POST', body }) }
  put<TRequest, TResponse>(path: string, body: TRequest, options?: Omit<ApiRequestOptions, 'method' | 'body'>) { return this.request<TResponse>(path, { ...options, method: 'PUT', body }) }
  delete<TResponse>(path: string, options?: Omit<ApiRequestOptions, 'method' | 'body'>) { return this.request<TResponse>(path, { ...options, method: 'DELETE' }) }
}

export const apiClient = new ApiClient()

export function unwrapApiResponse<T>(response: ApiEnvelope<T>): T {
  if (response.error || response.data === null) {
    throw new ApiClientError(response.error?.message ?? 'The API returned no data.', 500, response.error)
  }
  return response.data
}
