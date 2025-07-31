# 依赖和环境要求文档

本文档详细说明了浩流简历编辑器项目在不同环境下的所有依赖和要求。

## 📋 系统要求

### 🖥️ 硬件要求

#### 开发环境
- **CPU**: 2核心以上 (x86_64/ARM64)
- **内存**: 4GB RAM (推荐 8GB)
- **存储**: 10GB 可用空间
- **网络**: 稳定互联网连接

#### 生产环境
- **CPU**: 4核心以上 (x86_64)
- **内存**: 8GB RAM (推荐 16GB)
- **存储**: 50GB SSD (推荐 100GB)
- **网络**: 稳定互联网连接 + 公网IP

### 🐧 操作系统支持

#### 完全支持
- Ubuntu 20.04 LTS / 22.04 LTS
- Debian 11 / 12
- CentOS 8+ / Rocky Linux 9+
- Red Hat Enterprise Linux 8+

#### 部分支持 (开发环境)
- macOS 12+ (Intel/Apple Silicon)
- Windows 10/11 (WSL2 推荐)

## 🐍 后端依赖

### Python 环境
```bash
# Python 版本要求
Python >= 3.8, < 3.12 (推荐 3.11)

# 虚拟环境管理
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
```

### 核心依赖包
```txt
# Web 框架和扩展
Flask>=2.3.0,<3.0.0              # Web 应用框架
Flask-SQLAlchemy>=3.0.0,<4.0.0   # ORM 数据库操作
Flask-CORS>=4.0.0,<5.0.0         # 跨域请求支持
Flask-Migrate>=4.0.0,<5.0.0      # 数据库迁移
Flask-JWT-Extended>=4.5.0,<5.0.0 # JWT 认证
Flask-Bcrypt>=1.0.0,<2.0.0       # 密码哈希

# 数据库驱动
psycopg2-binary>=2.9.0,<3.0.0    # PostgreSQL 驱动 (生产环境)
# sqlite3 内置于 Python

# PDF 生成和文档处理
reportlab>=4.0.0,<5.0.0          # PDF 生成引擎
playwright>=1.40.0,<2.0.0        # 浏览器自动化 (HTML->PDF)
markdown>=3.4.0,<4.0.0           # Markdown 解析

# 工具库
python-dotenv>=1.0.0,<2.0.0      # 环境变量管理
requests>=2.31.0,<3.0.0          # HTTP 客户端
email-validator>=2.0.0,<3.0.0    # 邮箱验证

# 开发和测试 (可选)
pytest>=7.0.0,<8.0.0             # 测试框架
pytest-flask>=1.2.0,<2.0.0       # Flask 测试支持
black>=23.0.0,<24.0.0             # 代码格式化
flake8>=6.0.0,<7.0.0              # 代码检查
```

### 系统级依赖
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    python3 python3-pip python3-venv \
    curl wget git \
    postgresql-client \
    libpq-dev \
    libnss3 libnspr4 libdbus-1-3 \
    libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxss1 libgtk-3-0 \
    libgbm-dev libasound2

# CentOS/RHEL/Rocky Linux
sudo dnf install -y \
    python3 python3-pip \
    curl wget git \
    postgresql \
    postgresql-devel \
    nss nspr dbus-libs \
    atk atk-bridge2 \
    cups-libs libdrm libXScrnSaver gtk3 \
    libgbm alsa-lib
```

## ⚛️ 前端依赖

### Node.js 环境
```bash
# Node.js 版本要求
Node.js >= 16.0.0, < 20.0.0 (推荐 18.x LTS)
npm >= 8.0.0 或 yarn >= 1.22.0

# 安装 Node.js (Ubuntu)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 验证安装
node --version
npm --version
```

### 核心依赖包
```json
{
  "dependencies": {
    "react": "^18.2.0",                    // React 框架
    "react-dom": "^18.2.0",                // React DOM 渲染
    "react-router-dom": "^6.8.0",          // 路由管理
    "axios": "^1.6.0",                     // HTTP 客户端
    "lucide-react": "^0.294.0",            // 图标库
    "react-markdown": "^9.0.1",            // Markdown 渲染
    "react-hot-toast": "^2.4.1"            // 通知组件
  },
  "devDependencies": {
    "@types/react": "^18.2.43",            // React 类型定义
    "@types/react-dom": "^18.2.17",        // React DOM 类型定义
    "@vitejs/plugin-react": "^4.2.1",      // Vite React 插件
    "autoprefixer": "^10.4.16",            // CSS 自动前缀
    "eslint": "^8.55.0",                   // 代码检查
    "eslint-plugin-react": "^7.33.2",      // React ESLint 插件
    "eslint-plugin-react-hooks": "^4.6.0",     // React Hooks ESLint
    "eslint-plugin-react-refresh": "^0.4.5",   // React 刷新 ESLint
    "postcss": "^8.4.32",                  // CSS 后处理器
    "tailwindcss": "^3.3.6",               // CSS 框架
    "vite": "^5.0.8"                       // 构建工具
  }
}
```

## 🐳 容器化依赖

### Docker 环境
```bash
# Docker 版本要求
Docker >= 20.10.0 (推荐最新稳定版)
Docker Compose >= 2.0.0

# Ubuntu 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 基础镜像
```dockerfile
# 后端基础镜像
FROM python:3.11-slim

# 前端基础镜像  
FROM node:18-alpine as build
FROM nginx:alpine as production
```

## 🗄️ 数据库依赖

### 开发环境 (SQLite)
```bash
# SQLite3 (通常系统自带)
sqlite3 --version

# 如果没有安装
# Ubuntu/Debian
sudo apt-get install sqlite3

# CentOS/RHEL
sudo dnf install sqlite
```

