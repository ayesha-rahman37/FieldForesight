import React from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { Play } from 'lucide-react';

interface ParametersCardProps {
  crops: string[];
  regions: string[];
  selectedCrop: string;
  selectedRegion: string;
  selectedVariety: 'HYV' | 'Local';
  onCropChange: (crop: string) => void;
  onRegionChange: (region: string) => void;
  onVarietyChange: (variety: 'HYV' | 'Local') => void;
  onRunForecast: () => void;
  loading: boolean;
}

const ChevronDown = () => (
  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3.5 text-slate-400">
    <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
      <path d="M19 9l-7 7-7-7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  </div>
);

export const ParametersCard: React.FC<ParametersCardProps> = ({
  crops,
  regions,
  selectedCrop,
  selectedRegion,
  selectedVariety,
  onCropChange,
  onRegionChange,
  onVarietyChange,
  onRunForecast,
  loading,
}) => {
  const { t } = useLanguage();

  return (
    <div className="bg-[#FBFAF6] border border-[#E5E1D6] rounded-2xl p-6 shadow-[0_1px_2px_rgba(0,0,0,0.04)] flex flex-col justify-between h-full">
      <div>
        {/* Card Header */}
        <div className="flex items-center gap-1.5 mb-5">
          <span className="text-slate-500 font-bold text-sm">–</span>
          <h3 className="text-xs font-bold uppercase tracking-[0.06em] text-[#4A4A44]">
            {t('প্যারামিটারস', 'PARAMETERS')}
          </h3>
        </div>

        {/* Input Controls */}
        <div className="space-y-4">
          {/* Crop Selection */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-[#4A4A44] mb-1.5">
              {t('কৃষি ফসল', 'AGRICULTURAL CROP')}
            </label>
            <div className="relative">
              <select
                className="w-full h-[44px] pl-3.5 pr-10 rounded-xl border border-[#E5E1D6] bg-[#F1EEE6] text-[#1F1F1B] text-sm font-semibold focus:ring-2 focus:ring-[#0B5D45] focus:border-[#0B5D45] transition cursor-pointer appearance-none"
                value={selectedCrop}
                onChange={(e) => onCropChange(e.target.value)}
              >
                <option value="">{t('ফসল নির্বাচন করুন', 'Select Crop')}</option>
                {crops.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
              <ChevronDown />
            </div>
          </div>

          {/* Division & District */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-[#4A4A44] mb-1.5">
              {t('বিভাগ ও জেলা', 'DIVISION & DISTRICT')}
            </label>
            <div className="relative">
              <select
                className="w-full h-[44px] pl-3.5 pr-10 rounded-xl border border-[#E5E1D6] bg-[#F1EEE6] text-[#1F1F1B] text-sm font-semibold focus:ring-2 focus:ring-[#0B5D45] focus:border-[#0B5D45] transition cursor-pointer appearance-none"
                value={selectedRegion}
                onChange={(e) => onRegionChange(e.target.value)}
              >
                <option value="">{t('জেলা নির্বাচন করুন', 'Select District')}</option>
                {regions.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
              <ChevronDown />
            </div>
          </div>

          {/* Seed Variety */}
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-[#4A4A44] mb-1.5">
              {t('অনুমোদিত বীজের জাত', 'CERTIFIED SEED VARIETY')}
            </label>
            <div className="relative">
              <select
                className="w-full h-[44px] pl-3.5 pr-10 rounded-xl border border-[#E5E1D6] bg-[#F1EEE6] text-[#1F1F1B] text-sm font-semibold focus:ring-2 focus:ring-[#0B5D45] focus:border-[#0B5D45] transition cursor-pointer appearance-none"
                value={selectedVariety}
                onChange={(e) => onVarietyChange(e.target.value as 'HYV' | 'Local')}
              >
                <option value="HYV">{t('উচ্চ ফলনশীল (HYV)', 'High Yielding (HYV)')}</option>
                <option value="Local">{t('স্থানীয় জাত', 'Local Native Cultivar')}</option>
              </select>
              <ChevronDown />
            </div>
          </div>
        </div>
      </div>

      {/* Button & Telemetry Note */}
      <div className="mt-6 pt-2">
        <button
          type="button"
          disabled={!selectedCrop || !selectedRegion || loading}
          onClick={onRunForecast}
          className="w-full h-[48px] bg-[#0B5D45] hover:bg-[#084936] disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl text-[13px] font-semibold tracking-wider uppercase flex items-center justify-center gap-2 shadow.md hover:shadow-lg transition-all active:scale-[0.99]"
        >
          <Play className="w-4 h-4 fill-white text-white" />
          <span>{loading ? t('চলছে...', 'RUNNING...') : t('পূর্বাভাস মডেল চালান', 'RUN FORECAST MODEL')}</span>
        </button>

        {/* Telemetry Chips under button */}
        <div className="mt-3 text-[10px] text-slate-500 font-medium text-center flex flex-wrap justify-center gap-1.5">
          <span className="bg-[#F1EEE6] border border-[#E5E1D6] px-2 py-0.5 rounded-full">MODIS 250m</span>
          <span className="bg-[#F1EEE6] border border-[#E5E1D6] px-2 py-0.5 rounded-full">ERA5 Climate</span>
          <span className="bg-[#E6EFE6] text-[#0B5D45] border border-[#C5DCBF] px-2 py-0.5 rounded-full font-semibold">BARC Soil pH</span>
        </div>
      </div>
    </div>
  );
};
