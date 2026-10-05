import React from 'react';
import { Card } from './Card';
import { useLanguage } from '../../context/LanguageContext';
import { VegetationHealthIndicator } from '../../features/vegetation-health/VegetationHealthIndicator';

interface PredictionResult {
  prediction_id: number;
  predicted_yield: number;
  lower_bound: number;
  upper_bound: number;
  message?: string;
}

interface PredictionResultCardProps {
  prediction: PredictionResult;
  crop: string;
  region: string;
}

export const LocalValidationNote: React.FC<{ region: string; years?: number }> = ({ region, years = 5 }) => {
  const { t } = useLanguage();
  return (
    <div style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '6px',
      backgroundColor: 'rgba(74, 139, 124, 0.1)',
      padding: '6px 12px',
      borderRadius: '4px',
      marginTop: '12px'
    }}>
      <span style={{ color: '#4A8B7C' }}>ℹ️</span>
      <span className="caption" style={{ color: '#004741', fontWeight: 500, fontSize: '12px' }}>
        {t(`এই পূর্বাভাস ${region}-র গত ${years} বছরের ডেটার ভিত্তিতে তৈরি`, `This prediction is based on ${years} years of data from ${region}`)}
      </span>
    </div>
  );
};

export const PredictionResultCard: React.FC<PredictionResultCardProps> = ({ prediction, crop, region }) => {
  const { t } = useLanguage();
  const fullMaxVal = Math.ceil(prediction.upper_bound + 0.5);
  const lowerPercent = Math.max(0, Math.min(100, (prediction.lower_bound / fullMaxVal) * 100));
  const upperPercent = Math.max(0, Math.min(100, (prediction.upper_bound / fullMaxVal) * 100));
  const segmentWidth = upperPercent - lowerPercent;

  return (
    <Card className="interactive-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <span className="caption" style={{ textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>
            {region} • {crop}
          </span>
          <h1 style={{ marginTop: '4px', fontSize: '24px' }}>
            {t('আনুমানিক ফলন', 'Estimated Yield')}
          </h1>
        </div>
        <VegetationHealthIndicator region={region} />
      </div>

      <div style={{ marginTop: '24px' }}>
        <p style={{ fontSize: '32px', fontWeight: 700, color: '#004741', lineHeight: 1 }}>
          {prediction.predicted_yield.toFixed(2)}{' '}
          <span style={{ fontSize: '16px', fontWeight: 400, color: '#5A6E69' }}>{t('টন/হেক্টর', 'tons/ha')}</span>
        </p>
      </div>

      <div style={{ marginTop: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '6px' }}>
          <span className="caption" style={{ fontWeight: 500, color: '#5A6E69' }}>
            {t('সর্বনিম্ন ও সর্বোচ্চ সীমা', 'Confidence Range')}
          </span>
          <span style={{ fontSize: '14px', fontWeight: 600, color: '#004741' }}>
            {prediction.lower_bound.toFixed(2)} - {prediction.upper_bound.toFixed(2)}
          </span>
        </div>
        <div style={{ position: 'relative', height: '6px', backgroundColor: '#E5E1D5', borderRadius: '3px', width: '100%', overflow: 'hidden' }}>
          <div style={{
            position: 'absolute',
            left: `${lowerPercent}%`,
            width: `${segmentWidth}%`,
            top: 0,
            bottom: 0,
            backgroundColor: '#4A8B7C',
            borderRadius: '3px',
          }} />
        </div>
      </div>

      <LocalValidationNote region={region} />
    </Card>
  );
};
