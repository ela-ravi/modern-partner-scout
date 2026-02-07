import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';
import { Label } from '../components/ui/Label';
import { Slider } from '../components/ui/Slider';
import { TagInput } from '../components/ui/TagInput';
import { useToast } from '../hooks/useToast';
import { api } from '../lib/api';
import type { DiscoveryJob } from '../types';
import { ArrowRight, ArrowLeft, Check, AlertCircle } from 'lucide-react';
import { cn } from '../lib/utils';

const NewSessionPage: React.FC = () => {
    const navigate = useNavigate();
    const { toast } = useToast();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);

    // Form State
    const [formData, setFormData] = useState({
        name: '',
        brand_description: '',
        reference_profiles: [] as string[],
        keywords: [] as string[],
        discovery_limit: 50,
        min_score: 70,
        follower_range_min: 10000,
        follower_range_max: 500000
    });

    const updateField = (field: string, value: any) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const handleNext = () => {
        // Validation
        if (!formData.name) {
            toast({ title: "Validation Error", description: "Campaign name is required", variant: "destructive" });
            return;
        }
        if (formData.reference_profiles.length < 2) {
            toast({ title: "Validation Error", description: "Please add at least 2 reference profiles", variant: "destructive" });
            return;
        }
        setStep(2);
    };

    const handleSubmit = async () => {
        try {
            setLoading(true);

            // 1. Create Job
            const job = await api.post<DiscoveryJob>('/jobs', {
                name: formData.name,
                brand_description: formData.brand_description,
                reference_profiles: formData.reference_profiles,
                follower_range_min: formData.follower_range_min,
                follower_range_max: formData.follower_range_max,
                discovery_limit: formData.discovery_limit
            });

            // 2. Start Job
            await api.post(`/jobs/${job.id}/start`, {});

            toast({
                title: "Discovery Started",
                description: `Campaign "${job.name}" has been launched!`,
            });

            // Redirect to Dashboard
            navigate(`/dashboard/${job.id}`);

        } catch (error) {
            console.error('Failed to create job:', error);
            toast({
                title: "Error",
                description: "Failed to create discovery session. Please try again.",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="max-w-3xl w-full mx-auto px-6 py-12">
                {/* Stepper */}
                <div className="mb-16 animate-fade-in">
                    <div className="flex items-center justify-center gap-0 max-w-sm mx-auto">
                        <div className="flex items-center gap-3">
                            <div className={cn("w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold shadow-lg transition-colors", step >= 1 ? "bg-[#0071e3] text-white" : "bg-[#f5f5f7] text-[#aeaeb2]")}>
                                1
                            </div>
                            <span className={cn("font-medium hidden sm:block", step >= 1 ? "text-[#1d1d1f]" : "text-[#aeaeb2]")}>Configure</span>
                        </div>

                        <div className="flex-1 h-px mx-6 bg-gradient-to-r from-[#0071e3] to-[#f5f5f7] max-w-[80px]"></div>

                        <div className="flex items-center gap-3">
                            <div className={cn("w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold transition-colors", step >= 2 ? "bg-[#0071e3] text-white" : "bg-[#f5f5f7] text-[#aeaeb2]")}>
                                2
                            </div>
                            <span className={cn("font-medium hidden sm:block", step >= 2 ? "text-[#1d1d1f]" : "text-[#aeaeb2]")}>Launch</span>
                        </div>
                    </div>
                </div>

                {/* Page Header */}
                <div className="text-center mb-12 animate-slide-up" style={{ animationDelay: '0.1s' }}>
                    <h1 className="text-4xl font-semibold tracking-tight mb-4 text-[#1d1d1f]">
                        {step === 1 ? 'Configure Discovery' : 'Review & Launch'}
                    </h1>
                    <p className="text-[#86868b] text-xl max-w-lg mx-auto">
                        {step === 1 ? 'Define your brand DNA and discovery parameters' : 'Review your campaign details before starting'}
                    </p>
                </div>

                {/* Form Card */}
                <div className="bg-white rounded-[18px] shadow-[0_2px_12px_rgba(0,0,0,0.04),0_0_1px_rgba(0,0,0,0.1)] p-8 animate-slide-up" style={{ animationDelay: '0.2s' }}>
                    {step === 1 ? (
                        <div className="space-y-8">
                            {/* Campaign Name */}
                            <div className="space-y-2">
                                <Label>Campaign Name</Label>
                                <Input
                                    placeholder="e.g., Summer Wellness Campaign 2026"
                                    value={formData.name}
                                    onChange={(e) => updateField('name', e.target.value)}
                                />
                            </div>

                            {/* Brand Description */}
                            <div className="space-y-2">
                                <Label>Brand Description <span className="text-[#aeaeb2] font-normal ml-1">(optional)</span></Label>
                                <p className="text-[#86868b] text-sm">Describe your brand identity and what makes it unique</p>
                                <Textarea
                                    placeholder="We are a wellness brand focused on organic..."
                                    rows={3}
                                    value={formData.brand_description}
                                    onChange={(e) => updateField('brand_description', e.target.value)}
                                />
                            </div>

                            {/* Reference Profiles */}
                            <div className="space-y-2">
                                <Label>Reference Instagram Profiles <span className="text-[#aeaeb2] font-normal ml-1">(2-10 required)</span></Label>
                                <p className="text-[#86868b] text-sm">Add your brand or similar accounts for AI to analyze</p>
                                <TagInput
                                    placeholder="Add Instagram handle (e.g. @apple)"
                                    tags={formData.reference_profiles}
                                    setTags={(tags) => updateField('reference_profiles', tags)}
                                />
                            </div>

                            {/* Keywords */}
                            <div className="space-y-2">
                                <Label>Target Keywords & Hashtags</Label>
                                <TagInput
                                    placeholder="Add keyword or hashtag..."
                                    tags={formData.keywords}
                                    setTags={(tags) => updateField('keywords', tags)}
                                />
                            </div>

                            {/* Sliders */}
                            <div className="grid md:grid-cols-2 gap-6">
                                <div className="bg-[#f5f5f7] rounded-[12px] p-5 space-y-4">
                                    <div className="flex justify-between">
                                        <Label>Profiles to Discover</Label>
                                        <span className="font-semibold text-[#0071e3]">{formData.discovery_limit}</span>
                                    </div>
                                    <Slider
                                        min={10} max={100} step={10}
                                        value={[formData.discovery_limit]}
                                        onValueChange={(vals) => updateField('discovery_limit', vals[0])}
                                    />
                                    <div className="flex justify-between text-xs text-[#aeaeb2]">
                                        <span>10</span><span>100</span>
                                    </div>
                                </div>

                                <div className="bg-[#f5f5f7] rounded-[12px] p-5 space-y-4">
                                    <div className="flex justify-between">
                                        <Label>Minimum Score</Label>
                                        <span className="font-semibold text-[#34c759]">{formData.min_score}%</span>
                                    </div>
                                    <Slider
                                        min={50} max={95} step={5}
                                        value={[formData.min_score]}
                                        onValueChange={(vals) => updateField('min_score', vals[0])}
                                    />
                                    <div className="flex justify-between text-xs text-[#aeaeb2]">
                                        <span>50%</span><span>95%</span>
                                    </div>
                                </div>
                            </div>

                            {/* Follower Range (Simple Inputs for now) */}
                            <div className="bg-[#f5f5f7] rounded-[12px] p-5">
                                <Label className="mb-4 block">Follower Range</Label>
                                <div className="grid grid-cols-2 gap-4 mb-4">
                                    <div className="space-y-2">
                                        <span className="text-xs text-[#86868b]">Minimum</span>
                                        <Input
                                            type="number"
                                            value={formData.follower_range_min}
                                            onChange={(e) => updateField('follower_range_min', parseInt(e.target.value) || 0)}
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <span className="text-xs text-[#86868b]">Maximum</span>
                                        <Input
                                            type="number"
                                            value={formData.follower_range_max}
                                            onChange={(e) => updateField('follower_range_max', parseInt(e.target.value) || 0)}
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-8">
                            {/* Review Section */}
                            <div className="space-y-6">
                                <div className="border-b border-[rgba(0,0,0,0.06)] pb-4">
                                    <h3 className="text-lg font-semibold text-[#1d1d1f] mb-1">{formData.name}</h3>
                                    <p className="text-[#86868b]">{formData.brand_description || 'No description provided'}</p>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <span className="text-sm text-[#86868b] block mb-1">Target Profiles</span>
                                        <span className="font-medium">{formData.discovery_limit} profiles</span>
                                    </div>
                                    <div>
                                        <span className="text-sm text-[#86868b] block mb-1">Min Score Match</span>
                                        <span className="font-medium">{formData.min_score}%</span>
                                    </div>
                                    <div>
                                        <span className="text-sm text-[#86868b] block mb-1">Follower Range</span>
                                        <span className="font-medium">{formData.follower_range_min.toLocaleString()} - {formData.follower_range_max.toLocaleString()}</span>
                                    </div>
                                </div>
                                <div>
                                    <span className="text-sm text-[#86868b] block mb-2">Reference Profiles</span>
                                    <div className="flex flex-wrap gap-2">
                                        {formData.reference_profiles.map(p => (
                                            <span key={p} className="px-3 py-1 bg-[#f5f5f7] text-[#1d1d1f] rounded-full text-sm font-medium">{p}</span>
                                        ))}
                                    </div>
                                </div>
                                {/* Warning */}
                                <div className="bg-[#ff9500]/10 border border-[#ff9500]/20 rounded-xl p-4 flex gap-3">
                                    <AlertCircle className="w-5 h-5 text-[#ff9500] shrink-0" />
                                    <div>
                                        <p className="text-sm font-medium text-[#ff9500] mb-1">Ready to Launch</p>
                                        <p className="text-sm text-[#ff9500]/80">This will immediately start the AI discovery process. It may take 5-10 minutes to complete.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between mt-10 animate-fade-in" style={{ animationDelay: '0.3s' }}>
                    {step === 1 ? (
                        <Link to="/sessions">
                            <button className="flex items-center gap-2 text-[#86868b] hover:text-[#1d1d1f] transition-colors font-medium text-sm">
                                <ArrowLeft className="w-4 h-4" />
                                Cancel
                            </button>
                        </Link>
                    ) : (
                        <button
                            onClick={() => setStep(1)}
                            className="flex items-center gap-2 text-[#86868b] hover:text-[#1d1d1f] transition-colors font-medium text-sm"
                        >
                            <ArrowLeft className="w-4 h-4" />
                            Back
                        </button>
                    )}

                    {step === 1 ? (
                        <Button
                            variant="pill"
                            className="h-[44px] px-8"
                            onClick={handleNext}
                        >
                            Continue
                            <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                    ) : (
                        <Button
                            variant="pill"
                            className="h-[44px] px-8"
                            onClick={handleSubmit}
                            disabled={loading}
                        >
                            {loading ? 'Launching...' : 'Start Discovery'}
                            {!loading && <Check className="w-4 h-4 ml-2" />}
                        </Button>
                    )}
                </div>
            </div>
        </DashboardLayout>
    );
};

export default NewSessionPage;
