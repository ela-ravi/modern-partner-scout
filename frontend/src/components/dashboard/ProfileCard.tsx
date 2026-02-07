import React from 'react';
import type { CompleteProfile } from '../../types';
import { Mail, ExternalLink } from 'lucide-react';
import { cn } from '../../lib/utils';
// import { Button } from '../ui/Button';

interface ProfileCardProps {
    profile: CompleteProfile;
    onClick?: () => void;
}

export const ProfileCard: React.FC<ProfileCardProps> = ({ profile, onClick }) => {
    const score = profile.score ? Math.round(profile.score) : 0;

    // Determine gradient based on aesthetics or random (placeholder logic)
    // In real app, maybe analyze image dominant color?
    // Using random-ish deterministic assignment based on username length
    const gradients = [
        "from-rose-100 to-orange-100",
        "from-purple-100 to-blue-100",
        "from-emerald-100 to-teal-100",
        "from-amber-100 to-red-100",
        "from-cyan-100 to-blue-100",
        "from-pink-100 to-violet-100"
    ];
    const gradient = gradients[profile.username.length % gradients.length];

    // Score ring color
    const scoreColor = score >= 80 ? 'text-[#34c759]' : score >= 50 ? 'text-[#ff9500]' : 'text-[#ff3b30]';

    return (
        <div
            onClick={onClick}
            className="group bg-white rounded-[18px] border border-[rgba(0,0,0,0.04)] shadow-[0_2px_12px_rgba(0,0,0,0.04)] overflow-hidden transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_12px_40px_rgba(0,0,0,0.08)] cursor-pointer"
        >
            {/* Header/Cover */}
            <div className={cn("relative h-32 bg-gradient-to-br overflow-hidden", gradient)}>
                {/* Placeholder for cover image if we had one, or just gradient */}
                {/* <img src="..." className="w-full h-full object-cover opacity-80" /> */}

                <div className="absolute top-3 right-3 flex gap-2">
                    {profile.email && (
                        <span className="inline-flex items-center px-2 py-1 bg-[#0071e3]/90 text-white text-[10px] font-bold tracking-wider rounded-full uppercase shadow-sm">
                            EMAIL
                        </span>
                    )}
                    {score >= 90 && (
                        <span className="inline-flex items-center px-2 py-1 bg-[#ff9500]/90 text-white text-[10px] font-bold tracking-wider rounded-full uppercase shadow-sm">
                            ★ TOP
                        </span>
                    )}
                </div>

                {/* Bottom Fade */}
                <div className="absolute bottom-0 left-0 right-0 px-5 pb-3 pt-8 bg-gradient-to-t from-white via-white/95 to-transparent">
                    <div className="flex items-end gap-3">
                        <img
                            src={profile.profile_picture_url || `https://ui-avatars.com/api/?name=${profile.username}&background=random`}
                            alt={profile.username}
                            className="w-14 h-14 rounded-xl border-4 border-white object-cover shadow-lg -mb-6 bg-gray-100"
                            onError={(e) => {
                                (e.target as HTMLImageElement).src = `https://ui-avatars.com/api/?name=${profile.username}&background=random`;
                            }}
                        />
                        <div className="flex-1 min-w-0">
                            <h3 className="font-semibold text-base text-[#1d1d1f] truncate">{profile.full_name || profile.username}</h3>
                            <p className="text-[#86868b] text-sm truncate">@{profile.username}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Body */}
            <div className="relative px-5 pt-8 pb-5 bg-white">
                <p className="text-[#86868b] text-sm mb-4 line-clamp-2 h-10">
                    {profile.bio || "No bio available."}
                </p>

                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-4">
                        <div>
                            <p className="font-semibold text-sm text-[#1d1d1f]">{formatNumber(profile.followers)}</p>
                            <p className="text-[#aeaeb2] text-xs">Followers</p>
                        </div>
                        <div>
                            <p className="font-semibold text-sm text-[#1d1d1f]">
                                {profile.engagement_rate ? `${profile.engagement_rate.toFixed(1)}%` : '-'}
                            </p>
                            <p className="text-[#aeaeb2] text-xs">Engage</p>
                        </div>
                    </div>

                    {/* Score Ring */}
                    <div className="relative w-12 h-12 flex items-center justify-center">
                        <svg className="w-full h-full transform -rotate-90">
                            <circle
                                cx="24" cy="24" r="20"
                                stroke="#f5f5f7" strokeWidth="3" fill="none"
                            />
                            <circle
                                cx="24" cy="24" r="20"
                                stroke="currentColor" strokeWidth="3" fill="none"
                                strokeDasharray={2 * Math.PI * 20}
                                strokeDashoffset={2 * Math.PI * 20 * (1 - score / 100)}
                                className={cn("transition-all duration-1000 ease-out", scoreColor)}
                            />
                        </svg>
                        <span className={cn("absolute font-semibold text-sm", scoreColor)}>{score}</span>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                    <button className="flex-1 py-2.5 bg-[#0071e3] text-white font-medium rounded-xl text-sm hover:bg-[#0077ed] transition-colors shadow-sm shadow-blue-200">
                        View Profile
                    </button>
                    <button className="p-2.5 bg-[#f5f5f7] rounded-xl hover:bg-[#e5e5e5] transition-colors text-[#86868b] group/btn">
                        <Mail className="w-5 h-5 group-hover/btn:text-[#1d1d1f]" />
                    </button>
                    <a
                        href={`https://instagram.com/${profile.username}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2.5 bg-[#f5f5f7] rounded-xl hover:bg-[#e5e5e5] transition-colors text-[#86868b] group/btn flex items-center justify-center"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <ExternalLink className="w-5 h-5 group-hover/btn:text-[#1d1d1f]" />
                    </a>
                </div>
            </div>
        </div>
    );
};

function formatNumber(num: number): string {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}
