# 项目文件组织规范

## 🏗️ 项目目录结构

```
浩流简历编辑器/
├── 📋 README.md                    # 项目主要文档
├── 📋 CLAUDE.md                    # Claude 开发指导文档
├── 🔧 docker-compose.yml           # Docker 编排配置
├── 🚫 .gitignore                  # Git 忽略文件配置
│
├── 📁 docs/                       # 📚 文档目录
│   ├── 📋 CHANGELOG.md             # 版本更新日志
│   ├── 📋 VERSION.md               # 版本信息
│   ├── 📋 CONTRIBUTING.md          # 贡献指南
│   ├── 📋 CHATFLOW_INTEGRATION.md  # Chatflow 集成文档
│   ├── 📁 api/                     # API 文档
│   │   └── 📋 dify-api.md
│   ├── 📁 guides/                  # 用户指南
│   │   └── 📋 user-guide.md
│   └── 📁 development/             # 开发文档
│       ├── 📋 project-structure.md
│       ├── 📋 requirements.md
│       ├── 📋 dify-solutions.md
│       ├── 📋 prompts-backup.md
│       └── 📋 scripts-readme.md
│
├── 📁 backend/                    # 🐍 Python 后端
│   ├── 🐳 Dockerfile
│   ├── 🔧 requirements.txt
│   ├── 🚀 app.py                  # Flask 主应用
│   ├── 📊 models.py               # 数据模型
│   ├── 📁 routes/                 # API 路由
│   │   ├── auth_routes.py
│   │   ├── resume_routes.py
│   │   ├── chatflow_routes.py
│   │   ├── notification_routes.py
│   │   └── debug_routes.py
│   ├── 📁 services/               # 业务服务
│   │   ├── auth_service.py
│   │   ├── markdown_parser.py
│   │   ├── pdf_generator.py
│   │   ├── html_pdf_generator.py
│   │   └── dify_chatflow_service.py
│   ├── 📁 fonts/                  # 字体文件 (保留用于兼容)
│   ├── 📁 instance/               # Flask 实例文件
│   └── 📁 venv/                   # Python 虚拟环境
│
├── 📁 frontend/                   # ⚛️ React 前端
│   ├── 🐳 Dockerfile
│   ├── 📦 package.json
│   ├── 🔧 vite.config.js
│   ├── 🎨 tailwind.config.js
│   ├── 📄 index.html
│   ├── 🌐 nginx.conf
│   ├── 📁 src/
│   │   ├── 🚀 main.jsx            # 应用入口
│   │   ├── 📱 App.jsx             # 主组件
│   │   ├── 🎨 index.css           # 全局样式
│   │   ├── 📁 components/         # React 组件
│   │   │   ├── Layout.jsx
│   │   │   ├── ResumeEditor.jsx
│   │   │   ├── ResumeList.jsx
│   │   │   ├── ChatflowDialog.jsx
│   │   │   ├── NewResumeNotification.jsx
│   │   │   ├── EmptyState.jsx
│   │   │   ├── ProtectedRoute.jsx
│   │   │   └── 📁 auth/
│   │   │       ├── LoginForm.jsx
│   │   │       └── RegisterForm.jsx
│   │   ├── 📁 pages/              # 页面组件
│   │   │   ├── HomePage.jsx
│   │   │   ├── EditPage.jsx
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   └── ResumesPage.jsx
│   │   ├── 📁 contexts/           # React Context
│   │   │   └── AuthContext.jsx
│   │   ├── 📁 hooks/              # 自定义 Hooks
│   │   │   ├── useAutoRedirect.js
│   │   │   ├── useNotifications.js
│   │   │   └── useResumeNotification.js
│   │   └── 📁 utils/              # 工具函数
│   │       ├── api.js
│   │       └── helpers.js
│   ├── 📁 dist/                   # 构建输出
│   └── 📁 node_modules/           # Node 依赖
│
├── 📁 scripts/                   # 🔧 脚本工具
│   ├── 📁 deployment/            # 部署脚本
│   │   ├── start-full-environment.sh
│   │   ├── stop-full-environment.sh
│   │   └── launch-environment.sh
│   ├── 📁 development/           # 开发脚本
│   │   ├── quick-start.sh
│   │   ├── quick-stop.sh
│   │   ├── check-status.sh
│   │   ├── check_status.py
│   │   └── dify_debug.py
│   └── 📁 management/            # 管理脚本
│       └── manage.py
│
├── 📁 tests/                     # 🧪 测试文件
│   ├── test_backend.py
│   ├── test_chatflow_integration.py
│   ├── test_dify_connection.py
│   ├── test_dify_http_node.py
│   ├── test_dify_simple.py
│   ├── test_font_rendering.py
│   ├── test_full_conversation.py
│   ├── test_html_pdf.py
│   └── mock_dify_service.py
│
├── 📁 assets/                    # 📦 静态资源
│   └── 📁 fonts/                 # 字体文件
│       ├── 📁 HarmonyOS Sans/
│       ├── NotoSansCJKsc-Regular.otf
│       ├── SourceHanSansSC-Regular.otf
│       └── SourceHanSansSC-VF.otf
│
├── 📁 archive_scripts/           # 📦 归档脚本
│   ├── debug_json.py
│   ├── dify_integration_fix.py
│   ├── start.sh
│   ├── stop.sh
│   └── ...
│
├── 📁 logs/                      # 📋 日志文件
│   ├── backend.log
│   ├── frontend.log
│   └── ...
│
└── 📁 temp/                      # 🗂️ 临时文件
    ├── *.pid
    ├── test_*.pdf
    └── ...
```

