import React from 'react';
import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import type { DiscoveryJob, JobStatus } from '../../types';
import { Megaphone, Compass, CheckCircle, AlertCircle, Clock, MoreHorizontal } from 'lucide-react';
import { cn } from '../../lib/utils';

interface SessionCardProps {
    job: DiscoveryJob;
}

const statusConfig: Record<JobStatus, { color: string; bg: string; icon: React.ReactNode; label: string }> = {
    pending: { color: 'text-[#86868b]', bg: 'bg-[#f5f5f7]', icon: <Clock className="w-6 h-6" />, label: 'PENDING' },
    analyzing: { color: 'text-[#af52de]', bg: 'bg-[#af52de]/10', icon: <Compass className="w-6 h-6 spin-slow" />, label: 'ANALYZING' },
    discovering: { color: 'text-[#0071e3]', bg: 'bg-[#0071e3]/10', icon: <Compass className="w-6 h-6" />, label: 'DISCOVERING' },
    scoring: { color: 'text-[#ff9500]', bg: 'bg-[#ff9500]/10', icon: <Megaphone className="w-6 h-6" />, label: 'SCORING' },
    completed: { color: 'text-[#34c759]', bg: 'bg-[#34c759]/10', icon: <CheckCircle className="w-6 h-6" />, label: 'COMPLETED' },
    failed: { color: 'text-[#ff3b30]', bg: 'bg-[#ff3b30]/10', icon: <AlertCircle className="w-6 h-6" />, label: 'FAILED' },
};

export const SessionCard: React.FC<SessionCardProps> = ({ job }) => {
    const status = statusConfig[job.status] || statusConfig.pending;
    const progress = job.discovery_limit ? Math.round((job.profiles_discovered / job.discovery_limit) * 100) : 0;

    return (
        <div className="bg-white rounded-[16px] border border-[rgba(0,0,0,0.04)] p-6 transition-all duration-300 hover:border-[#0071e3]/20 hover:shadow-[0_8px_30px_rgba(0,0,0,0.06)] hover:-translate-y-[2px]">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div className="flex items-start gap-4">
                    {/* Icon */}
                    <div className={cn("w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors", status.bg)}>
                        <div className={status.color}>{status.icon}</div>
                    </div>

                    {/* Content */}
                    <div>
                        <div className="flex items-center gap-3 mb-1">
                            <h3 className="font-semibold text-lg text-[#1d1d1f]">{job.name}</h3>
                            <span className={cn("text-[11px] font-semibold tracking-wider px-2.5 py-1 rounded-full uppercase", status.bg, status.color)}>
                                {status.label}
                            </span>
                        </div>
                        <p className="text-[#86868b] text-sm mb-2">
                            Created {formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
                        </p>

                        {/* Stats */}
                        <div className="flex flex-wrap gap-4 text-sm mt-3">
                            <span className="text-[#86868b]">
                                <span className="font-medium text-[#1d1d1f]">{job.profiles_discovered}</span> profiles discovered
                            </span>
                            <span className="text-[#86868b]">
                                <span className="font-medium text-[#1d1d1f]">{job.profiles_scored}</span> scored
                            </span>
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-3 self-end lg:self-center">
                    <Link to={`/dashboard/${job.id}`}>
                        <button className="px-4 py-2 bg-[#f5f5f7] hover:bg-[#e5e5e5] rounded-xl text-sm font-medium transition-colors text-[#1d1d1f]">
                            {job.status === 'completed' ? 'View Results' : 'View Progress'}
                        </button>
                    </Link>
                    <button className="p-2 bg-[#f5f5f7] hover:bg-[#e5e5e5] rounded-xl transition-colors text-[#86868b]">
                        <MoreHorizontal className="w-5 h-5" />
                    </button>
                </div>
            </div>

            {/* Progress Bar (if active) */}
            {(job.status === 'discovering' || job.status === 'scoring' || job.status === 'analyzing') && (
                <div className="mt-4 pt-4 border-t border-[rgba(0,0,0,0.06)]">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-[#86868b]">Progress</span>
                        <span className="text-sm font-medium text-[#1d1d1f]">{progress}%</span>
                    </div>
                    <div className="h-1.5 bg-[#f5f5f7] rounded-full overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-[#0071e3] to-cyan-400 rounded-full transition-all duration-500"
                            style={{ width: `${progress}%` }}
                        ></div>
                    </div>
                </div>
            )}
        </div>
    );
};
