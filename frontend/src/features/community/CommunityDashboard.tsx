import React, { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  CartesianGrid,
} from 'recharts';
import { Card } from '../../components/common/Card';
import { Loader } from '../../components/common/Loader';
import { ErrorState } from '../../components/common/ErrorState';
import { useLanguage } from '../../context/LanguageContext';
import { getCommunityAggregation } from '../../api/community';
import type { CommunityYieldAggregationResponse } from './types';

interface CommunityDashboardProps {
  region: string;
  crop: string;
  predictionValue: number;
}

export const CommunityDashboard: React.FC<CommunityDashboardProps> = ({
  region,
  crop,
  predictionValue,
}) => {
  const { t } = useLanguage();
  const [data, setData] = useState<CommunityYieldAggregationResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);

  const fetchData = async () => {
    setLoading(true);
    setError(false);
    try {
      const res = await getCommunityAggregation(region, crop, predictionValue);
      setData(res);
    } catch (err) {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (region && crop && predictionValue !== undefined) {
      fetchData();
    }
  }, [region, crop, predictionValue]);

  if (loading) {
    return (
      <Card title={t('কমিউনিটি তুলনামূলক বিশ্লেষণ', 'Community Comparative Analysis')}>
        <Loader message={t('জেলা ভিত্তিক গড় ও ঐতিহাসিক তথ্য লোড হচ্ছে...', 'Loading district average & historical trends...')} />
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Card title={t('কমিউনিটি তুলনামূলক বিশ্লেষণ', 'Community Comparative Analysis')}>
        <ErrorState
          message={t('কমিউনিটি ডেটা লোড করতে ব্যর্থ হয়েছে', 'Failed to load community data')}
          onRetry={fetchData}
        />
      </Card>
    );
  }

  const currentYear = new Date().getFullYear();
  const chartPoints = [...data.historical_trend];
  
  // Only add the current year if it's not already in the historical trend
  if (!chartPoints.find(p => p.year === currentYear)) {
    chartPoints.push({
      year: currentYear,
      yield_value: data.llm_prediction,
    });
  }

  // Sort by year just in case
  chartPoints.sort((a, b) => a.year - b.year);

  const isHealthyOrAboveAvg = data.llm_prediction >= data.district_avg_value;
  const isSingleDataPoint = chartPoints.length <= 1;

  // Single point fallback: compare LLM vs Avg as two bars
  const barData = isSingleDataPoint ? [
    { name: t('এলাকার গড়', 'District Avg'), value: data.district_avg_value, fill: '#9CA3AF' },
    { name: t('তোমার প্রেডিকশন', 'Your Prediction'), value: data.llm_prediction, fill: isHealthyOrAboveAvg ? '#4A8B7C' : '#D97706' }
  ] : [];

  return (
    <Card
      title={t('কমিউনিটি তুলনামূলক বিশ্লেষণ', 'Community Comparative Analysis')}
      subtitle={t(`${data.region} জেলায় ${data.crop} এর ফলন পরিসংখ্যান`, `Yield statistics for ${data.crop} in ${data.region} district`)}
    >
      {/* 2. Big Number Row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '24px', margin: '20px 0 16px' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '13px', color: '#5A6E69', fontWeight: 600, marginBottom: '4px' }}>
            {t('তোমার প্রেডিকশন', 'Your Prediction')}
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, color: isHealthyOrAboveAvg ? '#004741' : '#D97706', lineHeight: 1 }}>
            {data.llm_prediction.toFixed(2)}
          </div>
        </div>
        
        <div style={{
          width: '28px', height: '28px', borderRadius: '50%', backgroundColor: '#F0EDE4',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '12px', fontWeight: 700, color: '#5A6E69'
        }}>
          {isHealthyOrAboveAvg ? '≥' : '<'}
        </div>

        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '13px', color: '#5A6E69', fontWeight: 600, marginBottom: '4px' }}>
            {t('এলাকার গড়', 'District Avg')}
          </div>
          <div style={{ fontSize: '28px', fontWeight: 700, color: '#5A6E69', lineHeight: 1 }}>
            {data.district_avg_value.toFixed(2)}
          </div>
        </div>
      </div>

      {/* 5. Compact Horizontal Legend */}
      <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', marginBottom: '16px', fontSize: '13px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '10px', height: '10px', backgroundColor: '#4A8B7C', display: 'inline-block', borderRadius: '2px' }} />
          <span>{t('আপনার বর্তমান পূর্বাভাস', 'Your Current Prediction')}</span>
        </div>
        {!isSingleDataPoint && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', backgroundColor: '#004741', display: 'inline-block', borderRadius: '2px' }} />
            <span>{t('ঐতিহাসিক ধারা', 'Historical Trend')}</span>
          </div>
        )}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ width: '16px', height: '2px', borderTop: '2px dashed #9CA3AF', display: 'inline-block' }} />
          <span>{t('জেলার গড়', 'District Average')}</span>
        </div>
      </div>

      {/* 3 & 4. Chart Section */}
      <div style={{ height: 260, width: '100%' }}>
        <ResponsiveContainer width="100%" height="100%">
          {isSingleDataPoint ? (
            <BarChart data={barData} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E1D5" />
              <XAxis dataKey="name" stroke="#5A6E69" fontSize={13} axisLine={false} tickLine={false} />
              <YAxis stroke="#5A6E69" fontSize={13} axisLine={false} tickLine={false} />
              <Tooltip
                cursor={{ fill: '#F0EDE4' }}
                contentStyle={{ backgroundColor: '#FFFFFF', borderRadius: '8px', borderColor: '#D8D3C5', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
              />
              <Bar dataKey="value" radius={[4, 4, 0, 0]} barSize={60} />
            </BarChart>
          ) : (
            <LineChart data={chartPoints} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E1D5" />
              <XAxis dataKey="year" stroke="#5A6E69" fontSize={13} axisLine={false} tickLine={false} />
              <YAxis stroke="#5A6E69" fontSize={13} domain={['auto', 'auto']} axisLine={false} tickLine={false} />
              <Tooltip
                formatter={(val: any) => [typeof val === 'number' ? `${val.toFixed(2)} ${t('টন/হেক্টর', 'tons/ha')}` : `${val}`, t('ফলন', 'Yield')]}
                contentStyle={{ backgroundColor: '#FFFFFF', borderRadius: '8px', borderColor: '#D8D3C5', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
              />
              <ReferenceLine
                y={data.district_avg_value}
                stroke="#9CA3AF"
                strokeDasharray="4 4"
              />
              <Line
                type="monotone"
                dataKey="yield_value"
                stroke="#004741"
                strokeWidth={3}
                activeDot={{ r: 8, stroke: '#4A8B7C', strokeWidth: 4, fill: '#FFFFFF' }}
                dot={(props: any) => {
                  const { cx, cy, payload } = props;
                  if (payload.year === currentYear) {
                    return (
                      <g key="my-pred">
                        <circle cx={cx} cy={cy} r={12} fill="#4A8B7C" opacity={0.2} />
                        <circle cx={cx} cy={cy} r={6} fill="#4A8B7C" stroke="#FFFFFF" strokeWidth={2} />
                      </g>
                    );
                  }
                  return <circle key={payload.year} cx={cx} cy={cy} r={4} fill="#004741" stroke="none" />;
                }}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>
    </Card>
  );
};
