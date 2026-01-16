# 国内网络经常无法直连 Docker Hub，默认使用镜像源（可用 build-arg 覆盖）
ARG DOCKER_REGISTRY=docker.m.daocloud.io

# ===== 依赖安装阶段 =====
FROM ${DOCKER_REGISTRY}/library/node:20-alpine AS deps

# 安装 libc6-compat 用于兼容性
RUN apk add --no-cache libc6-compat

WORKDIR /app

# 复制包管理文件
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

# ===== 构建阶段 =====
FROM ${DOCKER_REGISTRY}/library/node:20-alpine AS builder

WORKDIR /app

# 从 deps 阶段复制 node_modules
COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ ./

# 构建应用
ENV NEXT_TELEMETRY_DISABLED 1
RUN npm run build

# ===== 生产运行阶段 =====
FROM ${DOCKER_REGISTRY}/library/node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# 创建非 root 用户
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# 复制构建产物
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]

# ===== 开发模式阶段 =====
FROM ${DOCKER_REGISTRY}/library/node:20-alpine AS dev

WORKDIR /app/frontend

# 安装 wget 用于健康检查
RUN apk add --no-cache wget

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

COPY frontend/ ./

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "3000"]
