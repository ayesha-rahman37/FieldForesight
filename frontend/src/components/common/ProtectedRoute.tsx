import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import { ErrorState } from './ErrorState';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'admin' | 'farmer' | string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, requiredRole }) => {
  const { user, loading } = useAuth();
  const { t } = useLanguage();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <div className="w-8 h-8 border-3 border-emerald-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to={`/login?redirect=${encodeURIComponent(location.pathname + location.search)}`} replace />;
  }

  if (requiredRole && user.role !== requiredRole) {
    return (
      <ErrorState 
        message={t('অ্যাক্সেস অনুমোদিত নয়', 'Access denied.')}
      />
    );
  }

  return <>{children}</>;
};
