import React, { useEffect, useState } from 'react';
import { Card } from '../../components/common/Card';
import { SkeletonLoader } from '../../components/common/SkeletonLoader';
import { ErrorState } from '../../components/common/ErrorState';
import { useLanguage } from '../../context/LanguageContext';
import api from '../../api/client';

interface AdvisoryResponse {
  advisory_text: string;
  action_items: string[];
}

export const BanglaAdvisorySection: React.FC<{ crop: string; region: string; yieldVal: number }> = ({ crop, region, yieldVal }) => {
  const { t } = useLanguage();
  const [data, setData] = useState<AdvisoryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const loadAdvisory = async () => {
    setLoading(true);
    setError(false);
    try {
      // Group 3 API (placeholder path)
      const res = await api.get<AdvisoryResponse>('/api/advisory/generate', { params: { crop, region, yield: yieldVal } });
      setData(res.data);
    } catch (err) {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAdvisory();
  }, [crop, region, yieldVal]);

  if (loading) {
    return <SkeletonLoader height="150px" />;
  }

  if (error || !data) {
    return <ErrorState message={t('পরামর্শ লোড করা যায়নি।', 'Failed to load advisory.')} onRetry={loadAdvisory} />;
  }

  return (
    <Card style={{ backgroundColor: '#F9F8F6', border: '1px solid #E5E1D5' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
        <span style={{ fontSize: '24px' }}>🧑‍🌾</span>
        <h3 style={{ margin: 0, fontSize: '18px', color: '#004741' }}>
          {t('কৃষি পরামর্শ', 'Agricultural Advisory')}
        </h3>
      </div>
      <p style={{ fontSize: '16px', lineHeight: 1.6, color: '#004741', marginBottom: '16px' }}>
        {data.advisory_text}
      </p>
      {data.action_items && data.action_items.length > 0 && (
        <ul style={{ paddingLeft: '24px', margin: 0, color: '#5A6E69', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {data.action_items.map((item, i) => (
            <li key={i} style={{ fontSize: '15px' }}>{item}</li>
          ))}
        </ul>
      )}
    </Card>
  );
};
