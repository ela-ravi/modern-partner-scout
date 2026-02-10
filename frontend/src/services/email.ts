/**
 * Email Service
 * Handles email generation and sending via the backend API
 */

import { api } from '@/lib/api/client'
import type {
  EmailTone,
  GenerateEmailRequest,
  GenerateEmailResponse,
  SendEmailRequest,
  SendEmailResponse,
} from '@/types/api/email'

export const emailService = {
  /**
   * Get available email tones
   */
  getTones: async (): Promise<EmailTone[]> => {
    const response = await api.get<{ tones: Array<{ value: string; label: string; description: string }> }>('/email/tones')
    const tones = Array.isArray(response) ? response : response.tones
    return tones.map((t) => ({
      id: t.value ?? (t as unknown as EmailTone).id,
      name: t.label ?? (t as unknown as EmailTone).name,
      description: t.description,
    }))
  },

  /**
   * Generate an AI-powered email for a profile
   */
  generate: async (data: GenerateEmailRequest): Promise<GenerateEmailResponse> => {
    const response = await api.post<{ email: { subject: string; body: string }; profile_name: string; profile_username: string } | GenerateEmailResponse>('/email/generate', data)
    // Backend wraps subject/body inside an "email" key
    if ('email' in response && response.email) {
      return {
        subject: response.email.subject,
        body: response.email.body,
        recipient_email: '',
        recipient_name: response.profile_name || '',
        tone_used: data.tone || 'professional',
      }
    }
    return response as GenerateEmailResponse
  },

  /**
   * Send an email to a profile
   */
  send: async (data: SendEmailRequest): Promise<SendEmailResponse> => {
    return api.post<SendEmailResponse>('/email/send', data)
  },
}
