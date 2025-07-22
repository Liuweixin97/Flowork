# 简历编辑器 - 基于Dify的智能简历修改助手

一个专为配合Dify使用的简历编辑和修改工具，支持接收Dify HTTP节点输出的Markdown简历，提供可视化编辑界面和PDF导出功能。

## ✨ 功能特性

- 🔗 **Dify集成**: 接收来自Dify HTTP节点的简历数据
- 📝 **可视化编辑**: 现代化的Markdown编辑器，支持实时预览
- 📄 **PDF导出**: 一键导出精美的PDF格式简历
- 💾 **自动保存**: 编辑内容自动保存，无需担心数据丢失
- 🎨 **美观界面**: 基于Tailwind CSS的现代化UI设计
- 🐳 **容器化部署**: 支持Docker一键部署
- 🔄 **实时同步**: 与Dify工作流无缝对接

## 🚀 快速开始

### 方法一：Docker一键部署（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd resume-editor
```

2. **启动服务**
```bash
./start.sh
```

3. **访问应用**
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8080

### 方法二：手动部署

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

### 在Dify工作流中配置HTTP节点

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