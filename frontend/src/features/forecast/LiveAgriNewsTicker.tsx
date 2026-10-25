import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import {
  Radio,
  ExternalLink,
  RefreshCw,
  AlertTriangle,
  CloudRain,
  TrendingUp,
  Bug,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  ChevronUp,
  Newspaper,
  Layers,
  X,
  Search,
} from 'lucide-react';
import api from '../../api/client';

export interface ScrapedNewsAlert {
  id: number;
  title: string;
  source_url: string;
  summary?: string;
  district: string;
  risk_tag: string;
  crawled_at: string;
}

interface LiveAgriNewsTickerProps {
  selectedDistrict?: string;
}

export const LiveAgriNewsTicker: React.FC<LiveAgriNewsTickerProps> = ({ selectedDistrict }) => {
  const { t } = useLanguage();
  const [alerts, setAlerts] = useState<ScrapedNewsAlert[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isExpanded, setIsExpanded] = useState<boolean>(true);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [searchFilter, setSearchFilter] = useState<string>('');
  const [selectedTagFilter, setSelectedTagFilter] = useState<string>('ALL');

  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState<boolean>(false);
  const [canScrollRight, setCanScrollRight] = useState<boolean>(false);
  const [isHovered, setIsHovered] = useState<boolean>(false);

  const fetchAlerts = async () => {
    try {
      const res = await api.get<ScrapedNewsAlert[]>('/api/webhooks/alerts', {
        params: {
          district: selectedDistrict || undefined,
          limit: 20,
        },
      });
      setAlerts(res.data);
    } catch {
      // Graceful fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    // Auto-refresh from backend every 60 seconds
    const interval = setInterval(fetchAlerts, 60000);
    return () => clearInterval(interval);
  }, [selectedDistrict]);

  // Check scroll boundary to enable/disable arrow buttons
  const updateScrollButtons = useCallback(() => {
    const el = scrollContainerRef.current;
    if (!el) return;
    const { scrollLeft, scrollWidth, clientWidth } = el;
    setCanScrollLeft(scrollLeft > 10);
    setCanScrollRight(scrollLeft + clientWidth < scrollWidth - 10);
  }, []);

  useEffect(() => {
    updateScrollButtons();
    const el = scrollContainerRef.current;
    if (!el) return;
    el.addEventListener('scroll', updateScrollButtons, { passive: true });
    window.addEventListener('resize', updateScrollButtons);
    return () => {
      el.removeEventListener('scroll', updateScrollButtons);
      window.removeEventListener('resize', updateScrollButtons);
    };
  }, [alerts, updateScrollButtons]);

  // Smooth scroll handler
  const handleScroll = (direction: 'left' | 'right') => {
    const el = scrollContainerRef.current;
    if (!el) return;
    const cardWidth = 340; // Approx single card width + gap
    const scrollAmount = direction === 'left' ? -cardWidth : cardWidth;
    el.scrollBy({ left: scrollAmount, behavior: 'smooth' });
  };

  // Auto-slide gentle ticker when not hovered
  useEffect(() => {
    if (!isExpanded || isHovered || alerts.length <= 3) return;

    const timer = setInterval(() => {
      const el = scrollContainerRef.current;
      if (!el) return;
      const { scrollLeft, scrollWidth, clientWidth } = el;
      if (scrollLeft + clientWidth >= scrollWidth - 10) {
        // Loop back to start
        el.scrollTo({ left: 0, behavior: 'smooth' });
      } else {
        handleScroll('right');
      }
    }, 7000);

    return () => clearInterval(timer);
  }, [isExpanded, isHovered, alerts.length]);

  if (loading && alerts.length === 0) {
    return null;
  }

  if (alerts.length === 0) {
    return null;
  }

  const getTagBadge = (tag: string) => {
    switch (tag) {
      case 'Fertilizer Shortage':
        return {
          icon: <AlertTriangle className="w-3 h-3 text-amber-300" />,
          bg: 'bg-amber-500/20 text-amber-200 border-amber-500/40',
        };
      case 'Weather Extreme':
        return {
          icon: <CloudRain className="w-3 h-3 text-red-300" />,
          bg: 'bg-red-500/20 text-red-200 border-red-500/40',
        };
      case 'Market Trend':
        return {
          icon: <TrendingUp className="w-3 h-3 text-sky-300" />,
          bg: 'bg-sky-500/20 text-sky-200 border-sky-500/40',
        };
      case 'Pest/Disease':
        return {
          icon: <Bug className="w-3 h-3 text-rose-300" />,
          bg: 'bg-rose-500/20 text-rose-200 border-rose-500/40',
        };
      default:
        return {
          icon: <Radio className="w-3 h-3 text-emerald-300" />,
          bg: 'bg-emerald-500/20 text-emerald-200 border-emerald-500/40',
        };
    }
  };

  // Filtered alerts for the Full Archive Modal
  const modalAlerts = alerts.filter((item) => {
    const matchesTag = selectedTagFilter === 'ALL' || item.risk_tag === selectedTagFilter;
    const matchesQuery =
      !searchFilter ||
      item.title.toLowerCase().includes(searchFilter.toLowerCase()) ||
      item.district.toLowerCase().includes(searchFilter.toLowerCase()) ||
      (item.summary && item.summary.toLowerCase().includes(searchFilter.toLowerCase()));
    return matchesTag && matchesQuery;
  });

  return (
    <>
      <div
        className="rounded-2xl bg-gradient-to-r from-emerald-950 via-[#004741] to-teal-950 p-4 text-white shadow-md border border-emerald-800/60 transition-all"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Top Header Bar */}
        <div className="flex items-center justify-between gap-3 border-b border-emerald-700/50 pb-2.5">
          <div className="flex items-center gap-2.5 flex-wrap min-w-0">
            <span className="flex h-2.5 w-2.5 relative shrink-0">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-400"></span>
            </span>

            <h3 className="text-xs sm:text-sm font-bold tracking-wide uppercase flex items-center gap-1.5 text-emerald-100">
              <Newspaper className="w-4 h-4 text-emerald-300 shrink-0" />
              <span>{t('লাইভ ফিল্ড সংবাদ ও আবহাওয়া সতর্কতা', 'Live Ground Alerts & Agri-News Feed')}</span>
            </h3>

            <span className="text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded-full font-semibold">
              {t('n8n স্বয়ংক্রিয় ক্রলার', 'n8n Automated')}
            </span>

            {selectedDistrict && (
              <span className="text-[10px] bg-black/30 text-emerald-200 border border-emerald-600/30 px-2 py-0.5 rounded-full font-medium">
                📍 {selectedDistrict} + {t('জাতীয়', 'National')}
              </span>
            )}

            <span className="text-[10px] text-emerald-300/70 font-medium">
              ({alerts.length} {alerts.length === 1 ? t('সংবাদ', 'alert') : t('সংবাদসমূহ', 'alerts')})
            </span>
          </div>

          {/* Right Action Controls: Carousel Arrows + View All + Refresh + Collapse */}
          <div className="flex items-center gap-1.5 shrink-0">
            {/* Carousel Slide Left/Right Buttons */}
            {isExpanded && alerts.length > 2 && (
              <div className="flex items-center gap-1 bg-black/30 p-0.5 rounded-lg border border-white/10 mr-1">
                <button
                  type="button"
                  onClick={() => handleScroll('left')}
                  disabled={!canScrollLeft}
                  title={t('পূর্ববর্তী সংবাদ', 'Previous')}
                  className="p-1 rounded text-emerald-200 hover:text-white hover:bg-emerald-800/60 disabled:opacity-30 disabled:cursor-not-allowed transition cursor-pointer"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={() => handleScroll('right')}
                  disabled={!canScrollRight}
                  title={t('পরবর্তী সংবাদ', 'Next')}
                  className="p-1 rounded text-emerald-200 hover:text-white hover:bg-emerald-800/60 disabled:opacity-30 disabled:cursor-not-allowed transition cursor-pointer"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}

            {/* View All Button */}
            <button
              type="button"
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-200 hover:text-white bg-emerald-900/60 hover:bg-emerald-800 px-2.5 py-1 rounded-lg border border-emerald-600/40 transition cursor-pointer"
            >
              <Layers className="w-3 h-3 text-emerald-300" />
              <span>{t('সব দেখুন', 'View All')}</span>
            </button>

            {/* Refresh Button */}
            <button
              type="button"
              onClick={fetchAlerts}
              title={t('তাজা করুন', 'Refresh')}
              className="text-emerald-300 hover:text-white p-1 rounded-lg hover:bg-emerald-800/50 transition-colors cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>

            {/* Collapse/Expand Toggle */}
            <button
              type="button"
              onClick={() => setIsExpanded(!isExpanded)}
              title={isExpanded ? t('সংকুচিত করুন', 'Collapse') : t('প্রসারিত করুন', 'Expand')}
              className="text-emerald-300 hover:text-white p-1 rounded-lg hover:bg-emerald-800/50 transition-colors cursor-pointer"
            >
              {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          </div>
        </div>

        {/* Carousel Row: Fixed Height, Horizontal Scroll with Snap */}
        {isExpanded && (
          <div className="relative mt-3">
            <div
              ref={scrollContainerRef}
              className="flex gap-3.5 overflow-x-auto pb-1 scroll-smooth snap-x snap-mandatory scrollbar-thin scrollbar-thumb-emerald-700/60 scrollbar-track-transparent"
              style={{
                scrollbarWidth: 'thin',
              }}
            >
              {alerts.map((item) => {
                const badge = getTagBadge(item.risk_tag);
                return (
                  <div
                    key={item.id}
                    className="snap-start shrink-0 w-[290px] sm:w-[330px] md:w-[350px] bg-white/[0.07] hover:bg-white/[0.12] backdrop-blur-sm rounded-xl p-3 border border-white/10 flex flex-col justify-between transition-all duration-200 shadow-xs"
                  >
                    <div>
                      {/* Badge & District */}
                      <div className="flex items-center justify-between gap-2 mb-2">
                        <span
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold border ${badge.bg}`}
                        >
                          {badge.icon}
                          {item.risk_tag}
                        </span>
                        <span className="text-[10px] text-emerald-200/90 font-medium bg-black/30 px-2 py-0.5 rounded border border-white/5">
                          📍 {item.district}
                        </span>
                      </div>

                      {/* Headline */}
                      <h4 className="text-xs font-semibold text-white line-clamp-2 leading-snug mb-1.5" title={item.title}>
                        {item.title}
                      </h4>

                      {/* Summary */}
                      {item.summary && (
                        <p className="text-[11px] text-emerald-100/75 line-clamp-2 leading-relaxed">
                          {item.summary}
                        </p>
                      )}
                    </div>

                    {/* Bottom Metadata & Link */}
                    <div className="mt-3 pt-2 border-t border-white/10 flex items-center justify-between">
                      <span className="text-[10px] text-emerald-200/60">
                        {new Date(item.crawled_at).toLocaleDateString()}
                      </span>
                      <a
                        href={item.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[11px] text-emerald-300 hover:text-white font-medium inline-flex items-center gap-1 hover:underline"
                      >
                        <span>{t('সংবাদ দেখুন', 'Read News')}</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Slide-Over / Full Archive Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-xs animate-fadeIn">
          <div className="bg-slate-900 border border-slate-700 w-full max-w-4xl max-h-[85vh] rounded-2xl shadow-2xl flex flex-col text-slate-100 overflow-hidden">
            {/* Modal Header */}
            <div className="p-4 sm:p-5 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-emerald-600/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
                  <Newspaper className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    {t('সকল সংগৃহীত কৃষি সংবাদ ও ঝুঁকি সংকেত', 'All Crawled Agricultural News & Ground Alerts')}
                  </h3>
                  <p className="text-xs text-slate-400">
                    {t('স্বয়ংক্রিয় ক্রলার দ্বারা সংগৃহীত লাইভ ডেটাবেজ আর্কাইভ', 'Live ground news archive delivered via n8n automation')}
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Filter and Search Bar */}
            <div className="p-4 border-b border-slate-800 bg-slate-900/50 flex flex-col sm:flex-row items-center gap-3">
              <div className="relative w-full sm:w-72">
                <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
                <input
                  type="text"
                  value={searchFilter}
                  onChange={(e) => setSearchFilter(e.target.value)}
                  placeholder={t('শিরোনাম বা জেলা খুঁজুন...', 'Search headline or district...')}
                  className="w-full pl-9 pr-3 py-1.5 bg-slate-800/80 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex items-center gap-1.5 overflow-x-auto w-full pb-1 sm:pb-0">
                {['ALL', 'Market Trend', 'Weather Extreme', 'Fertilizer Shortage', 'Pest/Disease', 'General'].map(
                  (tag) => (
                    <button
                      key={tag}
                      type="button"
                      onClick={() => setSelectedTagFilter(tag)}
                      className={`text-[11px] px-2.5 py-1 rounded-full font-medium whitespace-nowrap transition cursor-pointer border ${
                        selectedTagFilter === tag
                          ? 'bg-emerald-600 text-white border-emerald-500'
                          : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'
                      }`}
                    >
                      {tag === 'ALL' ? t('সব', 'All') : tag}
                    </button>
                  )
                )}
              </div>
            </div>

            {/* Modal Body: Scrollable Grid */}
            <div className="p-4 sm:p-5 overflow-y-auto flex-1 max-h-[60vh] space-y-3">
              {modalAlerts.length === 0 ? (
                <div className="text-center py-12 text-slate-500 text-xs">
                  {t('কোনো সংবাদ পাওয়া যায়নি।', 'No agricultural news found matching criteria.')}
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3.5">
                  {modalAlerts.map((item) => {
                    const badge = getTagBadge(item.risk_tag);
                    return (
                      <div
                        key={item.id}
                        className="bg-slate-800/60 hover:bg-slate-800/90 border border-slate-700/80 rounded-xl p-3.5 flex flex-col justify-between transition"
                      >
                        <div>
                          <div className="flex items-center justify-between gap-2 mb-2">
                            <span
                              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold border ${badge.bg}`}
                            >
                              {badge.icon}
                              {item.risk_tag}
                            </span>
                            <span className="text-[10px] text-slate-300 font-medium bg-slate-900/80 px-2 py-0.5 rounded border border-slate-700">
                              📍 {item.district}
                            </span>
                          </div>

                          <h4 className="text-xs font-semibold text-white leading-snug mb-1.5">
                            {item.title}
                          </h4>

                          {item.summary && (
                            <p className="text-[11px] text-slate-400 line-clamp-3 leading-relaxed">
                              {item.summary}
                            </p>
                          )}
                        </div>

                        <div className="mt-3.5 pt-2.5 border-t border-slate-700/60 flex items-center justify-between">
                          <span className="text-[10px] text-slate-500">
                            {new Date(item.crawled_at).toLocaleDateString()}
                          </span>
                          <a
                            href={item.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[11px] text-emerald-400 hover:text-emerald-300 font-medium inline-flex items-center gap-1 hover:underline"
                          >
                            <span>{t('সংবাদ দেখুন', 'Read News')}</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-3.5 border-t border-slate-800 bg-slate-950/60 flex items-center justify-between text-xs text-slate-400">
              <span>
                {t('মোট সংবাদ:', 'Total Articles:')}{' '}
                <strong className="text-white">{modalAlerts.length}</strong>
              </span>
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold transition cursor-pointer"
              >
                {t('বন্ধ করুন', 'Close')}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
