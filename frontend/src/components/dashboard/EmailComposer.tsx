import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent } from '../ui/Modal';
import type { CompleteProfile } from '../../types';
import { Button } from '../ui/Button';
import { Textarea } from '../ui/Textarea';
import { useToast } from '../../hooks/useToast';
import { api } from '../../lib/api';
import { Send, Sparkles, Copy } from 'lucide-react';

interface EmailComposerProps {
    profile: CompleteProfile;
    isOpen: boolean;
    onClose: () => void;
}

export const EmailComposer: React.FC<EmailComposerProps> = ({ profile, isOpen, onClose }) => {
    const { toast } = useToast();
    const [emailBody, setEmailBody] = useState('');
    const [subject, setSubject] = useState('');
    const [loading, setLoading] = useState(false);
    const [generating, setGenerating] = useState(false);

    // Generate email when opened if empty
    useEffect(() => {
        if (isOpen && !emailBody) {
            generateEmail();
        }
    }, [isOpen]);

    const generateEmail = async () => {
        if (generating) return;
        try {
            setGenerating(true);
            const response = await api.post<{ subject: string; body: string }>('/email/generate', {
                profile_id: profile.id,
                tone: 'professional_friendly'
            });
            setSubject(response.subject);
            setEmailBody(response.body);
        } catch (error) {
            console.error('Failed to generate email:', error);
            toast({
                title: "Generation Failed",
                description: "Could not generate AI email draft.",
                variant: "destructive"
            });
            // Fallback
            setSubject(`Partnership Opportunity: ${profile.username} x PartnerScout`);
            setEmailBody(`Hi ${profile.full_name || profile.username},\n\nI came across your profile and loved your content...`);
        } finally {
            setGenerating(false);
        }
    };

    const handleSend = async () => {
        // Mock send for now as strict sending might require backend config
        // Actually hitting the 'send' endpoint implemented in backend
        try {
            setLoading(true);
            await api.post('/email/send', {
                profile_id: profile.id,
                subject,
                body: emailBody,
                to_email: profile.email
            });

            toast({
                title: "Email Sent",
                description: `Outreach email sent to ${profile.email}`,
            });
            onClose();
        } catch (error) {
            console.error('Failed to send email:', error);
            toast({
                title: "Send Failed",
                description: "Could not send email. Please check your configuration.",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(`Subject: ${subject}\n\n${emailBody}`);
        toast({ title: "Copied to clipboard" });
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="max-w-2xl bg-white p-0 overflow-hidden shadow-2xl rounded-2xl">
                <div className="flex flex-col h-[600px]">
                    {/* Header */}
                    <div className="bg-[#fbfbfd] border-b border-[rgba(0,0,0,0.06)] p-4 flex items-center justify-between">
                        <h3 className="font-semibold text-[#1d1d1f] flex items-center gap-2">
                            <Sparkles className="w-4 h-4 text-purple-500" />
                            Compose Outreach
                        </h3>
                    </div>

                    {/* Body */}
                    <div className="flex-1 p-6 flex flex-col gap-4 overflow-y-auto">
                        <div className="flex items-center gap-2 text-sm">
                            <span className="text-[#86868b] w-12">To:</span>
                            <span className="font-medium text-[#1d1d1f] bg-[#f5f5f7] px-2 py-1 rounded">{profile.email}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm border-b border-gray-100 pb-2">
                            <span className="text-[#86868b] w-12">Subject:</span>
                            <input
                                className="flex-1 outline-none font-medium text-[#1d1d1f] placeholder:font-normal"
                                value={subject}
                                onChange={(e) => setSubject(e.target.value)}
                                placeholder="Subject line..."
                            />
                        </div>

                        <div className="relative flex-1">
                            {generating ? (
                                <div className="absolute inset-0 flex items-center justify-center bg-white/50 backdrop-blur-sm z-10">
                                    <div className="flex flex-col items-center gap-2">
                                        <Sparkles className="w-8 h-8 text-purple-500 animate-spin-slow" />
                                        <p className="text-sm font-medium text-purple-600">Drafting with AI...</p>
                                    </div>
                                </div>
                            ) : null}
                            <Textarea
                                className="h-full border-none resize-none p-0 focus-visible:ring-0 text-base leading-relaxed"
                                value={emailBody}
                                onChange={(e) => setEmailBody(e.target.value)}
                                placeholder="Start typing..."
                            />
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="bg-[#fbfbfd] border-t border-[rgba(0,0,0,0.06)] p-4 flex justify-between items-center">
                        <Button variant="ghost" size="sm" onClick={generateEmail} disabled={generating}>
                            <Sparkles className="w-4 h-4 mr-2" />
                            Regenerate
                        </Button>

                        <div className="flex gap-2">
                            <Button variant="outline" size="sm" onClick={copyToClipboard}>
                                <Copy className="w-4 h-4 mr-2" />
                                Copy
                            </Button>
                            <Button variant="pill" size="sm" onClick={handleSend} disabled={loading || generating || !profile.email}>
                                {loading ? 'Sending...' : 'Send Email'}
                                {!loading && <Send className="w-4 h-4 ml-2" />}
                            </Button>
                        </div>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
};
