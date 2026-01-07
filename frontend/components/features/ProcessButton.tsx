'use client';

import { useCallback } from 'react';
import { cn, downloadBlob } from '@/lib/utils';
import { useAppStore } from '@/store';
import { ProcessingProgress } from './ProcessingProgress';
import { Switch } from '@/components/ui/Switch';
import { Download, Loader2 } from 'lucide-react';

interface ProcessButtonProps {
  className?: string;
}

export function ProcessButton({ className }: ProcessButtonProps) {
  const {
    file,
    selectedProfiles,
    options,
    status,
    progress,
    error,
    setStatus,
    setProgress,
    setError,
    setResult,
    setOptions,
  } = useAppStore();

  const canProcess = file && selectedProfiles.length > 0 && status !== 'processing';

  const handleProcess = useCallback(async () => {
    if (!file || selectedProfiles.length === 0) return;

    setStatus('processing');
    setProgress(5);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      for (const profile of selectedProfiles) {
        formData.append('selected_profiles', profile);
      }

      formData.append('deduplicate', String(options.deduplicate));

      setProgress(15);

      const response = await fetch('/api/process', {
        method: 'POST',
        body: formData,
      });

      setProgress(85);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `处理失败: ${response.status}`);
      }

      const blob = await response.blob();
      const contentDisposition = response.headers.get('content-disposition');
      const filename =
        contentDisposition?.match(/filename="?([^";]+)"?/i)?.[1] || 'outputs.zip';

      setProgress(100);
      setResult(blob, filename);
      setStatus('completed');

      // 自动下载
      downloadBlob(blob, filename);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知错误');
      setStatus('error');
    }
  }, [file, selectedProfiles, options, setStatus, setProgress, setError, setResult]);

  return (
    <div className={cn('space-y-4', className)}>
      {/* 选项面板 */}
      <div className="space-y-3">
        <Switch
          label="按标题去重"
          description="移除重复的文献条目"
          checked={options.deduplicate}
          onChange={(e) => setOptions({ deduplicate: e.target.checked })}
        />
      </div>

      {/* 进度显示 */}
      {status !== 'idle' && (
        <ProcessingProgress progress={progress} status={status} />
      )}

      {/* 错误提示 */}
      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {error}
        </div>
      )}

      {/* 处理按钮 */}
      <button
        onClick={handleProcess}
        disabled={!canProcess}
        className={cn(
          'flex w-full items-center justify-center gap-2 rounded-xl py-3 font-semibold transition-all',
          canProcess
            ? 'bg-blue-600 text-white hover:bg-blue-700 active:scale-[0.98]'
            : 'cursor-not-allowed bg-slate-200 text-slate-400'
        )}
      >
        {status === 'processing' ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            处理中...
          </>
        ) : (
          <>
            <Download className="h-5 w-5" />
            处理并下载 ZIP
          </>
        )}
      </button>

      {/* 提示信息 */}
      {!file && (
        <p className="text-center text-sm text-slate-400">请先上传 RIS 文件</p>
      )}
      {file && selectedProfiles.length === 0 && (
        <p className="text-center text-sm text-slate-400">请选择至少一个 Profile</p>
      )}
    </div>
  );
}

