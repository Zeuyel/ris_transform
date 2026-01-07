'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { FileUploader, ProfileSelector, ProcessButton } from '@/components/features';
import { FileText, Github, Settings } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();

  return (
    <div className="min-h-screen">
      {/* 头部导航 */}
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-600">
              <FileText className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="font-semibold text-slate-900">RIS 文件处理器</h1>
              <p className="text-xs text-slate-500">学术文献分类工具</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => router.push('/settings')}
              className="rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
              title="设置"
            >
              <Settings className="h-5 w-5" />
            </button>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
            >
              <Github className="h-5 w-5" />
            </a>
          </div>
        </div>
      </header>

      {/* 主内容区 */}
      <main className="mx-auto max-w-6xl px-4 py-8">
        <div className="grid gap-8 lg:grid-cols-[1fr_360px]">
          {/* 左侧主区域 */}
          <div className="space-y-8">
            {/* 步骤 1: 上传文件 */}
            <section className="rounded-2xl border border-slate-200 bg-white p-6">
              <div className="mb-4 flex items-center gap-3">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-600">
                  1
                </span>
                <div>
                  <h2 className="font-semibold text-slate-900">上传 RIS 文件</h2>
                  <p className="text-sm text-slate-500">
                    支持从 Scopus、Web of Science 等数据库导出的 RIS 格式文件
                  </p>
                </div>
              </div>
              <FileUploader />
            </section>

            {/* 步骤 2: 选择 Profiles */}
            <section className="rounded-2xl border border-slate-200 bg-white p-6">
              <div className="mb-4 flex items-center gap-3">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-600">
                  2
                </span>
                <div>
                  <h2 className="font-semibold text-slate-900">选择筛选 Profiles</h2>
                  <p className="text-sm text-slate-500">
                    根据预定义的组合标准筛选文献，每个 Profile 输出多份分类文件
                  </p>
                </div>
              </div>
              <ProfileSelector />
            </section>
          </div>

          {/* 右侧操作面板 */}
          <div className="lg:sticky lg:top-24 lg:self-start">
            <section className="rounded-2xl border border-slate-200 bg-white p-6">
              <div className="mb-4 flex items-center gap-3">
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-600">
                  3
                </span>
                <div>
                  <h2 className="font-semibold text-slate-900">处理并下载</h2>
                  <p className="text-sm text-slate-500">
                    生成分类后的 RIS 文件并打包下载
                  </p>
                </div>
              </div>
              <ProcessButton />
            </section>

            {/* 说明卡片 */}
            <div className="mt-4 rounded-xl bg-slate-100 p-4">
              <h3 className="text-sm font-medium text-slate-700">支持的评级体系</h3>
              <ul className="mt-2 space-y-1 text-xs text-slate-500">
                <li>• CCF - 中国计算机学会推荐</li>
                <li>• FMS - 金融管理科学</li>
                <li>• AJG - Academic Journal Guide</li>
                <li>• ZUFE - 浙江财经大学标准</li>
              </ul>
            </div>
          </div>
        </div>
      </main>

      {/* 页脚 */}
      <footer className="border-t border-slate-200 py-6">
        <div className="mx-auto max-w-6xl px-4 text-center text-sm text-slate-500">
          RIS 文件处理器 · 基于 Next.js 构建
        </div>
      </footer>
    </div>
  );
}