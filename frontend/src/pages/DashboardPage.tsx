import React, { useCallback, useEffect, useState, useRef } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Loader } from '../components/common/Loader';
import { ErrorState } from '../components/common/ErrorState';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import type { DashboardSection } from '../components/layout/DashboardNav';
import api from '../api/client';
import { fetchCrops, fetchRegions } from '../api/auth';
import { MyDataPanel } from '../features/personalization/MyDataPanel';
import { UserProfile } from '../features/personalization/UserProfile';
import { AdminPanel } from '../features/admin/AdminPanel';
import { ProtectedRoute } from '../components/common/ProtectedRoute';

// New Componentized Dashboard Cards
import { ParametersCard } from '../features/forecast/ParametersCard';
import { ProjectedYieldCard } from '../features/forecast/ProjectedYieldCard';
import { VegetationDriverCard } from '../features/forecast/VegetationDriverCard';
import { SimulationScenariosCard } from '../features/forecast/SimulationScenariosCard';
import { RegionalContextCard } from '../features/forecast/RegionalContextCard';
import { AdvisoryRisksCard } from '../features/forecast/AdvisoryRisksCard';
import { CommunityComparisonCard } from '../features/forecast/CommunityComparisonCard';

interface DashboardPageProps {
  initialCrop?: string;
  initialRegion?: string;
}

type VarietyApi = 'HYV' | 'Local';

