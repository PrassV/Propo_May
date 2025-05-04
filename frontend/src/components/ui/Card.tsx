import React from 'react';
import { cn } from '../../lib/utils';

type CardProps = {
  className?: string;
  children: React.ReactNode;
};

const Card = ({ className, children }: CardProps) => {
  return (
    <div
      className={cn(
        'bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden',
        className
      )}
    >
      {children}
    </div>
  );
};

const CardHeader = ({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) => {
  return <div className={cn('p-4 border-b border-gray-200', className)}>{children}</div>;
};

const CardTitle = ({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) => {
  return <h3 className={cn('text-lg font-semibold', className)}>{children}</h3>;
};

const CardDescription = ({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) => {
  return <p className={cn('text-sm text-gray-500 mt-1', className)}>{children}</p>;
};

const CardContent = ({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) => {
  return <div className={cn('p-4', className)}>{children}</div>;
};

const CardFooter = ({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) => {
  return (
    <div className={cn('p-4 border-t border-gray-200 bg-gray-50', className)}>
      {children}
    </div>
  );
};

export { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter };