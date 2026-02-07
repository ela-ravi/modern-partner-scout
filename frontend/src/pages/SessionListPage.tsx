import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Button } from '../components/ui/Button';
import { SessionCard } from '../components/dashboard/SessionCard';
import type { DiscoveryJob } from '../types';
import { api } from '../lib/api';
import { useToast } from '../hooks/useToast';
import { Plus } from 'lucide-react';

const SessionListPage: React.FC = () => {
    const [jobs, setJobs] = useState<DiscoveryJob[]>([]);
    const [loading, setLoading] = useState(true);
    const { toast } = useToast();

    const fetchJobs = async () => {
        try {
            setLoading(true);
            const response = await api.get<any>('/jobs');

            // DEBUG: Log the raw API response
            console.log('[SessionListPage] Raw API Response:', response);

            // Backend returns {jobs: [...], total: N, limit: N, offset: N}
            const jobsArray = response.jobs || (Array.isArray(response) ? response : []);

            // Sort by created_at desc
            const sortedJobs = jobsArray.sort((a: DiscoveryJob, b: DiscoveryJob) =>
                new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
            );

            console.log('[SessionListPage] Jobs count:', sortedJobs.length);
            setJobs(sortedJobs);
        } catch (error) {
            console.error('Failed to fetch jobs:', error);
            toast({
                title: "Error fetching sessions",
                description: "Could not load your discovery sessions. Please try again.",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchJobs();
    }, []);

    return (
        <DashboardLayout>
            <div className="max-w-6xl w-full mx-auto px-6 py-10">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10 animate-fade-in">
                    <div>
                        <h1 className="text-4xl font-semibold tracking-tight mb-2 text-[#1d1d1f]">Discovery Sessions</h1>
                        <p className="text-[#86868b] text-lg">View and manage all your discovery campaigns</p>
                    </div>
                    <Link to="/sessions/new">
                        <Button variant="pill" className="h-[44px] px-6">
                            <Plus className="w-5 h-5 mr-2" />
                            New Session
                        </Button>
                    </Link>
                </div>

                {/* Content */}
                {loading ? (
                    <div className="space-y-4">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="h-40 bg-white rounded-[16px] border border-gray-100 animate-pulse"></div>
                        ))}
                    </div>
                ) : jobs.length > 0 ? (
                    <div className="space-y-4 animate-slide-up">
                        {jobs.map((job) => (
                            <SessionCard key={job.id} job={job} />
                        ))}
                    </div>
                ) : (
                    <div className="border border-[rgba(0,0,0,0.06)] bg-white rounded-[20px] p-12 text-center animate-scale-in">
                        <div className="w-16 h-16 rounded-full bg-[#f5f5f7] flex items-center justify-center mx-auto mb-6">
                            <Plus className="w-8 h-8 text-[#86868b]" />
                        </div>
                        <h3 className="text-xl font-semibold mb-3 text-[#1d1d1f]">No sessions yet</h3>
                        <p className="text-[#86868b] mb-8 leading-relaxed max-w-md mx-auto">
                            Start your first AI discovery campaign to find the perfect partners for your brand.
                        </p>
                        <Link to="/sessions/new">
                            <Button variant="pill" className="h-[44px] px-8">
                                Start Discovery
                            </Button>
                        </Link>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
};

export default SessionListPage;
