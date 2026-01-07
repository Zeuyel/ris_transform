# AGENTS.md

## Project Status: Web 架构（前后端分离）
本仓库以 Web 形态为主：`frontend/`（Next.js） + `backend/`（FastAPI）。根目录保留原始 Python 处理核心（`core/`、`utils/`）供后端复用。

---

## Build/Run Commands

### Web（推荐）
- **一键启动（开发）**：`docker compose -f docker-compose.dev.yml up --build`
  - 前端：`http://localhost:3001`
  - 后端：`http://localhost:8000`
- **一键启动（生产风格）**：`docker compose up --build`
  - 前端：`http://localhost:3000`
  - 后端：`http://localhost:8000`

### Python/PyQt5（历史保留，仅供参考）
- **运行**：`python app.py`
- **构建**：`python build.py`
- **安装依赖**：`pip install -r requirements.txt`

---

## Code Style Guidelines

### TypeScript Frontend (`frontend/`)
- **Naming**: camelCase for variables/functions, PascalCase for components/types
- **Components**: Functional components with hooks
- **Styling**: Tailwind CSS utility classes, custom animations in `styles.css`

### Python Backend (`backend/`)
- **FastAPI**：接口尽量保持纯函数/可测试；错误信息携带上下文
- **依赖复用**：复用根目录 `core/` 逻辑时，避免在 API 层掺杂业务细节（集中到 `backend/app/processing.py`）

### Shared Conventions
- **File encoding**: UTF-8 for all files, UTF-8-sig for RIS files
- **Error messages**: Include context, use structured logging
 - **Async**: TypeScript uses `async/await`
 - **Data flow**: Frontend → FastAPI → Python core → Response

---

## Architecture

### Web Structure
```
frontend/                # Next.js 前端（页面 + 调用后端 API）
backend/                 # FastAPI 后端（API + 处理编排）
core/                    # 处理核心（被 backend 复用）
data/                    # 分类标准/评级数据/配置
outputs/                 # 输出目录（容器与本地均可挂载）
```

### Key Modules
- **Frontend API 封装**：`frontend/lib/api.ts`
- **Backend API 入口**：`backend/app/main.py`
- **处理编排**：`backend/app/processing.py`（复用 `core/paper_processor.py`）

### Data Flow
1. 用户在前端上传 RIS → `frontend/app/page.tsx`
2. 前端调用后端 → `POST /api/process`
3. 后端复用 Python 核心处理 → 生成多份输出并打包 zip
4. 浏览器下载 zip
