#!/bin/bash
# 停止完整环境 - Dify + 简历编辑器
# 作者: Claude AI Assistant
# 更新时间: 2025-07-25

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目路径配置
DIFY_DIR="/Users/liuweixin/Desktop/MyProjects/dify"
RESUME_DIR="/Users/liuweixin/Desktop/MyProjects/浩流简历编辑器"

# 函数: 打印状态信息
print_status() {
    local message="$1"
    local status="${2:-info}"
    
    case $status in
        "success")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "error")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "warning")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        *)
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
    esac
}

# 函数: 杀死端口上的进程
kill_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        print_status "停止端口 $port 上的服务..." "warning"
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 1
    fi
}

# 主函数: 停止完整环境
stop_complete_environment() {
    print_status "🛑 停止完整环境 (Dify + 简历编辑器)..." "info"
    
    # 1. 停止简历编辑器前端
    if [ -f "$RESUME_DIR/frontend.pid" ]; then
        FRONTEND_PID=$(cat "$RESUME_DIR/frontend.pid")
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            print_status "停止简历编辑器前端 (PID: $FRONTEND_PID)..." "info"
            kill $FRONTEND_PID 2>/dev/null || true
            sleep 2
            # 强制杀死如果还在运行
            kill -9 $FRONTEND_PID 2>/dev/null || true
        fi
        rm -f "$RESUME_DIR/frontend.pid"
        print_status "简历编辑器前端已停止" "success"
    else
        print_status "未找到前端PID文件，尝试清理端口..." "warning"
        kill_port 3000
    fi
    
    # 2. 停止简历编辑器后端
    if [ -f "$RESUME_DIR/backend.pid" ]; then
        BACKEND_PID=$(cat "$RESUME_DIR/backend.pid")
        if kill -0 $BACKEND_PID 2>/dev/null; then
            print_status "停止简历编辑器后端 (PID: $BACKEND_PID)..." "info"
            kill $BACKEND_PID 2>/dev/null || true
            sleep 2
            # 强制杀死如果还在运行
            kill -9 $BACKEND_PID 2>/dev/null || true
        fi
        rm -f "$RESUME_DIR/backend.pid"
        print_status "简历编辑器后端已停止" "success"
    else
        print_status "未找到后端PID文件，尝试清理端口..." "warning"
        kill_port 8080
    fi
    
    # 3. 停止 Dify 服务
    if [ -d "$DIFY_DIR" ]; then
        print_status "停止 Dify 服务..." "info"
        cd "$DIFY_DIR"
        
        if docker-compose ps | grep -q "Up"; then
            docker-compose down
            print_status "Dify 服务已停止" "success"
        else
            print_status "Dify 服务未在运行" "info"
        fi
    else
        print_status "Dify 目录不存在，跳过" "warning"
    fi
    
    # 4. 清理所有相关端口
    print_status "清理所有相关端口..." "info"
    kill_port 80     # Dify
    kill_port 8080   # 后端
    kill_port 3000   # 前端
    kill_port 5432   # PostgreSQL
    kill_port 6379   # Redis
    
    # 5. 清理日志和状态文件
    print_status "清理临时文件..." "info"
    rm -f "$RESUME_DIR/backend.log"
    rm -f "$RESUME_DIR/frontend.log"
    rm -f "$RESUME_DIR/服务状态.txt"
    
    # 6. 清理可能残留的进程
    print_status "清理残留进程..." "info"
    
    # 清理Python进程
    pkill -f "python.*app.py" 2>/dev/null || true
    
    # 清理Node进程  
    pkill -f "node.*vite" 2>/dev/null || true
    pkill -f "npm.*run.*dev" 2>/dev/null || true
    
    # 清理可能的Vite进程
    pkill -f "vite" 2>/dev/null || true
    
    sleep 2
    
    print_status "🎉 完整环境已停止！" "success"
    
    echo ""
    echo "========================================================"
    echo "🛑 浩流简历编辑器 - 完整环境已停止"
    echo "========================================================"
    echo "所有服务已关闭:"
    echo "✅ Dify 平台已停止"
    echo "✅ 简历编辑器后端已停止"
    echo "✅ 简历编辑器前端已停止"
    echo "✅ 相关端口已清理"
    echo ""
    echo "重新启动环境:"
    echo "   ./一键启动完整环境.sh"
    echo "========================================================"
}

# 错误处理
cleanup_on_error() {
    print_status "停止过程中出现错误" "error"
    exit 1
}

# 设置错误处理
trap cleanup_on_error ERR

# 主程序入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "使用方法: ./停止完整环境.sh"
    echo ""
    echo "此脚本将停止完整的开发环境，包括:"
    echo "1. Dify 平台 (Docker containers)" 
    echo "2. 简历编辑器后端 (Python Flask)"
    echo "3. 简历编辑器前端 (React + Vite)"
    echo "4. 清理相关端口和临时文件"
    exit 0
fi

# 执行主函数
stop_complete_environment