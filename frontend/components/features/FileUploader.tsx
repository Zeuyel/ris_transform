'use client';

import { useCallback, useState } from 'react';
import { cn, formatFileSize, readFileAsText } from '@/lib/utils';
import { countEntries } from '@/lib/ris-parser';
import { useAppStore } from '@/store';
import { Upload, File, X } from 'lucide-react';

interface FileUploaderProps {
  className?: string;
}

export function FileUploader({ className }: FileUploaderProps) {
  const { file, setFile, setFileContent } = useAppStore();
  const [isDragging, setIsDragging] = useState(false);
  const [entryCount, setEntryCount] = useState<number | null>(null);

  const handleFile = useCallback(
    async (selectedFile: File) => {
      if (!selectedFile.name.toLowerCase().endsWith('.ris')) {
        alert('请选择 .ris 文件');
        return;
      }

      setFile(selectedFile);

      try {
        const content = await readFileAsText(selectedFile);
        setFileContent(content);
        setEntryCount(countEntries(content));
      } catch (error) {
        console.error('读取文件失败:', error);
      }
    },
    [setFile, setFileContent]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile) {
        handleFile(droppedFile);
      }
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFile = e.target.files?.[0];
      if (selectedFile) {
        handleFile(selectedFile);
      }
    },
    [handleFile]
  );

  const handleClear = useCallback(() => {
    setFile(null);
    setFileContent(null);
    setEntryCount(null);
  }, [setFile, setFileContent]);

  return (
    <div className={cn('relative', className)}>
      {file ? (
        // 已选择文件状态
        <div className="flex items-center justify-between gap-4 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100">
              <File className="h-5 w-5 text-emerald-600" />
            </div>
            <div>
              <p className="font-medium text-slate-900">{file.name}</p>
              <p className="text-sm text-slate-500">
                {formatFileSize(file.size)}
                {entryCount !== null && ` · ${entryCount} 条目`}
              </p>
            </div>
          </div>
          <button
            onClick={handleClear}
            className="rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      ) : (
        // 拖放上传区域
        <label
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={cn(
            'flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-8 transition-colors',
            isDragging
              ? 'border-blue-400 bg-blue-50'
              : 'border-slate-200 bg-slate-50 hover:border-blue-300 hover:bg-blue-50/50'
          )}
        >
          <div
            className={cn(
              'flex h-12 w-12 items-center justify-center rounded-full transition-colors',
              isDragging ? 'bg-blue-100' : 'bg-slate-100'
            )}
          >
            <Upload
              className={cn(
                'h-6 w-6 transition-colors',
                isDragging ? 'text-blue-500' : 'text-slate-400'
              )}
            />
          </div>
          <div className="text-center">
            <p className="font-medium text-slate-700">
              {isDragging ? '释放以上传文件' : '拖放 RIS 文件到这里'}
            </p>
            <p className="mt-1 text-sm text-slate-500">或点击选择文件</p>
          </div>
          <input
            type="file"
            accept=".ris"
            onChange={handleInputChange}
            className="hidden"
          />
        </label>
      )}
    </div>
  );
}

