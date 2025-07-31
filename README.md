# 浩流简历编辑器

> 企业级智能简历编辑系统，支持多用户认证、AI 工作流集成、专业PDF导出，专为生产环境设计

[![Deploy Status](https://github.com/your-username/resume-editor/workflows/Deploy%20to%20Production/badge.svg)](https://github.com/your-username/resume-editor/actions)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://hub.docker.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 🚀 生产环境特性

### 🔐 企业级安全
- JWT 令牌认证 + 刷新令牌机制
- BCrypt 密码哈希 + 盐值加密
- 多用户数据隔离，权限精确控制
- Docker 安全容器运行（非root用户）
- 生产环境密钥管理

### 🤖 AI 智能集成
- Dify AI 工作流深度集成
- 实时流式对话，低延迟响应
- 智能简历生成，专业内容优化
- 错误处理机制，服务稳定可靠

### 📄 专业PDF引擎
- 双PDF引擎：ReportLab + Playwright HTML渲染
- 智能单页压缩算法，自适应布局
- HarmonyOS Sans 专业中文字体
- 高质量矢量输出，打印就绪

### 🏗️ 云原生架构
- Docker 容器化 + Docker Compose 编排
- 前后端分离，RESTful API 设计
- 健康检查 + 自动重启机制
- 资源限制 + 性能监控
- 生产就绪的日志系统

## 📋 系统要求

### 最低配置
- **CPU**: 2核心 (x86_64)
- **内存**: 4GB RAM
- **存储**: 10GB 可用空间
- **系统**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+

### 推荐配置
- **CPU**: 4核心 (x86_64)
- **内存**: 8GB RAM
- **存储**: 20GB SSD
- **网络**: 稳定互联网连接

### 软件依赖
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.0+
- Curl

## 🚀 快速部署

### 方式一：一键从GitHub部署（推荐）

```bash
# 下载部署脚本
curl -fsSL https://raw.githubusercontent.com/your-username/resume-editor/main/deploy-from-github.sh -o deploy-from-github.sh
chmod +x deploy-from-github.sh

# 执行部署（需要root权限）
sudo ./deploy-from-github.sh -r https://github.com/your-username/resume-editor.git
```

### 方式二：本地部署

```bash
# 1. 克隆项目
git clone https://github.com/your-username/resume-editor.git
cd resume-editor

# 2. 配置环境
cp .env.production.example .env.production
# 编辑 .env.production 配置文件

# 3. 部署到生产环境
./deploy-production.sh
```

### 方式三：Docker Compose 部署

```bash
# 使用生产配置启动
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps
```

## 🌐 访问应用

部署完成后，通过以下地址访问：

- **前端界面**: http://your-server-ip:3000
- **后端API**: http://your-server-ip:8080
- **健康检查**: http://your-server-ip:8080/api/health

## 📊 生产环境管理

### 服务管理命令

```bash
# 启动生产服务
./deploy-production.sh

# 停止生产服务
./stop-production.sh

# 查看服务状态  
docker-compose -f docker-compose.prod.yml ps

# 查看实时日志
docker-compose -f docker-compose.prod.yml logs -f

# 重启特定服务
docker-compose -f docker-compose.prod.yml restart resume-backend
```

### 监控和维护

```bash
# 健康检查
curl -f http://your-server:8080/api/health

# 查看资源使用情况
docker stats

# 备份数据
sudo cp -r /var/lib/resume-editor/data /backup/$(date +%Y%m%d)

# 更新应用
git pull origin main
./deploy-production.sh
```

## 🏗️ 项目架构

```
resume-editor/
├── 🚀 部署文件
│   ├── deploy-production.sh        # 生产环境部署脚本
│   ├── deploy-from-github.sh       # GitHub 一键部署
│   ├── stop-production.sh          # 停止生产服务
│   ├── docker-compose.yml          # 开发环境配置
│   ├── docker-compose.prod.yml     # 生产环境配置
│   └── .env.production.example     # 生产环境配置模板
├── 🔧 持续集成
│   └── .github/workflows/
│       └── deploy.yml              # GitHub Actions 部署流水线
├── 🐍 后端服务
│   ├── backend/
│   │   ├── Dockerfile              # 生产就绪容器配置
│   │   ├── app.py                  # Flask 应用入口
│   │   ├── models.py               # 数据模型定义
│   │   ├── routes/                 # RESTful API 路由
│   │   ├── services/               # 业务逻辑服务
│   │   └── requirements.txt        # Python 依赖包
├── ⚛️ 前端应用
│   ├── frontend/
│   │   ├── Dockerfile              # 多阶段构建配置
│   │   ├── nginx.conf              # Nginx 生产配置
│   │   ├── src/                    # React 源码
│   │   └── package.json            # Node.js 依赖
├── 📚 文档系统
│   ├── README.md                   # 项目主文档
│   ├── CLAUDE.md                   # 开发指导文档
│   └── docs/                       # 详细文档
└── 🛠️ 工具脚本
    └── scripts/                    # 部署和管理脚本
```

## ⚙️ 环境配置

### 生产环境配置

生产环境使用 `.env.production` 文件管理配置：

```bash
# 安全配置
SECRET_KEY=生产环境强密钥
JWT_SECRET_KEY=JWT专用密钥  
DATABASE_URL=postgresql://user:password@db:5432/resume_editor

# 网络配置
HOST=0.0.0.0
PORT=8080
FRONTEND_URL=https://your-domain.com

# 性能配置
WORKERS=4
TIMEOUT=30
LOG_LEVEL=INFO
```

### 数据库支持

| 数据库 | 使用场景 | 配置示例 |
|--------|----------|----------|
| SQLite | 开发/测试 | `sqlite:///data/resume_editor.db` |
| PostgreSQL | 生产环境 | `postgresql://user:pass@db:5432/resume_editor` |

## 🤖 AI 工作流集成

### Dify 生产环境配置

```bash
# 生产环境配置
DIFY_API_KEY=your-production-dify-api-key
DIFY_API_URL=https://api.dify.ai/v1
DIFY_WORKFLOW_ID=your-workflow-id
```

### API 集成示例

```javascript
// 前端调用示例
const response = await fetch('/api/chatflow/conversation', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    query: "请帮我生成一份软件工程师简历",
    conversation_id: null
  })
});
```

## 📡 API 文档

### 🔐 认证接口

| 方法 | 端点 | 描述 | 认证要求 |
|------|------|------|----------|
| POST | `/api/auth/register` | 用户注册 | 无 |
| POST | `/api/auth/login` | 用户登录 | 无 |
| POST | `/api/auth/logout` | 用户登出 | Bearer Token |
| POST | `/api/auth/refresh` | 刷新令牌 | Refresh Token |
| GET | `/api/auth/me` | 获取用户信息 | Bearer Token |

### 📄 简历管理接口

| 方法 | 端点 | 描述 | 认证要求 |
|------|------|------|----------|
| GET | `/api/resumes` | 获取简历列表 | Bearer Token |
| POST | `/api/resumes` | 创建新简历 | Bearer Token |
| GET | `/api/resumes/{id}` | 获取简历详情 | Bearer Token + 权限检查 |
| PUT | `/api/resumes/{id}` | 更新简历内容 | Bearer Token + 所有者权限 |
| DELETE | `/api/resumes/{id}` | 删除简历 | Bearer Token + 所有者权限 |
| GET | `/api/resumes/{id}/pdf` | 导出PDF | Bearer Token + 权限检查 |
| GET | `/api/resumes/{id}/html` | HTML预览 | Bearer Token + 权限检查 |

### 🔌 外部集成接口

| 方法 | 端点 | 描述 | 用途 |
|------|------|------|------|
| POST | `/api/resumes/from-dify` | Dify工作流集成 | AI简历生成 |
| POST | `/api/chatflow/conversation` | 对话流接口 | 实时AI对话 |
| GET | `/api/health` | 健康检查 | 监控和负载均衡 |

## 🔧 故障排除

### 生产环境常见问题

| 问题 | 症状 | 解决方案 |
|------|------|----------|
| 服务无法启动 | 容器退出 | 检查日志：`docker-compose -f docker-compose.prod.yml logs` |
| 内存不足 | 服务频繁重启 | 增加服务器内存或调整资源限制 |
| 数据库连接失败 | 后端API错误 | 检查数据库服务状态和连接字符串 |
| PDF生成失败 | 导出功能异常 | 确认Playwright依赖和字体文件完整 |
| 端口被占用 | 服务启动失败 | 修改端口配置或停止冲突服务 |

### 日志监控

```bash
# 查看所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f resume-backend

# 查看系统资源使用
docker stats

# 查看磁盘使用情况
df -h /var/lib/resume-editor/
```

### 备份和恢复

```bash
# 创建完整备份
sudo ./scripts/backup.sh

# 恢复数据
sudo ./scripts/restore.sh /path/to/backup

# 数据库迁移
docker-compose -f docker-compose.prod.yml exec resume-backend python -c "
from app import db
db.create_all()
"
```

## 🔒 安全配置

### 生产环境安全检查清单

- [ ] 更改所有默认密钥和密码
- [ ] 启用HTTPS（使用SSL证书）
- [ ] 配置防火墙规则
- [ ] 设置非root用户运行容器
- [ ] 启用容器安全限制
- [ ] 定期更新依赖包
- [ ] 配置日志监控和告警

### SSL/HTTPS 配置

```bash
# 使用 Let's Encrypt 获取免费证书
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# 配置 nginx SSL
# 编辑 nginx/nginx.prod.conf 添加SSL配置
```

## 📊 性能优化

### 生产环境性能调优

```bash
# 调整数据库连接池
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# 优化容器资源分配
# 在 docker-compose.prod.yml 中调整 resources 配置

# 启用Redis缓存（可选）
REDIS_URL=redis://redis:6379/0
```

### 监控指标

```bash
# 应用性能监控
curl http://localhost:8080/api/health

# 数据库性能
docker-compose -f docker-compose.prod.yml exec resume-db pg_stat_activity

# 系统资源监控
htop
iotop
```

## 🚀 技术栈

### 生产环境技术栈

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 后端框架 | Flask | 2.3+ | Web API服务 |
| 数据库 | PostgreSQL | 15+ | 数据持久化 |
| 容器化 | Docker | 20.10+ | 应用容器化 |
| 编排工具 | Docker Compose | 2.0+ | 服务编排 |
| 前端框架 | React | 18+ | 用户界面 |
| 构建工具 | Vite | 5+ | 前端构建 |
| 反向代理 | Nginx | 1.20+ | 负载均衡 |
| PDF引擎 | Playwright | 1.40+ | PDF生成 |

## 📋 维护计划

### 定期维护任务

| 频率 | 任务 | 命令 |
|------|------|------|
| 每日 | 备份数据 | `./scripts/daily-backup.sh` |
| 每周 | 清理日志 | `docker system prune -f` |
| 每月 | 更新依赖 | `./scripts/update-dependencies.sh` |
| 每季度 | 安全审计 | `./scripts/security-audit.sh` |

### 更新流程

```bash
# 1. 备份当前版本
sudo ./stop-production.sh
sudo cp -r /var/lib/resume-editor /backup/$(date +%Y%m%d)

# 2. 更新代码
git pull origin main

# 3. 重新部署
sudo ./deploy-production.sh

# 4. 验证部署
curl -f http://localhost:8080/api/health
```

## 📞 生产支持

### 紧急联系

- **生产环境问题**: 通过监控系统告警
- **安全问题**: 立即联系系统管理员
- **数据恢复**: 使用自动备份系统

### 文档资源

- **部署文档**: [CLAUDE.md](CLAUDE.md)
- **API文档**: `/docs/api/`
- **变更日志**: [CHANGELOG.md](docs/CHANGELOG.md)
- **故障手册**: [docs/troubleshooting.md](docs/troubleshooting.md)

## 📄 许可证

本项目采用 MIT 许可证。详情请查看 [LICENSE](LICENSE) 文件。

---

<div align="center">

**🏢 企业级简历编辑系统**

专为生产环境设计 | 支持大规模部署 | 7x24小时稳定运行

[部署指南](deploy-from-github.sh) • [API文档](#-api-文档) • [故障排除](#-故障排除) • [技术支持](#-生产支持)

</div>