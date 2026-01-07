'use client';

import { useEffect } from 'react';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/store';
import { Check, Plus } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface CriteriaSelectorProps {
  className?: string;
}

export function CriteriaSelector({ className }: CriteriaSelectorProps) {
  const router = useRouter();
  const {
    criteriaList,
    selectedCriteria,
    setCriteriaList,
    toggleCriteria,
    selectAllCriteria,
    clearCriteria,
  } = useAppStore();

  // 加载分类标准列表（包括自定义）
  useEffect(() => {
    async function loadCriteria() {
      try {
        const res = await fetch('/api/criteria');
        if (!res.ok) throw new Error('加载失败');
        const data = await res.json();

        // 合并自定义标准
        const customCriteria = localStorage.getItem('custom-criteria');
        let allCriteria = data.items || [];

        if (customCriteria) {
          try {
            const custom = JSON.parse(customCriteria);
            allCriteria = [
              ...allCriteria,
              ...custom.map((c: any) => ({
                id: c.id,
                name: c.name,
                description: c.description || `自定义: ${Object.keys(c.definition).join(', ')}`,
              })),
            ];
          } catch (e) {
            console.error('加载自定义标准失败:', e);
          }
        }

        setCriteriaList(allCriteria);
      } catch (error) {
        console.error('加载分类标准失败:', error);
      }
    }

    if (criteriaList.length === 0) {
      loadCriteria();
    }
  }, [criteriaList.length, setCriteriaList]);

  const allSelected = criteriaList.length > 0 && selectedCriteria.length === criteriaList.length;
  const someSelected = selectedCriteria.length > 0;

  return (
    <div className={cn('space-y-4', className)}>
      {/* 头部操作 */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-slate-900">分类标准</h3>
          <p className="text-sm text-slate-500">
            已选择 {selectedCriteria.length} / {criteriaList.length}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => router.push('/settings?tab=criteria')}
            className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium text-blue-600 transition-colors hover:bg-blue-50"
          >
            <Plus className="h-4 w-4" />
            自定义
          </button>
          <button
            onClick={selectAllCriteria}
            disabled={allSelected}
            className={cn(
              'rounded-lg px-3 py-1.5 text-sm font-medium transition-colors',
              allSelected
                ? 'cursor-not-allowed text-slate-300'
                : 'text-blue-600 hover:bg-blue-50'
            )}
          >
            全选
          </button>
          <button
            onClick={clearCriteria}
            disabled={!someSelected}
            className={cn(
              'rounded-lg px-3 py-1.5 text-sm font-medium transition-colors',
              !someSelected
                ? 'cursor-not-allowed text-slate-300'
                : 'text-slate-600 hover:bg-slate-100'
            )}
          >
            清除
          </button>
        </div>
      </div>

      {/* 标准卡片网格 */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        {criteriaList.map((item) => {
          const isSelected = selectedCriteria.includes(item.id);

          return (
            <button
              key={item.id}
              onClick={() => toggleCriteria(item.id)}
              className={cn(
                'group relative flex flex-col items-start rounded-xl border p-3 text-left transition-all',
                isSelected
                  ? 'border-blue-300 bg-blue-50 ring-1 ring-blue-200'
                  : 'border-slate-200 bg-white hover:border-blue-200 hover:bg-slate-50'
              )}
            >
              {/* 选中标记 */}
              <div
                className={cn(
                  'absolute right-2 top-2 flex h-5 w-5 items-center justify-center rounded-full transition-all',
                  isSelected
                    ? 'bg-blue-500 text-white'
                    : 'border border-slate-200 bg-white group-hover:border-blue-200'
                )}
              >
                {isSelected && <Check className="h-3 w-3" />}
              </div>

              {/* 标准信息 */}
              <span
                className={cn(
                  'font-semibold',
                  isSelected ? 'text-blue-700' : 'text-slate-900'
                )}
              >
                {item.name}
              </span>
              <span className="mt-0.5 text-xs text-slate-500">{item.id}</span>
              {item.description && (
                <span className="mt-1 line-clamp-2 text-xs text-slate-400">
                  {item.description}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* 空状态 */}
      {criteriaList.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 py-8">
          <p className="text-slate-500">加载中...</p>
        </div>
      )}
    </div>
  );
}

