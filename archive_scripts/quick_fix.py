#!/usr/bin/env python3
"""快速修复Dify连接问题"""

import subprocess
import json
import socket

def get_host_ip():
    """获取宿主机IP地址"""
    try:
        # 获取连接到8.8.8.8时使用的本地IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "10.165.129.118"  # 备用IP

def test_all_endpoints():
    """测试所有可能的端点"""
    host_ip = get_host_ip()
    
    print("🔍 测试所有可能的Dify连接方式...")
    print("=" * 50)
    
    endpoints = [
        ("宿主机IP", f"http://{host_ip}:8080/api/resumes/from-dify"),
        ("localhost", "http://localhost:8080/api/resumes/from-dify"),
        ("127.0.0.1", "http://127.0.0.1:8080/api/resumes/from-dify"),
    ]
    
    test_data = {
        "resume_markdown": "# 连接测试\n\n## 测试信息\n- 这是一个连接测试",
        "title": "连接测试"
    }
    
    successful_endpoints = []
    
    # 本地测试
    print("📍 本地连接测试:")
    for name, url in endpoints:
        try:
            cmd = [
                "curl", "-s", "-X", "POST",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(test_data),
                "-w", "HTTP:%{http_code}",
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and "HTTP:201" in result.stdout:
                print(f"   ✅ {name}: 成功")
                successful_endpoints.append((name, url))
            else:
                print(f"   ❌ {name}: 失败")
        except:
            print(f"   ❌ {name}: 超时")
    
    # Docker测试
    print(f"\n🐳 Docker容器测试:")
    docker_endpoints = [
        ("host.docker.internal", "http://host.docker.internal:8080/api/resumes/from-dify"),
        ("宿主机IP", f"http://{host_ip}:8080/api/resumes/from-dify"),
        ("Docker网关", "http://172.17.0.1:8080/api/resumes/from-dify"),
    ]
    
    for name, url in docker_endpoints:
        try:
            cmd = [
                "docker", "run", "--rm",
                "curlimages/curl:latest",
                "curl", "-s", "-X", "POST",
                "-H", "Content-Type: application/json",
                "-w", "HTTP:%{http_code}",
                "--data-raw", json.dumps(test_data),
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if result.returncode == 0 and "HTTP:201" in result.stdout:
                print(f"   ✅ {name}: 成功")
                successful_endpoints.append((f"Docker-{name}", url))
            else:
                print(f"   ❌ {name}: 失败")
        except:
            print(f"   ❌ {name}: 超时")
    
    return successful_endpoints, host_ip

def provide_final_solutions(successful_endpoints, host_ip):
    """提供最终解决方案"""
    print("\n" + "=" * 50)
    print("🎯 Dify配置解决方案")
    print("=" * 50)
    
    if successful_endpoints:
        print("✅ 以下连接方式已测试成功:")
        for i, (name, url) in enumerate(successful_endpoints, 1):
            print(f"{i}. {name}: {url}")
        
        # 推荐最佳方案
        docker_endpoints = [ep for ep in successful_endpoints if "Docker" in ep[0]]
        if docker_endpoints:
            recommended = docker_endpoints[0][1]
            print(f"\n🏆 推荐使用: {recommended}")
        else:
            recommended = f"http://{host_ip}:8080/api/resumes/from-dify"
            print(f"\n🏆 推荐使用: {recommended}")
    else:
        recommended = f"http://{host_ip}:8080/api/resumes/from-dify"
        print(f"⚠️ 自动测试未完全成功，建议手动尝试: {recommended}")
    
    print(f"\n📋 完整的Dify HTTP节点配置:")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"方法: POST")
    print(f"URL: {recommended}")
    print(f"请求头:")
    print(f"  Content-Type: application/json")
    print(f"请求体:")
    print(f'''{{
  "resume_markdown": "{{{{LLM生成的简历内容}}}}",
  "title": "{{{{简历标题}}}}"
}}''')
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    print(f"\n🔧 故障排除建议:")
    print(f"1. 如果仍然失败，尝试增加Dify的超时时间到30秒")
    print(f"2. 检查Dify的重试设置，建议设为0或1次")
    print(f"3. 确认Dify和简历编辑器都在运行")
    print(f"4. 尝试备选URL: http://localhost:8080/api/resumes/from-dify")

def main():
    print("🚀 Dify连接问题快速修复工具")
    print("=" * 50)
    
    # 检查后端服务状态
    try:
        result = subprocess.run([
            "curl", "-s", "http://localhost:8080/api/health"
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ 后端服务正常运行")
        else:
            print("❌ 后端服务未响应，请先启动后端服务")
            return
    except:
        print("❌ 无法连接到后端服务，请检查服务状态")
        return
    
    # 测试所有端点
    successful_endpoints, host_ip = test_all_endpoints()
    
    # 提供解决方案
    provide_final_solutions(successful_endpoints, host_ip)

if __name__ == "__main__":
    main()