## 📏 文件命名规范

### 🐍 Python 文件
- 使用下划线分隔: `user_service.py`
- 类名使用驼峰命名: `class UserService:`
- 函数名使用下划线: `def get_user_info():`

### ⚛️ JavaScript/React 文件
- 组件使用大驼峰: `UserProfile.jsx`
- 工具函数使用小驼峰: `apiHelper.js`
- 常量使用全大写: `API_ENDPOINTS.js`

### 📋 文档文件
- 使用连字符分隔: `user-guide.md`
- 英文小写，语义清晰
- 特殊文档大写: `README.md`, `CHANGELOG.md`

### 🔧 脚本文件
- 使用连字符分隔: `quick-start.sh`
- 描述功能动作: `start-services.sh`
- Python 脚本使用下划线: `check_status.py`

## 📂 目录组织原则

### 📚 文档组织 (`docs/`)
- **api/**: API 接口文档
- **guides/**: 用户使用指南
- **development/**: 开发相关文档

### 🔧 脚本组织 (`scripts/`)
- **deployment/**: 生产部署脚本
- **development/**: 开发调试脚本
- **management/**: 项目管理脚本

### 🧪 测试组织 (`tests/`)
- 按功能模块组织测试文件
- 包含模拟服务和测试数据
- 测试文件以 `test_` 开头

### 📦 资源组织 (`assets/`)
- **fonts/**: 字体文件
- **images/**: 图片资源 (如有)
- **templates/**: 模板文件 (如有)

## 🗂️ 文件分类说明

### 🔴 核心文件 (不可移动)
- `README.md`, `CLAUDE.md`
- `docker-compose.yml`
- `backend/app.py`, `frontend/src/main.jsx`

### 🟡 配置文件 (谨慎修改)
- `package.json`, `requirements.txt`
- `vite.config.js`, `tailwind.config.js`
- `.gitignore`

### 🟢 可移动文件
- 文档、脚本、测试文件
- 日志、临时文件
- 字体、静态资源

### 🔵 自动生成文件 (忽略)
- `node_modules/`, `venv/`
- `dist/`, `build/`
- `*.log`, `*.pid`

## 🧹 清理维护规范

### 定期清理
- 删除过期日志文件 (`logs/`)
- 清空临时文件 (`temp/`)
- 更新 `.gitignore` 忽略规则

### 版本管理
- 重要文档放在 `docs/` 目录
- 测试文件统一放在 `tests/` 目录
- 废弃脚本移动到 `archive_scripts/`

### 依赖管理
- 定期更新 `requirements.txt`
- 清理未使用的 npm 包
- 移除重复的字体文件

## 🎯 最佳实践

1. **保持结构清晰**: 每个目录职责单一明确
2. **命名语义化**: 文件名能体现其功能用途
3. **分类合理**: 相关文件放在同一目录
4. **定期维护**: 清理无用文件和依赖
5. **文档同步**: 结构变更及时更新文档

---

**维护者**: 浩流简历编辑器项目组  
**更新时间**: 2025-07-25  
**版本**: v2.1.0