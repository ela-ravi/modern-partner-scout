import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { StatsGrid } from '../components/dashboard/StatsGrid';
import { ProfileCard } from '../components/dashboard/ProfileCard';
import { ProfileDetailModal } from '../components/dashboard/ProfileDetailModal';
import { Button } from '../components/ui/Button';
import type { DiscoveryJob, JobAnalytics, CompleteProfile } from '../types';
import { api } from '../lib/api';
import { useToast } from '../hooks/useToast';
import { ArrowLeft, RefreshCw } from 'lucide-react';
import { cn } from '../lib/utils';

const DashboardPage: React.FC = () => {
    const { jobId } = useParams<{ jobId: string }>();
    const { toast } = useToast();

    const [job, setJob] = useState<DiscoveryJob | null>(null);
    const [profiles, setProfiles] = useState<CompleteProfile[]>([]);
    const [analytics, setAnalytics] = useState<JobAnalytics | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'all' | 'new' | 'processing' | 'done'>('all');

    // Modal State
    const [selectedProfile, setSelectedProfile] = useState<CompleteProfile | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const fetchDashboardData = async () => {
        if (!jobId) return;
        try {
            setLoading(true);

            // Fetch job details and analytics
            const [jobResponse, analyticsResponse] = await Promise.all([
                api.get<any>(`/jobs/${jobId}`),
                api.get<JobAnalytics>(`/jobs/${jobId}/analytics`)
            ]);

            console.log('[Dashboard] Job Response:', jobResponse);
            console.log('[Dashboard] Analytics Response:', analyticsResponse);

            // Parse job - backend returns {job: {...}, profiles: [...]}
            const jobData = jobResponse.job || jobResponse;
            const profilesData = jobResponse.profiles || [];

            setJob(jobData);
            setProfiles(profilesData);
            setAnalytics(analyticsResponse);
        } catch (error) {
            console.error('Failed to load dashboard:', error);
            toast({
                title: "Error loading dashboard",
                description: "Could not fetch job data. Please try again.",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDashboardData();
        const interval = setInterval(() => {
            if (job?.status === 'discovering' || job?.status === 'scoring') {
                fetchDashboardData();
            }
        }, 10000);
        return () => clearInterval(interval);
    }, [jobId]);

    const openProfileModal = (profile: CompleteProfile) => {
        setSelectedProfile(profile);
        setIsModalOpen(true);
    };

    const filteredProfiles = profiles.filter((p: CompleteProfile) => {
        if (activeTab === 'all') return true;
        return p.status === activeTab;
    });

    const sortedProfiles = [...filteredProfiles].sort((a: CompleteProfile, b: CompleteProfile) => (b.final_score || 0) - (a.final_score || 0));

    if (loading && !job) {
        return (
            <div className="max-w-6xl mx-auto px-6 py-10 space-y-8">
                <div className="h-20 card animate-pulse"></div>
                <div className="grid grid-cols-4 gap-4">
                    {[1, 2, 3, 4].map(i => <div key={i} className="h-32 card animate-pulse"></div>)}
                </div>
                <div className="grid grid-cols-3 gap-5">
                    {[1, 2, 3, 4, 5, 6].map(i => <div key={i} className="h-96 card animate-pulse"></div>)}
                </div>
            </div>
        );
    }

    if (!job) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[50vh] animate-fade-in">
                <div className="w-16 h-16 rounded-full bg-gray-50 flex items-center justify-center mb-6">
                    <ArrowLeft className="w-8 h-8 text-brand-secondary" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-brand-text">Session not found</h3>
                <p className="text-brand-secondary mb-8 leading-relaxed font-medium">The discovery session you're looking for doesn't exist.</p>
                <Link to="/sessions"><Button>Back to Sessions</Button></Link>
            </div>
        );
    }

    return (
        <div className="max-w-6xl w-full mx-auto px-6 py-10">
            {/* Page Header */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10 animate-fade-in">
                <div>
                    <div className="flex items-center gap-3 mb-3">
                        <Link to="/sessions" className="w-10 h-10 rounded-full bg-gray-50 flex items-center justify-center text-brand-secondary hover:text-brand-text hover:bg-gray-100 transition-all">
                            <ArrowLeft className="w-5 h-5" />
                        </Link>
                        <h1 className="text-4xl font-bold tracking-tight text-brand-text">{job.name}</h1>
                    </div>
                    <p className="text-brand-secondary text-lg font-medium ml-13">
                        {analytics?.total_profiles || profiles.length} partners discovered • {analytics?.done_profiles || 0} evaluated
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <div className={cn("px-4 py-1.5 rounded-full text-[11px] font-bold uppercase tracking-widest shadow-sm border", getStatusColor(job.status))}>
                        {job.status}
                    </div>
                    <Button variant="outline" size="sm" onClick={fetchDashboardData} className="h-10 rounded-full font-bold">
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Refresh
                    </Button>
                    <Link to="/sessions/new">
                        <Button size="sm" className="h-10 rounded-full font-bold shadow-soft">New Discovery</Button>
                    </Link>
                </div>
            </div>

            {/* Stats */}
            {analytics && <StatsGrid analytics={analytics} />}

            {/* Tabs & Filters */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 animate-fade-in" style={{ animationDelay: '0.2s' }}>
                <div className="inline-flex gap-1 p-1 bg-gray-100 rounded-full self-start">
                    {(['all', 'new', 'processing', 'done'] as const).map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={cn(
                                "px-6 py-2.5 rounded-full text-sm font-bold transition-all",
                                activeTab === tab
                                    ? "bg-white shadow-soft text-brand-blue"
                                    : "text-brand-secondary hover:text-brand-text"
                            )}
                        >
                            {tab.charAt(0).toUpperCase() + tab.slice(1)} <span className="opacity-40 ml-1">{getTabCount(profiles, tab)}</span>
                        </button>
                    ))}
                </div>

                <div className="flex items-center gap-3">
                    <span className="text-xs font-bold text-brand-secondary uppercase tracking-widest">Sort by:</span>
                    <button className="inline-flex items-center gap-2 px-5 py-2.5 bg-white border border-gray-100 rounded-full text-sm font-bold hover:bg-gray-50 transition-all shadow-sm">
                        Score (High to Low)
                    </button>
                </div>
            </div>

            {/* Grid */}
            {sortedProfiles.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-slide-up" style={{ animationDelay: '0.3s' }}>
                    {sortedProfiles.map((profile) => (
                        <ProfileCard
                            key={profile.id}
                            profile={profile}
                            onClick={() => openProfileModal(profile)}
                        />
                    ))}
                </div>
            ) : (
                <div className="py-24 text-center bg-white rounded-3xl border border-dashed border-gray-200 animate-scale-in">
                    <div className="w-16 h-16 rounded-full bg-gray-50 flex items-center justify-center mx-auto mb-6">
                        <RefreshCw className="w-8 h-8 text-brand-secondary opacity-20" />
                    </div>
                    <p className="text-brand-secondary font-bold text-lg">No profiles found in this category.</p>
                </div>
            )}

            {/* Profile Detail Modal */}
            <ProfileDetailModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                profile={selectedProfile}
            />
        </div>
    );
};

const getStatusColor = (status: string) => {
    switch (status) {
        case 'completed': return 'bg-brand-success/10 text-brand-success border-brand-success/20';
        case 'discovering': return 'bg-brand-blue/10 text-brand-blue border-brand-blue/20';
        case 'scoring': return 'bg-brand-warning/10 text-brand-warning border-brand-warning/20';
        case 'failed': return 'bg-brand-error/10 text-brand-error border-brand-error/20';
        default: return 'bg-gray-100 text-gray-500 border-gray-200';
    }
};

const getTabCount = (profiles: CompleteProfile[], tab: string) => {
    if (tab === 'all') return profiles.length;
    return profiles.filter((p: CompleteProfile) => p.status === tab).length;
};

export default DashboardPage;
