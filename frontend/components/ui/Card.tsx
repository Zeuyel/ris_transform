import { type ReactNode } from 'react';
import { cn } from '@/lib/utils';

export interface CardProps {
  children: ReactNode;
  className?: string;
}

export function Card({ children, className }: CardProps) {
  return (
    <div className={cn('rounded-2xl border border-slate-200 bg-white', className)}>
      {children}
    </div>
  );
}

export interface CardHeaderProps {
  children: ReactNode;
  className?: string;
}

export function CardHeader({ children, className }: CardHeaderProps) {
  return (
    <div className={cn('px-6 py-4 border-b border-slate-100', className)}>
      {children}
    </div>
  );
}

export interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function CardContent({ children, className }: CardContentProps) {
  return <div className={cn('p-6', className)}>{children}</div>;
}

export interface CardTitleProps {
  children: ReactNode;
  className?: string;
  as?: 'h1' | 'h2' | 'h3' | 'h4';
}

export function CardTitle({ children, className, as: Tag = 'h3' }: CardTitleProps) {
  return (
    <Tag className={cn('font-semibold text-slate-900', className)}>{children}</Tag>
  );
}

export interface CardDescriptionProps {
  children: ReactNode;
  className?: string;
}

export function CardDescription({ children, className }: CardDescriptionProps) {
  return <p className={cn('text-sm text-slate-500 mt-1', className)}>{children}</p>;
}

