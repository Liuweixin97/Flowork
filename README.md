# 浩流简历编辑器 v2.1.0 - 多用户智能简历系统

支持多用户认证的智能简历编辑系统，集成Dify AI工作流，提供完整的用户注册、登录、简历创建、编辑和PDF导出功能。

## ✨ v2.1.0 核心功能

### 👥 多用户认证系统
- 🔐 **完整认证**: 用户注册、登录、权限控制、JWT令牌管理
- 🛡️ **数据隔离**: 每个用户只能查看和编辑自己的简历
- 👤 **用户管理**: 支持管理员和普通用户角色
- 🔑 **安全加密**: BCrypt密码哈希，安全令牌机制

### 🚀 一键启动环境
- ⚡ **完整环境**: 一键启动Dify和简历编辑器所有服务
- 🛠️ **智能管理**: 自动依赖检查、PID管理、后台运行
- 🌐 **内网穿透**: 支持花生壳等内网穿透工具访问
- 📊 **状态监控**: 实时服务状态检查和日志输出

### 🤖 AI智能对话
- 💬 **流式对话**: 支持实时流式AI对话，体验更流畅
- 🧠 **浩流集成**: 完整集成浩流简历·flowork对话系统
- 🎯 **智能生成**: AI引导式简历创建，个性化内容生成
- 🔄 **实时跳转**: 简历生成完成后自动跳转编辑页面

### 📝 强化编辑功能
- ✏️ **可视化编辑**: 现代化Markdown编辑器，支持实时预览
- 🎨 **弹窗优化**: 使用React Portal的高层级通知弹窗
- 💾 **自动保存**: 编辑内容自动保存，用户关联存储
- 🔀 **权限控制**: 基于用户权限的编辑和查看控制

### 📄 专业PDF导出
- 📋 **多引擎支持**: ReportLab和HTML渲染双PDF引擎
- 🎨 **智能一页**: 自适应压缩算法，完美单页呈现
- 🆔 **中文字体**: HarmonyOS Sans字体，完美中文支持
- ⚡ **快速导出**: 优化的PDF生成性能

### 💻 现代化架构
- 🏗️ **微服务架构**: 前后端分离，模块化设计
- 🔗 **API集成**: 完整的RESTful API和认证系统
- 🐳 **容器化**: Docker支持，一键部署
- 📱 **响应式**: 完美适配各种设备屏幕

## 🚀 快速开始

### ⚡ 一键启动完整环境（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd 浩流简历编辑器
```

2. **一键启动完整环境**
```bash
./一键启动完整环境.sh
```
*这将自动启动Dify和简历编辑器的所有服务*

3. **体验完整功能**
- 🌐 前端界面: http://localhost:3000
- 🔧 后端API: http://localhost:8080
- 🤖 Dify服务: http://localhost (需重新安装)
- 👤 测试账号: demo@gmail.com / demo123

4. **停止所有服务**
```bash
./停止完整环境.sh
```

### 📱 快速体验模式

使用便捷脚本快速启动：
```bash
./快速启动.sh    # 启动简历编辑器服务
./检查状态.sh    # 检查服务运行状态
./快速停止.sh    # 停止简历编辑器服务
```

### 🐳 Docker部署（生产环境）

1. **启动服务**
```bash
./start.sh
```

2. **访问应用**
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8080

### ⚙️ 手动部署（开发环境）

#### 后端服务

```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### 前端服务

```bash
cd frontend
npm install
npm run dev
```

## 📡 与Dify集成

### 🤖 AI Chatflow集成（推荐）

本项目提供完整的AI对话式简历创建体验：

1. **用户体验流程**：
   - 用户点击「AI创建简历」
   - AI助手引导用户逐步填写信息
   - 自动生成个性化简历
   - 直接跳转到编辑页面进行微调

2. **Dify工作流配置**：
   - 创建Chatflow工作流用于简历生成
   - 配置多轮对话收集用户信息
   - 工作流完成时返回简历内容

3. **配置环境变量**：
   ```bash
   DIFY_API_BASE=http://localhost:8001/v1
   DIFY_API_KEY=your-dify-api-key
   DIFY_WORKFLOW_ID=your-workflow-id
   ```

