#!/usr/bin/env python3
"""
测试Dify Chatflow集成功能
"""
import requests
import json
import time

# 配置
BASE_URL = "http://localhost:8080"
CHATFLOW_ENDPOINTS = {
    'start': f"{BASE_URL}/api/chatflow/start",
    'message': f"{BASE_URL}/api/chatflow/message",
    'history': f"{BASE_URL}/api/chatflow/history",
    'end': f"{BASE_URL}/api/chatflow/end",
    'status': f"{BASE_URL}/api/chatflow/status"
}

def test_chatflow_status():
    """测试Chatflow服务状态"""
    print("🔍 测试Chatflow服务状态...")
    try:
        response = requests.get(CHATFLOW_ENDPOINTS['status'], timeout=5)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chatflow服务正常: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ 服务状态异常: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_start_conversation():
    """测试启动对话"""
    print("\n🚀 测试启动Chatflow对话...")
    try:
        payload = {"user_id": "test_user_123"}
        response = requests.post(
            CHATFLOW_ENDPOINTS['start'], 
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                conversation_id = data.get('conversation_id')
                print(f"✅ 对话启动成功: {conversation_id}")
                return conversation_id
            else:
                print(f"❌ 对话启动失败: {data.get('error')}")
        else:
            print(f"❌ 启动请求失败: {response.text}")
        
        return None
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_send_message(conversation_id):
    """测试发送消息"""
    if not conversation_id:
        print("❌ 没有有效的conversation_id，跳过消息测试")
        return False
    
    print(f"\n💬 测试发送消息 (会话ID: {conversation_id})...")
    
    test_messages = [
        "你好，我想创建一份简历",
        "我是一名软件工程师，有3年工作经验",
        "我熟悉Python、JavaScript和React"
    ]
    
    for i, message in enumerate(test_messages):
        try:
            payload = {
                "conversation_id": conversation_id,
                "message": message,
                "inputs": {}
            }
            
            print(f"\n📝 发送消息 {i+1}: {message}")
            response = requests.post(
                CHATFLOW_ENDPOINTS['message'],
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30  # Dify处理可能需要较长时间
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    ai_response = data.get('message', '无响应')
                    status = data.get('status', 'unknown')
                    print(f"✅ AI回复: {ai_response}")
                    print(f"对话状态: {status}")
                    
                    # 检查是否完成
                    if status == 'completed':
                        resume_content = data.get('resume_content')
                        if resume_content:
                            print("🎉 简历生成完成!")
                            print(f"简历内容预览: {str(resume_content)[:200]}...")
                            return True
                else:
                    print(f"❌ 消息发送失败: {data.get('error')}")
            else:
                print(f"❌ 请求失败: {response.text}")
            
            # 短暂等待避免过快请求
            time.sleep(1)
            
        except requests.RequestException as e:
            print(f"❌ 请求异常: {e}")
            return False
    
    return True

def test_conversation_history(conversation_id):
    """测试获取对话历史"""
    if not conversation_id:
        return False
    
    print(f"\n📚 测试获取对话历史...")
    try:
        response = requests.get(
            f"{CHATFLOW_ENDPOINTS['history']}/{conversation_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                messages = data.get('messages', [])
                print(f"✅ 获取到 {len(messages)} 条消息历史")
                for i, msg in enumerate(messages[:3]):  # 只显示前3条
                    print(f"  {i+1}. [{msg['type']}] {msg['content'][:50]}...")
                return True
            else:
                print(f"❌ 获取历史失败: {data.get('error')}")
        else:
            print(f"❌ 请求失败: {response.text}")
        
        return False
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_end_conversation(conversation_id):
    """测试结束对话"""
    if not conversation_id:
        return False
    
    print(f"\n🔚 测试结束对话...")
    try:
        payload = {"conversation_id": conversation_id}
        response = requests.post(
            CHATFLOW_ENDPOINTS['end'],
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 对话结束成功")
                return True
            else:
                print(f"❌ 结束对话失败: {data.get('error')}")
        else:
            print(f"❌ 请求失败: {response.text}")
        
        return False
    except requests.RequestException as e:
        print(f"❌ 请求异常: {e}")
        return False

def main():
    """主测试流程"""
    print("🧪 开始Dify Chatflow集成测试\n")
    print("=" * 50)
    
    # 测试服务状态
    if not test_chatflow_status():
        print("\n❌ 服务状态检查失败，请确保后端服务已启动")
        return
    
    # 测试完整对话流程
    conversation_id = test_start_conversation()
    
    if conversation_id:
        # 测试发送消息
        test_send_message(conversation_id)
        
        # 测试获取历史
        test_conversation_history(conversation_id)
        
        # 测试结束对话
        test_end_conversation(conversation_id)
    
    print("\n" + "=" * 50)
    print("🏁 测试完成")
    
    # 给出配置建议
    print("\n📋 Dify配置建议:")
    print("1. 确保Dify工作流已正确配置")
    print("2. 在.env文件中设置正确的DIFY_API_KEY和DIFY_WORKFLOW_ID")
    print("3. 工作流应该能够处理用户输入并生成简历内容")
    print("4. 完成时应该返回包含'简历创建完成'或类似标识的响应")

if __name__ == "__main__":
    main()