#!/bin/bash

# 从GitHub部署脚本
# Deploy from GitHub Script for Resume Editor

set -e

# 颜色输出函数
print_info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

# 配置变量
REPO_URL="https://github.com/YOUR_USERNAME/resume-editor.git"  # 请替换为实际的GitHub仓库地址
DEPLOY_DIR="/opt/resume-editor"
BRANCH="main"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--repo)
            REPO_URL="$2"
            shift 2
            ;;
        -b|--branch)
            BRANCH="$2"
            shift 2
            ;;
        -d|--dir)
            DEPLOY_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "使用方法: $0 [选项]"
            echo "选项:"
            echo "  -r, --repo    GitHub仓库地址"
            echo "  -b, --branch  分支名称 (默认: main)"
            echo "  -d, --dir     部署目录 (默认: /opt/resume-editor)"
            echo "  -h, --help    显示帮助信息"
            exit 0
            ;;
        *)
            print_error "未知参数: $1"
            exit 1
            ;;
    esac
done

# 检查权限
check_permissions() {
    if [ "$EUID" -ne 0 ]; then
        print_error "此脚本需要root权限运行"
        print_info "请使用: sudo ./deploy-from-github.sh"
        exit 1
    fi
}

# 检查系统要求
check_requirements() {
    print_info "检查系统要求..."
    
    # 检查Git
    if ! command -v git &> /dev/null; then
        print_info "安装Git..."
        apt-get update && apt-get install -y git
    fi
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        print_info "安装Docker..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        systemctl enable docker
        systemctl start docker
    fi
    
    # 检查Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_info "安装Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    
    print_success "系统要求检查完成"
}

# 克隆或更新代码
deploy_code() {
    print_info "部署代码..."
    
    if [ -d "$DEPLOY_DIR" ]; then
        print_info "更新现有代码..."
        cd "$DEPLOY_DIR"
        git fetch origin
        git reset --hard origin/$BRANCH
        git clean -fd
    else
        print_info "克隆新代码..."
        git clone -b "$BRANCH" "$REPO_URL" "$DEPLOY_DIR"
        cd "$DEPLOY_DIR"
    fi
    
    print_success "代码部署完成"
}

# 设置权限
setup_permissions() {
    print_info "设置文件权限..."
    
    # 创建应用用户（如果不存在）
    if ! id "resume-app" &>/dev/null; then
        useradd -r -s /bin/false resume-app
    fi
    
    # 设置目录权限
    chown -R resume-app:resume-app "$DEPLOY_DIR"
    chmod +x "$DEPLOY_DIR/deploy-production.sh"
    chmod +x "$DEPLOY_DIR/stop-production.sh"
    
    print_success "权限设置完成"
}

# 配置环境
setup_environment() {
    print_info "配置环境..."
    
    cd "$DEPLOY_DIR"
    
    # 如果不存在环境配置文件，创建一个
    if [ ! -f ".env.production" ]; then
        if [ -f ".env.production.example" ]; then
            cp .env.production.example .env.production
            
            # 生成随机密钥
            SECRET_KEY=$(openssl rand -hex 32)
            JWT_SECRET_KEY=$(openssl rand -hex 32)
            
            # 替换默认密钥
            sed -i "s/your-very-secure-secret-key-here-change-this-in-production/$SECRET_KEY/" .env.production
            sed -i "s/your-jwt-secret-key-here-change-this-in-production/$JWT_SECRET_KEY/" .env.production
            
            # 设置域名（如果有公网IP）
            PUBLIC_IP=$(curl -s ifconfig.me || echo "localhost")
            sed -i "s/your-domain.com/$PUBLIC_IP/" .env.production
            
            print_success "环境配置文件已创建"
        else
            print_error "找不到环境配置模板文件"
            exit 1
        fi
    else
        print_info "环境配置文件已存在，跳过创建"
    fi
}

# 部署服务
deploy_services() {
    print_info "部署服务..."
    
    cd "$DEPLOY_DIR"
    
    # 停止现有服务（如果存在）
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        print_info "停止现有服务..."
        docker-compose -f docker-compose.prod.yml down
    fi
    
    # 启动新服务
    print_info "启动新服务..."
    ./deploy-production.sh
    
    print_success "服务部署完成"
}

# 配置系统服务（可选）
setup_systemd_service() {
    read -p "是否要配置系统服务以开机自启？[y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "配置系统服务..."
        
        cat > /etc/systemd/system/resume-editor.service << EOF
[Unit]
Description=Resume Editor Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$DEPLOY_DIR
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
        
        systemctl daemon-reload
        systemctl enable resume-editor.service
        
        print_success "系统服务配置完成"
    fi
}

# 显示部署信息
show_deployment_info() {
    print_success "======================================"
    print_success " 浩流简历编辑器 GitHub 部署完成！"
    print_success "======================================"
    echo ""
    print_info "部署信息："
    echo "  部署目录: $DEPLOY_DIR"
    echo "  仓库地址: $REPO_URL"
    echo "  部署分支: $BRANCH"
    echo ""
    print_info "访问地址："
    PUBLIC_IP=$(curl -s ifconfig.me || echo "localhost")
    echo "  前端: http://$PUBLIC_IP:3000"
    echo "  后端API: http://$PUBLIC_IP:8080"
    echo ""
    print_info "管理命令："
    echo "  查看日志: cd $DEPLOY_DIR && docker-compose -f docker-compose.prod.yml logs -f"
    echo "  重启服务: cd $DEPLOY_DIR && ./deploy-production.sh"
    echo "  停止服务: cd $DEPLOY_DIR && ./stop-production.sh"
    echo ""
    print_info "更新部署："
    echo "  运行: sudo $0 -r $REPO_URL -b $BRANCH -d $DEPLOY_DIR"
    echo ""
}

# 主函数
main() {
    print_info "开始从GitHub部署浩流简历编辑器..."
    
    check_permissions
    check_requirements
    deploy_code
    setup_permissions
    setup_environment
    deploy_services
    setup_systemd_service
    show_deployment_info
    
    print_success "GitHub部署完成！"
}

# 运行主函数
main "$@"