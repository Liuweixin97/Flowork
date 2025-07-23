# CLAUDE.md

此文件为Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

这是一个简历编辑器应用程序，旨在与Dify AI工作流集成。包含以下组成部分：
- **后端**: Python Flask API，使用SQLAlchemy ORM进行简历管理和PDF生成
- **前端**: React SPA，使用Vite构建系统和Tailwind CSS样式
- **集成**: 接收来自Dify HTTP节点的简历数据，并提供可视化编辑界面

## 核心架构

### 后端结构
- `app.py`: Flask应用工厂，配置CORS以支持多源访问
- `models.py`: SQLAlchemy模型，Resume实体存储markdown和结构化JSON数据
- `routes/`: 按功能拆分的API蓝图 (resume_routes, debug_routes)  
- `services/`: 业务逻辑模块 (markdown_parser, pdf_generator, html_pdf_generator)

### 前端结构
- React Router设置，包含两个主要路由: HomePage (/) 和 EditPage (/edit/:id)
- 组件架构: Layout包装器、支持markdown的ResumeEditor、ResumeList
- `utils/api.js`中的API通信层使用axios
- 使用Tailwind CSS样式和react-hot-toast通知

### 数据库架构
- 单一`Resume`模型，字段包括: id, title, raw_markdown, structured_data (JSON), timestamps
- SQLite数据库，启动时自动创建表

## 开发命令

### 后端开发
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 前端开发  
```bash
cd frontend
npm install
npm run dev          # 开发服务器
npm run build        # 生产构建
npm run lint         # ESLint检查
npm run preview      # 预览构建
```

### Docker部署
```bash
./start.sh           # 启动所有服务
./stop.sh            # 停止所有服务
docker-compose logs -f  # 查看日志
```

## API集成模式

### Dify集成端点
- POST `/api/resumes/from-dify` - 接收Dify工作流数据的主要集成点
- 期望JSON格式: `{"resume_markdown": "...", "title": "..."}`
- 返回简历ID和编辑URL用于用户重定向

### 核心CRUD操作
- GET `/api/resumes` - 列出所有简历
- GET `/api/resumes/{id}` - 获取特定简历及结构化数据
- PUT `/api/resumes/{id}` - 更新简历内容
- GET `/api/resumes/{id}/pdf` - 导出为PDF (支持 `smart_onepage=true` 参数)
- GET `/api/resumes/{id}/pdf-html` - 使用HTML渲染方式导出PDF
- GET `/api/resumes/{id}/html` - 获取HTML内容用于预览

## 主要依赖

### 后端
- Flask + Flask-SQLAlchemy + Flask-CORS API层
- reportlab 用于PDF生成，支持HarmonyOS Sans字体
- python-markdown 用于处理markdown
- python-dotenv 用于环境配置
- playwright 用于HTML转PDF (备用方案)

### 前端
- React 18 配合React Router进行SPA导航
- Vite作为构建工具，配置ESLint
- axios HTTP客户端，react-markdown用于渲染
- lucide-react图标，react-hot-toast通知

## 环境配置

### 后端 (.env)
```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///resume_editor.db  
HOST=0.0.0.0
PORT=8080
```

### 前端 (.env)
```
VITE_API_URL=http://localhost:8080
```

## Docker网络设置

- 配置连接到外部`dify_default`网络用于Dify集成
- 内部`resume_network`用于服务通信
- 为后端服务配置健康检查
- SQLite数据库的持久化卷

## 字体配置

### PDF字体设置
- 主要字体: HarmonyOS Sans (简体中文)
- 字体文件位置: `backend/fonts/HarmonyOS Sans/HarmonyOS_Sans_SC/`
- 支持字重: Regular, Bold, Medium, Light
- 如果HarmonyOS Sans不可用，自动回退到系统字体
- 字体注册在服务启动时进行

### 使用的字体字重
- NameTitle: Bold字重用于简历姓名/标题
- SectionTitle: Medium字重用于章节标题
- JobTitle: Medium字重用于职位/教育标题
- ModernBodyText: Regular字重用于正文内容
- ContactInfo: Regular字重用于联系信息

## 智能一页功能

### 概述
智能PDF压缩系统，自动调整字体大小、间距和边距，使简历内容适合单张A4纸，同时保持可读性。

