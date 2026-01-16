"""
数据管理器
负责加载和管理评级数据、配置文件
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from .data_types import (
    DataConfig,
    JournalRating,
    RatingFileMapping,
    Profile,
    SelectionCriteria
)


class DataManager:
    """数据管理器"""
    
    def __init__(self, data_dir: str = "data"):
        """
        初始化数据管理器
        
        Args:
            data_dir: 数据目录路径
        """
        self.data_dir = Path(data_dir)
        self.config: Optional[DataConfig] = None
        self.rating_data_cache: Dict[str, List[Dict]] = {}
        self.profiles_cache: Dict[str, Profile] = {}
        
    def load_config(self) -> DataConfig:
        """加载全局配置"""
        if self.config is not None:
            return self.config
            
        config_path = self.data_dir / "config.json"
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        self.config = DataConfig(
            rating_systems=config_data.get('rating_systems', {}),
            rating_file_paths=config_data.get('rating_file_paths', {}),
            json_attribute_mapping=config_data.get('json_attribute_mapping', {}),
            token_missuo=config_data.get('token_missuo', ''),
            token_linuxdo=config_data.get('token_linuxdo', ''),
            output_directory=config_data.get('output_directory', 'outputs'),
            subfolder=config_data.get('subfolder', '')
        )
        
        return self.config
    
    def load_rating_data(self, system_id: str) -> List[Dict]:
        """
        加载评级数据
        
        Args:
            system_id: 评级系统ID (CCF, FMS, AJG, ZUFE等)
            
        Returns:
            评级数据列表
        """
        # 检查缓存
        if system_id in self.rating_data_cache:
            return self.rating_data_cache[system_id]
        
        # 加载配置
        if self.config is None:
            self.load_config()
        
        # 获取文件路径
        relative_path = self.config.rating_file_paths.get(system_id)
        if not relative_path:
            raise ValueError(f"未找到评级系统 {system_id} 的文件路径配置")
        
        # 处理路径分隔符（兼容 Windows 和 Unix）
        relative_path = relative_path.replace('\\', '/')
        file_path = self.data_dir / relative_path
        
        if not file_path.exists():
            raise FileNotFoundError(f"评级数据文件不存在: {file_path}")
        
        # 加载数据
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 缓存数据
        self.rating_data_cache[system_id] = data
        
        return data
    
    def get_rating_mapping(self, system_id: str) -> RatingFileMapping:
        """
        获取评级文件字段映射
        
        Args:
            system_id: 评级系统ID
            
        Returns:
            字段映射配置
        """
        if self.config is None:
            self.load_config()
        
        mapping = self.config.json_attribute_mapping.get(system_id)
        if not mapping:
            raise ValueError(f"未找到评级系统 {system_id} 的字段映射配置")
        
        return RatingFileMapping(
            paper_name=mapping.get('paper_name', 'Paper_name'),
            level=mapping.get('level', 'Level'),
            type=mapping.get('type')
        )
    
    def find_journal_rating(
        self,
        journal_name: str,
        system_id: str
    ) -> Optional[JournalRating]:
        """
        查找期刊评级
        
        Args:
            journal_name: 期刊名称
            system_id: 评级系统ID
            
        Returns:
            期刊评级信息，未找到返回 None
        """
        # 加载评级数据
        rating_data = self.load_rating_data(system_id)
        mapping = self.get_rating_mapping(system_id)
        
        # 标准化期刊名称（小写）
        journal_name_lower = journal_name.lower().strip()
        
        # 查找匹配的期刊
        for item in rating_data:
            item_name = str(item.get(mapping.paper_name, '')).lower().strip()
            
            if item_name == journal_name_lower:
                level = str(item.get(mapping.level, ''))
                type_value = str(item.get(mapping.type, '')) if mapping.type else None
                
                return JournalRating(
                    paper_name=journal_name,
                    level=level,
                    type=type_value
                )

        return None

    def load_profile(self, profile_id: str) -> Profile:
        """
        加载机构配置文件

        Args:
            profile_id: 配置文件ID

        Returns:
            Profile 对象
        """
        # 检查缓存
        if profile_id in self.profiles_cache:
            return self.profiles_cache[profile_id]

        # 加载文件
        profile_path = self.data_dir / "profiles" / f"{profile_id}.json"

        if not profile_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {profile_path}")

        with open(profile_path, 'r', encoding='utf-8') as f:
            profile_data = json.load(f)

        # 解析 criteria_sets
        criteria_sets = {}
        for set_name, criteria_dict in profile_data.get('criteria_sets', {}).items():
            criteria_sets[set_name] = SelectionCriteria(criteria=criteria_dict)

        # 创建 Profile 对象
        profile = Profile(
            id=profile_id,
            name=profile_data.get('name', profile_id),
            description=profile_data.get('description', ''),
            criteria_sets=criteria_sets
        )

        # 缓存
        self.profiles_cache[profile_id] = profile

        return profile

    def list_profiles(self) -> List[str]:
        """
        列出所有可用的配置文件

        Returns:
            配置文件ID列表
        """
        profiles_dir = self.data_dir / "profiles"

        if not profiles_dir.exists():
            return []

        profiles = []
        for file_path in profiles_dir.glob("*.json"):
            profiles.append(file_path.stem)

        return profiles

    def get_all_rating_systems(self) -> List[str]:
        """
        获取所有评级系统ID

        Returns:
            评级系统ID列表
        """
        if self.config is None:
            self.load_config()

        return list(self.config.rating_systems.keys())


