import React, { useEffect, useState } from 'react';
import { Card } from '../../components/common/Card';
import { Badge } from '../../components/common/Badge';
import { SkeletonLoader } from '../../components/common/SkeletonLoader';
import { ErrorState } from '../../components/common/ErrorState';
import { useLanguage } from '../../context/LanguageContext';
import api from '../../api/client';

interface RiskAlert {
  id: string;
  level: 'high' | 'medium' | 'low';
  title: string;
  description: string;
}

export const WarningCards: React.FC<{ crop: string; region: string }> = ({ crop, region }) => {
  const { t } = useLanguage();
  const [alerts, setAlerts] = useState<RiskAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const loadAlerts = async () => {
    setLoading(true);
    setError(false);
    try {
      // Group 3 API (placeholder path)
      const res = await api.get<RiskAlert[]>('/api/risk/alerts', { params: { crop, region } });
      setAlerts(res.data);
    } catch (err) {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, [crop, region]);

  if (loading) {
    return <SkeletonLoader height="80px" />;
  }

  if (error) {
    return <ErrorState message={t('ঝুঁকির সতর্কতা লোড করা যায়নি।', 'Failed to load risk alerts.')} onRetry={loadAlerts} />;
  }

  if (alerts.length === 0) {
    return null; // Or empty state
  }

  const levelColorMap = {
    high: { border: '#C62828', badge: 'red' as const, label: t('উচ্চ ঝুঁকি', 'High Risk') },
    medium: { border: '#F9A825', badge: 'yellow' as const, label: t('মাঝারি', 'Medium') },
    low: { border: '#2E7D32', badge: 'green' as const, label: t('কম', 'Low') },
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      {alerts.map((alert) => {
        const { border, badge, label } = levelColorMap[alert.level] || levelColorMap.low;
        return (
          <Card key={alert.id} style={{ borderLeft: `6px solid ${border}`, padding: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
              <Badge label={label} color={badge} />
              <h4 style={{ margin: 0, fontSize: '15px', fontWeight: 600, color: '#004741' }}>{alert.title}</h4>
            </div>
            <p style={{ margin: 0, fontSize: '14px', color: '#5A6E69' }}>{alert.description}</p>
          </Card>
        );
      })}
    </div>
  );
};
