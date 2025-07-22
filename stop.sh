#!/bin/bash

echo "🛑 停止简历编辑器服务..."

docker-compose down

echo "✅ 服务已停止"
echo ""
echo "💡 如需重新启动服务，请运行: ./start.sh"
echo "🗑️  如需完全清理（包括数据），请运行: docker-compose down -v"