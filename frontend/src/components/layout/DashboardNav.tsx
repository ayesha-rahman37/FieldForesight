import React from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useAuth } from '../../context/AuthContext';
import { LayoutDashboard, Database, User as UserIcon, ShieldAlert } from 'lucide-react';

export type DashboardSection = 'overview' | 'my-data' | 'profile' | 'admin';

interface DashboardNavProps {
  activeSection: DashboardSection;
  onSelect: (section: DashboardSection) => void;
}

export const DashboardNav: React.FC<DashboardNavProps> = ({ activeSection, onSelect }) => {
  const { t } = useLanguage();
  const { user } = useAuth();

  const links: { id: DashboardSection; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: t('ড্যাশবোর্ড', 'Dashboard'), icon: <LayoutDashboard size={20} /> },
    { id: 'my-data', label: t('আমার ডেটা', 'My Data'), icon: <Database size={20} /> },
    { id: 'profile', label: t('প্রোফাইল', 'User Profile'), icon: <UserIcon size={20} /> },
  ];

  if (user && user.role === 'admin') {
    links.push({ id: 'admin', label: t('অ্যাডমিন প্যানেল', 'Admin Panel'), icon: <ShieldAlert size={20} /> });
  }

  return (
    <nav style={{
      width: '100%',
      backgroundColor: '#FFFFFF',
      borderBottom: '1px solid #D8D3C5',
      padding: '0 40px',
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
      position: 'sticky',
      top: '72px', // Height of the TopNavbar
      zIndex: 10,
      overflowX: 'auto',
    }}>
      <div style={{
        maxWidth: '1200px',
        width: '100%',
        margin: '0 auto',
        display: 'flex',
        gap: '8px',
        padding: '16px 0'
      }}>
        {links.map((link) => {
          const isActive = activeSection === link.id;
          return (
            <button
              key={link.id}
              onClick={() => onSelect(link.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 16px',
                borderRadius: '8px',
                backgroundColor: isActive ? '#E8F4F1' : 'transparent',
                color: isActive ? '#004741' : '#5A6E69',
                fontWeight: isActive ? 600 : 500,
                border: 'none',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                transition: 'all 0.2s ease',
              }}
            >
              {link.icon}
              {link.label}
            </button>
          );
        })}
      </div>
    </nav>
  );
};
