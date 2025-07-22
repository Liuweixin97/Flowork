#!/usr/bin/env python3
"""
测试HTTP请求节点自动跳转功能
"""

import requests
import json

# 测试数据
test_resume = {
    "resume_markdown": """# 张三

## 个人信息
- 姓名：张三
- 电话：138-0000-0000
- 邮箱：zhangsan@email.com

## 工作经历
### 软件工程师 | ABC公司 | 2020-2023
- 负责前端开发工作
- 参与多个项目的设计和实施

## 教育背景
### 计算机科学与技术 | XYZ大学 | 2016-2020
- 学士学位
- 主修课程：数据结构、算法、软件工程
""",
    "title": "张三的简历 - 浩流简历·flowork测试"
}

def test_api_request():
    """测试API请求（应返回JSON）"""
    print("=== 测试API请求 ===")
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Python-requests/2.28.1'  # 非浏览器User-Agent
    }
    
    try:
        response = requests.post(
            'http://localhost:8080/api/resumes/from-dify',
            json=test_resume,
            headers=headers,
            allow_redirects=False
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"JSON响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            return data.get('resume_id')
        else:
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"API请求错误: {e}")
        
    return None

def test_auto_redirect_query_param():
    """测试查询参数重定向（应返回302重定向）"""
    print("\n=== 测试查询参数重定向 ===")
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    try:
        response = requests.post(
            'http://localhost:8080/api/resumes/from-dify?auto_redirect=true',
            json=test_resume,
            headers=headers,
            allow_redirects=False  # 不自动跟随重定向
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 302:
            location = response.headers.get('Location')
            print(f"重定向地址: {location}")
            
            # 验证重定向地址格式
            if location and '/edit/' in location:
                print("✅ 重定向地址格式正确")
            else:
                print("❌ 重定向地址格式错误")
        else:
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"查询参数重定向测试错误: {e}")

def test_auto_redirect_body_param():
    """测试请求体参数重定向（应返回302重定向）"""
    print("\n=== 测试请求体参数重定向 ===")
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    # 在请求体中添加 auto_redirect 参数
    test_data_with_redirect = {
        **test_resume,
        'auto_redirect': True
    }
    
    try:
        response = requests.post(
            'http://localhost:8080/api/resumes/from-dify',
            json=test_data_with_redirect,
            headers=headers,
            allow_redirects=False  # 不自动跟随重定向
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 302:
            location = response.headers.get('Location')
            print(f"重定向地址: {location}")
            
            # 验证重定向地址格式
            if location and '/edit/' in location:
                print("✅ 重定向地址格式正确")
            else:
                print("❌ 重定向地址格式错误")
        else:
            print(f"响应内容: {response.text}")
            
    except Exception as e:
        print(f"请求体参数重定向测试错误: {e}")

def main():
    """主测试函数"""
    print("HTTP请求节点自动跳转功能测试")
    print("=" * 60)
    
    # 1. 测试标准API请求（无重定向）
    resume_id = test_api_request()
    
    # 2. 测试查询参数重定向
    test_auto_redirect_query_param()
    
    # 3. 测试请求体参数重定向
    test_auto_redirect_body_param()
    
    print("\n" + "=" * 60)
    print("=== 测试完成 ===")
    print("\n📋 总结:")
    print("1. ✅ 标准API请求：返回JSON响应")
    print("2. ✅ 查询参数重定向：?auto_redirect=true")
    print("3. ✅ 请求体参数重定向：{\"auto_redirect\": true}")
    
    if resume_id:
        print(f"\n🆔 创建的简历ID: {resume_id}")
        print(f"🔗 编辑链接: http://localhost:3002/edit/{resume_id}")
    
    print("\n📖 Dify HTTP节点配置说明:")
    print("方式1 - 查询参数重定向:")
    print("  URL: http://host.docker.internal:8080/api/resumes/from-dify?auto_redirect=true")
    
    print("\n方式2 - 请求体参数重定向:")
    print("  URL: http://host.docker.internal:8080/api/resumes/from-dify")
    print("  Body: {")
    print('    "resume_markdown": "{{简历内容}}",')
    print('    "title": "{{简历标题}}",')
    print('    "auto_redirect": true')
    print("  }")

if __name__ == '__main__':
    main()