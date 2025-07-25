# CLAUDE.md

此文件为Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

这是一个支持多用户的简历编辑器应用程序，旨在与Dify AI工作流集成。包含以下组成部分：
- **后端**: Python Flask API，使用SQLAlchemy ORM和JWT认证进行用户管理、简历管理和PDF生成
- **前端**: React SPA，使用Vite构建系统、Tailwind CSS样式和React Context进行状态管理
- **认证系统**: 完整的用户注册、登录、权限控制系统，支持多用户数据隔离
- **集成**: 接收来自Dify HTTP节点的简历数据，并提供可视化编辑界面

## 核心架构

### 后端结构
- `app.py`: Flask应用工厂，配置JWT认证、CORS和PostgreSQL/SQLite数据库支持
- `models.py`: SQLAlchemy模型，包括User和Resume实体，支持用户关联和权限控制
- `routes/`: 按功能拆分的API蓝图 (resume_routes, auth_routes, debug_routes)  
- `services/`: 业务逻辑模块 (markdown_parser, pdf_generator, html_pdf_generator, auth_service)

### 前端结构
- React Router设置，包含认证路由: LoginPage (/login), RegisterPage (/register) 和主要功能: HomePage (/) 和 EditPage (/edit/:id)
- 组件架构: Layout包装器、支持markdown的ResumeEditor、ResumeList、认证组件(LoginForm, RegisterForm)
- `contexts/AuthContext.jsx`提供全局认证状态管理和JWT token处理
- `utils/api.js`中的API通信层使用axios，包含认证拦截器
- 使用Tailwind CSS样式和react-hot-toast通知

### 数据库架构
- **User模型**: 用户认证和资料管理，包括username, email, password_hash, full_name, is_admin等字段
- **Resume模型**: 简历数据，包括title, raw_markdown, structured_data (JSON), user_id (外键), is_public等字段
- 支持PostgreSQL (生产环境) 和SQLite (开发环境)，启动时自动创建表
- 用户-简历一对多关系，支持数据隔离和权限控制

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

### 用户认证API
- POST `/api/auth/register` - 用户注册
- POST `/api/auth/login` - 用户登录
- POST `/api/auth/logout` - 用户登出
- POST `/api/auth/refresh` - 刷新JWT token
- GET `/api/auth/me` - 获取当前用户信息
- PUT `/api/auth/profile` - 更新用户资料
- POST `/api/auth/change-password` - 修改密码
- POST `/api/auth/check-username` - 检查用户名可用性
- POST `/api/auth/check-email` - 检查邮箱可用性

### 核心CRUD操作 (支持认证和权限控制)
- GET `/api/resumes` - 列出简历 (认证用户看到自己的+公开的，未认证用户只看公开的)
- POST `/api/resumes` - 创建简历 (需要认证)
- GET `/api/resumes/{id}` - 获取特定简历及结构化数据 (基于权限)
- PUT `/api/resumes/{id}` - 更新简历内容 (需要所有者权限)
- DELETE `/api/resumes/{id}` - 删除简历 (需要所有者权限)
- GET `/api/resumes/{id}/pdf` - 导出为PDF (基于访问权限, 支持 `smart_onepage=true` 参数)
- GET `/api/resumes/{id}/pdf-html` - 使用HTML渲染方式导出PDF (基于访问权限)
- GET `/api/resumes/{id}/html` - 获取HTML内容用于预览 (基于访问权限)

## 主要依赖

### 后端
- Flask + Flask-SQLAlchemy + Flask-CORS + Flask-JWT-Extended API层
- Flask-Bcrypt 用于密码哈希加密
- reportlab 用于PDF生成，支持HarmonyOS Sans字体
- python-markdown 用于处理markdown
- python-dotenv 用于环境配置
- playwright 用于HTML转PDF (备用方案)
- email-validator 用于邮箱格式验证
- psycopg2 用于PostgreSQL连接 (生产环境)

### 前端
- React 18 配合React Router进行SPA导航
- Vite作为构建工具，配置ESLint
- axios HTTP客户端，react-markdown用于渲染
- lucide-react图标，react-hot-toast通知

## 环境配置

