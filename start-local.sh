#!/bin/bash

echo "🚀 启动简历编辑器服务（本地模式）..."

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 错误处理函数
error_exit() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# 检查必要的命令
check_command() {
    if ! command -v $1 &> /dev/null; then
        error_exit "$1 未安装，请先安装 $1"
    fi
}

# 检查依赖
echo "📋 检查系统依赖..."
check_command "python3"
check_command "npm"

# 切换到项目目录
cd "$SCRIPT_DIR"

# 设置后端
echo "🐍 设置后端服务..."
cd "$BACKEND_DIR"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    info "创建 Python 虚拟环境..."
    python3 -m venv venv || error_exit "创建虚拟环境失败"
fi

# 激活虚拟环境并安装依赖
info "安装后端依赖..."
source venv/bin/activate || error_exit "激活虚拟环境失败"
pip install -r requirements.txt > /dev/null 2>&1 || error_exit "安装 Python 依赖失败"

# 设置前端
echo "📦 设置前端服务..."
cd "$FRONTEND_DIR"

# 检查是否需要安装依赖
if [ ! -d "node_modules" ]; then
    info "安装前端依赖..."
    npm install || error_exit "安装前端依赖失败"
fi

# 启动服务
echo "🚀 启动服务..."

# 启动后端（后台运行）
info "启动后端服务..."
cd "$BACKEND_DIR"
source venv/bin/activate
nohup python app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid

# 等待后端启动
sleep 3

# 检查后端是否成功启动
if ! ps -p $BACKEND_PID > /dev/null 2>&1; then
    error_exit "后端服务启动失败，请检查 backend.log"
fi

# 启动前端（后台运行）
info "启动前端服务..."
cd "$FRONTEND_DIR"
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid

# 等待前端启动
sleep 5

# 检查前端是否成功启动
if ! ps -p $FRONTEND_PID > /dev/null 2>&1; then
    warning "前端服务可能启动失败，请检查 frontend.log"
fi

# 健康检查
echo "🏥 检查服务健康状态..."
sleep 2

# 检查后端健康状态
if curl -f http://localhost:8080/api/health > /dev/null 2>&1; then
    success "后端服务运行正常"
else
    warning "后端服务健康检查失败"
fi

# 检查前端（简单的端口检查）
if netstat -an | grep -q ":3000.*LISTEN"; then
    success "前端服务运行正常"
else
    warning "前端服务可能未正常启动"
fi

echo ""
echo "🎉 简历编辑器服务启动完成！"
echo ""
echo -e "${BLUE}📍 访问地址:${NC}"
echo -e "   前端界面: ${GREEN}http://localhost:3000${NC}"
echo -e "   后端API:  ${GREEN}http://localhost:8080${NC}"
echo ""
echo -e "${BLUE}📡 Dify配置:${NC}"
echo "   HTTP节点URL: http://localhost:8080/api/resumes/from-dify"
echo "   请求方法: POST"
echo "   请求体示例:"
echo "   {"
echo "     \"resume_markdown\": \"您的简历Markdown内容\","
echo "     \"title\": \"简历标题\""
echo "   }"
echo ""
echo -e "${BLUE}📖 管理命令:${NC}"
echo "   查看后端日志: tail -f backend.log"
echo "   查看前端日志: tail -f frontend.log"
echo "   停止服务: ./stop-local.sh"
echo ""
echo -e "${YELLOW}💡 提示: 服务在后台运行，关闭终端不会停止服务${NC}"