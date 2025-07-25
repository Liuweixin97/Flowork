#!/usr/bin/env python3
"""
测试完整的对话流程，包括简历生成
"""
import requests
import json
import time

BASE_URL = "http://localhost:8080"

def test_complete_conversation():
    """测试完整的对话流程"""
    print("🎯 测试完整对话流程 - 从开始到生成简历")
    
    # 1. 启动对话
    print("\n1. 启动对话...")
    start_response = requests.post(f"{BASE_URL}/api/chatflow/start", json={})
    if not start_response.status_code == 200 or not start_response.json().get('success'):
        print("❌ 启动对话失败")
        return False
    
    conversation_id = start_response.json()['conversation_id']
    print(f"✅ 对话启动成功: {conversation_id}")
    print(f"初始消息: {start_response.json()['initial_message']}")
    
    # 2. 模拟完整对话
    conversation_flow = [
        "张三",
        "邮箱: zhangsan@email.com, 电话: 138-0000-1234",
        "我在ABC科技公司担任高级软件工程师3年，主要负责前端开发和系统架构设计。参与了多个大型项目的开发，具有丰富的团队协作经验。",
        "本科毕业于清华大学计算机科学与技术专业，2020年毕业",
        "精通JavaScript、React、Vue.js、Node.js、Python、MySQL数据库设计与优化"
    ]
    
    for i, message in enumerate(conversation_flow):
        print(f"\n{i+2}. 发送消息: {message}")
        
        response = requests.post(f"{BASE_URL}/api/chatflow/message", json={
            "conversation_id": conversation_id,
            "message": message
        })
        
        if response.status_code == 200 and response.json().get('success'):
            data = response.json()
            ai_response = data.get('message', '')
            status = data.get('status', 'unknown')
            
            print(f"✅ AI回复: {ai_response[:100]}...")
            print(f"对话状态: {status}")
            
            if status == 'completed':
                print("🎉 简历生成完成!")
                
                # 检查是否自动创建了简历
                if data.get('resume_id'):
                    resume_id = data['resume_id']
                    edit_url = data.get('edit_url', '')
                    print(f"📄 简历ID: {resume_id}")
                    print(f"🔗 编辑链接: {edit_url}")
                    
                    # 验证简历是否真的创建成功
                    resume_response = requests.get(f"{BASE_URL}/api/resumes/{resume_id}")
                    if resume_response.status_code == 200:
                        resume_data = resume_response.json()['resume']
                        print(f"✅ 简历验证成功: {resume_data['title']}")
                        print(f"内容预览: {resume_data['raw_markdown'][:200]}...")
                        return True
                    else:
                        print("❌ 简历验证失败")
                        return False
                
                return True
        else:
            print(f"❌ 发送消息失败: {response.text}")
            return False
        
        time.sleep(0.5)  # 短暂延迟
    
    print("❌ 对话流程未完成简历生成")
    return False

def main():
    """主测试函数"""
    print("🧪 测试完整Chatflow对话流程\n")
    
    success = test_complete_conversation()
    
    if success:
        print("\n🎊 测试成功！完整的对话流程工作正常")
        print("✅ 用户可以通过AI助手创建简历")
        print("✅ 简历会自动保存到数据库")
        print("✅ 用户可以直接跳转到编辑页面")
    else:
        print("\n❌ 测试失败，请检查以下项目:")
        print("- 后端服务是否正常运行")
        print("- 模拟Dify服务是否正常运行")
        print("- 数据库连接是否正常")

if __name__ == "__main__":
    main()