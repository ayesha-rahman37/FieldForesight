import React, { useEffect, useState } from 'react';
import { Card } from '../../components/common/Card';
import { ErrorState } from '../../components/common/ErrorState';
import { Skeleton } from '../../components/common/SkeletonLoader';
import { useMinDelay } from '../../hooks/useMinDelay';
import { useLanguage } from '../../context/LanguageContext';
import type { ExplainabilityResponse } from './types';
import { getExplainability } from '../../api/explainability';

interface ExplainabilityPanelProps {
  predictionId: number;
}

const factorTranslationsBn: Record<string, string> = {
  rainfall: 'বৃষ্টিপাত',
  soil: 'মাটি ও এনডিভিআই',
  temperature: 'তাপমাত্রা',
};

const factorTranslationsEn: Record<string, string> = {
  rainfall: 'Rainfall',
  soil: 'Soil & NDVI',
  temperature: 'Temperature',
};

const BAR_HEIGHT = 16;
const ROW_GAP = 18;
const LABEL_WIDTH = 105;
const PERCENT_WIDTH = 44;
const BAR_AREA_PADDING = 8;

export const ExplainabilityPanel: React.FC<ExplainabilityPanelProps> = ({ predictionId }) => {
  const { t, language } = useLanguage();
  const [data, setData] = useState<ExplainabilityResponse | null>(null);
  const [rawLoading, setRawLoading] = useState<boolean>(true);
  const [error, setError] = useState<boolean>(false);

  const loading = useMinDelay(rawLoading, 300);

  const fetchExplanation = async () => {
    setRawLoading(true);
    setError(false);
    try {
      const res = await getExplainability(predictionId);
      setData(res);
    } catch {
      setError(true);
    } finally {
      setRawLoading(false);
    }
  };

  useEffect(() => {
    if (predictionId) {
      fetchExplanation();
    }
  }, [predictionId]);

  if (loading) {
    return (
      <Card title={t('কেন এই পূর্বাভাস?', 'Why this prediction?')} style={{ height: 'auto' }}>
        <div className="py-4 space-y-4">
          {[80, 60, 45].map((w, idx) => (
            <div key={idx} className="flex gap-3 items-center">
              <Skeleton width="90px" height="14px" borderRadius="4px" />
              <Skeleton width={`${w}%`} height={`${BAR_HEIGHT}px`} borderRadius="6px" />
            </div>
          ))}
        </div>
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Card title={t('কেন এই পূর্বাভাস?', 'Why this prediction?')} style={{ height: 'auto' }}>
        <ErrorState
          featureName={t('পূর্বাভাস ব্যাখ্যা', 'Prediction Explanation')}
          message={t('ব্যাখ্যা লোড করা যায়নি', 'Failed to load explanation')}
          onRetry={fetchExplanation}
        />
      </Card>
    );
  }

  const factorMap = language === 'bn' ? factorTranslationsBn : factorTranslationsEn;

  const chartData = Object.entries(data.contributions)
    .map(([factor, percent]) => {
      const normalizedKey = factor.toLowerCase().trim();
      return {
        factorKey: normalizedKey,
        factorLabel: factorMap[normalizedKey] || (factor.charAt(0).toUpperCase() + factor.slice(1).toLowerCase()),
        percent: Number(percent),
      };
    })
    .sort((a, b) => b.percent - a.percent);

  const topFactor = data.top_factor.toLowerCase();
  const numRows = chartData.length;
  const svgHeight = numRows * (BAR_HEIGHT + ROW_GAP) - ROW_GAP + BAR_HEIGHT;

  return (
    <Card
      title={t('কেন এই পূর্বাভাস?', 'Why this prediction?')}
      style={{ height: 'auto' }}
    >
      {/* Custom horizontal bar chart */}
      <div style={{ marginTop: '12px', marginBottom: '4px', width: '100%' }}>
        <svg
          width="100%"
          viewBox={`0 0 400 ${svgHeight}`}
          preserveAspectRatio="xMidYMid meet"
          style={{ display: 'block', overflow: 'visible' }}
        >
          {chartData.map((entry, i) => {
            const isTop = entry.factorKey === topFactor;
            const barColor = isTop ? '#004741' : '#4A8B7C';
            const barOpacity = isTop ? 1 : 0.7;
            const barMaxWidth = 400 - LABEL_WIDTH - PERCENT_WIDTH - BAR_AREA_PADDING * 2;
            const barWidth = (entry.percent / 100) * barMaxWidth;
            const rowY = i * (BAR_HEIGHT + ROW_GAP);
            const barX = LABEL_WIDTH + BAR_AREA_PADDING;
            const textY = rowY + BAR_HEIGHT / 2 + 1;

            return (
              <g key={entry.factorKey}>
                {/* Background track */}
                <rect
                  x={LABEL_WIDTH + BAR_AREA_PADDING}
                  y={rowY}
                  width={barMaxWidth}
                  height={BAR_HEIGHT}
                  rx={BAR_HEIGHT / 2}
                  fill="#EDE9DF"
                />

                {/* Filled bar */}
                <rect
                  x={barX}
                  y={rowY}
                  width={barWidth}
                  height={BAR_HEIGHT}
                  rx={BAR_HEIGHT / 2}
                  fill={barColor}
                  opacity={barOpacity}
                  style={{ transition: 'width 0.4s ease' }}
                />

                {/* Factor label */}
                <text
                  x={LABEL_WIDTH - 10}
                  y={textY}
                  textAnchor="end"
                  dominantBaseline="middle"
                  fontSize={isTop ? '13' : '12'}
                  fontWeight={isTop ? '700' : '500'}
                  fill={isTop ? '#004741' : '#5A6E69'}
                  fontFamily="Inter, sans-serif"
                >
                  {entry.factorLabel}
                </text>

                {/* Percentage label */}
                <text
                  x={barX + barWidth + 7}
                  y={textY}
                  textAnchor="start"
                  dominantBaseline="middle"
                  fontSize={isTop ? '13' : '12'}
                  fontWeight={isTop ? '700' : '500'}
                  fill={isTop ? '#004741' : '#5A6E69'}
                  fontFamily="Inter, sans-serif"
                >
                  {entry.percent.toFixed(1)}%
                </text>

                {/* Top factor indicator */}
                {isTop && (
                  <circle
                    cx={barX - 8}
                    cy={rowY + BAR_HEIGHT / 2}
                    r={4}
                    fill="#004741"
                  />
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Bengali summary callout */}
      <div
        style={{
          marginTop: '12px',
          padding: '10px 14px',
          backgroundColor: '#EEF7F5',
          borderLeft: '3px solid #4A8B7C',
          borderRadius: '0 8px 8px 0',
        }}
      >
        <p style={{ fontSize: '13px', color: '#004741', lineHeight: '1.6', margin: 0, fontWeight: 450 }}>
          {data.summary_text_bn}
        </p>
      </div>
    </Card>
  );
};
