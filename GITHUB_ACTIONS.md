# GitHub Actions Docker 发布配置指南

## 1. 创建 Docker Hub Access Token

1. 登录 [Docker Hub](https://hub.docker.com/)
2. 点击右上角头像 -> Account Settings
3. 左侧菜单选择 "Security"
4. 点击 "New Access Token"
5. 输入描述（如：GitHub Actions）
6. 选择权限：Read, Write, Delete
7. 点击 "Generate"
8. **重要**：复制生成的 token（只显示一次）

## 2. 配置 GitHub Secrets

1. 进入你的 GitHub 仓库
2. 点击 Settings -> Secrets and variables -> Actions
3. 点击 "New repository secret"
4. 添加以下 secrets：

### DOCKER_USERNAME
- Name: `DOCKER_USERNAME`
- Secret: 你的 Docker Hub 用户名

### DOCKER_PASSWORD  
- Name: `DOCKER_PASSWORD`
- Secret: 刚才创建的 Access Token（不是密码！）

## 3. Workflow 触发条件

当前配置的 workflow 会在以下情况触发：

### 自动触发

1. **推送到 main 分支**
   ```bash
   git push origin main
   ```
   生成标签：`latest`, `main`, `main-<commit-sha>`

2. **推送到 develop 分支**
   ```bash
   git push origin develop
   ```
   生成标签：`develop`, `develop-<commit-sha>`

3. **创建版本标签**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
   生成标签：`v1.0.0`, `1.0`, `1`

4. **Pull Request**
   - 仅构建镜像，不推送到 Docker Hub
   - 用于验证构建是否成功

### 手动触发

1. 进入 GitHub 仓库
2. 点击 Actions 标签页
3. 选择 "Build and Push Docker Image" workflow
4. 点击 "Run workflow"
5. 选择分支并点击 "Run workflow" 按钮

## 4. 镜像标签策略

| Git 操作 | 生成的镜像标签 |
|---------|--------------|
| 推送到 main | `latest`, `main`, `main-abc123` |
| 推送到 develop | `develop`, `develop-abc123` |
| 标签 v1.2.3 | `v1.2.3`, `1.2`, `1` |
| PR #123 | `pr-123` (仅构建) |

## 5. 使用构建好的镜像

### 拉取镜像

```bash
# 拉取最新版本
docker pull your-username/ris-transform-frontend:latest

# 拉取特定版本
docker pull your-username/ris-transform-frontend:v1.0.0

# 拉取开发版本
docker pull your-username/ris-transform-frontend:develop
```

### 运行镜像

```bash
docker run -d \
  -p 3000:3000 \
  -e NODE_ENV=production \
  --name ris-transform-frontend \
  your-username/ris-transform-frontend:latest
```

### 在 docker-compose 中使用

修改 `.env` 文件：
```env
DOCKER_USERNAME=your-username
TAG=v1.0.0
```

然后运行：
```bash
docker-compose --profile prod up -d
```

## 6. 查看构建状态

### 在 GitHub 上查看

1. 进入仓库的 Actions 页面
2. 查看最新的 workflow 运行记录
3. 点击进入查看详细日志

### 在 Docker Hub 上查看

1. 登录 Docker Hub
2. 进入你的仓库
3. 查看 Tags 页面，确认镜像已推送

## 7. Workflow 优化说明

当前 workflow 包含以下优化：

### 缓存优化
- 使用 GitHub Actions cache 加速构建
- 缓存 Docker 构建层
- 减少重复构建时间

### 多平台支持（可选）
如果需要构建多平台镜像（如 amd64 和 arm64），可以修改 workflow：

```yaml
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    platforms: linux/amd64,linux/arm64
    # ... 其他配置
```

### 构建优化
- 使用 BuildKit 加速构建
- 多阶段构建减小镜像体积
- 生产环境不包含源码

## 8. 常见问题

### Q: 构建失败提示认证错误
A: 检查 DOCKER_USERNAME 和 DOCKER_PASSWORD 是否正确配置

### Q: 镜像推送速度很慢
A: GitHub Actions 服务器在国外，推送到 Docker Hub 速度正常
   可以考虑使用 GitHub Container Registry (ghcr.io)

### Q: 如何推送到多个镜像仓库？
A: 可以添加更多的 login 和 push 步骤，例如同时推送到 Docker Hub 和 ghcr.io

### Q: 如何只在 main 分支推送 latest 标签？
A: 当前配置已经实现，通过 `enable={{is_default_branch}}` 控制

## 9. 安全建议

1. **使用 Access Token 而不是密码**
   - Access Token 可以随时撤销
   - 可以限制权限范围

2. **定期轮换 Token**
   - 建议每 3-6 个月更换一次
   - 在 Docker Hub 删除旧 token

3. **最小权限原则**
   - Token 只给必要的权限（Read, Write）
   - 不需要 Delete 权限可以不勾选

4. **不要在代码中硬编码 secrets**
   - 所有敏感信息都使用 GitHub Secrets
   - 不要在 commit 中包含 token

## 10. 下一步

- [ ] 配置 GitHub Secrets
- [ ] 测试推送代码触发构建
- [ ] 验证镜像已推送到 Docker Hub
- [ ] 测试拉取并运行镜像
- [ ] （可选）配置 ghcr.io 作为备用仓库

