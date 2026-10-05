import React, { useState, useEffect, useRef } from 'react';
import { Card } from '../../components/common/Card';
import { runScenario } from '../../api/scenario';
import { useLanguage } from '../../context/LanguageContext';
import type { ScenarioResponse } from './types';

interface ScenarioSliderProps {
  crop: string;
  region: string;
  variety?: string;
  cropping_type?: string;
}

export const ScenarioSlider: React.FC<ScenarioSliderProps> = ({
  crop,
  region,
  variety = 'HYV',
  cropping_type = 'single',
}) => {
  const { t } = useLanguage();
  const [rainfallAdj, setRainfallAdj] = useState<number>(0);
  const [tempAdj, setTempAdj] = useState<number>(0);
  const [result, setResult] = useState<ScenarioResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const requestIdRef = useRef<number>(0);

  const isSliderActive = rainfallAdj !== 0 || tempAdj !== 0;

  const fetchScenarioResult = async (rf: number, temp: number) => {
    const currentReqId = ++requestIdRef.current;
    setLoading(true);
    setError(null);
    try {
      const res = await runScenario({
        crop,
        region,
        variety,
        cropping_type,
        rainfall_adjustment_percent: rf,
        temperature_adjustment_percent: temp,
      });
      if (currentReqId === requestIdRef.current) {
        setResult(res);
      }
    } catch (err) {
      if (currentReqId === requestIdRef.current) {
        setError(t('সিনারিও গণনা করতে ব্যর্থ হয়েছে', 'Failed to recalculate scenario'));
      }
    } finally {
      if (currentReqId === requestIdRef.current) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(() => {
      fetchScenarioResult(rainfallAdj, tempAdj);
    }, 400);

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [rainfallAdj, tempAdj, crop, region, variety, cropping_type]);

  const formatValue = (val: number) => (val > 0 ? `+${val}%` : `${val}%`);

  const renderSliderTrack = (
    label: string,
    value: number,
    onChange: (val: number) => void
  ) => {
    const handlePosPercent = value + 50; // 0 to 100
    const isPositive = value >= 0;
    const fillLeft = isPositive ? 50 : handlePosPercent;
    const fillWidth = Math.abs(value);
    const fillColor = isPositive ? '#4A8B7C' : '#B33A3A';

    return (
      <div>
        <div style={{ textAlign: 'center', marginBottom: '4px' }}>
          <span className="caption" style={{ fontWeight: 600, color: '#5A6E69', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            {label}
          </span>
        </div>

        <div style={{ textAlign: 'center', marginBottom: '8px' }}>
          <span style={{ fontSize: '26px', fontWeight: 700, color: isPositive && value > 0 ? '#004741' : value < 0 ? '#B33A3A' : '#004741' }}>
            {formatValue(value)}
          </span>
        </div>

        <div style={{ position: 'relative', padding: '8px 0' }}>
          <div
            style={{
              position: 'relative',
              height: '8px',
              backgroundColor: '#E5E1D5',
              borderRadius: '4px',
              width: '100%',
            }}
          >
            {/* Center tick mark at 0% */}
            <div
              style={{
                position: 'absolute',
                left: '50%',
                top: '-3px',
                bottom: '-3px',
                width: '2px',
                backgroundColor: '#7A8C88',
                transform: 'translateX(-50%)',
                zIndex: 1,
              }}
            />

            {/* Fill bar from 0% */}
            {value !== 0 && (
              <div
                style={{
                  position: 'absolute',
                  left: `${fillLeft}%`,
                  width: `${fillWidth}%`,
                  top: 0,
                  bottom: 0,
                  backgroundColor: fillColor,
                  borderRadius: isPositive ? '0 4px 4px 0' : '4px 0 0 4px',
                  zIndex: 2,
                  transition: 'all 0.05s linear',
                }}
              />
            )}
          </div>

          <input
            type="range"
            min="-50"
            max="50"
            value={value}
            onChange={(e) => onChange(Number(e.target.value))}
            style={{
              position: 'absolute',
              top: '2px',
              left: 0,
              width: '100%',
              height: '20px',
              opacity: 0,
              cursor: 'pointer',
              zIndex: 5,
              margin: 0,
            }}
          />

          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: `${handlePosPercent}%`,
              transform: 'translate(-50%, -50%)',
              width: '18px',
              height: '18px',
              borderRadius: '50%',
              backgroundColor: '#004741',
              boxShadow: '0 2px 6px rgba(0,71,65,0.3)',
              pointerEvents: 'none',
              zIndex: 4,
            }}
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px' }}>
            <span className="caption" style={{ fontSize: '11px', color: '#7A8C88' }}>-50%</span>
            <span className="caption" style={{ fontSize: '11px', color: '#7A8C88' }}>+50%</span>
          </div>
        </div>
      </div>
    );
  };

  // Determine Adjusted Stat Block Background Tint
  let adjustedBg = '#F3F4F6'; // neutral default
  let adjustedBorder = '#E5E1D5';
  if (isSliderActive && result) {
    if (result.adjusted_yield > result.original_yield) {
      adjustedBg = '#E8F4F1'; // green tint for increased yield
      adjustedBorder = '#4A8B7C';
    } else if (result.adjusted_yield < result.original_yield) {
      adjustedBg = '#FDF2F2'; // red tint for decreased yield
      adjustedBorder = '#F87171';
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* ZONE 1: Sliders Card */}
      <Card title={t('কী হতে পারতো?', 'What-if Scenario')}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', minWidth: 0 }}>
          {renderSliderTrack(t('বৃষ্টিপাত', 'Rainfall'), rainfallAdj, setRainfallAdj)}
          {renderSliderTrack(t('তাপমাত্রা', 'Temperature'), tempAdj, setTempAdj)}
        </div>
      </Card>

      {/* ZONE 2: Result Comparison Card */}
      <Card
        style={{
          opacity: isSliderActive ? 1 : 0.75,
          transition: 'all 0.3s ease',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
          <h3 style={{ fontSize: '16px' }}>{t('ফলাফল তুলনা', 'Result Comparison')}</h3>
          {loading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <div
                style={{
                  width: '14px',
                  height: '14px',
                  border: '2px solid #D8D3C5',
                  borderTop: '2px solid #004741',
                  borderRadius: '50%',
                  animation: 'spin 0.8s linear infinite',
                }}
              />
              <span className="caption" style={{ color: '#004741', fontSize: '12px' }}>
                {t('হিসাব করা হচ্ছে...', 'Recalculating...')}
              </span>
            </div>
          )}
        </div>

        {error ? (
          <p style={{ color: '#B33A3A', textAlign: 'center', fontWeight: 600, fontSize: '14px' }}>{error}</p>
        ) : !isSliderActive ? (
          /* Subdued Placeholder state before slider is moved */
          <div
            style={{
              padding: '24px 16px',
              backgroundColor: '#F9F8F5',
              borderRadius: '12px',
              border: '1.5px dashed #D8D3C5',
              textAlign: 'center',
            }}
          >
            <p style={{ color: '#5A6E69', fontSize: '14px', fontWeight: 500 }}>
              {t('স্লাইডার সরান ফলাফল দেখতে', 'Move sliders above to simulate yield outcome')}
            </p>
          </div>
        ) : (
          /* Active live comparison cards with smooth transition */
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr auto 1fr',
              alignItems: 'center',
              gap: '16px',
              transition: 'opacity 0.2s ease',
            }}
          >
            {/* Original Yield Block */}
            <div
              style={{
                padding: '16px',
                backgroundColor: '#F3F4F6',
                borderRadius: '12px',
                border: '1px solid #E5E1D5',
                textAlign: 'center',
              }}
            >
              <span className="caption" style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>
                {t('মূল ফলন', 'Original')}
              </span>
              <p style={{ fontSize: '24px', fontWeight: 600, color: '#5A6E69' }}>
                {result ? result.original_yield.toFixed(2) : '--'}
              </p>
              <span className="caption" style={{ fontSize: '11px' }}>{t('টন/হেক্টর', 'tons/ha')}</span>
            </div>

            {/* Transition Arrow */}
            <div style={{ fontSize: '22px', color: '#004741', fontWeight: 300, textAlign: 'center' }}>→</div>

            {/* Adjusted Yield Block */}
            <div
              style={{
                padding: '16px',
                backgroundColor: adjustedBg,
                borderRadius: '12px',
                border: `1px solid ${adjustedBorder}`,
                textAlign: 'center',
                transition: 'all 0.3s ease',
              }}
            >
              <span className="caption" style={{ display: 'block', marginBottom: '4px', fontWeight: 600, color: '#004741' }}>
                {t('সংশোধিত ফলন', 'Adjusted')}
              </span>
              <p style={{ fontSize: '24px', fontWeight: 700, color: '#004741' }}>
                {result ? result.adjusted_yield.toFixed(2) : '--'}
              </p>
              <span className="caption" style={{ fontSize: '11px', fontWeight: 500 }}>{t('টন/হেক্টর', 'tons/ha')}</span>
            </div>
          </div>
        )}
      </Card>

      {/* ZONE 3: Description & Compact Confidence Stat Card */}
      {isSliderActive && result && (
        <Card
          style={{
            backgroundColor: '#F0EDE4',
            border: '1px solid #D8D3C5',
            padding: '18px 20px',
            transition: 'opacity 0.3s ease',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
            {/* Info SVG Icon */}
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#004741" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: '2px' }}>
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
              {/* Message text */}
              <p style={{ fontSize: '14px', color: '#004741', fontWeight: 500, lineHeight: '1.5' }}>
                {result.message}
              </p>

              {/* Compact inline confidence range text */}
              <div style={{ fontSize: '12px', color: '#5A6E69', display: 'flex', gap: '12px', borderTop: '1px solid #D8D3C5', paddingTop: '8px', marginTop: '2px' }}>
                <span>
                  <strong>{t('সর্বনিম্ন:', 'Min:')}</strong> {result.lower_bound.toFixed(2)} {t('টন/হেক্টর', 'tons/ha')}
                </span>
                <span>•</span>
                <span>
                  <strong>{t('সর্বোচ্চ:', 'Max:')}</strong> {result.upper_bound.toFixed(2)} {t('টন/হেক্টর', 'tons/ha')}
                </span>
              </div>
            </div>
          </div>
        </Card>
      )}

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
