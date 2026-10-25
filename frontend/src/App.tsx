import React from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { LanguageProvider } from './context/LanguageContext';
import { ComingSoonProvider } from './context/ComingSoonContext';
import { ChatProvider } from './context/ChatContext';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { ChatWidget } from './components/chat/ChatWidget';
import { HomePage } from './pages/HomePage';
import { DashboardPage } from './pages/DashboardPage';
import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { SecurityArchitecturePage } from './features/security-docs/SecurityArchitecturePage';
import { YieldInsightsPage } from './pages/YieldInsightsPage';
import { ProtectedRoute } from './components/common/ProtectedRoute';
import { TopNavbar } from './components/layout/TopNavbar';

const AppRoutes: React.FC = () => {
  const location = useLocation();
  const hideNavbar =
    location.pathname === '/login' ||
    location.pathname === '/signup';

  return (
    <div className="flex flex-col min-h-screen">
      {!hideNavbar && <TopNavbar />}
      <div className="flex-1">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/yield-insights"
            element={
              <ProtectedRoute>
                <YieldInsightsPage />
              </ProtectedRoute>
            }
          />
          <Route path="/security" element={<SecurityArchitecturePage />} />
        </Routes>
      </div>
      <ChatWidget />
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <LanguageProvider>
        <AuthProvider>
          <ComingSoonProvider>
            <ChatProvider>
              <ErrorBoundary isPageLevel={true}>
                <AppRoutes />
              </ErrorBoundary>
            </ChatProvider>
          </ComingSoonProvider>
        </AuthProvider>
      </LanguageProvider>
    </BrowserRouter>
  );
};

export default App;
