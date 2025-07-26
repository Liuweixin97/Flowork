# CLAUDE.md

此文件为 Claude Code 在此代码库中工作时提供指导。

## 项目概述

这是一个支持多用户的智能简历编辑器应用程序，专为与 Dify AI 工作流集成而设计。项目采用现代化的前后端分离架构，提供完整的用户认证、简历管理和PDF导出功能。

### 核心组成
- **后端服务**: Python Flask API，使用 SQLAlchemy ORM 和 JWT 认证
- **前端应用**: React SPA，使用 Vite 构建系统和 Tailwind CSS
- **认证系统**: 完整的用户注册、登录、权限控制，支持多用户数据隔离
- **AI集成**: 接收 Dify 工作流数据，提供可视化编辑界面

## 项目架构

### 后端架构
```
backend/
├── app.py                 # Flask 应用入口，配置 JWT、CORS、数据库
├── models.py              # SQLAlchemy 数据模型 (User, Resume)
├── routes/                # API 路由模块
│   ├── auth_routes.py     # 用户认证相关路由
│   ├── resume_routes.py   # 简历管理路由
│   ├── chatflow_routes.py # AI 对话流路由
│   └── debug_routes.py    # 调试和健康检查
├── services/              # 业务逻辑服务
│   ├── auth_service.py    # 认证服务
│   ├── pdf_generator.py   # PDF 生成服务 (ReportLab)
│   ├── html_pdf_generator.py # HTML 转 PDF 服务
│   ├── markdown_parser.py # Markdown 解析服务
│   └── dify_chatflow_service.py # Dify 对话流集成
└── requirements.txt       # Python 依赖
```

### 前端架构
```
frontend/
├── src/
│   ├── components/        # React 组件
│   │   ├── auth/         # 认证相关组件
│   │   ├── ResumeEditor.jsx # 简历编辑器
│   │   ├── ResumeList.jsx   # 简历列表
│   │   └── ChatflowDialog.jsx # AI 对话组件
│   ├── pages/            # 页面组件
│   │   ├── HomePage.jsx  # 主页
│   │   ├── EditPage.jsx  # 编辑页面
│   │   ├── LoginPage.jsx # 登录页面
│   │   └── RegisterPage.jsx # 注册页面
│   ├── contexts/         # React Context
│   │   └── AuthContext.jsx # 全局认证状态
│   ├── hooks/            # 自定义 Hooks
│   └── utils/
│       └── api.js        # API 通信层
├── package.json          # Node.js 依赖
└── vite.config.js        # Vite 配置
```

### 数据库设计
- **User 模型**: 用户认证和资料管理
  - `id`, `username`, `email`, `password_hash`
  - `full_name`, `is_admin`, `created_at`
- **Resume 模型**: 简历数据存储
  - `id`, `title`, `raw_markdown`, `structured_data`
  - `user_id` (外键), `is_public`, `created_at`, `updated_at`
- 支持 PostgreSQL (生产环境) 和 SQLite (开发环境)

## 开发工作流

### 环境配置

#### 后端开发环境
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

#### 前端开发环境
```bash
cd frontend
npm install
npm run dev          # 开发服务器
npm run build        # 生产构建
npm run lint         # ESLint 检查
```

#### 快速启动
```bash
./setup.sh           # 初始化配置
./start.sh           # 启动所有服务
./stop.sh            # 停止所有服务
```

#### Docker 部署
```bash
./deploy-docker.sh   # 一键 Docker 部署
./docker-start.sh    # 启动 Docker 服务
./docker-stop.sh     # 停止 Docker 服务
```

### 环境变量配置

#### 后端配置 (backend/.env)
```bash
# 应用配置
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
HOST=0.0.0.0
PORT=8080

# 数据库配置
DATABASE_URL=sqlite:///resume_editor.db
# DATABASE_URL=postgresql://user:pass@localhost/dbname

# CORS 配置
FRONTEND_URL=http://localhost:3000

# Dify 集成配置 (可选)
DIFY_API_KEY=your_dify_api_key
DIFY_API_URL=https://api.dify.ai/v1
```

#### 前端配置 (frontend/.env)
```bash
# API 配置
VITE_API_URL=http://localhost:8080
```

## API 接口规范

### 认证系统 API
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录 
- `POST /api/auth/logout` - 用户登出
- `POST /api/auth/refresh` - 刷新 JWT 令牌
- `GET /api/auth/me` - 获取当前用户信息
- `PUT /api/auth/profile` - 更新用户资料
- `POST /api/auth/change-password` - 修改密码

