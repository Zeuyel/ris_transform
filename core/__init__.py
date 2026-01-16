"""
核心处理模块
包含 RIS 文件处理、数据管理和类型定义
"""

from .data_types import RatingSystem, JournalRating, DataConfig
from .data_manager import DataManager
from .paper_processor import PaperProcessor

__all__ = [
    'RatingSystem',
    'JournalRating',
    'DataConfig',
    'DataManager',
    'PaperProcessor',
]

