'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { ArrowLeft, Settings2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { GeneralSettings } from '@/components/settings/GeneralSettings';
import { ProfileSettings } from '@/components/settings/ProfileSettings';
import { RatingSystemSettings } from '@/components/settings/RatingSystemSettings';
import { Suspense, useEffect, useState } from 'react';
import { RatingSystem } from '@/types/profiles';

function SettingsContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const defaultTab = searchParams.get('tab') || 'general';
  const [ratingSystems, setRatingSystems] = useState<RatingSystem[]>([]);

  useEffect(() => {
    // 加载评级系统
    async function loadRatingSystems() {
      try {
        const res = await fetch('/api/rating-systems');
        if (res.ok) {
          const data = await res.json();
          setRatingSystems(data.items || []);
        }
      } catch (error) {
        console.error('加载评级系统失败:', error);
      }
    }
    loadRatingSystems();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50">
      {/* 头部 */}
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm" onClick={() => router.push('/')}>
              <ArrowLeft className="h-4 w-4 mr-1" />
              返回
            </Button>
            <div className="h-6 w-px bg-slate-200" />
            <div className="flex items-center gap-2">
              <Settings2 className="h-5 w-5 text-slate-500" />
              <h1 className="font-semibold text-slate-900">设置面板</h1>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8">
        <Tabs defaultValue={defaultTab} className="space-y-6">
          <TabsList className="w-full justify-start bg-white p-1 border border-slate-200 rounded-lg shadow-sm">
            <TabsTrigger value="general" className="flex-1 sm:flex-none">常规设置</TabsTrigger>
            <TabsTrigger value="profiles" className="flex-1 sm:flex-none">Profiles 管理</TabsTrigger>
            <TabsTrigger value="systems" className="flex-1 sm:flex-none">评级系统</TabsTrigger>
          </TabsList>

          <TabsContent value="general" className="animate-in fade-in-50 slide-in-from-left-2 duration-300">
            <GeneralSettings />
          </TabsContent>

          <TabsContent value="profiles" className="animate-in fade-in-50 slide-in-from-left-2 duration-300">
            <ProfileSettings ratingSystems={ratingSystems} />
          </TabsContent>

          <TabsContent value="systems" className="animate-in fade-in-50 slide-in-from-left-2 duration-300">
            <RatingSystemSettings />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

export default function SettingsPage() {
  return (
    <Suspense>
      <SettingsContent />
    </Suspense>
  );
}

