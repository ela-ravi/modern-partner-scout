import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { StatsGrid } from '../components/dashboard/StatsGrid';
import { ProfileCard } from '../components/dashboard/ProfileCard';
import { ProfileDetailModal } from '../components/dashboard/ProfileDetailModal';
import { Button } from '../components/ui/Button';
import type { DiscoveryJob, JobAnalytics, CompleteProfile } from '../types';
import { api } from '../lib/api';
import { useToast } from '../hooks/useToast';
import { ArrowLeft, RefreshCw } from 'lucide-react';

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
            <DashboardLayout>
                <div className="max-w-6xl mx-auto px-6 py-10 space-y-8">
                    <div className="h-20 bg-gray-100 rounded-xl animate-pulse"></div>
                    <div className="grid grid-cols-4 gap-4">
                        {[1, 2, 3, 4].map(i => <div key={i} className="h-32 bg-gray-100 rounded-xl animate-pulse"></div>)}
                    </div>
                    <div className="grid grid-cols-3 gap-5">
                        {[1, 2, 3, 4, 5, 6].map(i => <div key={i} className="h-96 bg-gray-100 rounded-xl animate-pulse"></div>)}
                    </div>
                </div>
            </DashboardLayout>
        );
    }

    if (!job) {
        return (
            <DashboardLayout>
                <div className="flex flex-col items-center justify-center min-h-[50vh]">
                    <p className="text-lg text-gray-500">Job not found.</p>
                    <Link to="/sessions"><Button className="mt-4">Back to Sessions</Button></Link>
                </div>
            </DashboardLayout>
        );
    }

    return (
        <DashboardLayout>
            <div className="max-w-6xl w-full mx-auto px-6 py-10">
                {/* Page Header */}
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10 animate-fade-in">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <Link to="/sessions" className="text-[#86868b] hover:text-[#1d1d1f] transition-colors">
                                <ArrowLeft className="w-5 h-5" />
                            </Link>
                            <h1 className="text-3xl font-semibold tracking-tight text-[#1d1d1f]">{job.name}</h1>
                        </div>
                        <p className="text-[#86868b] text-lg">
                            {analytics?.total_profiles || profiles.length} partners discovered • {analytics?.done_profiles || 0} evaluated
                        </p>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${getStatusColor(job.status)}`}>
                            {job.status}
                        </div>
                        <Button variant="outline" size="sm" onClick={fetchDashboardData}>
                            <RefreshCw className="w-4 h-4 mr-2" />
                            Refresh
                        </Button>
                        <Link to="/sessions/new">
                            <Button size="sm">New Discovery</Button>
                        </Link>
                    </div>
                </div>

                {/* Stats */}
                {analytics && <StatsGrid analytics={analytics} />}

                {/* Tabs & Filters */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 animate-fade-in" style={{ animationDelay: '0.2s' }}>
                    <div className="inline-flex gap-1 p-1 bg-[#f5f5f7] rounded-xl self-start">
                        {(['all', 'new', 'processing', 'done'] as const).map((tab) => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === tab
                                    ? 'bg-white shadow-sm text-[#1d1d1f]'
                                    : 'text-[#86868b] hover:text-[#1d1d1f]'
                                    }`}
                            >
                                {tab.charAt(0).toUpperCase() + tab.slice(1)} ({getTabCount(profiles, tab)})
                            </button>
                        ))}
                    </div>

                    <div className="flex items-center gap-3">
                        <span className="text-sm text-[#86868b]">Sort by:</span>
                        <button className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-[rgba(0,0,0,0.1)] rounded-xl text-sm font-medium hover:bg-[#f5f5f7] transition-colors">
                            Score (High to Low)
                        </button>
                    </div>
                </div>

                {/* Grid */}
                {sortedProfiles.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 animate-slide-up" style={{ animationDelay: '0.3s' }}>
                        {sortedProfiles.map((profile) => (
                            <ProfileCard
                                key={profile.id}
                                profile={profile}
                                onClick={() => openProfileModal(profile)}
                            />
                        ))}
                    </div>
                ) : (
                    <div className="py-20 text-center bg-white rounded-2xl border border-dashed border-gray-200">
                        <p className="text-gray-500">No profiles found in this category.</p>
                    </div>
                )}
            </div>

            {/* Profile Detail Modal */}
            <ProfileDetailModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                profile={selectedProfile}
            />
        </DashboardLayout>
    );
};

const getStatusColor = (status: string) => {
    switch (status) {
        case 'completed': return 'bg-green-100 text-green-700';
        case 'discovering': return 'bg-blue-100 text-blue-700';
        case 'scoring': return 'bg-orange-100 text-orange-700';
        case 'failed': return 'bg-red-100 text-red-700';
        default: return 'bg-gray-100 text-gray-700';
    }
};

const getTabCount = (profiles: CompleteProfile[], tab: string) => {
    if (tab === 'all') return profiles.length;
    return profiles.filter((p: CompleteProfile) => p.status === tab).length;
};

export default DashboardPage;
