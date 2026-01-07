'use client';

import { forwardRef, type InputHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, leftIcon, rightIcon, id, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label htmlFor={id} className="block text-sm font-medium text-slate-700 mb-1.5">
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            id={id}
            className={cn(
              'w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm transition-colors',
              'placeholder:text-slate-400',
              'focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20',
              'disabled:cursor-not-allowed disabled:bg-slate-50 disabled:text-slate-500',
              error && 'border-rose-300 focus:border-rose-500 focus:ring-rose-500/20',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              className
            )}
            {...props}
          />
          {rightIcon && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400">
              {rightIcon}
            </div>
          )}
        </div>
        {error && <p className="mt-1.5 text-xs text-rose-600">{error}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };

