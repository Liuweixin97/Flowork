#!/usr/bin/env python3
"""检查服务状态"""

import urllib.request
import json

def check_services():
    print("🔍 检查简历编辑器服务状态...")
    
    # 检查后端
    try:
        response = urllib.request.urlopen("http://localhost:8080/api/health", timeout=5)
        result = json.loads(response.read().decode('utf-8'))
        print("✅ 后端服务运行正常")
        print(f"   状态: {result.get('status')}")
        print(f"   服务: {result.get('service')}")
    except Exception as e:
        print(f"❌ 后端服务连接失败: {e}")
        return False
    
    # 检查前端
    try:
        response = urllib.request.urlopen("http://localhost:3000", timeout=5)
        if response.getcode() == 200:
            print("✅ 前端服务运行正常")
        else:
            print(f"❌ 前端服务响应异常: {response.getcode()}")
            return False
    except Exception as e:
        print(f"❌ 前端服务连接失败: {e}")
        return False
    
    # 检查简历数据
    try:
        response = urllib.request.urlopen("http://localhost:8080/api/resumes", timeout=5)
        result = json.loads(response.read().decode('utf-8'))
        resumes = result.get('resumes', [])
        print(f"✅ 数据库正常，已有 {len(resumes)} 份简历")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if check_services():
        print("\n🎉 所有服务运行正常！")
        print("\n📋 访问信息:")
        print("🖥️  前端界面: http://localhost:3000")
        print("🔧 后端API: http://localhost:8080")
        print("📡 Dify接收端点: http://localhost:8080/api/resumes/from-dify")
    else:
        print("\n❌ 某些服务存在问题，请检查")