import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from '../components/layout/Header';

const AppLayout: React.FC = () => {
    return (
        <div className="min-h-screen bg-brand-background flex flex-col">
            <Header />
            <main className="flex-1 flex flex-col items-center">
                <div className="max-w-7xl w-full">
                    <Outlet />
                </div>
            </main>

            {/* Dynamic Background Elements - Apple style subtle gradients */}
            <div className="fixed top-0 left-0 w-full h-full pointer-events-none overflow-hidden -z-10">
                <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-brand-blue/5 rounded-full blur-[120px]" />
                <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-brand-success/5 rounded-full blur-[120px]" />
            </div>
        </div>
    );
};

export default AppLayout;
