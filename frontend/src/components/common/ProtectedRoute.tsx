import React from 'react';
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

  if (loading) {
    return null; // Or a full page spinner
  }

  if (!user) {
    return (
      <ErrorState 
        message={t('এই পেজটি দেখার জন্য লগইন করা প্রয়োজন।', 'You must be logged in to view this page.')}
      />
    );
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
