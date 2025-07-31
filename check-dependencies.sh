#!/bin/bash

# 浩流简历编辑器 - 依赖环境检查脚本
# Resume Editor Dependencies Check Script

set -e

# 颜色输出函数
print_info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[✅]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[⚠️]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[❌]\033[0m $1"
}

print_header() {
    echo "=================================================="
    echo "🔍 浩流简历编辑器 - 依赖环境检查"
    echo "   Resume Editor Dependencies Check"
    echo "=================================================="
    echo
}

# 检查系统信息
check_system_info() {
    print_info "检查系统信息..."
    echo "操作系统: $(uname -s)"
    echo "架构: $(uname -m)"
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "发行版: $NAME $VERSION"
    fi
    echo "内核版本: $(uname -r)"
    echo
}

# 检查 Python 环境
check_python() {
    print_info "检查 Python 环境..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1)
        PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
        PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
        
        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ] && [ "$PYTHON_MINOR" -lt 12 ]; then
            print_success "$PYTHON_VERSION"
        else
            print_warning "$PYTHON_VERSION (推荐 Python 3.8-3.11)"
        fi
        
        # 检查 pip
        if command -v pip3 &> /dev/null; then
            PIP_VERSION=$(pip3 --version)
            print_success "pip3 已安装"
        else
            print_error "pip3 未安装"
        fi
        
        # 检查虚拟环境
        if python3 -c "import venv" &> /dev/null; then
            print_success "venv 模块可用"
        else
            print_error "venv 模块不可用"
        fi
    else
        print_error "Python3 未安装"
    fi
    echo
}

# 检查 Node.js 环境
check_nodejs() {
    print_info "检查 Node.js 环境..."
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        NODE_MAJOR=$(node --version | cut -d'.' -f1 | sed 's/v//')
        
        if [ "$NODE_MAJOR" -ge 16 ]; then
            print_success "Node.js $NODE_VERSION"
        else
            print_warning "Node.js $NODE_VERSION (推荐 16.0.0+)"
        fi
        
        # 检查 npm
        if command -v npm &> /dev/null; then
            NPM_VERSION=$(npm --version)
            print_success "npm $NPM_VERSION"
        else
            print_error "npm 未安装"
        fi
    else
        print_error "Node.js 未安装"
    fi
    echo
}

# 检查 Docker 环境
check_docker() {
    print_info "检查 Docker 环境..."
    
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | sed 's/,//')
        print_success "Docker $DOCKER_VERSION"
        
        # 检查 Docker 服务状态
        if docker info &> /dev/null; then
            print_success "Docker 服务运行正常"
        else
            print_warning "Docker 服务未运行或权限不足"
        fi
    else
        print_error "Docker 未安装"
    fi
    
    # 检查 Docker Compose
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f4 | sed 's/,//')
        print_success "Docker Compose $COMPOSE_VERSION"
    else
        print_error "Docker Compose 未安装"
    fi
    echo
}

# 检查 Git 环境
check_git() {
    print_info "检查 Git 环境..."
    
    if command -v git &> /dev/null; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        print_success "Git $GIT_VERSION"
        
        # 检查 Git 配置
        if git config --get user.name &> /dev/null && git config --get user.email &> /dev/null; then
            print_success "Git 用户配置完整"
        else
            print_warning "Git 用户配置不完整"
        fi
    else
        print_error "Git 未安装"
    fi
    echo
}

# 检查数据库环境
check_database() {
    print_info "检查数据库环境..."
    
    # 检查 SQLite3
    if command -v sqlite3 &> /dev/null; then
        SQLITE_VERSION=$(sqlite3 --version | cut -d' ' -f1)
        print_success "SQLite3 $SQLITE_VERSION"
    else
        print_warning "SQLite3 未安装 (开发环境可能需要)"
    fi
    
    # 检查 PostgreSQL 客户端
    if command -v psql &> /dev/null; then
        PSQL_VERSION=$(psql --version | cut -d' ' -f3)
        print_success "PostgreSQL 客户端 $PSQL_VERSION"
    else
        print_warning "PostgreSQL 客户端未安装 (生产环境需要)"
    fi
    echo
}