### 📡 传统HTTP节点集成

如需使用HTTP节点方式集成：

1. **添加HTTP节点**
2. **配置请求参数**：
   - **方法**: POST
   - **URL**: `http://localhost:8080/api/resumes/from-dify`
   - **请求头**: `Content-Type: application/json`
   - **请求体**:
   ```json
   {
     "resume_markdown": "{{生成的简历Markdown内容}}",
     "title": "{{简历标题}}"
   }
   ```

3. **示例工作流**：
```
LLM节点(生成简历) → HTTP节点(发送到简历编辑器) → 返回编辑链接
```

### Dify网络配置

如果Dify运行在Docker中，确保两个服务在同一网络中：

```bash
# 查看Dify网络
docker network ls | grep dify

# 连接到Dify网络（已在docker-compose.yml中配置）
```

## 📚 API文档

### 接收Dify数据
```http
POST /api/resumes/from-dify
Content-Type: application/json

{
  "resume_markdown": "# 张三\n\n## 个人信息\n...",
  "title": "张三的简历"
}
```

### 获取简历列表
```http
GET /api/resumes
```

### 获取特定简历
```http
GET /api/resumes/{id}
```

### 更新简历
```http
PUT /api/resumes/{id}
Content-Type: application/json

{
  "title": "新标题",
  "raw_markdown": "更新的内容"
}
```

### 导出PDF
```http
GET /api/resumes/{id}/pdf
```

## 🏗️ 项目架构

```
resume-editor/
├── backend/              # Python Flask后端
│   ├── app.py           # 主应用文件
│   ├── models.py        # 数据模型
│   ├── routes/          # API路由
│   ├── services/        # 业务服务
│   └── requirements.txt # Python依赖
├── frontend/            # React前端
│   ├── src/
│   │   ├── components/  # React组件
│   │   ├── pages/       # 页面组件
│   │   ├── utils/       # 工具函数
│   │   └── main.jsx     # 入口文件
│   └── package.json     # Node.js依赖
├── docker-compose.yml   # Docker编排
├── start.sh            # 启动脚本
└── stop.sh             # 停止脚本
```

## 🛠️ 技术栈

### 后端
- **Python 3.11+**
- **Flask** - Web框架
- **SQLAlchemy** - ORM
- **WeasyPrint** - PDF生成
- **python-markdown** - Markdown解析

### 前端
- **React 18** - UI框架
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **React Router** - 路由管理
- **React Markdown** - Markdown渲染

### 部署
- **Docker & Docker Compose**
- **Nginx** (前端静态文件服务)

## 📋 使用流程

1. **在Dify中创建简历生成工作流**
2. **配置HTTP节点发送简历到本服务**
3. **用户在浏览器中打开编辑链接**
4. **可视化编辑简历内容**
5. **导出PDF格式的最终简历**

## 🔧 配置说明

### 环境变量

#### 后端 (.env)
```bash
FLASK_DEBUG=True
SECRET_KEY=your-secret-key
HOST=0.0.0.0
PORT=8080
DATABASE_URL=sqlite:///resume_editor.db
```

#### 前端 (.env)
```bash
VITE_API_URL=http://localhost:8080
```

### Docker网络配置

如果需要与现有Dify部署集成：

1. **查看Dify网络**:
```bash
docker network ls
```

2. **修改docker-compose.yml**中的网络配置

3. **确保端口不冲突**

## 🐛 故障排除

### 常见问题

1. **端口冲突**
   - 检查8080和3000端口是否被占用
   - 修改docker-compose.yml中的端口映射

2. **Dify连接失败**
   - 确认网络配置正确
   - 检查防火墙设置
   - 验证URL地址正确

3. **PDF生成失败**
   - 确认WeasyPrint依赖已正确安装
   - 检查系统字体支持

4. **前端无法访问后端**
   - 检查CORS配置
   - 确认API_URL环境变量

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f resume-backend
docker-compose logs -f resume-frontend
```

### 重置数据

```bash
# 停止服务并删除数据卷
docker-compose down -v

# 重新启动
./start.sh
```

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 📄 许可证

MIT License

## 📞 支持

如有问题或建议，请提交Issue或联系维护团队。