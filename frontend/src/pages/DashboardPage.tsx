import React, { useCallback, useEffect, useState, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Phone, Sprout, BarChart3, Satellite, ShieldAlert, Sparkles, RotateCcw } from 'lucide-react';
import { Loader } from '../components/common/Loader';
import { ErrorState } from '../components/common/ErrorState';
import { ErrorBoundary } from '../components/common/ErrorBoundary';
import { useLanguage } from '../context/LanguageContext';
import type { DashboardSection } from '../components/layout/DashboardNav';
import api from '../api/client';
import { fetchCrops, fetchRegions } from '../api/auth';
import { MyDataPanel } from '../features/personalization/MyDataPanel';
import { UserProfile } from '../features/personalization/UserProfile';
import { AdminPanel } from '../features/admin/AdminPanel';
import { ProtectedRoute } from '../components/common/ProtectedRoute';
import { useAuth } from '../context/AuthContext';
import { useChat } from '../context/ChatContext';
import type { ScenarioResponse } from '../features/scenario-planner/types';

// Dashboard Cards
import { ParametersCard } from '../features/forecast/ParametersCard';
import { ProjectedYieldCard } from '../features/forecast/ProjectedYieldCard';
import { VegetationDriverCard } from '../features/forecast/VegetationDriverCard';
import { SimulationScenariosCard } from '../features/forecast/SimulationScenariosCard';
import { RegionalContextCard } from '../features/forecast/RegionalContextCard';
import { AdvisoryRisksCard } from '../features/forecast/AdvisoryRisksCard';
import { WarningCards } from '../features/advisory/WarningCards';
import { LiveAgriNewsTicker } from '../features/forecast/LiveAgriNewsTicker';

interface DashboardPageProps {
  initialCrop?: string;
  initialRegion?: string;
}

interface PredictionData {
  prediction_id: number;
  predicted_yield: number;
  lower_bound: number;
  upper_bound: number;
  message: string;
  model_version?: string;
}

const STORAGE_KEY = 'fieldforesight_active_forecast';

interface StoredForecast {
  crop: string;
  region: string;
  variety: string;
  prediction: PredictionData;
  predictionId: number | null;
  simRainfallAdj?: number;
  simTempAdj?: number;
  scenarioResult?: ScenarioResponse | null;
}

const getStoredForecast = (): StoredForecast | null => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as StoredForecast;
  } catch {
    return null;
  }
};

const saveForecastToStorage = (data: StoredForecast) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch {
    // Ignore storage quota / access issues
  }
};

const clearForecastFromStorage = () => {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Ignore storage issues
  }
};

