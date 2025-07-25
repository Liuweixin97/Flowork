#!/usr/bin/env python3
"""Dify连接调试工具"""

import subprocess
import json
import time
import socket

def check_port_availability(host, port):
    """检查端口是否可访问"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def test_endpoints():
    """测试各种访问方式"""
    print("🔍 诊断Dify连接问题...")
    print("=" * 60)
    
    # 测试数据
    test_data = {
        "resume_markdown": "# 测试简历\n\n## 个人信息\n- 测试数据",
        "title": "Dify测试简历"
    }
    
    endpoints = [
        ("本机localhost", "http://localhost:8080/api/resumes/from-dify"),
        ("本机127.0.0.1", "http://127.0.0.1:8080/api/resumes/from-dify"),
        ("本机IP", "http://10.165.129.118:8080/api/resumes/from-dify"),
    ]
    
    # 1. 检查端口
    print("1️⃣ 检查端口可访问性:")
    hosts_to_check = [
        ("localhost", 8080),
        ("127.0.0.1", 8080),
        ("10.165.129.118", 8080)
    ]
    
    for host, port in hosts_to_check:
        accessible = check_port_availability(host, port)
        status = "✅ 可访问" if accessible else "❌ 不可访问"
        print(f"   {host}:{port} - {status}")
    
    print("\n2️⃣ 测试HTTP请求:")
    
    for name, url in endpoints:
        print(f"\n🔗 测试 {name}: {url}")
        
        try:
            cmd = [
                "curl", "-s", "-X", "POST",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(test_data),
                "-w", "HTTP:%{http_code}|Time:%{time_total}s",
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                # 分离响应和状态信息
                output = result.stdout
                if "|" in output:
                    response_part, status_part = output.rsplit("|", 1)
                    status_info = status_part.split("|")
                    
                    print(f"   状态: {status_info[0] if status_info else 'Unknown'}")
                    print(f"   响应时间: {status_info[1] if len(status_info) > 1 else 'Unknown'}")
                    
                    try:
                        response_json = json.loads(response_part)
                        if response_json.get('success'):
                            print(f"   ✅ 成功! 简历ID: {response_json.get('resume_id')}")
                        else:
                            print(f"   ❌ 失败: {response_json.get('error', '未知错误')}")
                    except json.JSONDecodeError:
                        print(f"   📝 响应: {response_part[:100]}...")
                else:
                    print(f"   📝 原始响应: {output}")
                    
            else:
                print(f"   ❌ 请求失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("   ❌ 请求超时 (15秒)")
        except Exception as e:
            print(f"   ❌ 异常: {e}")
    
    # 3. 测试Docker内访问
    print(f"\n3️⃣ 测试Docker容器内访问:")
    docker_urls = [
        ("host.docker.internal", "http://host.docker.internal:8080/api/resumes/from-dify"),
        ("Gateway IP", "http://172.17.0.1:8080/api/resumes/from-dify")
    ]
    
    for name, url in docker_urls:
        print(f"\n🐳 Docker测试 {name}: {url}")
        
        try:
            cmd = [
                "docker", "run", "--rm", 
                "curlimages/curl:latest",
                "curl", "-s", "-X", "POST",
                "-H", "Content-Type: application/json",
                "--data-raw", json.dumps(test_data),
                "-w", "HTTP:%{http_code}|Time:%{time_total}s",
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                output = result.stdout
                if "|" in output:
                    response_part, status_part = output.rsplit("|", 1)
                    status_info = status_part.split("|")
                    
                    print(f"   状态: {status_info[0] if status_info else 'Unknown'}")
                    print(f"   响应时间: {status_info[1] if len(status_info) > 1 else 'Unknown'}")
                    
                    try:
                        response_json = json.loads(response_part)
                        if response_json.get('success'):
                            print(f"   ✅ 成功! 简历ID: {response_json.get('resume_id')}")
                        else:
                            print(f"   ❌ 失败: {response_json.get('error', '未知错误')}")
                    except json.JSONDecodeError:
                        print(f"   📝 响应: {response_part[:100]}...")
                else:
                    print(f"   📝 原始响应: {output}")
            else:
                print(f"   ❌ 请求失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("   ❌ 请求超时 (30秒)")
        except Exception as e:
            print(f"   ❌ 异常: {e}")

def main():
    test_endpoints()
    
    print("\n" + "=" * 60)
    print("📋 Dify配置建议:")
    print("\n如果Docker内测试成功，在Dify中使用:")
    print("URL: http://host.docker.internal:8080/api/resumes/from-dify")
    print("\n如果本机IP测试成功，在Dify中使用:")
    print("URL: http://10.165.129.118:8080/api/resumes/from-dify")
    print("\n通用配置:")
    print("方法: POST")
    print("请求头: Content-Type: application/json")
    print('请求体: {"resume_markdown": "{{LLM输出}}", "title": "简历标题"}')
    print("=" * 60)

if __name__ == "__main__":
    main()