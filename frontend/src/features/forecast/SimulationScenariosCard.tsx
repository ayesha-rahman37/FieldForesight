import React, { useState, useEffect, useRef } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { SlidersHorizontal } from 'lucide-react';
import { runScenario } from '../../api/scenario';
import type { ScenarioResponse } from '../scenario-planner/types';

interface SimulationScenariosCardProps {
  crop: string;
  region: string;
  variety?: string;
  cropping_type?: string;
  baseYield: number;
  onScenarioChange?: (
    result: ScenarioResponse | null,
    rainfallAdj: number,
    tempAdj: number
  ) => void;
}

export const SimulationScenariosCard: React.FC<SimulationScenariosCardProps> = ({
  crop,
  region,
  variety = 'HYV',
  cropping_type = 'single',
  onScenarioChange,
}) => {
  const { t } = useLanguage();
  const [rainfallAdj, setRainfallAdj] = useState<number>(0);
  const [tempAdj, setTempAdj] = useState<number>(0);

  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const requestIdRef = useRef<number>(0);

  const isSliderActive = rainfallAdj !== 0 || tempAdj !== 0;

  // Reset sliders when crop/region/variety changes
  useEffect(() => {
    setRainfallAdj(0);
    setTempAdj(0);
    onScenarioChange?.(null, 0, 0);
  }, [crop, region, variety]);

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
        onScenarioChange?.(res, rf, temp);
      }
    } catch {
      // Ignore transient errors
    }
  };

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    debounceRef.current = setTimeout(() => {
      if (isSliderActive) {
        void fetchScenarioResult(rainfallAdj, tempAdj);
      } else {
        onScenarioChange?.(null, 0, 0);
      }
    }, 250);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [rainfallAdj, tempAdj, crop, region, variety, cropping_type]);

  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="w-4 h-4 text-emerald-700" />
          <h3 className="text-[11px] font-bold uppercase tracking-[0.06em] text-slate-800">
            {t('সিমুলেশন সিনারিও', 'SIMULATION SCENARIOS')}
          </h3>
        </div>
        <span className="px-2 py-0.5 rounded-md bg-slate-50 border border-slate-200 text-[10px] font-semibold text-slate-500">
          Interactive
        </span>
      </div>

      <div className="space-y-4">
        {/* Slider 1: Rainfall Variance */}
        <div>
          <div className="flex items-center justify-between text-xs font-semibold text-slate-700 mb-1.5">
            <span>{t('বৃষ্টিপাতের পরিবর্তন', 'Rainfall Variance')}</span>
            <span className="px-2 py-0.5 rounded bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-bold">
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
              className="w-full accent-[#047857] h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-[10px] font-medium text-slate-400 mt-1">
              <span>-50%</span>
              <span>Baseline</span>
              <span>+50%</span>
            </div>
          </div>
        </div>

        {/* Slider 2: Temperature Shift */}
        <div>
          <div className="flex items-center justify-between text-xs font-semibold text-slate-700 mb-1.5">
            <span>{t('তাপমাত্রার পরিবর্তন', 'Temperature Shift')}</span>
            <span className="px-2 py-0.5 rounded bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-bold">
              {tempAdj > 0 ? `+${tempAdj}°C` : `${tempAdj}°C`}
            </span>
          </div>

          <div className="relative py-1">
            <input
              type="range"
              min="-5"
              max="5"
              step="0.5"
              value={tempAdj}
              onChange={(e) => setTempAdj(Number(e.target.value))}
              className="w-full accent-[#047857] h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-[10px] font-medium text-slate-400 mt-1">
              <span>-5°C</span>
              <span>Baseline</span>
              <span>+5°C</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