export const DashboardPage: React.FC<DashboardPageProps> = ({
  initialCrop = '',
  initialRegion = '',
}) => {
  const { user, loading: authLoading } = useAuth();
  const { t } = useLanguage();
  const location = useLocation();
  const { setPageContext } = useChat();

  const getTabFromURL = (): DashboardSection => {
    const params = new URLSearchParams(location.search);
    const tab = params.get('tab');
    if (tab === 'my-data' || tab === 'profile' || tab === 'admin') return tab as DashboardSection;
    return 'overview';
  };

  const savedForecast = getStoredForecast();

  const [activeSection, setActiveSection] = useState<DashboardSection>(getTabFromURL());
  const [crops, setCrops] = useState<string[]>([]);
  const [regions, setRegions] = useState<string[]>([]);

  const [selectedCrop, setSelectedCrop] = useState(initialCrop || savedForecast?.crop || '');
  const [selectedRegion, setSelectedRegion] = useState(initialRegion || savedForecast?.region || '');
  const [selectedVariety, setSelectedVariety] = useState<string>(savedForecast?.variety || 'HYV');

  const [prediction, setPrediction] = useState<PredictionData | null>(savedForecast?.prediction || null);
  const [scenarioResult, setScenarioResult] = useState<ScenarioResponse | null>(savedForecast?.scenarioResult || null);
  const [simRainfallAdj, setSimRainfallAdj] = useState<number>(savedForecast?.simRainfallAdj || 0);
  const [simTempAdj, setSimTempAdj] = useState<number>(savedForecast?.simTempAdj || 0);
  const [predictionId, setPredictionId] = useState<number | null>(savedForecast?.predictionId ?? savedForecast?.prediction?.prediction_id ?? null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [forecastStarted, setForecastStarted] = useState(Boolean(savedForecast?.prediction));

  useEffect(() => {
    setActiveSection(getTabFromURL());
  }, [location.search]);

  useEffect(() => {
    setPageContext({
      crop: selectedCrop || undefined,
      region: selectedRegion || undefined,
      predicted_yield: prediction?.predicted_yield ?? null,
    });
  }, [selectedCrop, selectedRegion, prediction, setPageContext]);

  const mountRef = useRef(false);

  const runForecast = useCallback(
    async (crop = selectedCrop, region = selectedRegion, variety = selectedVariety) => {
      if (!crop || !region) return;
      setForecastStarted(true);
      setLoading(true);
      setError(false);
      setScenarioResult(null);
      setSimRainfallAdj(0);
      setSimTempAdj(0);
      try {
        const res = await api.post<PredictionData>('/api/predict', {
          crop,
          region,
          variety,
          cropping_type: 'single',
        });
        setPrediction(res.data);
        setPredictionId(res.data.prediction_id ?? null);
        saveForecastToStorage({
          crop,
          region,
          variety,
          prediction: res.data,
          predictionId: res.data.prediction_id ?? null,
          simRainfallAdj: 0,
          simTempAdj: 0,
          scenarioResult: null,
        });
      } catch {
        setError(true);
        setPrediction(null);
        setPredictionId(null);
        clearForecastFromStorage();
      } finally {
        setLoading(false);
      }
    },
    [selectedCrop, selectedRegion, selectedVariety]
  );

  useEffect(() => {
    if (mountRef.current) return;
    mountRef.current = true;

    Promise.all([fetchCrops(), fetchRegions()])
      .then(([cList, rList]) => {
        setCrops(cList);
        setRegions(rList);
        if (initialCrop) setSelectedCrop(initialCrop);
        if (initialRegion) setSelectedRegion(initialRegion);
      })
      .catch((err) => {
        console.warn('Failed to fetch crops/regions list:', err);
      });

    // If no active prediction in localStorage, check if user has a saved prediction in account history
    if (!savedForecast && localStorage.getItem('access_token')) {
      api
        .get<any[]>('/api/predictions/history')
        .then((res) => {
          if (res.data && res.data.length > 0 && !getStoredForecast()) {
            const latest = res.data[0];
            const restoredPred: PredictionData = {
              prediction_id: latest.id,
              predicted_yield: latest.predicted_yield,
              lower_bound: latest.lower_bound,
              upper_bound: latest.upper_bound,
              message: `Restored from your account history (${latest.crop} in ${latest.region})`,
              model_version: 'persisted-history-v1',
            };
            setSelectedCrop(latest.crop);
            setSelectedRegion(latest.region);
            if (latest.variety) setSelectedVariety(latest.variety);
            setPrediction(restoredPred);
            setPredictionId(latest.id);
            setForecastStarted(true);
            saveForecastToStorage({
              crop: latest.crop,
              region: latest.region,
              variety: latest.variety || 'HYV',
              prediction: restoredPred,
              predictionId: latest.id,
              simRainfallAdj: 0,
              simTempAdj: 0,
            });
          }
        })
        .catch(() => {
          // If unauthorized or network error, ignore
        });
    }
  }, [initialCrop, initialRegion]);

  useEffect(() => {
    if (initialCrop) setSelectedCrop(initialCrop);
    if (initialRegion) setSelectedRegion(initialRegion);
  }, [initialCrop, initialRegion]);

  const baseYield = prediction?.predicted_yield ?? 0;
  const displayedYield = scenarioResult ? scenarioResult.adjusted_yield : baseYield;
  const displayedLower = scenarioResult
    ? scenarioResult.lower_bound
    : prediction?.lower_bound ?? 0;
  const displayedUpper = scenarioResult
    ? scenarioResult.upper_bound
    : prediction?.upper_bound ?? 0;
  const baselineDelta = scenarioResult ? scenarioResult.adjusted_yield - baseYield : 0;

  const handlePresetSelect = (presetCrop: string, presetRegion: string) => {
    setSelectedCrop(presetCrop);
    setSelectedRegion(presetRegion);
  };

  const handleClearForecast = () => {
    clearForecastFromStorage();
    setPrediction(null);
    setPredictionId(null);
    setScenarioResult(null);
    setSimRainfallAdj(0);
    setSimTempAdj(0);
    setForecastStarted(false);
  };

  const renderOverviewResults = () => {
    if (loading && !prediction) {
      return (
        <section className="bg-white rounded-2xl p-12 shadow-xs border border-slate-200">
          <Loader
            message={t(
              `${selectedRegion || 'নির্বাচিত'} অঞ্চলে ${selectedCrop || 'ফসলের'} পূর্বাভাস তৈরি করা হচ্ছে...`,
              `Generating forecast for ${selectedCrop || 'crop'} in ${selectedRegion || 'region'}...`
            )}
          />
        </section>
      );
    }

    if ((error || !prediction) && forecastStarted && !loading) {
      return (
        <section className="bg-white rounded-2xl p-8 shadow-xs border border-slate-200">
          <ErrorState
            message={t(
              'পূর্বাভাস গণনা করতে সমস্যা হয়েছে। অনুগ্রহ করে পুনরায় চেষ্টা করুন।',
              'Failed to calculate prediction. Please try again.'
            )}
            onRetry={() => void runForecast()}
          />
        </section>
      );
    }

    if (!prediction) {
      return (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
          {/* LEFT COLUMN (lg:col-span-4): Parameters Card */}
          <div className="lg:col-span-4 space-y-4">
            <ErrorBoundary featureName={t('পূর্বাভাস প্যারামিটার', 'Forecast Parameters')}>
              <ParametersCard
                crops={crops}
                regions={regions}
                selectedCrop={selectedCrop}
                selectedRegion={selectedRegion}
                selectedVariety={selectedVariety}
                onCropChange={(c) => setSelectedCrop(c)}
                onRegionChange={(r) => setSelectedRegion(r)}
                onVarietyChange={(v) => setSelectedVariety(v)}
                onRunForecast={() => void runForecast()}
                loading={loading}
              />
            </ErrorBoundary>
          </div>

          {/* RIGHT COLUMN (lg:col-span-8): Ready for Forecast Guide & Presets */}
          <div className="lg:col-span-8 space-y-5">
            <div className="bg-white border border-slate-200/90 rounded-2xl p-6 sm:p-8 shadow-xs relative overflow-hidden">
              <div className="absolute top-0 right-0 w-72 h-72 bg-gradient-to-bl from-emerald-100/40 via-emerald-50/20 to-transparent rounded-full blur-2xl pointer-events-none" />

              <div className="relative z-10">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-bold tracking-wide uppercase mb-3">
                  <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                  <span>{t('কৃত্রিম বুদ্ধিমত্তা ফলন প্ল্যাটফর্ম প্রস্তুত', 'AI Yield Engine Ready')}</span>
                </div>

                <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900 tracking-tight">
                  {t('কৃষি ফলন পূর্বাভাস ও ঝুঁকি মূল্যায়ন', 'Agricultural Yield Forecast & Risk Advisory')}
                </h2>

                <p className="mt-2 text-sm text-slate-600 leading-relaxed max-w-2xl">
                  {t(
                    'বাম পাশের প্যানেল থেকে আপনার কাঙ্ক্ষিত কৃষি ফসল ও অঞ্চল (জেলা) নির্বাচন করুন। এরপর "RUN FORECAST & ADVISORY" বাটনে ক্লিক করলে উপগ্রহ চিত্র (Sentinel-2 NDVI), আবহাওয়া জলবায়ু সিমুলেশন এবং বিএআরসি ও ব্রি অনুমোদিত বাস্তবসম্মত কৃষি পরামর্শ সরাসরি লোড হবে।',
                    'Select your target agricultural crop and district from the left panel. Then click "RUN FORECAST & ADVISORY" to generate live Sentinel-2 multispectral vegetation index, climate anomaly sensitivity, and BARC/BRRI-certified agronomic advisory.'
                  )}
                </p>

                {/* 3 Core Capabilities */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 mt-6">
                  <div className="bg-slate-50/80 border border-slate-200/80 rounded-xl p-4">
                    <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center mb-3">
                      <Satellite className="w-4 h-4 text-emerald-700" />
                    </div>
                    <h4 className="text-xs font-bold text-slate-900">
                      {t('স্যাটেলাইট ক্যানোপি ইনডেক্স', 'Sentinel-2 Multispectral')}
                    </h4>
                    <p className="text-[11px] text-slate-500 mt-1 leading-normal">
                      {t('উপগ্রহ চিত্র ও এনডিভিআই সূচক দ্বারা ফসলের পাতার ঘনত্ব ও স্বাস্থ্য বিশ্লেষণ।', 'Normalized Difference Vegetation Index (NDVI) monitoring.')}
                    </p>
                  </div>

                  <div className="bg-slate-50/80 border border-slate-200/80 rounded-xl p-4">
                    <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center mb-3">
                      <BarChart3 className="w-4 h-4 text-emerald-700" />
                    </div>
                    <h4 className="text-xs font-bold text-slate-900">
                      {t('১০ বছরের ফলন প্রক্ষেপণ', 'Calibrated Yield Model')}
                    </h4>
                    <p className="text-[11px] text-slate-500 mt-1 leading-normal">
                      {t('বিএআরসি ও বিবিএস তথ্যভিত্তিক ৯৫% আত্মবিশ্বাস পরিসীমা সহ ফলন হিসাব।', 'Statistical trend regressor with 95% confidence intervals.')}
                    </p>
                  </div>

                  <div className="bg-slate-50/80 border border-slate-200/80 rounded-xl p-4">
                    <div className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-800 flex items-center justify-center mb-3">
                      <ShieldAlert className="w-4 h-4 text-emerald-700" />
                    </div>
                    <h4 className="text-xs font-bold text-slate-900">
                      {t('ঝুঁকি মূল্যায়ন ও পরামর্শ', 'Agronomic Advisory')}
                    </h4>
                    <p className="text-[11px] text-slate-500 mt-1 leading-normal">
                      {t('সার, সেচ ও বালাই দমনে স্থানীয় আবহাওয়া অনুকূল বাংলা পরামর্শ।', 'Localized actionable guidance for optimal harvest output.')}
                    </p>
                  </div>
                </div>

                {/* Quick Presets */}
                <div className="mt-6 pt-5 border-t border-slate-200/70">
                  <div className="text-xs font-bold text-slate-700 mb-2.5">
                    {t('দ্রুত নির্বাচন ও নমুনা পূর্বাভাস (Quick Presets):', 'Quick Presets (Click to Select):')}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {[
                      { crop: 'Rice', region: 'Rangpur', label: t('ধান — রংপুর', 'Rice — Rangpur') },
                      { crop: 'Wheat', region: 'Dhaka', label: t('গম — ঢাকা', 'Wheat — Dhaka') },
                      { crop: 'Maize', region: 'Rajshahi', label: t('ভুট্টা — রাজশাহী', 'Maize — Rajshahi') },
                      { crop: 'Potato', region: 'Bogura', label: t('আলু — বগুড়া', 'Potato — Bogura') },
                      { crop: 'Mustard', region: 'Tangail', label: t('সরিষা — টাঙ্গাইল', 'Mustard — Tangail') },
                    ].map((preset) => (
                      <button
                        key={`${preset.crop}-${preset.region}`}
                        type="button"
                        onClick={() => handlePresetSelect(preset.crop, preset.region)}
                        className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition cursor-pointer ${
                          selectedCrop === preset.crop && selectedRegion === preset.region
                            ? 'bg-emerald-700 text-white border-emerald-700 shadow-xs'
                            : 'bg-white hover:bg-slate-100 text-slate-700 border-slate-200 shadow-2xs'
                        }`}
                      >
                        <Sprout className="w-3.5 h-3.5" />
                        <span>{preset.label}</span>
                        {selectedCrop === preset.crop && selectedRegion === preset.region && (
                          <span className="text-[10px] ml-1 bg-emerald-800 px-1.5 py-0.2 rounded text-emerald-100">
                            {t('নির্বাচিত', 'Selected')}
                          </span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* Active Forecast Summary & Reset Action Bar */}
        <div className="lg:col-span-12 bg-white/95 backdrop-blur-xs border border-emerald-900/10 rounded-xl px-4 py-2.5 flex items-center justify-between gap-3 shadow-2xs">
          <div className="flex items-center gap-2.5 flex-wrap">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-xs font-bold text-slate-800">
              {t('সক্রিয় পূর্বাভাস:', 'Active Forecast:')}{' '}
              <span className="text-emerald-850 font-extrabold">{selectedCrop}</span> ({selectedVariety}) —{' '}
              <span className="text-emerald-850 font-extrabold">{selectedRegion}</span>
            </span>
            <span className="text-[10px] bg-emerald-100 text-emerald-900 font-bold px-2 py-0.5 rounded-full border border-emerald-200">
              {displayedYield.toFixed(2)} t/ha
            </span>
            {scenarioResult && (
              <span className="text-[10px] bg-amber-50 text-amber-900 font-semibold px-2 py-0.5 rounded-full border border-amber-200">
                {t('সিমুলেশন প্রয়োগকৃত', 'Simulation Applied')} ({simRainfallAdj > 0 ? `+${simRainfallAdj}% Rain` : simRainfallAdj < 0 ? `${simRainfallAdj}% Rain` : ''} {simTempAdj !== 0 ? `${simTempAdj > 0 ? `+${simTempAdj}` : simTempAdj}°C` : ''})
              </span>
            )}
          </div>

          <button
            type="button"
            onClick={handleClearForecast}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200/80 border border-slate-200 transition cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
            <span>{t('নতুন পূর্বাভাস', 'New Forecast')}</span>
          </button>
        </div>

        {/* LEFT COLUMN (lg:col-span-4): Parameters + Simulation Scenarios + Regional Validation Note */}
        <div className="lg:col-span-4 space-y-4">
          <ErrorBoundary featureName={t('পূর্বাভাস প্যারামিটার', 'Forecast Parameters')}>
            <ParametersCard
              crops={crops}
              regions={regions}
              selectedCrop={selectedCrop}
              selectedRegion={selectedRegion}
              selectedVariety={selectedVariety}
              onCropChange={(c) => setSelectedCrop(c)}
              onRegionChange={(r) => setSelectedRegion(r)}
              onVarietyChange={(v) => setSelectedVariety(v)}
              onRunForecast={() => void runForecast()}
              loading={loading}
            />
          </ErrorBoundary>

          <ErrorBoundary featureName={t('জলবায়ু সিমুলেশন', 'Climate Simulation')}>
            <SimulationScenariosCard
              crop={selectedCrop}
              region={selectedRegion}
              variety={selectedVariety}
              baseYield={baseYield}
              onScenarioChange={(res, rf, temp) => {
                setScenarioResult(res);
                setSimRainfallAdj(rf);
                setSimTempAdj(temp);
                if (prediction) {
                  saveForecastToStorage({
                    crop: selectedCrop,
                    region: selectedRegion,
                    variety: selectedVariety,
                    prediction,
                    predictionId,
                    simRainfallAdj: rf,
                    simTempAdj: temp,
                    scenarioResult: res,
                  });
                }
              }}
            />
          </ErrorBoundary>

          <ErrorBoundary featureName={t('আঞ্চলিক প্রেক্ষাপট', 'Regional Validation')}>
            <RegionalContextCard region={selectedRegion} crop={selectedCrop} />
          </ErrorBoundary>
        </div>

        {/* CENTER COLUMN (lg:col-span-5): Projected Yield + Risk Evaluation & Advisory */}
        <div className="lg:col-span-5 space-y-4">
          <ErrorBoundary featureName={t('ফলন পূর্বাভাস', 'Projected Yield')}>
            <ProjectedYieldCard
              predictedYield={displayedYield}
              lowerBound={displayedLower}
              upperBound={displayedUpper}
              region={selectedRegion}
              baselineDelta={baselineDelta}
            />
          </ErrorBoundary>

          <ErrorBoundary featureName={t('কৃষি ঝুঁকি ও পরামর্শ', 'Advisory & Risks')}>
            <AdvisoryRisksCard
              crop={selectedCrop}
              region={selectedRegion}
              yieldVal={displayedYield}
              variety={selectedVariety}
              predictionId={predictionId}
              lowerBound={displayedLower}
              upperBound={displayedUpper}
              rainfallAdj={simRainfallAdj}
              tempAdj={simTempAdj}
            />
          </ErrorBoundary>
        </div>

        {/* RIGHT COLUMN (lg:col-span-3): Vegetation Health & Driver Attribution + Active Field Warnings */}
        <div className="lg:col-span-3 space-y-4">
          <ErrorBoundary featureName={t('স্যাটেলাইট ভেজিটেশন ইনডেক্স', 'Vegetation & Driver')}>
            <VegetationDriverCard
              region={selectedRegion}
              crop={selectedCrop}
              predictionId={predictionId}
              rainfallAdj={simRainfallAdj}
              tempAdj={simTempAdj}
            />
          </ErrorBoundary>

          {/* Active Field Risk Warnings below Vegetation Health */}
          <div id="field-warnings-section" className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-xs">
            <div className="flex items-center justify-between gap-2 mb-3.5">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-amber-600" />
                <h3 className="text-[11px] font-bold uppercase tracking-[0.06em] text-slate-800">
                  {t('মাঠ পর্যায়ের ঝুঁকি ও সতর্কতা', 'FIELD RISKS & WARNINGS')}
                </h3>
              </div>
            </div>
            <ErrorBoundary featureName={t('মাঠ সতর্কতা', 'Field Warnings')}>
              <WarningCards
                crop={selectedCrop}
                region={selectedRegion}
                variety={selectedVariety}
                yieldVal={displayedYield}
              />
            </ErrorBoundary>
          </div>

          {/* One-Line Community Benchmark Summary with Link to Yield Insights */}
          <div className="bg-white border border-slate-200/90 rounded-2xl p-4 shadow-xs flex items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2.5 text-slate-700 min-w-0">
              <span className="w-2 h-2 rounded-full bg-emerald-600 shrink-0" />
              <span className="truncate">
                {t(
                  `${selectedRegion} অঞ্চলে ${selectedCrop} এর ঐতিহাসিক ও আঞ্চলিক পরিসংখ্যান বিশ্লেষণ উপলব্ধ।`,
                  `Historical and regional community benchmark available for ${selectedCrop} in ${selectedRegion}.`
                )}
              </span>
            </div>
            <Link
              to={`/yield-insights?crop=${encodeURIComponent(selectedCrop)}&region=${encodeURIComponent(selectedRegion)}`}
              className="text-[#004741] hover:text-emerald-800 font-bold shrink-0 flex items-center gap-1 hover:underline"
            >
              <span>{t('ফলন ইনসাইট', 'Yield Insights')}</span>
              <span>→</span>
            </Link>
          </div>
        </div>
      </div>
    );
  };

  const renderSectionPanel = () => {
    switch (activeSection) {
      case 'overview':
        return (
          <div className="space-y-5">
            <ErrorBoundary featureName={t('লাইভ কৃষি সংবাদ', 'Live Agri News')}>
              <LiveAgriNewsTicker selectedDistrict={selectedRegion} />
            </ErrorBoundary>
            {!authLoading && !user ? (
              <div className="bg-white border border-emerald-100 rounded-3xl p-8 sm:p-12 text-center shadow-lg shadow-emerald-950/5 max-w-2xl mx-auto my-8">
                <div className="w-16 h-16 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center justify-center mx-auto mb-4 text-emerald-800">
                  <ShieldAlert className="w-8 h-8 text-emerald-700" />
                </div>
                <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
                  {t('এআই পূর্বাভাস ও পরামর্শ পেতে সাইন ইন করুন', 'Sign In to Access Precision Yield Forecasting')}
                </h2>
                <p className="mt-2 text-sm text-slate-600 max-w-md mx-auto leading-relaxed">
                  {t(
                    'বাংলাদেশের ৬৪টি জেলার মেটা প্রফেট ইয়েল্ড মডেল, স্যাটেলাইট এনডিভিআই এবং এআই এগ্রোনমিক পরামর্শ নিরাপদে ব্যবহারের জন্য লগইন করুন।',
                    'Access district-level Meta Prophet yield projections, satellite vegetation indices, and localized agricultural advisories securely.'
                  )}
                </p>
                <div className="mt-6 flex flex-col sm:flex-row items-center justify-center gap-3">
                  <Link
                    to="/login"
                    className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-[#047857] hover:bg-[#065f46] text-white font-semibold text-sm transition shadow-sm"
                  >
                    {t('সাইন ইন করুন', 'Sign In')}
                  </Link>
                  <Link
                    to="/signup"
                    className="w-full sm:w-auto px-6 py-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-800 font-semibold text-sm transition shadow-sm"
                  >
                    {t('নতুন একাউন্ট তৈরি করুন', 'Create Account')}
                  </Link>
                </div>
              </div>
            ) : (
              renderOverviewResults()
            )}
          </div>
        );
      case 'my-data':
        return (
          <ProtectedRoute>
            <MyDataPanel />
          </ProtectedRoute>
        );
      case 'profile':
        return (
          <ProtectedRoute>
            <UserProfile />
          </ProtectedRoute>
        );
      case 'admin':
        return (
          <ProtectedRoute requiredRole="admin">
            <AdminPanel />
          </ProtectedRoute>
        );
      default:
        return renderOverviewResults();
    }
  };

  return (
    <div
      className="min-h-screen text-slate-900 flex flex-col antialiased selection:bg-[#047857] selection:text-white"
      style={{
        fontFamily: 'var(--font-sans)',
        backgroundColor: '#F4F6F8',
      }}
    >
      {/* Main Content Area */}
      <main className="flex-1 max-w-[1400px] w-full mx-auto px-4 sm:px-6 py-5">
        {renderSectionPanel()}
      </main>

      {/* Bottom Footer */}
      <footer className="mt-auto border-t border-slate-200 bg-white py-3.5 text-xs text-slate-500">
        <div className="max-w-[1400px] mx-auto px-4 sm:px-6 flex flex-col md:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2.5 flex-wrap">
            <span className="font-bold text-slate-800">
              FieldForesight Platform © {new Date().getFullYear()}.
            </span>
            <span>
              All agricultural models calibrated for Bangladesh agro-ecological zones.
            </span>
            <span className="inline-flex items-center text-[10px] font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200">
              AI YIELD V2.4
            </span>
          </div>
          <div className="flex items-center gap-5 text-slate-500 font-medium">
            <Link className="hover:text-emerald-700 transition-colors" to="/security">
              Privacy Shield
            </Link>
            <Link className="hover:text-emerald-700 transition-colors" to="/security">
              API Documentation
            </Link>
            <span className="text-slate-300">|</span>
            <a
              href="tel:16123"
              className="inline-flex items-center gap-1.5 text-emerald-800 font-bold hover:text-emerald-900 transition-colors"
            >
              <Phone className="w-3.5 h-3.5 text-emerald-700" />
              <span>Farmer Support Helpline: 16123</span>
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default DashboardPage;
