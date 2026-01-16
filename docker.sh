#!/bin/bash

# RIS Transform Docker 管理脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo "RIS Transform Docker 管理脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  dev-up       启动开发环境"
    echo "  dev-down     停止开发环境"
    echo "  dev-logs     查看开发环境日志"
    echo "  dev-restart  重启开发环境"
    echo ""
    echo "  prod-up      启动生产环境"
    echo "  prod-down    停止生产环境"
    echo "  prod-logs    查看生产环境日志"
    echo "  prod-restart 重启生产环境"
    echo ""
    echo "  build-dev    构建开发镜像"
    echo "  build-prod   构建生产镜像"
    echo ""
    echo "  status       查看服务状态"
    echo "  clean        清理 Docker 资源"
    echo "  help         显示此帮助信息"
}

# 检查 .env 文件
check_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}警告: .env 文件不存在${NC}"
        echo -e "${YELLOW}正在从 .env.example 创建 .env 文件...${NC}"
        cp .env.example .env
        echo -e "${GREEN}已创建 .env 文件，请根据需要修改配置${NC}"
    fi
}

# 开发环境命令
dev_up() {
    check_env
    echo -e "${GREEN}启动开发环境...${NC}"
    docker-compose --profile dev up -d
    echo -e "${GREEN}开发环境已启动！${NC}"
    echo -e "${GREEN}访问: http://localhost:${FRONTEND_PORT:-3000}${NC}"
}

dev_down() {
    echo -e "${YELLOW}停止开发环境...${NC}"
    docker-compose --profile dev down
    echo -e "${GREEN}开发环境已停止${NC}"
}

dev_logs() {
    docker-compose --profile dev logs -f
}

dev_restart() {
    dev_down
    dev_up
}

# 生产环境命令
prod_up() {
    check_env
    echo -e "${GREEN}启动生产环境...${NC}"
    docker-compose --profile prod up -d
    echo -e "${GREEN}生产环境已启动！${NC}"
    echo -e "${GREEN}访问: http://localhost:${FRONTEND_PORT:-3000}${NC}"
}

prod_down() {
    echo -e "${YELLOW}停止生产环境...${NC}"
    docker-compose --profile prod down
    echo -e "${GREEN}生产环境已停止${NC}"
}

prod_logs() {
    docker-compose --profile prod logs -f
}

prod_restart() {
    prod_down
    prod_up
}

# 构建命令
build_dev() {
    echo -e "${GREEN}构建开发镜像...${NC}"
    docker-compose --profile dev build
    echo -e "${GREEN}开发镜像构建完成${NC}"
}

build_prod() {
    echo -e "${GREEN}构建生产镜像...${NC}"
    docker-compose --profile prod build
    echo -e "${GREEN}生产镜像构建完成${NC}"
}

# 状态查看
show_status() {
    echo -e "${GREEN}=== Docker 容器状态 ===${NC}"
    docker-compose ps
    echo ""
    echo -e "${GREEN}=== 健康检查状态 ===${NC}"
    docker ps --filter "name=ris-transform" --format "table {{.Names}}\t{{.Status}}"
}

# 清理资源
clean() {
    echo -e "${YELLOW}清理 Docker 资源...${NC}"
    read -p "确定要清理未使用的 Docker 资源吗？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker system prune -f
        echo -e "${GREEN}清理完成${NC}"
    else
        echo -e "${YELLOW}已取消${NC}"
    fi
}

# 主逻辑
case "${1:-help}" in
    dev-up)
        dev_up
        ;;
    dev-down)
        dev_down
        ;;
    dev-logs)
        dev_logs
        ;;
    dev-restart)
        dev_restart
        ;;
    prod-up)
        prod_up
        ;;
    prod-down)
        prod_down
        ;;
    prod-logs)
        prod_logs
        ;;
    prod-restart)
        prod_restart
        ;;
    build-dev)
        build_dev
        ;;
    build-prod)
        build_prod
        ;;
    status)
        show_status
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}错误: 未知命令 '$1'${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac


