# 简历编辑器 - 基于Dify的智能简历修改助手

一个专为配合Dify使用的简历编辑和修改工具，支持接收Dify HTTP节点输出的Markdown简历，提供可视化编辑界面和PDF导出功能。

## ✨ 功能特性

### 🤖 AI智能功能
- 💬 **AI对话助手**: 通过自然对话引导用户创建简历
- 🧠 **智能简历生成**: 基于Dify Chatflow的多轮对话收集用户信息
- 🎯 **个性化定制**: AI根据用户回答生成定制化简历内容

### 🔗 Dify深度集成
- 📡 **HTTP节点对接**: 接收Dify HTTP节点的简历数据
- 🔄 **工作流集成**: 支持Dify Chatflow工作流无缝对接
- ⚡ **实时通信**: 完整的会话管理和状态追踪

### 📝 强大编辑功能
- ✏️ **可视化编辑**: 现代化的Markdown编辑器，支持实时预览
- 💾 **自动保存**: 编辑内容自动保存，无需担心数据丢失
- 🔀 **双模式切换**: 支持Markdown源码编辑和预览模式

### 📄 专业导出功能
- 📋 **PDF导出**: 一键导出精美的PDF格式简历
- 🎨 **智能排版**: 支持智能一页优化，确保内容完美呈现
- 🆔 **中文字体**: 内置HarmonyOS Sans字体，完美支持中文显示

### 💻 现代化体验
- 🎨 **美观界面**: 基于Tailwind CSS的现代化UI设计
- 📱 **响应式设计**: 完美适配各种屏幕尺寸
- 🐳 **容器化部署**: 支持Docker一键部署

## 🚀 快速开始

### 🎯 体验AI简历助手（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd resume-editor
```

2. **一键启动所有服务**
```bash
./start_services.sh
```

3. **访问应用并体验AI功能**
- 前端界面: http://localhost:3002 (或查看终端输出)
- 后端API: http://localhost:8080
- 点击「AI创建简历」体验完整对话流程

4. **停止服务**
```bash
./stop_services.sh
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