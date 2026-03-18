/**
 * Typed API Client
 * Handles authentication, error handling, and request/response transformation
 */

import { ApiError } from './errors'
import { supabase } from '@/lib/supabase/client'

interface RequestConfig extends Omit<RequestInit, 'body'> {
  params?: Record<string, string | number | boolean | undefined>
  body?: unknown
}

interface ApiErrorResponse {
  error?: {
    code?: string
    message?: string
  }
  message?: string
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async getAuthToken(): Promise<string | null> {
    const {
      data: { session },
    } = await supabase.auth.getSession()
    return session?.access_token ?? null
  }

  private buildUrl(endpoint: string, params?: RequestConfig['params']): string {
    const url = new URL(`${this.baseUrl}${endpoint}`)

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          url.searchParams.set(key, String(value))
        }
      })
    }

    return url.toString()
  }

  async request<T>(endpoint: string, config: RequestConfig = {}): Promise<T> {
    const { params, body, headers: customHeaders, ...init } = config

    const url = this.buildUrl(endpoint, params)
    const token = await this.getAuthToken()

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...customHeaders,
    }

    try {
      const response = await fetch(url, {
        ...init,
        headers,
        body: body ? JSON.stringify(body) : undefined,
      })

      if (!response.ok) {
        const errorData: ApiErrorResponse = await response.json().catch(() => ({}))
        const message =
          errorData.error?.message ||
          errorData.message ||
          `Request failed with status ${response.status}`
        throw new ApiError(response.status, message, errorData.error?.code)
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return {} as T
      }

      return response.json()
    } catch (error) {
      if (error instanceof ApiError) {
        throw error
      }

      // Network error
      throw new ApiError(0, error instanceof Error ? error.message : 'Network error')
    }
  }

  get<T>(endpoint: string, params?: RequestConfig['params']): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET', params })
  }

  post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, { method: 'POST', body: data })
  }

  put<T>(endpoint: string, data: unknown): Promise<T> {
    return this.request<T>(endpoint, { method: 'PUT', body: data })
  }

  patch<T>(endpoint: string, data: unknown): Promise<T> {
    return this.request<T>(endpoint, { method: 'PATCH', body: data })
  }

  delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }
}

// Export singleton instance
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api'
export const api = new ApiClient(API_URL)
