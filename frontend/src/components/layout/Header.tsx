import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from '../ui/Button';
import { useAuth } from '../../hooks/useAuth';
import { Instagram, LogOut, LayoutDashboard, History, User } from 'lucide-react';
import { cn } from '../../lib/utils';

const Header: React.FC = () => {
    const { user, signOut } = useAuth();
    const location = useLocation();

    const navItems = [
        { label: 'Sessions', path: '/sessions', icon: History },
        { label: 'Design System', path: '/design-system', icon: LayoutDashboard },
    ];

    return (
        <header className="sticky top-0 z-50 w-full glass border-b border-gray-100/50 px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-8">
                <Link to="/" className="flex items-center gap-2 group">
                    <div className="w-8 h-8 rounded-lg bg-brand-blue flex items-center justify-center text-white shadow-soft group-hover:scale-105 transition-transform">
                        <Instagram className="w-5 h-5" />
                    </div>
                    <span className="text-xl font-bold tracking-tight text-brand-text">PartnerScout</span>
                </Link>

                {user && (
                    <nav className="hidden md:flex items-center gap-1">
                        {navItems.map((item) => {
                            const Icon = item.icon;
                            const isActive = location.pathname === item.path;
                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    className={cn(
                                        "px-4 py-2 rounded-full text-sm font-medium flex items-center gap-2 transition-all",
                                        isActive
                                            ? "text-brand-blue bg-brand-blue/5"
                                            : "text-brand-secondary hover:text-brand-text hover:bg-gray-100"
                                    )}
                                >
                                    <Icon className="w-4 h-4" />
                                    {item.label}
                                </Link>
                            );
                        })}
                    </nav>
                )}
            </div>

            <div className="flex items-center gap-4">
                {user ? (
                    <div className="flex items-center gap-3">
                        <div className="hidden sm:flex flex-col items-end mr-1">
                            <span className="text-sm font-semibold text-brand-text">{user.email?.split('@')[0]}</span>
                            <span className="text-[11px] text-brand-secondary uppercase tracking-wider font-bold">Pro Account</span>
                        </div>
                        <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-brand-secondary border border-gray-200 shadow-sm">
                            <User className="w-5 h-5" />
                        </div>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => signOut()}
                            className="text-brand-error hover:bg-brand-error/5"
                        >
                            <LogOut className="w-5 h-5" />
                        </Button>
                    </div>
                ) : (
                    <Link to="/login">
                        <Button>Sign In</Button>
                    </Link>
                )}
            </div>
        </header>
    );
};

export default Header;
