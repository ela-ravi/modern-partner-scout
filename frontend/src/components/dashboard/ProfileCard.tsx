import React from 'react';
import type { CompleteProfile } from '../../types';
import { Mail, ExternalLink, Instagram } from 'lucide-react';
import { cn } from '../../lib/utils';
import { ScoreRing } from '../ui/ScoreRing';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';

interface ProfileCardProps {
    profile: CompleteProfile;
    onClick?: () => void;
}

export const ProfileCard: React.FC<ProfileCardProps> = ({ profile, onClick }) => {
    const score = profile.score ? Math.round(profile.score) : 0;

    // Determine gradient based on username length
    const gradients = [
        "from-rose-100 to-orange-100",
        "from-purple-100 to-blue-100",
        "from-emerald-100 to-teal-100",
        "from-amber-100 to-red-100",
        "from-cyan-100 to-blue-100",
        "from-pink-100 to-violet-100"
    ];
    const gradient = gradients[profile.username.length % gradients.length];

    return (
        <div
            onClick={onClick}
            className="group bg-white rounded-3xl border border-gray-100 shadow-soft overflow-hidden transition-all duration-500 hover:-translate-y-2 hover:shadow-strong cursor-pointer"
        >
            {/* Header/Cover */}
            <div className={cn("relative h-32 bg-gradient-to-br overflow-hidden", gradient)}>
                {profile.cover_image_url && (
                    <img
                        src={profile.cover_image_url}
                        className="w-full h-full object-cover opacity-60 mix-blend-overlay transition-transform duration-700 group-hover:scale-110"
                        alt=""
                    />
                )}

                <div className="absolute top-4 right-4 flex gap-2">
                    {profile.email && (
                        <Badge variant="info" className="shadow-sm">EMAIL</Badge>
                    )}
                    {score >= 90 && (
                        <Badge variant="warning" className="shadow-sm">★ TOP</Badge>
                    )}
                </div>

                {/* Bottom Fade */}
                <div className="absolute bottom-0 left-0 right-0 px-6 pb-4 pt-10 bg-gradient-to-t from-white via-white/80 to-transparent">
                    <div className="flex items-end gap-3">
                        <div className="relative">
                            <img
                                src={profile.profile_picture_url || `https://ui-avatars.com/api/?name=${profile.username}&background=random`}
                                alt={profile.username}
                                className="w-16 h-16 rounded-2xl border-4 border-white object-cover shadow-strong -mb-8 bg-gray-100"
                                onError={(e) => {
                                    (e.target as HTMLImageElement).src = `https://ui-avatars.com/api/?name=${profile.username}&background=random`;
                                }}
                            />
                        </div>
                        <div className="flex-1 min-w-0 pb-1">
                            <h3 className="font-bold text-lg text-brand-text truncate leading-tight">{profile.full_name || profile.username}</h3>
                            <p className="text-brand-secondary text-sm font-medium truncate">@{profile.username}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Body */}
            <div className="relative px-6 pt-10 pb-6 bg-white">
                <p className="text-brand-secondary text-sm mb-6 line-clamp-2 h-10 font-medium leading-relaxed">
                    {profile.bio || "No bio available for this creator."}
                </p>

                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-6">
                        <div>
                            <p className="font-bold text-base text-brand-text leading-none mb-1">{formatNumber(profile.followers_count)}</p>
                            <p className="text-[10px] font-bold text-brand-secondary uppercase tracking-widest">Followers</p>
                        </div>
                        <div>
                            <p className="font-bold text-base text-brand-text leading-none mb-1">
                                {profile.engagement_rate ? `${profile.engagement_rate.toFixed(1)}%` : '-'}
                            </p>
                            <p className="text-[10px] font-bold text-brand-secondary uppercase tracking-widest">Engage</p>
                        </div>
                    </div>

                    {/* Score Ring */}
                    <ScoreRing score={score} size={48} />
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                    <Button className="flex-1 h-11 rounded-xl font-bold">
                        View Profile
                    </Button>
                    <Button variant="secondary" size="icon" className="w-11 h-11 rounded-xl group/btn">
                        <Mail className="w-5 h-5" />
                    </Button>
                    <a
                        href={`https://instagram.com/${profile.username}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="w-11 h-11 bg-gray-100 rounded-xl hover:bg-gray-200 transition-all flex items-center justify-center text-brand-secondary group/insta"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <Instagram className="w-5 h-5 group-hover/insta:text-brand-text" />
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
