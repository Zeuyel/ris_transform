"""
RIS 文件处理 API
"""
import io
import zipfile
from typing import List
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# 导入核心处理模块
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core import DataManager, PaperProcessor


router = APIRouter()

# 初始化数据管理器和处理器
data_manager = DataManager(data_dir=str(project_root / "data"))
processor = PaperProcessor(data_manager)


class ProcessResponse(BaseModel):
    """处理响应模型"""
    success: bool
    message: str = ""
    total_entries: int = 0
    processed_entries: int = 0
    output_files: List[str] = []


@router.post("/process")
async def process_ris_file(
    file: UploadFile = File(...),
    selected_profiles: List[str] = Form(...),
    deduplicate: bool = Form(True)
):
    """
    处理 RIS 文件
    
    Args:
        file: 上传的 RIS 文件
        selected_profiles: 选中的配置文件ID列表
        deduplicate: 是否去重
        
    Returns:
        ZIP 文件流（包含处理后的 RIS 文件）
    """
    try:
        # 读取文件内容
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # 处理文件
        result = processor.process_file(
            content=content_str,
            profile_ids=selected_profiles,
            deduplicate=deduplicate
        )
        
        # 创建 ZIP 文件
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for output_key, entries in result.output_files.items():
                # 生成 RIS 内容
                ris_content = processor.entries_to_ris(entries)
                
                # 添加到 ZIP
                # output_key 格式: "profile_id/criteria_set_name"
                file_path = f"{output_key}.ris"
                zip_file.writestr(file_path, ris_content)
        
        # 重置缓冲区位置
        zip_buffer.seek(0)
        
        # 生成文件名
        original_filename = file.filename or "output"
        if original_filename.endswith('.ris'):
            original_filename = original_filename[:-4]
        
        zip_filename = f"{original_filename}_outputs.zip"
        
        # 返回 ZIP 文件
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{zip_filename}"'
            }
        )
    
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="文件编码错误，请确保文件使用 UTF-8 编码"
        )
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"配置文件未找到: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"处理失败: {str(e)}"
        )


@router.get("/profiles")
async def list_profiles():
    """
    获取所有可用的配置文件
    
    Returns:
        配置文件列表
    """
    try:
        profiles = data_manager.list_profiles()
        
        # 加载详细信息
        profile_details = []
        for profile_id in profiles:
            try:
                profile = data_manager.load_profile(profile_id)
                profile_details.append({
                    "id": profile.id,
                    "name": profile.name,
                    "description": profile.description,
                    "criteria_sets": list(profile.criteria_sets.keys())
                })
            except Exception as e:
                print(f"加载配置文件 {profile_id} 失败: {e}")
                continue
        
        return {
            "success": True,
            "items": profile_details
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取配置文件列表失败: {str(e)}"
        )


@router.get("/rating-systems")
async def list_rating_systems():
    """
    获取所有评级系统
    
    Returns:
        评级系统列表
    """
    try:
        config = data_manager.load_config()
        
        systems = []
        for system_id, system_info in config.rating_systems.items():
            systems.append({
                "id": system_id,
                "name": system_info.get("name", system_id),
                "description": system_info.get("description", "")
            })
        
        return {
            "success": True,
            "items": systems
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取评级系统列表失败: {str(e)}"
        )

