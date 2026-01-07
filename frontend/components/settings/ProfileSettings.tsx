'use client';

import { useState, useEffect } from 'react';
import { Profile, CriteriaSet, RatingSystem } from '@/types/profiles';

interface ProfileSettingsProps {
  ratingSystems: RatingSystem[];
}

export function ProfileSettings({ ratingSystems }: ProfileSettingsProps) {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingProfile, setEditingProfile] = useState<Profile | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  // 新增：当前选中的 CriteriaSet 名称
  const [selectedSetName, setSelectedSetName] = useState<string | null>(null);

  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    try {
      const response = await fetch('/api/profiles');
      const data = await response.json();
      setProfiles(data.items || []);
    } catch (error) {
      console.error('加载 Profiles 失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingProfile({
      id: '',
      name: '',
      description: '',
      criteria_sets: {}
    });
    setIsCreating(true);
    setSelectedSetName(null);
  };

  const handleEdit = (profile: Profile) => {
    setEditingProfile({ ...profile });
    setIsCreating(false);
    // 默认选中第一个 CriteriaSet
    const setNames = Object.keys(profile.criteria_sets);
    setSelectedSetName(setNames.length > 0 ? setNames[0] : null);
  };

  const handleDelete = async (profileId: string) => {
    if (!confirm(`确定要删除 Profile "${profileId}" 吗？`)) return;

    try {
      const response = await fetch(`/api/profiles/${profileId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        await loadProfiles();
      } else {
        alert('删除失败');
      }
    } catch (error) {
      console.error('删除 Profile 失败:', error);
      alert('删除失败');
    }
  };

  const handleSave = async () => {
    if (!editingProfile) return;

    if (!editingProfile.id.trim()) {
      alert('请输入 Profile ID');
      return;
    }

    try {
      const url = isCreating
        ? '/api/profiles'
        : `/api/profiles/${editingProfile.id}`;
      const method = isCreating ? 'POST' : 'PUT';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editingProfile),
      });

      if (response.ok) {
        await loadProfiles();
        setEditingProfile(null);
        setIsCreating(false);
      } else {
        alert('保存失败');
      }
    } catch (error) {
      console.error('保存 Profile 失败:', error);
      alert('保存失败');
    }
  };

  const handleCancel = () => {
    setEditingProfile(null);
    setIsCreating(false);
    setSelectedSetName(null);
  };

  const addCriteriaSet = () => {
    if (!editingProfile) return;
    const setName = prompt('请输入 CriteriaSet 名称:');
    if (!setName || setName.trim() === '') return;

    if (editingProfile.criteria_sets[setName]) {
      alert('该名称已存在');
      return;
    }

    setEditingProfile({
      ...editingProfile,
      criteria_sets: {
        ...editingProfile.criteria_sets,
        [setName]: { criteria: {} }
      }
    });
    // 自动选中新创建的 CriteriaSet
    setSelectedSetName(setName);
  };

  const removeCriteriaSet = (setName: string) => {
    if (!editingProfile) return;
    if (!confirm(`确定要删除 "${setName}" 吗？`)) return;

    const newSets = { ...editingProfile.criteria_sets };
    delete newSets[setName];
    setEditingProfile({
      ...editingProfile,
      criteria_sets: newSets
    });

    // 如果删除的是当前选中的，切换到其他
    if (selectedSetName === setName) {
      const remaining = Object.keys(newSets);
      setSelectedSetName(remaining.length > 0 ? remaining[0] : null);
    }
  };

  const renameCriteriaSet = (oldName: string) => {
    if (!editingProfile) return;
    const newName = prompt('请输入新名称:', oldName);
    if (!newName || newName.trim() === '' || newName === oldName) return;

    if (editingProfile.criteria_sets[newName]) {
      alert('该名称已存在');
      return;
    }

    const newSets: Record<string, CriteriaSet> = {};
    for (const [key, value] of Object.entries(editingProfile.criteria_sets)) {
      if (key === oldName) {
        newSets[newName] = value;
      } else {
        newSets[key] = value;
      }
    }

    setEditingProfile({
      ...editingProfile,
      criteria_sets: newSets
    });

    if (selectedSetName === oldName) {
      setSelectedSetName(newName);
    }
  };

  const updateCriteriaSet = (setName: string, systemId: string, levels: (string | number)[]) => {
    if (!editingProfile) return;

    const newCriteria = { ...editingProfile.criteria_sets[setName].criteria };
    if (levels.length === 0) {
      delete newCriteria[systemId];
    } else {
      newCriteria[systemId] = levels;
    }

    setEditingProfile({
      ...editingProfile,
      criteria_sets: {
        ...editingProfile.criteria_sets,
        [setName]: { criteria: newCriteria }
      }
    });
  };

  if (loading) {
    return <div className="p-4">加载中...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Profiles 管理</h2>
        <button
          onClick={handleCreate}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          创建新 Profile
        </button>
      </div>

      {/* Profile 列表 */}
      {!editingProfile && (
        <div className="grid gap-4">
          {profiles.length === 0 ? (
            <div className="text-gray-500 text-center py-8">
              暂无 Profiles，点击上方按钮创建
            </div>
          ) : (
            profiles.map((profile) => (
              <div
                key={profile.id}
                className="border rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold">{profile.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{profile.description || '无描述'}</p>
                    <div className="mt-2 text-sm text-gray-500">
                      包含 {Object.keys(profile.criteria_sets).length} 个 CriteriaSet
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(profile)}
                      className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
                    >
                      编辑
                    </button>
                    <button
                      onClick={() => handleDelete(profile.id)}
                      className="px-3 py-1 text-sm bg-red-100 text-red-700 hover:bg-red-200 rounded"
                    >
                      删除
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Profile 编辑器 */}
      {editingProfile && (
        <div className="border rounded-lg p-6 bg-gray-50">
          <h3 className="text-xl font-semibold mb-4">
            {isCreating ? '创建新 Profile' : '编辑 Profile'}
          </h3>

          <div className="space-y-4">
            {/* 基本信息 */}
            <div>
              <label className="block text-sm font-medium mb-1">Profile ID</label>
              <input
                type="text"
                value={editingProfile.id}
                onChange={(e) => setEditingProfile({ ...editingProfile, id: e.target.value })}
                disabled={!isCreating}
                className="w-full px-3 py-2 border rounded disabled:bg-gray-100"
                placeholder="例如: zufe"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">名称</label>
              <input
                type="text"
                value={editingProfile.name}
                onChange={(e) => setEditingProfile({ ...editingProfile, name: e.target.value })}
                className="w-full px-3 py-2 border rounded"
                placeholder="显示名称"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">描述</label>
              <textarea
                value={editingProfile.description}
                onChange={(e) => setEditingProfile({ ...editingProfile, description: e.target.value })}
                className="w-full px-3 py-2 border rounded"
                rows={2}
                placeholder="可选描述"
              />
            </div>

            {/* CriteriaSets 管理 - 左右分栏设计 */}
            <div className="border-t pt-4">
              <div className="flex justify-between items-center mb-3">
                <h4 className="font-medium">CriteriaSets（分组标准）</h4>
                <button
                  onClick={addCriteriaSet}
                  className="px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700"
                >
                  + 添加分组
                </button>
              </div>

              {Object.keys(editingProfile.criteria_sets).length === 0 ? (
                <div className="text-gray-500 text-sm text-center py-8 bg-gray-50 rounded border-2 border-dashed">
                  暂无分组，点击上方按钮添加第一个 CriteriaSet
                </div>
              ) : (
                <div className="flex gap-4">
                  {/* 左侧：分组列表 */}
                  <div className="w-48 flex-shrink-0">
                    <div className="text-sm font-medium text-gray-600 mb-2">分组列表</div>
                    <div className="border rounded bg-white">
                      {Object.keys(editingProfile.criteria_sets).map((setName) => (
                        <div
                          key={setName}
                          onClick={() => setSelectedSetName(setName)}
                          className={`px-3 py-2 cursor-pointer border-b last:border-b-0 flex justify-between items-center group ${
                            selectedSetName === setName
                              ? 'bg-blue-50 border-l-4 border-l-blue-600'
                              : 'hover:bg-gray-50'
                          }`}
                        >
                          <span className={selectedSetName === setName ? 'font-medium text-blue-700' : ''}>
                            {setName}
                          </span>
                          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button
                              onClick={(e) => { e.stopPropagation(); renameCriteriaSet(setName); }}
                              className="text-xs text-gray-500 hover:text-blue-600 px-1"
                              title="重命名"
                            >
                              ✏️
                            </button>
                            <button
                              onClick={(e) => { e.stopPropagation(); removeCriteriaSet(setName); }}
                              className="text-xs text-gray-500 hover:text-red-600 px-1"
                              title="删除"
                            >
                              🗑️
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 右侧：评级系统选择 */}
                  <div className="flex-1 border rounded p-4 bg-white">
                    {selectedSetName && editingProfile.criteria_sets[selectedSetName] ? (
                      <>
                        <div className="text-lg font-medium mb-4 pb-2 border-b">
                          编辑分组: <span className="text-blue-600">{selectedSetName}</span>
                        </div>
                        <div className="text-sm text-gray-600 mb-4">
                          点击等级按钮选择/取消该等级。蓝色表示已选中。
                        </div>
                        <div className="space-y-4">
                          {ratingSystems.map((system) => {
                            const criteriaSet = editingProfile.criteria_sets[selectedSetName];
                            const selectedLevels = criteriaSet?.criteria?.[system.id] || [];

                            // 获取按类型分组的等级
                            const levelsByType = system.levels_by_type || {};
                            const typeNames = Object.keys(levelsByType);
                            const hasTypes = typeNames.length > 0 && !(typeNames.length === 1 && typeNames[0] === '');

                            // 使用字符串比较来检查是否选中
                            // 对于有类型的系统，存储格式为 "等级类型"（如 "A期刊"）
                            const isLevelSelected = (level: string | number, typeName?: string) => {
                              const valueToCheck = typeName ? `${level}${typeName}` : String(level);
                              return selectedLevels.some(
                                (selected) => String(selected) === valueToCheck
                              );
                            };

                            const handleLevelClick = (level: string | number, typeName?: string) => {
                              const valueToStore = typeName ? `${level}${typeName}` : String(level);
                              const isSelected = isLevelSelected(level, typeName);
                              let newLevels: (string | number)[];
                              if (isSelected) {
                                newLevels = selectedLevels.filter(
                                  (l) => String(l) !== valueToStore
                                );
                              } else {
                                newLevels = [...selectedLevels, valueToStore];
                              }
                              updateCriteriaSet(selectedSetName, system.id, newLevels);
                            };

                            return (
                              <div key={system.id} className="border rounded p-3 bg-gray-50">
                                <div className="font-medium text-sm mb-3 flex items-center gap-2">
                                  <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                                  {system.name}
                                  <span className="text-xs text-gray-400">({system.id})</span>
                                </div>

                                {hasTypes ? (
                                  // 按类型分组显示
                                  <div className="space-y-3">
                                    {typeNames.map((typeName) => {
                                      const typeLevels = levelsByType[typeName] || [];
                                      return (
                                        <div key={typeName} className="pl-3 border-l-2 border-blue-200">
                                          <div className="text-sm font-medium text-gray-600 mb-2">
                                            {typeName}
                                          </div>
                                          <div className="flex flex-wrap gap-2">
                                            {typeLevels.map((level) => {
                                              const isSelected = isLevelSelected(level, typeName);
                                              return (
                                                <button
                                                  key={`${level}-${typeName}`}
                                                  onClick={() => handleLevelClick(level, typeName)}
                                                  className={`px-4 py-2 text-sm rounded-md transition-all ${
                                                    isSelected
                                                      ? 'bg-blue-600 text-white shadow-sm'
                                                      : 'bg-white border border-gray-300 hover:border-blue-400 hover:bg-blue-50'
                                                  }`}
                                                >
                                                  {level}
                                                </button>
                                              );
                                            })}
                                          </div>
                                        </div>
                                      );
                                    })}
                                  </div>
                                ) : (
                                  // 不分类型，直接显示所有等级
                                  <div className="flex flex-wrap gap-2">
                                    {(system.levels || []).map((level) => {
                                      const isSelected = isLevelSelected(level);
                                      return (
                                        <button
                                          key={String(level)}
                                          onClick={() => handleLevelClick(level)}
                                          className={`px-4 py-2 text-sm rounded-md transition-all ${
                                            isSelected
                                              ? 'bg-blue-600 text-white shadow-sm'
                                              : 'bg-white border border-gray-300 hover:border-blue-400 hover:bg-blue-50'
                                          }`}
                                        >
                                          {level}
                                        </button>
                                      );
                                    })}
                                    {(system.levels || []).length === 0 && (
                                      <span className="text-gray-400 text-sm">暂无可用等级</span>
                                    )}
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      </>
                    ) : (
                      <div className="text-gray-500 text-center py-8">
                        ← 请从左侧选择一个分组进行编辑
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* 操作按钮 */}
            <div className="flex gap-3 pt-4">
              <button
                onClick={handleSave}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                保存
              </button>
              <button
                onClick={handleCancel}
                className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
