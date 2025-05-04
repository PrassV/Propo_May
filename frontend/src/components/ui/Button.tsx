import React from 'react';
import { cn } from '../../lib/utils';

type ButtonProps = {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
} & React.ButtonHTMLAttributes<HTMLButtonElement>;

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    return (
      <button
        className={cn(
          'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none',
          {
            'bg-blue-700 text-white hover:bg-blue-800 focus-visible:ring-blue-700': variant === 'primary',
            'bg-gray-100 text-gray-900 hover:bg-gray-200 focus-visible:ring-gray-300': variant === 'secondary',
            'border border-gray-300 text-gray-700 hover:bg-gray-50 focus-visible:ring-gray-300': variant === 'outline',
            'text-gray-700 hover:bg-gray-100 focus-visible:ring-gray-300': variant === 'ghost',
            'bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-600': variant === 'danger',
            'text-sm px-3 py-1.5 h-8': size === 'sm',
            'text-base px-4 py-2 h-10': size === 'md',
            'text-lg px-5 py-2.5 h-12': size === 'lg',
          },
          className
        )}
        ref={ref}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;