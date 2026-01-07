# RIS 文件处理器 - 前端

基于 Next.js 15 + TypeScript 的学术文献分类处理工具。

## ✨ 功能特性

### 核心功能
- 📤 **文件上传**：拖放或点击上传 RIS 文件
- 🏷️ **分类标准**：支持 CCF、FMS、AJG、ZUFE 等评级体系
- ✏️ **自定义标准**：可视化创建和管理自定义分类规则
- 🌐 **自动翻译**：集成 DeepLX 翻译标题和摘要
- 📦 **批量输出**：ZIP 打包下载分类结果

### 高级功能
- ⚙️ **设置面板**：翻译配置、评级系统管理
- 🔄 **去重处理**：按标题自动去重
- 📊 **Profile 输出**：支持二级组合标准

## 🚀 快速开始

### 安装依赖
\`\`\`bash
cd frontend
npm install
\`\`\`

### 开发模式
\`\`\`bash
npm run dev
\`\`\`

访问 http://localhost:3000

### 生产构建
\`\`\`bash
npm run build
npm start
\`\`\`

## 📁 项目结构

\`\`\`
frontend/
├── app/
│   ├── api/                    # API Routes
│   │   ├── criteria/           # 获取分类标准
│   │   ├── process/            # 处理 RIS 文件
│   │   └── translate/          # 翻译服务
│   ├── criteria/               # 自定义标准页面
│   ├── layout.tsx
│   └── page.tsx                # 首页
│
├── components/
│   ├── features/               # 业务组件
│   │   ├── FileUploader.tsx
│   │   ├── CriteriaSelector.tsx
│   │   ├── ProcessButton.tsx
│   │   └── SettingsPanel.tsx
│   └── ui/                     # 基础 UI 组件
│       ├── Button.tsx
│       ├── Switch.tsx
│       ├── Input.tsx
│       ├── Card.tsx
│       └── Accordion.tsx
│
├── lib/                        # 工具库
│   ├── utils.ts
│   ├── ris-parser.ts
│   └── rating-matcher.ts
│
├── store/                      # Zustand 状态管理
│   ├── use-app-store.ts
│   └── use-settings-store.ts
│
└── types/                      # TypeScript 类型
    ├── ris.ts
    └── criteria.ts
\`\`\`

## 🎯 使用流程

### 1. 上传 RIS 文件
- 拖放文件到上传区域
- 或点击选择文件
- 支持 Scopus、Web of Science 等导出格式

### 2. 选择分类标准
- 点击卡片选择预定义标准
- 或点击「自定义」创建新标准

### 3. 自定义标准（可选）
- 访问 `/criteria` 页面
- 填写标准 ID、名称、描述
- 选择评级系统和等级组合
- 保存后自动出现在主页选择列表

### 4. 配置选项
- 点击右上角齿轮图标打开设置
- 配置翻译服务（标题/摘要）
- 管理评级系统启用状态

### 5. 处理并下载
- 点击「处理并下载 ZIP」按钮
- 等待处理完成
- 自动下载包含所有分类结果的 ZIP 文件

## 🔧 技术栈

- **框架**: Next.js 15 (App Router)
- **语言**: TypeScript 5.7
- **状态管理**: Zustand
- **样式**: Tailwind CSS 3.4
- **图标**: Lucide React
- **打包**: JSZip

## 📝 自定义标准格式

自定义标准存储在 localStorage，格式如下：

\`\`\`json
{
  "id": "top_journals",
  "name": "顶级期刊",
  "description": "CCF A 类期刊 + FMS 1* 期刊",
  "definition": {
    "CCF": ["A期刊"],
    "FMS": ["1*"]
  }
}
\`\`\`

## 🌐 翻译服务

### DeepLX 端点
默认使用以下免费端点（负载均衡）：
- https://api.deeplx.org/translate
- https://deeplx.missuo.ru/translate

可在设置面板中添加自定义端点。

### API 调用
\`\`\`typescript
POST /api/translate
{
  "text": "Hello World",
  "sourceLang": "auto",
  "targetLang": "ZH",
  "service": "deeplx"
}
\`\`\`

## 🐛 常见问题

### 1. "添加" 按钮文字竖排
已修复：在 Button 组件添加 \`whitespace-nowrap\` 类。

### 2. 自定义标准不显示
检查浏览器 localStorage 是否启用，键名为 \`custom-criteria\`。

### 3. 翻译失败
- 检查网络连接
- 尝试切换到「模拟」服务测试
- 或添加其他 DeepLX 端点

## 📄 许可证

MIT

