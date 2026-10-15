import React, { useEffect, useState } from 'react';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { Skeleton } from '../../components/common/SkeletonLoader';
import { useMinDelay } from '../../hooks/useMinDelay';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import { useComingSoon } from '../../context/ComingSoonContext';
import api from '../../api/client';
import { getUserPreference } from '../../api/personalization';

export const UserProfile: React.FC = () => {
  const { user, logout } = useAuth();
  const { t } = useLanguage();
  const { openComingSoon } = useComingSoon();

  const [totalPredictions, setTotalPredictions] = useState<number | null>(null);
  const [region, setRegion] = useState<string | null>(null);
  const [rawLoading, setRawLoading] = useState<boolean>(true);

  const loading = useMinDelay(rawLoading, 300);

  useEffect(() => {
    if (user) {
      setRawLoading(true);
      Promise.all([
        api.get('/api/predictions/history').then((res) => setTotalPredictions(res.data.length)).catch(() => {}),
        getUserPreference(user.id).then((pref) => pref?.last_region && setRegion(pref.last_region)).catch(() => {}),
      ]).finally(() => {
        setRawLoading(false);
      });
    }
  }, [user]);

  if (!user) return null;

  const roleText = user.role === 'admin' ? t('অ্যাডমিন', 'Admin') : t('কৃষক', 'Farmer');
  const roleColor = user.role === 'admin' ? 'red' : 'green';
  const avatarInitial = user.username.charAt(0).toUpperCase();

  return (
    <div style={{ display: 'flex', justifyContent: 'center', width: '100%' }}>
      <Card style={{ maxWidth: '600px', width: '100%', padding: '32px' }}>
        {/* Header Section */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '32px' }}>
          <div
            style={{
              width: '70px',
              height: '70px',
              borderRadius: '50%',
              backgroundColor: '#004741',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '32px',
              fontWeight: 'bold',
              flexShrink: 0,
            }}
          >
            {avatarInitial}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '8px' }}>
            <h2 style={{ fontSize: '24px', margin: 0, fontWeight: 700, color: '#1A1A1A' }}>{user.username}</h2>
            <Badge label={roleText} color={roleColor} />
            {(user as any).created_at && (
              <span style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                {t('সদস্য:', 'Member since:')} {new Date((user as any).created_at).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>

        <hr style={{ border: 'none', borderTop: '1px solid #D8D3C5', margin: '0 0 32px 0' }} />

        {/* Info Section */}
        {loading ? (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '32px' }}>
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="space-y-1.5">
                <Skeleton width="60px" height="12px" borderRadius="4px" />
                <Skeleton width="120px" height="18px" borderRadius="6px" />
              </div>
            ))}
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '32px' }}>
            <div>
              <span style={{ display: 'block', fontSize: '12px', color: '#666', marginBottom: '4px' }}>{t('ইমেইল', 'Email')}</span>
              <p style={{ margin: 0, fontWeight: 500, fontSize: '16px', color: '#1A1A1A' }}>{user.email}</p>
            </div>
            <div>
              <span style={{ display: 'block', fontSize: '12px', color: '#666', marginBottom: '4px' }}>{t('অঞ্চল', 'Region')}</span>
              <p style={{ margin: 0, fontWeight: 500, fontSize: '16px', color: '#1A1A1A' }}>
                {region || <span style={{ color: '#999' }}>{t('নির্ধারিত নয়', 'Not set')}</span>}
              </p>
            </div>
            <div>
              <span style={{ display: 'block', fontSize: '12px', color: '#666', marginBottom: '4px' }}>{t('সর্বশেষ কার্যকলাপ', 'Last Activity')}</span>
              <p style={{ margin: 0, fontWeight: 500, fontSize: '16px', color: '#1A1A1A' }}>
                {t('আজ', 'Today')}
              </p>
            </div>
            <div>
              <span style={{ display: 'block', fontSize: '12px', color: '#666', marginBottom: '4px' }}>{t('মোট পূর্বাভাস', 'Total Predictions')}</span>
              <p style={{ margin: 0, fontWeight: 500, fontSize: '16px', color: '#1A1A1A' }}>
                {totalPredictions !== null ? totalPredictions : '0'}
              </p>
            </div>
          </div>
        )}

        <hr style={{ border: 'none', borderTop: '1px solid #D8D3C5', margin: '0 0 32px 0' }} />

        {/* Actions Section */}
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          <button
            type="button"
            onClick={() => openComingSoon(t('প্রোফাইল সম্পাদনা', 'Edit Profile'))}
            style={{
              padding: '10px 20px',
              border: '1px solid #004741',
              backgroundColor: 'transparent',
              color: '#004741',
              borderRadius: '6px',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'background-color 0.2s',
            }}
            onMouseOver={(e) => (e.currentTarget.style.backgroundColor = 'rgba(0, 71, 65, 0.05)')}
            onMouseOut={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
          >
            {t('প্রোফাইল সম্পাদনা', 'Edit Profile')}
          </button>
          <button
            type="button"
            onClick={() => openComingSoon(t('পাসওয়ার্ড পরিবর্তন', 'Change Password'))}
            style={{
              padding: '10px 20px',
              border: '1px solid #004741',
              backgroundColor: 'transparent',
              color: '#004741',
              borderRadius: '6px',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'background-color 0.2s',
            }}
            onMouseOver={(e) => (e.currentTarget.style.backgroundColor = 'rgba(0, 71, 65, 0.05)')}
            onMouseOut={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
          >
            {t('পাসওয়ার্ড পরিবর্তন', 'Change Password')}
          </button>

          <div style={{ flexGrow: 1 }} />

          <button
            type="button"
            onClick={logout}
            style={{
              padding: '10px 20px',
              border: '1px solid transparent',
              backgroundColor: 'rgba(220, 38, 38, 0.1)',
              color: '#dc2626',
              borderRadius: '6px',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'all 0.2s',
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = '#dc2626';
              e.currentTarget.style.color = 'white';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(220, 38, 38, 0.1)';
              e.currentTarget.style.color = '#dc2626';
            }}
          >
            {t('লগ আউট', 'Logout')}
          </button>
        </div>
      </Card>
    </div>
  );
};
