/**
 * EmailComposer Modal Component
 * AI-powered email composition for partner outreach
 */

import { useState, useId, useRef, useEffect } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import CloseIcon from '@mui/icons-material/Close'
import MailIcon from '@mui/icons-material/Mail'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import SendIcon from '@mui/icons-material/Send'
import { clsx } from 'clsx'

import { Avatar } from '@/components/ui/Avatar'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { Textarea } from '@/components/ui/Textarea'
import { Spinner } from '@/components/ui/Spinner'
import { useEmailTones, useGenerateEmail, useSendEmail } from '@/hooks/email'
import type { EmailComposerData } from '@/types/api/email'

interface EmailComposerProps {
  isOpen: boolean
  onClose: () => void
  profile: EmailComposerData
  onSent?: () => void
}

export function EmailComposer({
  isOpen,
  onClose,
  profile,
  onSent,
}: EmailComposerProps) {
  const titleId = useId()
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [selectedTone, setSelectedTone] = useState('professional')

  const hasGenerated = useRef(false)

  const { data: tones = [], isLoading: tonesLoading } = useEmailTones()
  const generateEmail = useGenerateEmail()
  const sendEmail = useSendEmail()

  // Auto-regenerate when tone changes (only after first generation)
  useEffect(() => {
    if (hasGenerated.current && !generateEmail.isPending) {
      handleGenerate()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTone])

  const handleGenerate = async () => {
    try {
      const result = await generateEmail.mutateAsync({
        profile_id: profile.profileId,
        job_id: profile.jobId,
        tone: selectedTone,
      })
      setSubject(result.subject ?? '')
      setBody(result.body ?? '')
      hasGenerated.current = true
    } catch (error) {
      console.error('Failed to generate email:', error)
    }
  }

  const handleSend = async () => {
    if (!(subject || '').trim() || !(body || '').trim()) return

    try {
      await sendEmail.mutateAsync({
        profile_id: profile.profileId,
        job_id: profile.jobId,
        subject,
        body,
        recipient_email: profile.recipientEmail,
      })
      onSent?.()
      onClose()
    } catch (error) {
      console.error('Failed to send email:', error)
    }
  }

  const handleClose = () => {
    setSubject('')
    setBody('')
    setSelectedTone('professional')
    hasGenerated.current = false
    onClose()
  }

  return (
    <Dialog.Root open={isOpen} onOpenChange={(open) => !open && handleClose()}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 animate-fade-in" />
        <Dialog.Content
          className="fixed left-1/2 top-1/2 z-50 w-full max-w-3xl -translate-x-1/2 -translate-y-1/2 rounded-2xl bg-white shadow-2xl max-h-[90vh] flex flex-col animate-scale-in"
          aria-modal="true"
          aria-labelledby={titleId}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100 flex-shrink-0">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center">
                <MailIcon className="text-blue-600 text-xl" />
              </div>
              <div>
                <Dialog.Title id={titleId} className="font-semibold text-lg">
                  Compose Email
                </Dialog.Title>
                <p className="text-gray-500 text-sm">AI-powered outreach</p>
              </div>
            </div>
            <Dialog.Close asChild>
              <button
                className="w-9 h-9 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center text-gray-500 transition-colors"
                aria-label="Close"
              >
                <CloseIcon className="text-xl" />
              </button>
            </Dialog.Close>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* Recipient */}
            <div>
              <p className="block text-sm font-medium text-gray-500 mb-2">
                To
              </p>
              <div className="flex items-center gap-3 p-3.5 bg-gray-50 rounded-xl">
                <Avatar
                  src={profile.profileImageUrl}
                  alt={profile.recipientName}
                  size="sm"
                  name={profile.recipientName}
                />
                <div className="flex-1">
                  <span className="font-medium">{profile.recipientName}</span>
                  <span className="text-gray-400 mx-2">•</span>
                  <span className="text-gray-500 text-sm">
                    {profile.recipientEmail}
                  </span>
                </div>
              </div>
            </div>

            {/* Tone Selection */}
            <div>
              <p className="block text-sm font-medium text-gray-500 mb-3">
                Tone
              </p>
              <div className="flex flex-wrap gap-2">
                {tonesLoading ? (
                  <Spinner size="sm" />
                ) : (
                  tones.map((tone) => (
                    <button
                      key={tone.id}
                      type="button"
                      onClick={() => setSelectedTone(tone.id)}
                      className={clsx(
                        'px-4 py-2 rounded-full text-sm font-medium transition-all',
                        selectedTone === tone.id
                          ? 'bg-blue-50 text-blue-600 border border-blue-200'
                          : 'bg-gray-100 text-gray-500 border border-transparent hover:bg-gray-200'
                      )}
                    >
                      {tone.name}
                    </button>
                  ))
                )}
              </div>
            </div>

            {/* Subject */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label
                  htmlFor="email-subject"
                  className="text-sm font-medium text-gray-500"
                >
                  Subject
                </label>
                <button
                  type="button"
                  onClick={handleGenerate}
                  disabled={generateEmail.isPending}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-blue-600 text-xs font-medium hover:bg-blue-50 rounded-lg transition-colors disabled:opacity-50"
                >
                  {generateEmail.isPending ? (
                    <Spinner size="xs" />
                  ) : (
                    <AutoAwesomeIcon className="text-sm" />
                  )}
                  {generateEmail.isPending ? 'Generating...' : 'Generate with AI'}
                </button>
              </div>
              <Input
                id="email-subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Enter subject line..."
                aria-label="Subject"
              />
            </div>

            {/* Email Body */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label
                  htmlFor="email-body"
                  className="text-sm font-medium text-gray-500"
                >
                  Message
                </label>
              </div>
              <Textarea
                id="email-body"
                value={body}
                onChange={(e) => setBody(e.target.value)}
                placeholder="Write your message..."
                rows={10}
                className="min-h-[280px] resize-none leading-relaxed"
                aria-label="Message"
              />
            </div>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50/50 flex-shrink-0">
            <Button variant="ghost" onClick={handleClose}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={handleSend}
              disabled={!(subject || '').trim() || !(body || '').trim() || sendEmail.isPending}
              loading={sendEmail.isPending}
              leftIcon={!sendEmail.isPending ? <SendIcon /> : undefined}
            >
              {sendEmail.isPending ? 'Sending...' : 'Send Email'}
            </Button>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
