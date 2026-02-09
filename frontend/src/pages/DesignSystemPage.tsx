import { Button } from "../components/ui/Button"
import { Input } from "../components/ui/Input"
import { Badge } from "../components/ui/Badge"
import { ScoreRing } from "../components/ui/ScoreRing"
import { ProgressBar } from "../components/ui/ProgressBar"
import { Plus, Mail, Instagram, ChevronRight, Check } from "lucide-react"
import { cn } from "../lib/utils"

export default function DesignSystemPage() {
    return (
        <div className="min-h-screen bg-brand-background p-10 animate-fade-in">
            <div className="max-w-4xl mx-auto space-y-16">
                <header>
                    <h1 className="text-5xl font-bold tracking-tight text-brand-text mb-2">Design System</h1>
                    <p className="text-xl text-brand-secondary font-medium">Apple-inspired atomic components for PartnerScout AI</p>
                </header>

                {/* Colors Section */}
                <section className="space-y-6">
                    <h2 className="text-2xl font-semibold">Core Colors</h2>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <ColorCard name="Brand Blue" hex="#0071e3" className="bg-[#0071e3] text-white" />
                        <ColorCard name="Success" hex="#34c759" className="bg-[#34c759] text-white" />
                        <ColorCard name="Warning" hex="#ff9500" className="bg-[#ff9500] text-white" />
                        <ColorCard name="Error" hex="#ff3b30" className="bg-[#ff3b30] text-white" />
                        <ColorCard name="Background" hex="#fbfbfd" className="bg-[#fbfbfd] border border-gray-100" />
                        <ColorCard name="Text" hex="#1d1d1f" className="bg-[#1d1d1f] text-white" />
                        <ColorCard name="Secondary" hex="#86868b" className="bg-[#86868b] text-white" />
                    </div>
                </section>

                {/* Buttons Section */}
                <section className="space-y-6">
                    <h2 className="text-2xl font-semibold">Buttons</h2>
                    <div className="flex flex-wrap gap-4 items-end">
                        <div className="space-y-2">
                            <span className="text-xs font-bold text-gray-400 uppercase">Primary</span>
                            <div className="flex gap-2">
                                <Button>Default Button</Button>
                                <Button size="sm">Small</Button>
                                <Button size="lg">Large Action</Button>
                            </div>
                        </div>
                        <div className="space-y-2">
                            <span className="text-xs font-bold text-gray-400 uppercase">Secondary</span>
                            <Button variant="secondary">Secondary Action</Button>
                        </div>
                        <div className="space-y-2">
                            <span className="text-xs font-bold text-gray-400 uppercase">Outline</span>
                            <Button variant="outline">Outline</Button>
                        </div>
                        <div className="space-y-2">
                            <span className="text-xs font-bold text-gray-400 uppercase">With Icons</span>
                            <div className="flex gap-2">
                                <Button>
                                    <Plus className="w-5 h-5 mr-2" />
                                    New Session
                                </Button>
                                <Button variant="secondary" size="icon">
                                    <Instagram className="w-5 h-5" />
                                </Button>
                            </div>
                        </div>
                    </div>
                </section>

                {/* Inputs Section */}
                <section className="space-y-6">
                    <h2 className="text-2xl font-semibold">Inputs</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        <div className="space-y-2">
                            <label className="text-[13px] font-semibold text-brand-secondary ml-1">Default Input</label>
                            <Input placeholder="Enter brand name..." />
                        </div>
                        <div className="space-y-2">
                            <label className="text-[13px] font-semibold text-brand-secondary ml-1">With Value</label>
                            <Input defaultValue="Luxury Boutique" />
                        </div>
                    </div>
                </section>

                {/* Badges Section */}
                <section className="space-y-6">
                    <h2 className="text-2xl font-semibold">Badges & Indicators</h2>
                    <div className="flex flex-wrap gap-6 items-center">
                        <div className="flex gap-2">
                            <Badge variant="default">New</Badge>
                            <Badge variant="success">Genuine</Badge>
                            <Badge variant="warning">Suspicious</Badge>
                            <Badge variant="error">Likely Fake</Badge>
                            <Badge variant="secondary">Processing</Badge>
                        </div>
                        <div className="flex gap-4 items-center border-l pl-6 border-gray-100">
                            <ScoreRing score={85} size={56} />
                            <ScoreRing score={62} size={56} />
                            <ScoreRing score={24} size={56} />
                        </div>
                    </div>
                </section>

                {/* Progress Section */}
                <section className="space-y-6">
                    <h2 className="text-2xl font-semibold">Progress Visualization</h2>
                    <div className="max-w-md space-y-6">
                        <ProgressBar value={85} label="Aesthetic Match" showValue />
                        <ProgressBar value={45} label="Follower Quality" color="warning" showValue />
                        <ProgressBar value={15} label="Content Alignment" color="error" showValue />
                    </div>
                </section>

                {/* Cards Section */}
                <section className="space-y-6">
                    <h2 className="text-2xl font-semibold">Cards & Surfaces</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="card space-y-4">
                            <h3 className="text-lg font-bold">Standard Card</h3>
                            <p className="text-brand-secondary">Used for static content and containers.</p>
                            <Button variant="ghost" className="p-0 h-auto">Learn more <ChevronRight className="w-4 h-4 ml-1" /></Button>
                        </div>
                        <div className="card-hover space-y-4 group">
                            <div className="flex justify-between items-start">
                                <h3 className="text-lg font-bold">Interactive Card</h3>
                                <Check className="w-5 h-5 text-brand-success opacity-0 group-hover:opacity-100 transition-opacity" />
                            </div>
                            <p className="text-brand-secondary">Lifts on hover and adds a shadow. Used for session list items.</p>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    )
}

function ColorCard({ name, hex, className }: { name: string, hex: string, className: string }) {
    return (
        <div className={cn("rounded-2xl p-4 space-y-1", className)}>
            <div className="font-bold text-sm">{name}</div>
            <div className="text-[10px] opacity-70 font-mono tracking-wider">{hex}</div>
        </div>
    )
}
