"""
核心数据类型定义
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class RatingSystem(str, Enum):
    """评级系统枚举"""
    CCF = "CCF"      # 中国计算机学会
    FMS = "FMS"      # 金融管理科学
    AJG = "AJG"      # Academic Journal Guide
    ZUFE = "ZUFE"    # 浙江财经大学
    ZDY = "zdy"      # 自定义


@dataclass
class JournalRating:
    """期刊评级数据结构"""
    paper_name: str              # 期刊名称
    level: str                   # 评级等级
    type: Optional[str] = None   # 类型(用于CCF区分期刊/会议)


@dataclass
class RatingFileMapping:
    """评级文件字段映射"""
    paper_name: str              # JSON中期刊名称字段
    level: str                   # JSON中等级字段
    type: Optional[str] = None   # JSON中类型字段(可选)


@dataclass
class RatingSystemConfig:
    """评级系统配置"""
    id: str
    name: str
    description: str


@dataclass
class DataConfig:
    """全局数据配置"""
    rating_systems: Dict[str, Dict[str, str]]                    # 评级系统配置
    rating_file_paths: Dict[str, str]                            # 评级文件路径
    json_attribute_mapping: Dict[str, Dict[str, str]]            # JSON属性映射
    token_missuo: str = ""                                       # 米索翻译令牌
    token_linuxdo: str = ""                                      # LinuxDo翻译令牌
    output_directory: str = "outputs"                            # 输出目录
    subfolder: str = ""                                          # 子文件夹名称


@dataclass
class SelectionCriteria:
    """分类标准"""
    criteria: Dict[str, List[str]]  # 评级系统ID -> 等级列表


@dataclass
class Profile:
    """机构配置文件"""
    id: str
    name: str
    description: str = ""
    criteria_sets: Dict[str, SelectionCriteria] = None  # CriteriaSet名称 -> SelectionCriteria
    
    def __post_init__(self):
        if self.criteria_sets is None:
            self.criteria_sets = {}


@dataclass
class RisEntry:
    """RIS 条目数据结构"""
    data: Dict[str, List[str]]  # 标签 -> 值列表
    
    def get_title(self) -> Optional[str]:
        """获取标题"""
        return self.data.get('TI', [None])[0]
    
    def get_journal(self) -> Optional[str]:
        """获取期刊名"""
        return self.data.get('T2', [None])[0]
    
    def get_authors(self) -> List[str]:
        """获取作者列表"""
        return self.data.get('AU', [])
    
    def get_year(self) -> Optional[str]:
        """获取年份"""
        return self.data.get('PY', [None])[0]
    
    def get_abstract(self) -> Optional[str]:
        """获取摘要"""
        return self.data.get('AB', [None])[0]
    
    def set_custom_field(self, field: str, value: str):
        """设置自定义字段"""
        if field not in self.data:
            self.data[field] = []
        self.data[field].append(value)
    
    def to_ris_text(self) -> str:
        """转换为 RIS 格式文本"""
        lines = []
        for tag, values in self.data.items():
            for value in values:
                if value:
                    lines.append(f"{tag}  - {value}")
        lines.append("ER  -")
        return "\n".join(lines)


@dataclass
class ProcessingResult:
    """处理结果"""
    total_entries: int                           # 总条目数
    processed_entries: int                       # 已处理条目数
    output_files: Dict[str, List[RisEntry]]      # 输出文件 -> 条目列表
    errors: List[str] = None                     # 错误信息列表
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

