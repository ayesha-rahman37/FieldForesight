import React from 'react';

interface LoaderProps {
  message?: string;
}

export const Loader: React.FC<LoaderProps> = ({ message = 'লোড হচ্ছে...' }) => {
  return (
    <div style={{ padding: '32px', textAlign: 'center', color: '#004741' }}>
      <div
        style={{
          display: 'inline-block',
          width: '32px',
          height: '32px',
          border: '3px solid #E5E1D5',
          borderTop: '3px solid #004741',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
        }}
      />
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
      <p style={{ marginTop: '12px', fontSize: '14px', fontWeight: 500 }}>{message}</p>
    </div>
  );
};
