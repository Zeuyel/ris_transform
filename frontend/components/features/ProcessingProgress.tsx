'use client';

import { cn } from '@/lib/utils';

interface ProcessingProgressProps {
  progress: number;
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'error';
  message?: string;
  className?: string;
}

export function ProcessingProgress({
  progress,
  status,
  message,
  className,
}: ProcessingProgressProps) {
  if (status === 'idle') return null;

  const getStatusColor = () => {
    switch (status) {
      case 'uploading':
        return 'bg-blue-500';
      case 'processing':
        return 'bg-amber-500';
      case 'completed':
        return 'bg-emerald-500';
      case 'error':
        return 'bg-rose-500';
      default:
        return 'bg-slate-400';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'uploading':
        return '上传中...';
      case 'processing':
        return '处理中...';
      case 'completed':
        return '处理完成';
      case 'error':
        return '处理失败';
      default:
        return '';
    }
  };

  return (
    <div className={cn('space-y-2', className)}>
      {/* 状态文本 */}
      <div className="flex items-center justify-between text-sm">
        <span
          className={cn(
            'font-medium',
            status === 'error' ? 'text-rose-600' : 'text-slate-700'
          )}
        >
          {message || getStatusText()}
        </span>
        {status !== 'error' && (
          <span className="text-slate-500">{Math.round(progress)}%</span>
        )}
      </div>

      {/* 进度条 */}
      <div className="h-2 overflow-hidden rounded-full bg-slate-100">
        <div
          className={cn(
            'h-full transition-all duration-300 ease-out',
            getStatusColor(),
            status === 'processing' && 'animate-pulse'
          )}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}

