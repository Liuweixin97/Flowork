#!/usr/bin/env python3
"""
测试Dify HTTP节点向简历编辑器发送请求的脚本
用于诊断为什么Dify工作流HTTP请求失败
"""

import requests
import json
import os
from datetime import datetime

# 配置
BACKEND_URL = "http://localhost:8080"
FRONTEND_URL = "http://localhost:3000"

def test_from_dify_endpoint():
    """测试 /api/resumes/from-dify 端点"""
    print("=" * 60)
    print("测试 Dify HTTP 节点 -> 简历编辑器集成")
    print("=" * 60)
    
    # 测试用的简历内容
    test_resume_markdown = """# 李明的简历

## 个人信息
- **姓名**: 李明
- **邮箱**: liming@example.com  
- **电话**: 138-1234-5678
- **地址**: 上海市浦东新区
- **GitHub**: https://github.com/liming

## 工作经验

### 高级软件工程师 | 上海科技公司 | 2021.01 - 至今
- 负责核心产品后端开发，使用Python/Django技术栈
- 主导微服务架构重构，提升系统性能40%
- 带领5人开发团队，建立代码规范和CI/CD流程

### 软件工程师 | 北京互联网公司 | 2019.06 - 2020.12
- 参与多个Web应用开发和维护
- 使用React/Node.js技术栈开发前后端应用
- 优化数据库查询性能，减少响应时间50%

## 教育背景

### 计算机科学与技术学士 | 清华大学 | 2015.09 - 2019.06
- **主修课程**: 数据结构、算法设计、软件工程
- **GPA**: 3.7/4.0

## 技能特长
- **编程语言**: Python, JavaScript, Java, Go
- **框架技术**: Django, Flask, React, Vue.js
- **数据库**: MySQL, PostgreSQL, Redis, MongoDB
- **工具平台**: Git, Docker, Kubernetes, AWS

## 项目经验

### 企业级ERP系统 | 2022.03 - 2022.11
- **项目描述**: 为制造业企业提供全流程管理的ERP系统
- **技术栈**: Python, Django, PostgreSQL, Redis, Docker
- **个人贡献**: 
  - 设计和开发订单管理模块
  - 实现复杂的库存管理算法
  - 搭建微服务架构和API网关

### 智能客服聊天机器人 | 2021.08 - 2022.02  
- **项目描述**: 基于NLP技术的智能客服系统
- **技术栈**: Python, FastAPI, TensorFlow, MySQL
- **个人贡献**:
  - 训练和优化自然语言处理模型
  - 开发对话管理和意图识别系统
  - 集成第三方API和消息平台

## 获奖荣誉
- 2022年度公司"技术创新奖"
- 2021年"全国程序设计大赛"一等奖

## 自我评价
拥有扎实的计算机基础和丰富的项目经验，熟悉多种编程语言和技术栈。具备良好的团队协作能力和学习能力，能够快速适应新技术和业务需求。对代码质量和用户体验有较高要求。
"""

    # 测试多种请求格式
    test_cases = [
        {
            "name": "标准Dify HTTP节点格式",
            "data": {
                "resume_markdown": test_resume_markdown,
                "title": "浩流简历·flowork生成的简历 - 李明"
            },
            "headers": {
                "Content-Type": "application/json",
                "User-Agent": "Dify-HTTP-Node/1.0"
            }
        },
        {
            "name": "包含用户ID的格式",
            "data": {
                "resume_markdown": test_resume_markdown,
                "title": "浩流简历·flowork生成的简历 - 李明",
                "user_id": "demo-user-123"
            },
            "headers": {
                "Content-Type": "application/json",
                "User-Agent": "Dify-HTTP-Node/1.0"
            }
        },
        {
            "name": "带认证token的格式",
            "data": {
                "resume_markdown": test_resume_markdown,
                "title": "浩流简历·flowork生成的简历 - 李明"
            },
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer test-token-123",
                "User-Agent": "Dify-HTTP-Node/1.0"
            }
        },
        {
            "name": "不同字段名格式 (content)",
            "data": {
                "content": test_resume_markdown,
                "title": "浩流简历·flowork生成的简历 - 李明"
            },
            "headers": {
                "Content-Type": "application/json",
                "User-Agent": "Dify-HTTP-Node/1.0"
            }
        },
        {
            "name": "不同字段名格式 (markdown)",
            "data": {
                "markdown": test_resume_markdown,
                "title": "浩流简历·flowork生成的简历 - 李明"
            },
            "headers": {
                "Content-Type": "application/json",
                "User-Agent": "Dify-HTTP-Node/1.0"
            }
        }
    ]
    
    endpoint_url = f"{BACKEND_URL}/api/resumes/from-dify"
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试: {test_case['name']}")
        print("-" * 40)
        
        try:
            response = requests.post(
                endpoint_url,
                json=test_case['data'],
                headers=test_case['headers'],
                timeout=30
            )
            
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                
                if response.status_code == 201 and response_data.get('success'):
                    print("✅ 请求成功！")
                    resume_id = response_data.get('resume_id')
                    if resume_id:
                        print(f"📝 简历ID: {resume_id}")
                        edit_url = response_data.get('edit_url', f'/edit/{resume_id}')
                        print(f"🔗 编辑链接: {FRONTEND_URL}{edit_url}")
                else:
                    print("❌ 请求失败")
                    
            except json.JSONDecodeError:
                print(f"响应内容 (非JSON): {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络错误: {e}")
        
        print()

