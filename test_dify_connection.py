#!/usr/bin/env python3
"""测试Dify连接的脚本"""

import subprocess
import json

def test_dify_connection():
    print("🧪 测试Dify到简历编辑器的连接...")
    
    # 测试数据
    test_data = {
        "resume_markdown": """# 李四

## 个人信息
- 邮箱: lisi@example.com
- 电话: 13900139000
- 地址: 上海市浦东新区

## 工作经验

### 前端工程师 | XYZ科技公司 | 2021-2024
- 负责React应用开发
- 参与组件库建设
- 优化前端性能

## 技能
- React, Vue, JavaScript
- HTML5, CSS3, TypeScript
- Webpack, Vite
""",
        "title": "李四的简历"
    }
    
    urls_to_test = [
        "http://localhost:8080/api/resumes/from-dify",  # 本地测试
        "http://host.docker.internal:8080/api/resumes/from-dify",  # Docker推荐
        "http://10.165.129.118:8080/api/resumes/from-dify"  # IP地址
    ]
    
    for url in urls_to_test:
        print(f"\n🔗 测试URL: {url}")
        
        try:
            # 使用Docker容器模拟Dify环境
            if "host.docker.internal" in url or "10.165.129.118" in url:
                cmd = [
                    "docker", "run", "--rm",
                    "curlimages/curl:latest",
                    "curl", "-s", "-X", "POST",
                    "-H", "Content-Type: application/json",
                    "-d", json.dumps(test_data),
                    url
                ]
            else:
                # 本地测试
                cmd = [
                    "curl", "-s", "-X", "POST",
                    "-H", "Content-Type: application/json",
                    "-d", json.dumps(test_data),
                    url
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                try:
                    response = json.loads(result.stdout)
                    if response.get('success'):
                        print(f"✅ 连接成功！简历ID: {response.get('resume_id')}")
                        if "host.docker.internal" in url:
                            print("🎯 推荐在Dify中使用此URL!")
                    else:
                        print(f"❌ 请求失败: {response.get('error', '未知错误')}")
                except json.JSONDecodeError:
                    print(f"❌ 响应格式错误: {result.stdout}")
            else:
                print(f"❌ 连接失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_dify_connection()
    
    print("\n" + "="*60)
    print("📋 Dify配置建议:")
    print("URL: http://host.docker.internal:8080/api/resumes/from-dify")
    print("方法: POST")
    print("请求头: Content-Type: application/json")
    print("请求体: {\"resume_markdown\": \"{{LLM输出}}\", \"title\": \"简历标题\"}")
    print("="*60)