# 检查网络工具
check_network_tools() {
    print_info "检查网络工具..."
    
    if command -v curl &> /dev/null; then
        print_success "curl 已安装"
    else
        print_error "curl 未安装"
    fi
    
    if command -v wget &> /dev/null; then
        print_success "wget 已安装"
    else
        print_warning "wget 未安装"
    fi
    echo
}

# 检查系统资源
check_system_resources() {
    print_info "检查系统资源..."
    
    # 检查内存
    if command -v free &> /dev/null; then
        TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f MB", $2}')
        AVAILABLE_MEM=$(free -m | awk 'NR==2{printf "%.0f MB", $7}')
        echo "总内存: $TOTAL_MEM"
        echo "可用内存: $AVAILABLE_MEM"
        
        TOTAL_MEM_GB=$(free -m | awk 'NR==2{printf "%.1f", $2/1024}')
        if (( $(echo "$TOTAL_MEM_GB >= 4.0" | bc -l) )); then
            print_success "内存充足 (${TOTAL_MEM_GB}GB)"
        else
            print_warning "内存不足 (${TOTAL_MEM_GB}GB, 推荐4GB+)"
        fi
    fi
    
    # 检查磁盘空间
    if command -v df &> /dev/null; then
        DISK_USAGE=$(df -h . | awk 'NR==2{print $4}')
        print_success "可用磁盘空间: $DISK_USAGE"
    fi
    echo
}

# 检查项目特定依赖
check_project_dependencies() {
    print_info "检查项目特定依赖..."
    
    # 检查 Python 包 (如果在虚拟环境中)
    if [ -d "backend" ] && [ -f "backend/requirements.txt" ]; then
        print_info "检查 Python 后端依赖..."
        if [ -f "backend/venv/bin/activate" ]; then
            source backend/venv/bin/activate
            pip check &> /dev/null && print_success "Python 依赖完整" || print_warning "Python 依赖可能有问题"
            deactivate
        else
            print_warning "后端虚拟环境未找到"
        fi
    fi
    
    # 检查 Node.js 包
    if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
        print_info "检查 Node.js 前端依赖..."
        if [ -d "frontend/node_modules" ]; then
            print_success "Node.js 依赖已安装"
        else
            print_warning "Node.js 依赖未安装，运行 'cd frontend && npm install'"
        fi
    fi
    echo
}

# 提供安装建议
provide_installation_suggestions() {
    print_info "📋 安装建议..."
    
    echo "如果缺少依赖，可以运行以下命令："
    echo ""
    echo "🐧 Ubuntu/Debian:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install -y python3 python3-pip python3-venv nodejs npm git curl sqlite3"
    echo ""
    echo "🎩 CentOS/RHEL/Rocky Linux:"
    echo "  sudo dnf install -y python3 python3-pip nodejs npm git curl sqlite"
    echo ""
    echo "🐳 Docker:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    echo ""
    echo "📦 项目依赖:"
    echo "  ./setup.sh  # 自动安装和配置"
    echo "  或手动运行："
    echo "  cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    echo "  cd frontend && npm install"
    echo
}

# 生成总结报告
generate_summary() {
    print_info "📊 检查总结..."
    echo "依赖检查完成！请确保所有必需的依赖都已正确安装。"
    echo ""
    echo "🔗 有用的链接："
    echo "  项目文档: README.md"
    echo "  依赖详情: DEPENDENCIES.md"
    echo "  部署指南: CLAUDE.md"
    echo "  快速部署: ./deploy-production.sh"
    echo ""
    echo "如需帮助，请查看项目文档或提交 GitHub Issue。"
}

# 主函数
main() {
    print_header
    
    check_system_info
    check_python
    check_nodejs
    check_docker
    check_git
    check_database
    check_network_tools
    check_system_resources
    check_project_dependencies
    
    provide_installation_suggestions
    generate_summary
    
    echo "=================================================="
    echo "✨ 依赖检查完成"
    echo "=================================================="
}

# 运行主函数
main "$@"