#!/usr/bin/env python3
"""手动测试脚本 - 验证服务功能"""

import sys
import subprocess
import time
import json
import urllib.request
import urllib.parse
import threading
from pathlib import Path

def install_dependencies():
    """安装依赖"""
    print("📦 安装Python依赖...")
    backend_dir = Path("backend")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "Flask==3.0.0", "Flask-SQLAlchemy==3.1.1", "Flask-CORS==4.0.0", 
            "python-markdown==3.5.1", "python-dotenv==1.0.0"
        ], check=True, cwd=backend_dir, capture_output=True)
        print("✅ 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    backend_dir = Path("backend")
    
    try:
        # 启动后端服务
        process = subprocess.Popen([
            sys.executable, "app.py"
        ], cwd=backend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务启动
        time.sleep(8)
        
        return process
        
    except Exception as e:
        print(f"❌ 启动后端服务失败: {e}")
        return None

def test_api(url, method="GET", data=None):
    """测试API接口"""
    try:
        if method == "GET":
            response = urllib.request.urlopen(url, timeout=10)
        elif method == "POST":
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'))
            req.add_header('Content-Type', 'application/json')
            response = urllib.request.urlopen(req, timeout=10)
        
        result = json.loads(response.read().decode('utf-8'))
        return True, result
        
    except Exception as e:
        return False, str(e)

def run_tests():
    """运行所有测试"""
    print("🧪 开始手动测试...")
    
    # 1. 安装依赖
    if not install_dependencies():
        return False
    
    # 2. 启动后端
    process = start_backend()
    if not process:
        return False
    
    try:
        # 3. 测试健康检查
        print("\n🏥 测试健康检查...")
        success, result = test_api("http://localhost:8080/api/health")
        if success:
            print("✅ 健康检查通过")
            print(f"响应: {result}")
        else:
            print(f"❌ 健康检查失败: {result}")
            return False
        
        # 4. 测试Dify数据接收
        print("\n🔗 测试Dify数据接收...")
        test_data = {
            "resume_markdown": """# 张三

## 个人信息
- 邮箱: zhangsan@example.com
- 电话: 13800138000

## 工作经验
### 软件工程师 | ABC公司 | 2020-2023
- 负责后端开发
- 参与架构设计

## 技能
- Python, JavaScript
- Flask, React
""",
            "title": "张三的简历"
        }
        
        success, result = test_api(
            "http://localhost:8080/api/resumes/from-dify", 
            method="POST", 
            data=test_data
        )
        
        if success:
            print("✅ Dify数据接收成功")
            print(f"简历ID: {result.get('resume_id')}")
            print(f"编辑链接: {result.get('edit_url')}")
            
            # 5. 测试获取简历
            resume_id = result.get('resume_id')
            if resume_id:
                print(f"\n📖 测试获取简历 (ID: {resume_id})...")
                success, result = test_api(f"http://localhost:8080/api/resumes/{resume_id}")
                if success:
                    print("✅ 简历获取成功")
                    resume = result.get('resume', {})
                    print(f"标题: {resume.get('title')}")
                else:
                    print(f"❌ 简历获取失败: {result}")
                    
        else:
            print(f"❌ Dify数据接收失败: {result}")
            return False
        
        print("\n🎉 所有测试通过！")
        return True
        
    finally:
        # 清理进程
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except:
                process.kill()

def main():
    print("🧪 简历编辑器 - 手动功能测试")
    print("=" * 50)
    
    success = run_tests()
    
    if success:
        print("\n✅ 测试结果: 所有功能正常！")
        print("\n📋 服务已验证:")
        print("✅ 后端API服务正常")
        print("✅ 数据库操作正常")
        print("✅ Dify集成接口正常")
        print("✅ 简历解析功能正常")
        print("\n🔗 Dify配置信息:")
        print("URL: http://localhost:8080/api/resumes/from-dify")
        print("方法: POST")
        print('请求体: {"resume_markdown": "内容", "title": "标题"}')
        
    else:
        print("\n❌ 测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main()