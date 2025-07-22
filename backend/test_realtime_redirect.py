#!/usr/bin/env python3
"""
测试实时自动跳转功能
模拟Dify HTTP节点发送请求，验证前端能否自动跳转
"""

import requests
import json
import time
import threading

# 测试简历数据
test_resume_data = {
    "resume_markdown": """# 王小明 - 前端工程师

## 个人信息
- 姓名：王小明
- 电话：138-0000-0001
- 邮箱：xiaoming.wang@email.com
- 地址：北京市海淀区

## 工作经历
### 高级前端工程师 | ABC科技公司 | 2021-2023
- 负责企业级Web应用的前端架构设计和开发
- 主导React生态系统技术栈的升级和优化
- 带领5人前端团队完成多个重要项目

### 前端工程师 | XYZ创业公司 | 2019-2021  
- 从0到1搭建公司前端技术体系
- 开发响应式单页应用和移动端H5页面
- 实现前后端分离架构和API接口设计

## 教育背景
### 计算机科学与技术 | 北京理工大学 | 2015-2019
- 学士学位，GPA 3.7/4.0
- 主修课程：数据结构、算法设计、Web开发、数据库系统

## 技能专长
- 前端框架：React、Vue.js、Angular
- 开发语言：JavaScript、TypeScript、HTML5、CSS3
- 工具链：Webpack、Vite、Babel、ESLint
- 版本控制：Git、GitHub、GitLab
- 设计工具：Figma、Adobe XD

## 项目经验

### 企业管理系统前端重构 | 2022-2023
**技术栈：** React 18, TypeScript, Ant Design, Redux Toolkit
- 将传统jQuery项目重构为现代化React应用
- 实现了用户权限管理、数据可视化看板等核心功能
- 性能优化后页面加载时间减少60%

### 电商移动端App | 2020-2021
**技术栈：** React Native, Redux, TypeScript
- 独立负责iOS和Android双平台开发
- 实现商品浏览、购物车、支付等完整电商流程  
- 用户活跃度提升35%，转化率提升22%
""",
    "title": "王小明的简历 - 浩流简历·flowork自动跳转测试"
}

def test_realtime_notification():
    """测试实时通知功能"""
    print("🚀 实时自动跳转功能测试")
    print("=" * 60)
    print()
    
    print("📋 测试场景：")
    print("1. 模拟Dify HTTP节点发送简历数据到后端")  
    print("2. 后端创建简历并发送SSE通知")
    print("3. 前端接收通知并自动跳转到编辑页面")
    print()
    
    # 测试1: 发送HTTP请求创建简历（无重定向参数）
    print("📡 测试1: 发送HTTP请求到 /api/resumes/from-dify")
    print(f"📄 简历标题: {test_resume_data['title']}")
    
    try:
        response = requests.post(
            'http://localhost:8080/api/resumes/from-dify',
            json=test_resume_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"✅ 请求状态: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print(f"📝 响应数据:")
            print(f"   - 简历ID: {result.get('resume_id')}")
            print(f"   - 编辑链接: {result.get('edit_url')}")
            print(f"   - 重定向URL: {result.get('redirect_url')}")
            print(f"   - 通知已发送: {result.get('notification_sent', False)}")
            
            resume_id = result.get('resume_id')
            redirect_url = result.get('redirect_url')
            
            print()
            print("🎯 期望结果:")
            print(f"   - 前端应该自动跳转到: {redirect_url}")
            print(f"   - 用户会看到简历编辑页面")
            
            return resume_id, redirect_url
            
        else:
            print(f"❌ 请求失败: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ 请求错误: {e}")
        return None, None

def test_notification_api():
    """测试通知API"""
    print("\n" + "=" * 60)
    print("🔔 测试2: 直接测试通知API")
    
    try:
        response = requests.post(
            'http://localhost:8080/api/notifications/test',
            json={
                'type': 'test_redirect',
                'message': '这是一个测试自动跳转的通知消息'
            },
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"✅ 通知API状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📝 API响应: {result.get('message')}")
            print("🎯 期望结果: 前端应该接收到测试通知事件")
        else:
            print(f"❌ 通知API失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 通知API错误: {e}")

def show_instructions():
    """显示使用说明"""
    print("\n" + "=" * 60)
    print("📖 使用说明")
    print()
    print("1. 🖥️  确保后端服务运行在: http://localhost:8080")
    print("2. 🌐 确保前端服务运行在: http://localhost:3002")  
    print("3. 👀 在浏览器中打开前端页面，观察是否自动跳转")
    print("4. 🔍 查看浏览器开发者工具的Console，观察SSE连接状态")
    print()
    print("🔧 Dify HTTP节点配置:")
    print("   URL: http://host.docker.internal:8080/api/resumes/from-dify")
    print("   Method: POST")
    print("   Content-Type: application/json")
    print("   Body: {")
    print('     "resume_markdown": "{{LLM生成的简历内容}}",')
    print('     "title": "{{简历标题}}"')
    print("   }")
    print()
    print("✨ 自动跳转流程:")
    print("   Dify HTTP节点 → 后端API → SSE通知 → 前端自动跳转")

def main():
    print("🎯 浩流简历·flowork 实时自动跳转测试")
    print("=" * 60)
    print()
    
    # 主要测试
    resume_id, redirect_url = test_realtime_notification()
    
    # 附加测试
    test_notification_api()
    
    # 使用说明
    show_instructions()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    
    if resume_id:
        print(f"📝 创建的简历ID: {resume_id}")
        print(f"🔗 如果前端未自动跳转，请手动访问: {redirect_url}")
    
    print("\n💡 提示: 保持前端页面打开，观察是否收到通知并自动跳转")

if __name__ == '__main__':
    main()