#!/bin/bash

# 本地快速启动脚本

echo "🚀 本地启动 RIS Transform"
echo "=========================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python"
    exit 1
fi

echo "📦 安装后端依赖..."
pip3 install -r backend/requirements.txt

echo ""
echo "✅ 依赖安装完成！"
echo ""
echo "🔧 启动后端服务..."
echo "   访问: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo ""

# 启动后端
uvicorn backend.app.main:app --reload --port 8000

