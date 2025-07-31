# 更新日志

## [v2.2.0] - 2025-07-31 - 生产环境部署优化

### 🚀 生产环境特性
- **Docker 生产配置优化**: 使用非root用户运行容器，增强安全性
- **自动化部署系统**: 提供一键从GitHub部署脚本和GitHub Actions工作流
- **生产环境监控**: 完整的健康检查、资源限制和自动重启机制
- **企业级安全配置**: 安全检查清单、SSL/HTTPS配置、容器安全限制

### 🛠️ 部署和运维工具
- **一键部署脚本**: `deploy-production.sh` 和 `deploy-from-github.sh`
- **环境检查工具**: `check-dependencies.sh` 自动验证系统依赖
- **版本管理系统**: `version-management.sh` 统一版本号管理
- **完整的生产配置**: `docker-compose.prod.yml` 和 `.env.production.example`

### 📚 文档体系完善
- **生产部署指南**: README.md 重写，专注生产环境部署
- **技术栈文档**: CLAUDE.md 新增生产环境部署指南章节
- **依赖管理**: DEPENDENCIES.md 详细说明所有环境依赖和要求
- **CI/CD流水线**: GitHub Actions 自动化测试、构建和部署

### 🔧 架构优化
- **多阶段Docker构建**: 前端使用Nginx优化，后端安装Playwright依赖
- **资源管理**: 容器资源限制、日志管理、数据持久化
- **网络安全**: CORS配置、防火墙规则、API安全增强
- **性能监控**: 系统资源监控、应用性能指标、数据库优化建议

### 🏗️ 项目结构优化
- **清理冗余文件**: 删除archive_scripts、空目录和重复资源
- **代码质量**: ESLint配置、Python语法检查、依赖安全审计
- **环境分离**: 开发、测试、生产环境完全分离配置

## [v1.3.0] - 2025-07-23 - HTML转PDF优化

### 🎉 新增功能
- **HTML转PDF导出**: 新增基于HTML渲染的PDF导出方式，解决传统ReportLab方式中的段落丢失问题
- **双引擎支持**: 支持wkhtmltopdf (首选) 和 Playwright (备用) 两种PDF生成引擎
- **重新设计的导出菜单**: 清晰区分传统PDF导出和HTML渲染导出两种方式
- **HTML内容预览**: 新增HTML内容获取API，支持浏览器直接预览
- **智能一页兼容**: HTML渲染方式也完全支持智能一页压缩功能

### 🔧 技术改进
- 新增`backend/services/html_pdf_generator.py`服务模块
- 使用python-markdown标准库进行可靠的markdown到HTML转换
- 专为A4打印优化的CSS样式设计
- 完善的错误处理和依赖检查机制
- 自动检测可用的PDF生成引擎并智能回退

### 📋 API更新
- `GET /api/resumes/{id}/pdf-html` - HTML渲染方式PDF导出
- `GET /api/resumes/{id}/html` - 获取简历HTML内容 (支持`raw=true`参数直接预览)
- 保持所有现有API端点完全向后兼容

### 🎨 前端优化
- 导出菜单重新设计，分为"传统PDF导出"和"HTML渲染导出"两个区域
- HTML渲染方式标记为"推荐"，引导用户使用更稳定的导出方式
- 增强错误提示，显示具体失败原因和解决建议
- 导出文件名包含方式标识，便于用户区分不同导出结果

### 📦 依赖管理
- 新增playwright依赖，提供可靠的HTML转PDF能力
- 自动依赖检测，在缺少依赖时提供详细安装指导
- 支持Docker环境中的wkhtmltopdf集成

### 📚 文档更新
- CLAUDE.md恢复为中文版本，方便中文用户阅读
- 新增HTML转PDF功能详细说明和使用指南
- 整理完整的版本历史记录
- 更新API文档和依赖安装说明

### 🧪 测试增强
- 新增`test_html_pdf.py`专用测试脚本
- 验证HTML内容生成和PDF转换的完整流程
- 对比传统PDF和HTML渲染两种方式的输出质量
- 确认智能一页功能在HTML渲染下的正确性

---

## [v1.2.0] - 2025-07-22 - PDF导出格式优化

