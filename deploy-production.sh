#!/bin/bash

# 生产环境部署脚本
# Production Deployment Script for Resume Editor

set -e  # 遇到错误立即退出

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

# 检查系统要求
check_requirements() {
    print_info "检查系统要求..."
    
    # 检查 Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    # 检查 Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    # 检查系统资源
    AVAILABLE_MEM=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    if [ "$AVAILABLE_MEM" -lt 2048 ]; then
        print_warning "可用内存不足 2GB，可能影响性能"
    fi
    
    print_success "系统要求检查完成"
}

# 创建必要的目录
create_directories() {
    print_info "创建必要的目录..."
    
    sudo mkdir -p /var/lib/resume-editor/{data,logs,postgres}
    sudo chown -R $USER:$USER /var/lib/resume-editor
    chmod -R 755 /var/lib/resume-editor
    
    print_success "目录创建完成"
}

# 设置环境配置
setup_environment() {
    print_info "设置环境配置..."
    
    if [ ! -f ".env.production" ]; then
        if [ -f ".env.production.example" ]; then
            cp .env.production.example .env.production
            print_warning "已创建 .env.production 文件，请编辑配置"
            print_warning "特别注意修改 SECRET_KEY 和 JWT_SECRET_KEY"
            return 1
        else
            print_error ".env.production.example 文件不存在"
            exit 1
        fi
    fi
    
    print_success "环境配置完成"
}

# 构建Docker镜像
build_images() {
    print_info "构建 Docker 镜像..."
    
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    print_success "Docker 镜像构建完成"
}

# 启动服务
start_services() {
    print_info "启动生产服务..."
    
    # 启动数据库服务
    docker-compose -f docker-compose.prod.yml up -d resume-db
    sleep 10
    
    # 启动后端服务
    docker-compose -f docker-compose.prod.yml up -d resume-backend
    sleep 15
    
    # 启动前端服务
    docker-compose -f docker-compose.prod.yml up -d resume-frontend
    
    # 如果有 nginx 配置，启动 nginx
    if [ -f "nginx/nginx.prod.conf" ]; then
        docker-compose -f docker-compose.prod.yml up -d nginx
    fi
    
    print_success "生产服务启动完成"
}

# 健康检查
health_check() {
    print_info "执行健康检查..."
    
    # 等待服务启动
    sleep 30
    
    # 检查后端健康状态
    if curl -f http://localhost:8080/api/health > /dev/null 2>&1; then
        print_success "后端服务健康"
    else
        print_error "后端服务不健康"
        return 1
    fi
    
    # 检查前端可访问性
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_success "前端服务可访问"
    else
        print_error "前端服务不可访问"
        return 1
    fi
    
    print_success "健康检查完成"
}

# 显示部署信息
show_deployment_info() {
    print_success "======================================"
    print_success " 浩流简历编辑器部署完成！"
    print_success "======================================"
    echo ""
    print_info "访问地址："
    echo "  前端: http://localhost:3000"
    echo "  后端API: http://localhost:8080"
    echo "  API文档: http://localhost:8080/api/health"
    echo ""
    print_info "管理命令："
    echo "  查看日志: docker-compose -f docker-compose.prod.yml logs -f"
    echo "  停止服务: docker-compose -f docker-compose.prod.yml down"
    echo "  重启服务: docker-compose -f docker-compose.prod.yml restart"
    echo ""
    print_info "数据位置："
    echo "  应用数据: /var/lib/resume-editor/data"
    echo "  日志文件: /var/lib/resume-editor/logs"
    echo "  数据库: /var/lib/resume-editor/postgres"
    echo ""
}

# 主函数
main() {
    print_info "开始生产环境部署..."
    
    check_requirements
    create_directories
    
    if ! setup_environment; then
        print_error "请先配置 .env.production 文件后重新运行此脚本"
        exit 1
    fi
    
    build_images
    start_services
    
    if health_check; then
        show_deployment_info
    else
        print_error "部署失败，请检查日志"
        docker-compose -f docker-compose.prod.yml logs
        exit 1
    fi
}

# 运行主函数
main "$@"