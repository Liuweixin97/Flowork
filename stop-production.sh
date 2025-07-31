#!/bin/bash

# 停止生产环境服务脚本
# Stop Production Services Script for Resume Editor

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

# 停止所有服务
stop_services() {
    print_info "停止生产环境服务..."
    
    if [ -f "docker-compose.prod.yml" ]; then
        docker-compose -f docker-compose.prod.yml down
        print_success "所有服务已停止"
    else
        print_error "docker-compose.prod.yml 文件不存在"
        exit 1
    fi
}

# 清理资源（可选）
cleanup_resources() {
    read -p "是否要清理Docker镜像和卷？[y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "清理Docker资源..."
        
        # 清理未使用的镜像
        docker image prune -f
        
        # 清理未使用的卷（谨慎使用）
        read -p "警告：这将删除未使用的数据卷，确定继续？[y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker volume prune -f
        fi
        
        print_success "Docker资源清理完成"
    fi
}

# 备份数据（可选）
backup_data() {
    read -p "是否要备份数据？[y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "创建数据备份..."
        
        BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # 备份应用数据
        if [ -d "/var/lib/resume-editor/data" ]; then
            cp -r /var/lib/resume-editor/data "$BACKUP_DIR/"
        fi
        
        # 备份数据库
        if [ -d "/var/lib/resume-editor/postgres" ]; then
            cp -r /var/lib/resume-editor/postgres "$BACKUP_DIR/"
        fi
        
        print_success "数据已备份到 $BACKUP_DIR"
    fi
}

# 显示服务状态
show_status() {
    print_info "当前服务状态："
    docker-compose -f docker-compose.prod.yml ps
}

# 主函数
main() {
    print_info "停止浩流简历编辑器生产环境..."
    
    # 显示当前状态
    show_status
    
    # 询问是否备份
    backup_data
    
    # 停止服务
    stop_services
    
    # 询问是否清理
    cleanup_resources
    
    print_success "生产环境已停止"
}

# 运行主函数
main "$@"