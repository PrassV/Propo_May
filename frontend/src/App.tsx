import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AppProvider } from './context/AppContext';
import Layout from './components/layout/Layout';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import ProfilePage from './pages/ProfilePage';
import DashboardPage from './pages/DashboardPage';
import PropertiesPage from './pages/PropertiesPage';
import TenantsPage from './pages/TenantsPage';
import MaintenancePage from './pages/MaintenancePage';
import PaymentsPage from './pages/PaymentsPage';
import SettingsPage from './pages/SettingsPage';
import { useAuth } from './context/AuthContext';

const RequireAuth = ({ children }: { children: React.ReactNode }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-700"></div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  // If user hasn't set their role yet, redirect to profile setup
  if (user && !user.role) {
    return <Navigate to="/profile" />;
  }
  
  return <>{children}</>;
};

const RequireNoAuth = ({ children }: { children: React.ReactNode }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-700"></div>
      </div>
    );
  }
  
  if (user) {
    if (!user.role) {
      return <Navigate to="/profile" />;
    }
    return <Navigate to="/dashboard" />;
  }
  
  return <>{children}</>;
};

// Wrapper component to use hooks outside of the AuthContext provider
const AppWithProviders = () => {
  return (
    <AuthProvider>
      <AppProvider>
        <AppRoutes />
      </AppProvider>
    </AuthProvider>
  );
};

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<LandingPage />} />
      
      <Route 
        path="/login" 
        element={
          <RequireNoAuth>
            <LoginPage />
          </RequireNoAuth>
        } 
      />
      
      <Route 
        path="/signup" 
        element={
          <RequireNoAuth>
            <SignupPage />
          </RequireNoAuth>
        } 
      />
      
      {/* Route that requires authentication but not within the main layout */}
      <Route 
        path="/profile" 
        element={
          <RequireAuth>
            <ProfilePage />
          </RequireAuth>
        } 
      />
      
      {/* Protected routes within Layout */}
      <Route 
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/properties" element={<PropertiesPage />} />
        <Route path="/tenants" element={<TenantsPage />} />
        <Route path="/maintenance" element={<MaintenancePage />} />
        <Route path="/payments" element={<PaymentsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
      
      {/* Fallback route */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

function App() {
  return (
    <Router>
      <AppWithProviders />
    </Router>
  );
}

export default App;
