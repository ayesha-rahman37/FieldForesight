import React, { useEffect, useRef } from 'react';
import { Wrench, X, Clock } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

interface ComingSoonDrawerProps {
  featureName: string | null;
  onClose: () => void;
}

export const ComingSoonDrawer: React.FC<ComingSoonDrawerProps> = ({ featureName, onClose }) => {
  const { t } = useLanguage();
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (featureName) {
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [featureName, onClose]);

  if (!featureName) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Semi-transparent backdrop overlay */}
      <div
        className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs transition-opacity duration-200"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Slide-in Drawer Panel */}
      <div
        ref={panelRef}
        className="relative z-50 w-full max-w-[360px] h-full bg-[#FBFAF6] border-l border-[#E5E1D6] shadow-2xl flex flex-col justify-between p-6 overflow-y-auto transform transition-transform duration-250 ease-out"
        role="dialog"
        aria-modal="true"
      >
        {/* Top bar with Close Button */}
        <div>
          <div className="flex items-center justify-between pb-4 border-b border-[#E5E1D6]/70">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-600 animate-pulse" />
              <span className="text-xs font-bold uppercase tracking-wider text-[#0B5D45]">
                {t('আপডেট নোটিশ', 'UPDATE NOTICE')}
              </span>
            </div>
            <button
              type="button"
              onClick={onClose}
              className="w-8 h-8 rounded-full bg-[#E6EFE6] text-[#0B5D45] hover:bg-[#0B5D45] hover:text-white flex items-center justify-center transition-colors cursor-pointer"
              aria-label="Close panel"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Main Content */}
          <div className="py-8 flex flex-col items-center text-center space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-[#E6EFE6] border border-[#C5DCBF] flex items-center justify-center text-[#0B5D45] shadow-sm">
              <Wrench className="w-8 h-8" />
            </div>

            <div className="space-y-2">
              <h3 className="text-xl font-bold tracking-tight text-[#1F1F1B]">
                {t('শীঘ্রই আসছে', 'Coming Soon')}
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed max-w-[280px] mx-auto">
                {t(
                  `«${featureName}» ফিচারটি এখনো তৈরি হচ্ছে, খুব শীঘ্রই যুক্ত হবে।`,
                  `The "${featureName}" feature is currently under development and will be available soon.`
                )}
              </p>
            </div>

            <div className="pt-4 flex items-center gap-2 text-xs font-semibold text-[#0B5D45] bg-[#E6EFE6]/80 px-3.5 py-1.5 rounded-full border border-[#C5DCBF]">
              <Clock className="w-3.5 h-3.5" />
              <span>{t('সংস্করণ ২.৫ প্রকাশের অপেক্ষা', 'Awaiting v2.5 release')}</span>
            </div>
          </div>
        </div>

        {/* Footer Action */}
        <div className="pt-4 border-t border-[#E5E1D6]">
          <button
            type="button"
            onClick={onClose}
            className="w-full py-2.5 px-4 bg-[#0B5D45] text-white rounded-xl text-xs font-bold hover:bg-[#084936] transition cursor-pointer shadow-sm"
          >
            {t('ঠিক আছে', 'Got it')}
          </button>
        </div>
      </div>
    </div>
  );
};
