import React from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { LanguageProvider } from './context/LanguageContext';
import { ComingSoonProvider } from './context/ComingSoonContext';
import { HomePage } from './pages/HomePage';
import { DashboardPage } from './pages/DashboardPage';
import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { SecurityArchitecturePage } from './features/security-docs/SecurityArchitecturePage';
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
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/security" element={<SecurityArchitecturePage />} />
        </Routes>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <LanguageProvider>
        <AuthProvider>
          <ComingSoonProvider>
            <AppRoutes />
          </ComingSoonProvider>
        </AuthProvider>
      </LanguageProvider>
    </BrowserRouter>
  );
};

export default App;