interface PredictionData {
  prediction_id: number;
  predicted_yield: number;
  lower_bound: number;
  upper_bound: number;
  message: string;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ initialCrop = '', initialRegion = '' }) => {
  const { t } = useLanguage();
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const getTabFromURL = (): DashboardSection => {
    const params = new URLSearchParams(location.search);
    const tab = params.get('tab');
    if (tab === 'my-data' || tab === 'profile' || tab === 'admin') return tab as DashboardSection;
    return 'overview';
  };

  const [activeSection, setActiveSection] = useState<DashboardSection>(getTabFromURL());
  const [crops, setCrops] = useState<string[]>([]);
  const [regions, setRegions] = useState<string[]>([]);

  const [selectedCrop, setSelectedCrop] = useState(initialCrop);
  const [selectedRegion, setSelectedRegion] = useState(initialRegion);
  const [selectedVariety, setSelectedVariety] = useState<VarietyApi>('HYV');

  const [prediction, setPrediction] = useState<PredictionData | null>(null);
  const [predictionId, setPredictionId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);
  const [lastUpdated, setLastUpdated] = useState('');
  const [forecastStarted, setForecastStarted] = useState(false);

  useEffect(() => {
    setActiveSection(getTabFromURL());
  }, [location.search]);

  const mountRef = useRef(false);

  useEffect(() => {
    if (mountRef.current) return;
    mountRef.current = true;

    Promise.all([fetchCrops(), fetchRegions()])
      .then(([cList, rList]) => {
        setCrops(cList);
        setRegions(rList);
        const defaultCrop = initialCrop || (cList.length > 0 ? cList[0] : 'Rice');
        const defaultRegion = initialRegion || (rList.length > 0 ? rList[0] : 'Rangpur');
        setSelectedCrop(defaultCrop);
        setSelectedRegion(defaultRegion);
        void runForecast(defaultCrop, defaultRegion, 'HYV');
      })
      .catch((err) => {
        console.error(err);
        // Fallback defaults
        setSelectedCrop('Rice');
        setSelectedRegion('Rangpur');
        void runForecast('Rice', 'Rangpur', 'HYV');
      });
  }, []);

  useEffect(() => {
    if (initialCrop) setSelectedCrop(initialCrop);
    if (initialRegion) setSelectedRegion(initialRegion);
  }, [initialCrop, initialRegion]);

  const handleSectionSelect = (section: DashboardSection) => {
    setActiveSection(section);
    navigate(`/dashboard?tab=${section}`);
  };

  const runForecast = useCallback(
    async (crop = selectedCrop, region = selectedRegion, variety = selectedVariety) => {
      if (!crop || !region) return;
      setForecastStarted(true);
      setLoading(true);
      setError(false);
      try {
        const res = await api.post<PredictionData>('/api/predict', {
          crop,
          region,
          variety,
          cropping_type: 'single',
        });
        setPrediction(res.data);
        setPredictionId(res.data.prediction_id ?? null);
        setLastUpdated(new Date().toLocaleTimeString());
      } catch {
        setError(true);
        setPrediction(null);
        setPredictionId(null);
      } finally {
        setLoading(false);
      }
    },
    [selectedCrop, selectedRegion, selectedVariety]
  );

  const applyPreset = (crop: string, region: string, variety: VarietyApi = 'HYV') => {
    setSelectedCrop(crop);
    setSelectedRegion(region);
    setSelectedVariety(variety);
    setActiveSection('overview');
    navigate('/dashboard?tab=overview');
    void runForecast(crop, region, variety);
  };

  const renderEmptyState = () => (
    <section className="bg-[#FBFAF6] rounded-2xl p-6 sm:p-12 shadow-[0_1px_2px_rgba(0,0,0,0.04)] border border-[#E5E1D6] relative overflow-hidden">
      <div className="max-w-2xl mx-auto text-center">
        <div className="relative mx-auto w-20 h-20 mb-6 flex items-center justify-center">
          <div className="w-20 h-20 rounded-full bg-[#0B5D45] flex items-center justify-center text-white shadow-lg">
            <svg className="w-10 h-10 text-emerald-200" fill="none" stroke="currentColor" strokeWidth="1.8" viewBox="0 0 24 24">
              <path d="M7 20h10" />
              <path d="M10 20c5.5-2.5.8-6.4 3-10" />
              <path d="M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4-.1 5.5.8z" />
              <path d="M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4.2.9-4.9 2z" />
            </svg>
          </div>
        </div>
        <h2 className="text-2xl sm:text-3xl font-extrabold text-[#1F1F1B] tracking-tight mb-3">
          {t('আপনার প্রথম পূর্বাভাস শুরু করুন', 'Start your first yield prediction')}
        </h2>
        <p className="text-slate-600 text-sm sm:text-base leading-relaxed mb-8 max-w-lg mx-auto">
          {t(
            'উপরের রিবন থেকে ফসল, অঞ্চল ও জাত নির্বাচন করে «Run Forecast Model» চাপুন।',
            'Select your crop, division, and seed variety from the top ribbon, then click Run Forecast Model.'
          )}
        </p>

        {/* Top ribbon inputs for quick launch if empty */}
        <div className="bg-[#F1EEE6] p-4 rounded-xl border border-[#E5E1D6] mb-8 max-w-xl mx-auto">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
            <div>
              <label className="block text-[10px] font-bold uppercase text-[#4A4A44] mb-1">{t('ফসল', 'Crop')}</label>
              <select
                className="w-full text-xs font-semibold h-9 rounded-lg border-[#E5E1D6] bg-white text-[#1F1F1B]"
                value={selectedCrop}
                onChange={(e) => setSelectedCrop(e.target.value)}
              >
                <option value="">{t('নির্বাচন', 'Select')}</option>
                {crops.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-[10px] font-bold uppercase text-[#4A4A44] mb-1">{t('জেলা', 'District')}</label>
              <select
                className="w-full text-xs font-semibold h-9 rounded-lg border-[#E5E1D6] bg-white text-[#1F1F1B]"
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
              >
                <option value="">{t('নির্বাচন', 'Select')}</option>
                {regions.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>
            <div className="flex items-end">
              <button
                type="button"
                disabled={!selectedCrop || !selectedRegion || loading}
                onClick={() => void runForecast()}
                className="w-full h-9 bg-[#0B5D45] text-white text-xs font-bold rounded-lg uppercase hover:bg-[#084936] transition disabled:opacity-50"
              >
                {t('পূর্বাভাস চালান', 'Run Model')}
              </button>
            </div>
          </div>
        </div>

        <div className="relative flex py-2 items-center mb-6">
          <div className="flex-grow border-t border-[#E5E1D6]" />
          <span className="flex-shrink mx-4 text-[11px] font-bold tracking-wider uppercase text-slate-400">
            {t('দ্রুত টেমপ্লেট', 'Or quick-launch a verified regional template')}
          </span>
          <div className="flex-grow border-t border-[#E5E1D6]" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-left">
          <PresetCard
            badge={t('উচ্চ ফলন', 'High Yield')}
            badgeClass="bg-emerald-100 text-emerald-800"
            title={t('বগুড়া বোরো', 'Bogura Boro Harvest')}
            desc="Rice • Rangpur • HYV"
            metaLeft="98.4% Acc."
            onClick={() => applyPreset('Rice', 'Rangpur', 'HYV')}
          />
          <PresetCard
            badge={t('গম', 'Blast Resistant')}
            badgeClass="bg-amber-100 text-amber-800"
            title={t('দিনাজপুর গম', 'Dinajpur Wheat Model')}
            desc="Wheat • Rangpur • HYV"
            metaLeft="Rabi Cycle"
            onClick={() => applyPreset('Wheat', 'Rangpur', 'HYV')}
          />
          <PresetCard
            badge={t('আর্দ্র', 'Moisture Calibrated')}
            badgeClass="bg-blue-100 text-blue-800"
            title={t('শেরপুর হাওর', 'Sherpur Haor Basin')}
            desc="Rice • Dhaka • Local"
            metaLeft="Early Warning"
            onClick={() => applyPreset('Rice', 'Dhaka', 'Local')}
          />
        </div>
      </div>
    </section>
  );

  const renderOverviewResults = () => {
    if (!forecastStarted) {
      return renderEmptyState();
    }
    if (loading) {
      return (
        <section className="bg-[#FBFAF6] rounded-2xl p-12 shadow-[0_1px_2px_rgba(0,0,0,0.04)] border border-[#E5E1D6]">
          <Loader
            message={t(
              `${selectedRegion} অঞ্চলে ${selectedCrop} এর পূর্বাভাস তৈরি করা হচ্ছে...`,
              `Generating forecast for ${selectedCrop} in ${selectedRegion}...`
            )}
          />
        </section>
      );
    }
    if (error || !prediction) {
      return (
        <section className="bg-[#FBFAF6] rounded-2xl p-8 shadow-[0_1px_2px_rgba(0,0,0,0.04)] border border-[#E5E1D6]">
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

    return (
      /* Newly Restructured Reference Layout (Row 1, Row 2, Row 3) */
      <div className="space-y-5">
        {/* ROW 1: 3 Columns on Desktop (lg:grid-cols-12) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch">
          {/* Card 1: PARAMETERS CARD (lg:col-span-3, order-2 on mobile) */}
          <div className="order-2 lg:order-none lg:col-span-3">
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
          </div>

          {/* Card 2: PROJECTED YIELD CARD (lg:col-span-6, order-1 on mobile) */}
          <div className="order-1 lg:order-none lg:col-span-6">
            <ProjectedYieldCard
              predictedYield={prediction.predicted_yield}
              lowerBound={prediction.lower_bound}
              upperBound={prediction.upper_bound}
              region={selectedRegion}
            />
          </div>

          {/* Card 3: VEGETATION HEALTH & DRIVER ATTRIBUTION CARD (lg:col-span-3, order-3 on mobile) */}
          <div className="order-3 lg:order-none lg:col-span-3">
            <VegetationDriverCard
              region={selectedRegion}
              predictionId={predictionId}
            />
          </div>
        </div>

        {/* ROW 2: 3 Columns on Desktop (lg:grid-cols-12) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-stretch">
          {/* Card 1: SIMULATION SCENARIOS (lg:col-span-4, order-4 on mobile) */}
          <div className="order-4 lg:order-none lg:col-span-4">
            <SimulationScenariosCard
              crop={selectedCrop}
              region={selectedRegion}
              variety={selectedVariety}
              baseYield={prediction.predicted_yield}
            />
          </div>

          {/* Card 2: REGIONAL CONTEXT CARD (lg:col-span-5, order-6 on mobile) */}
          <div className="order-6 lg:order-none lg:col-span-5">
            <RegionalContextCard region={selectedRegion} />
          </div>

          {/* Card 3: ADVISORY & RISKS CARD (lg:col-span-3, order-5 on mobile) */}
          <div className="order-5 lg:order-none lg:col-span-3">
            <AdvisoryRisksCard
              crop={selectedCrop}
              region={selectedRegion}
              yieldVal={prediction.predicted_yield}
            />
          </div>
        </div>

        {/* ROW 3: FULL-WIDTH COMMUNITY COMPARISON (order-7 on mobile) */}
        <div className="order-7 lg:order-none w-full">
          <CommunityComparisonCard
            region={selectedRegion}
            crop={selectedCrop}
            predictionValue={prediction.predicted_yield}
          />
        </div>
      </div>
    );
  };

  const renderSectionPanel = () => {
    switch (activeSection) {
      case 'overview':
        return renderOverviewResults();
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

  const tabBtnClass = (active: boolean) =>
    active
      ? 'inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold bg-[#0B5D45] text-white shadow-sm transition-all'
      : 'inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium text-[#4A4A44] hover:text-[#0B5D45] hover:bg-[#F1EEE6] transition-colors';

  return (
    <div
      className="min-h-screen text-[#1F1F1B] flex flex-col antialiased selection:bg-[#0B5D45] selection:text-white"
      style={{
        fontFamily: '"Plus Jakarta Sans", "Inter", sans-serif',
        backgroundColor: '#F1EEE6',
      }}
    >
      <main className="flex-1 max-w-[1280px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-1 border-b border-[#E5E1D6]">
          <div className="inline-flex p-1 bg-[#FBFAF6] rounded-2xl shadow-[0_1px_2px_rgba(0,0,0,0.04)] border border-[#E5E1D6] flex-wrap">
            <button type="button" className={tabBtnClass(activeSection === 'overview')} onClick={() => handleSectionSelect('overview')}>
              {t('ড্যাশবোর্ড ওয়ার্কস্পেস', 'Dashboard Workspace')}
            </button>
            <button type="button" className={tabBtnClass(activeSection === 'my-data')} onClick={() => handleSectionSelect('my-data')}>
              {t('টেলিমেট্রি আর্কাইভ', 'Telemetry Archives')}
            </button>
            <button type="button" className={tabBtnClass(activeSection === 'profile')} onClick={() => handleSectionSelect('profile')}>
              {t('কৃষক প্রোফাইল', 'Farmer Profile')}
            </button>
            {user?.role === 'admin' && (
              <button type="button" className={tabBtnClass(activeSection === 'admin')} onClick={() => handleSectionSelect('admin')}>
                Admin
              </button>
            )}
          </div>
          <div className="flex items-center gap-3 self-end sm:self-center">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#E6EFE6] border border-[#C5DCBF] text-[11px] font-bold text-[#0B5D45]">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Sentinel-2 Multispectral Synced</span>
              {lastUpdated && (
                <span className="text-slate-400 font-normal">| {lastUpdated}</span>
              )}
            </div>
          </div>
        </div>

        {renderSectionPanel()}
      </main>

      <footer className="mt-auto border-t border-[#E5E1D6] bg-[#FBFAF6] py-5 text-xs text-slate-500 font-medium">
        <div className="max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 flex-wrap">
            <span>FieldForesight Platform © {new Date().getFullYear()}. All agricultural models calibrated for Bangladesh agro-ecological zones.</span>
            <span className="inline-flex items-center text-[10px] font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
              AI YIELD V2.4
            </span>
          </div>
          <div className="flex items-center gap-6 text-slate-500">
            <Link className="hover:text-[#0B5D45] transition-colors" to="/security">
              Privacy Shield
            </Link>
            <Link className="hover:text-[#0B5D45] transition-colors" to="/security">
              API Documentation
            </Link>
            <span className="hover:text-[#0B5D45] transition-colors">Farmer Support Helpline (16123)</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

const PresetCard: React.FC<{
  badge: string;
  badgeClass: string;
  title: string;
  desc: string;
  metaLeft: string;
  onClick: () => void;
}> = ({ badge, badgeClass, title, desc, metaLeft, onClick }) => (
  <button
    type="button"
    onClick={onClick}
    className="group p-4 rounded-xl border border-[#E5E1D6] hover:border-[#0B5D45] bg-[#F1EEE6]/50 hover:bg-white hover:shadow-md transition-all text-left flex flex-col justify-between"
  >
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${badgeClass}`}>{badge}</span>
        <span className="text-xs text-slate-400 group-hover:text-[#0B5D45] font-bold transition">→</span>
      </div>
      <h3 className="text-xs font-bold text-slate-800 group-hover:text-[#0B5D45] transition">{title}</h3>
      <p className="text-[11px] text-slate-500 mt-1">{desc}</p>
    </div>
    <div className="mt-3 pt-2 border-t border-[#E5E1D6] flex items-center justify-between text-[10px] text-slate-500">
      <span>{metaLeft}</span>
      <span className="text-[#0B5D45] font-semibold">Ready to run</span>
    </div>
  </button>
);

export default DashboardPage;
