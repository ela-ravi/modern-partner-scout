import React, { useState } from 'react';
import { Dialog, DialogContent } from '../ui/Modal';
import type { CompleteProfile } from '../../types';
import { Button } from '../ui/Button';
import { Mail, ExternalLink } from 'lucide-react';
import { cn } from '../../lib/utils';
import { EmailComposer } from './EmailComposer';

interface ProfileDetailModalProps {
    profile: CompleteProfile | null;
    isOpen: boolean;
    onClose: () => void;
}

export const ProfileDetailModal: React.FC<ProfileDetailModalProps> = ({ profile, isOpen, onClose }) => {
    const [isEmailOpen, setIsEmailOpen] = useState(false);

    if (!profile) return null;

    const score = profile.score ? Math.round(profile.score) : 0;
    const scoreColor = score >= 80 ? 'text-[#34c759]' : score >= 50 ? 'text-[#ff9500]' : 'text-[#ff3b30]';

    return (
        <>
            <Dialog open={isOpen} onOpenChange={onClose}>
                <DialogContent className="max-w-4xl p-0 overflow-hidden bg-[#fbfbfd] border-none shadow-2xl">
                    <div className="flex flex-col md:flex-row h-[80vh] md:h-[600px]">
                        {/* Sidebar / Header Info */}
                        <div className="md:w-1/3 bg-white border-r border-[rgba(0,0,0,0.06)] flex flex-col">
                            <div className="p-8 flex-1 overflow-y-auto">
                                <div className="flex flex-col items-center text-center mb-6">
                                    <div className="relative mb-4">
                                        <img
                                            src={profile.profile_picture_url || `https://ui-avatars.com/api/?name=${profile.username}&background=random`}
                                            alt={profile.username}
                                            className="w-24 h-24 rounded-full border-4 border-white shadow-lg"
                                        />
                                        <div className="absolute -bottom-2 -right-2 bg-white rounded-full p-1.5 shadow-sm">
                                            {/* Circular Score */}
                                            <div className="relative w-10 h-10 flex items-center justify-center bg-gray-50 rounded-full">
                                                <span className={cn("font-bold text-sm", scoreColor)}>{score}</span>
                                            </div>
                                        </div>
                                    </div>
                                    <h2 className="text-xl font-bold text-[#1d1d1f] mb-1">{profile.full_name || profile.username}</h2>
                                    <a href={`https://instagram.com/${profile.username}`} target="_blank" rel="noreferrer" className="text-[#0071e3] text-sm hover:underline flex items-center gap-1">
                                        @{profile.username} <ExternalLink className="w-3 h-3" />
                                    </a>
                                    <p className="text-[#86868b] text-sm mt-4 line-clamp-4">{profile.bio}</p>
                                </div>

                                <div className="grid grid-cols-2 gap-4 mb-6">
                                    <div className="bg-[#f5f5f7] rounded-xl p-3 text-center">
                                        <p className="text-[#1d1d1f] font-semibold">{formatNumber(profile.followers_count)}</p>
                                        <p className="text-[#86868b] text-xs">Followers</p>
                                    </div>
                                    <div className="bg-[#f5f5f7] rounded-xl p-3 text-center">
                                        <p className="text-[#1d1d1f] font-semibold">{profile.engagement_rate?.toFixed(2)}%</p>
                                        <p className="text-[#86868b] text-xs">Engagement</p>
                                    </div>
                                    <div className="bg-[#f5f5f7] rounded-xl p-3 text-center">
                                        <p className="text-[#1d1d1f] font-semibold">{profile.posts_count || 0}</p>
                                        <p className="text-[#86868b] text-xs">Posts</p>
                                    </div>
                                    <div className="bg-[#f5f5f7] rounded-xl p-3 text-center">
                                        <p className="text-[#1d1d1f] font-semibold">{profile.is_verified ? 'Yes' : 'No'}</p>
                                        <p className="text-[#86868b] text-xs">Verified</p>
                                    </div>
                                </div>

                                {profile.email && (
                                    <div className="bg-blue-50 border border-blue-100 rounded-xl p-3 mb-4 flex items-center gap-3">
                                        <div className="p-2 bg-blue-100 rounded-lg text-blue-600">
                                            <Mail className="w-4 h-4" />
                                        </div>
                                        <div className="overflow-hidden">
                                            <p className="text-xs text-blue-600 font-medium uppercase">Email Discovered</p>
                                            <p className="text-sm text-[#1d1d1f] truncate" title={profile.email}>{profile.email}</p>
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="p-4 border-t border-[rgba(0,0,0,0.06)] bg-gray-50/50">
                                <Button className="w-full mb-2" onClick={() => setIsEmailOpen(true)} disabled={!profile.email}>
                                    <Mail className="w-4 h-4 mr-2" />
                                    Draft Email
                                </Button>
                            </div>
                        </div>

                        {/* Main Content */}
                        <div className="flex-1 flex flex-col h-full bg-[#fbfbfd]">
                            <div className="p-6 border-b border-[rgba(0,0,0,0.06)] bg-white">
                                <h3 className="text-lg font-semibold text-[#1d1d1f]">AI Analysis</h3>
                            </div>
                            <div className="p-8 overflow-y-auto">
                                <div className="space-y-8">
                                    {/* Score Breakdown */}
                                    <section>
                                        <h4 className="text-sm font-semibold text-[#86868b] uppercase tracking-wider mb-4">Score Breakdown</h4>
                                        <div className="space-y-4">
                                            <ScoreRow label="Visual Aesthetic" value={profile.visual_aesthetic_match || 0} />
                                            <ScoreRow label="Content Alignment" value={profile.content_theme_alignment || 0} />
                                            <ScoreRow label="Engagement Quality" value={profile.engagement_rate_score || 0} />
                                            <ScoreRow label="Follower Quality" value={profile.follower_quality || 0} />
                                            <ScoreRow label="Business Indicators" value={profile.business_indicators || 0} />
                                            <ScoreRow label="Activity Recency" value={profile.activity_recency || 0} />
                                        </div>
                                    </section>

                                    {/* Reasoning */}
                                    <section className="bg-white rounded-2xl p-6 border border-[rgba(0,0,0,0.06)] shadow-sm">
                                        <h4 className="flex items-center gap-2 text-sm font-semibold text-[#1d1d1f] mb-3">
                                            <span className="w-2 h-2 rounded-full bg-purple-500"></span>
                                            Why this partner?
                                        </h4>
                                        <p className="text-[#1d1d1f] text-sm leading-relaxed whitespace-pre-line">
                                            {profile.reasoning?.summary || profile.reasoning?.text || "No AI reasoning available for this profile yet."}
                                        </p>
                                    </section>

                                    {/* Recent Posts */}
                                    {profile.recent_posts && profile.recent_posts.length > 0 && (
                                        <section>
                                            <h4 className="text-sm font-semibold text-[#86868b] uppercase tracking-wider mb-4">Recent Content</h4>
                                            <div className="flex gap-3 overflow-x-auto pb-4 scrollbar-hide">
                                                {profile.recent_posts.map((post, i) => (
                                                    <div key={i} className="flex-shrink-0 w-32 group/post">
                                                        <div className="aspect-square rounded-xl overflow-hidden bg-gray-100 border border-[rgba(0,0,0,0.04)] shadow-sm">
                                                            <img
                                                                src={post.image_url}
                                                                className="w-full h-full object-cover transition-transform duration-300 group-hover/post:scale-110"
                                                                alt=""
                                                                onError={(e) => {
                                                                    (e.target as HTMLImageElement).src = 'https://via.placeholder.com/150?text=No+Image';
                                                                }}
                                                            />
                                                        </div>
                                                        {post.likes !== undefined && (
                                                            <p className="text-[10px] text-[#86868b] mt-1.5 flex items-center gap-1">
                                                                <span className="font-semibold text-[#1d1d1f]">{post.likes.toLocaleString()}</span> likes
                                                            </p>
                                                        )}
                                                    </div>
                                                ))}
                                            </div>
                                        </section>
                                    )}

                                    {/* Keywords/Themes */}
                                    {profile.reasoning?.keywords && profile.reasoning.keywords.length > 0 && (
                                        <section>
                                            <h4 className="text-sm font-semibold text-[#86868b] uppercase tracking-wider mb-3">Detected Themes</h4>
                                            <div className="flex flex-wrap gap-2">
                                                {profile.reasoning.keywords.map((k: string, i: number) => (
                                                    <span key={i} className="px-3 py-1 bg-white border border-gray-200 rounded-full text-xs font-medium text-gray-600">{k}</span>
                                                ))}
                                            </div>
                                        </section>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </DialogContent>
            </Dialog>

            <EmailComposer
                isOpen={isEmailOpen}
                onClose={() => setIsEmailOpen(false)}
                profile={profile}
            />
        </>
    );
};

const ScoreRow: React.FC<{ label: string; value: number }> = ({ label, value }) => (
    <div className="flex items-center gap-4">
        <span className="text-sm text-[#1d1d1f] w-40 truncate">{label}</span>
        <div className="flex-1 h-2 bg-[#f5f5f7] rounded-full overflow-hidden">
            <div
                className={cn("h-full rounded-full transition-all duration-1000",
                    value >= 80 ? "bg-[#34c759]" : value >= 50 ? "bg-[#ff9500]" : "bg-[#ff3b30]"
                )}
                style={{ width: `${value}%` }}
            ></div>
        </div>
        <span className="text-sm font-medium text-[#1d1d1f] w-8 text-right">{Math.round(value)}</span>
    </div>
);

function formatNumber(num: number): string {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}
