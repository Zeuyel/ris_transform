'use client';

import { forwardRef, type InputHTMLAttributes, useId } from 'react';
import { cn } from '@/lib/utils';

export interface SwitchProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'size'> {
  label?: string;
  description?: string;
  size?: 'sm' | 'md';
}

const Switch = forwardRef<HTMLInputElement, SwitchProps>(
  ({ className, label, description, size = 'md', id: propId, checked, onChange, ...props }, ref) => {
    const generatedId = useId();
    const id = propId || generatedId;

    const sizes = {
      sm: {
        track: 'w-8 h-4',
        thumb: 'h-3 w-3',
        thumbTranslate: 'translate-x-4',
      },
      md: {
        track: 'w-11 h-6',
        thumb: 'h-5 w-5',
        thumbTranslate: 'translate-x-5',
      },
    };

    return (
      <label htmlFor={id} className={cn('flex items-center justify-between gap-3 cursor-pointer', className)}>
        {(label || description) && (
          <div className="flex-1">
            {label && <span className="text-sm font-medium text-slate-700">{label}</span>}
            {description && <p className="text-xs text-slate-500 mt-0.5">{description}</p>}
          </div>
        )}
        <div className="relative inline-flex items-center flex-shrink-0">
          <input
            ref={ref}
            id={id}
            type="checkbox"
            className="peer sr-only"
            checked={checked}
            onChange={onChange}
            {...props}
          />
          {/* Track */}
          <div
            className={cn(
              'rounded-full transition-colors',
              checked ? 'bg-blue-600' : 'bg-slate-200',
              'peer-focus:ring-2 peer-focus:ring-blue-500 peer-focus:ring-offset-2',
              sizes[size].track
            )}
          />
          {/* Thumb */}
          <div
            className={cn(
              'absolute left-0.5 top-0.5 rounded-full bg-white shadow transition-transform',
              sizes[size].thumb,
              checked && sizes[size].thumbTranslate
            )}
          />
        </div>
      </label>
    );
  }
);

Switch.displayName = 'Switch';

export { Switch };

