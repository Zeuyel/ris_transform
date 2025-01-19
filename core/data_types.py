from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class RatingSystem(str, Enum):
    """评级系统枚举"""
    # 默认的评级系统
    CCF = "CCF"
    FMS = "FMS"
    AJG = "AJG"
    ZUFE = "ZUFE"
    
    @classmethod
    def from_config(cls, config_data: dict) -> Dict[str, Dict[str, str]]:
        """从配置文件加载评级系统配置
        
        Args:
            config_data: 配置数据，包含rating_systems字段
            
        Returns:
            Dict[str, Dict[str, str]]: 评级系统配置
        """
        # 获取配置中的评级系统
        return config_data.get('rating_systems', {
            'CCF': {'name': 'CCF期刊/会议分类', 'description': '中国计算机学会推荐期刊会议目录'},
            'FMS': {'name': 'FMS期刊分类', 'description': '金融管理科学期刊目录'},
            'AJG': {'name': 'AJG期刊分类', 'description': 'Academic Journal Guide'},
            'ZUFE': {'name': 'ZUFE期刊分类', 'description': '浙江财经大学期刊目录'}
        })

@dataclass
class JournalRating:
    """期刊评级数据结构"""
    paper_name: str  # 期刊名称
    level: str      # 评级等级
    type: Optional[str] = None  # 类型(用于CCF区分期刊/会议)

@dataclass
class DataConfig:
    """配置数据结构"""
    rating_systems: Dict[str, Dict[str, str]] = field(default_factory=dict)  # 评级系统配置
    rating_file_paths: Dict[str, str] = field(default_factory=dict)  # 评级文件路径
    json_attribute_mapping: Dict[str, Dict[str, str]] = field(default_factory=dict)  # JSON属性映射
    token_missuo: str = ""  # 米索翻译令牌
    token_linuxdo: str = ""  # LinuxDo翻译令牌
    output_directory: str = ""  # 输出目录
    subfolder: str = ""  # 子文件夹名称
