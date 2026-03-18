/**
 * Hook for generating AI-powered emails
 */

import { useMutation } from '@tanstack/react-query'
import { emailService } from '@/services/email'
import type { GenerateEmailRequest, GenerateEmailResponse } from '@/types/api/email'

export function useGenerateEmail() {
  return useMutation<GenerateEmailResponse, Error, GenerateEmailRequest>({
    mutationFn: (data) => emailService.generate(data),
  })
}
