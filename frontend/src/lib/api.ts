import { supabase } from './supabase';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api';

interface RequestOptions extends RequestInit {
    token?: string;
}

export const api = {
    async get<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
        return this.request<T>(endpoint, { ...options, method: 'GET' });
    },

    async post<T>(endpoint: string, body: any, options: RequestOptions = {}): Promise<T> {
        return this.request<T>(endpoint, { ...options, method: 'POST', body: JSON.stringify(body) });
    },

    async put<T>(endpoint: string, body: any, options: RequestOptions = {}): Promise<T> {
        return this.request<T>(endpoint, { ...options, method: 'PUT', body: JSON.stringify(body) });
    },

    async delete<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
        return this.request<T>(endpoint, { ...options, method: 'DELETE' });
    },

    async patch<T>(endpoint: string, body: any, options: RequestOptions = {}): Promise<T> {
        return this.request<T>(endpoint, { ...options, method: 'PATCH', body: JSON.stringify(body) });
    },

    async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
        const { token: providedToken, ...fetchOptions } = options;
        const headers = new Headers(options.headers);
        headers.set('Content-Type', 'application/json');

        // Always get the latest session to ensure token is fresh
        const { data: { session } } = await supabase.auth.getSession();
        const token = providedToken || session?.access_token;

        if (token) {
            headers.set('Authorization', `Bearer ${token}`);
        } else {
            console.warn('API Request warning: No authenticated session found for', endpoint);
        }

        // Debug logging
        console.log('[API Debug]', endpoint, 'Token:', token ? token.substring(0, 30) + '...' : 'NO TOKEN');

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...fetchOptions,
            headers,
        });

        if (!response.ok) {
            let errorMessage = 'An error occurred';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail?.message || errorData.message || errorMessage;
            } catch (e) {
                errorMessage = `HTTP Error ${response.status}: ${response.statusText}`;
            }
            throw new Error(errorMessage);
        }

        // Handle 204 No Content
        if (response.status === 204) {
            return {} as T;
        }

        return response.json();
    }
};
