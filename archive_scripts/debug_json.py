#!/usr/bin/env python3
"""调试JSON解析问题"""

import subprocess
import json
import urllib.request
import urllib.parse

def test_json_variations():
    """测试各种JSON格式"""
    print("🔍 测试JSON解析问题...")
    print("=" * 60)
    
    # 各种可能的JSON格式
    test_cases = [
        {
            "name": "标准格式",
            "data": {
                "resume_markdown": "# 测试简历\n\n## 个人信息\n- 姓名: 测试用户",
                "title": "JSON测试"
            }
        },
        {
            "name": "带转义字符",
            "data": {
                "resume_markdown": "# 测试简历\\n\\n## 个人信息\\n- 姓名: 测试用户",
                "title": "转义测试"
            }
        },
        {
            "name": "包含特殊字符",
            "data": {
                "resume_markdown": "# 测试简历 🔁 LLM/(✏️text)\n\n## 个人信息\n- 姓名: 测试用户",
                "title": "特殊字符测试"
            }
        },
        {
            "name": "空内容",
            "data": {
                "resume_markdown": "",
                "title": "空内容测试"
            }
        },
        {
            "name": "模拟Dify格式1",
            "data": {
                "resume_markdown": "🔁 LLM/(✏️text)",
                "title": "测试0721"
            }
        },
        {
            "name": "模拟Dify格式2(添加其他字段)",
            "data": {
                "resume_markdown": "🔁 LLM/(✏️text)",
                "title": "测试0721",
                "timestamp": "2025-07-21",
                "source": "dify"
            }
        }
    ]
    
    base_url = "http://localhost:8080/api/resumes/from-dify"
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ 测试: {test_case['name']}")
        
        try:
            # 准备数据
            json_data = json.dumps(test_case['data'], ensure_ascii=False)
            print(f"   📤 发送数据: {json_data}")
            
            # 发送请求
            req = urllib.request.Request(
                base_url,
                data=json_data.encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            response = urllib.request.urlopen(req, timeout=10)
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('success'):
                print(f"   ✅ 成功: 简历ID {result.get('resume_id')}")
            else:
                print(f"   ❌ 失败: {result.get('error')}")
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f"   ❌ HTTP错误 {e.code}: {error_body}")
        except Exception as e:
            print(f"   ❌ 异常: {e}")

def test_docker_json():
    """测试Docker环境下的JSON解析"""
    print(f"\n🐳 Docker环境JSON测试...")
    
    test_data = {
        "resume_markdown": "🔁 LLM/(✏️text)",
        "title": "Docker JSON测试"
    }
    
    # 测试不同的Docker网络访问方式
    urls = [
        "http://host.docker.internal:8080/api/resumes/from-dify",
        "http://172.20.0.1:8080/api/resumes/from-dify",  # Dify网络网关
        "http://10.165.129.118:8080/api/resumes/from-dify"  # 本机IP
    ]
    
    for url in urls:
        print(f"\n🔗 测试URL: {url}")
        
        try:
            # 使用Docker容器发送请求
            cmd = [
                "docker", "run", "--rm", "--network", "dify_default",
                "curlimages/curl:latest",
                "curl", "-v", "-X", "POST",
                "-H", "Content-Type: application/json",
                "-H", "Accept: application/json",
                "--connect-timeout", "15",
                "--max-time", "30",
                "--data-raw", json.dumps(test_data, ensure_ascii=False),
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
            
            print(f"   返回码: {result.returncode}")
            if result.returncode == 0:
                # 尝试提取JSON响应
                lines = result.stdout.strip().split('\n')
                json_line = None
                for line in reversed(lines):
                    if line.strip().startswith('{'):
                        json_line = line.strip()
                        break
                
                if json_line:
                    try:
                        response = json.loads(json_line)
                        if response.get('success'):
                            print(f"   ✅ 成功: {response.get('message')}")
                        else:
                            print(f"   ❌ 失败: {response.get('error')}")
                    except json.JSONDecodeError:
                        print(f"   📝 原始响应: {json_line}")
                else:
                    print(f"   📝 完整输出: {result.stdout[-200:]}")
            else:
                print(f"   ❌ 错误: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("   ⏰ 超时")
        except Exception as e:
            print(f"   ❌ 异常: {e}")

def check_backend_logs():
    """检查后端日志以获取更多信息"""
    print(f"\n📋 后端日志检查建议:")
    print("请查看后端控制台输出，寻找 [DIFY] 标记的日志")
    print("这些日志会显示:")
    print("- 接收到的原始数据")
    print("- JSON解析过程")
    print("- 具体的错误信息")

def main():
    print("🚨 JSON解析问题调试工具")
    print("=" * 60)
    
    # 1. 测试本地JSON解析
    test_json_variations()
    
    # 2. 测试Docker环境
    test_docker_json()
    
    # 3. 检查日志建议
    check_backend_logs()
    
    print("\n" + "=" * 60)
    print("💡 可能的解决方案:")
    print("1. 检查Dify发送的JSON格式是否正确")
    print("2. 确认Content-Type设置为application/json")
    print("3. 检查是否有特殊字符导致编码问题")
    print("4. 尝试使用IP地址替代host.docker.internal")
    print("5. 增加Dify的请求超时时间")
    print("=" * 60)

if __name__ == "__main__":
    main()