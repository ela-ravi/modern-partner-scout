import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { Search, Bell, LogOut, User as UserIcon, Settings } from 'lucide-react';

interface DashboardLayoutProps {
    children: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
    const { user, signOut } = useAuth();
    const location = useLocation();
    const [isProfileOpen, setIsProfileOpen] = React.useState(false);

    const isActive = (path: string) => location.pathname === path;

    return (
        <div className="flex flex-col min-h-screen bg-[#fbfbfd]">
            {/* Header */}
            <header className="sticky top-0 z-50 bg-[#fbfbfd]/80 backdrop-blur-xl border-b border-[rgba(0,0,0,0.06)]">
                <div className="max-w-6xl mx-auto px-6">
                    <div className="flex items-center justify-between h-14">
                        {/* Logo */}
                        <Link to="/sessions" className="flex items-center gap-2.5">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#0071e3] to-blue-600 flex items-center justify-center">
                                <svg className="w-4.5 h-4.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
                                </svg>
                            </div>
                            <span className="font-semibold text-lg tracking-tight text-[#1d1d1f]">PartnerScout</span>
                        </Link>

                        {/* Navigation */}
                        <nav className="hidden md:flex items-center gap-8">
                            {/* Dashboard link usually points to the specific job, but here maybe global dashboard or just sessions */}
                            {/* For now keeping as design, but linking Dashboard to latest session or generic analytics could be future work */}
                            <Link
                                to="/sessions"
                                className={`text-sm font-medium transition-colors ${isActive('/sessions') ? 'text-[#1d1d1f]' : 'text-[#86868b] hover:text-[#1d1d1f]'}`}
                            >
                                Sessions
                            </Link>
                            {/* Placeholder for Analytics */}
                            <a href="#" className="text-sm font-medium text-[#86868b] hover:text-[#1d1d1f] transition-colors">
                                Analytics
                            </a>
                        </nav>

                        {/* Actions */}
                        <div className="flex items-center gap-4">
                            <button className="p-2 rounded-full hover:bg-[#f5f5f7] transition-colors">
                                <Search className="w-5 h-5 text-[#86868b]" />
                            </button>
                            <button className="relative p-2 rounded-full hover:bg-[#f5f5f7] transition-colors">
                                <Bell className="w-5 h-5 text-[#86868b]" />
                            </button>

                            {/* User Menu */}
                            <div className="relative">
                                <button
                                    onClick={() => setIsProfileOpen(!isProfileOpen)}
                                    className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center cursor-pointer hover:ring-2 hover:ring-[#0071e3]/30 transition-all"
                                >
                                    <span className="text-white text-sm font-semibold">{user?.email?.[0].toUpperCase()}</span>
                                </button>

                                {isProfileOpen && (
                                    <>
                                        <div
                                            className="fixed inset-0 z-40"
                                            onClick={() => setIsProfileOpen(false)}
                                        ></div>
                                        <div className="absolute right-0 top-12 bg-white rounded-2xl shadow-xl border border-[rgba(0,0,0,0.06)] min-w-[220px] py-2 z-50">
                                            <div className="px-4 py-3 border-b border-[rgba(0,0,0,0.06)]">
                                                <p className="font-semibold text-sm text-[#1d1d1f]">User</p>
                                                <p className="text-[#86868b] text-xs truncate">{user?.email}</p>
                                            </div>
                                            <div className="py-1">
                                                <a href="#" className="flex items-center gap-3 px-4 py-2.5 text-sm text-[#1d1d1f] hover:bg-[#f5f5f7] transition-colors">
                                                    <UserIcon className="w-4 h-4 text-[#86868b]" />
                                                    Profile Settings
                                                </a>
                                                <a href="#" className="flex items-center gap-3 px-4 py-2.5 text-sm text-[#1d1d1f] hover:bg-[#f5f5f7] transition-colors">
                                                    <Settings className="w-4 h-4 text-[#86868b]" />
                                                    Preferences
                                                </a>
                                            </div>
                                            <div className="border-t border-[rgba(0,0,0,0.06)] pt-1 mt-1">
                                                <button
                                                    onClick={() => signOut()}
                                                    className="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-[#ff3b30] hover:bg-[#ff3b30]/5 transition-colors text-left"
                                                >
                                                    <LogOut className="w-4 h-4" />
                                                    Sign Out
                                                </button>
                                            </div>
                                        </div>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 w-full mx-auto">
                {children}
            </main>

            {/* Footer */}
            <footer className="py-8 mt-auto border-t border-[rgba(0,0,0,0.06)]">
                <div className="max-w-6xl mx-auto px-6">
                    <p className="text-center text-[#aeaeb2] text-sm">
                        © 2026 PartnerScout AI
                    </p>
                </div>
            </footer>
        </div>
    );
};
