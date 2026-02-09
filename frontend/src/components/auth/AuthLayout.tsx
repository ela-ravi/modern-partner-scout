import React from 'react';

interface AuthLayoutProps {
    children: React.ReactNode;
    title: string;
    subtitle: string;
}

export const AuthLayout: React.FC<AuthLayoutProps> = ({ children, title, subtitle }) => {
    return (
        <div className="bg-brand-background text-brand-text min-h-screen flex items-center justify-center p-6">
            <div className="w-full max-w-md">
                {/* Logo Section */}
                <div className="text-center mb-8 animate-fade-in">
                    <div className="inline-flex items-center gap-3 mb-6">
                        <div className="w-12 h-12 rounded-2xl bg-brand-blue flex items-center justify-center shadow-medium text-white">
                            <svg
                                className="w-7 h-7"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                                strokeWidth="2.5"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                        </div>
                        <span className="font-bold text-2xl tracking-tight">PartnerScout</span>
                    </div>
                    <h1 className="text-3xl font-bold tracking-tight mb-2">{title}</h1>
                    <p className="text-brand-secondary font-medium">{subtitle}</p>
                </div>

                {/* Auth Card */}
                <div className="card animate-slide-up p-8" style={{ animationDelay: '0.1s', animationFillMode: 'both' }}>
                    {children}
                </div>

                {/* Footer */}
                <p className="text-center text-brand-secondary text-sm mt-8 animate-fade-in" style={{ animationDelay: '0.2s', animationFillMode: 'both' }}>
                    By signing in, you agree to our
                    <a href="#" className="text-brand-blue hover:underline ml-1 font-medium">Terms</a> and
                    <a href="#" className="text-brand-blue hover:underline ml-1 font-medium">Privacy Policy</a>
                </p>
            </div>
        </div>
    );
};
