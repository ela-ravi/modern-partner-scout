import React from 'react';

interface AuthLayoutProps {
    children: React.ReactNode;
    title: string;
    subtitle: string;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({ children, title, subtitle }) => {
    return (
        <div className="bg-[#f5f5f7] text-[#1d1d1f] min-h-screen flex items-center justify-center p-6 font-sans">
            <div className="w-full max-w-md">
                {/* Logo Section */}
                <div className="text-center mb-8 animate-fade-in">
                    <div className="inline-flex items-center gap-3 mb-6">
                        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#0071e3] to-blue-600 flex items-center justify-center shadow-lg">
                            <svg
                                className="w-7 h-7 text-white"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                strokeWidth="2.5"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <span className="font-semibold text-2xl tracking-tight">PartnerScout</span>
                    </div>
                    <h1 className="text-3xl font-semibold tracking-tight mb-2">{title}</h1>
                    <p className="text-[#86868b]">{subtitle}</p>
                </div>

                {/* Auth Card */}
                <div className="bg-white rounded-[20px] shadow-[0_4px_24px_rgba(0,0,0,0.06),0_0_1px_rgba(0,0,0,0.1)] p-8 animate-slide-up" style={{ animationDelay: '0.1s', animationFillMode: 'both' }}>
                    {children}
                </div>

                {/* Footer */}
                <p className="text-center text-[#aeaeb2] text-sm mt-8 animate-fade-in" style={{ animationDelay: '0.2s', animationFillMode: 'both' }}>
                    By signing in, you agree to our
                    <a href="#" className="text-[#0071e3] hover:underline ml-1">Terms</a> and
                    <a href="#" className="text-[#0071e3] hover:underline ml-1">Privacy Policy</a>
                </p>
            </div>
        </div>
    );
};
