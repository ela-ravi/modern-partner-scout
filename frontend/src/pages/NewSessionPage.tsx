import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
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
        <div className="max-w-3xl w-full mx-auto px-6 py-12">
            {/* Stepper */}
            <div className="mb-16 animate-fade-in text-center">
                <div className="inline-flex items-center justify-center p-1 bg-gray-100 rounded-full">
                    <div className={cn("flex items-center gap-2 px-6 py-2 rounded-full text-sm font-bold transition-all", step === 1 ? "bg-white text-brand-blue shadow-soft" : "text-brand-secondary")}>
                        <div className={cn("w-5 h-5 rounded-full flex items-center justify-center text-[10px]", step === 1 ? "bg-brand-blue text-white" : "bg-gray-200")}>1</div>
                        Configure
                    </div>
                    <div className={cn("flex items-center gap-2 px-6 py-2 rounded-full text-sm font-bold transition-all", step === 2 ? "bg-white text-brand-blue shadow-soft" : "text-brand-secondary")}>
                        <div className={cn("w-5 h-5 rounded-full flex items-center justify-center text-[10px]", step === 2 ? "bg-brand-blue text-white" : "bg-gray-200")}>2</div>
                        Launch
                    </div>
                </div>
            </div>

            {/* Page Header */}
            <div className="text-center mb-12 animate-slide-up" style={{ animationDelay: '0.1s' }}>
                <h1 className="text-4xl font-bold tracking-tight mb-4 text-brand-text">
                    {step === 1 ? 'Configure Discovery' : 'Review & Launch'}
                </h1>
                <p className="text-brand-secondary text-xl max-w-lg mx-auto font-medium">
                    {step === 1 ? 'Define your brand DNA and discovery parameters' : 'Review your campaign details before starting'}
                </p>
            </div>

            {/* Form Card */}
            <div className="card animate-slide-up p-8" style={{ animationDelay: '0.2s' }}>
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
                            <Label>Brand Description <span className="text-brand-secondary font-normal ml-1 opacity-50">(optional)</span></Label>
                            <p className="text-brand-secondary text-[13px] font-medium">Describe your brand identity and what makes it unique</p>
                            <Textarea
                                placeholder="We are a wellness brand focused on organic..."
                                rows={3}
                                value={formData.brand_description}
                                onChange={(e) => updateField('brand_description', e.target.value)}
                            />
                        </div>

                        {/* Reference Profiles */}
                        <div className="space-y-2">
                            <Label>Reference Instagram Profiles <span className="text-brand-secondary font-normal ml-1 opacity-50">(2-10 required)</span></Label>
                            <p className="text-brand-secondary text-[13px] font-medium">Add your brand or similar accounts for AI to analyze</p>
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
                            <div className="bg-gray-50 rounded-2xl p-6 space-y-5">
                                <div className="flex justify-between items-center">
                                    <Label>Profiles to Discover</Label>
                                    <span className="font-bold text-brand-blue bg-white px-3 py-1 rounded-full text-xs shadow-soft">{formData.discovery_limit}</span>
                                </div>
                                <Slider
                                    min={10} max={100} step={10}
                                    value={[formData.discovery_limit]}
                                    onValueChange={(vals) => updateField('discovery_limit', vals[0])}
                                />
                                <div className="flex justify-between text-[10px] font-bold text-gray-300 uppercase tracking-widest">
                                    <span>10</span><span>100</span>
                                </div>
                            </div>

                            <div className="bg-gray-50 rounded-2xl p-6 space-y-5">
                                <div className="flex justify-between items-center">
                                    <Label>Minimum Score</Label>
                                    <span className="font-bold text-brand-success bg-white px-3 py-1 rounded-full text-xs shadow-soft">{formData.min_score}%</span>
                                </div>
                                <Slider
                                    min={50} max={95} step={5}
                                    value={[formData.min_score]}
                                    onValueChange={(vals) => updateField('min_score', vals[0])}
                                />
                                <div className="flex justify-between text-[10px] font-bold text-gray-300 uppercase tracking-widest">
                                    <span>50%</span><span>95%</span>
                                </div>
                            </div>
                        </div>

                        {/* Follower Range */}
                        <div className="bg-brand-blue/5 rounded-2xl p-6 border border-brand-blue/10">
                            <Label className="mb-4 block">Target Follower Range</Label>
                            <div className="grid grid-cols-2 gap-5">
                                <div className="space-y-2">
                                    <span className="text-[11px] font-bold text-brand-blue uppercase tracking-wider">Minimum</span>
                                    <Input
                                        type="number"
                                        value={formData.follower_range_min}
                                        onChange={(e) => updateField('follower_range_min', parseInt(e.target.value) || 0)}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <span className="text-[11px] font-bold text-brand-blue uppercase tracking-wider">Maximum</span>
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
                        <div className="space-y-8 px-2">
                            <div className="border-b border-gray-100 pb-6">
                                <h3 className="text-2xl font-bold text-brand-text mb-2">{formData.name}</h3>
                                <p className="text-brand-secondary font-medium">{formData.brand_description || 'No description provided'}</p>
                            </div>

                            <div className="grid grid-cols-2 gap-8">
                                <div className="space-y-1">
                                    <span className="text-[11px] font-bold text-brand-secondary uppercase tracking-widest block">Target Profiles</span>
                                    <span className="text-lg font-bold text-brand-text">{formData.discovery_limit} partners</span>
                                </div>
                                <div className="space-y-1">
                                    <span className="text-[11px] font-bold text-brand-secondary uppercase tracking-widest block">Match Threshold</span>
                                    <span className="text-lg font-bold text-brand-success">{formData.min_score}%+</span>
                                </div>
                                <div className="space-y-1 col-span-2">
                                    <span className="text-[11px] font-bold text-brand-secondary uppercase tracking-widest block">Follower Range</span>
                                    <span className="text-lg font-bold text-brand-text">{formData.follower_range_min.toLocaleString()} - {formData.follower_range_max.toLocaleString()}</span>
                                </div>
                            </div>

                            <div>
                                <span className="text-[11px] font-bold text-brand-secondary uppercase tracking-widest block mb-3">Reference Profiles</span>
                                <div className="flex flex-wrap gap-2">
                                    {formData.reference_profiles.map(p => (
                                        <span key={p} className="px-4 py-2 bg-gray-100 text-brand-text rounded-full text-sm font-bold shadow-sm">{p}</span>
                                    ))}
                                </div>
                            </div>

                            {/* Alert Box */}
                            <div className="bg-brand-warning/10 border border-brand-warning/20 rounded-2xl p-5 flex gap-4">
                                <div className="w-10 h-10 rounded-full bg-brand-warning/20 flex items-center justify-center shrink-0">
                                    <AlertCircle className="w-5 h-5 text-brand-warning" />
                                </div>
                                <div>
                                    <p className="text-sm font-bold text-brand-warning mb-1">Ready to Launch</p>
                                    <p className="text-[13px] text-brand-warning/80 font-medium">Our AI discovery engine will begin scanning Instagram immediately. The first results typically appear within 5-10 minutes.</p>
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
                        <button className="flex items-center gap-2 text-brand-secondary hover:text-brand-text transition-all font-bold text-sm bg-gray-50 px-5 py-2.5 rounded-full hover:bg-gray-100">
                            <ArrowLeft className="w-4 h-4" />
                            Cancel
                        </button>
                    </Link>
                ) : (
                    <button
                        onClick={() => setStep(1)}
                        className="flex items-center gap-2 text-brand-secondary hover:text-brand-text transition-all font-bold text-sm bg-gray-50 px-5 py-2.5 rounded-full hover:bg-gray-100"
                    >
                        <ArrowLeft className="w-4 h-4" />
                        Back
                    </button>
                )}

                {step === 1 ? (
                    <Button
                        className="h-[48px] px-10 shadow-medium"
                        onClick={handleNext}
                    >
                        Continue
                        <ArrowRight className="w-4 h-4 ml-2" />
                    </Button>
                ) : (
                    <Button
                        className="h-[48px] px-10 shadow-medium"
                        onClick={handleSubmit}
                        disabled={loading}
                    >
                        {loading ? 'Launching Session...' : 'Launch Session'}
                        {!loading && <Check className="w-4 h-4 ml-2" />}
                    </Button>
                )}
            </div>
        </div>
    );
};

export default NewSessionPage;