### 生产环境 (PostgreSQL)
```bash
# PostgreSQL 版本要求
PostgreSQL >= 12.0, < 16.0 (推荐 15.x)

# Ubuntu 安装
sudo apt-get install postgresql postgresql-contrib

# CentOS/RHEL 安装
sudo dnf install postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql

# 创建数据库和用户
sudo -u postgres psql
postgres=# CREATE DATABASE resume_editor;
postgres=# CREATE USER resume_user WITH PASSWORD 'secure_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE resume_editor TO resume_user;
postgres=# \q
```

## 🌐 网络和服务依赖

### 反向代理 (Nginx)
```bash
# Nginx 版本要求 (生产环境推荐)
Nginx >= 1.18.0

# Ubuntu 安装
sudo apt-get install nginx

# 基本配置
sudo systemctl enable nginx
sudo systemctl start nginx
```

### SSL 证书 (生产环境)
```bash
# Let's Encrypt (免费证书)
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com
```

## 🔧 开发工具依赖

### Git 版本控制
```bash
# Git 版本要求
Git >= 2.25.0

# 安装
# Ubuntu/Debian
sudo apt-get install git

# CentOS/RHEL  
sudo dnf install git

# 配置
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 代码编辑器推荐
```bash
# Visual Studio Code (推荐)
# 推荐扩展：
- Python
- JavaScript/TypeScript 
- Docker
- GitLens
- Prettier
- ESLint

# 其他支持的编辑器
- PyCharm Professional
- WebStorm  
- Vim/Neovim (配置相应插件)
```

## 📦 AI 集成依赖

### Dify AI 平台
```bash
# API 访问要求
- Dify API Key (生产环境)
- 稳定的网络连接
- HTTPS 支持 (生产环境)

# 环境变量配置
DIFY_API_KEY=your_api_key
DIFY_API_URL=https://api.dify.ai/v1
DIFY_WORKFLOW_ID=your_workflow_id
```

## 🚀 部署环境要求

### 云平台支持

#### AWS
```bash
# 推荐服务
- EC2 (t3.medium 或更高)
- RDS PostgreSQL
- Application Load Balancer
- CloudFront (CDN)
- Route 53 (DNS)
```

#### 阿里云
```bash
# 推荐服务  
- ECS (ecs.c6.large 或更高)
- RDS PostgreSQL
- SLB 负载均衡
- CDN 
- 云解析 DNS
```

#### 自建服务器
```bash
# 最低配置
- 4核 CPU
- 8GB RAM  
- 50GB SSD
- 100Mbps 网络
- 固定公网IP
```

## 📝 环境变量清单

### 必需环境变量
```bash
# 应用安全
SECRET_KEY=                 # 应用密钥 (必须修改)
JWT_SECRET_KEY=            # JWT 密钥 (必须修改)

# 数据库
DATABASE_URL=              # 数据库连接字符串

# 网络配置
HOST=0.0.0.0              # 绑定地址
PORT=8080                 # 后端端口
FRONTEND_URL=             # 前端地址
```

### 可选环境变量
```bash
# AI 集成
DIFY_API_KEY=             # Dify API 密钥
DIFY_API_URL=             # Dify API 地址
DIFY_WORKFLOW_ID=         # 工作流 ID

# 性能配置
WORKERS=4                 # 工作进程数
TIMEOUT=30               # 请求超时时间
LOG_LEVEL=INFO           # 日志级别

# 邮件配置 (可选)
MAIL_SERVER=             # SMTP 服务器
MAIL_PORT=587            # SMTP 端口
MAIL_USERNAME=           # 邮箱用户名
MAIL_PASSWORD=           # 邮箱密码
```

## 🔍 依赖检查脚本

创建 `check-dependencies.sh` 脚本来验证环境：

```bash
#!/bin/bash

echo "=== 浩流简历编辑器 - 依赖检查 ==="

# 检查 Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ $PYTHON_VERSION"
else
    echo "❌ Python3 未安装"
fi

# 检查 Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION"
else
    echo "❌ Node.js 未安装"
fi

# 检查 Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "✅ $DOCKER_VERSION"
else
    echo "❌ Docker 未安装"
fi

# 检查 Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo "✅ $COMPOSE_VERSION"
else
    echo "❌ Docker Compose 未安装"
fi

# 检查 Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo "✅ $GIT_VERSION"
else
    echo "❌ Git 未安装"
fi

echo "=== 检查完成 ==="
```

## 🆘 故障排除

### 常见依赖问题

#### Python 依赖问题
```bash
# 问题：pip 安装失败
# 解决：升级 pip
python3 -m pip install --upgrade pip

# 问题：Playwright 安装失败
# 解决：手动安装浏览器
playwright install chromium
```

#### Node.js 依赖问题
```bash
# 问题：npm 安装慢
# 解决：使用国内镜像
npm config set registry https://registry.npmmirror.com

# 问题：权限错误
# 解决：使用 npm ci
npm ci --only=production
```

#### Docker 依赖问题
```bash
# 问题：权限不足
# 解决：添加用户到 docker 组
sudo usermod -aG docker $USER
newgrp docker

# 问题：镜像拉取失败
# 解决：配置镜像加速
# 编辑 /etc/docker/daemon.json
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com"
  ]
}
```

---

## 📞 支持和帮助

如果在依赖安装过程中遇到问题：

1. 查看项目 [README.md](README.md) 
2. 检查 [故障排除文档](docs/troubleshooting.md)
3. 提交 [GitHub Issue](https://github.com/your-repo/issues)
4. 参考 [部署脚本](deploy-from-github.sh) 自动安装