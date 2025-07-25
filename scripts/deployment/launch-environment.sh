#!/bin/bash
# 启动完整环境 - 包括Dify和简历编辑器

echo "🌟 启动完整环境 (Dify + 简历编辑器)..."

# 启动Dify
echo "1. 启动Dify服务..."
python3 manage.py dify

# 等待Dify启动
echo "⏳ 等待Dify启动完成..."
sleep 15

# 启动简历编辑器
echo "2. 启动简历编辑器..."
python3 manage.py start

echo "🎉 完整环境启动完成！"