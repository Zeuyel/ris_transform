.PHONY: help dev-up dev-down dev-logs dev-restart prod-up prod-down prod-logs prod-restart build-dev build-prod status clean

# 默认目标
help:
	@echo "RIS Transform Docker 管理命令"
	@echo ""
	@echo "开发环境:"
	@echo "  make dev-up       - 启动开发环境"
	@echo "  make dev-down     - 停止开发环境"
	@echo "  make dev-logs     - 查看开发环境日志"
	@echo "  make dev-restart  - 重启开发环境"
	@echo ""
	@echo "生产环境:"
	@echo "  make prod-up      - 启动生产环境"
	@echo "  make prod-down    - 停止生产环境"
	@echo "  make prod-logs    - 查看生产环境日志"
	@echo "  make prod-restart - 重启生产环境"
	@echo ""
	@echo "构建:"
	@echo "  make build-dev    - 构建开发镜像"
	@echo "  make build-prod   - 构建生产镜像"
	@echo ""
	@echo "其他:"
	@echo "  make status       - 查看服务状态"
	@echo "  make clean        - 清理 Docker 资源"

# 开发环境
dev-up:
	@if [ ! -f .env ]; then cp .env.example .env; echo "已创建 .env 文件"; fi
	docker-compose --profile dev up -d
	@echo "开发环境已启动: http://localhost:$${FRONTEND_PORT:-3000}"

dev-down:
	docker-compose --profile dev down

dev-logs:
	docker-compose --profile dev logs -f

dev-restart: dev-down dev-up

# 生产环境
prod-up:
	@if [ ! -f .env ]; then cp .env.example .env; echo "已创建 .env 文件"; fi
	docker-compose --profile prod up -d
	@echo "生产环境已启动: http://localhost:$${FRONTEND_PORT:-3000}"

prod-down:
	docker-compose --profile prod down

prod-logs:
	docker-compose --profile prod logs -f

prod-restart: prod-down prod-up

# 构建
build-dev:
	docker-compose --profile dev build

build-prod:
	docker-compose --profile prod build

# 状态
status:
	@echo "=== Docker 容器状态 ==="
	@docker-compose ps
	@echo ""
	@echo "=== 健康检查状态 ==="
	@docker ps --filter "name=ris-transform" --format "table {{.Names}}\t{{.Status}}"

# 清理
clean:
	docker system prune -f
	@echo "清理完成"

