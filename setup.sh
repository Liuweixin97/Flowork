#!/bin/bash

# 浩流简历编辑器 - 初始化部署脚本
# 该脚本将帮助您配置环境变量并部署项目

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

# 检查系统依赖
check_dependencies() {
    print_step "检查系统依赖"
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 未安装，请先安装 Python 3.8+"
        exit 1
    fi
    print_success "Python 3 已安装: $(python3 --version)"
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js 未安装，请先安装 Node.js 16+"
        exit 1
    fi
    print_success "Node.js 已安装: $(node --version)"
    
    # 检查 npm
    if ! command -v npm &> /dev/null; then
        print_error "npm 未安装，请先安装 npm"
        exit 1
    fi
    print_success "npm 已安装: $(npm --version)"
    
    # 检查 Docker (可选)
    if command -v docker &> /dev/null; then
        print_success "Docker 已安装: $(docker --version)"
        DOCKER_AVAILABLE=true
    else
        print_warning "Docker 未安装，跳过 Docker 部署选项"
        DOCKER_AVAILABLE=false
    fi
}

# 生成随机密钥
generate_secret_key() {
    python3 -c "import secrets; print(secrets.token_urlsafe(32))"
}

# 配置后端环境变量
setup_backend_env() {
    print_step "配置后端环境变量"
    
    BACKEND_ENV_FILE="backend/.env"
    
    if [ -f "$BACKEND_ENV_FILE" ]; then
        echo "后端环境配置文件已存在，是否要重新配置？(y/n)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_success "跳过后端环境变量配置"
            return
        fi
    fi
    
    echo "请选择数据库类型："
    echo "1) SQLite (开发环境，推荐)"
    echo "2) PostgreSQL (生产环境)"
    read -r db_choice
    
    if [ "$db_choice" = "2" ]; then
        echo "请输入 PostgreSQL 连接信息："
        read -p "数据库主机 (默认: localhost): " db_host
        db_host=${db_host:-localhost}
        read -p "数据库端口 (默认: 5432): " db_port  
        db_port=${db_port:-5432}
        read -p "数据库名称: " db_name
        read -p "数据库用户名: " db_user
        read -s -p "数据库密码: " db_password
        echo
        DATABASE_URL="postgresql://${db_user}:${db_password}@${db_host}:${db_port}/${db_name}"
    else
        DATABASE_URL="sqlite:///resume_editor.db"
    fi
    
    read -p "后端端口 (默认: 8080): " backend_port
    backend_port=${backend_port:-8080}
    
    read -p "前端地址 (默认: http://localhost:3000): " frontend_url
    frontend_url=${frontend_url:-http://localhost:3000}
    
    # 询问是否配置内网穿透
    echo "是否需要配置内网穿透？(y/n)"
    read -r tunnel_response
    if [[ "$tunnel_response" =~ ^[Yy]$ ]]; then
        echo "请选择内网穿透工具："
        echo "1) 花生壳"
        echo "2) ngrok"
        echo "3) 其他"
        read -r tunnel_choice
        
        case $tunnel_choice in
            1)
                read -p "请输入花生壳域名 (例如: abc123.vicp.fun): " tunnel_domain
                frontend_url="https://${tunnel_domain}"
                ;;
            2)
                read -p "请输入 ngrok 域名 (例如: abc123.ngrok.io): " tunnel_domain
                frontend_url="https://${tunnel_domain}"
                ;;
            3)
                read -p "请输入自定义域名: " tunnel_domain
                frontend_url="https://${tunnel_domain}"
                ;;
        esac
    fi
    
    # 生成密钥
    SECRET_KEY=$(generate_secret_key)
    JWT_SECRET_KEY=$(generate_secret_key)
    
    # 写入环境变量
    cat > "$BACKEND_ENV_FILE" << EOF
# 应用配置
SECRET_KEY=${SECRET_KEY}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
HOST=0.0.0.0
PORT=${backend_port}

# 数据库配置
DATABASE_URL=${DATABASE_URL}

# CORS 配置
FRONTEND_URL=${frontend_url}

# 可选：Dify 集成配置
# DIFY_API_KEY=your_dify_api_key_here
# DIFY_API_URL=https://api.dify.ai/v1
EOF
    
    print_success "后端环境变量配置完成"
}

