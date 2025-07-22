#!/usr/bin/env python3
"""
测试弹窗通知功能
验证HTTP请求创建简历后，前端是否显示弹窗通知
"""

import requests
import json
import time

# 测试简历数据
test_resume = {
    "resume_markdown": """# 赵大明 - 全栈工程师

## 个人信息
- 姓名：赵大明
- 电话：136-0000-0003
- 邮箱：daming.zhao@email.com
- GitHub：https://github.com/zhaodaming
- 个人网站：https://zhaodaming.dev

## 工作经历
### 高级全栈工程师 | 腾讯 | 2021-2024
- 负责微信小程序开发平台的前后端开发
- 主导微服务架构重构，系统性能提升50%
- 带领8人技术团队，负责核心业务模块开发

### 全栈工程师 | 滴滴出行 | 2019-2021
- 开发司机端和乘客端核心功能模块
- 实现实时定位和路径规划算法优化
- 参与系统高可用架构设计和实施

## 教育背景
### 软件工程 | 清华大学 | 2015-2019
- 工学学士，GPA 3.8/4.0
- 计算机科学与技术双学位
- ACM-ICPC亚洲区域赛银牌

## 技能专长
### 后端技术
- 编程语言：Java、Python、Go、Node.js
- 框架：Spring Boot、Django、Gin、Express.js
- 数据库：MySQL、PostgreSQL、Redis、MongoDB
- 消息队列：RabbitMQ、Apache Kafka

### 前端技术
- 框架：React、Vue.js、Angular
- 移动端：React Native、Flutter、微信小程序
- 构建工具：Webpack、Vite、Rollup

### 云服务与运维
- 云平台：AWS、阿里云、腾讯云
- 容器化：Docker、Kubernetes
- 监控：Prometheus、Grafana、ELK Stack

## 项目经验

### 微信小程序开发者工具优化 | 2022-2023
**技术栈：** React、Electron、Node.js、WebSocket
- 重构开发者工具核心模块，启动速度提升60%
- 实现实时预览和热更新功能
- 支持多平台适配（Windows、macOS、Linux）
- 月活跃开发者突破100万

### 滴滴智能调度系统 | 2020-2021
**技术栈：** Java、Spring Cloud、Apache Kafka、Redis
- 设计实现智能派单算法，匹配效率提升35%
- 构建高并发分布式系统，支持每秒10万订单处理
- 优化数据库查询性能，平均响应时间降低40%
- 实现系统零宕机部署和灰度发布

### 开源项目：DevFlow工作流引擎 | 2019-至今
**技术栈：** Go、gRPC、etcd、Vue.js
- GitHub Star数超过5000，Docker Hub下载量100万+
- 实现可视化工作流设计器和执行引擎
- 支持多语言插件扩展和分布式部署
- 被多家企业采用作为核心业务流程引擎

## 获奖与认证
- 2023年 - 腾讯技术突破奖
- 2021年 - 滴滴优秀员工奖  
- 2020年 - AWS Solutions Architect认证
- 2019年 - Google Cloud Professional认证
- 2018年 - ACM-ICPC亚洲区域赛银牌
""",
    "title": "赵大明的全栈工程师简历 - 弹窗通知测试"
}

def test_popup_notification():
    """测试弹窗通知功能"""
    print("🔔 简历创建弹窗通知测试")
    print("=" * 60)
    print()
    
    print("📋 测试流程:")
    print("1. HTTP请求创建简历")
    print("2. 后端保存简历并创建通知状态文件")  
    print("3. 前端轮询检查通知状态")
    print("4. 发现未显示的通知，显示弹窗")
    print("5. 用户点击按钮跳转到编辑页面")
    print()
    
    # 第1步：发送简历创建请求
    print("📡 步骤1: 发送HTTP请求创建简历")
    print(f"📄 简历标题: {test_resume['title']}")
    
    try:
        response = requests.post(
            'http://localhost:8080/api/resumes/from-dify',
            json=test_resume,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"✅ HTTP请求状态: {response.status_code}")
        
        if response.status_code != 201:
            print(f"❌ 创建简历失败: {response.text}")
            return False
        
        result = response.json()
        resume_id = result.get('resume_id')
        title = result.get('message')
        
        print(f"📝 简历创建成功:")
        print(f"   - ID: {resume_id}")
        print(f"   - 响应: {title}")
        
        # 第2步：检查通知状态文件是否创建
        print(f"\n🔍 步骤2: 检查后端通知状态")
        check_notification_file()
        
        # 第3步：测试通知API
        print(f"\n📡 步骤3: 测试通知API")
        test_notification_api()
        
        return True
        
    except Exception as e:
        print(f"❌ 请求发生错误: {e}")
        return False

def check_notification_file():
    """检查后端通知状态文件"""
    try:
        import os
        notification_file = 'instance/latest_resume_notification.json'
        
        if os.path.exists(notification_file):
            print("✅ 通知状态文件已创建")
            
            with open(notification_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📋 通知内容:")
            print(f"   - 类型: {data.get('type')}")
            print(f"   - 简历ID: {data.get('resume_id')}")
            print(f"   - 标题: {data.get('title')}")
            print(f"   - 已显示: {data.get('shown', False)}")
            print(f"   - 时间: {data.get('timestamp')}")
            
        else:
            print("❌ 通知状态文件未找到")
            
    except Exception as e:
        print(f"❌ 检查通知文件失败: {e}")

def test_notification_api():
    """测试通知API"""
    try:
        # 测试获取通知
        response = requests.get('http://localhost:8080/api/resume-notification')
        
        print(f"✅ 获取通知API状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success') and result.get('notification'):
                notification = result['notification']
                print(f"🔔 发现待显示通知:")
                print(f"   - 简历ID: {notification.get('resume_id')}")
                print(f"   - 标题: {notification.get('title')}")
                print(f"   - 跳转链接: {notification.get('redirect_url')}")
                
                return True
            else:
                print("ℹ️ 暂无待显示通知")
                return False
        else:
            print(f"❌ 获取通知失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试通知API失败: {e}")
        return False

def show_frontend_guide():
    """显示前端操作指南"""
    print("\n" + "=" * 60)
    print("📖 前端测试指南")
    print()
    print("🌐 前端设置:")
    print("1. 确保前端运行在: http://localhost:3002")
    print("2. 在浏览器中打开首页")
    print("3. 确保在简历列表页面（不是编辑页面）")
    print()
    print("👀 预期效果:")
    print("1. 3秒内应该出现弹窗通知")
    print("2. 弹窗显示'简历初稿已生成'")
    print("3. 显示简历标题和ID信息")
    print("4. 提供'立即编辑简历'按钮")
    print("5. 点击按钮跳转到编辑页面")
    print()
    print("🔍 调试信息:")
    print("- 打开浏览器开发者工具")
    print("- 查看Console中的[NOTIFICATION]日志")
    print("- 观察网络请求中的/api/resume-notification调用")
    print()
    print("🔧 Dify配置（标准）:")
    print("URL: http://host.docker.internal:8080/api/resumes/from-dify")
    print("Method: POST")
    print("Body: {\"resume_markdown\": \"...\", \"title\": \"...\"}")

def main():
    print("🎯 简历创建弹窗通知完整测试")
    print("=" * 60)
    print()
    
    # 执行测试
    success = test_popup_notification()
    
    # 显示前端指南
    show_frontend_guide()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 后端测试完成！请在前端观察弹窗通知效果")
    else:
        print("❌ 后端测试失败，请检查服务状态")
    
    print()
    print("💡 提示: 保持前端页面打开并观察弹窗通知的出现")

if __name__ == '__main__':
    main()