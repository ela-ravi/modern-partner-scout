import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

export const AuthGuard = () => {
    const { user, loading } = useAuth();
    const location = useLocation();

    if (loading) {
        // Apple-style loading spinner placeholder
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#fbfbfd]">
                <div className="animate-spin w-8 h-8 border-4 border-[#0071e3] border-t-transparent rounded-full"></div>
            </div>
        );
    }

    if (!user) {
        // Redirect to login but save the attempted location
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return <Outlet />;
};
