#!/usr/bin/env python3
"""Dify集成修复工具"""

import subprocess
import json
import time

def create_dify_compatible_service():
    """创建与Dify兼容的服务"""
    print("🔧 创建Dify兼容服务...")
    
    # 1. 停止现有的后端服务
    print("1️⃣ 停止现有后端服务...")
    try:
        subprocess.run(["pkill", "-f", "python.*app.py"], check=False)
        time.sleep(2)
    except:
        pass
    
    # 2. 在Dify网络中启动容器化后端
    print("2️⃣ 启动容器化后端服务...")
    
    dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY backend/ .

# 暴露端口
EXPOSE 8080

# 启动服务
CMD ["python", "app.py"]
'''
    
    # 创建Dockerfile
    with open("/Users/liuweixin/Desktop/MyProjects/resume-editor/Dockerfile.backend", "w") as f:
        f.write(dockerfile_content)
    
    # 构建镜像
    build_cmd = [
        "docker", "build", 
        "-f", "Dockerfile.backend",
        "-t", "resume-editor-backend",
        "."
    ]
    
    try:
        result = subprocess.run(build_cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("   ✅ 镜像构建成功")
        else:
            print(f"   ❌ 镜像构建失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("   ⏰ 构建超时")
        return False
    except Exception as e:
        print(f"   ❌ 构建异常: {e}")
        return False
    
    # 3. 在Dify网络中运行容器
    print("3️⃣ 在Dify网络中启动容器...")
    
    run_cmd = [
        "docker", "run", "-d",
        "--name", "resume-editor-backend",
        "--network", "dify_default",
        "-p", "8080:8080",
        "--restart", "unless-stopped",
        "resume-editor-backend"
    ]
    
    try:
        # 先删除可能存在的容器
        subprocess.run(["docker", "rm", "-f", "resume-editor-backend"], capture_output=True)
        
        result = subprocess.run(run_cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("   ✅ 容器启动成功")
            container_id = result.stdout.strip()
            print(f"   📦 容器ID: {container_id[:12]}")
            return True
        else:
            print(f"   ❌ 容器启动失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ 容器启动异常: {e}")
        return False

def test_dify_network_access():
    """测试Dify网络内访问"""
    print("\n🧪 测试Dify网络内访问...")
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(10)
    
    # 从Dify网络内测试访问
    test_data = {
        "resume_markdown": "# Dify网络测试\n\n## 测试内容\n- 网络连接测试",
        "title": "Dify网络测试"
    }
    
    # 获取容器IP
    get_ip_cmd = [
        "docker", "inspect", "resume-editor-backend",
        "--format", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"
    ]
    
    try:
        result = subprocess.run(get_ip_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            container_ip = result.stdout.strip()
            print(f"📍 容器IP: {container_ip}")
            
            # 从Dify网络内测试访问容器IP
            test_cmd = [
                "docker", "run", "--rm", "--network", "dify_default",
                "curlimages/curl:latest",
                "curl", "-s", "-X", "POST",
                "-H", "Content-Type: application/json",
                "--data-raw", json.dumps(test_data),
                f"http://{container_ip}:8080/api/resumes/from-dify"
            ]
            
            result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    if response.get('success'):
                        print("   ✅ Dify网络内访问成功!")
                        return container_ip
                    else:
                        print(f"   ❌ 服务返回错误: {response.get('error')}")
                except json.JSONDecodeError:
                    print(f"   📝 原始响应: {result.stdout}")
            else:
                print(f"   ❌ 网络访问失败: {result.stderr}")
                
    except Exception as e:
        print(f"   ❌ 测试异常: {e}")
    
    return None

def provide_solutions():
    """提供解决方案"""
    print("\n" + "=" * 60)
    print("🎯 Dify连接解决方案")
    print("=" * 60)
    
    container_ip = test_dify_network_access()
    
    if container_ip:
        print(f"\n✅ 推荐配置 (容器IP):")
        print(f"URL: http://{container_ip}:8080/api/resumes/from-dify")
    
    print(f"\n🔄 备选配置:")
    print("1. host.docker.internal (如果支持):")
    print("   URL: http://host.docker.internal:8080/api/resumes/from-dify")
    
    print("\n2. 宿主机IP:")
    print("   URL: http://10.165.129.118:8080/api/resumes/from-dify")
    
    print("\n3. localhost (仅限本机测试):")
    print("   URL: http://localhost:8080/api/resumes/from-dify")
    
    print("\n📋 通用配置:")
    print("方法: POST")
    print("请求头: Content-Type: application/json")
    print("请求体:")
    print('''{
  "resume_markdown": "{{LLM生成的简历内容}}",
  "title": "{{简历标题}}"
}''')
    
    print("\n🔍 如果仍然失败，请检查:")
    print("1. Dify的网络模式设置")
    print("2. Docker的host.docker.internal支持")
    print("3. Dify的超时设置 (建议30秒以上)")
    print("4. Dify的重试次数设置")

def fallback_solution():
    """备用解决方案：使用宿主机模式"""
    print("\n🚀 备用解决方案：宿主机网络模式")
    
    # 停止容器版本
    subprocess.run(["docker", "stop", "resume-editor-backend"], capture_output=True)
    subprocess.run(["docker", "rm", "resume-editor-backend"], capture_output=True)
    
    # 启动宿主机网络模式的容器
    run_cmd = [
        "docker", "run", "-d",
        "--name", "resume-editor-backend-host",
        "--network", "host",
        "--restart", "unless-stopped",
        "resume-editor-backend"
    ]
    
    try:
        result = subprocess.run(run_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 宿主机网络模式启动成功")
            print("🔗 Dify配置URL: http://localhost:8080/api/resumes/from-dify")
            return True
        else:
            print(f"❌ 启动失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

def main():
    print("🔧 Dify集成修复工具")
    print("=" * 60)
    
    # 检查Docker环境
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True)
        if result.returncode != 0:
            print("❌ Docker未安装或未启动")
            return
    except:
        print("❌ Docker命令不可用")
        return
    
    # 尝试容器化解决方案
    if create_dify_compatible_service():
        provide_solutions()
    else:
        print("\n⚠️ 容器化方案失败，尝试备用方案...")
        if fallback_solution():
            print("✅ 备用方案启动成功")
        else:
            print("❌ 所有自动方案都失败了")
            print("\n🛠️ 手动解决步骤:")
            print("1. 确保后端服务在8080端口运行")
            print("2. 在Dify中使用: http://10.165.129.118:8080/api/resumes/from-dify")
            print("3. 检查防火墙和网络设置")

if __name__ == "__main__":
    main()