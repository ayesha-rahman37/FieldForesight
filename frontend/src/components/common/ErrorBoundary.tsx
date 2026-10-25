import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertCircle, RotateCcw, Home } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  featureName?: string;
  isPageLevel?: boolean;
  compact?: boolean;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log privately to console for debugging; never expose stack traces to farmers
    console.error('ErrorBoundary caught an unhandled rendering error:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  private handleReload = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  private handleGoHome = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/dashboard';
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const featureTitle = this.props.featureName
        ? `${this.props.featureName} অংশটি এখন লোড করা যাচ্ছে না`
        : 'এই অংশটি এখন লোড করা যাচ্ছে না';

      // 1. Full Page Level Crash Fallback
      if (this.props.isPageLevel) {
        return (
          <div className="min-h-screen w-full flex items-center justify-center p-6 bg-[#F4F6F8]">
            <div className="max-w-md w-full p-8 bg-white border border-slate-200/90 rounded-3xl shadow-sm text-center">
              <div className="w-14 h-14 rounded-2xl bg-amber-100/70 text-amber-800 flex items-center justify-center mx-auto mb-4">
                <AlertCircle className="w-7 h-7 text-amber-700" />
              </div>

              <h2 className="text-lg font-bold text-slate-800 mb-2">
                পৃষ্ঠাটি লোড করতে সাময়িক সমস্যা হয়েছে
              </h2>

              <p className="text-xs text-slate-600 mb-6 leading-relaxed">
                চিন্তার কিছু নেই, আপনার পূর্বের সংরক্ষিত তথ্য সুরক্ষিত রয়েছে। অনুগ্রহ করে পুনরায় চেষ্টা করুন অথবা ড্যাশবোর্ডে ফিরে যান।
              </p>

              <div className="flex items-center justify-center gap-3 flex-wrap">
                <button
                  type="button"
                  onClick={this.handleReload}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-[#004741] hover:bg-emerald-900 text-white text-xs font-semibold rounded-xl shadow-xs transition-colors cursor-pointer"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>আবার চেষ্টা করুন</span>
                </button>

                <button
                  type="button"
                  onClick={this.handleGoHome}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-white hover:bg-slate-100 text-slate-700 border border-slate-200 text-xs font-semibold rounded-xl shadow-2xs transition-colors cursor-pointer"
                >
                  <Home className="w-3.5 h-3.5 text-slate-500" />
                  <span>ড্যাশবোর্ডে ফিরে যান</span>
                </button>
              </div>
            </div>
          </div>
        );
      }

      // 2. Compact / Inline Feature Level Fallback
      if (this.props.compact) {
        return (
          <div className="py-2.5 px-3.5 bg-amber-50/60 border border-amber-200/80 rounded-xl flex items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2 min-w-0">
              <AlertCircle className="w-4 h-4 text-amber-700 shrink-0" />
              <span className="font-medium text-slate-700 truncate">{featureTitle}</span>
            </div>
            <button
              type="button"
              onClick={this.handleReset}
              className="inline-flex items-center gap-1 font-bold text-[#004741] hover:underline shrink-0 cursor-pointer text-xs"
            >
              <RotateCcw className="w-3 h-3" />
              <span>আবার চেষ্টা করুন</span>
            </button>
          </div>
        );
      }

      // 3. Standard Card Level Fallback (keeps page structure completely intact)
      return (
        <div className="p-6 bg-white border border-slate-200/90 rounded-2xl flex flex-col items-center justify-center text-center shadow-xs min-h-[180px]">
          <div className="w-10 h-10 rounded-full bg-amber-50 text-amber-700 flex items-center justify-center mb-3">
            <AlertCircle className="w-5 h-5 text-amber-600" />
          </div>

          <h4 className="text-sm font-bold text-slate-800 mb-1">
            {featureTitle}
          </h4>

          <p className="text-xs text-slate-500 max-w-sm mb-4 leading-relaxed">
            চিন্তার কিছু নেই, বাকি ফিচারগুলো স্বাভাবিকভাবে কাজ করছে।
          </p>

          <button
            type="button"
            onClick={this.handleReset}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-[#004741] hover:bg-emerald-900 text-white text-xs font-semibold rounded-xl shadow-xs transition-colors cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>আবার চেষ্টা করুন</span>
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
