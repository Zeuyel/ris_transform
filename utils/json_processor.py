"""
JSON 处理工具
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class JsonProcessor:
    """JSON 处理器"""
    
    @staticmethod
    def load_json(file_path: str) -> Any:
        """
        加载 JSON 文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            解析后的数据
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def save_json(data: Any, file_path: str, indent: int = 2):
        """
        保存数据为 JSON 文件
        
        Args:
            data: 要保存的数据
            file_path: 文件路径
            indent: 缩进空格数
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
    
    @staticmethod
    def merge_json_files(file_paths: List[str]) -> List[Dict]:
        """
        合并多个 JSON 文件
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            合并后的数据列表
        """
        merged_data = []
        
        for file_path in file_paths:
            try:
                data = JsonProcessor.load_json(file_path)
                
                if isinstance(data, list):
                    merged_data.extend(data)
                elif isinstance(data, dict):
                    merged_data.append(data)
            
            except Exception as e:
                print(f"加载文件失败 {file_path}: {e}")
                continue
        
        return merged_data
    
    @staticmethod
    def filter_json_data(
        data: List[Dict],
        filter_func: callable
    ) -> List[Dict]:
        """
        过滤 JSON 数据
        
        Args:
            data: 数据列表
            filter_func: 过滤函数
            
        Returns:
            过滤后的数据
        """
        return [item for item in data if filter_func(item)]
    
    @staticmethod
    def transform_json_data(
        data: List[Dict],
        transform_func: callable
    ) -> List[Dict]:
        """
        转换 JSON 数据
        
        Args:
            data: 数据列表
            transform_func: 转换函数
            
        Returns:
            转换后的数据
        """
        return [transform_func(item) for item in data]
    
    @staticmethod
    def deduplicate_json_data(
        data: List[Dict],
        key: str
    ) -> List[Dict]:
        """
        根据指定键去重
        
        Args:
            data: 数据列表
            key: 用于去重的键
            
        Returns:
            去重后的数据
        """
        seen = set()
        unique_data = []
        
        for item in data:
            value = item.get(key)
            
            if value and value not in seen:
                seen.add(value)
                unique_data.append(item)
        
        return unique_data

