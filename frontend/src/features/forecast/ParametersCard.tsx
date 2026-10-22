import React, { useEffect, useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { Play, Clock, Hourglass, Zap, Check, Satellite } from 'lucide-react';
import api from '../../api/client';

export interface VarietyItem {
  id: number;
  crop: string;
  variety_code: string;
  name_en: string;
  name_bn: string;
  variety_type: string;
  yield_coefficient: number;
  potential_yield_min?: number;
  potential_yield_max?: number;
  maturity_days?: number;
  season?: string;
  stress_tolerance?: string;
  description_bn?: string;
  description_en?: string;
  is_recommended: boolean;
}

interface ParametersCardProps {
  crops: string[];
  regions: string[];
  selectedCrop: string;
  selectedRegion: string;
  selectedVariety: string;
  onCropChange: (crop: string) => void;
  onRegionChange: (region: string) => void;
  onVarietyChange: (variety: string) => void;
  onRunForecast: () => void;
  loading: boolean;
}

const CROP_LABELS: Record<string, string> = {
  Rice: 'Rice (ধান) — Oryza sativa',
  Wheat: 'Wheat (গম) — Triticum aestivum',
  Maize: 'Maize (ভুট্টা) — Zea mays',
  Potato: 'Potato (আলু) — Solanum tuberosum',
  Jute: 'Jute (পাট) — Corchorus olitorius',
  Mustard: 'Mustard (সরিষা) — Brassica juncea',
  Lentil: 'Lentil (মসুর) — Lens culinaris',
};

const REGION_AGROZONE_LABELS: Record<string, string> = {
  Dhaka: 'Dhaka (ঢাকা) — Central Agrozone',
  Rangpur: 'Rangpur (রংপুর) — Northern Agrozone',
  Rajshahi: 'Rajshahi (রাজশাহী) — Barind Agrozone',
  Bogura: 'Bogura (বগুড়া) — Karatoya Floodplain',
  Dinajpur: 'Dinajpur (দিনাজপুর) — Himalayan Piedmont',
  Mymensingh: 'Mymensingh (ময়মনসিংহ) — Old Brahmaputra',
  Sylhet: 'Sylhet (সিলেট) — Surma-Kushiara Basin',
  Khulna: 'Khulna (খুলনা) — Ganges Tidal Floodplain',
  Barishal: 'Barishal (বরিশাল) — Southern Delta Zone',
  Chattogram: 'Chattogram (চট্টগ্রাম) — Coastal Chittagong',
  Cumilla: 'Cumilla (কুমিল্লা) — Meghna Estuarine',
  Jashore: 'Jashore (যশোর) — High Ganges River',
  Faridpur: 'Faridpur (ফরিদপুর) — Low Ganges Basin',
  Pabna: 'Pabna (পাবনা) — Lower Purnabhaba',
  Sirajganj: 'Sirajganj (সিরাজগঞ্জ) — Active Brahmaputra',
  Tangail: 'Tangail (টাঙ্গাইল) — Young Brahmaputra',
  Munshiganj: 'Munshiganj (মুন্সীগঞ্জ) — Arial Bil Basin',
};

const ChevronDown = () => (
  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-slate-400">
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
  const [varieties, setVarieties] = useState<VarietyItem[]>([]);
  const [loadingVarieties, setLoadingVarieties] = useState<boolean>(false);

  useEffect(() => {
    let active = true;
    if (!selectedCrop) {
      setVarieties([]);
      return;
    }

    setLoadingVarieties(true);
    api
      .get<VarietyItem[]>('/api/varieties', { params: { crop: selectedCrop } })
      .then((res) => {
        if (active) {
          setVarieties(res.data);
          if (res.data.length > 0) {
            const hasMatch = res.data.some(
              (v) => v.variety_code === selectedVariety || v.name_en === selectedVariety
            );
            if (!hasMatch) {
              onVarietyChange(res.data[0].variety_code);
            }
          }
        }
      })
      .catch((err) => {
        console.warn('Failed to fetch dynamic varieties:', err);
      })
      .finally(() => {
        if (active) setLoadingVarieties(false);
      });

    return () => {
      active = false;
    };
  }, [selectedCrop]);

  const activeVarietyInfo = varieties.find(
    (v) => v.variety_code === selectedVariety || v.name_en === selectedVariety
  );

  return (
    <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs">
      {/* Card Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-600" />
          <h3 className="text-[11px] font-bold uppercase tracking-[0.06em] text-slate-800">
            {t('প্যারামিটারস ও জাত নির্বাচন', 'PARAMETERS & VARIETY SELECTION')}
          </h3>
        </div>
        <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          STEP 01
        </span>
      </div>

      {/* Input Controls */}
      <div className="space-y-3.5">
        {/* Crop Selection */}
        <div>
          <label className="block text-[11px] font-semibold text-slate-600 mb-1">
            Agricultural Crop <span className="text-slate-400 font-normal">(কৃষি ফসল)</span>
          </label>
          <div className="relative">
            <select
              className="w-full h-10 pl-3 pr-9 rounded-lg border border-slate-200 bg-slate-50/70 text-slate-900 text-xs font-semibold focus:ring-2 focus:ring-emerald-600 focus:border-emerald-600 transition cursor-pointer appearance-none"
              value={selectedCrop}
              onChange={(e) => onCropChange(e.target.value)}
            >
              <option value="">{t('ফসল নির্বাচন করুন', 'Select Crop')}</option>
              {crops.map((c) => (
                <option key={c} value={c}>
                  {CROP_LABELS[c] || c}
                </option>
              ))}
            </select>
            <ChevronDown />
          </div>
        </div>

        {/* Division & District */}
        <div>
          <label className="block text-[11px] font-semibold text-slate-600 mb-1">
            Division & District <span className="text-slate-400 font-normal">(বিভাগ ও জেলা)</span>
          </label>
          <div className="relative">
            <select
              className="w-full h-10 pl-3 pr-9 rounded-lg border border-slate-200 bg-slate-50/70 text-slate-900 text-xs font-semibold focus:ring-2 focus:ring-emerald-600 focus:border-emerald-600 transition cursor-pointer appearance-none"
              value={selectedRegion}
              onChange={(e) => onRegionChange(e.target.value)}
            >
              <option value="">{t('জেলা নির্বাচন করুন', 'Select District')}</option>
              {regions.map((r) => (
                <option key={r} value={r}>
                  {REGION_AGROZONE_LABELS[r] || `${r} — Regional Agrozone`}
                </option>
              ))}
            </select>
            <ChevronDown />
          </div>
        </div>

        {/* Certified Seed Variety */}
        <div>
          <div className="flex items-center justify-between mb-1">
            <label className="block text-[11px] font-semibold text-slate-600">
              Certified Seed Variety <span className="text-slate-400 font-normal">(অনুমোদিত বীজ জাত)</span>
            </label>
            {loadingVarieties && (
              <span className="text-[10px] text-emerald-700 animate-pulse font-medium">
                {t('লোড হচ্ছে...', 'loading...')}
              </span>
            )}
          </div>
          <div className="relative">
            <select
              className="w-full h-10 pl-3 pr-9 rounded-lg border border-slate-200 bg-slate-50/70 text-slate-900 text-xs font-semibold focus:ring-2 focus:ring-emerald-600 focus:border-emerald-600 transition cursor-pointer appearance-none"
              value={selectedVariety}
              onChange={(e) => onVarietyChange(e.target.value)}
            >
              {varieties.length > 0 ? (
                varieties.map((v) => (
                  <option key={v.variety_code} value={v.variety_code}>
                    {v.name_en} — {v.name_bn || 'বাংলাদেশ কৃষি গবেষণা'}
                  </option>
                ))
              ) : (
                <>
                  <option value="HYV">Standard HYV — বাংলাদেশ কৃষি গবেষণা</option>
                  <option value="Local">Local Native Cultivar — দেশি জাত</option>
                </>
              )}
            </select>
            <ChevronDown />
          </div>

          {/* Selected Variety Trait Preview Badge */}
          {selectedCrop && (
            <div className="mt-3 p-2.5 rounded-xl bg-emerald-50/80 border border-emerald-200/90 flex items-center justify-between gap-2">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="w-8 h-8 rounded-lg bg-emerald-100 border border-emerald-200 flex items-center justify-center text-emerald-800 shrink-0">
                  <Hourglass className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <div className="text-xs font-bold text-slate-900 truncate">
                    {activeVarietyInfo ? activeVarietyInfo.name_en : `BARI / BRRI (${selectedVariety})`}
                  </div>
                  <div className="flex items-center gap-1.5 text-[10px] text-emerald-800 font-medium mt-0.5">
                    <span className="inline-flex items-center gap-1">
                      <Clock className="w-3 h-3 text-emerald-600" />
                      Maturity: {activeVarietyInfo?.maturity_days ?? 105}d
                    </span>
                    <span>•</span>
                    <span className="font-semibold">
                      x{(activeVarietyInfo?.yield_coefficient ?? 1.0).toFixed(2)} coeff
                    </span>
                  </div>
                </div>
              </div>
              <span className="px-2 py-0.5 rounded bg-emerald-600/15 text-[10px] font-bold text-emerald-900 border border-emerald-300/80 shrink-0">
                {activeVarietyInfo?.variety_type || 'HYV'}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Primary Action Button */}
      <div className="mt-4">
        <button
          type="button"
          disabled={!selectedCrop || !selectedRegion || loading}
          onClick={onRunForecast}
          className="w-full h-10 bg-[#047857] hover:bg-[#065F46] disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg text-xs font-bold tracking-wider uppercase flex items-center justify-center gap-2 shadow-xs transition-all active:scale-[0.99]"
        >
          <Play className="w-3.5 h-3.5 fill-white text-white" />
          <span>{loading ? t('চলছে...', 'RUNNING...') : t('পূর্বাভাস ও ঝুঁকি বিশ্লেষণ', 'RUN FORECAST & ADVISORY')}</span>
        </button>

        {/* Telemetry Chips under button */}
        <div className="mt-3 flex flex-wrap justify-center gap-1.5 text-[10px] font-semibold text-slate-600">
          <span className="inline-flex items-center gap-1 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded-md">
            <Zap className="w-3 h-3 text-amber-500 fill-amber-500" />
            Groq Llama 3.3
          </span>
          <span className="inline-flex items-center gap-1 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded-md">
            <Check className="w-3 h-3 text-emerald-600" />
            BRRI / BARI Certified
          </span>
          <span className="inline-flex items-center gap-1 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded-md">
            <Satellite className="w-3 h-3 text-blue-600" />
            MODIS NDVI & Risk Alert
          </span>
        </div>
      </div>
    </div>
  );
};
