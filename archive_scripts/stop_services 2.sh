#!/bin/bash

echo "🛑 停止简历编辑器所有服务"
echo "========================"

# 停止进程的函数
stop_service() {
    SERVICE_NAME=$1
    PID_FILE=$2
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            echo "停止 $SERVICE_NAME (PID: $PID)"
            kill $PID
            sleep 2
            # 如果进程还在运行，强制终止
            if kill -0 $PID 2>/dev/null; then
                echo "强制终止 $SERVICE_NAME"
                kill -9 $PID
            fi
        else
            echo "$SERVICE_NAME 进程已停止"
        fi
        rm -f "$PID_FILE"
    else
        echo "未找到 $SERVICE_NAME 的PID文件"
    fi
}

# 停止所有服务
stop_service "后端服务" "backend.pid"
stop_service "前端服务" "frontend.pid"
stop_service "模拟Dify服务" "mock_dify.pid"

# 额外清理：按端口终止可能的残留进程
echo "🧹 清理残留进程..."

for port in 8080 8001 3000 3001 3002; do
    PID=$(lsof -ti:$port)
    if [ ! -z "$PID" ]; then
        echo "终止端口 $port 上的进程 (PID: $PID)"
        kill -9 $PID 2>/dev/null || true
    fi
done

echo "✅ 所有服务已停止"