### 实现细节
- **内容分析**: `_analyze_content_requirements()` 估算总高度需求
- **智能压缩**: `_create_optimized_styles()` 在需要时生成缩小的样式
- **动态调整**: 字体大小最多减少15%，间距减少高达40%
- **边距优化**: 页面边距必要时减少高达20%

### 使用方法
- 前端: 导出下拉菜单中的"智能一页导出"选项
- API: 在PDF导出端点添加 `smart_onepage=true` 参数
- 自动: 系统检测内容是否超过一页并应用优化

### 算法特性
- **自适应压缩策略**: 基于内容密度的两级压缩
  - 标准压缩 (比例 ≥ 0.75): 字体缩放85-95%，间距缩放60-90%
  - 激进压缩 (比例 < 0.75): 字体缩放75%+，间距缩放45%+
- **标题特定优化**: 标题元素独立缩放
  - 姓名标题: 最小18pt字体大小，优化行距
  - 联系信息: 最小8pt，减少间距
- **精细元素控制**: 各元素字体大小最小值保证可读性
  - 正文: 最小8pt，章节标题: 最小12pt
  - 项目符号: 最小8pt，减少缩进
- **智能间距减少**: 最多55%间距压缩，同时保持层次结构
- **增强边距优化**: 基于压缩需求的动态边距减少

## HTML转PDF功能 (新增)

### 概述
新增的HTML渲染PDF导出功能，解决传统ReportLab方式中的段落丢失问题。

### 实现方式
- **双引擎支持**: 优先使用wkhtmltopdf，回退到Playwright
- **标准markdown转换**: 使用python-markdown库进行HTML转换
- **CSS样式优化**: 专为PDF打印优化的CSS样式
- **智能一页支持**: HTML方式也支持智能一页压缩

### 新增API端点
- GET `/api/resumes/{id}/pdf-html` - HTML渲染方式PDF导出
- GET `/api/resumes/{id}/html` - 获取简历HTML内容

### 依赖安装
```bash
# 方案1: 安装Playwright (推荐)
pip install playwright
playwright install chromium

# 方案2: 安装wkhtmltopdf (macOS上已被禁用)
# brew install wkhtmltopdf  # 不再可用
```

### 前端集成
导出菜单分为两个部分：
- **传统PDF导出 (ReportLab)**: 原有的PDF生成方式
- **HTML渲染导出 (推荐)**: 新的HTML转PDF方式，更好的格式兼容性

## 测试文件

项目根目录中的测试脚本：
- `test_backend.py`, `test_dify_connection.py` - 后端API测试
- `test_html_pdf.py` - HTML转PDF功能测试
- `check_status.py`, `service_manager.py` - 服务管理工具
- 各种针对特定功能验证的手动测试脚本

## 版本历史

### v1.3.0 - HTML转PDF优化 (2025-07-23)
- **新增功能**:
  - 新增HTML转PDF导出方式，解决段落丢失问题
  - 支持双PDF引擎：wkhtmltopdf和Playwright
  - 重新设计的导出菜单，分传统和HTML渲染两种方式
  - 新增HTML内容预览API端点
- **技术改进**:
  - 新增`html_pdf_generator.py`服务
  - 优化CSS样式适配A4打印
  - HTML渲染也支持智能一页功能
- **依赖更新**:
  - 新增playwright依赖用于HTML转PDF

### v1.2.0 - PDF导出加粗斜体支持 (之前版本)
- **新增功能**:
  - PDF导出支持markdown加粗和斜体格式
  - 改进字体渲染效果
- **修复问题**:
  - 修复自动生成测试简历的问题
  - 优化自动发送消息机制

### v1.1.0 - 智能一页功能 (之前版本)
- **新增功能**:
  - 智能一页PDF导出功能
  - 自适应字体和间距压缩算法
  - 动态页面边距优化
- **技术改进**:
  - 增强PDF生成器压缩策略
  - 改进内容高度估算算法

### v1.0.0 - 基础版本 (之前版本)
- **基础功能**:
  - 简历的创建、编辑、删除
  - Markdown编辑器和实时预览
  - PDF导出功能
  - Dify工作流集成
- **技术架构**:
  - Flask后端 + React前端
  - SQLite数据库
  - HarmonyOS Sans字体支持

## 重要说明
在进行任何修改时，请遵循以下原则：
- 总是先阅读现有代码以了解架构和规范
- 保持代码风格一致性
- 优先编辑现有文件而非创建新文件
- 遵循安全最佳实践，避免暴露密钥和敏感信息