def test_backend_health():
    """测试后端健康状态"""
    print("检查后端服务状态...")
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 后端服务正常运行")
            print(f"   服务: {health_data.get('service')}")
            print(f"   版本: {health_data.get('version')}")
            print(f"   状态: {health_data.get('status')}")
            return True
        else:
            print(f"❌ 后端服务异常: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接后端服务: {e}")
        return False

def test_cors():
    """测试CORS配置"""
    print("\n检查CORS配置...")
    
    try:
        # 发送OPTIONS预检请求
        response = requests.options(
            f"{BACKEND_URL}/api/resumes/from-dify",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=10
        )
        
        print(f"OPTIONS请求状态码: {response.status_code}")
        cors_headers = {
            k: v for k, v in response.headers.items() 
            if k.lower().startswith('access-control')
        }
        print(f"CORS响应头: {cors_headers}")
        
        if 'access-control-allow-origin' in cors_headers:
            print("✅ CORS配置正常")
        else:
            print("❌ CORS配置可能有问题")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS检查失败: {e}")

def check_backend_logs():
    """提示检查后端日志"""
    print("\n" + "=" * 60)
    print("后端日志检查建议")
    print("=" * 60)
    print("请在后端终端查看详细日志，重点关注:")
    print("1. [DIFY] 开头的请求日志")
    print("2. JSON解析错误")
    print("3. 认证相关错误") 
    print("4. 数据库连接错误")
    print("5. CORS相关错误")
    print("\n如果使用Docker，可以用以下命令查看日志:")
    print("docker-compose logs -f backend")
    print("\n如果直接运行Python，请检查控制台输出")

def analyze_potential_issues():
    """分析潜在问题"""
    print("\n" + "=" * 60)
    print("潜在问题分析")
    print("=" * 60)
    
    issues = [
        "1. **认证问题**: Dify HTTP节点可能没有发送JWT token，但端点需要认证",
        "2. **请求格式**: Dify发送的JSON格式可能与后端期望的不匹配",
        "3. **CORS配置**: 跨域请求可能被阻止",
        "4. **网络连接**: Dify无法访问后端端点URL",
        "5. **超时问题**: 请求超时导致失败",
        "6. **内容长度**: 请求体太大被服务器拒绝",
        "7. **HTTP方法**: 可能使用了错误的HTTP方法",
        "8. **Content-Type**: 请求头设置不正确"
    ]
    
    for issue in issues:
        print(issue)
    
    print("\n建议解决步骤:")
    print("1. 检查后端日志确定具体错误")
    print("2. 确认Dify HTTP节点配置的URL正确")
    print("3. 检查Dify HTTP节点的请求格式")
    print("4. 验证网络连通性")
    print("5. 考虑在/api/resumes/from-dify端点添加更详细的错误日志")

if __name__ == "__main__":
    print("Dify HTTP节点集成诊断工具")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 检查后端健康状态
    if not test_backend_health():
        print("\n❌ 后端服务不可用，请先启动后端服务")
        exit(1)
    
    # 2. 测试CORS
    test_cors()
    
    # 3. 测试from-dify端点
    test_from_dify_endpoint()
    
    # 4. 分析潜在问题
    analyze_potential_issues()
    
    # 5. 日志检查建议
    check_backend_logs()
    
    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)
    print("请根据上述测试结果和建议进行问题排查")