### 简历管理 API
- `GET /api/resumes` - 获取简历列表 (支持权限过滤)
- `POST /api/resumes` - 创建新简历 (需要认证)
- `GET /api/resumes/{id}` - 获取简历详情 (基于权限)
- `PUT /api/resumes/{id}` - 更新简历 (需要所有者权限)
- `DELETE /api/resumes/{id}` - 删除简历 (需要所有者权限)
- `GET /api/resumes/{id}/pdf` - 导出 PDF (支持智能一页)
- `GET /api/resumes/{id}/pdf-html` - HTML 渲染 PDF 导出
- `GET /api/resumes/{id}/html` - 获取 HTML 预览

### 外部集成 API
- `POST /api/resumes/from-dify` - Dify 工作流集成入口

## 核心功能实现

### 用户认证系统
- JWT 令牌认证，支持访问令牌和刷新令牌
- BCrypt 密码哈希加密
- 令牌黑名单机制，确保安全登出
- 基于角色的权限控制 (普通用户/管理员)

### PDF 导出引擎
项目支持双 PDF 引擎：

#### ReportLab 引擎
- 使用 HarmonyOS Sans 字体，完美支持中文
- 智能一页压缩算法，自适应字体和间距
- 支持 Markdown 加粗、斜体格式

#### HTML 渲染引擎  
- 使用 Playwright 进行 HTML 转 PDF
- 解决传统方式段落丢失问题
- 支持复杂布局和样式

### 智能一页功能
- 内容分析算法，估算总高度需求
- 自适应压缩策略，字体大小最多减少 15%
- 动态间距调整，最多减少 40%
- 页面边距优化，必要时减少 20%

### AI 对话流集成
- 支持实时流式对话，提升用户体验
- 自动跳转到编辑页面，无缝衔接
- 错误处理增强，支持详细错误信息展示

## 开发规范

### 代码风格
- 后端遵循 PEP 8 Python 编码规范
- 前端使用 ESLint 和 Prettier 格式化
- 组件使用 JSX 语法，遵循 React 最佳实践

### 安全要求
- 所有用户输入必须验证和清理
- 密码使用 BCrypt 哈希存储
- API 接口实现适当的权限控制
- 避免在代码中硬编码敏感信息

### Git 工作流
- 使用语义化提交消息
- 功能开发使用分支，通过 PR 合并
- 发布时打标签，维护版本历史

## 测试和调试

### 测试账户
- 演示用户: demo@gmail.com / demo123
- 管理员: admin@gmail.com / admin123

### 调试工具
- 后端日志: `backend/backend.log`
- 前端控制台: 浏览器开发者工具
- API 测试: `tests/test_backend.py`

### 性能监控
- PDF 生成性能优化
- 数据库查询优化
- 前端包大小控制

## 部署指南

### 开发环境
使用 `./setup.sh` 进行一键配置，支持：
- 自动依赖检查和安装
- 环境变量交互式配置
- 内网穿透配置支持

### 生产环境
使用 `./deploy-docker.sh` 进行 Docker 部署：
- 支持 PostgreSQL 数据库
- 自动 SSL 证书配置
- 负载均衡和监控

### 内网穿透支持
- 花生壳、ngrok 等工具支持
- 自动域名检测和 API 地址切换
- 无需手动修改配置文件

## 故障排除

### 常见问题
1. **端口冲突**: 检查 8080 和 3000 端口占用
2. **数据库连接**: 确认连接字符串和服务状态
3. **PDF 生成失败**: 检查字体文件和依赖安装
4. **认证问题**: 验证 JWT 密钥配置

### 日志查看
```bash
# Docker 部署
docker-compose logs -f

# 传统部署  
tail -f backend/backend.log
tail -f frontend/frontend.log
```

## 版本管理

### 当前版本: v2.1.1
- 弹窗层级修复和错误处理增强
- 内网穿透支持优化
- React Portal 弹窗渲染
- Dify 错误事件标准处理

### 版本发布流程
1. 更新版本号和 CHANGELOG
2. 运行完整测试套件
3. 构建和验证部署包
4. 创建 Git 标签和发布

## 开发注意事项

### 代码修改原则
- 优先编辑现有文件，避免创建新文件
- 保持代码风格一致性
- 遵循现有架构模式
- 确保向后兼容性

### 数据库迁移
- 使用 SQLAlchemy 迁移工具
- 备份生产数据库
- 测试迁移脚本

### 性能优化
- 前端代码分割和懒加载
- 后端数据库查询优化
- PDF 生成缓存机制

### 安全考虑
- 定期更新依赖包
- 输入验证和 SQL 注入防护
- HTTPS 强制和 CORS 配置
- 敏感信息环境变量化

这个项目专注于提供专业的简历编辑和管理功能，所有开发工作都应围绕用户体验和系统稳定性展开。