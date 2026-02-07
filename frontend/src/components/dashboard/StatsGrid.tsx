import React from 'react';
import type { JobAnalytics } from '../../types';
import { Users, CheckCircle, Mail, BarChart2 } from 'lucide-react';

interface StatsGridProps {
    analytics: JobAnalytics;
}

export const StatsGrid: React.FC<StatsGridProps> = ({ analytics }) => {
    return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <div className="bg-white rounded-[16px] border border-[rgba(0,0,0,0.04)] p-5 shadow-[0_2px_12px_rgba(0,0,0,0.04)]">
                <div className="flex items-center justify-between mb-2">
                    <p className="text-[#86868b] text-sm font-medium">Total Discovered</p>
                    <Users className="w-5 h-5 text-[#0071e3]" />
                </div>
                <p className="text-3xl font-semibold tracking-tight text-[#1d1d1f]">{analytics.total_profiles}</p>
                <div className="flex items-center gap-2 mt-1">
                    <span className="text-[12px] font-medium text-[#34c759] bg-[#34c759]/10 px-2 py-0.5 rounded-full">
                        {analytics.new_profiles} new
                    </span>
                </div>
            </div>

            <div className="bg-white rounded-[16px] border border-[rgba(0,0,0,0.04)] p-5 shadow-[0_2px_12px_rgba(0,0,0,0.04)]">
                <div className="flex items-center justify-between mb-2">
                    <p className="text-[#86868b] text-sm font-medium">High Match</p>
                    <CheckCircle className="w-5 h-5 text-[#34c759]" />
                </div>
                {/* Assuming High Match is > 80. Backend doesn't give this count directly in analytics, using Max Score logic or placeholder for now. 
                    Actually, let's use Done profiles as proxy for now or if we had score distribution we'd use that.
                    Use 'done_profiles' for now as 'Evaluated'.
                 */}
                <p className="text-3xl font-semibold tracking-tight text-[#1d1d1f]">{analytics.done_profiles}</p>
                <p className="text-[#86868b] text-xs font-medium mt-1">Evaluated Profiles</p>
            </div>

            <div className="bg-white rounded-[16px] border border-[rgba(0,0,0,0.04)] p-5 shadow-[0_2px_12px_rgba(0,0,0,0.04)]">
                <div className="flex items-center justify-between mb-2">
                    <p className="text-[#86868b] text-sm font-medium">Emails Found</p>
                    <Mail className="w-5 h-5 text-[#ff9500]" />
                </div>
                <p className="text-3xl font-semibold tracking-tight text-[#1d1d1f]">{analytics.profiles_with_email}</p>
                <p className="text-[#86868b] text-xs font-medium mt-1">
                    {analytics.total_profiles > 0 ? Math.round((analytics.profiles_with_email / analytics.total_profiles) * 100) : 0}% extraction
                </p>
            </div>

            <div className="bg-white rounded-[16px] border border-[rgba(0,0,0,0.04)] p-5 shadow-[0_2px_12px_rgba(0,0,0,0.04)]">
                <div className="flex items-center justify-between mb-2">
                    <p className="text-[#86868b] text-sm font-medium">Avg Score</p>
                    <BarChart2 className="w-5 h-5 text-[#af52de]" />
                </div>
                <p className="text-3xl font-semibold tracking-tight text-[#1d1d1f]">
                    {analytics.avg_score ? Math.round(analytics.avg_score) : 0}%
                </p>
                <p className="text-[#86868b] text-xs font-medium mt-1">
                    Max: {analytics.max_score ? Math.round(analytics.max_score) : 0}%
                </p>
            </div>
        </div>
    );
};