### 🎉 新增功能
- **Markdown格式支持**: PDF导出现在完全支持markdown的加粗(`**文本**`)和斜体(`*文本*`)格式
- **字体渲染增强**: 改进中文字体的粗体和斜体显示效果

### 🐛 修复问题
- 修复自动生成测试简历导致的数据混乱问题
- 优化自动发送消息机制，改为发送"开始"以避免自动生成简历
- 修复PDF导出中格式标记被直接显示的问题

### 🔧 技术改进
- 优化`_clean_markdown`方法，正确处理加粗和斜体标记
- 改进字体注册和渲染逻辑
- 增强ReportLab的格式化文本处理能力

---

## [v1.1.0] - 2025-07-21 - 智能一页功能

### 🎉 新增功能
- **智能一页PDF导出**: 自动分析简历内容，智能调整字体大小和间距，确保内容适合A4单页
- **自适应压缩算法**: 根据内容密度采用不同的压缩策略
- **动态边距优化**: 根据压缩需求自动调整页面边距

### 🔧 技术特性
- **两级压缩策略**: 
  - 标准压缩 (内容比例 ≥ 0.75): 字体缩放85-95%，间距缩放60-90%
  - 激进压缩 (内容比例 < 0.75): 字体缩放75%+，间距缩放45%+
- **精细化控制**: 不同元素设置最小字体大小，保证可读性
- **智能间距调整**: 最多55%间距压缩，同时保持视觉层次

### 📋 API更新
- PDF导出API支持`smart_onepage=true`参数
- 前端导出菜单新增"智能一页导出"选项

---

## [v1.0.0] - 2025-07-20 - 基础版本

### 🎉 核心功能
- **简历管理**: 创建、编辑、删除和列表查看简历
- **Markdown编辑器**: 支持实时预览的markdown编辑界面
- **PDF导出**: 基于ReportLab的专业PDF生成
- **Dify集成**: 完整的Dify AI工作流集成，支持HTTP节点数据接收

### 🏗️ 技术架构
- **后端**: Python Flask + SQLAlchemy ORM + SQLite数据库
- **前端**: React 18 + Vite + Tailwind CSS
- **字体支持**: HarmonyOS Sans中文字体，支持多种字重
- **API设计**: RESTful API设计，完整的CRUD操作

### 🔧 基础特性
- 响应式前端界面，支持桌面和移动端
- 自动保存功能，防止数据丢失
- 实时markdown预览
- 专业的PDF样式设计
- Docker容器化部署支持

### 📦 集成能力
- Dify工作流无缝集成
- HTTP请求节点数据接收
- 自动跳转到编辑界面
- 支持多种数据格式

---

## 技术栈概览

### 后端技术
- **框架**: Flask 2.3+
- **数据库**: SQLAlchemy + SQLite
- **PDF生成**: ReportLab + python-markdown + Playwright
- **字体**: HarmonyOS Sans 字体家族
- **API**: RESTful API设计

### 前端技术  
- **框架**: React 18 + Vite
- **样式**: Tailwind CSS
- **路由**: React Router
- **HTTP客户端**: Axios
- **图标**: Lucide React
- **通知**: React Hot Toast

### 开发工具
- **容器化**: Docker + Docker Compose
- **代码检查**: ESLint
- **版本控制**: Git
- **测试**: 自定义测试脚本

---

## 安装和使用

### 快速开始
```bash
# 克隆项目
git clone <repository-url>
cd resume-editor

# 启动服务 (推荐使用Docker)
./start.sh

# 或手动启动
cd backend && python app.py &
cd frontend && npm install && npm run dev
```

### 访问地址
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8080
- 健康检查: http://localhost:8080/api/health

### HTML转PDF依赖
```bash
# 安装Playwright (推荐)
pip install playwright
playwright install chromium
```

---

## 贡献指南

本项目欢迎贡献！请遵循以下原则：

1. **代码风格**: 保持与现有代码一致的风格
2. **测试**: 新功能请添加相应的测试
3. **文档**: 更新相关文档和CLAUDE.md
4. **提交信息**: 使用清晰的提交信息格式

## 许可证

[请添加适当的许可证信息]

---

*最后更新: 2025-07-23*