import React, { createContext, useContext, useState } from 'react';
import { ComingSoonDrawer } from '../components/common/ComingSoonDrawer';

interface ComingSoonContextType {
  openComingSoon: (featureName: string) => void;
  closeComingSoon: () => void;
}

const ComingSoonContext = createContext<ComingSoonContextType | undefined>(undefined);

export const ComingSoonProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [featureName, setFeatureName] = useState<string | null>(null);

  const openComingSoon = (name: string) => {
    setFeatureName(name);
  };

  const closeComingSoon = () => {
    setFeatureName(null);
  };

  return (
    <ComingSoonContext.Provider value={{ openComingSoon, closeComingSoon }}>
      {children}
      <ComingSoonDrawer featureName={featureName} onClose={closeComingSoon} />
    </ComingSoonContext.Provider>
  );
};

export const useComingSoon = () => {
  const context = useContext(ComingSoonContext);
  if (!context) {
    throw new Error('useComingSoon must be used within a ComingSoonProvider');
  }
  return context;
};
