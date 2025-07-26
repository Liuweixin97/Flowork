# 浩流简历编辑器

> 支持多用户认证的智能简历编辑系统，集成 AI 工作流，提供完整的简历创建、编辑和导出功能

## 核心特性

### 用户认证系统
- 完整的用户注册、登录、权限控制系统
- JWT 令牌认证，支持多用户数据隔离
- BCrypt 密码加密，安全可靠

### AI 智能集成
- 集成 Dify AI 工作流，支持智能简历生成
- 实时流式对话界面，用户体验流畅
- 自动跳转编辑页面，无缝衔接

### 专业PDF导出
- 双引擎支持：ReportLab 和 HTML 渲染
- 智能一页压缩算法，完美单页呈现
- HarmonyOS Sans 中文字体，专业美观

### 现代化架构
- 前后端分离设计，API 完整
- Docker 容器化部署，开箱即用
- 响应式界面，多设备适配

## 快速开始

### 一键部署（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd 浩流简历编辑器
```

2. **初始化配置**
```bash
./setup.sh
```
该脚本将自动配置环境变量、安装依赖并创建启动脚本。

3. **启动服务**
```bash
./start.sh
```

4. **访问应用**
- 前端界面：http://localhost:3000
- 后端 API：http://localhost:8080

### Docker 部署

1. **一键部署**
```bash
./deploy-docker.sh
```

2. **管理服务**
```bash
./docker-start.sh    # 启动服务
./docker-stop.sh     # 停止服务
./docker-logs.sh     # 查看日志
./docker-restart.sh  # 重启服务
```

## 项目结构

```
浩流简历编辑器/
├── setup.sh                 # 初始化配置脚本
├── deploy-docker.sh          # Docker 一键部署脚本
├── README.md                 # 项目文档
├── CLAUDE.md                 # 开发指导文档
├── backend/                  # Python Flask 后端
│   ├── app.py               # 主应用
│   ├── models.py            # 数据模型
│   ├── routes/              # API 路由
│   ├── services/            # 业务服务
│   └── requirements.txt     # Python 依赖
├── frontend/                # React 前端
│   ├── src/                 # 源码目录
│   │   ├── components/      # React 组件
│   │   ├── pages/          # 页面组件
│   │   ├── contexts/       # 状态管理
│   │   └── utils/          # 工具函数
│   └── package.json        # Node.js 依赖
├── scripts/                 # 项目脚本
│   ├── deployment/         # 部署相关
│   ├── development/        # 开发工具
│   └── management/         # 管理脚本
├── assets/                  # 静态资源
├── docs/                    # 完整文档
└── docker-compose.yml       # Docker 编排
```

## 环境配置

### 支持的数据库
- **SQLite**：开发环境，零配置启动
- **PostgreSQL**：生产环境，支持云平台部署

### 环境变量说明

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

# Dify 集成 (可选)
DIFY_API_KEY=your_dify_api_key
DIFY_API_URL=https://api.dify.ai/v1
```

#### 前端配置 (frontend/.env)
```bash
# API 配置
VITE_API_URL=http://localhost:8080
```

## AI 工作流集成

### Dify 集成配置

1. **创建 Chatflow 工作流**
   - 设计多轮对话收集用户信息
   - 配置简历内容生成逻辑

2. **配置环境变量**
   ```bash
   DIFY_API_KEY=your-api-key
   DIFY_WORKFLOW_ID=your-workflow-id
   ```

3. **前端集成**
   - 用户点击"AI 创建简历"
   - 打开对话界面进行信息收集
   - 自动生成简历并跳转编辑

### HTTP 节点集成（传统方式）

1. **添加 HTTP 节点**
   - 方法：POST
   - URL：`http://localhost:8080/api/resumes/from-dify`
   - 请求头：`Content-Type: application/json`

2. **请求体格式**
   ```json
   {
     "resume_markdown": "# 简历内容...",
     "title": "简历标题"
   }
   ```

## API 接口

### 认证相关
```http
POST /api/auth/register      # 用户注册
POST /api/auth/login         # 用户登录
POST /api/auth/logout        # 用户登出
GET  /api/auth/me           # 获取用户信息
```

### 简历管理
```http
GET    /api/resumes              # 获取简历列表
POST   /api/resumes              # 创建新简历
GET    /api/resumes/{id}         # 获取简历详情
PUT    /api/resumes/{id}         # 更新简历
DELETE /api/resumes/{id}         # 删除简历
GET    /api/resumes/{id}/pdf     # 导出 PDF
```

### 外部集成
```http
POST /api/resumes/from-dify      # Dify 工作流集成
```

## 内网穿透支持

### 支持的工具
- 花生壳
- ngrok
- 其他内网穿透工具

### 自动检测机制
前端会根据访问域名自动选择对应的后端 API 地址，无需手动配置。

### 配置示例
```bash
# 花生壳映射设置
外网地址: your-domain.vicp.fun:8080
内网地址: 127.0.0.1:8080
协议类型: TCP
```

## 测试账户

系统提供开发模式测试账户：

- **演示用户**：demo@gmail.com / demo123
- **管理员**：admin@gmail.com / admin123

## 技术栈

### 后端
- Python 3.8+
- Flask Web 框架
- SQLAlchemy ORM
- Flask-JWT-Extended 认证
- ReportLab/Playwright PDF 生成
- BCrypt 密码加密

### 前端
- React 18
- Vite 构建工具
- Tailwind CSS 样式框架
- React Router 路由管理
- Axios HTTP 客户端

### 部署
- Docker & Docker Compose
- PostgreSQL/SQLite 数据库
- Nginx 静态文件服务

## 故障排除

### 常见问题

1. **端口冲突**
   - 检查 8080 和 3000 端口占用情况
   - 修改配置文件中的端口设置

2. **数据库连接失败**
   - 确认数据库服务正常运行
   - 检查连接字符串配置

3. **PDF 导出失败**
   - 确认字体文件完整
   - 检查 Playwright 依赖安装

4. **前端无法访问后端**
   - 检查 CORS 配置
   - 确认 API URL 环境变量

### 查看日志

```bash
# Docker 部署
docker-compose logs -f

# 传统部署
tail -f backend/backend.log
tail -f frontend/frontend.log
```

### 重置数据

```bash
# 清理数据库
rm backend/instance/resume_editor.db

# 重启服务
./stop.sh && ./start.sh
```

## 开发指南

详细的开发说明请参考 [CLAUDE.md](CLAUDE.md) 文档。

### 开发环境搭建

1. **后端开发**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

2. **前端开发**
```bash
cd frontend
npm install
npm run dev
```

### 代码规范

- 后端遵循 PEP 8 Python 编码规范
- 前端使用 ESLint 代码检查
- 提交前请运行测试套件

## 版本历史

- **v2.1.1**：弹窗层级修复和错误处理增强
- **v2.1.0**：一键启动环境和弹窗优化
- **v2.0.0**：用户认证系统和多用户支持
- **v1.3.0**：HTML 转 PDF 优化
- **v1.2.0**：PDF 导出加粗斜体支持
- **v1.1.0**：智能一页功能
- **v1.0.0**：基础版本

详细版本信息请查看 [CHANGELOG.md](docs/CHANGELOG.md)。

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目。

1. Fork 项目仓库
2. 创建功能分支
3. 提交代码更改
4. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证。详情请查看 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件至项目维护者
- 参与项目讨论区