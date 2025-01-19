import json
import os
from typing import Dict, List, Optional
from .data_types import *

class DataManager:
    """数据管理类"""
    
    def __init__(self, base_path: str, config_path: str):
        """初始化数据管理器
        
        Args:
            base_path: 基础路径，所有相对路径都基于此路径
            config_path: 配置文件路径
        """
        self.base_path = base_path
        self.config_path = config_path
        self.config = self._load_config()
        self.rating_data: Dict[RatingSystem, List[JournalRating]] = {}
        self.selection_criteria: Dict[str, Dict[RatingSystem, List[str]]] = {}
        self.selection_profiles: Dict[str, Dict[str, Dict[RatingSystem, List[str]]]] = {}
        
        # 创建必要的目录
        self.criteria_dir = os.path.join(self.base_path, 'criteria')
        self.profiles_dir = os.path.join(self.base_path, 'profiles')
        os.makedirs(self.criteria_dir, exist_ok=True)
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        # 加载所有数据
        self._load_all_data()
    
    def _load_config(self) -> DataConfig:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            # 加载评级系统配置
            rating_systems = RatingSystem.from_config(config_data)
                
            # 将相对路径转换为绝对路径
            rating_file_paths = {}
            for system, rel_path in config_data.get('rating_file_paths', {}).items():
                if system in rating_systems:  # 只加载已定义的评级系统的文件路径
                    abs_path = os.path.join(self.base_path, rel_path)
                    rating_file_paths[system] = abs_path
                
            return DataConfig(
                rating_systems=rating_systems,
                rating_file_paths=rating_file_paths,
                json_attribute_mapping=config_data.get('json_attribute_mapping', {}),
                token_missuo=config_data.get('token_missuo', ''),
                token_linuxdo=config_data.get('token_linuxdo', ''),
                output_directory=config_data.get('output_directory', ''),
                subfolder=config_data.get('subfolder', '')
            )
        except FileNotFoundError:
            # 如果配置文件不存在，返回默认配置
            return DataConfig()
            
    def _load_all_data(self):
        """加载所有数据"""
        # 加载评级数据
        for system, file_path in self.config.rating_file_paths.items():
            if os.path.exists(file_path):
                self.rating_data[system] = self._load_rating_data(system, file_path)
            
        # 加载基础筛选标准
        self._load_all_criteria()
        
        # 加载组合筛选标准
        self._load_all_profiles()
    
    def _load_rating_data(self, system: RatingSystem, file_path: str) -> List[JournalRating]:
        """加载评级数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
        mapping = self.config.json_attribute_mapping[system]
        return [
            JournalRating(
                paper_name=item[mapping['paper_name']],
                level=item[mapping['level']],
                type=item.get(mapping.get('type', '')) if 'type' in mapping else None
            )
            for item in data
        ]
    
    def _load_all_criteria(self):
        """加载所有基础筛选标准"""
        if not os.path.exists(self.criteria_dir):
            return
            
        for file_name in os.listdir(self.criteria_dir):
            if file_name.endswith('.json'):
                name = file_name[:-5]  # 移除.json后缀
                file_path = os.path.join(self.criteria_dir, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    criteria_data = json.load(f)
                    self.selection_criteria[name] = {
                        system: levels
                        for system, levels in criteria_data.items()
                        if system in self.config.rating_systems  # 只加载已定义的评级系统
                    }
    
    def _load_all_profiles(self):
        """加载所有组合筛选标准"""
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir, exist_ok=True)
            return
            
        for file_name in os.listdir(self.profiles_dir):
            if file_name.endswith('.json'):
                name = file_name[:-5]  # 移除.json后缀
                file_path = os.path.join(self.profiles_dir, file_name)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        profile_data = json.load(f)
                        # 直接使用加载的数据，不需要转换
                        if 'criteria_sets' in profile_data:
                            self.selection_profiles[name] = profile_data['criteria_sets']
                except Exception as e:
                    print(f"加载组合标准文件 {file_path} 时出错: {str(e)}")
                    continue
    
    def save_criteria(self, name: str, criteria: Dict[str, dict]):
        """保存基础筛选标准
        
        Args:
            name: 标准名称
            criteria: 评级系统 -> 等级列表的映射
        """
        file_path = os.path.join(self.criteria_dir, f'{name}.json')
        
        # 确保 criteria 目录存在
        os.makedirs(self.criteria_dir, exist_ok=True)
        
        # 直接使用传入的 criteria 数据，不需要转换
        data = {}
        for system_id, system_criteria in criteria.items():
            data[system_id] = system_criteria
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        # 更新内存中的数据
        self.selection_criteria[name] = criteria
    
    def save_profile(self, name: str, profile: Dict[str, Dict[str, List[str]]]):
        """保存组合筛选标准
        
        Args:
            name: 配置名称
            profile: 分组名称 -> (评级系统 -> 等级列表)的映射
        """
        file_path = os.path.join(self.profiles_dir, f'{name}.json')
        
        # 确保 profiles 目录存在
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        # 直接使用传入的 profile 数据，不需要转换
        data = {
            'name': name,
            'criteria_sets': profile
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        # 更新内存中的数据
        self.selection_profiles[name] = profile
    
    def delete_criteria(self, name: str) -> bool:
        """删除基础筛选标准
        
        Args:
            name: 标准名称
            
        Returns:
            bool: 是否删除成功
        """
        file_path = os.path.join(self.criteria_dir, f'{name}.json')
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            if name in self.selection_criteria:
                del self.selection_criteria[name]
            return True
        except:
            return False
    
    def delete_profile(self, name: str) -> bool:
        """删除组合筛选标准
        
        Args:
            name: 配置名称
            
        Returns:
            bool: 是否删除成功
        """
        file_path = os.path.join(self.profiles_dir, f'{name}.json')
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            if name in self.selection_profiles:
                del self.selection_profiles[name]
            return True
        except:
            return False
    
    def get_rating_data(self, system: RatingSystem) -> List[JournalRating]:
        """获取评级数据"""
        return self.rating_data.get(system, [])
    
    def get_selection_criteria(self) -> Dict[str, Dict[RatingSystem, List[str]]]:
        """获取所有基础筛选标准"""
        return self.selection_criteria
    
    def get_selection_profiles(self) -> Dict[str, Dict[str, Dict[RatingSystem, List[str]]]]:
        """获取所有组合筛选标准"""
        return self.selection_profiles
    
    def get_profile(self, name: str) -> Optional[Dict[str, Dict[RatingSystem, List[str]]]]:
        """获取指定的组合筛选标准"""
        return self.selection_profiles.get(name)
    
    def get_criteria(self, name: str) -> Optional[Dict[RatingSystem, List[str]]]:
        """获取指定的基础筛选标准"""
        return self.selection_criteria.get(name)
    
    def save_rating_data(self, system: RatingSystem, ratings: List[JournalRating]):
        """保存评级数据"""
        file_path = self.config.rating_file_paths[system]
        mapping = self.config.json_attribute_mapping[system]
        
        data = []
        for rating in ratings:
            item = {
                mapping['paper_name']: rating.paper_name,
                mapping['level']: rating.level
            }
            if 'type' in mapping and rating.type:
                item[mapping['type']] = rating.type
            data.append(item)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        # 更新内存中的数据
        self.rating_data[system] = ratings
    
    def update_profile_criteria_set(self, profile_name: str, set_name: str, 
                                criteria: Dict[RatingSystem, List[str]]) -> bool:
        """更新指定profile中的某个criteria set
        
        Args:
            profile_name: profile名称
            set_name: 要更新的criteria set名称
            criteria: 新的评级系统 -> 等级列表的映射
            
        Returns:
            bool: 更新是否成功
        """
        if profile_name not in self.selection_profiles:
            return False
            
        # 更新内存中的数据
        self.selection_profiles[profile_name][set_name] = criteria
        
        # 保存到文件
        file_path = os.path.join(self.profiles_dir, f'{profile_name}.json')
        try:
            data = {
                'name': profile_name,
                'criteria_sets': {
                    set_name: {
                        system.value: levels
                        for system, levels in criteria_set.items()
                    }
                    for set_name, criteria_set in self.selection_profiles[profile_name].items()
                }
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def add_profile_criteria_set(self, profile_name: str, set_name: str, 
                             criteria: Dict[RatingSystem, List[str]]) -> bool:
        """向指定profile添加新的criteria set
        
        Args:
            profile_name: profile名称
            set_name: 新的criteria set名称
            criteria: 评级系统 -> 等级列表的映射
            
        Returns:
            bool: 添加是否成功
        """
        if profile_name not in self.selection_profiles:
            return False
            
        if set_name in self.selection_profiles[profile_name]:
            return False  # 已存在同名的criteria set
            
        # 更新内存中的数据
        self.selection_profiles[profile_name][set_name] = criteria
        
        # 保存到文件
        return self.update_profile_criteria_set(profile_name, set_name, criteria)
    
    def remove_profile_criteria_set(self, profile_name: str, set_name: str) -> bool:
        """从指定profile中删除criteria set
        
        Args:
            profile_name: profile名称
            set_name: 要删除的criteria set名称
            
        Returns:
            bool: 删除是否成功
        """
        if profile_name not in self.selection_profiles:
            return False
            
        if set_name not in self.selection_profiles[profile_name]:
            return False
            
        # 更新内存中的数据
        del self.selection_profiles[profile_name][set_name]
        
        # 保存到文件
        file_path = os.path.join(self.profiles_dir, f'{profile_name}.json')
        try:
            data = {
                'name': profile_name,
                'criteria_sets': {
                    set_name: {
                        system.value: levels
                        for system, levels in criteria_set.items()
                    }
                    for set_name, criteria_set in self.selection_profiles[profile_name].items()
                }
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def rename_profile_criteria_set(self, profile_name: str, old_name: str, new_name: str) -> bool:
        """重命名profile中的criteria set
        
        Args:
            profile_name: profile名称
            old_name: 原criteria set名称
            new_name: 新criteria set名称
            
        Returns:
            bool: 重命名是否成功
        """
        if profile_name not in self.selection_profiles:
            return False
            
        if old_name not in self.selection_profiles[profile_name]:
            return False
            
        if new_name in self.selection_profiles[profile_name]:
            return False  # 新名称已存在
            
        # 更新内存中的数据
        criteria = self.selection_profiles[profile_name][old_name]
        del self.selection_profiles[profile_name][old_name]
        self.selection_profiles[profile_name][new_name] = criteria
        
        # 保存到文件
        file_path = os.path.join(self.profiles_dir, f'{profile_name}.json')
        try:
            data = {
                'name': profile_name,
                'criteria_sets': {
                    set_name: {
                        system.value: levels
                        for system, levels in criteria_set.items()
                    }
                    for set_name, criteria_set in self.selection_profiles[profile_name].items()
                }
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def save_config(self):
        """保存配置到文件"""
        try:
            config_data = {
                'rating_systems': self.config.rating_systems,
                'rating_file_paths': {
                    system: os.path.relpath(path, self.base_path)
                    for system, path in self.config.rating_file_paths.items()
                },
                'json_attribute_mapping': self.config.json_attribute_mapping,
                'token_missuo': self.config.token_missuo,
                'token_linuxdo': self.config.token_linuxdo,
                'output_directory': self.config.output_directory,
                'subfolder': self.config.subfolder
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存配置文件出错：{str(e)}")
            return False
            
    def update_config(self, **kwargs):
        """更新配置
        
        Args:
            **kwargs: 要更新的配置项，可以包含：
                - token_missuo: str
                - token_linuxdo: str
                - output_directory: str
                - subfolder: str
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def get_rating_systems(self) -> Dict[str, Dict[str, str]]:
        """获取所有评级系统配置"""
        return self.config.rating_systems
        
    def add_rating_system(self, system_id: str, name: str, description: str = "") -> bool:
        """添加新的评级系统
        
        Args:
            system_id: 系统ID（如 'CCF', 'FMS'）
            name: 系统名称
            description: 系统描述
            
        Returns:
            bool: 是否添加成功
        """
        if system_id in self.config.rating_systems:
            return False
            
        self.config.rating_systems[system_id] = {
            'name': name,
            'description': description
        }
        return self.save_config()
        
    def remove_rating_system(self, system_id: str) -> bool:
        """删除评级系统
        
        Args:
            system_id: 系统ID
            
        Returns:
            bool: 是否删除成功
        """
        if system_id not in self.config.rating_systems:
            return False
            
        # 删除相关数据
        del self.config.rating_systems[system_id]
        if system_id in self.config.rating_file_paths:
            del self.config.rating_file_paths[system_id]
        if system_id in self.config.json_attribute_mapping:
            del self.config.json_attribute_mapping[system_id]
            
        # 从所有criteria和profile中删除该系统
        for criteria in self.selection_criteria.values():
            if system_id in criteria:
                del criteria[system_id]
                
        for profile in self.selection_profiles.values():
            for criteria_set in profile.values():
                if system_id in criteria_set:
                    del criteria_set[system_id]
                    
        return self.save_config()
    
    def add_rating_file(self, system_id: str, file_path: str, json_attribute_mapping: dict):
        """添加评级系统的数据文件
        Args:
            system_id: 评级系统ID
            file_path: 文件路径
            json_attribute_mapping: JSON属性映射，包含paper_name和level字段
        """
        # 检查系统是否存在
        if system_id not in self.config.rating_systems:
            raise ValueError(f"评级系统 {system_id} 不存在")
        
        # 更新文件路径
        self.config.rating_file_paths[system_id] = file_path
        
        # 更新属性映射
        self.config.json_attribute_mapping[system_id] = json_attribute_mapping
        
        # 保存配置
        self.save_config()
        
        # 重新加载数据
        self._load_all_data()
    
    def update_rating_file(self, system_id: str, file_path: str) -> bool:
        """更新评级文件
        
        Args:
            system_id: 评级系统ID
            file_path: 新的评级文件路径
            
        Returns:
            bool: 是否更新成功
        """
        try:
            # 确保评级系统存在
            if system_id not in self.config.rating_systems:
                return False
                
            # 获取原有的属性映射
            mapping = self.config.json_attribute_mapping.get(system_id, {})
            
            # 使用原有的属性映射更新文件
            return self.add_rating_file(
                system_id=system_id,
                file_path=file_path,
                json_attribute_mapping=mapping
            )
            
        except Exception as e:
            print(f"更新评级文件出错：{str(e)}")
            return False
            
    def remove_rating_file(self, system_id: str) -> bool:
        """删除评级文件
        
        Args:
            system_id: 评级系统ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            # 确保评级系统存在
            if system_id not in self.config.rating_file_paths:
                return False
                
            # 获取文件路径
            file_path = os.path.join(self.base_path, self.config.rating_file_paths[system_id])
            
            # 删除文件
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # 更新配置
            del self.config.rating_file_paths[system_id]
            if system_id in self.config.json_attribute_mapping:
                del self.config.json_attribute_mapping[system_id]
            if system_id in self.rating_data:
                del self.rating_data[system_id]
            
            # 保存配置
            return self.save_config()
            
        except Exception as e:
            print(f"删除评级文件出错：{str(e)}")
            return False
            
    def get_rating_file_info(self, system_id: str) -> Optional[dict]:
        """获取评级文件信息
        
        Args:
            system_id: 评级系统ID
            
        Returns:
            Optional[dict]: 包含文件路径和属性映射的字典，如果系统不存在则返回None
        """
        if system_id not in self.config.rating_systems:
            return None
            
        return {
            'file_path': self.config.rating_file_paths.get(system_id),
            'mapping': self.config.json_attribute_mapping.get(system_id),
            'data_count': len(self.rating_data.get(system_id, []))
        }
    def reload_config(self):
        """重新加载配置和所有数据"""
        try:
            # 重新加载配置文件
            self.config = self._load_config()
            
            # 清空现有数据
            self.rating_data.clear()
            self.selection_criteria.clear()
            self.selection_profiles.clear()
            
            # 重新加载所有数据
            self._load_all_data()
            
        except Exception as e:
            raise Exception(f"重新加载配置失败：{str(e)}")
