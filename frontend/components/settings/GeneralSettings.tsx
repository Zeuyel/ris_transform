'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';
import { useSettingsStore, TranslationEndpoint } from '@/store';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Switch } from '@/components/ui/Switch';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Languages, Plus, Trash2, ChevronDown, ChevronUp } from 'lucide-react';

export function GeneralSettings() {
  const {
    translateTitle,
    translateAbstract,
    translationEndpoints,
    setTranslateTitle,
    setTranslateAbstract,
    setTranslationEndpoints,
  } = useSettingsStore();

  const [expandedEndpoint, setExpandedEndpoint] = useState<string | null>(null);
  const [newEndpointUrl, setNewEndpointUrl] = useState('');

  const handleAddEndpoint = () => {
    if (!newEndpointUrl.trim()) return;

    const newEndpoint: TranslationEndpoint = {
      id: Date.now().toString(),
      url: newEndpointUrl.trim(),
      weight: 1,
      rpm: 60,
      enabled: true,
    };

    setTranslationEndpoints([...translationEndpoints, newEndpoint]);
    setNewEndpointUrl('');
  };

  const handleRemoveEndpoint = (id: string) => {
    setTranslationEndpoints(translationEndpoints.filter((e) => e.id !== id));
  };

  const handleUpdateEndpoint = (id: string, updates: Partial<TranslationEndpoint>) => {
    setTranslationEndpoints(
      translationEndpoints.map((e) => (e.id === id ? { ...e, ...updates } : e))
    );
  };

  const toggleEndpointExpand = (id: string) => {
    setExpandedEndpoint(expandedEndpoint === id ? null : id);
  };

  return (
    <div className="space-y-6">
      {/* 翻译设置 */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Languages className="h-4 w-4 text-blue-600" />
            <CardTitle>翻译设置</CardTitle>
          </div>
          <CardDescription>配置文献标题和摘要的自动翻译</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* 翻译选项 */}
          <div className="space-y-3">
            <Switch
              label="翻译标题"
              description="将英文标题翻译为中文，存储在 C1 字段"
              checked={translateTitle}
              onChange={(e) => setTranslateTitle(e.target.checked)}
            />
            <Switch
              label="翻译摘要"
              description="将英文摘要翻译为中文，追加到 AB 字段"
              checked={translateAbstract}
              onChange={(e) => setTranslateAbstract(e.target.checked)}
            />
          </div>

          {/* API 端点配置 */}
          <div className="border-t pt-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h4 className="text-sm font-medium text-slate-700">翻译 API 端点</h4>
                <p className="text-xs text-slate-500 mt-0.5">
                  配置多个端点实现负载均衡，权重越高使用概率越大
                </p>
              </div>
            </div>

            {/* 端点列表 */}
            <div className="space-y-2 mb-3">
              {translationEndpoints.length === 0 ? (
                <div className="text-center py-6 text-sm text-slate-400 bg-slate-50 rounded-lg border-2 border-dashed">
                  暂无 API 端点，请添加至少一个翻译服务端点
                </div>
              ) : (
                translationEndpoints.map((endpoint) => (
                  <div
                    key={endpoint.id}
                    className={cn(
                      'border rounded-lg overflow-hidden transition-all',
                      endpoint.enabled ? 'bg-white' : 'bg-slate-50 opacity-60'
                    )}
                  >
                    {/* 端点主行 */}
                    <div className="flex items-center gap-2 px-3 py-2">
                      <Switch
                        size="sm"
                        checked={endpoint.enabled}
                        onChange={(e) =>
                          handleUpdateEndpoint(endpoint.id, { enabled: e.target.checked })
                        }
                      />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm truncate font-mono">{endpoint.url}</div>
                        <div className="text-xs text-slate-400">
                          权重: {endpoint.weight} · RPM: {endpoint.rpm}
                          {endpoint.token && ' · 已配置Token'}
                        </div>
                      </div>
                      <button
                        onClick={() => toggleEndpointExpand(endpoint.id)}
                        className="p-1 text-slate-400 hover:text-slate-600"
                      >
                        {expandedEndpoint === endpoint.id ? (
                          <ChevronUp className="h-4 w-4" />
                        ) : (
                          <ChevronDown className="h-4 w-4" />
                        )}
                      </button>
                      <button
                        onClick={() => handleRemoveEndpoint(endpoint.id)}
                        className="p-1 text-slate-400 hover:text-red-500"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>

                    {/* 展开的详细设置 */}
                    {expandedEndpoint === endpoint.id && (
                      <div className="px-3 py-3 bg-slate-50 border-t space-y-3">
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <label className="block text-xs font-medium text-slate-600 mb-1">
                              权重
                            </label>
                            <Input
                              type="number"
                              min={1}
                              max={100}
                              value={endpoint.weight}
                              onChange={(e) =>
                                handleUpdateEndpoint(endpoint.id, {
                                  weight: parseInt(e.target.value) || 1,
                                })
                              }
                              className="text-sm"
                            />
                            <p className="text-xs text-slate-400 mt-1">值越大，被选中概率越高</p>
                          </div>
                          <div>
                            <label className="block text-xs font-medium text-slate-600 mb-1">
                              RPM (每分钟请求数)
                            </label>
                            <Input
                              type="number"
                              min={1}
                              max={1000}
                              value={endpoint.rpm}
                              onChange={(e) =>
                                handleUpdateEndpoint(endpoint.id, {
                                  rpm: parseInt(e.target.value) || 60,
                                })
                              }
                              className="text-sm"
                            />
                            <p className="text-xs text-slate-400 mt-1">限制请求频率</p>
                          </div>
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-slate-600 mb-1">
                            Token / API Key (可选)
                          </label>
                          <Input
                            type="password"
                            value={endpoint.token || ''}
                            onChange={(e) =>
                              handleUpdateEndpoint(endpoint.id, { token: e.target.value })
                            }
                            placeholder="如需认证请填写"
                            className="text-sm font-mono"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>

            {/* 添加新端点 */}
            <div className="flex gap-2">
              <Input
                value={newEndpointUrl}
                onChange={(e) => setNewEndpointUrl(e.target.value)}
                placeholder="https://api.example.com/translate"
                className="flex-1 text-sm font-mono"
                onKeyDown={(e) => e.key === 'Enter' && handleAddEndpoint()}
              />
              <Button size="sm" onClick={handleAddEndpoint} className="whitespace-nowrap">
                <Plus className="h-4 w-4 mr-1" />
                添加
              </Button>
            </div>

            {/* 预设端点快捷添加 */}
            <div className="mt-3 pt-3 border-t">
              <p className="text-xs text-slate-500 mb-2">快速添加常用端点：</p>
              <div className="flex flex-wrap gap-2">
                {[
                  { name: 'DeepLX (missuo)', url: 'https://deeplx.missuo.ru/translate' },
                  { name: 'DeepLX (api)', url: 'https://api.deeplx.org/translate' },
                  { name: 'FindMyIP', url: 'https://findmyip.net/api/translate.php' },
                  { name: 'Edu6', url: 'https://deeplx.edu6.eu.org/translate' },
                ].map((preset) => {
                  const exists = translationEndpoints.some((e) => e.url === preset.url);
                  return (
                    <button
                      key={preset.url}
                      disabled={exists}
                      onClick={() => {
                        const newEndpoint: TranslationEndpoint = {
                          id: Date.now().toString(),
                          url: preset.url,
                          weight: 1,
                          rpm: 60,
                          enabled: true,
                        };
                        setTranslationEndpoints([...translationEndpoints, newEndpoint]);
                      }}
                      className={cn(
                        'px-2 py-1 text-xs rounded border transition-colors',
                        exists
                          ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                          : 'bg-white hover:bg-blue-50 hover:border-blue-300 text-slate-600'
                      )}
                    >
                      {exists ? '✓ ' : '+ '}
                      {preset.name}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

