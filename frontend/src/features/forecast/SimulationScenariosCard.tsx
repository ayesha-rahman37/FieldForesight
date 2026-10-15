import React, { useState, useEffect, useRef } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { runScenario } from '../../api/scenario';
import type { ScenarioResponse } from '../scenario-planner/types';

interface SimulationScenariosCardProps {
  crop: string;
  region: string;
  variety?: string;
  cropping_type?: string;
  baseYield: number;
}

export const SimulationScenariosCard: React.FC<SimulationScenariosCardProps> = ({
  crop,
  region,
  variety = 'HYV',
  cropping_type = 'single',
  baseYield,
}) => {
  const { t } = useLanguage();
  const [rainfallAdj, setRainfallAdj] = useState<number>(0);
  const [tempAdj, setTempAdj] = useState<number>(0);
  const [result, setResult] = useState<ScenarioResponse | null>(null);

  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const requestIdRef = useRef<number>(0);

  const isSliderActive = rainfallAdj !== 0 || tempAdj !== 0;

  const fetchScenarioResult = async (rf: number, temp: number) => {
    const currentReqId = ++requestIdRef.current;
    try {
      const res = await runScenario({
        crop,
        region,
        variety,
        cropping_type,
        rainfall_adjustment_percent: rf,
        temperature_adjustment_percent: temp * 10,
      });
      if (currentReqId === requestIdRef.current) {
        setResult(res);
      }
    } catch {
      // Keep previous or fallback calculation
    }
  };

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    debounceRef.current = setTimeout(() => {
      if (isSliderActive) {
        void fetchScenarioResult(rainfallAdj, tempAdj);
      } else {
        setResult(null);
      }
    }, 350);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [rainfallAdj, tempAdj, crop, region, variety, cropping_type]);

  const currentYield = result ? result.adjusted_yield : baseYield;
  const delta = currentYield - baseYield;
  const formattedDelta = delta >= 0 ? `+${delta.toFixed(2)}` : `${delta.toFixed(2)}`;

  return (
    <div className="bg-[#FBFAF6] border border-[#E5E1D6] rounded-2xl p-6 shadow-[0_1px_2px_rgba(0,0,0,0.04)] flex flex-col justify-between h-full space-y-6">
      <div>
        {/* Header */}
        <div className="flex items-center gap-1.5 mb-5">
          <span className="text-[#0B5D45] text-sm font-bold">❖</span>
          <h3 className="text-xs font-bold uppercase tracking-[0.06em] text-[#4A4A44]">
            {t('সিমুলেশন সিনারিও', 'SIMULATION SCENARIOS')}
          </h3>
        </div>

        <div className="space-y-6">
          {/* Slider 1: Rainfall Variance */}
          <div>
            <div className="flex items-center justify-between text-sm font-semibold text-[#1F1F1B] mb-2">
              <span>{t('বৃষ্টিপাতের পরিবর্তন', 'Rainfall variance')}</span>
              <span className="text-base font-bold text-[#1F1F1B]">
                {rainfallAdj > 0 ? `+${rainfallAdj}%` : `${rainfallAdj}%`}
              </span>
            </div>

            <div className="relative py-1">
              <input
                type="range"
                min="-50"
                max="50"
                value={rainfallAdj}
                onChange={(e) => setRainfallAdj(Number(e.target.value))}
                className="w-full accent-[#0B5D45] h-2 bg-[#D9DDD0] rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-[11px] font-medium text-slate-400 mt-1">
                <span>-50%</span>
                <span>Baseline</span>
                <span>+50%</span>
              </div>
            </div>
          </div>

          {/* Slider 2: Temperature Shift */}
          <div>
            <div className="flex items-center justify-between text-sm font-semibold text-[#1F1F1B] mb-2">
              <span>{t('তাপমাত্রার পরিবর্তন', 'Temperature shift')}</span>
              <span className="text-base font-bold text-[#1F1F1B]">
                {tempAdj > 0 ? `+${tempAdj}°C` : `${tempAdj}°C`}
              </span>
            </div>

            <div className="relative py-1">
              <input
                type="range"
                min="-5"
                max="5"
                value={tempAdj}
                onChange={(e) => setTempAdj(Number(e.target.value))}
                className="w-full accent-[#0B5D45] h-2 bg-[#D9DDD0] rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-[11px] font-medium text-slate-400 mt-1">
                <span>-5°C</span>
                <span>Baseline</span>
                <span>+5°C</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Row: Adjusted Yield */}
      <div className="pt-4 border-t border-[#E5E1D6]/80 flex items-baseline justify-between">
        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
          {t('সংশোধিত ফলন', 'ADJUSTED YIELD')}
        </span>
        <div className="flex items-baseline gap-2">
          <span className="text-xl font-extrabold text-[#1F1F1B]">
            {currentYield.toFixed(2)} t/ha
          </span>
          <span className={`text-xs font-bold ${delta >= 0 ? 'text-[#0B5D45]' : 'text-red-600'}`}>
            {formattedDelta}
          </span>
        </div>
      </div>
    </div>
  );
};
