# 简历编辑器 - 使用指南

## 🎯 项目概述

这是一个专为配合Dify使用的智能简历修改助手，支持接收Dify HTTP节点输出的Markdown简历，提供可视化编辑界面和PDF导出功能。

## ✨ 已实现功能

✅ **Dify集成**: 接收来自Dify HTTP节点的简历数据  
✅ **Markdown解析**: 智能解析简历结构  
✅ **可视化编辑**: 现代化的实时编辑器  
✅ **PDF导出**: 一键生成精美PDF简历  
✅ **自动保存**: 编辑内容自动保存  
✅ **美观界面**: 基于Tailwind CSS的现代UI  
✅ **容器化部署**: Docker一键部署  

## 🚀 快速开始

### 方法一：手动启动（推荐用于开发）

#### 1. 启动后端服务
```bash
cd backend
pip install -r requirements.txt
python app.py
```

#### 2. 启动前端服务
```bash
cd frontend
npm install
npm run dev
```

### 方法二：Docker部署（推荐用于生产）
```bash
./start.sh
```

## 🔗 与Dify集成配置

### 在Dify工作流中添加HTTP节点

**配置参数**：
- **方法**: POST
- **URL**: `http://localhost:8080/api/resumes/from-dify`
- **请求头**: `Content-Type: application/json`
- **请求体**:
```json
{
  "resume_markdown": "{{LLM生成的简历内容}}",
  "title": "{{简历标题}}"
}
```

### 示例Dify工作流

```
开始 → LLM节点(生成简历) → HTTP节点(发送到简历编辑器) → 结束
```

## 📋 API接口说明

### 核心接口

| 接口 | 方法 | 说明 |
|-----|------|------|
| `/api/resumes/from-dify` | POST | 接收Dify数据 |
| `/api/resumes` | GET | 获取简历列表 |
| `/api/resumes/{id}` | GET | 获取特定简历 |
| `/api/resumes/{id}` | PUT | 更新简历 |
| `/api/resumes/{id}/pdf` | GET | 导出PDF |
| `/api/health` | GET | 健康检查 |

### 示例请求

#### 从Dify接收简历数据
```bash
curl -X POST http://localhost:8080/api/resumes/from-dify \\
  -H "Content-Type: application/json" \\
  -d '{
    "resume_markdown": "# 张三\\n\\n## 个人信息\\n- 邮箱: zhang@example.com",
    "title": "张三的简历"
  }'
```

响应：
```json
{
  "success": true,
  "message": "简历接收成功",
  "resume_id": 1,
  "edit_url": "/edit/1"
}
```

## 🛠️ 项目结构

```
resume-editor/
├── backend/                 # Python Flask后端
│   ├── app.py              # 主应用文件
│   ├── models.py           # 数据模型
│   ├── routes/             # API路由
│   │   └── resume_routes.py
│   ├── services/           # 业务服务
│   │   ├── markdown_parser.py  # Markdown解析
│   │   └── pdf_generator.py    # PDF生成
│   ├── requirements.txt    # Python依赖
│   └── Dockerfile         # 后端容器配置
├── frontend/               # React前端
│   ├── src/
│   │   ├── components/     # React组件
│   │   ├── pages/         # 页面组件
│   │   └── utils/         # 工具函数
│   ├── package.json       # Node.js依赖
│   └── Dockerfile         # 前端容器配置
├── docker-compose.yml      # Docker编排
├── start.sh               # 启动脚本
├── stop.sh                # 停止脚本
└── README.md              # 项目文档
```

## 💻 技术栈

### 后端
- **Python 3.9+**
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

## 📱 使用流程

1. **在Dify中创建简历生成工作流**
2. **配置HTTP节点发送简历到本服务**
3. **用户在浏览器中访问编辑链接**
4. **可视化编辑简历内容**
5. **一键导出PDF格式简历**

## 🎨 界面截图说明

### 主页面
- 显示所有从Dify接收的简历
- 支持编辑、PDF导出、删除操作
- 显示简历创建和更新时间

### 编辑器页面
- 左侧：Markdown编辑器
- 右侧：实时预览
- 顶部：保存、导出PDF按钮
- 自动保存功能

## 🐛 故障排除

### 常见问题

1. **端口冲突**
   - 检查8080和3000端口是否被占用
   - 修改配置文件中的端口

2. **Docker网络问题**
   - 确认Dify网络配置
   - 检查防火墙设置

3. **依赖安装失败**
   - 确认Python和Node.js版本
   - 使用国内镜像源

### 日志查看
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务
docker-compose logs -f resume-backend
```

## 📞 技术支持

如有问题，请检查：
1. Python版本 >= 3.9
2. Node.js版本 >= 16
3. Docker版本 >= 20.0
4. 网络连接正常

## 🚀 扩展功能建议

未来可以考虑添加：
- 简历模板选择
- 更多导出格式（Word、HTML）
- 简历评分功能
- 多用户支持
- 云存储集成

---

**现在您的简历编辑器已经准备就绪！** 🎉

开始使用：
1. 启动服务：`./start.sh`
2. 访问：http://localhost:3000
3. 在Dify中配置HTTP节点指向：http://localhost:8080/api/resumes/from-dify