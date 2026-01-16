"""
RIS 文件处理器
负责解析 RIS 文件、期刊分类、去重等核心功能
"""
import re
from typing import Dict, List, Optional, Set
from .data_types import RisEntry, ProcessingResult, SelectionCriteria
from .data_manager import DataManager


class PaperProcessor:
    """RIS 文件处理器"""
    
    def __init__(self, data_manager: DataManager):
        """
        初始化处理器
        
        Args:
            data_manager: 数据管理器实例
        """
        self.data_manager = data_manager
    
    def parse_ris(self, content: str) -> List[RisEntry]:
        """
        解析 RIS 文件内容
        
        Args:
            content: RIS 文件文本内容
            
        Returns:
            RIS 条目列表
        """
        entries = []
        current_entry_data = {}
        
        lines = content.split('\n')
        
        for raw_line in lines:
            line = raw_line.strip()
            
            if not line:
                continue
            
            # 条目结束标记
            if line == 'ER  -':
                if current_entry_data:
                    # 初始化自定义字段
                    if 'C1' not in current_entry_data:
                        current_entry_data['C1'] = []
                    if 'C2' not in current_entry_data:
                        current_entry_data['C2'] = []
                    if 'LB' not in current_entry_data:
                        current_entry_data['LB'] = []
                    
                    entries.append(RisEntry(data=current_entry_data))
                    current_entry_data = {}
                continue
            
            # 解析标签和值 (格式: XX  - value)
            if len(line) > 6:
                tag = line[:2]
                value = line[6:].strip()
                
                if tag not in current_entry_data:
                    current_entry_data[tag] = []
                current_entry_data[tag].append(value)
        
        # 处理最后一个条目（如果没有 ER 结束标记）
        if current_entry_data:
            if 'C1' not in current_entry_data:
                current_entry_data['C1'] = []
            if 'C2' not in current_entry_data:
                current_entry_data['C2'] = []
            if 'LB' not in current_entry_data:
                current_entry_data['LB'] = []
            entries.append(RisEntry(data=current_entry_data))
        
        return entries
    
    def entries_to_ris(self, entries: List[RisEntry]) -> str:
        """
        将条目列表转换为 RIS 格式文本
        
        Args:
            entries: RIS 条目列表
            
        Returns:
            RIS 格式文本
        """
        lines = []
        
        for entry in entries:
            lines.append(entry.to_ris_text())
            lines.append('')  # 空行分隔
        
        return '\n'.join(lines)
    
    def deduplicate_entries(self, entries: List[RisEntry]) -> List[RisEntry]:
        """
        根据标题去重
        
        Args:
            entries: RIS 条目列表
            
        Returns:
            去重后的条目列表
        """
        unique_map: Dict[str, RisEntry] = {}
        
        for entry in entries:
            title = entry.get_title()
            if not title:
                continue
            
            title_key = title.lower().strip()
            
            if title_key not in unique_map:
                unique_map[title_key] = entry
            else:
                # 保留字段更完整的条目
                existing = unique_map[title_key]
                if len(entry.data) > len(existing.data):
                    unique_map[title_key] = entry
        
        return list(unique_map.values())
    
    def get_entry_ratings(
        self,
        entry: RisEntry,
        system_ids: List[str]
    ) -> Dict[str, str]:
        """
        获取条目在各评级系统中的评级
        
        Args:
            entry: RIS 条目
            system_ids: 评级系统ID列表
            
        Returns:
            评级系统ID -> 评级等级的映射
        """
        ratings = {}
        journal_name = entry.get_journal()
        
        if not journal_name:
            return {system_id: 'Not Found' for system_id in system_ids}
        
        for system_id in system_ids:
            try:
                rating = self.data_manager.find_journal_rating(journal_name, system_id)
                
                if rating:
                    # CCF 特殊处理：等级+类型
                    if system_id == 'CCF' and rating.type:
                        ratings[system_id] = f"{rating.level}{rating.type}"
                    else:
                        ratings[system_id] = rating.level
                else:
                    ratings[system_id] = 'Not Found'
            except Exception as e:
                print(f"获取评级失败 [{system_id}]: {e}")
                ratings[system_id] = 'Not Found'

        return ratings

    def matches_criteria(
        self,
        ratings: Dict[str, str],
        criteria: SelectionCriteria
    ) -> bool:
        """
        检查条目是否匹配分类标准

        Args:
            ratings: 条目的评级信息
            criteria: 分类标准

        Returns:
            是否匹配
        """
        for system_id, required_levels in criteria.criteria.items():
            entry_rating = ratings.get(system_id)

            if not entry_rating or entry_rating == 'Not Found':
                continue

            # 检查是否匹配任一要求的等级
            for level in required_levels:
                level_str = str(level)
                if entry_rating == level_str or entry_rating.startswith(level_str):
                    return True

        return False

    def filter_entries_by_criteria(
        self,
        entries: List[RisEntry],
        all_ratings: Dict[str, Dict[str, str]],
        criteria: SelectionCriteria
    ) -> List[RisEntry]:
        """
        根据分类标准筛选条目

        Args:
            entries: RIS 条目列表
            all_ratings: 所有条目的评级信息 (标题 -> 评级映射)
            criteria: 分类标准

        Returns:
            筛选后的条目列表
        """
        filtered = []

        for entry in entries:
            title = entry.get_title()
            if not title:
                continue

            title_key = title.lower().strip()
            ratings = all_ratings.get(title_key)

            if not ratings:
                continue

            if self.matches_criteria(ratings, criteria):
                filtered.append(entry)

        return filtered

    def batch_get_ratings(
        self,
        entries: List[RisEntry],
        system_ids: List[str]
    ) -> Dict[str, Dict[str, str]]:
        """
        批量获取所有条目的评级信息

        Args:
            entries: RIS 条目列表
            system_ids: 评级系统ID列表

        Returns:
            标题 -> 评级映射的字典
        """
        ratings_map = {}

        for entry in entries:
            title = entry.get_title()
            if not title:
                continue

            title_key = title.lower().strip()
            ratings = self.get_entry_ratings(entry, system_ids)
            ratings_map[title_key] = ratings

        return ratings_map

    def process_file(
        self,
        content: str,
        profile_ids: List[str],
        deduplicate: bool = True
    ) -> ProcessingResult:
        """
        处理 RIS 文件

        Args:
            content: RIS 文件内容
            profile_ids: 要应用的配置文件ID列表
            deduplicate: 是否去重

        Returns:
            处理结果
        """
        # 解析 RIS 文件
        entries = self.parse_ris(content)
        total_entries = len(entries)

        # 去重
        if deduplicate:
            entries = self.deduplicate_entries(entries)

        # 获取所有评级系统
        system_ids = self.data_manager.get_all_rating_systems()

        # 批量获取评级信息
        all_ratings = self.batch_get_ratings(entries, system_ids)

        # 处理每个 Profile
        output_files = {}

        for profile_id in profile_ids:
            try:
                profile = self.data_manager.load_profile(profile_id)

                # 处理 Profile 中的每个 CriteriaSet
                for criteria_set_name, criteria in profile.criteria_sets.items():
                    filtered_entries = self.filter_entries_by_criteria(
                        entries,
                        all_ratings,
                        criteria
                    )

                    if filtered_entries:
                        output_key = f"{profile_id}/{criteria_set_name}"
                        output_files[output_key] = filtered_entries

            except Exception as e:
                print(f"处理 Profile {profile_id} 失败: {e}")
                continue

        return ProcessingResult(
            total_entries=total_entries,
            processed_entries=len(entries),
            output_files=output_files
        )


