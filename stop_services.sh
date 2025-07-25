#!/bin/bash

# 浩流简历编辑器前后端服务停止脚本
# 使用方法: ./stop_services.sh

echo "=== 浩流简历编辑器服务停止脚本 ==="

# 定义颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${YELLOW}正在停止所有服务...${NC}"

# 停止后端服务
if [ -f "$BACKEND_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$BACKEND_DIR/backend.pid")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 2
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo "强制停止后端服务..."
            kill -9 $BACKEND_PID
        fi
        echo -e "${GREEN}✓ 后端服务已停止${NC}"
    else
        echo "后端服务未运行"
    fi
    rm -f "$BACKEND_DIR/backend.pid"
else
    echo "未找到后端PID文件"
fi

# 停止前端服务
if [ -f "$FRONTEND_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$FRONTEND_DIR/frontend.pid")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        sleep 2
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo "强制停止前端服务..."
            kill -9 $FRONTEND_PID
        fi
        echo -e "${GREEN}✓ 前端服务已停止${NC}"
    else
        echo "前端服务未运行"
    fi
    rm -f "$FRONTEND_DIR/frontend.pid"
else
    echo "未找到前端PID文件"
fi

# 清理残留进程
echo "清理残留进程..."
pkill -f "python.*app.py" 2>/dev/null && echo "清理了残留的Python进程" || true
pkill -f "npm.*dev" 2>/dev/null && echo "清理了残留的npm进程" || true  
pkill -f "vite" 2>/dev/null && echo "清理了残留的Vite进程" || true

# 强制释放端口
lsof -ti:8080 2>/dev/null | xargs kill -9 2>/dev/null && echo "释放了8080端口" || true
lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null && echo "释放了3000端口" || true

echo -e "\n${GREEN}=== 所有服务已停止 ===${NC}"
echo "如需重新启动服务，请运行: ./restart_services.sh"