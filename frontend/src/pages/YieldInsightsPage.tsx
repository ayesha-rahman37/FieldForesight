import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { fetchCrops, fetchRegions } from '../api/auth';
import { fetchPredictionHistory, type PredictionHistoryRaw } from '../api/dataOwnership';
import { CommunityComparisonCard } from '../features/forecast/CommunityComparisonCard';
import { Skeleton } from '../components/common/SkeletonLoader';
import api from '../api/client';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import {
  Layers,
  RefreshCw,
  CheckSquare,
  Square,
  AlertCircle,
  Sparkles,
} from 'lucide-react';

interface HistoricalDataResponse {
  years: number[];
  rainfall?: number[];
  yield: number[];
  source_type?: string;
}

export const YieldInsightsPage: React.FC = () => {
  const { t } = useLanguage();
  const location = useLocation();

  const queryParams = new URLSearchParams(location.search);
  const initialCropQuery = queryParams.get('crop') || '';
  const initialRegionQuery = queryParams.get('region') || '';

  // Dropdown lists
  const [crops, setCrops] = useState<string[]>([]);
  const [regions, setRegions] = useState<string[]>([]);

  // Selected crop & region for Historical Trends
  const [selectedCrop, setSelectedCrop] = useState<string>(initialCropQuery || 'Wheat');
  const [selectedRegion, setSelectedRegion] = useState<string>(initialRegionQuery || 'Dhaka');

  // Section 1: Historical Data
  const [historicalData, setHistoricalData] = useState<HistoricalDataResponse | null>(null);
  const [loadingHistory, setLoadingHistory] = useState<boolean>(true);
  const [historyError, setHistoryError] = useState<boolean>(false);

  // Section 2: Prediction Comparison
  const [userPredictions, setUserPredictions] = useState<PredictionHistoryRaw[]>([]);
  const [loadingPredictions, setLoadingPredictions] = useState<boolean>(true);
  const [selectedPredIds, setSelectedPredIds] = useState<number[]>([]);

  // Active Prediction Value for Community Comparison
  const [activePredYield, setActivePredYield] = useState<number>(3.25);

  // Load Crops and Regions
  useEffect(() => {
    Promise.all([fetchCrops(), fetchRegions()])
      .then(([cList, rList]) => {
        setCrops(cList);
        setRegions(rList);
        if (!initialCropQuery && cList.length > 0) {
          setSelectedCrop(cList.includes('Wheat') ? 'Wheat' : cList[0]);
        }
        if (!initialRegionQuery && rList.length > 0) {
          setSelectedRegion(rList.includes('Dhaka') ? 'Dhaka' : rList[0]);
        }
      })
      .catch((err) => {
        console.warn('Failed to load crops/regions list:', err);
      });
  }, [initialCropQuery, initialRegionQuery]);

  // Fetch Section 1: Historical Trend Data
  const loadHistoricalTrend = async (c = selectedCrop, r = selectedRegion) => {
    if (!c || !r) return;
    setLoadingHistory(true);
    setHistoryError(false);
    try {
      const res = await api.get<HistoricalDataResponse>('/api/historical-data', {
        params: { crop: c, region: r },
      });
      setHistoricalData(res.data);
    } catch {
      setHistoryError(true);
      setHistoricalData(null);
    } finally {
      setLoadingHistory(false);
    }
  };

  useEffect(() => {
    if (selectedCrop && selectedRegion) {
      void loadHistoricalTrend(selectedCrop, selectedRegion);
    }
  }, [selectedCrop, selectedRegion]);

  // Fetch Section 2: User Prediction History
  const loadUserPredictions = async () => {
    setLoadingPredictions(true);
    try {
      const list = await fetchPredictionHistory();
      setUserPredictions(list);
      if (list.length > 0) {
        // Pre-select latest up to 3 predictions
        const top3 = list.slice(0, 3).map((p) => p.id);
        setSelectedPredIds(top3);
        setActivePredYield(list[0].predicted_yield);
      }
    } catch {
      setUserPredictions([]);
    } finally {
      setLoadingPredictions(false);
    }
  };

  useEffect(() => {
    void loadUserPredictions();
  }, []);

  // Format historical chart data
  const chartData =
    historicalData?.years && historicalData?.yield
      ? historicalData.years.map((yr, idx) => ({
          year: yr,
          yield: Number(historicalData.yield[idx]?.toFixed(2) ?? 0),
          rainfall: historicalData.rainfall ? historicalData.rainfall[idx] : undefined,
        }))
      : [];

  const toggleSelectPrediction = (id: number) => {
    setSelectedPredIds((prev) => {
      if (prev.includes(id)) {
        return prev.filter((item) => item !== id);
      }
      if (prev.length >= 3) {
        // Replace oldest or cap at 3
        return [...prev.slice(1), id];
      }
      return [...prev, id];
    });
  };

  const selectedPredObjects = userPredictions.filter((p) => selectedPredIds.includes(p.id));

  return (
    <div
      className="min-h-screen text-slate-900 pb-12 antialiased selection:bg-[#004741] selection:text-white"
      style={{
        fontFamily: 'var(--font-sans)',
        backgroundColor: '#F4F6F8',
      }}
    >
      {/* Main Content */}
      <main className="max-w-[1400px] mx-auto px-4 sm:px-6 py-5 space-y-5">
        {/* Compact Title Row */}
        <div className="flex items-center justify-between gap-3 flex-wrap">
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">
              {t('ফলন ইনসাইটস ও কমিউনিটি তুলনা', 'Yield Insights & Benchmarks')}
            </h1>
            <span className="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
              <Sparkles className="w-3 h-3 text-emerald-600" />
              BBS 10-Year Series
            </span>
          </div>
          <p className="text-xs text-slate-500 hidden sm:block">
            {t(
              'বাস্তব উপাত্তভিত্তিক বাৎসরিক ফলন ট্রেন্ড এবং আঞ্চলিক কমিউনিটি পরিসংখ্যান।',
              'Real 10-year historical BBS harvest dynamics and regional benchmarks.'
            )}
          </p>
        </div>

        {/* ========================================================= */}
        {/* SECTION 1: Historical Yield Trend                         */}
        {/* ========================================================= */}
        <section className="bg-white border border-slate-200/90 rounded-2xl p-5 sm:p-7 shadow-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-100">
            <div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-[#004741]" />
                <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900">
                  {t('ঐতিহাসিক ফলন ট্রেন্ড (১০ বছরের পরিসংখ্যান)', 'Historical Yield Trend (10-Year Series)')}
                </h2>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                {t(
                  `${selectedRegion} অঞ্চলে ${selectedCrop} ফসলের বাৎসরিক ফলন বৃদ্ধি/হ্রাস সূচক (টন/হেক্টর)`,
                  `Annual yield dynamics for ${selectedCrop} in ${selectedRegion} District (ton/hectare)`
                )}
              </p>
            </div>

            {/* Crop & Region Selectors */}
            <div className="flex items-center gap-2.5 flex-wrap">
              <select
                value={selectedCrop}
                onChange={(e) => setSelectedCrop(e.target.value)}
                className="h-9 px-3 text-xs font-semibold rounded-lg border border-slate-200 bg-slate-50 text-slate-800 outline-none focus:ring-2 focus:ring-[#004741]"
              >
                {crops.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>

              <select
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
                className="h-9 px-3 text-xs font-semibold rounded-lg border border-slate-200 bg-slate-50 text-slate-800 outline-none focus:ring-2 focus:ring-[#004741]"
              >
                {regions.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>

              <button
                type="button"
                onClick={() => void loadHistoricalTrend(selectedCrop, selectedRegion)}
                className="p-2 rounded-lg border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 transition"
                title={t('পুনরায় লোড', 'Reload')}
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="mt-5">
            {loadingHistory ? (
              <div className="h-64 flex items-center justify-center">
                <Skeleton width="100%" height="240px" borderRadius="12px" />
              </div>
            ) : historyError || chartData.length === 0 ? (
              <div className="h-56 flex flex-col items-center justify-center text-center p-6 bg-slate-50 rounded-xl border border-dashed border-slate-200 space-y-2">
                <AlertCircle className="w-7 h-7 text-slate-400" />
                <p className="text-xs font-bold text-slate-700">
                  {t('পর্যাপ্ত ঐতিহাসিক তথ্য পাওয়া যায়নি।', 'Insufficient historical records available for this crop and region.')}
                </p>
                <p className="text-[11px] text-slate-500">
                  {t('অনুগ্রহ করে অন্য কোনো ফসল বা জেলা নির্বাচন করুন।', 'Please select a different crop or district.')}
                </p>
              </div>
            ) : (
              <div>
                <div className="h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                      <XAxis dataKey="year" stroke="#64748B" fontSize={11} tickLine={false} />
                      <YAxis stroke="#64748B" fontSize={11} tickLine={false} unit=" t/ha" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: '#0F172A',
                          borderRadius: '8px',
                          color: '#FFFFFF',
                          fontSize: '11px',
                          border: 'none',
                        }}
                        formatter={(val: any) => [`${val} t/ha`, t('ফলন', 'Yield')]}
                        labelFormatter={(label: any) => `${t('বছর', 'Year')}: ${label}`}
                      />
                      <Line
                        type="monotone"
                        dataKey="yield"
                        stroke="#004741"
                        strokeWidth={2.8}
                        dot={{ fill: '#004741', r: 4 }}
                        activeDot={{ r: 6, fill: '#10B981' }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
                <div className="mt-3 flex items-center justify-between text-[11px] text-slate-400">
                  <span>Source: Bangladesh Bureau of Statistics (BBS) & DAE Calibrated Series</span>
                  <span className="font-mono text-emerald-800 font-bold">
                    Latest: {chartData[chartData.length - 1]?.yield} t/ha ({chartData[chartData.length - 1]?.year})
                  </span>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* ========================================================= */}
        {/* 2-COLUMN SECTION: Prediction Comparison + Community Bench */}
        {/* ========================================================= */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* LEFT: Past Prediction Side-by-Side Comparison (lg:col-span-7) */}
          <section className="lg:col-span-7 bg-white border border-slate-200/90 rounded-2xl p-5 sm:p-7 shadow-xs space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-600" />
                  <h2 className="text-sm font-bold uppercase tracking-wider text-slate-900">
                    {t('অতীত পূর্বাভাস তুলনা (সর্বোচ্চ ৩টি নির্বাচন করুন)', 'Past Predictions Comparison (Select up to 3)')}
                  </h2>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                  {t('আপনার একাউন্টের পূর্বাভাসগুলোর তুলনামূলক বিশ্লেষণ।', 'Compare side-by-side yields across crops, regions, and seed varieties.')}
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-slate-400">
                {selectedPredIds.length}/3
              </span>
            </div>

            {loadingPredictions ? (
              <div className="space-y-3">
                <Skeleton width="100%" height="45px" borderRadius="8px" />
                <Skeleton width="100%" height="45px" borderRadius="8px" />
              </div>
            ) : userPredictions.length === 0 ? (
              <div className="py-10 text-center space-y-2 bg-slate-50 rounded-xl border border-dashed border-slate-200">
                <Layers className="w-7 h-7 text-slate-400 mx-auto" />
                <p className="text-xs font-bold text-slate-700">
                  {t('এখনো কোনো পূর্বাভাস সংরক্ষিত নেই।', 'No past predictions found in your account history.')}
                </p>
                <p className="text-[11px] text-slate-500">
                  {t('পূর্বাভাস তৈরি করতে ড্যাশবোর্ডে যান।', 'Go to the Dashboard to create your first harvest prediction.')}
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* List with Checkboxes */}
                <div className="max-h-52 overflow-y-auto space-y-2 pr-1">
                  {userPredictions.map((p) => {
                    const isSelected = selectedPredIds.includes(p.id);
                    return (
                      <div
                        key={p.id}
                        onClick={() => toggleSelectPrediction(p.id)}
                        className={`p-3 rounded-xl border text-xs flex items-center justify-between gap-3 cursor-pointer transition ${
                          isSelected
                            ? 'bg-[#E6F0ED] border-[#004741] text-[#004741] font-bold shadow-2xs'
                            : 'bg-slate-50/70 border-slate-200 text-slate-700 hover:bg-white'
                        }`}
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          {isSelected ? (
                            <CheckSquare className="w-4 h-4 text-[#004741] shrink-0" />
                          ) : (
                            <Square className="w-4 h-4 text-slate-400 shrink-0" />
                          )}
                          <div className="truncate">
                            <span className="font-extrabold">{p.crop}</span> ({p.variety || 'HYV'}) —{' '}
                            <span>{p.region}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2.5 shrink-0">
                          <span className="font-extrabold text-sm">{p.predicted_yield.toFixed(2)} t/ha</span>
                          <span className="text-[10px] text-slate-400">
                            {p.created_at ? p.created_at.substring(0, 10) : ''}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Side-by-Side Comparison Cards */}
                {selectedPredObjects.length >= 2 ? (
                  <div className="pt-3 border-t border-slate-200">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-3">
                      {t('পাশাপাশি তুলনামূলক চিত্র (Side-by-Side Table)', 'Side-by-Side Comparison Table')}
                    </h3>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                      {selectedPredObjects.map((item) => (
                        <div
                          key={item.id}
                          className="bg-slate-50 border border-slate-200/90 rounded-xl p-3.5 space-y-2 text-xs"
                        >
                          <div className="font-extrabold text-slate-900 border-b border-slate-200 pb-1.5 flex justify-between">
                            <span>{item.crop}</span>
                            <span className="text-[10px] text-[#004741] font-bold px-1.5 py-0.2 bg-emerald-100 rounded">
                              {item.variety || 'HYV'}
                            </span>
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-400 block">{t('অঞ্চল / জেলা', 'District')}</span>
                            <span className="font-bold text-slate-800">{item.region}</span>
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-400 block">{t('পূর্বাভাসকৃত ফলন', 'Predicted Yield')}</span>
                            <span className="font-black text-base text-[#004741]">{item.predicted_yield.toFixed(2)} t/ha</span>
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-400 block">{t('আস্থা পরিসীমা (Bounds)', 'Range')}</span>
                            <span className="text-[11px] font-mono text-slate-600 font-semibold">
                              {item.lower_bound?.toFixed(2) ?? '—'} - {item.upper_bound?.toFixed(2) ?? '—'}
                            </span>
                          </div>
                          <div className="text-[10px] text-slate-400 pt-1 border-t border-slate-200">
                            {item.created_at ? item.created_at.substring(0, 10) : 'Recent'}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-slate-500 italic pt-2">
                    {t(
                      'কমপক্ষে ২টি বা ৩টি পূর্বাভাসে টিক চিহ্ন দিন পাশাপাশি তুলনা দেখার জন্য।',
                      'Check at least 2 or 3 predictions above to view side-by-side comparison.'
                    )}
                  </p>
                )}
              </div>
            )}
          </section>

          {/* RIGHT: Community Comparison & Regional Distribution (lg:col-span-5) */}
          <section className="lg:col-span-5 space-y-4">
            <CommunityComparisonCard
              region={selectedRegion}
              crop={selectedCrop}
              predictionValue={activePredYield}
            />

            <div className="bg-[#FAF9F5] border border-slate-200 rounded-2xl p-4 text-xs text-slate-600 leading-relaxed">
              <span className="font-bold text-slate-800 block mb-1">
                {t('আঞ্চলিক পরিসংখ্যান সূত্র:', 'Regional Benchmark Methodology:')}
              </span>
              {t(
                'বাংলাদেশ কৃষি সম্প্রসারণ অধিদপ্তর (DAE) ও নার্স (NARS) পার্টনারদের ১০ বছরের ঐতিহাসিক গড় ফলন থেকে এই জেলার গড় মান হিসাব করা হয়েছে।',
                'District averages are computed from 10-year historical BBS harvest archives and DAE agro-ecological monitoring data.'
              )}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default YieldInsightsPage;
