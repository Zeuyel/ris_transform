#!/bin/bash

# RIS Transform 快速启动脚本

set -e

echo "🚀 RIS Transform 快速启动"
echo "=========================="
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "📝 创建 .env 文件..."
    cp .env.example .env
    echo "✅ .env 文件已创建，请根据需要修改配置"
fi

# 选择启动模式
echo "请选择启动模式："
echo "1) 开发模式（支持热重载）"
echo "2) 生产模式"
echo "3) 仅后端"
echo "4) 仅前端"
read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🔧 启动开发模式..."
        docker-compose --profile dev up -d
        echo ""
        echo "✅ 服务已启动！"
        echo "   前端: http://localhost:3000"
        echo "   后端: http://localhost:8000"
        echo "   API 文档: http://localhost:8000/docs"
        echo ""
        echo "查看日志: docker-compose --profile dev logs -f"
        echo "停止服务: docker-compose --profile dev down"
        ;;
    2)
        echo ""
        echo "🚀 启动生产模式..."
        docker-compose --profile prod up -d
        echo ""
        echo "✅ 服务已启动！"
        echo "   前端: http://localhost:3000"
        echo "   后端: http://localhost:8000"
        echo "   API 文档: http://localhost:8000/docs"
        echo ""
        echo "查看日志: docker-compose --profile prod logs -f"
        echo "停止服务: docker-compose --profile prod down"
        ;;
    3)
        echo ""
        echo "🔧 启动后端服务..."
        docker-compose up -d backend-dev
        echo ""
        echo "✅ 后端服务已启动！"
        echo "   后端: http://localhost:8000"
        echo "   API 文档: http://localhost:8000/docs"
        echo ""
        echo "查看日志: docker-compose logs -f backend-dev"
        echo "停止服务: docker-compose stop backend-dev"
        ;;
    4)
        echo ""
        echo "🔧 启动前端服务..."
        docker-compose up -d frontend-dev
        echo ""
        echo "✅ 前端服务已启动！"
        echo "   前端: http://localhost:3000"
        echo ""
        echo "查看日志: docker-compose logs -f frontend-dev"
        echo "停止服务: docker-compose stop frontend-dev"
        ;;
    *)
        echo "❌ 无效的选项"
        exit 1
        ;;
esac

