#!/bin/bash

echo "🚀 启动简历编辑器服务 (包含Dify Chatflow集成)"
echo "================================================"

# 检查端口占用
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null; then
        echo "⚠️  端口 $1 已被占用"
        return 1
    else
        echo "✅ 端口 $1 可用"
        return 0
    fi
}

# 启动后端服务
start_backend() {
    echo "🔧 启动后端服务..."
    cd backend
    
    if [ ! -d "venv" ]; then
        echo "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    
    echo "后端服务启动在: http://localhost:8080"
    python3 app.py &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    cd ..
}

# 启动模拟Dify服务
start_mock_dify() {
    echo "🎭 启动模拟Dify服务..."
    echo "Dify API端点: http://localhost:8001"
    python3 mock_dify_service.py &
    DIFY_PID=$!
    echo $DIFY_PID > mock_dify.pid
}

# 启动前端服务
start_frontend() {
    echo "⚡ 启动前端服务..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo "安装Node.js依赖..."
        npm install > /dev/null 2>&1
    fi
    
    echo "前端服务启动在: http://localhost:3000 (或其他可用端口)"
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    cd ..
}

# 主要启动流程
main() {
    # 检查必要的命令
    command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 未安装"; exit 1; }
    command -v npm >/dev/null 2>&1 || { echo "❌ Node.js/npm 未安装"; exit 1; }
    
    # 启动服务
    start_backend
    sleep 2
    
    start_mock_dify
    sleep 2
    
    start_frontend
    sleep 3
    
    echo ""
    echo "🎉 所有服务已启动!"
    echo "================================================"
    echo "📋 服务信息:"
    echo "  • 后端服务: http://localhost:8080"
    echo "  • 前端页面: http://localhost:3002 (或查看上面的输出)"
    echo "  • 模拟Dify: http://localhost:8001"
    echo ""
    echo "🧪 测试命令:"
    echo "  • python3 test_chatflow_integration.py"
    echo "  • python3 test_full_conversation.py"
    echo ""
    echo "🛑 停止服务:"
    echo "  • ./stop_services.sh"
    echo ""
    echo "🎯 现在可以在浏览器中访问前端页面，点击'AI创建简历'体验完整功能！"
}

main "$@"