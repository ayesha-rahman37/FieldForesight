import React, { useState } from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  children,
  style,
  onMouseEnter,
  onMouseLeave,
  onMouseDown,
  onMouseUp,
  ...props
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isActive, setIsActive] = useState(false);

  let bg = '#004741';
  let color = '#F0EDE4';
  let border = 'none';

  if (variant === 'secondary') {
    bg = 'transparent';
    color = '#004741';
    border = '1px solid #004741';
  } else if (variant === 'danger') {
    bg = '#B33A3A';
    color = '#FFFFFF';
  }

  if (isHovered && !props.disabled) {
    if (variant === 'primary') bg = '#003631';
    else if (variant === 'secondary') bg = 'rgba(0, 71, 65, 0.08)';
    else if (variant === 'danger') bg = '#992D2D';
  }

  let padding = '10px 20px';
  let fontSize = '15px';
  if (size === 'small') {
    padding = '6px 14px';
    fontSize = '13px';
  } else if (size === 'large') {
    padding = '14px 28px';
    fontSize = '18px';
  }

  return (
    <button
      onMouseEnter={(e) => {
        setIsHovered(true);
        onMouseEnter?.(e);
      }}
      onMouseLeave={(e) => {
        setIsHovered(false);
        setIsActive(false);
        onMouseLeave?.(e);
      }}
      onMouseDown={(e) => {
        setIsActive(true);
        onMouseDown?.(e);
      }}
      onMouseUp={(e) => {
        setIsActive(false);
        onMouseUp?.(e);
      }}
      style={{
        backgroundColor: bg,
        color: color,
        border: border,
        padding: padding,
        fontSize: fontSize,
        fontWeight: 600,
        borderRadius: '8px',
        cursor: props.disabled ? 'not-allowed' : 'pointer',
        opacity: props.disabled ? 0.6 : 1,
        transform: isActive ? 'translateY(0)' : isHovered ? 'translateY(-1px)' : 'translateY(0)',
        boxShadow: isHovered && !props.disabled ? '0 4px 12px rgba(0, 71, 65, 0.15)' : 'none',
        transition: 'all 0.2s ease',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        ...style,
      }}
      {...props}
    >
      {children}
    </button>
  );
};
