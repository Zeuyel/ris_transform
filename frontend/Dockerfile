# 国内网络经常无法直连 Docker Hub，默认使用镜像源（可用 build-arg 覆盖）
ARG DOCKER_REGISTRY=docker.m.daocloud.io
FROM ${DOCKER_REGISTRY}/library/node:20-alpine

WORKDIR /app

COPY frontend/package.json /app/frontend/package.json
COPY frontend/tsconfig.json /app/frontend/tsconfig.json
COPY frontend/next.config.mjs /app/frontend/next.config.mjs
COPY frontend/tailwind.config.ts /app/frontend/tailwind.config.ts
COPY frontend/postcss.config.mjs /app/frontend/postcss.config.mjs

COPY frontend/app /app/frontend/app
COPY frontend/styles /app/frontend/styles
COPY frontend/lib /app/frontend/lib

WORKDIR /app/frontend
RUN npm install

EXPOSE 3000
CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0", "-p", "3000"]
