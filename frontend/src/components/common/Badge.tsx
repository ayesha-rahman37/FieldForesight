import React from 'react';

interface BadgeProps {
  label: string;
  color?: 'green' | 'yellow' | 'red' | 'gray';
}

const colorMap = {
  green: { dot: '#2E7D32', text: '#1B5E20', bg: '#E8F5E9' },
  yellow: { dot: '#F9A825', text: '#F57F17', bg: '#FFFDE7' },
  red: { dot: '#C62828', text: '#B71C1C', bg: '#FFEBEE' },
  gray: { dot: '#757575', text: '#424242', bg: '#F5F5F5' },
};

export const Badge: React.FC<BadgeProps> = ({ label, color = 'gray' }) => {
  const styles = colorMap[color];

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '4px 10px',
        borderRadius: '16px',
        backgroundColor: styles.bg,
        color: styles.text,
        fontSize: '12px',
        fontWeight: 600,
        lineHeight: 1,
      }}
    >
      <span
        style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          backgroundColor: styles.dot,
        }}
      />
      {label}
    </span>
  );
};
