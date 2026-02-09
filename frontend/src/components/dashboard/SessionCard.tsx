import React from 'react';
import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import type { DiscoveryJob, JobStatus } from '../../types';
import { Megaphone, Compass, CheckCircle, AlertCircle, Clock, MoreHorizontal } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { ProgressBar } from '../ui/ProgressBar';

interface SessionCardProps {
    job: DiscoveryJob;
}

const statusConfig: Record<JobStatus, { variant: "info" | "warning" | "success" | "error" | "default"; icon: React.ReactNode; label: string }> = {
    pending: { variant: 'default', icon: <Clock className="w-5 h-5" />, label: 'PENDING' },
    analyzing: { variant: 'info', icon: <Compass className="w-5 h-5 animate-spin-slow" />, label: 'ANALYZING' },
    discovering: { variant: 'info', icon: <Compass className="w-5 h-5" />, label: 'DISCOVERING' },
    scoring: { variant: 'warning', icon: <Megaphone className="w-5 h-5" />, label: 'SCORING' },
    completed: { variant: 'success', icon: <CheckCircle className="w-5 h-5" />, label: 'COMPLETED' },
    failed: { variant: 'error', icon: <AlertCircle className="w-5 h-5" />, label: 'FAILED' },
};

export const SessionCard: React.FC<SessionCardProps> = ({ job }) => {
    const status = statusConfig[job.status] || statusConfig.pending;
    const progress = job.discovery_limit ? Math.round((job.profiles_discovered / job.discovery_limit) * 100) : 0;

    return (
        <div className="bg-white rounded-3xl border border-gray-100 p-6 transition-all duration-300 hover:border-brand-blue/20 hover:shadow-soft hover:-translate-y-1">
            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div className="flex items-start gap-4">
                    {/* Icon */}
                    <div className={cn("w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0 transition-colors",
                        status.variant === 'success' ? 'bg-brand-success/10 text-brand-success' :
                            status.variant === 'info' ? 'bg-brand-blue/10 text-brand-blue' :
                                status.variant === 'warning' ? 'bg-brand-warning/10 text-brand-warning' :
                                    status.variant === 'error' ? 'bg-brand-error/10 text-brand-error' :
                                        'bg-gray-100 text-gray-500'
                    )}>
                        {status.icon}
                    </div>

                    {/* Content */}
                    <div>
                        <div className="flex items-center gap-3 mb-1">
                            <h3 className="font-bold text-lg text-brand-text">{job.name}</h3>
                            <Badge variant={status.variant}>{status.label}</Badge>
                        </div>
                        <p className="text-brand-secondary text-sm font-medium">
                            Created {formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
                        </p>

                        {/* Stats */}
                        <div className="flex flex-wrap gap-4 text-sm mt-3">
                            <span className="text-brand-secondary font-medium">
                                <span className="font-bold text-brand-text">{job.profiles_discovered}</span> profiles discovered
                            </span>
                            <span className="text-brand-secondary font-medium">
                                <span className="font-bold text-brand-text">{job.profiles_scored}</span> scored
                            </span>
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 self-end lg:self-center">
                    <Link to={`/dashboard/${job.id}`}>
                        <Button variant="secondary" size="sm" className="h-10 px-6 rounded-full font-bold">
                            {job.status === 'completed' ? 'View Results' : 'View Progress'}
                        </Button>
                    </Link>
                    <Button variant="ghost" size="icon" className="w-10 h-10 rounded-full text-brand-secondary hover:text-brand-text">
                        <MoreHorizontal className="w-5 h-5" />
                    </Button>
                </div>
            </div>

            {/* Progress Bar (if active) */}
            {(job.status === 'discovering' || job.status === 'scoring' || job.status === 'analyzing') && (
                <div className="mt-6 pt-5 border-t border-gray-50">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-bold text-brand-secondary uppercase tracking-widest">Progress</span>
                        <span className="text-sm font-bold text-brand-text">{progress}%</span>
                    </div>
                    <ProgressBar value={progress} size="sm" animated />
                </div>
            )}
        </div>
    );
};
