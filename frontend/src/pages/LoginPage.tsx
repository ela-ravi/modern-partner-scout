import React from 'react';
import { AuthLayout } from '../components/auth/AuthLayout';
import { LoginForm } from '../components/auth/LoginForm';

const LoginPage: React.FC = () => {
    return (
        <AuthLayout
            title="Welcome back"
            subtitle="Sign in to discover your ideal brand partners"
        >
            <LoginForm />
        </AuthLayout>
    );
};

export default LoginPage;
