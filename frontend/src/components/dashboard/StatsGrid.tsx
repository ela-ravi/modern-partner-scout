import React from 'react';
import type { JobAnalytics } from '../../types';
import { Users, CheckCircle, Mail, BarChart2 } from 'lucide-react';
import { cn } from '../../lib/utils';

interface StatsGridProps {
    analytics: JobAnalytics;
}

export const StatsGrid: React.FC<StatsGridProps> = ({ analytics }) => {
    return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-12 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            {/* Total Discovered */}
            <div className="card p-6 border-brand-blue/5 hover:border-brand-blue/10 transition-all">
                <div className="flex items-center justify-between mb-4">
                    <p className="text-[10px] font-bold text-brand-secondary uppercase tracking-widest">Total Discovered</p>
                    <div className="w-10 h-10 rounded-xl bg-brand-blue/10 flex items-center justify-center text-brand-blue">
                        <Users className="w-5 h-5" />
                    </div>
                </div>
                <p className="text-4xl font-bold tracking-tight text-brand-text mb-2">{analytics.total_profiles}</p>
                <div className="flex items-center gap-2">
                    <span className="text-[12px] font-bold text-brand-success bg-brand-success/10 px-2.5 py-0.5 rounded-full">
                        +{analytics.new_profiles} new
                    </span>
                </div>
            </div>

            {/* Evaluated */}
            <div className="card p-6 border-brand-success/5 hover:border-brand-success/10 transition-all">
                <div className="flex items-center justify-between mb-4">
                    <p className="text-[10px] font-bold text-brand-secondary uppercase tracking-widest">Evaluated</p>
                    <div className="w-10 h-10 rounded-xl bg-brand-success/10 flex items-center justify-center text-brand-success">
                        <CheckCircle className="w-5 h-5" />
                    </div>
                </div>
                <p className="text-4xl font-bold tracking-tight text-brand-text mb-2">{analytics.done_profiles}</p>
                <p className="text-brand-secondary text-xs font-bold uppercase tracking-wider">High precision</p>
            </div>

            {/* Emails Found */}
            <div className="card p-6 border-brand-warning/5 hover:border-brand-warning/10 transition-all">
                <div className="flex items-center justify-between mb-4">
                    <p className="text-[10px] font-bold text-brand-secondary uppercase tracking-widest">Emails Found</p>
                    <div className="w-10 h-10 rounded-xl bg-brand-warning/10 flex items-center justify-center text-brand-warning">
                        <Mail className="w-5 h-5" />
                    </div>
                </div>
                <p className="text-4xl font-bold tracking-tight text-brand-text mb-2">{analytics.profiles_with_email}</p>
                <p className="text-brand-secondary text-xs font-bold uppercase tracking-wider">
                    {analytics.total_profiles > 0 ? Math.round((analytics.profiles_with_email / analytics.total_profiles) * 100) : 0}% extraction
                </p>
            </div>

            {/* Avg Score */}
            <div className="card p-6 bg-brand-text text-white hover:bg-black transition-all">
                <div className="flex items-center justify-between mb-4">
                    <p className="text-[10px] font-bold opacity-60 uppercase tracking-widest">Avg Score</p>
                    <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center text-white">
                        <BarChart2 className="w-5 h-5" />
                    </div>
                </div>
                <p className="text-4xl font-bold tracking-tight mb-2">
                    {analytics.avg_score ? Math.round(analytics.avg_score) : 0}%
                </p>
                <p className="text-white/60 text-xs font-bold uppercase tracking-wider">
                    Max: {analytics.max_score ? Math.round(analytics.max_score) : 0}%
                </p>
            </div>
        </div>
    );
};
