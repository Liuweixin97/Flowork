#!/usr/bin/env python3
"""
测试简化的自动跳转功能
使用轮询机制检测新创建的简历
"""

import requests
import json
import time

# 测试简历数据
test_resume = {
    "resume_markdown": """# 李小红 - UI/UX设计师

## 个人信息
- 姓名：李小红
- 电话：139-0000-0002
- 邮箱：xiaohong.li@email.com
- 作品集：https://lixiaohong.design

## 工作经历
### 高级UI设计师 | 美团 | 2022-2024
- 负责美团外卖App的UI设计和用户体验优化
- 主导设计系统建设，提升设计效率40%
- 参与用户调研，优化关键业务流程转化率

### UI设计师 | 字节跳动 | 2020-2022  
- 负责抖音创作者工具的界面设计
- 设计移动端和Web端产品界面
- 与产品经理和开发团队紧密协作

## 教育背景
### 视觉传达设计 | 中央美术学院 | 2016-2020
- 学士学位，专业排名前10%
- 获得国家奖学金、优秀毕业设计奖

## 技能专长
- 设计工具：Figma、Sketch、Adobe Creative Suite
- 原型工具：Principle、Framer、Axure RP
- 前端技术：HTML、CSS、基础JavaScript
- 用户研究：用户访谈、可用性测试、A/B测试

## 项目作品

### 美团外卖订单体验优化 | 2023
**角色：** 主设计师
- 重新设计外卖订单流程，减少用户操作步骤30%
- 优化支付页面设计，支付成功率提升15%
- 获得公司年度最佳用户体验奖

### 抖音创作者中心改版 | 2021
**角色：** UI设计师  
- 设计全新的创作者数据看板界面
- 提升内容发布流程的易用性
- 日活跃创作者数量增长25%

## 获奖经历
- 2023年 - 美团年度最佳用户体验奖
- 2021年 - 字节跳动优秀员工奖
- 2020年 - 中央美院优秀毕业设计奖
- 2019年 - 全国大学生设计大赛金奖
""",
    "title": "李小红的设计师简历 - 轮询自动跳转测试"
}

def test_polling_redirect():
    """测试基于轮询的自动跳转功能"""
    print("🎯 轮询自动跳转功能测试")
    print("=" * 60)
    print()
    
    print("📋 工作原理:")
    print("1. Dify HTTP节点发送简历数据到后端")
    print("2. 后端创建简历并保存到数据库")  
    print("3. 前端每2秒轮询检查最新简历")
    print("4. 发现新简历后自动跳转到编辑页面")
    print()
    
    # 发送简历创建请求
    print("📡 发送HTTP请求创建简历...")
    print(f"📄 简历标题: {test_resume['title']}")
    
    try:
        response = requests.post(
            'http://localhost:8080/api/resumes/from-dify',
            json=test_resume,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"✅ 请求状态码: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            
            print(f"📝 API响应:")
            print(f"   - 成功: {result.get('success')}")
            print(f"   - 消息: {result.get('message')}")
            print(f"   - 简历ID: {result.get('resume_id')}")
            print(f"   - 编辑链接: {result.get('edit_url')}")
            print(f"   - 完整跳转URL: {result.get('redirect_url')}")
            print(f"   - 自动跳转已启用: {result.get('auto_redirect_enabled')}")
            
            resume_id = result.get('resume_id')
            redirect_url = result.get('redirect_url')
            
            print()
            print("🎯 期望结果:")
            print(f"   1. 简历ID {resume_id} 已保存到数据库")
            print(f"   2. 前端轮询会在2秒内检测到新简历")
            print(f"   3. 用户浏览器自动跳转到: {redirect_url}")
            print(f"   4. 显示简历编辑页面")
            
            print()
            print("📊 验证数据库中的简历:")
            verify_resume_in_db(resume_id)
            
            return resume_id, redirect_url
            
        else:
            print(f"❌ 创建简历失败:")
            print(f"   状态码: {response.status_code}")
            print(f"   响应: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"❌ 请求发生错误: {e}")
        return None, None

def verify_resume_in_db(resume_id):
    """验证简历是否正确保存到数据库"""
    try:
        response = requests.get(
            f'http://localhost:8080/api/resumes/{resume_id}',
            timeout=5
        )
        
        if response.status_code == 200:
            resume_data = response.json()['resume']
            created_time = resume_data['created_at']
            print(f"   ✅ 简历已保存，创建时间: {created_time}")
            print(f"   📝 标题: {resume_data['title']}")
            return True
        else:
            print(f"   ❌ 无法获取简历数据: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ 验证简历失败: {e}")
        return False

def show_frontend_instructions():
    """显示前端操作说明"""
    print()
    print("=" * 60)
    print("📖 前端操作说明")
    print()
    print("1. 🌐 确保前端运行在: http://localhost:3002")
    print("2. 📱 在浏览器中打开首页，确保在简历列表页面")
    print("3. 👀 保持页面打开，观察是否出现自动跳转")
    print("4. 🔍 查看浏览器控制台日志，观察轮询检测过程")
    print()
    print("💡 预期行为:")
    print("   - 页面显示新简历创建的通知")
    print("   - 1.5秒后自动跳转到简历编辑页面")
    print("   - 显示'已自动跳转到简历编辑页面'提示")
    print()
    print("🔧 Dify HTTP节点标准配置:")
    print("   URL: http://host.docker.internal:8080/api/resumes/from-dify")
    print("   Method: POST")
    print("   Content-Type: application/json")
    print("   Body: {")
    print('     "resume_markdown": "{{LLM生成的简历内容}}",')
    print('     "title": "{{简历标题}}"')
    print("   }")

def main():
    print("🚀 简化自动跳转功能测试")
    print("使用轮询检测机制")
    print("=" * 60)
    print()
    
    # 执行测试
    resume_id, redirect_url = test_polling_redirect()
    
    # 显示使用说明  
    show_frontend_instructions()
    
    print("\n" + "=" * 60)
    print("✅ 后端测试完成！")
    
    if resume_id:
        print(f"📝 创建的简历ID: {resume_id}")
        print(f"🔗 期望跳转地址: {redirect_url}")
        print()
        print("⏰ 请在2-5秒内观察前端页面是否自动跳转")
    else:
        print("❌ 简历创建失败，请检查后端服务")

if __name__ == '__main__':
    main()