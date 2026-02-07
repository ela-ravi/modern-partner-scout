import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from './components/ui/Toaster';
import { AuthProvider } from './context/AuthContext';
import { AuthGuard } from './components/auth/AuthGuard';
import LoginPage from './pages/LoginPage';
import SessionListPage from './pages/SessionListPage';
import NewSessionPage from './pages/NewSessionPage';
import DashboardPage from './pages/DashboardPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-background font-sans text-foreground">
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<LoginPage />} />

            {/* Protected Routes */}
            <Route element={<AuthGuard />}>
              <Route path="/" element={<Navigate to="/sessions" replace />} />
              <Route path="/sessions" element={<SessionListPage />} />
              <Route path="/sessions/new" element={<NewSessionPage />} />
              <Route path="/dashboard/:jobId" element={<DashboardPage />} />
            </Route>

            <Route path="*" element={<Navigate to="/sessions" replace />} />
          </Routes>
          <Toaster />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
