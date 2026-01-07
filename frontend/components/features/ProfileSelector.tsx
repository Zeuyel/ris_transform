'use client';

import { useEffect } from 'react';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/store';
import { Check, Plus } from 'lucide-react';
import { useRouter } from 'next/navigation';

interface ProfileSelectorProps {
  className?: string;
}

export function ProfileSelector({ className }: ProfileSelectorProps) {
  const router = useRouter();
  const {
    profilesList,
    selectedProfiles,
    setProfilesList,
    toggleProfile,
    selectAllProfiles,
    clearProfiles,
  } = useAppStore();

  // 加载 Profiles 列表
  useEffect(() => {
    async function loadProfiles() {
      try {
        const res = await fetch('/api/profiles');
        if (!res.ok) throw new Error('加载失败');
        const data = await res.json();
        setProfilesList(data.items || []);
      } catch (error) {
        console.error('加载 Profiles 失败:', error);
      }
    }

    if (profilesList.length === 0) {
      loadProfiles();
    }
  }, [profilesList.length, setProfilesList]);

  const allSelected = profilesList.length > 0 && selectedProfiles.length === profilesList.length;
  const someSelected = selectedProfiles.length > 0;

  return (
    <div className={cn('space-y-4', className)}>
      {/* 头部操作 */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="font-semibold text-slate-900">筛选 Profiles</h3>
          <p className="text-sm text-slate-500">
            已选择 {selectedProfiles.length} / {profilesList.length}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => router.push('/settings?tab=profiles')}
            className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium text-blue-600 transition-colors hover:bg-blue-50"
          >
            <Plus className="h-4 w-4" />
            管理
          </button>
          <button
            onClick={selectAllProfiles}
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
            onClick={clearProfiles}
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

      {/* Profile 卡片网格 */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        {profilesList.map((item) => {
          const isSelected = selectedProfiles.includes(item.id);
          const criteriaSetCount = Object.keys(item.criteria_sets).length;

          return (
            <button
              key={item.id}
              onClick={() => toggleProfile(item.id)}
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

              {/* Profile 信息 */}
              <span
                className={cn(
                  'font-semibold',
                  isSelected ? 'text-blue-700' : 'text-slate-900'
                )}
              >
                {item.name}
              </span>
              <span className="mt-0.5 text-xs text-slate-500">
                {criteriaSetCount} 个 CriteriaSet
              </span>
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
      {profilesList.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-200 py-8">
          <p className="text-slate-500">加载中...</p>
        </div>
      )}
    </div>
  );
}