### 后端 (.env)
```
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=sqlite:///resume_editor.db  # 开发环境
# DATABASE_URL=postgresql://user:pass@localhost/dbname  # 生产环境
HOST=0.0.0.0
PORT=8080
FRONTEND_URL=http://localhost:3000
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

### v2.1.0 - 一键启动环境和弹窗优化 (2025-07-25)
- **新增功能**:
  - 新增一键启动完整环境脚本 (`一键启动完整环境.sh`)，支持同时启动Dify和简历编辑器前后端服务
  - 新增停止完整环境脚本 (`停止完整环境.sh`)，统一停止所有服务
  - 优化简历创建通知弹窗，使用React Portal渲染确保在最高层级显示
  - 添加弹窗动画效果，提升用户体验
- **配置更新**:
  - 更新内网穿透配置，支持新的花生壳域名 (mi3qm328989.vicp.fun)
  - 修复内网穿透访问时后端服务未运行的配置问题
  - 优化前端允许的主机配置，支持多种内网穿透工具
- **用户体验改进**:
  - 简历创建通知弹窗现在直接在对话流界面顶层显示，而非编辑器下方
  - 弹窗添加缩放动画和阴影效果，视觉体验更佳
  - 改进按钮样式，增加悬停效果
- **技术优化**:
  - 使用`createPortal`将弹窗渲染到document.body，避免z-index层级问题
  - 启动脚本增加详细的依赖检查和错误处理
  - 支持后台运行服务并保存PID文件便于管理
- **启动方式**:
  - 一键启动: `./一键启动完整环境.sh`
  - 原有启动: `python3 manage.py start`
  - 停止服务: `./停止完整环境.sh` 或 `python3 manage.py stop`

### v2.0.0 - 用户认证系统和多用户支持 (2025-07-23)
- **重大更新**:
  - 完整的用户认证系统：注册、登录、登出、密码修改
  - JWT令牌认证，支持访问令牌和刷新令牌
  - 用户数据隔离，个人简历管理
  - 基于角色的权限控制 (普通用户/管理员)
- **前端功能**:
  - 现代化登录/注册界面，响应式设计
  - 实时表单验证 (用户名/邮箱可用性检查)
  - 认证状态管理和自动令牌刷新
  - 开发模式快速登录功能 (demo@gmail.com, admin@gmail.com)
- **用户体验优化**:
  - 未登录用户友好提示和自动跳转
  - 丰富的简历模板，包含完整示例内容
  - 智能跳转，登录后返回原页面
- **技术架构**:
  - PostgreSQL生产数据库支持，兼容Heroku等云平台
  - BCrypt密码哈希，增强安全性
  - CORS优化，支持ngrok等工具进行生产部署
  - 令牌黑名单机制，安全登出
- **API增强**:
  - 新增完整认证API端点
  - 简历API增加权限控制和用户隔离
  - 向后兼容，支持原有Dify集成功能

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

## 用户认证和权限说明

### 开发模式测试账户
- **演示用户**: demo@gmail.com / demo123 (普通用户权限)
- **管理员**: admin@gmail.com / admin123 (管理员权限，可查看所有简历)

### 权限控制说明
- **未认证用户**: 只能查看公开简历，无法创建或编辑
- **普通用户**: 可以创建、编辑、删除自己的简历，查看自己的和公开的简历
- **管理员**: 可以查看和管理所有用户的简历

### 安全特性
- 密码使用BCrypt哈希存储
- JWT令牌有效期为24小时
- 支持令牌刷新和黑名单机制
- 邮箱格式验证和用户名唯一性检查
- CORS配置支持多域名访问

## Dify完整卸载记录 (2025-07-25)

### 卸载原因
- PostgreSQL配置文件损坏导致数据库容器持续重启
- 用户确认数据丢失可接受，要求完整卸载后手动重装

### 卸载操作记录

#### 1. 停止并删除所有Dify容器
```bash
cd /Users/liuweixin/Desktop/MyProjects/dify/docker
docker-compose down -v --remove-orphans
```
**结果**: 成功停止并删除了所有Dify相关容器

#### 2. 删除所有Dify相关Docker镜像
```bash
# 查找所有Dify镜像
docker images | grep dify

# 删除找到的镜像
docker rmi langgenius/dify-web:1.6.0
docker rmi langgenius/dify-api:1.6.0
docker rmi langgenius/dify-plugin-daemon:0.1.3-local
docker rmi langgenius/dify-sandbox:0.2.12
```
**结果**: 成功删除所有Dify Docker镜像，释放约2GB磁盘空间

#### 3. 清理Docker系统资源
```bash
# 清理未使用的卷
docker volume prune -f

# 清理未使用的网络
docker network prune -f
```
**结果**: 清理完成，无额外空间回收

#### 4. 删除Dify本地数据文件
```bash
# 删除整个volumes目录，包含数据库数据
rm -rf /Users/liuweixin/Desktop/MyProjects/dify/docker/volumes
```
**结果**: 成功删除所有持久化数据，包括：
- PostgreSQL数据库文件
- Redis缓存数据
- 应用配置和用户数据
- 上传的文件和媒体资源

#### 5. 更新简历编辑器配置
- 注释掉backend/.env中的Dify API配置
- 添加"已卸载，需重新配置"说明

### 卸载验证
```bash
# 确认没有Dify相关容器
docker ps -a | grep dify
# (无输出，确认清理完成)

# 确认没有Dify相关镜像
docker images | grep dify
# (无输出，确认清理完成)

# 确认数据目录已删除
ls -la /Users/liuweixin/Desktop/MyProjects/dify/docker/volumes
# (目录不存在，确认清理完成)
```

### 重新安装说明
如需重新安装Dify，请执行以下步骤：

1. **进入Dify目录**
   ```bash
   cd /Users/liuweixin/Desktop/MyProjects/dify/docker
   ```

2. **检查Docker Compose配置**
   ```bash
   # 确认docker-compose.yaml文件完整
   cat docker-compose.yaml
   ```

3. **启动Dify服务**
   ```bash
   # 拉取最新镜像并启动
   docker-compose up -d
   
   # 查看启动日志
   docker-compose logs -f
   ```

4. **等待服务初始化**
   - 数据库初始化需要1-2分钟
   - 等待所有容器状态变为healthy
   - 访问 http://localhost 确认服务可用

5. **重新配置简历编辑器集成**
   - 在Dify中创建新的应用
   - 获取新的API Key
   - 更新backend/.env中的DIFY_API_BASE和DIFY_API_KEY
   - 取消注释相关配置行

### 注意事项
- 此次卸载为完全清理，所有Dify数据已永久删除
- 重新安装后需要重新创建应用和配置API Key
- 简历编辑器的Dify集成功能在重新配置前将无法使用

## 重要说明
在进行任何修改时，请遵循以下原则：
- 总是先阅读现有代码以了解架构和规范
- 保持代码风格一致性
- 优先编辑现有文件而非创建新文件
- 遵循安全最佳实践，避免暴露密钥和敏感信息
- 认证相关的修改需要同时考虑前后端的兼容性
- 新增API端点时要考虑权限控制和数据隔离