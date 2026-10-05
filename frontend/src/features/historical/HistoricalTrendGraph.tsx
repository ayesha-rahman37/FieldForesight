import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card } from '../../components/common/Card';
import { SkeletonLoader } from '../../components/common/SkeletonLoader';
import { ErrorState } from '../../components/common/ErrorState';
import { useLanguage } from '../../context/LanguageContext';
import api from '../../api/client';

interface HistoricalDataResponse {
  years: number[];
  rainfall: number[];
  yield: number[];
}

export const HistoricalTrendGraph: React.FC<{ crop: string; region: string }> = ({ crop, region }) => {
  const { t } = useLanguage();
  const [data, setData] = useState<{ year: number; yield: number }[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const loadData = async () => {
    setLoading(true);
    setError(false);
    try {
      const res = await api.get<HistoricalDataResponse>('/api/historical-data', { params: { crop, region } });
      const formattedData = res.data.years.map((y, i) => ({
        year: y,
        yield: res.data.yield[i]
      }));
      setData(formattedData);
    } catch (err) {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [crop, region]);

  if (loading) {
    return <SkeletonLoader height="300px" />;
  }

  if (error) {
    return <ErrorState message={t('ঐতিহাসিক ডেটা লোড করা যায়নি।', 'Failed to load historical data.')} onRetry={loadData} />;
  }

  return (
    <Card>
      <h3 style={{ fontSize: '16px', marginBottom: '16px', color: '#004741' }}>
        {t('ঐতিহাসিক ফলনের ধারা', 'Historical Yield Trend')}
      </h3>
      <div style={{ width: '100%', height: 300 }}>
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E1D5" />
            <XAxis 
              dataKey="year" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: '#5A6E69', fontSize: 12 }} 
              dy={10}
            />
            <YAxis 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: '#5A6E69', fontSize: 12 }} 
            />
            <Tooltip 
              contentStyle={{ borderRadius: '8px', border: '1px solid #D8D3C5', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}
              itemStyle={{ color: '#004741', fontWeight: 600 }}
            />
            <Line 
              type="monotone" 
              dataKey="yield" 
              name={t('ফলন (টন/হেক্টর)', 'Yield (t/ha)')}
              stroke="#004741" 
              strokeWidth={3}
              dot={{ r: 4, fill: '#004741', strokeWidth: 0 }}
              activeDot={{ r: 6, fill: '#4A8B7C', strokeWidth: 0 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};
