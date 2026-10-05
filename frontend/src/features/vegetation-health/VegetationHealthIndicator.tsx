import React, { useEffect, useState } from 'react';
import { getNDVI } from '../../api/ndvi';
import { useLanguage } from '../../context/LanguageContext';
import type { NDVIResponse } from './types';

interface VegetationHealthIndicatorProps {
  region: string;
}

export const VegetationHealthIndicator: React.FC<VegetationHealthIndicatorProps> = ({ region }) => {
  const { t } = useLanguage();
  const [data, setData] = useState<NDVIResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);

  const fetchNDVI = async () => {
    if (!region) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(false);
    try {
      const res = await getNDVI(region);
      setData(res);
    } catch (err) {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNDVI();
  }, [region]);

  if (loading) {
    return (
      <div
        style={{
          padding: '12px 16px',
          backgroundColor: '#FFFFFF',
          borderRadius: '8px',
          border: '1px solid #E5E1D5',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '10px',
        }}
      >
        <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: '#E5E1D5' }} />
        <span className="caption">{t('ভেজিটেশন ডাটা লোড হচ্ছে...', 'Loading vegetation data...')}</span>
      </div>
    );
  }

  // Null or unavailable data state with relevant icon
  if (error || !data || data.ndvi_value === null || data.ndvi_value === undefined) {
    return (
      <div
        style={{
          padding: '12px 16px',
          backgroundColor: '#FFFFFF',
          borderRadius: '8px',
          border: '1px dashed #D8D3C5',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '10px',
        }}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span style={{ fontSize: '13px', fontWeight: 600, color: '#6B7280' }}>
            {t('তথ্য এখনো পাওয়া যায়নি', 'Data not yet available')}
          </span>
          <span className="caption" style={{ color: '#9CA3AF', fontSize: '11px' }}>
            {t(`${region} অঞ্চল`, `${region} Region`)}
          </span>
        </div>
      </div>
    );
  }

  let dotColor = '#9CA3AF';

  const statusLower = data.vegetation_status.toLowerCase();
  let statusText = data.vegetation_status;

  if (statusLower.includes('healthy') || statusLower.includes('ভাল') || statusLower.includes('উত্তম')) {
    dotColor = '#4A8B7C';
    statusText = t('উত্তম ভেজিটেশন', 'Healthy Vegetation');
  } else if (statusLower.includes('moderate') || statusLower.includes('মাঝারি')) {
    dotColor = '#D97706';
    statusText = t('মাঝারি ভেজিটেশন', 'Moderate Vegetation');
  } else if (statusLower.includes('poor') || statusLower.includes('খারাপ')) {
    dotColor = '#B33A3A';
    statusText = t('দুর্বল ভেজিটেশন', 'Poor Vegetation');
  }

  const formattedDate = data.computed_at
    ? new Date(data.computed_at).toLocaleDateString(t('bn-BD', 'en-US'), {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    : '';

  // Calculate ring properties (NDVI ranges from -1 to 1, we map to 0-100% for the ring)
  const normalizedNdvi = Math.max(0, (data.ndvi_value + 1) / 2);
  const radius = 20;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - normalizedNdvi * circumference;

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
      {/* Circular Progress Ring */}
      <div style={{ position: 'relative', width: '56px', height: '56px' }}>
        <svg width="56" height="56" viewBox="0 0 56 56">
          <circle
            cx="28" cy="28" r={radius}
            fill="none" stroke="#E5E1D5" strokeWidth="6"
          />
          <circle
            cx="28" cy="28" r={radius}
            fill="none" stroke={dotColor} strokeWidth="6"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            transform="rotate(-90 28 28)"
            style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
          />
        </svg>
        <div style={{
          position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '12px', fontWeight: 700, color: dotColor
        }}>
          {Math.round(data.ndvi_value * 100) / 100}
        </div>
      </div>

      {/* Stacked Text */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
        <span style={{ fontSize: '16px', fontWeight: 600, color: '#004741' }}>
          {statusText}
        </span>
        <span style={{ fontSize: '13px', color: '#5A6E69' }}>
          NDVI: {data.ndvi_value.toFixed(2)}
        </span>
        {formattedDate && (
          <span style={{ fontSize: '11px', color: '#9CA3AF' }}>
            {t(`সর্বশেষ আপডেট: ${formattedDate}`, `Updated: ${formattedDate}`)}
          </span>
        )}
      </div>
    </div>
  );
};
