"""
FastAPI 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import process

# 创建 FastAPI 应用
app = FastAPI(
    title="RIS Transform API",
    description="RIS 文件处理和分类 API",
    version="0.2.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(process.router, prefix="/api", tags=["process"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "RIS Transform API",
        "version": "0.2.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

