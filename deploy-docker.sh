#!/bin/bash

# 浩流简历编辑器 - 一键 Docker 部署脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 工具函数
print_step() {
    echo -e "${BLUE}==== $1 ====${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# 检查 Docker 环境
check_docker() {
    print_step "检查 Docker 环境"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        echo "安装指南:"
        echo "macOS: https://docs.docker.com/docker-for-mac/install/"
        echo "Windows: https://docs.docker.com/docker-for-windows/install/"
        echo "Linux: https://docs.docker.com/engine/install/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null 2>&1; then
        print_error "Docker Compose 未安装或不可用"
        exit 1
    fi
    
    # 检查 Docker 是否运行
    if ! docker info &> /dev/null; then
        print_error "Docker 服务未运行，请启动 Docker"
        exit 1
    fi
    
    print_success "Docker 环境检查通过"
}

# 配置环境变量
setup_docker_env() {
    print_step "配置 Docker 环境变量"
    
    DOCKER_ENV_FILE=".env.docker"
    
    if [ -f "$DOCKER_ENV_FILE" ]; then
        echo "Docker 环境配置文件已存在，是否要重新配置？(y/n)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_success "使用现有的 Docker 环境变量配置"
            return
        fi
    fi
    
    # 获取用户输入
    read -p "前端端口 (默认: 3000): " frontend_port
    frontend_port=${frontend_port:-3000}
    
    read -p "后端端口 (默认: 8080): " backend_port
    backend_port=${backend_port:-8080}
    
    # 询问是否配置内网穿透
    echo "是否需要配置内网穿透域名？(y/n)"
    read -r tunnel_response
    if [[ "$tunnel_response" =~ ^[Yy]$ ]]; then
        read -p "请输入外部访问域名 (例如: your-domain.com): " external_domain
        FRONTEND_URL="https://${external_domain}"
        API_URL="https://${external_domain}/api"
    else
        FRONTEND_URL="http://localhost:${frontend_port}"
        API_URL="http://localhost:${backend_port}"
    fi
    
    # 询问数据库配置
    echo "请选择数据库类型："
    echo "1) SQLite (容器内文件，简单部署)"
    echo "2) PostgreSQL (Docker 容器，推荐生产环境)"
    read -r db_choice
    
    if [ "$db_choice" = "2" ]; then
        read -p "PostgreSQL 数据库名 (默认: resume_editor): " postgres_db
        postgres_db=${postgres_db:-resume_editor}
        read -p "PostgreSQL 用户名 (默认: postgres): " postgres_user  
        postgres_user=${postgres_user:-postgres}
        read -s -p "PostgreSQL 密码 (默认: resume123): " postgres_password
        postgres_password=${postgres_password:-resume123}
        echo
        
        DATABASE_URL="postgresql://${postgres_user}:${postgres_password}@postgres:5432/${postgres_db}"
        USE_POSTGRES=true
    else
        DATABASE_URL="sqlite:///resume_editor.db"
        USE_POSTGRES=false
    fi
    
    # 生成密钥
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)
    JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || openssl rand -base64 32)
    
    # 写入环境变量文件
    cat > "$DOCKER_ENV_FILE" << EOF
# 端口配置
FRONTEND_PORT=${frontend_port}
BACKEND_PORT=${backend_port}

# 应用配置
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
FRONTEND_URL=${FRONTEND_URL}

# 数据库配置
DATABASE_URL=${DATABASE_URL}
USE_POSTGRES=${USE_POSTGRES}

# PostgreSQL 配置 (仅在使用 PostgreSQL 时需要)
POSTGRES_DB=${postgres_db}
POSTGRES_USER=${postgres_user}
POSTGRES_PASSWORD=${postgres_password}

# API 配置
VITE_API_URL=${API_URL}
EOF
    
    print_success "Docker 环境变量配置完成"
}

