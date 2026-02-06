/**
 * Hook for sending emails
 */

import { useMutation, useQueryClient } from '@tanstack/react-query'
import { emailService } from '@/services/email'
import type { SendEmailRequest, SendEmailResponse } from '@/types/api/email'

export function useSendEmail() {
  const queryClient = useQueryClient()

  return useMutation<SendEmailResponse, Error, SendEmailRequest>({
    mutationFn: (data) => emailService.send(data),
    onSuccess: (_data, variables) => {
      // Invalidate profile queries to refresh email status
      queryClient.invalidateQueries({
        queryKey: ['profiles', variables.profile_id],
      })
    },
  })
}
