# RIS Transform Backend

FastAPI 后端服务，提供 RIS 文件处理 API。

## 功能特性

- RIS 文件解析与处理
- 期刊评级匹配（CCF、FMS、AJG、ZUFE）
- 多分类标准筛选
- 文献去重
- ZIP 打包输出

## 快速开始

### 本地运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动服务：
```bash
uvicorn backend.app.main:app --reload --port 8000
```

3. 访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker 运行

```bash
# 构建镜像
docker build -t ris-transform-backend -f backend/Dockerfile .

# 运行容器
docker run -d -p 8000:8000 ris-transform-backend
```

## API 端点

### POST /api/process
处理 RIS 文件

**请求参数：**
- `file`: RIS 文件（multipart/form-data）
- `selected_profiles`: 配置文件ID列表
- `deduplicate`: 是否去重（默认 true）

**响应：**
- ZIP 文件流（包含处理后的 RIS 文件）

### GET /api/profiles
获取所有可用的配置文件

**响应：**
```json
{
  "success": true,
  "items": [
    {
      "id": "zufe",
      "name": "zufe",
      "description": "",
      "criteria_sets": ["1a", "top"]
    }
  ]
}
```

### GET /api/rating-systems
获取所有评级系统

**响应：**
```json
{
  "success": true,
  "items": [
    {
      "id": "CCF",
      "name": "CCF期刊/会议分类",
      "description": "中国计算机学会推荐期刊会议目录"
    }
  ]
}
```

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI 主应用
│   └── api/
│       ├── __init__.py
│       └── process.py    # 处理 API 路由
├── requirements.txt      # Python 依赖
├── Dockerfile           # Docker 配置
└── README.md           # 本文件
```

## 依赖说明

- **FastAPI**: Web 框架
- **Uvicorn**: ASGI 服务器
- **Pydantic**: 数据验证
- **python-multipart**: 文件上传支持
- **requests**: HTTP 请求（翻译功能）

## 开发说明

### 添加新的 API 端点

1. 在 `backend/app/api/` 下创建新的路由文件
2. 在 `backend/app/main.py` 中注册路由

### 修改核心处理逻辑

核心处理逻辑位于项目根目录的 `core/` 和 `utils/` 目录，后端通过导入这些模块来使用。

## 环境变量

- `PORT`: 服务端口（默认 8000）
- `HOST`: 服务地址（默认 0.0.0.0）

## 许可证

MIT License

