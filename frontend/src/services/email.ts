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
    return api.get<EmailTone[]>('/api/email/tones')
  },

  /**
   * Generate an AI-powered email for a profile
   */
  generate: async (data: GenerateEmailRequest): Promise<GenerateEmailResponse> => {
    return api.post<GenerateEmailResponse>('/api/email/generate', data)
  },

  /**
   * Send an email to a profile
   */
  send: async (data: SendEmailRequest): Promise<SendEmailResponse> => {
    return api.post<SendEmailResponse>('/api/email/send', data)
  },
}
