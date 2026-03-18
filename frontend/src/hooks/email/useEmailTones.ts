/**
 * Hook for fetching available email tones
 */

import { useQuery } from '@tanstack/react-query'
import { emailService } from '@/services/email'
import type { EmailTone } from '@/types/api/email'

export function useEmailTones() {
  return useQuery<EmailTone[], Error>({
    queryKey: ['email', 'tones'],
    queryFn: () => emailService.getTones(),
    staleTime: 1000 * 60 * 60, // 1 hour - tones don't change often
  })
}
