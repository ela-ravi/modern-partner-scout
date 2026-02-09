import React, { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { useToast } from '../../hooks/useToast';
import { Eye, EyeOff, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const LoginForm: React.FC = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const { signInWithPassword } = useAuth();
    const { toast } = useToast();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        try {
            const { error } = await signInWithPassword(email, password);
            if (error) {
                throw error;
            }
            toast({
                title: "Welcome back!",
                description: "Successfully signed in.",
                variant: "success",
            });
            navigate('/');
        } catch (err: any) {
            console.error(err);
            setError(err.message || 'Invalid credentials');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            {/* Tab Switcher - Apple style */}
            <div className="flex gap-1 p-1 bg-gray-100 rounded-2xl mb-8">
                <button className="flex-1 py-2.5 rounded-xl text-sm font-semibold bg-white text-brand-text shadow-soft transition-all">
                    Sign In
                </button>
                <button className="flex-1 py-2.5 rounded-xl text-sm font-semibold text-brand-secondary hover:text-brand-text transition-all">
                    Sign Up
                </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                    <label className="text-[13px] font-semibold text-brand-secondary ml-1">Email Address</label>
                    <Input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="name@company.com"
                        required
                        disabled={isLoading}
                    />
                </div>

                <div className="space-y-2">
                    <div className="flex items-center justify-between px-1">
                        <label className="text-[13px] font-semibold text-brand-secondary">Password</label>
                        <a href="#" className="text-[13px] text-brand-blue hover:underline font-medium">Forgot password?</a>
                    </div>
                    <div className="relative">
                        <Input
                            type={showPassword ? 'text' : 'password'}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            className="pr-12"
                            required
                            disabled={isLoading}
                        />
                        <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-4 top-1/2 -translate-y-1/2 text-brand-secondary hover:text-brand-text transition-colors"
                        >
                            {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                        </button>
                    </div>
                </div>

                <div className="flex items-center gap-3 px-1">
                    <input
                        type="checkbox"
                        id="remember"
                        className="w-4 h-4 rounded-md border-gray-300 text-brand-blue focus:ring-brand-blue/20"
                    />
                    <label htmlFor="remember" className="text-[13px] font-medium text-brand-secondary">Keep me signed in</label>
                </div>

                <Button
                    type="submit"
                    disabled={isLoading}
                    className="w-full"
                >
                    {isLoading ? 'Signing in...' : 'Sign In'}
                </Button>

                {error && (
                    <div className="p-4 bg-brand-error/5 border border-brand-error/10 rounded-2xl animate-fade-in">
                        <div className="flex items-start gap-3">
                            <AlertCircle className="text-brand-error w-5 h-5 flex-shrink-0 mt-0.5" />
                            <div>
                                <p className="text-sm font-bold text-brand-error">Authentication failed</p>
                                <p className="text-[13px] text-brand-error/80 mt-1">{error}</p>
                            </div>
                        </div>
                    </div>
                )}
            </form>

            <div className="flex items-center gap-4 my-8">
                <div className="flex-1 h-px bg-gray-100"></div>
                <span className="text-[11px] font-bold text-gray-300 uppercase tracking-widest">Or Continue With</span>
                <div className="flex-1 h-px bg-gray-100"></div>
            </div>

            <div className="grid grid-cols-2 gap-3">
                <button type="button" className="flex items-center justify-center gap-3 py-3 bg-white border border-gray-200 rounded-2xl hover:bg-gray-50 active:scale-[0.98] transition-all group">
                    <svg className="w-5 h-5" viewBox="0 0 24 24">
                        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                    </svg>
                    <span className="text-sm font-bold text-brand-text">Google</span>
                </button>
                <button type="button" className="flex items-center justify-center gap-3 py-3 bg-white border border-gray-200 rounded-2xl hover:bg-gray-50 active:scale-[0.98] transition-all group">
                    <svg className="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.604-3.369-1.341-3.369-1.341-.454-1.155-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z" />
                    </svg>
                    <span className="text-sm font-bold text-brand-text">GitHub</span>
                </button>
            </div>
        </>
    );
};
