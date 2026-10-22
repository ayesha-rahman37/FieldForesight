import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
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
    console.error('ErrorBoundary caught an unhandled rendering error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      if (this.fallback) {
        return this.fallback;
      }

      return (
        <div className="min-h-[200px] w-full flex items-center justify-center p-6 bg-amber-50/60 border border-amber-200 rounded-2xl text-center">
          <div className="max-w-md space-y-3">
            <h3 className="text-base font-semibold text-[#004741]">
              পৃষ্ঠার কিছু অংশ প্রদর্শনে সমস্যা হয়েছে / Something went wrong
            </h3>
            <p className="text-xs text-slate-600">
              অনুগ্রহ করে পৃষ্ঠাটি রিলোড দিন বা কিছুক্ষণ পর পুনরায় চেষ্টা করুন।
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.reload();
              }}
              className="px-4 py-2 bg-[#004741] text-[#F0EDE4] text-xs font-semibold rounded-xl hover:bg-[#084936] transition-colors cursor-pointer"
            >
              পুনরায় লোড করুন (Reload)
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }

  private get fallback(): ReactNode | undefined {
    return this.props.fallback;
  }
}

export default ErrorBoundary;
