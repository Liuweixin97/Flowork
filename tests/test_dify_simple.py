#!/usr/bin/env python3
"""简化的Dify测试"""

import subprocess
import json

def test_dify_exactly():
    """完全模拟Dify的请求"""
    print("🎯 模拟Dify的确切请求...")
    
    # 使用用户提供的确切数据
    test_data = {
        "resume_markdown": "🔁 LLM/(✏️text)",
        "title": "测试0721"
    }
    
    print(f"📤 发送数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    # 测试host.docker.internal (Dify使用的URL)
    cmd = [
        "docker", "run", "--rm",
        "-i",  # 交互模式
        "curlimages/curl:latest",
        "curl", 
        "-v",  # 详细输出
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-H", "Accept: application/json",
        "--connect-timeout", "10",
        "--max-time", "30",
        "--retry", "0",  # 不重试，模拟Dify
        "--data-raw", json.dumps(test_data),
        "http://host.docker.internal:8080/api/resumes/from-dify"
    ]
    
    print("🚀 执行命令:", " ".join(cmd[-8:]))  # 只显示关键部分
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        
        print(f"\n📊 结果:")
        print(f"   返回码: {result.returncode}")
        
        if result.returncode == 0:
            print("   ✅ 请求成功!")
            try:
                response = json.loads(result.stdout.split('\n')[-2])  # 获取最后的JSON响应
                print(f"   📄 响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
            except:
                print(f"   📄 原始响应: {result.stdout}")
        else:
            print("   ❌ 请求失败!")
            print(f"   错误输出: {result.stderr}")
            
        print(f"\n🔍 详细信息:")
        print(f"标准输出:\n{result.stdout}")
        if result.stderr:
            print(f"错误输出:\n{result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ 请求超时 (45秒)")
    except Exception as e:
        print(f"❌ 异常: {e}")

def check_response_time():
    """检查响应时间"""
    print("\n⏱️ 检查响应时间...")
    
    for i in range(3):
        cmd = [
            "curl", "-s", "-w", "%{time_total}s\\n",
            "-X", "POST",
            "-H", "Content-Type: application/json",
            "-d", '{"resume_markdown": "测试", "title": "时间测试"}',
            "http://localhost:8080/api/resumes/from-dify"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                time_taken = lines[-1] if lines else "未知"
                print(f"   第{i+1}次: {time_taken}")
            else:
                print(f"   第{i+1}次: 失败")
        except:
            print(f"   第{i+1}次: 超时")

if __name__ == "__main__":
    test_dify_exactly()
    check_response_time()
    
    print("\n" + "="*50)
    print("💡 如果测试成功但Dify仍然失败，可能的原因:")
    print("1. Dify的超时设置太短")
    print("2. Dify的网络配置问题")
    print("3. Dify容器无法访问host.docker.internal")
    print("4. 请尝试使用IP地址: http://10.165.129.118:8080/api/resumes/from-dify")
    print("="*50)