#!/bin/bash

# 浩流简历编辑器前后端服务重启脚本
# 使用方法: ./restart_services.sh

set -e  # 遇到错误时停止执行

echo "=== 浩流简历编辑器服务重启脚本 ==="
echo "开始重启前后端服务..."

# 定义颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo -e "${YELLOW}项目目录: $PROJECT_ROOT${NC}"

# 1. 停止现有服务
echo -e "\n${YELLOW}1. 停止现有服务...${NC}"

# 停止后端服务
if [ -f "$BACKEND_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$BACKEND_DIR/backend.pid")
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 2
    fi
    rm -f "$BACKEND_DIR/backend.pid"
fi

# 停止前端服务
if [ -f "$FRONTEND_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$FRONTEND_DIR/frontend.pid")
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        sleep 2
    fi
    rm -f "$FRONTEND_DIR/frontend.pid"
fi

# 强制清理可能残留的进程
echo "清理残留进程..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "npm.*dev" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

# 强制释放端口
lsof -ti:8080 2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null || true

echo -e "${GREEN}服务停止完成${NC}"

# 2. 启动后端服务
echo -e "\n${YELLOW}2. 启动后端服务...${NC}"
cd "$BACKEND_DIR"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: python3 未安装${NC}"
    exit 1
fi

# 检查依赖
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}错误: 未找到 requirements.txt${NC}"
    exit 1
fi

# 启动后端
echo "启动Flask后端服务..."
nohup python3 app.py > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid

# 等待后端启动
echo "等待后端服务启动..."
sleep 5

# 检查后端是否成功启动
if ps -p $BACKEND_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端服务启动成功 (PID: $BACKEND_PID)${NC}"
    echo "  访问地址: http://localhost:8080"
else
    echo -e "${RED}✗ 后端服务启动失败${NC}"
    echo "查看日志: tail -20 $BACKEND_DIR/backend.log"
    exit 1
fi

# 3. 启动前端服务
echo -e "\n${YELLOW}3. 启动前端服务...${NC}"
cd "$FRONTEND_DIR"

# 检查Node.js环境
if ! command -v npm &> /dev/null; then
    echo -e "${RED}错误: npm 未安装${NC}"
    exit 1
fi

# 检查依赖
if [ ! -f "package.json" ]; then
    echo -e "${RED}错误: 未找到 package.json${NC}"
    exit 1
fi

# 安装依赖（如果需要）
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

# 启动前端
echo "启动Vite开发服务器..."
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > frontend.pid

# 等待前端启动
echo "等待前端服务启动..."
sleep 8

# 检查前端是否成功启动
if ps -p $FRONTEND_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 前端服务启动成功 (PID: $FRONTEND_PID)${NC}"
    echo "  访问地址: http://localhost:3000"
else
    echo -e "${RED}✗ 前端服务启动失败${NC}"
    echo "查看日志: tail -20 $FRONTEND_DIR/frontend.log"
    exit 1
fi

# 4. 验证服务状态
echo -e "\n${YELLOW}4. 验证服务状态...${NC}"

# 检查后端API
echo "检查后端API..."
if curl -s http://localhost:8080/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端API响应正常${NC}"
else
    echo -e "${YELLOW}⚠ 后端API可能需要更多时间启动${NC}"
fi

# 检查前端页面
echo "检查前端页面..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 前端页面响应正常${NC}"
else
    echo -e "${YELLOW}⚠ 前端页面可能需要更多时间启动${NC}"
fi

# 5. 显示服务信息
echo -e "\n${GREEN}=== 服务重启完成 ===${NC}"
echo -e "${YELLOW}服务状态:${NC}"
echo "  后端服务: http://localhost:8080 (PID: $BACKEND_PID)"
echo "  前端服务: http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo -e "${YELLOW}日志文件:${NC}"
echo "  后端日志: $BACKEND_DIR/backend.log"
echo "  前端日志: $FRONTEND_DIR/frontend.log"
echo ""
echo -e "${YELLOW}停止服务:${NC}"
echo "  使用 ./stop_services.sh 或手动停止进程"
echo ""
echo -e "${YELLOW}常用命令:${NC}"
echo "  查看后端日志: tail -f $BACKEND_DIR/backend.log"
echo "  查看前端日志: tail -f $FRONTEND_DIR/frontend.log"
echo "  检查进程状态: ps aux | grep -E '(python.*app.py|npm.*dev)'"

echo -e "\n${GREEN}✓ 所有服务已成功重启！${NC}"