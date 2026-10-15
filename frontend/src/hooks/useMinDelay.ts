import { useEffect, useRef, useState } from 'react';

/**
 * Custom hook to enforce a minimum loading duration (default 300ms)
 * for skeleton loader displays. Prevents UI skeleton flickering when API calls
 * finish in <300ms.
 */
export function useMinDelay(loading: boolean, minDelayMs = 300): boolean {
  const [displayLoading, setDisplayLoading] = useState(loading);
  const startTimeRef = useRef<number | null>(null);

  useEffect(() => {
    if (loading) {
      startTimeRef.current = Date.now();
      setDisplayLoading(true);
    } else {
      if (startTimeRef.current !== null) {
        const elapsed = Date.now() - startTimeRef.current;
        const remaining = Math.max(0, minDelayMs - elapsed);
        const timer = setTimeout(() => {
          setDisplayLoading(false);
          startTimeRef.current = null;
        }, remaining);
        return () => clearTimeout(timer);
      } else {
        setDisplayLoading(false);
      }
    }
  }, [loading, minDelayMs]);

  return displayLoading;
}
