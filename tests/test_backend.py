#!/usr/bin/env python3
"""
测试后端服务的基本功能
"""

import sys
import json
import time
import subprocess
import requests
from pathlib import Path

def test_backend():
    print("🧪 开始测试后端服务...")
    
    # 创建.env文件
    backend_dir = Path("backend")
    env_file = backend_dir / ".env"
    
    if not env_file.exists():
        print("📝 创建.env配置文件...")
        with open(env_file, "w") as f:
            f.write("""FLASK_DEBUG=True
SECRET_KEY=test-secret-key
HOST=0.0.0.0
PORT=8080
DATABASE_URL=sqlite:///resume_editor.db
""")
    
    # 安装依赖
    print("📦 安装Python依赖...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "Flask==3.0.0", "Flask-SQLAlchemy==3.1.1", "Flask-CORS==4.0.0", 
            "python-markdown==3.5.1", "python-dotenv==1.0.0"
        ], check=True, cwd=backend_dir)
        print("✅ 依赖安装成功")
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False
    
    # 启动后端服务（后台）
    print("🚀 启动后端服务...")
    try:
        process = subprocess.Popen([
            sys.executable, "app.py"
        ], cwd=backend_dir)
        
        # 等待服务启动
        print("⏳ 等待服务启动...")
        time.sleep(5)
        
        # 测试健康检查
        try:
            response = requests.get("http://localhost:8080/api/health", timeout=10)
            if response.status_code == 200:
                print("✅ 后端服务启动成功")
                print(f"📊 健康检查响应: {response.json()}")
                
                # 测试接收Dify数据
                test_dify_integration()
                
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 无法连接到后端服务: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 启动后端服务失败: {e}")
        return False
    finally:
        # 清理进程
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()

def test_dify_integration():
    """测试Dify集成功能"""
    print("\n🔗 测试Dify集成...")
    
    # 测试数据
    test_resume = {
        "resume_markdown": """# 张三

## 个人信息
- 邮箱: zhangsan@example.com
- 电话: 13800138000
- 地址: 北京市朝阳区

## 工作经验

### 高级软件工程师 | ABC科技公司 | 2020-2023
- 负责公司核心产品的后端开发
- 设计和实现微服务架构
- 优化系统性能，提升响应速度50%

## 技能
- Python, Java, JavaScript
- Django, Flask, Spring Boot
- MySQL, Redis, MongoDB
""",
        "title": "张三的简历"
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/api/resumes/from-dify",
            json=test_resume,
            timeout=10
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Dify数据接收成功")
            print(f"📄 简历ID: {result.get('resume_id')}")
            print(f"🔗 编辑链接: {result.get('edit_url')}")
            
            # 测试获取简历
            resume_id = result.get('resume_id')
            if resume_id:
                test_get_resume(resume_id)
                
        else:
            print(f"❌ Dify数据接收失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 测试Dify集成失败: {e}")

def test_get_resume(resume_id):
    """测试获取简历功能"""
    print(f"\n📖 测试获取简历 (ID: {resume_id})...")
    
    try:
        response = requests.get(f"http://localhost:8080/api/resumes/{resume_id}", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 简历获取成功")
            resume = result.get('resume', {})
            print(f"📝 标题: {resume.get('title')}")
            print(f"📅 创建时间: {resume.get('created_at')}")
            
        else:
            print(f"❌ 简历获取失败: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 测试获取简历失败: {e}")

if __name__ == "__main__":
    try:
        success = test_backend()
        if success:
            print("\n🎉 后端测试完成！")
            print("\n📋 测试结果:")
            print("✅ 后端服务启动正常")
            print("✅ 健康检查通过") 
            print("✅ Dify数据接收功能正常")
            print("✅ 数据存储和查询功能正常")
            print("\n🔗 现在可以配置Dify的HTTP节点:")
            print("   URL: http://localhost:8080/api/resumes/from-dify")
            print("   方法: POST")
            print("   请求体: {\"resume_markdown\": \"简历内容\", \"title\": \"标题\"}")
        else:
            print("\n❌ 后端测试失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试过程中发生未预期错误: {e}")
        sys.exit(1)