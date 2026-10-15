import React from 'react';

interface SkeletonProps {
  height?: string | number;
  width?: string | number;
  borderRadius?: string | number;
  className?: string;
  style?: React.CSSProperties;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  height = '100%',
  width = '100%',
  borderRadius = '8px',
  className = '',
  style,
}) => {
  return (
    <div
      className={`skeleton-shimmer ${className}`}
      style={{
        height,
        width,
        borderRadius,
        ...style,
      }}
    />
  );
};

export const SkeletonLoader = Skeleton;
