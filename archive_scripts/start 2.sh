#!/bin/bash

echo "🚀 启动简历编辑器服务..."

# 检查是否有Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 检查Dify网络是否存在
if ! docker network ls | grep -q "dify_default"; then
    echo "⚠️  Dify网络不存在，创建独立网络..."
    # 如果Dify网络不存在，修改docker-compose配置
    sed -i.bak 's/dify_default:/# dify_default:/' docker-compose.yml
    sed -i.bak 's/external: true/# external: true/' docker-compose.yml
fi

echo "📦 构建并启动服务..."
docker-compose up --build -d

echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 检查后端健康状态
echo "🏥 检查后端健康状态..."
if curl -f http://localhost:8080/api/health > /dev/null 2>&1; then
    echo "✅ 后端服务正常运行"
else
    echo "❌ 后端服务启动失败"
    docker-compose logs resume-backend
    exit 1
fi

echo ""
echo "🎉 简历编辑器服务启动成功！"
echo ""
echo "📍 访问地址:"
echo "   前端界面: http://localhost:3000"
echo "   后端API:  http://localhost:8080"
echo ""
echo "📡 Dify配置:"
echo "   HTTP节点URL: http://localhost:8080/api/resumes/from-dify"
echo "   请求方法: POST"
echo "   请求体示例:"
echo "   {"
echo "     \"resume_markdown\": \"您的简历Markdown内容\","
echo "     \"title\": \"简历标题\""
echo "   }"
echo ""
echo "📖 查看日志: docker-compose logs -f"
echo "🛑 停止服务: docker-compose down"