# 创建 Docker Compose 文件
create_docker_compose() {
    print_step "创建 Docker Compose 配置"
    
    # 读取环境变量
    source .env.docker
    
    if [ "$USE_POSTGRES" = "true" ]; then
        # 使用 PostgreSQL 的 Docker Compose
        cat > docker-compose.override.yml << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: \${POSTGRES_DB}
      POSTGRES_USER: \${POSTGRES_USER}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \${POSTGRES_USER} -d \${POSTGRES_DB}"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  postgres_data:
EOF
    else
        # 移除 PostgreSQL 覆盖文件
        rm -f docker-compose.override.yml
    fi
    
    print_success "Docker Compose 配置创建完成"
}

# 构建和启动服务
deploy_services() {
    print_step "构建和启动 Docker 服务"
    
    # 停止现有服务
    docker-compose --env-file .env.docker down 2>/dev/null || true
    
    # 构建镜像
    print_step "构建 Docker 镜像..."
    docker-compose --env-file .env.docker build --no-cache
    
    # 启动服务
    print_step "启动服务..."
    docker-compose --env-file .env.docker up -d
    
    # 等待服务启动
    echo "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    if docker-compose --env-file .env.docker ps | grep -q "Up"; then
        print_success "服务启动成功！"
    else
        print_error "服务启动失败，请检查日志"
        docker-compose --env-file .env.docker logs
        exit 1
    fi
}

# 显示访问信息
show_access_info() {
    source .env.docker
    
    echo -e "${GREEN}"
    echo "=========================================="
    echo "      Docker 部署完成！"
    echo "=========================================="
    echo -e "${NC}"
    
    echo "服务访问地址："
    echo "• 前端应用: http://localhost:${FRONTEND_PORT}"
    echo "• 后端 API: http://localhost:${BACKEND_PORT}"
    
    if [ "$USE_POSTGRES" = "true" ]; then
        echo "• PostgreSQL: localhost:5432"
    fi
    
    echo ""
    echo "开发模式测试账户："
    echo "• 演示用户: demo@gmail.com / demo123"
    echo "• 管理员: admin@gmail.com / admin123"
    
    echo ""
    echo "常用命令："
    echo "• 查看服务状态: docker-compose --env-file .env.docker ps"
    echo "• 查看日志: docker-compose --env-file .env.docker logs -f"
    echo "• 停止服务: docker-compose --env-file .env.docker down"
    echo "• 重启服务: docker-compose --env-file .env.docker restart"
    
    if [ -n "$external_domain" ]; then
        echo ""
        echo "外部访问地址："
        echo "• https://${external_domain}"
        print_warning "请确保域名已正确配置并指向此服务器"
    fi
}

# 创建管理脚本
create_management_scripts() {
    print_step "创建 Docker 管理脚本"
    
    # 启动脚本
    cat > docker-start.sh << 'EOF'
#!/bin/bash
echo "启动 Docker 服务..."
docker-compose --env-file .env.docker up -d
echo "服务已启动，使用 docker-logs.sh 查看日志"
EOF
    
    # 停止脚本
    cat > docker-stop.sh << 'EOF'
#!/bin/bash
echo "停止 Docker 服务..."
docker-compose --env-file .env.docker down
echo "服务已停止"
EOF
    
    # 日志脚本
    cat > docker-logs.sh << 'EOF'
#!/bin/bash
echo "查看 Docker 服务日志 (Ctrl+C 退出)..."
docker-compose --env-file .env.docker logs -f
EOF
    
    # 重启脚本
    cat > docker-restart.sh << 'EOF'
#!/bin/bash
echo "重启 Docker 服务..."
docker-compose --env-file .env.docker restart
echo "服务已重启"
EOF
    
    chmod +x docker-start.sh docker-stop.sh docker-logs.sh docker-restart.sh
    
    print_success "Docker 管理脚本创建完成"
}

# 主函数
main() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "    浩流简历编辑器 - Docker 一键部署"
    echo "=========================================="
    echo -e "${NC}"
    
    check_docker
    setup_docker_env
    create_docker_compose
    create_management_scripts
    deploy_services
    show_access_info
}

# 运行主函数
main