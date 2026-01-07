'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Trash2, Save, Edit2, Plus, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useSettingsStore } from '@/store';
import { Switch } from '@/components/ui/Switch';

interface RatingSystem {
  id: string;
  name: string;
  description: string;
  enabled?: boolean;
}

interface RatingSystemForm {
  id: string;
  name: string;
  description: string;
  levels: string[];
}

export function RatingSystemSettings() {
  const [systems, setSystems] = useState<RatingSystem[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [formData, setFormData] = useState<RatingSystemForm>({ id: '', name: '', description: '', levels: [] });
  const [levelInput, setLevelInput] = useState('');
  
  // 从 Store 获取启用状态控制
  const { ratingSystems: storeSystems, toggleRatingSystem } = useSettingsStore();

  useEffect(() => {
    loadSystems();
  }, []);

  const loadSystems = async () => {
    try {
      const res = await fetch('/api/rating-systems');
      if (res.ok) {
        const data = await res.json();
        setSystems(data.items || []);
      }
    } catch (error) { console.error(error); }
  };

  const handleSave = async () => {
    if (!formData.id || !formData.name || formData.levels.length === 0) return alert('请填写完整信息');
    try {
      const res = await fetch('/api/rating-systems', {
        method: 'POST',
        body: JSON.stringify({ id: formData.id, name: formData.name, description: formData.description }),
      });
      if (!res.ok) throw new Error('保存失败');
      
      localStorage.setItem(`rating-levels-${formData.id}`, JSON.stringify(formData.levels));
      await loadSystems();
      resetForm();
    } catch (e) { alert((e as Error).message); }
  };

  const handleDelete = async (id: string) => {
    if (!confirm(`确定删除 ${id}？`)) return;
    try {
      const res = await fetch(`/api/rating-systems?id=${id}`, { method: 'DELETE' });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || '删除失败');
      }
      localStorage.removeItem(`rating-levels-${id}`);
      await loadSystems();
    } catch (e) { alert((e as Error).message); }
  };

  const resetForm = () => {
    setFormData({ id: '', name: '', description: '', levels: [] });
    setEditingId(null);
    setIsCreating(false);
  };

  const startEdit = (sys: RatingSystem) => {
    const saved = localStorage.getItem(`rating-levels-${sys.id}`);
    setFormData({
      id: sys.id,
      name: sys.name,
      description: sys.description,
      levels: saved ? JSON.parse(saved) : [],
    });
    setEditingId(sys.id);
    setIsCreating(false);
  };

  const handleAddLevel = () => {
    if (!levelInput.trim()) return;
    if (!formData.levels.includes(levelInput.trim())) {
      setFormData(prev => ({ ...prev, levels: [...prev.levels, levelInput.trim()] }));
    }
    setLevelInput('');
  };

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
      <div className={cn('space-y-4', (isCreating || editingId) ? 'hidden lg:block' : 'block')}>
         <div className="flex items-center justify-between">
            <h3 className="font-semibold text-slate-900">评级系统列表</h3>
            <Button size="sm" onClick={() => { resetForm(); setIsCreating(true); }} disabled={isCreating || !!editingId}>
              <Plus className="h-4 w-4 mr-1" /> 新建系统
            </Button>
         </div>

         <div className="space-y-3">
            {systems.map((system) => {
              // Store 中的启用状态
              const isEnabled = storeSystems.find(s => s.id === system.id)?.enabled ?? true;
              const savedLevels = localStorage.getItem(`rating-levels-${system.id}`);
              const levels = savedLevels ? JSON.parse(savedLevels) : [];

              return (
                <Card key={system.id}>
                   <CardContent className="flex items-center justify-between p-4">
                      <div>
                        <div className="flex items-center gap-3">
                           <h4 className="font-semibold text-slate-900">{system.name}</h4>
                           <span className="text-xs bg-slate-100 px-1.5 py-0.5 rounded text-slate-500">{system.id}</span>
                        </div>
                        <p className="text-sm text-slate-500 mt-1">{system.description}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                           {levels.map((l: string) => <span key={l} className="text-[10px] bg-slate-50 px-1.5 rounded border border-slate-100">{l}</span>)}
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <Switch checked={isEnabled} onChange={() => toggleRatingSystem(system.id)} />
                        <div className="flex gap-1">
                          <button onClick={() => startEdit(system)} className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded"><Edit2 className="h-4 w-4" /></button>
                          <button onClick={() => handleDelete(system.id)} className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded"><Trash2 className="h-4 w-4" /></button>
                        </div>
                      </div>
                   </CardContent>
                </Card>
              );
            })}
         </div>
      </div>

      {(isCreating || editingId) && (
        <Card className="h-fit border-blue-200 shadow-lg lg:sticky lg:top-4">
          <CardHeader className="border-b border-slate-100 bg-slate-50/50 flex flex-row items-center justify-between py-3">
            <CardTitle className="text-base">{editingId ? '编辑系统' : '新建系统'}</CardTitle>
            <button onClick={resetForm}><X className="h-4 w-4 text-slate-400" /></button>
          </CardHeader>
          <CardContent className="space-y-4 p-4">
             <Input label="ID" value={formData.id} onChange={e => setFormData({...formData, id: e.target.value.toUpperCase()})} disabled={!!editingId} placeholder="SYSTEM_ID" />
             <Input label="名称" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} placeholder="系统名称" />
             <Input label="描述" value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} placeholder="描述" />
             
             <div className="space-y-2">
                <label className="text-xs font-medium text-slate-500">等级列表</label>
                <div className="flex gap-2">
                   <Input value={levelInput} onChange={e => setLevelInput(e.target.value)} placeholder="输入等级按回车" onKeyDown={e => e.key === 'Enter' && handleAddLevel()} className="h-8 text-xs" />
                   <Button size="sm" onClick={handleAddLevel} className="h-8">添加</Button>
                </div>
                <div className="flex flex-wrap gap-1.5">
                   {formData.levels.map(l => (
                     <span key={l} className="flex items-center gap-1 bg-slate-100 px-2 py-1 rounded text-xs">
                        {l} 
                        <button onClick={() => setFormData(p => ({...p, levels: p.levels.filter(x => x !== l)}))} className="text-slate-400 hover:text-rose-500">×</button>
                     </span>
                   ))}
                </div>
             </div>

             <div className="flex gap-2 pt-2">
                <Button onClick={handleSave} className="flex-1">保存</Button>
                <Button variant="secondary" onClick={resetForm}>取消</Button>
             </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

