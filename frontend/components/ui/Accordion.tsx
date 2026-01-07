'use client';

import { createContext, useContext, useState, type ReactNode } from 'react';
import { cn } from '@/lib/utils';
import { ChevronDown } from 'lucide-react';

interface AccordionContextValue {
  openItems: string[];
  toggle: (value: string) => void;
  type: 'single' | 'multiple';
}

const AccordionContext = createContext<AccordionContextValue | null>(null);

interface AccordionProps {
  children: ReactNode;
  type?: 'single' | 'multiple';
  defaultValue?: string[];
  className?: string;
}

export function Accordion({
  children,
  type = 'single',
  defaultValue = [],
  className,
}: AccordionProps) {
  const [openItems, setOpenItems] = useState<string[]>(defaultValue);

  const toggle = (value: string) => {
    if (type === 'single') {
      setOpenItems((prev) => (prev.includes(value) ? [] : [value]));
    } else {
      setOpenItems((prev) =>
        prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value]
      );
    }
  };

  return (
    <AccordionContext.Provider value={{ openItems, toggle, type }}>
      <div className={cn('divide-y divide-slate-100', className)}>{children}</div>
    </AccordionContext.Provider>
  );
}

interface AccordionItemProps {
  value: string;
  children: ReactNode;
  className?: string;
}

export function AccordionItem({ value, children, className }: AccordionItemProps) {
  return (
    <div className={className} data-value={value}>
      {children}
    </div>
  );
}

interface AccordionTriggerProps {
  children: ReactNode;
  className?: string;
  value: string;
}

export function AccordionTrigger({ children, className, value }: AccordionTriggerProps) {
  const context = useContext(AccordionContext);
  if (!context) throw new Error('AccordionTrigger must be used within Accordion');

  const isOpen = context.openItems.includes(value);

  return (
    <button
      type="button"
      onClick={() => context.toggle(value)}
      className={cn(
        'flex w-full items-center justify-between py-4 text-left font-medium transition-colors hover:text-slate-900',
        className
      )}
    >
      {children}
      <ChevronDown
        className={cn(
          'h-4 w-4 text-slate-500 transition-transform duration-200',
          isOpen && 'rotate-180'
        )}
      />
    </button>
  );
}

interface AccordionContentProps {
  children: ReactNode;
  className?: string;
  value: string;
}

export function AccordionContent({ children, className, value }: AccordionContentProps) {
  const context = useContext(AccordionContext);
  if (!context) throw new Error('AccordionContent must be used within Accordion');

  const isOpen = context.openItems.includes(value);

  if (!isOpen) return null;

  return (
    <div
      className={cn(
        'pb-4 text-sm text-slate-600 animate-fade-in',
        className
      )}
    >
      {children}
    </div>
  );
}

