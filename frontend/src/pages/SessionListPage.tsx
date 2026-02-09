import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
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
        <div className="max-w-6xl w-full mx-auto px-6 py-10">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10 animate-fade-in">
                <div>
                    <h1 className="text-4xl font-bold tracking-tight mb-2 text-brand-text">Discovery Sessions</h1>
                    <p className="text-brand-secondary text-lg font-medium">View and manage discovery campaigns</p>
                </div>
                <Link to="/sessions/new">
                    <Button className="h-[44px] px-6">
                        <Plus className="w-5 h-5 mr-2" />
                        New Session
                    </Button>
                </Link>
            </div>

            {/* Content */}
            {loading ? (
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="h-40 card animate-pulse"></div>
                    ))}
                </div>
            ) : jobs.length > 0 ? (
                <div className="space-y-4 animate-slide-up">
                    {jobs.map((job) => (
                        <SessionCard key={job.id} job={job} />
                    ))}
                </div>
            ) : (
                <div className="card p-12 text-center animate-scale-in flex flex-col items-center">
                    <div className="w-16 h-16 rounded-full bg-gray-50 flex items-center justify-center mb-6">
                        <Plus className="w-8 h-8 text-brand-secondary" />
                    </div>
                    <h3 className="text-xl font-bold mb-3 text-brand-text">No sessions yet</h3>
                    <p className="text-brand-secondary mb-8 leading-relaxed max-w-md mx-auto font-medium">
                        Start your first AI discovery campaign to find the perfect partners for your brand.
                    </p>
                    <Link to="/sessions/new">
                        <Button className="h-[44px] px-8">
                            Start Discovery
                        </Button>
                    </Link>
                </div>
            )}
        </div>
    );
};

export default SessionListPage;
