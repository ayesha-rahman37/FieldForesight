import React from 'react';

interface CardProps {
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
  headerAction?: React.ReactNode;
  interactive?: boolean;
  onClick?: () => void;
  style?: React.CSSProperties;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  children,
  className = '',
  headerAction,
  interactive = false,
  onClick,
  style,
}) => {
  return (
    <div
      onClick={onClick}
      className={`${interactive ? 'interactive-card' : ''} ${className}`}
      style={{
        backgroundColor: '#FFFFFF',
        borderRadius: '12px',
        padding: '24px',
        boxShadow: '0 4px 12px rgba(0, 71, 65, 0.05)',
        border: '1px solid #E5E1D5',
        cursor: interactive || onClick ? 'pointer' : 'default',
        ...style,
      }}
    >
      {(title || subtitle || headerAction) && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
          <div>
            {title && <h2>{title}</h2>}
            {subtitle && <p className="caption" style={{ marginTop: '4px' }}>{subtitle}</p>}
          </div>
          {headerAction && <div>{headerAction}</div>}
        </div>
      )}
      {children}
    </div>
  );
};
