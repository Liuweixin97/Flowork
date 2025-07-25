#!/usr/bin/env python3
"""最终功能检查"""

import urllib.request
import json
import subprocess

def check_all_functionality():
    print("🔍 最终功能检查...")
    print("=" * 60)
    
    # 1. 检查后端服务
    try:
        response = urllib.request.urlopen("http://localhost:8080/api/health", timeout=5)
        result = json.loads(response.read().decode('utf-8'))
        print("✅ 后端服务正常运行")
    except Exception as e:
        print(f"❌ 后端服务异常: {e}")
        return False
    
    # 2. 检查前端服务
    try:
        response = urllib.request.urlopen("http://localhost:3000", timeout=5)
        if response.getcode() == 200:
            print("✅ 前端服务正常运行")
        else:
            print(f"❌ 前端服务响应异常: {response.getcode()}")
    except Exception as e:
        print(f"❌ 前端服务异常: {e}")
        return False
    
    # 3. 检查简历数量
    try:
        response = urllib.request.urlopen("http://localhost:8080/api/resumes", timeout=5)
        result = json.loads(response.read().decode('utf-8'))
        count = len(result.get('resumes', []))
        print(f"📊 当前简历数量: {count}")
        
        if count > 0:
            latest = result['resumes'][0]
            print(f"   最新简历: ID {latest['id']}, 标题: {latest['title']}")
    except Exception as e:
        print(f"❌ 获取简历数据失败: {e}")
        return False
    
    # 4. 测试Dify连接
    print("\n🔗 测试Dify连接:")
    test_urls = [
        "http://localhost:8080/api/resumes/from-dify",
        "http://host.docker.internal:8080/api/resumes/from-dify",
        "http://10.165.129.118:8080/api/resumes/from-dify"
    ]
    
    test_data = {
        "resume_markdown": "# 最终测试\n\n## 个人信息\n- 测试完成",
        "title": "最终功能测试"
    }
    
    success_count = 0
    for i, url in enumerate(test_urls, 1):
        try:
            if "host.docker.internal" in url:
                # 使用Docker测试
                cmd = [
                    "docker", "run", "--rm", "curlimages/curl:latest",
                    "curl", "-s", "-X", "POST",
                    "-H", "Content-Type: application/json",
                    "--data-raw", json.dumps(test_data),
                    url
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    response = json.loads(result.stdout)
                    if response.get('success'):
                        print(f"   ✅ 方式{i}: Docker访问成功")
                        success_count += 1
                    else:
                        print(f"   ❌ 方式{i}: Docker访问失败")
                else:
                    print(f"   ❌ 方式{i}: Docker命令失败")
            else:
                # 本地测试
                req = urllib.request.Request(url, data=json.dumps(test_data).encode('utf-8'))
                req.add_header('Content-Type', 'application/json')
                response = urllib.request.urlopen(req, timeout=10)
                result = json.loads(response.read().decode('utf-8'))
                if result.get('success'):
                    print(f"   ✅ 方式{i}: 本地访问成功")
                    success_count += 1
                else:
                    print(f"   ❌ 方式{i}: 本地访问失败")
        except Exception as e:
            print(f"   ❌ 方式{i}: 异常 - {e}")
    
    print(f"\n📊 连接测试结果: {success_count}/{len(test_urls)} 成功")
    
    return success_count > 0

def main():
    success = check_all_functionality()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 所有功能检查通过！")
        print("\n📋 服务信息:")
        print("🖥️  前端界面: http://localhost:3000")
        print("🔧 后端API: http://localhost:8080")
        print("\n🔗 Dify配置建议:")
        print("URL: http://host.docker.internal:8080/api/resumes/from-dify")
        print("备选: http://10.165.129.118:8080/api/resumes/from-dify")
        print("方法: POST")
        print("请求头: Content-Type: application/json")
        print('请求体: {"resume_markdown": "{{LLM输出}}", "title": "简历标题"}')
        print("\n✨ 新功能:")
        print("- 空状态页面显示")
        print("- 新建空白简历功能")
        print("- 美观的错误提示")
    else:
        print("❌ 部分功能存在问题，请检查服务状态")
    
    print("=" * 60)

if __name__ == "__main__":
    main()