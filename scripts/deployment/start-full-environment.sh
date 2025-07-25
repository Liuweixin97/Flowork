#!/bin/bash
# 一键启动完整环境 - Dify + 简历编辑器
# 作者: Claude AI Assistant
# 更新时间: 2025-07-25

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目路径配置
DIFY_DIR="/Users/liuweixin/Desktop/MyProjects/dify"
RESUME_DIR="/Users/liuweixin/Desktop/MyProjects/浩流简历编辑器"
BACKEND_DIR="$RESUME_DIR/backend"
FRONTEND_DIR="$RESUME_DIR/frontend"

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

# 函数: 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 函数: 检查端口是否被占用
check_port() {
    lsof -i :$1 >/dev/null 2>&1
}

# 函数: 杀死端口上的进程
kill_port() {
    local port=$1
    if check_port $port; then
        print_status "清理端口 $port 上的进程..." "warning"
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# 函数: 等待服务启动
wait_for_service() {
    local url="$1"
    local name="$2"
    local max_attempts="${3:-30}"
    local attempt=1
    
    print_status "等待 $name 服务启动..." "info"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_status "$name 服务已就绪" "success"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo ""
    print_status "$name 服务启动超时" "error"
    return 1
}

# 主函数: 启动完整环境
start_complete_environment() {
    print_status "🌟 启动完整环境 (Dify + 简历编辑器)..." "info"
    
    # 1. 检查系统依赖
    print_status "检查系统依赖..." "info"
    
    if ! command_exists docker; then
        print_status "Docker 未安装，请先安装 Docker" "error"
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_status "Docker Compose 未安装，请先安装 Docker Compose" "error"
        exit 1
    fi
    
    if ! command_exists python3; then
        print_status "Python 3 未安装，请先安装 Python 3" "error"
        exit 1
    fi
    
    if ! command_exists node; then
        print_status "Node.js 未安装，请先安装 Node.js" "error"
        exit 1
    fi
    
    if ! command_exists npm; then
        print_status "npm 未安装，请先安装 npm" "error"
        exit 1
    fi
    
    print_status "系统依赖检查通过" "success"
    
    # 2. 检查项目目录
    if [ ! -d "$DIFY_DIR" ]; then
        print_status "Dify 目录不存在: $DIFY_DIR" "error"
        exit 1
    fi
    
    if [ ! -d "$RESUME_DIR" ]; then
        print_status "简历编辑器目录不存在: $RESUME_DIR" "error"
        exit 1
    fi
    
    print_status "项目目录检查通过" "success"
    
    # 3. 清理端口占用
    print_status "清理端口占用..." "info"
    kill_port 80    # Dify
    kill_port 8080  # 后端
    kill_port 3000  # 前端
    kill_port 5432  # PostgreSQL
    kill_port 6379  # Redis
    
    # 4. 启动 Dify
    print_status "启动 Dify 服务..." "info"
    cd "$DIFY_DIR"
    
    # 检查 Dify 是否已经在运行
    if docker-compose ps | grep -q "Up"; then
        print_status "Dify 服务已在运行，重启服务..." "warning"
        docker-compose down
        sleep 5
    fi
    
    # 启动 Dify
    if docker-compose up -d; then
        print_status "Dify 服务启动命令执行成功" "success"
        
        # 等待 Dify 完全启动
        if wait_for_service "http://localhost" "Dify" 60; then
            print_status "Dify 服务启动完成" "success"
        else
            print_status "Dify 服务启动超时，但继续启动简历编辑器..." "warning"
        fi
    else
        print_status "Dify 服务启动失败" "error"
        exit 1
    fi
    
    # 5. 启动简历编辑器后端
    print_status "启动简历编辑器后端..." "info"
    cd "$BACKEND_DIR"
    
    # 检查和创建虚拟环境
    if [ ! -d "venv" ]; then
        print_status "创建 Python 虚拟环境..." "info"
        python3 -m venv venv
    fi
    
    # 激活虚拟环境并安装依赖
    source venv/bin/activate
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        print_status "安装后端依赖..." "info"
        pip install -r requirements.txt >/dev/null 2>&1
    fi
    
    # 启动后端服务 (后台运行)
    nohup python app.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    
    # 等待后端启动
    if wait_for_service "http://localhost:8080/api/health" "后端" 20; then
        print_status "简历编辑器后端启动成功 (PID: $BACKEND_PID)" "success"
    else
        print_status "后端服务启动失败" "error"
        exit 1
    fi
    
    # 6. 启动简历编辑器前端
    print_status "启动简历编辑器前端..." "info"
    cd "$FRONTEND_DIR"
    
    # 使用内网穿透配置
    if [ -f ".env.tunnel" ]; then
        print_status "使用内网穿透配置..." "info"
        cp .env.tunnel .env
    fi
    
    # 安装前端依赖
    if [ ! -d "node_modules" ]; then
        print_status "安装前端依赖..." "info"
        npm install >/dev/null 2>&1
    fi
    
    # 启动前端服务 (后台运行)
    nohup npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    
    # 等待前端启动
    sleep 10  # 前端启动需要更长时间
    if wait_for_service "http://localhost:3000" "前端" 30; then
        print_status "简历编辑器前端启动成功 (PID: $FRONTEND_PID)" "success"
    else
        print_status "前端服务启动失败" "error"
        exit 1
    fi
    
    # 7. 显示启动完成信息
    print_status "🎉 完整环境启动成功！" "success"
    
    echo ""
    echo "========================================================"
    echo "🌟 浩流简历编辑器 - 完整环境已启动"
    echo "========================================================"
    echo "📡 Dify 平台:           http://localhost"
    echo "🖥️  简历编辑器前端:      http://localhost:3000"
    echo "🔧 简历编辑器后端 API: http://localhost:8080"
    echo ""
    echo "🌐 内网穿透地址:"
    echo "   前端: http://mi3qm328989.vicp.fun"
    echo "   后端: http://mi3qm328989.vicp.fun:45093"
    echo ""
    echo "📋 Dify 集成端点:"
    echo "   POST http://localhost:8080/api/resumes/from-dify"
    echo ""
    echo "📊 服务状态检查:"
    echo "   python3 manage.py status"
    echo ""
    echo "🛑 停止所有服务:"
    echo "   ./停止完整环境.sh"
    echo "   或: python3 manage.py stop"
    echo "========================================================"
    
    # 8. 保存启动信息
    cat > "$RESUME_DIR/服务状态.txt" << EOF
启动时间: $(date)
Dify PID: $(docker-compose -f "$DIFY_DIR/docker-compose.yaml" ps -q)
后端 PID: $BACKEND_PID
前端 PID: $FRONTEND_PID

日志文件:
- 后端日志: $RESUME_DIR/backend.log
- 前端日志: $RESUME_DIR/frontend.log
- Dify 日志: docker-compose logs -f (在 $DIFY_DIR 目录下)
EOF
    
    print_status "服务信息已保存到 服务状态.txt" "info"
}

# 错误处理
cleanup_on_error() {
    print_status "启动过程中出现错误，正在清理..." "error"
    
    # 停止可能已启动的服务
    if [ -f "$RESUME_DIR/backend.pid" ]; then
        BACKEND_PID=$(cat "$RESUME_DIR/backend.pid")
        kill $BACKEND_PID 2>/dev/null || true
        rm -f "$RESUME_DIR/backend.pid"
    fi
    
    if [ -f "$RESUME_DIR/frontend.pid" ]; then
        FRONTEND_PID=$(cat "$RESUME_DIR/frontend.pid")
        kill $FRONTEND_PID 2>/dev/null || true  
        rm -f "$RESUME_DIR/frontend.pid"
    fi
    
    exit 1
}

# 设置错误处理
trap cleanup_on_error ERR

# 检查是否以root用户运行
if [ "$EUID" -eq 0 ]; then
    print_status "请不要以 root 用户运行此脚本" "error"
    exit 1
fi

# 主程序入口
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "使用方法: ./一键启动完整环境.sh"
    echo ""
    echo "此脚本将启动完整的开发环境，包括:"
    echo "1. Dify 平台 (Docker)"
    echo "2. 简历编辑器后端 (Python Flask)"
    echo "3. 简历编辑器前端 (React + Vite)"
    echo ""
    echo "注意事项:"
    echo "- 需要 Docker 和 Docker Compose"
    echo "- 需要 Python 3 和 Node.js"
    echo "- 将使用内网穿透配置"
    echo "- 服务将在后台运行"
    exit 0
fi

# 执行主函数
start_complete_environment