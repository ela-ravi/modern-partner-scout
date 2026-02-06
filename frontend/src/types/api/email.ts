/**
 * Email API Types
 */

export interface EmailTone {
  id: string
  name: string
  description: string
}

export interface GenerateEmailRequest {
  profile_id: string
  job_id: string
  tone?: string
  custom_message?: string
}

export interface GenerateEmailResponse {
  subject: string
  body: string
  recipient_email: string
  recipient_name: string
  tone_used: string
}

export interface SendEmailRequest {
  profile_id: string
  job_id: string
  subject: string
  body: string
  recipient_email: string
}

export interface SendEmailResponse {
  success: boolean
  message_id?: string
  error?: string
}

export interface EmailComposerData {
  profileId: string
  jobId: string
  recipientName: string
  recipientEmail: string
  recipientHandle: string
  profileImageUrl?: string
}