# 配置前端环境变量
setup_frontend_env() {
    print_step "配置前端环境变量"
    
    FRONTEND_ENV_FILE="frontend/.env"
    
    if [ -f "$FRONTEND_ENV_FILE" ]; then
        echo "前端环境配置文件已存在，是否要重新配置？(y/n)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            print_success "跳过前端环境变量配置"
            return
        fi
    fi
    
    read -p "后端 API 地址 (默认: http://localhost:8080): " api_url
    api_url=${api_url:-http://localhost:8080}
    
    cat > "$FRONTEND_ENV_FILE" << EOF
# API 配置
VITE_API_URL=${api_url}
EOF
    
    print_success "前端环境变量配置完成"
}

# 安装后端依赖
install_backend_deps() {
    print_step "安装后端依赖"
    
    cd backend
    
    # 检查是否已存在虚拟环境
    if [ ! -d "venv" ]; then
        print_step "创建 Python 虚拟环境"
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    
    cd ..
    print_success "后端依赖安装完成"
}

# 安装前端依赖
install_frontend_deps() {
    print_step "安装前端依赖"
    
    cd frontend
    npm install
    cd ..
    
    print_success "前端依赖安装完成"
}

# 配置 Dify 集成（可选）
setup_dify_integration() {
    print_step "配置 Dify 集成（可选）"
    
    echo "是否需要配置 Dify AI 工作流集成？(y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_success "跳过 Dify 集成配置"
        return
    fi
    
    read -p "请输入 Dify API Key: " dify_api_key
    read -p "请输入 Dify API URL (默认: https://api.dify.ai/v1): " dify_api_url
    dify_api_url=${dify_api_url:-https://api.dify.ai/v1}
    
    # 更新后端环境变量
    echo >> backend/.env
    echo "# Dify 集成配置" >> backend/.env
    echo "DIFY_API_KEY=${dify_api_key}" >> backend/.env
    echo "DIFY_API_URL=${dify_api_url}" >> backend/.env
    
    print_success "Dify 集成配置完成"
    print_warning "请确保在 Dify 工作流中配置 HTTP 节点指向: http://localhost:8080/api/resumes/from-dify"
}

# 创建启动脚本
create_start_script() {
    print_step "创建启动脚本"
    
    cat > start.sh << 'EOF'
#!/bin/bash

# 启动浩流简历编辑器

echo "启动后端服务..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid
cd ..

echo "启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo $FRONTEND_PID > frontend.pid
cd ..

echo "服务启动完成！"
echo "前端地址: http://localhost:3000"
echo "后端地址: http://localhost:8080"
echo ""
echo "使用以下命令停止服务："
echo "./stop.sh"
EOF

    cat > stop.sh << 'EOF'
#!/bin/bash

# 停止浩流简历编辑器

echo "停止服务..."

if [ -f backend/backend.pid ]; then
    kill $(cat backend/backend.pid) 2>/dev/null && rm backend/backend.pid
    echo "后端服务已停止"
fi

if [ -f frontend/frontend.pid ]; then
    kill $(cat frontend/frontend.pid) 2>/dev/null && rm frontend/frontend.pid
    echo "前端服务已停止"
fi

echo "所有服务已停止"
EOF

    chmod +x start.sh stop.sh
    print_success "启动脚本创建完成"
}

# 主函数
main() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "     浩流简历编辑器 - 初始化部署脚本"
    echo "=========================================="
    echo -e "${NC}"
    
    check_dependencies
    setup_backend_env
    setup_frontend_env
    install_backend_deps
    install_frontend_deps
    setup_dify_integration
    create_start_script
    
    echo -e "${GREEN}"
    echo "=========================================="
    echo "         部署配置完成！"
    echo "=========================================="
    echo -e "${NC}"
    
    echo "接下来您可以："
    echo "1. 运行 ./start.sh 启动服务"
    echo "2. 访问 http://localhost:3000 使用应用"
    echo "3. 运行 ./stop.sh 停止服务"
    echo ""
    echo "如需 Docker 部署，请运行："
    echo "./deploy-docker.sh"
    echo ""
    echo "开发模式测试账户："
    echo "• 演示用户: demo@gmail.com / demo123"
    echo "• 管理员: admin@gmail.com / admin123"
}

# 运行主函数
main