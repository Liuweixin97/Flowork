#!/bin/bash

echo "🛑 停止简历编辑器服务（本地模式）..."

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# 切换到项目目录
cd "$SCRIPT_DIR"

# 停止后端服务
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        info "停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 2
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            warning "强制停止后端服务..."
            kill -9 $BACKEND_PID
        fi
        success "后端服务已停止"
    else
        warning "后端服务未运行"
    fi
    rm -f backend.pid
else
    warning "未找到后端服务PID文件"
fi

# 停止前端服务
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        info "停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        sleep 2
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            warning "强制停止前端服务..."
            kill -9 $FRONTEND_PID
        fi
        success "前端服务已停止"
    else
        warning "前端服务未运行"
    fi
    rm -f frontend.pid
else
    warning "未找到前端服务PID文件"
fi

# 额外清理：按端口停止可能残留的进程
info "清理可能残留的进程..."

# 停止占用 8080 端口的进程（后端）
BACKEND_PORT_PID=$(lsof -t -i:8080 2>/dev/null)
if [ ! -z "$BACKEND_PORT_PID" ]; then
    info "发现占用8080端口的进程，正在停止..."
    kill $BACKEND_PORT_PID 2>/dev/null
    sleep 1
    if lsof -t -i:8080 > /dev/null 2>&1; then
        kill -9 $BACKEND_PORT_PID 2>/dev/null
    fi
fi

# 停止占用 3000 端口的进程（前端）
FRONTEND_PORT_PID=$(lsof -t -i:3000 2>/dev/null)
if [ ! -z "$FRONTEND_PORT_PID" ]; then
    info "发现占用3000端口的进程，正在停止..."
    kill $FRONTEND_PORT_PID 2>/dev/null
    sleep 1
    if lsof -t -i:3000 > /dev/null 2>&1; then
        kill -9 $FRONTEND_PORT_PID 2>/dev/null
    fi
fi

# 清理日志文件（可选）
read -p "是否清理日志文件？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    info "清理日志文件..."
    rm -f backend.log frontend.log
    success "日志文件已清理"
fi

echo ""
echo "🎉 简历编辑器服务已完全停止！"
echo ""
echo -e "${BLUE}📍 重新启动服务:${NC}"
echo "   ./start-local.sh"